"""Dragon AI API
API endpoints for Kagema Dragon AI Orchestrator
"""
from fastapi import APIRouter, HTTPException, Query
from kagema_dragon_ai_orchestrator import get_orchestrator
from dragon_karau_ui_automator import dragon_ui_automator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/dragon-ai', tags=['Dragon AI Orchestrator'])

@router.get('/status')
async def get_orchestrator_status():
    """Get Dragon AI Orchestrator status"""
    try:
        orchestrator = get_orchestrator()
        status = await orchestrator.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting orchestrator status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/run-tasks')
async def trigger_maintenance_cycle():
    """Manually trigger the complete 7-task maintenance cycle"""
    try:
        orchestrator = get_orchestrator()
        results = await orchestrator.run_daily_maintenance_cycle()
        return results
    except Exception as e:
        logger.error(f"Error running maintenance cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/history')
async def get_orchestrator_history(limit: int = Query(10, ge=1, le=100)):
    """Get orchestrator execution history"""
    try:
        orchestrator = get_orchestrator()
        history = await orchestrator.get_history(limit=limit)
        return {'history': history}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/test-history')
async def get_ui_test_history(limit: int = Query(10, ge=1, le=100)):
    """Get UI test history"""
    try:
        history = await dragon_ui_automator.get_test_history(limit=limit)
        return {'test_history': history}
    except Exception as e:
        logger.error(f"Error getting test history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/test-stats')
async def get_ui_test_statistics():
    """Get UI test statistics"""
    try:
        stats = await dragon_ui_automator.get_test_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting test stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/run-ui-tests')
async def trigger_ui_tests():
    """Manually trigger UI test suite"""
    try:
        results = await dragon_ui_automator.run_full_ui_test_suite()
        return results
    except Exception as e:
        logger.error(f"Error running UI tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/latest-test')
async def get_latest_test_results():
    """Get the most recent test results"""
    try:
        history = await dragon_ui_automator.get_test_history(limit=1)
        if history:
            return history[0]
        return {'message': 'No test results available'}
    except Exception as e:
        logger.error(f"Error getting latest test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
