from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Literal
from datetime import datetime

class ScrapeRequest(BaseModel):
    url: HttpUrl
    render_js: bool = False
    output_format: Literal["json", "markdown"] = "json"
    selectors: Optional[Dict[str, str]] = None

class CrawlRequest(BaseModel):
    start_url: HttpUrl
    max_pages: int = 10
    allowed_domains: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    render_js: bool = False
    output_format: Literal["json", "markdown"] = "json"

class ScrapedData(BaseModel):
    url: HttpUrl
    title: str
    content: str
    metadata: Dict[str, str]
    timestamp: datetime = datetime.now()

class CrawlJob(BaseModel):
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_pages: int
    pages_scraped: int
    results: List[ScrapedData]
    error: Optional[str] = None 