"""Orchestral Automation API
API endpoints for complete Dragon KARAU AI automation
"""
from fastapi import APIRouter, HTTPException
from dragon_orchestral_automation import get_automation
from pydantic import BaseModel
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/orchestral', tags=['Orchestral Automation'])

class AutomationSettings(BaseModel):
    auto_crawl_enabled: bool = None
    auto_validate_enabled: bool = None
    auto_heal_enabled: bool = None
    auto_optimize_enabled: bool = None
    min_stations_threshold: int = None
    max_stations_target: int = None

@router.post('/run-full-cycle')
async def run_full_automation_cycle():
    """
    Run Complete Orchestral Automation Cycle
    
    Executes all 7 automation tasks:
    1. Station Count Maintenance
    2. Auto-Validation
    3. Auto-Healing
    4. Database Optimization
    5. Quality Control
    6. Coverage Analysis
    7. Performance Monitoring
    
    **This is the MASTER automation endpoint**
    """
    try:
        automation = get_automation()
        result = await automation.run_full_automation_cycle()
        return result
    except Exception as e:
        logger.error(f"Automation cycle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/status')
async def get_automation_status():
    """
    Get Orchestral Automation Status
    
    Returns:
    - Current settings
    - Last execution times
    - Automation state (active/manual)
    - All enabled/disabled features
    """
    try:
        automation = get_automation()
        status = await automation.get_automation_status()
        return status
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/settings')
async def update_automation_settings(settings: AutomationSettings):
    """
    Update Automation Settings
    
    Configure automation behavior:
    - Enable/disable auto-crawl
    - Enable/disable auto-validation
    - Enable/disable auto-healing
    - Enable/disable auto-optimization
    - Set station thresholds
    - Set intervals
    
    **Example:**
    ```json
    {
      "auto_crawl_enabled": true,
      "min_stations_threshold": 10000,
      "max_stations_target": 15000
    }
    ```
    """
    try:
        automation = get_automation()
        
        # Convert to dict and remove None values
        settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
        
        result = await automation.update_settings(settings_dict)
        return result
    except Exception as e:
        logger.error(f"Settings update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/health')
async def get_system_health():
    """
    Get Complete System Health
    
    Returns comprehensive health check of:
    - Dragon AI Orchestrator
    - Dragon Crawler
    - Radio Intelligence Bot
    - Database
    - All automation systems
    
    **Perfect for monitoring dashboards**
    """
    try:
        from dragon_ai_crawler_system import get_crawler
        from ai_radio_intelligence_bot import get_bot
        from kagema_dragon_ai_orchestrator import get_orchestrator
        
        crawler = get_crawler()
        bot = get_bot()
        orchestrator = get_orchestrator()
        automation = get_automation()
        
        # Get all statuses
        crawler_status = await crawler.get_status()
        bot_status = await bot.get_status()
        orchestrator_status = await orchestrator.get_status()
        automation_status = await automation.get_automation_status()
        
        # Get database stats
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        total_stations = await db.radio_stations.count_documents({})
        validated_stations = await db.radio_stations.count_documents({'validated': True})
        operational_stations = await db.radio_stations.count_documents({'health_status': 'OPERATIONAL'})
        
        return {
            'overall_status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'crawler': {
                    'status': 'idle' if not crawler_status['is_running'] else 'running',
                    'database_total': crawler_status['statistics']['database_total']
                },
                'intelligence_bot': {
                    'status': bot_status['status'],
                    'ai_enabled': bot_status['ai_enabled'],
                    'operational_stations': bot_status['statistics']['operational_stations']
                },
                'orchestrator': {
                    'status': orchestrator_status['status'],
                    'cycle_count': orchestrator_status['cycle_count'],
                    'total_tasks': orchestrator_status['total_tasks']
                },
                'automation': {
                    'status': automation_status['current_status'],
                    'auto_mode': automation_status['state']['is_auto_mode']
                },
                'database': {
                    'total_stations': total_stations,
                    'validated_stations': validated_stations,
                    'operational_stations': operational_stations,
                    'validation_rate': f"{(validated_stations/total_stations*100):.1f}%" if total_stations > 0 else "0%"
                }
            },
            'quick_stats': {
                'total_stations': total_stations,
                'validated': validated_stations,
                'operational': operational_stations,
                'validation_rate': f"{(validated_stations/total_stations*100):.1f}%" if total_stations > 0 else "0%",
                'health_rate': f"{(operational_stations/total_stations*100):.1f}%" if total_stations > 0 else "0%"
            }
        }
    except Exception as e:
        logger.error(f\"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/statistics')
async def get_comprehensive_statistics():
    """
    Get Comprehensive System Statistics
    
    Returns detailed statistics from all systems:
    - Dragon Crawler stats
    - Validation metrics
    - Healing metrics
    - Quality distribution
    - Geographic coverage
    - Performance metrics
    
    **Perfect for analytics and reporting**
    """
    try:
        from dragon_ai_crawler_system import get_crawler
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        crawler = get_crawler()
        mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Get crawler statistics
        crawler_stats = await crawler.get_statistics()
        
        # Get quality distribution
        quality_pipeline = [
            {
                '$bucket': {
                    'groupBy': '$quality_score',
                    'boundaries': [0, 40, 60, 80, 100],
                    'default': 'Other',
                    'output': {'count': {'$sum': 1}}
                }
            }
        ]
        quality_dist = await db.radio_stations.aggregate(quality_pipeline).to_list(length=10)
        
        # Get genre distribution
        genre_pipeline = [
            {'$group': {'_id': '$genre', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_genres = await db.radio_stations.aggregate(genre_pipeline).to_list(length=10)
        
        # Get language distribution
        language_pipeline = [
            {'$group': {'_id': '$language', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_languages = await db.radio_stations.aggregate(language_pipeline).to_list(length=10)
        
        return {
            'crawler': crawler_stats,
            'quality_distribution': quality_dist,
            'top_genres': top_genres,
            'top_languages': top_languages,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime
