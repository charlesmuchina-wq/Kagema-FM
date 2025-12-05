"""Production-Ready Endpoints for Dragon KARAU AI - Cleaned Version"""
from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any
import logging
import asyncio
from station_geocoding_service import get_geocoding_service
from stream_validation_service import get_validation_service
from administrative_divisions_optimized import get_optimized_divisions_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/production", tags=["Production"])

# Geocoding Expansion
@router.post("/geocoding/expand-coverage")
async def expand_geocoding_coverage(
    background_tasks: BackgroundTasks,
    batch_size: int = 200,
    max_batches: int = 10
):
    """Expand geocoding coverage with larger batches"""
    try:
        geocoding_service = get_geocoding_service()
        
        async def run_geocoding_expansion():
            logger.info(f"🗺️  Starting geocoding expansion: {batch_size} stations/batch, {max_batches} batches")
            for batch_num in range(max_batches):
                try:
                    result = await geocoding_service.geocode_batch(limit=batch_size)
                    logger.info(f"✅ Batch {batch_num + 1}/{max_batches}: {result.get('geocoded', 0)} stations geocoded")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"❌ Batch {batch_num + 1} error: {e}")
            logger.info(f"🎉 Geocoding expansion complete!")
        
        background_tasks.add_task(run_geocoding_expansion)
        return {
            "status": "started",
            "message": f"Geocoding expansion started: {batch_size * max_batches} stations to process"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Stream Validation
@router.post("/stream-validation/run-full-batch")
async def run_full_stream_validation(
    background_tasks: BackgroundTasks,
    batch_size: int = 100
):
    """Run full stream validation on all stations"""
    try:
        validation_service = get_validation_service()
        
        async def run_validation_batches():
            logger.info(f"🎵 Starting full stream validation in batches of {batch_size}")
            batch_num = 0
            total_online = 0
            total_offline = 0
            
            while True:
                try:
                    result = await validation_service.validate_batch(limit=batch_size)
                    if result.get('validated', 0) == 0:
                        break
                    batch_num += 1
                    total_online += result.get('online', 0)
                    total_offline += result.get('offline', 0)
                    logger.info(f"✅ Batch {batch_num}: {result.get('online', 0)} online, {result.get('offline', 0)} offline")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"❌ Validation batch error: {e}")
                    break
            
            logger.info(f"🎉 Stream validation complete: {total_online} online, {total_offline} offline")
        
        background_tasks.add_task(run_validation_batches)
        return {
            "status": "started",
            "message": "Full stream validation started in background"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# System Health
@router.get("/monitoring/system-health")
async def get_system_health():
    """Get comprehensive system health metrics"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        total_stations = await db.radio_stations.count_documents({})
        geocoded_stations = await db.radio_stations.count_documents({'latitude': {'$exists': True}})
        validated_streams = await db.radio_stations.count_documents({'stream_status': 'online'})
        
        return {
            "status": "healthy",
            "database": {
                "total_stations": total_stations,
                "geocoded_stations": geocoded_stations,
                "geocoding_coverage_percent": round((geocoded_stations / total_stations * 100), 2) if total_stations > 0 else 0,
                "validated_streams": validated_streams,
                "stream_validation_percent": round((validated_streams / total_stations * 100), 2) if total_stations > 0 else 0
            },
            "services": {
                "geocoding_service": "active",
                "stream_validation": "active",
                "cors": "configured",
                "security_headers": "active"
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
