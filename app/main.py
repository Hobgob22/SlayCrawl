from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .models import ScrapeRequest, CrawlRequest, ScrapedData, CrawlJob
from .scraper import Scraper
from .cache import Cache
from .worker import Worker
from .formatter import Formatter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="SlayCrawl API",
    description="A modern, async web scraping API that slays Firecrawl's vibe",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cache = Cache(redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"))
worker = Worker(cache)
scraper = Scraper()

@app.on_event("shutdown")
async def shutdown_event():
    await cache.close()
    await worker.close()
    await scraper.close()

@app.post("/scrape")
async def scrape_page(request: ScrapeRequest):
    """
    Scrape a single page and return the results
    """
    try:
        # Check cache first
        cache_key = cache.get_key(str(request.url), {"render_js": request.render_js})
        cached_data = await cache.get(cache_key)
        
        if cached_data:
            data = ScrapedData(**cached_data)
        else:
            data = await scraper.scrape_page(
                str(request.url),
                render_js=request.render_js,
                selectors=request.selectors
            )
            # Cache the result
            await cache.set(cache_key, data.dict())
        
        return Formatter.format_output(data, request.output_format)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start a crawl job and return a job ID
    """
    try:
        job_id = await worker.start_crawl_job(request)
        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crawl/{job_id}")
async def get_crawl_status(job_id: str):
    """
    Get the status of a crawl job
    """
    job = await worker.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = job.dict()
    if job.status == "completed":
        response["results"] = Formatter.format_output(job.results, "json")
        background_tasks.add_task(worker.cleanup_job, job_id)
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 