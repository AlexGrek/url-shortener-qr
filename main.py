import base64
import hashlib
import io
import json
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import qrcode
from diskcache import Cache
import logging
import asyncio

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings from .env
class Settings(BaseSettings):
    DOMAIN: str

    class Config:
        env_file = ".env"

settings = Settings()

# FastAPI app
API_KEY = os.getenv("API_KEY")
app = FastAPI()
cache = Cache("url_cache")
logger.info(f"API key: {API_KEY}")

# Cleanup task
async def cleanup_task():
    while True:
        now = datetime.utcnow()
        for key in list(cache.iterkeys()):
            try:
                value = json.loads(cache.get(key))
                if datetime.fromisoformat(value["expiration_date"]) < now:
                    cache.delete(key)
                    logger.info(f"Deleted expired key: {key}")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_task())  # Start background cleanup
    await cleanup_task()  # Run once on startup

class CreateRequest(BaseModel):
    ttl: int
    url: str
    apikey: str
    reason: str

@app.post("/api/create")
async def create_url(data: CreateRequest, request: Request):
        # Validate API key
    if data.apikey != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")


    logger.info(f"Received create request: {data.dict()}")

    # Calculate short key
    base_key = base64.urlsafe_b64encode(
        hashlib.sha256(data.url.encode()).digest()
    ).decode()[:6]

    key = base_key
    counter = 0
    while key in cache:
        counter += 1
        key = base_key + str(counter)

    # Generate short URL and QR code
    short_url = f"{settings.DOMAIN}/{key}"
    qr_img = qrcode.make(short_url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    now = datetime.utcnow()
    entry = {
        "creation_date": now.isoformat(),
        "expiration_date": (now + timedelta(seconds=data.ttl)).isoformat(),
        "url": data.url,
        "short_url": short_url,
        "qr": qr_b64,
        "original_request": data.dict()
    }

    cache.set(key, json.dumps(entry))
    logger.info(f"Stored short URL: {short_url}")

    return entry

@app.get("/{key}")
async def redirect(key: str):
    data = cache.get(key)
    if not data:
        return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)
    record = json.loads(data)
    if datetime.fromisoformat(record["expiration_date"]) < datetime.utcnow():
        cache.delete(key)
        return HTMLResponse("<h1>404 Not Found (Expired)</h1>", status_code=404)
    return RedirectResponse(record["url"])
