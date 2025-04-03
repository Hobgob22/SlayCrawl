from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

class ScrapedData(BaseModel):
    url: HttpUrl
    title: str
    content: str
    metadata: Dict[str, str]

class ScrapeRequest(BaseModel):
    url: HttpUrl
    render_js: bool = False 