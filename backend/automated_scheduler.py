"""Automated Scheduler
Runs self-healing, self-maintenance, and data discovery every 6 hours
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AutomatedScheduler:
    """Schedules and runs automated maintenance tasks every 6 hours"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        self.is_running = False
        self.next_run = None
        self.last_run = None
        
        # Schedule interval (6 hours)
        self.interval_hours = 6
        self.interval_seconds = self.interval_hours * 3600
        
        logger.info(f"Automated Scheduler initialized (every {self.interval_hours} hours)")
    
    async def start(self) -> None:
        """Start the automated scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        logger.info(f"🚀 Automated Scheduler started (runs every {self.interval_hours} hours)")
        
        # Run immediately on start
        await self.run_maintenance_cycle()
        
        # Then run every 6 hours
        while self.is_running:
            self.next_run = datetime.utcnow() + timedelta(seconds=self.interval_seconds)
            logger.info(f"⏰ Next maintenance cycle at: {self.next_run.isoformat()}")
            
            # Wait for 6 hours
            await asyncio.sleep(self.interval_seconds)
            
            if self.is_running:
                await self.run_maintenance_cycle()
    
    async def stop(self) -> None:
        """Stop the automated scheduler"""
        self.is_running = False
        logger.info("Automated Scheduler stopped")
    
    async def run_maintenance_cycle(self) -> Dict[str, Any]:
        """Run complete maintenance cycle"""
        cycle_start = datetime.utcnow()
        logger.info(f"\n{'='*60}")
        logger.info(f"🔧 AUTOMATED MAINTENANCE CYCLE STARTED")
        logger.info(f"Started at: {cycle_start.isoformat()}")
        logger.info(f"{'='*60}\n")
        
        results = {
            'cycle_id': str(cycle_start.timestamp()),
            'started_at': cycle_start.isoformat(),
            'tasks': {}
        }
        
        try:
            # Task 1: Run automated tests
            logger.info("1️⃣  Running automated tests...")
            test_result = await self.run_automated_tests()
            results['tasks']['automated_tests'] = test_result
            
            # Task 2: Self-healing (fix broken stations)
            logger.info("2️⃣  Running self-healing...")
            healing_result = await self.run_self_healing()
            results['tasks']['self_healing'] = healing_result
            
            # Task 3: Data discovery (crawl new stations)
            logger.info("3️⃣  Running data discovery...")
            discovery_result = await self.run_data_discovery()
            results['tasks']['data_discovery'] = discovery_result
            
            # Task 4: Database optimization
            logger.info("4️⃣  Running database optimization...")
            optimization_result = await self.run_database_optimization()
            results['tasks']['database_optimization'] = optimization_result
            
            # Task 5: System cleanup
            logger.info("5️⃣  Running system cleanup...")
            cleanup_result = await self.run_system_cleanup()
            results['tasks']['system_cleanup'] = cleanup_result
            
            # Task 6: Health monitoring
            logger.info("6️⃣  Running health monitoring...")
            health_result = await self.run_health_monitoring()
            results['tasks']['health_monitoring'] = health_result
            
            results['status'] = 'completed'
            results['completed_at'] = datetime.utcnow().isoformat()
            results['duration_seconds'] = (datetime.utcnow() - cycle_start).total_seconds()
            
            self.last_run = cycle_start
            
            # Save cycle results
            await self.db.maintenance_cycles.insert_one(results)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ MAINTENANCE CYCLE COMPLETED")
            logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
            logger.info(f"{'='*60}\n")
            
            return results
        
        except Exception as e:
            logger.error(f"Maintenance cycle error: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            return results
    
    async def run_automated_tests(self) -> Dict[str, Any]:
        """Run automated tests"""
        try:
            from automated_testing_orchestrator import get_testing_orchestrator
            
            orchestrator = get_testing_orchestrator()
            test_results = await orchestrator.run_full_test_suite()
            
            logger.info(f"   Tests: {test_results['overall_status']}")
            return {
                'status': 'success',
                'result': test_results['overall_status'],
                'tests_run': True
            }
        except Exception as e:
            logger.error(f"   Test execution error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_self_healing(self) -> Dict[str, Any]:
        """Run self-healing on broken stations"""
        try:
            from ai_radio_intelligence_bot import get_healing_bot
            
            healing_bot = get_healing_bot()
            
            # Get broken stations
            broken_stations = await self.db.radio_stations.find({
                'stream_accessible': False
            }).limit(100).to_list(length=100)
            
            healed_count = 0
            failed_count = 0
            
            for station in broken_stations:
                result = await healing_bot.heal_station(station)
                if result.get('status') == 'healed':
                    healed_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"   Healed: {healed_count}, Failed: {failed_count}")
            
            return {
                'status': 'success',
                'healed': healed_count,
                'failed': failed_count,
                'total_processed': len(broken_stations)
            }
        except Exception as e:
            logger.error(f"   Self-healing error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_data_discovery(self) -> Dict[str, Any]:
        """Run data discovery to find new stations"""
        try:
            from multi_source_crawler_manager import get_multi_crawler
            
            multi_crawler = get_multi_crawler()
            await multi_crawler.initialize_crawlers()
            
            # Get current count
            current_count = await self.db.radio_stations.count_documents({})
            
            # Discover 1000 new stations
            target = current_count + 1000
            result = await multi_crawler.crawl_all_sources(target)
            
            new_stations = result.get('final_count', current_count) - current_count
            
            logger.info(f"   Discovered: {new_stations} new stations")
            
            return {
                'status': 'success',
                'new_stations': new_stations,
                'total_stations': result.get('final_count', current_count)
            }
        except Exception as e:
            logger.error(f"   Data discovery error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_database_optimization(self) -> Dict[str, Any]:
        """Run database optimization tasks"""
        try:
            # Remove duplicate stations
            duplicates_removed = 0
            
            # Find duplicates by stream_url
            pipeline = [
                {'$group': {
                    '_id': '$stream_url',
                    'count': {'$sum': 1},
                    'ids': {'$push': '$_id'}
                }},
                {'$match': {'count': {'$gt': 1}}}
            ]
            
            duplicates = await self.db.radio_stations.aggregate(pipeline).to_list(length=1000)
            
            for dup in duplicates:
                # Keep first, remove others
                ids_to_remove = dup['ids'][1:]
                result = await self.db.radio_stations.delete_many({'_id': {'$in': ids_to_remove}})
                duplicates_removed += result.deleted_count
            
            # Rebuild indexes
            await self.db.radio_stations.create_index('stream_url')
            await self.db.radio_stations.create_index('country')
            await self.db.radio_stations.create_index('call_sign')
            
            logger.info(f"   Removed {duplicates_removed} duplicates, rebuilt indexes")
            
            return {
                'status': 'success',
                'duplicates_removed': duplicates_removed,
                'indexes_rebuilt': True
            }
        except Exception as e:
            logger.error(f"   Database optimization error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_system_cleanup(self) -> Dict[str, Any]:
        """Run system cleanup tasks"""
        try:
            # Clean old test results (keep last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = await self.db.test_results.delete_many({
                'started_at': {'$lt': cutoff_date.isoformat()}
            })
            
            # Clean old maintenance cycles (keep last 60 days)
            cutoff_maintenance = datetime.utcnow() - timedelta(days=60)
            
            result2 = await self.db.maintenance_cycles.delete_many({
                'started_at': {'$lt': cutoff_maintenance.isoformat()}
            })
            
            logger.info(f"   Cleaned {result.deleted_count + result2.deleted_count} old records")
            
            return {
                'status': 'success',
                'records_cleaned': result.deleted_count + result2.deleted_count
            }
        except Exception as e:
            logger.error(f"   System cleanup error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_health_monitoring(self) -> Dict[str, Any]:
        """Monitor system health"""
        try:
            from automated_testing_orchestrator import get_testing_orchestrator
            
            orchestrator = get_testing_orchestrator()
            health = await orchestrator.get_system_health()
            
            logger.info(f"   System health: {health['overall']}")
            
            return {
                'status': 'success',
                'health': health
            }
        except Exception as e:
            logger.error(f"   Health monitoring error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'interval_hours': self.interval_hours,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'time_until_next_run': str(self.next_run - datetime.utcnow()) if self.next_run else None
        }
    
    async def get_recent_cycles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent maintenance cycles"""
        cycles = await self.db.maintenance_cycles.find().sort(
            'started_at', -1
        ).limit(limit).to_list(length=limit)
        
        return [{
            'cycle_id': c.get('cycle_id'),
            'started_at': c.get('started_at'),
            'status': c.get('status'),
            'duration_seconds': c.get('duration_seconds'),
            'tasks_completed': len(c.get('tasks', {}))
        } for c in cycles]


# Global instance
scheduler_instance = None


def get_scheduler() -> AutomatedScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = AutomatedScheduler()
    return scheduler_instance
