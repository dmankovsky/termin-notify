from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from app.core.config import settings
from app.api import api_router
from app.services.monitor import MonitoringService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Termin-Notify application...")

    # Start monitoring scheduler
    monitoring_service = MonitoringService()

    scheduler.add_job(
        monitoring_service.monitor_all_services,
        'interval',
        minutes=settings.SCRAPE_INTERVAL_MINUTES,
        id='monitor_services',
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Monitoring scheduler started (interval: {settings.SCRAPE_INTERVAL_MINUTES} minutes)")

    # Run initial monitoring immediately
    try:
        await monitoring_service.monitor_all_services()
    except Exception as e:
        logger.error(f"Error in initial monitoring: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    scheduler.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Termin-Notify",
    description="Appointment notification service for German government services",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check
@app.get("/")
async def root():
    return {
        "message": "Termin-Notify API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
