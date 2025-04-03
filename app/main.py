from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .models import ScrapeRequest, ScrapedData
from .scraper import Scraper
from .security import get_api_key
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid

class APIKey(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    last_used: Optional[datetime] = None

class APIKeyRequest(BaseModel):
    name: str
    description: Optional[str] = None

app = FastAPI(title="Web Scraper API")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize database
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS api_keys
                 (key TEXT PRIMARY KEY, name TEXT, description TEXT,
                  created_at TIMESTAMP, last_used TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html") as f:
        return f.read()

@app.get("/api/keys", response_model=List[APIKey])
async def list_keys():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('SELECT key, name, description, created_at, last_used FROM api_keys')
    keys = []
    for row in c.fetchall():
        keys.append(APIKey(
            key=row[0],
            name=row[1],
            description=row[2],
            created_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
            last_used=datetime.fromisoformat(row[4]) if row[4] else None
        ))
    conn.close()
    return keys

@app.post("/api/keys", response_model=APIKey)
async def create_key(request: APIKeyRequest):
    new_key = APIKey(
        key=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        created_at=datetime.now()
    )
    
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO api_keys (key, name, description, created_at) VALUES (?, ?, ?, ?)',
        (new_key.key, new_key.name, new_key.description, new_key.created_at.isoformat())
    )
    conn.commit()
    conn.close()
    
    return new_key

@app.delete("/api/keys/{key}")
async def delete_key(key: str):
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('DELETE FROM api_keys WHERE key = ?', (key,))
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    conn.commit()
    conn.close()
    return {"message": "Key deleted"}

@app.post("/scrape", response_model=ScrapedData)
async def scrape_url(request: ScrapeRequest, api_key: str = Depends(get_api_key)):
    try:
        scraper = Scraper()
        result = await scraper.scrape_page(str(request.url), request.render_js)
        await scraper.close()
        return result
    except Exception as e:
        logger.error(f"Error processing scrape request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 