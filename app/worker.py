import asyncio
from typing import Optional, List
import logging
from uuid import uuid4
from .models import CrawlJob, CrawlRequest
from .scraper import Scraper
from .cache import RedisCache
import re

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.active_jobs: dict[str, CrawlJob] = {}
        self.scraper = Scraper()

    def _matches_pattern(self, url: str, patterns: List[str]) -> bool:
        return any(re.match(pattern, url) for pattern in patterns)

    async def start_crawl_job(self, request: CrawlRequest) -> str:
        """
        Kicks off a crawl job in the background and returns the new job_id.
        """
        job_id = str(uuid4())
        job = CrawlJob(
            job_id=job_id,
            status="pending",
            total_pages=request.max_pages,
            pages_scraped=0,
            results=[]
        )
        
        self.active_jobs[job_id] = job
        asyncio.create_task(self._crawl(job_id, request))
        
        return job_id

    async def _crawl(self, job_id: str, request: CrawlRequest):
        """
        Internal method to perform the crawling logic in an async task.
        """
        job = self.active_jobs[job_id]
        job.status = "running"
        
        try:
            to_visit = {str(request.start_url)}
            visited = set()
            
            while to_visit and len(visited) < request.max_pages:
                url = to_visit.pop()

                if url in visited:
                    continue

                # Check if URL matches any exclude patterns
                if request.exclude_patterns and self._matches_pattern(url, request.exclude_patterns):
                    continue

                # Scrape the page
                try:
                    result = await self.scraper.scrape_page(url, render_js=request.render_js)
                    job.results.append(result)
                    job.pages_scraped += 1
                    visited.add(url)
                    
                    # Cache the result using RedisCache.cache_data(...)
                    cache_key = f"{url}|render_js={request.render_js}"
                    await self.cache.cache_data(cache_key, result.dict())

                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue

            job.status = "completed"

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            logger.error(f"Crawl job {job_id} failed: {str(e)}")

    async def get_job_status(self, job_id: str) -> Optional[CrawlJob]:
        """
        Retrieve the current status of a specific crawl job by ID.
        """
        return self.active_jobs.get(job_id)

    async def cleanup_job(self, job_id: str):
        """
        Remove a completed or failed crawl job from active tracking.
        """
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]

    async def close(self):
        """
        Clean up resources (e.g., the scraper).
        """
        await self.scraper.close()