from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, List, Literal
from datetime import datetime

class APIKeyRequest(BaseModel):
    """Request model for creating a new API key."""
    name: str
    description: Optional[str] = None

class APIKey(BaseModel):
    """Response model for API key information."""
    key: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    last_used: Optional[datetime] = None

class ScrapeRequest(BaseModel):
    url: HttpUrl
    render_js: bool = False
    output_format: Literal["json", "markdown"] = "json"
    selectors: Optional[Dict[str, str]] = None
    wait_for: Optional[str] = None  # CSS selector to wait for
    timeout: Optional[int] = 30000  # Timeout in milliseconds


class ScrapedData(BaseModel):
    """Response model for scraped webpage data."""
    # Keep your existing fields the same. 
    # 'url' can stay as HttpUrl if you like, since the code 
    # now always returns a valid scheme. 
    url: str
    title: str
    content: str
    metadata: Dict[str, str]
    timestamp: datetime = datetime.utcnow()
    cached: bool = False

class BatchScrapeRequest(BaseModel):
    """Request model for batch scraping multiple webpages."""
    urls: List[HttpUrl]
    render_js: bool = False
    concurrent_limit: int = 5
    output_format: Literal["json", "markdown"] = "json"

class BatchScrapeResponse(BaseModel):
    """Response model for batch scraping results."""
    results: List[ScrapedData]
    failed_urls: List[Dict[str, str]]  # List of failed URLs with error messages
    total_time: float  # Total time taken in seconds

class CrawlRequest(BaseModel):
    """
    Request model for crawling multiple pages starting from a URL.
    
    Attributes:
        start_url: The initial URL to start crawling from
        max_pages: Maximum number of pages to crawl (default: 10)
        allowed_domains: List of domains to restrict crawling to
        exclude_patterns: URL patterns to exclude from crawling
        render_js: Whether to render JavaScript on pages
        output_format: The desired output format
    """
    start_url: HttpUrl
    max_pages: int = 10
    allowed_domains: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    render_js: bool = False
    output_format: Literal["json", "markdown"] = "json"

class CrawlJob(BaseModel):
    """
    Model representing the status of a crawling job.
    
    Attributes:
        job_id: Unique identifier for the crawl job
        status: Current status of the job
        total_pages: Total number of pages to crawl
        pages_scraped: Number of pages successfully scraped
        results: List of scraped data from each page
        error: Error message if the job failed
    """
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_pages: int
    pages_scraped: int
    results: List[ScrapedData]
    error: Optional[str] = None 