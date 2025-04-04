from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import ValidationError, BaseModel
import os
import logging

from .models import (
    ScrapeRequest,
    ScrapedData,
    APIKeyRequest,
    APIKey
)
from .scraper import Scraper
from .cache import cache
from .database import (
    get_session,
    APIKeyModel,
    ScrapedDataModel,
    init_db
)

import json

# Health check response model
class HealthCheck(BaseModel):
    status: str
    version: str
    redis_status: str
    database_status: str

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="SlayCrawl API",
    description="""
    A modern, async web scraping API built with FastAPI, Redis, and Playwright.
    Provides powerful web scraping capabilities with JS rendering support,
    caching, and customizable data extraction.
    """,
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return detailed error messages"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [
                {
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        }
    )

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database and cache on startup."""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close cache connection on shutdown."""
    await cache.close()

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Health check endpoint that verifies the API and its dependencies are working.
    Checks database and Redis connectivity.
    """
    try:
        # Test database
        await session.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    try:
        # Test Redis connection
        await cache.redis.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        redis_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"

    return HealthCheck(
        status=overall_status,
        version="1.0.0",
        redis_status=redis_status,
        database_status=db_status
    )

# API Key validation dependency
async def get_api_key(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> str:
    """
    Validate API Key unless request is from the local web UI (x-webui-token).
    """
    # If coming from the local UI, skip requirement
    if request.headers.get("x-webui-token") == "true":
        return "browser_ui"

    # Otherwise, read from X-API-Key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required (use 'X-API-Key' header)."
        )

    # Validate
    stmt = select(APIKeyModel).where(APIKeyModel.key == api_key)
    result = await session.execute(stmt)
    key_model = result.scalar_one_or_none()
    if not key_model:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Update last_used
    key_model.last_used = datetime.utcnow()
    await session.commit()

    return api_key

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def read_root():
    """Serve the main HTML interface."""
    with open("app/static/index.html") as f:
        return f.read()

@app.get("/health-ui", response_class=HTMLResponse, tags=["UI"])
async def health_ui():
    """Serve the health check UI interface."""
    with open("app/static/health.html") as f:
        return f.read()

@app.get("/api/keys", response_model=list[APIKey], tags=["API Keys"])
async def list_keys(session: AsyncSession = Depends(get_session)):
    """List all API keys."""
    stmt = select(APIKeyModel)
    result = await session.execute(stmt)
    return [
        APIKey(
            key=key.key,
            name=key.name,
            description=key.description,
            created_at=key.created_at,
            last_used=key.last_used
        )
        for key in result.scalars()
    ]

@app.post("/api/keys", response_model=APIKey, tags=["API Keys"])
async def create_key(
    request: APIKeyRequest,
    session: AsyncSession = Depends(get_session)
):
    """Create a new API key."""
    import uuid
    
    new_key = APIKeyModel(
        key=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        created_at=datetime.utcnow()
    )
    
    session.add(new_key)
    await session.commit()
    
    return APIKey(
        key=new_key.key,
        name=new_key.name,
        description=new_key.description,
        created_at=new_key.created_at,
        last_used=new_key.last_used
    )

@app.delete("/api/keys/{key}", tags=["API Keys"])
async def delete_key(
    key: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete an API key."""
    stmt = select(APIKeyModel).where(APIKeyModel.key == key)
    result = await session.execute(stmt)
    key_model = result.scalar_one_or_none()
    
    if not key_model:
        raise HTTPException(status_code=404, detail="Key not found")
    
    await session.delete(key_model)
    await session.commit()
    return {"message": "Key deleted"}

@app.post("/scrape", response_model=ScrapedData, tags=["Scraping"])
async def scrape_url(
    request: ScrapeRequest,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(get_api_key)
):
    """
    Scrape a webpage with optional JavaScript rendering.
    Uses Redis cache to avoid re-scraping recently accessed pages.
    """
    logger.info(f"Scrape request for URL: {request.url}")
    
    url = str(request.url)

    async def scrape_and_store():
        logger.info("Cache miss - starting scrape operation")
        scraper = Scraper()
        try:
            result = await scraper.scrape_page(url, request.render_js)
            logger.info("Scrape completed successfully")
            await scraper.close()
            
            # Save in DB
            data_model = ScrapedDataModel(
                url=url,
                title=result.title,
                content=result.content,
                page_metadata=json.dumps(result.metadata),
                timestamp=datetime.utcnow(),
                cached=f"scrape:{url}"
            )
            session.add(data_model)
            await session.commit()
            
            return result.dict()
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise

    # Use Redis cache first
    try:
        data = await cache.get_or_set(url, scrape_and_store)
        return ScrapedData(**data)
    except Exception as e:
        logger.error(f"Error in cache operation or scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
