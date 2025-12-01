"""Radio Intelligence API
API endpoints for AI Radio Intelligence Bot
"""
from fastapi import APIRouter, HTTPException
from ai_radio_intelligence_bot import get_bot
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/radio-intelligence', tags=['Radio Intelligence'])

@router.get('/status')
async def get_bot_status():
    """Get AI Radio Intelligence Bot status and statistics"""
    try:
        bot = get_bot()
        status = await bot.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/stations')
async def get_all_stations():
    """Get all registered radio stations with health status"""
    try:
        bot = get_bot()
        stations = await bot.get_all_stations()
        return {'stations': stations}
    except Exception as e:
        logger.error(f"Error getting stations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/scan')
async def trigger_maintenance_scan():
    """Trigger a comprehensive maintenance scan of all stations"""
    try:
        bot = get_bot()
        results = await bot.scan_all_stations()
        return results
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/validate/{station_id}')
async def validate_specific_station(station_id: str):
    """Validate a specific radio station"""
    try:
        bot = get_bot()
        
        # Find station
        station = await bot.db.radio_stations.find_one({'id': station_id})
        if not station:
            station = await bot.db.radio_stations.find_one({'_id': station_id})
        
        if not station:
            raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
        
        validation = await bot.validate_station(station)
        return validation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating station: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/heal/{station_id}')
async def heal_specific_station(station_id: str):
    """Attempt to heal a specific broken station"""
    try:
        bot = get_bot()
        
        # Find station
        station = await bot.db.radio_stations.find_one({'id': station_id})
        if not station:
            station = await bot.db.radio_stations.find_one({'_id': station_id})
        
        if not station:
            raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
        
        heal_result = await bot.heal_station(station)
        return heal_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error healing station: {e}")
        raise HTTPException(status_code=500, detail=str(e))
