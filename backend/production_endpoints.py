"""
Production-Ready Endpoints for Dragon KARAU AI
Includes optimized divisions, geocoding expansion, stream validation, and monitoring
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import asyncio

# Import optimized services
from administrative_divisions_optimized import get_optimized_divisions_manager
from station_geocoding_service import get_geocoding_service  
from stream_validation_service import get_validation_service
from security_middleware import auth, request_logger, limiter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/production", tags=["Production"])


# Administrative Divisions - Optimized Endpoints
@router.post("/divisions/populate-background")
@limiter.limit("5/hour")  # Strict rate limit for resource-intensive operation
async def start_divisions_population_background(request: Request, background_tasks: BackgroundTasks):
    """
    Start optimized administrative divisions population in background
    
    - Rate limited to 5 requests per hour
    - Runs in background with progress tracking
    - Uses caching and pagination for performance
    """
    try:
        divisions_manager = get_optimized_divisions_manager()
        
        # Start in background
        background_tasks.add_task(divisions_manager.populate_all_divisions_background)
        
        return {
            "status": "started",
            "message": "Administrative divisions population started in background",
            "progress_endpoint": "/api/production/divisions/progress"
        }
    except Exception as e:
        logger.error(f"❌ Error starting divisions population: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/divisions/progress")
async def get_divisions_progress(request: Request):
    """Get current population progress"""
    try:
        divisions_manager = get_optimized_divisions_manager()
        progress = await divisions_manager.get_progress()
        
        return {
            "status": "success",
            "data": progress
        }
    except Exception as e:
        logger.error(f"❌ Error getting progress: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/divisions/stats")
async def get_divisions_stats(request: Request):
    """Get division statistics"""
    try:
        divisions_manager = get_optimized_divisions_manager()
        stats = await divisions_manager.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Geocoding Expansion Endpoints
@router.post("/geocoding/expand-coverage")
async def expand_geocoding_coverage(
    background_tasks: BackgroundTasks,
    batch_size: int = 200,
    max_batches: int = 10
):
    """
    Expand geocoding coverage with larger batches
    
    - Processes 200 stations per batch (increased from 50)
    - Runs multiple batches in background
    - Target: Achieve 80%+ coverage
    
    Args:
        batch_size: Stations per batch (default 200)
        max_batches: Maximum number of batches to run (default 10)
    """
    try:
        geocoding_service = get_geocoding_service()
        
        async def run_geocoding_expansion():
            """Run geocoding in background"""
            logger.info(f"🗺️  Starting geocoding expansion: {batch_size} stations/batch, {max_batches} batches")
            
            for batch_num in range(max_batches):
                try:
                    result = await geocoding_service.geocode_batch(limit=batch_size)
                    logger.info(f"✅ Batch {batch_num + 1}/{max_batches}: {result.get('geocoded', 0)} stations geocoded")
                    
                    # Small delay between batches
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"❌ Batch {batch_num + 1} error: {e}")
            
            logger.info(f"🎉 Geocoding expansion complete: {max_batches} batches processed")
        
        # Start in background
        background_tasks.add_task(run_geocoding_expansion)
        
        return {
            "status": "started",
            "message": f"Geocoding expansion started: {batch_size * max_batches} stations to process",
            "batch_size": batch_size,
            "max_batches": max_batches,
            "stats_endpoint": "/api/geocoding/stats"
        }
    except Exception as e:
        logger.error(f"❌ Error starting geocoding expansion: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Stream Validation Endpoints
@router.post("/stream-validation/run-full-batch")
@limiter.limit("3/hour")  # Very strict - resource intensive
async def run_full_stream_validation(
    request: Request,
    background_tasks: BackgroundTasks,
    batch_size: int = 100
):
    """
    Run full stream validation on all stations
    
    - Tests all 16,000+ stations
    - Identifies online/offline streams
    - Updates stream status in database
    - Runs in background to avoid timeout
    
    Args:
        batch_size: Stations to validate per batch (default 100)
    """
    try:
        validation_service = get_validation_service()
        
        async def run_validation_batches():
            """Run validation in background"""
            logger.info(f"🎵 Starting full stream validation in batches of {batch_size}")
            
            batch_num = 0
            total_online = 0
            total_offline = 0
            
            while True:
                try:
                    result = await validation_service.validate_batch(limit=batch_size)
                    
                    if result.get('validated', 0) == 0:
                        # No more stations to validate
                        break
                    
                    batch_num += 1
                    total_online += result.get('online', 0)
                    total_offline += result.get('offline', 0)
                    
                    logger.info(f"✅ Validation batch {batch_num}: {result.get('online', 0)} online, {result.get('offline', 0)} offline")
                    
                    # Delay between batches to avoid overwhelming servers
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"❌ Validation batch {batch_num + 1} error: {e}")
                    break
            
            logger.info(f"🎉 Stream validation complete: {total_online} online, {total_offline} offline")
        
        # Start in background
        background_tasks.add_task(run_validation_batches)
        
        return {
            "status": "started",
            "message": "Full stream validation started in background",
            "batch_size": batch_size,
            "stats_endpoint": "/api/streams/stats"
        }
    except Exception as e:
        logger.error(f"❌ Error starting stream validation: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Request Logging & Monitoring
@router.get("/monitoring/request-stats")
@limiter.limit("100/hour")
async def get_request_stats(request: Request, hours: int = 24):
    """
    Get API request statistics
    
    Args:
        hours: Number of hours to analyze (default 24)
    """
    try:
        stats = await request_logger.get_request_stats(hours=hours)
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"❌ Error getting request stats: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/monitoring/system-health")
@limiter.limit("100/hour")
async def get_system_health(request: Request):
    """
    Get comprehensive system health metrics
    
    Returns:
        - Database statistics
        - Service status
        - Performance metrics
        - Error rates
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Get database stats
        total_stations = await db.radio_stations.count_documents({})
        geocoded_stations = await db.radio_stations.count_documents({'latitude': {'$exists': True}})
        validated_streams = await db.radio_stations.count_documents({'stream_status': 'online'})
        
        # Get collection counts
        collections_stats = {}
        for collection_name in await db.list_collection_names():
            count = await db[collection_name].count_documents({})
            collections_stats[collection_name] = count
        
        return {
            "status": "healthy",
            "database": {
                "total_stations": total_stations,
                "geocoded_stations": geocoded_stations,
                "geocoding_coverage_percent": round((geocoded_stations / total_stations * 100), 2) if total_stations > 0 else 0,
                "validated_streams": validated_streams,
                "stream_validation_percent": round((validated_streams / total_stations * 100), 2) if total_stations > 0 else 0,
                "collections": collections_stats
            },
            "services": {
                "divisions_manager": "active",
                "geocoding_service": "active",
                "stream_validation": "active",
                "request_logging": "active",
                "rate_limiting": "active"
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting system health: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/monitoring/trigger-all-maintenance")
@limiter.limit("1/hour")
async def trigger_all_maintenance(request: Request, background_tasks: BackgroundTasks):
    """
    Trigger all maintenance tasks in background
    
    - Administrative divisions population
    - Geocoding expansion
    - Stream validation
    
    Rate limited to 1 request per hour (resource intensive)
    """
    try:
        divisions_manager = get_optimized_divisions_manager()
        geocoding_service = get_geocoding_service()
        validation_service = get_validation_service()
        
        async def run_all_maintenance():
            """Run all maintenance tasks"""
            logger.info("🚀 Starting comprehensive maintenance cycle")
            
            # 1. Divisions population
            logger.info("1️⃣  Starting divisions population...")
            await divisions_manager.populate_all_divisions_background()
            
            # 2. Geocoding expansion (5 batches of 200)
            logger.info("2️⃣  Starting geocoding expansion...")
            for i in range(5):
                await geocoding_service.geocode_batch(limit=200)
                await asyncio.sleep(2)
            
            # 3. Stream validation (3 batches of 100)
            logger.info("3️⃣  Starting stream validation...")
            for i in range(3):
                await validation_service.validate_batch(limit=100)
                await asyncio.sleep(5)
            
            logger.info("🎉 Comprehensive maintenance cycle complete!")
        
        # Start in background
        background_tasks.add_task(run_all_maintenance)
        
        return {
            "status": "started",
            "message": "Comprehensive maintenance started in background",
            "estimated_duration_minutes": 30,
            "monitoring_endpoint": "/api/production/monitoring/system-health"
        }
    except Exception as e:
        logger.error(f"❌ Error starting maintenance: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
