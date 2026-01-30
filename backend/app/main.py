import os
# Set cache directory for Vercel (read-only filesystem except /tmp)
os.environ["XDG_CACHE_HOME"] = "/tmp"

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.api.api import api_router
from app.services.price_updater import update_prices
from fastapi.middleware.cors import CORSMiddleware

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Scheduler is useful for local dev, but on Vercel it may not persist.
    # The cron endpoint below handles Vercel updates.
    scheduler.add_job(update_prices, 'interval', minutes=10)
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="Stock Game API", lifespan=lifespan)

# Vercel Cron Integration
@app.get("/api/v1/cron/update-prices")
async def cron_update_prices():
    """
    Endpoint for Vercel Cron Jobs to trigger price updates.
    """
    await update_prices()
    return {"status": "success"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Stock Game API", "env": settings.ENV_NAME}

@app.get("/health")
def health_check():
    return {"status": "ok"}
