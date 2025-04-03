import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Dict, Optional
import logging
from .models import ScrapedData
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "SlayCrawl/1.0"}
        )
        self._playwright = None

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

    async def scrape_page(self, url: str, render_js: bool = False, selectors: Optional[Dict[str, str]] = None) -> ScrapedData:
        try:
            if render_js:
                html_content = await self._fetch_with_js(url)
            else:
                response = await self.http_client.get(url)
                html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract data based on selectors or use defaults
            title = soup.title.string if soup.title else ""
            
            if selectors:
                content = {}
                for key, selector in selectors.items():
                    elements = soup.select(selector)
                    content[key] = [el.get_text(strip=True) for el in elements]
            else:
                # Default extraction
                content = soup.body.get_text(strip=True) if soup.body else ""

            metadata = {
                "description": soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else "",
                "keywords": soup.find("meta", {"name": "keywords"})["content"] if soup.find("meta", {"name": "keywords"}) else ""
            }

            return ScrapedData(
                url=url,
                title=title,
                content=content,
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