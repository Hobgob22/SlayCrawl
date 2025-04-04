from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
import sqlite3
from datetime import datetime

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(key: str) -> bool:
    conn = sqlite3.connect('api_keys.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM api_keys WHERE key = ?', (key,))
    exists = c.fetchone() is not None
    if exists:
        c.execute('UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE key = ?', (key,))
        conn.commit()
    conn.close()
    return exists

async def get_api_key(
    request: Request,
    api_key_header: str = Security(api_key_header)
) -> str:
    # Check if request is coming from the browser UI
    accept_header = request.headers.get("accept", "").lower()
    is_browser = "text/html" in accept_header
    
    # Allow browser requests without API key
    if is_browser:
        return "browser_access"
        
    # For API requests, require valid API key
    if not api_key_header or not await validate_api_key(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    
    return api_key_header 