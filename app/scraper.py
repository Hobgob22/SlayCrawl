import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Dict, Optional
import logging
from .models import ScrapedData
import html2text
import re

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "SlayCrawl/1.0"}
        )
        self._playwright = None
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True  # Ignore links in markdown conversion
        self.html_converter.ignore_images = True  # Ignore images in markdown conversion
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # No wrapping

    async def _get_playwright(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def _fetch_with_js(self, url: str) -> str:
        playwright = await self._get_playwright()
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            content = await page.content()
        finally:
            await browser.close()
        
        return content

    def _clean_content(self, html_content: str) -> str:
        # Remove SVG <svg> tags using regex
        html_content = re.sub(r'<svg[^>]*>.*?</svg>', '', html_content, flags=re.DOTALL)
        
        # Remove inline SVG data URLs
        html_content = re.sub(r'data:image/svg\+xml;base64,[^"\']*', '', html_content)
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove <img> tags with src starting with "data:image/svg+xml"
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src.startswith("data:image/svg+xml"):
                img.decompose()
        
        # Remove all links but keep their text
        for link in soup.find_all('a'):
            link.replace_with(link.get_text())
        
        return str(soup)

    async def scrape_page(self, url: str, render_js: bool = False) -> ScrapedData:
        try:
            if render_js:
                html_content = await self._fetch_with_js(url)
            else:
                response = await self.http_client.get(url)
                html_content = response.text

            # Clean the content before parsing
            html_content = self._clean_content(html_content)
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract title and metadata
            title = soup.title.string if soup.title else ""
            
            metadata = {
                "description": soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else "",
                "keywords": soup.find("meta", {"name": "keywords"})["content"] if soup.find("meta", {"name": "keywords"}) else ""
            }

            # Convert HTML to markdown
            markdown_content = self.html_converter.handle(html_content)

            return ScrapedData(
                url=url,
                title=title,
                content=markdown_content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise

    async def close(self):
        await self.http_client.aclose()
        if self._playwright:
            await self._playwright.stop()

    def is_valid_url(self, url: str, allowed_domains: Optional[list[str]] = None) -> bool:
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if allowed_domains:
                return any(parsed.netloc.endswith(domain) for domain in allowed_domains)
            return True
        except:
            return False 