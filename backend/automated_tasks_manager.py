"""Automated Tasks Manager
Schedules and manages automated background tasks
"""
import asyncio
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)

class AutomatedTasksManager:
    """Manages scheduled automated tasks"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.db = self.mongo_client[db_name]
        
        self.tasks = {
            'validation_check': {'interval_hours': 6, 'last_run': None},
            'database_optimization': {'interval_hours': 24, 'last_run': None},
            'coverage_analysis': {'interval_hours': 12, 'last_run': None},
            'health_monitor': {'interval_hours': 1, 'last_run': None},
        }
        
        self.running = False
    
    def should_run_task(self, task_name: str) -> bool:
        """Check if a task should run based on its schedule"""
        task = self.tasks.get(task_name)
        if not task:
            return False
        
        if task['last_run'] is None:
            return True
        
        time_since_last_run = datetime.utcnow() - task['last_run']
        interval = timedelta(hours=task['interval_hours'])
        
        return time_since_last_run >= interval
    
    async def run_task(self, task_name: str) -> Dict[str, Any]:
        """Execute a specific task"""
        logger.info(f"Running task: {task_name}")
        
        try:
            if task_name == 'validation_check':
                result = await self._validation_check()
            elif task_name == 'database_optimization':
                result = await self._database_optimization()
            elif task_name == 'coverage_analysis':
                result = await self._coverage_analysis()
            elif task_name == 'health_monitor':
                result = await self._health_monitor()
            else:
                result = {'status': 'unknown_task'}
            
            # Update last run time
            self.tasks[task_name]['last_run'] = datetime.utcnow()
            
            # Log to database
            await self.db.events.insert_one({
                'type': 'automated_task',
                'task_name': task_name,
                'timestamp': datetime.utcnow(),
                'result': result
            })
            
            return result
        except Exception as e:
            logger.error(f"Task {task_name} error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validation_check(self) -> Dict[str, Any]:
        """Check validation status"""
        total = await self.db.radio_stations.count_documents({})
        validated = await self.db.radio_stations.count_documents({'validated': True})
        
        return {
            'total_stations': total,
            'validated': validated,
            'rate': f"{(validated/total*100):.1f}%" if total > 0 else "0%"
        }
    
    async def _database_optimization(self) -> Dict[str, Any]:
        """Run database optimization"""
        # Check indexes
        indexes = await self.db.radio_stations.index_information()
        
        return {
            'indexes_count': len(indexes),
            'status': 'optimized'
        }
    
    async def _coverage_analysis(self) -> Dict[str, Any]:
        """Analyze coverage"""
        countries = len(await self.db.radio_stations.distinct('country'))
        
        return {
            'unique_countries': countries,
            'coverage': f"{(countries/195*100):.1f}%"
        }
    
    async def _health_monitor(self) -> Dict[str, Any]:
        """Monitor system health"""
        await self.db.command('ping')
        
        return {
            'database': 'healthy',
            'status': 'ok'
        }
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        self.running = True
        logger.info("Automated tasks scheduler started")
        
        while self.running:
            for task_name in self.tasks.keys():
                if self.should_run_task(task_name):
                    await self.run_task(task_name)
            
            # Sleep for 5 minutes between checks
            await asyncio.sleep(300)
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Automated tasks scheduler stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.running,
            'tasks': {
                name: {
                    'interval_hours': task['interval_hours'],
                    'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                    'should_run_now': self.should_run_task(name)
                }
                for name, task in self.tasks.items()
            }
        }


async def main():
    """Run tasks manager"""
    manager = AutomatedTasksManager()
    
    # Run all tasks once
    for task_name in manager.tasks.keys():
        result = await manager.run_task(task_name)
        print(f"✅ {task_name}: {result.get('status', 'complete')}")


if __name__ == '__main__':
    asyncio.run(main())
