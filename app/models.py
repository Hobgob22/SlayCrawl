from pydantic import BaseModel, HttpUrl
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
    """Request model for scraping a single webpage."""
    url: HttpUrl
    render_js: bool = False
    output_format: Literal["json", "markdown"] = "json"
    selectors: Optional[Dict[str, str]] = None
    wait_for: Optional[str] = None
    timeout: Optional[int] = 30000

class ScrapedData(BaseModel):
    """Response model for scraped webpage data."""
    url: str
    title: str
    content: str
    metadata: Dict[str, str]
    timestamp: datetime = datetime.utcnow()
    cached: bool = False
