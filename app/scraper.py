import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from typing import Optional
import logging
from .models import ScrapedData
import html2text
import re
import random
import asyncio
import os
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self):
        # Concurrency limit from env
        self._max_concurrency = int(os.getenv("MAX_CONCURRENT_SCRAPES", "10"))
        self._semaphore = asyncio.Semaphore(self._max_concurrency)

        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "SlayCrawl/1.0"}
        )
        self._playwright = None
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0

    async def _get_playwright(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def _fetch_with_js(self, url: str) -> str:
        playwright = await self._get_playwright()
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        
        try:
            await stealth_async(page)
            page.on("dialog", lambda dialog: dialog.dismiss())
            
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(random.uniform(1000, 3000))  # 1-3 second delay
            
            content = await page.content()
        finally:
            await browser.close()
        
        return content

    def _clean_content(self, html_content: str) -> str:
        # Remove <svg> tags
        html_content = re.sub(r'<svg[^>]*>.*?</svg>', '', html_content, flags=re.DOTALL)
        # Remove inline SVG data URIs
        html_content = re.sub(r'data:image/svg\+xml;base64,[^"\']*', '', html_content)
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove <img> tags with inline SVG
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src.startswith("data:image/svg+xml"):
                img.decompose()
        
        # Remove all links but keep link text
        for link in soup.find_all('a'):
            link.replace_with(link.get_text())
        
        return str(soup)

    async def scrape_page(self, url: str, render_js: bool = False) -> ScrapedData:
        """Scrape a single page. Optionally render JS with Playwright."""
        async with self._semaphore:
            try:
                if render_js:
                    html_content = await self._fetch_with_js(url)
                else:
                    response = await self.http_client.get(url)
                    html_content = response.text

                # Clean the content
                html_content = self._clean_content(html_content)
                
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Extract title
                title = soup.title.string if soup.title else ""
                
                # Extract some metadata
                desc = soup.find("meta", {"name": "description"})
                keys = soup.find("meta", {"name": "keywords"})
                metadata = {
                    "description": desc["content"] if desc else "",
                    "keywords": keys["content"] if keys else ""
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
        """Close HTTP client and playwright instance."""
        await self.http_client.aclose()
        if self._playwright:
            await self._playwright.stop()

    def is_valid_url(self, url: str) -> bool:
        """Optional local check for URL format."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
