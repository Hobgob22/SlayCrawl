import asyncio
from typing import Optional, List
import logging
from uuid import uuid4
from .models import CrawlJob, CrawlRequest, ScrapedData
from .scraper import Scraper
from .cache import Cache
import re

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, cache: Cache):
        self.cache = cache
        self.active_jobs: dict[str, CrawlJob] = {}
        self.scraper = Scraper()

    def _matches_pattern(self, url: str, patterns: List[str]) -> bool:
        return any(re.match(pattern, url) for pattern in patterns)

    async def start_crawl_job(self, request: CrawlRequest) -> str:
        job_id = str(uuid4())
        job = CrawlJob(
            job_id=job_id,
            status="pending",
            total_pages=request.max_pages,
            pages_scraped=0,
            results=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start crawling in background
        asyncio.create_task(self._crawl(job_id, request))
        
        return job_id

    async def _crawl(self, job_id: str, request: CrawlRequest):
        job = self.active_jobs[job_id]
        job.status = "running"
        
        try:
            to_visit = {str(request.start_url)}
            visited = set()
            
            while to_visit and len(visited) < request.max_pages:
                url = to_visit.pop()
                
                if url in visited:
                    continue
                    
                # Check if URL matches exclude patterns
                if request.exclude_patterns and self._matches_pattern(url, request.exclude_patterns):
                    continue

                # Scrape the page
                try:
                    result = await self.scraper.scrape_page(url, render_js=request.render_js)
                    job.results.append(result)
                    job.pages_scraped += 1
                    visited.add(url)
                    
                    # Cache the result
                    cache_key = self.cache.get_key(url, {"render_js": request.render_js})
                    await self.cache.set(cache_key, result.dict())
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue

            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            logger.error(f"Crawl job {job_id} failed: {str(e)}")

    async def get_job_status(self, job_id: str) -> Optional[CrawlJob]:
        return self.active_jobs.get(job_id)

    async def cleanup_job(self, job_id: str):
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]

    async def close(self):
        await self.scraper.close() 