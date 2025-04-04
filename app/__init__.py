"""
SlayCrawl API - A modern, async web scraping API that slays Firecrawl's vibe
"""

from .models import ScrapeRequest, ScrapedData, CrawlRequest, CrawlJob
from .scraper import Scraper
from .worker import Worker
from .cache import Cache
from .formatter import Formatter

__version__ = "1.0.0"
