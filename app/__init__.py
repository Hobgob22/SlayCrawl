"""
SlayCrawl API - A modern, async web scraping API that slays Firecrawl's vibe
"""

from .models import ScrapeRequest, ScrapedData
from .scraper import Scraper
from .cache import RedisCache
from .formatter import Formatter

__version__ = "1.0.0"
