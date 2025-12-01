"""Kagema Dragon AI Orchestrator
Master control system that coordinates all AI modules
Runs daily at 3:00 AM
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class KagemaDragonAIOrchestrator:
    """Master orchestrator for all Dragon AI systems"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        self.status = 'idle'
        self.current_task = None
        self.last_run = None
        self.cycle_count = 0
        
        # Task definitions
        self.tasks = [
            {'name': 'Discovery Engine', 'function': self._task_discovery_engine},
            {'name': 'Satellite Scanner', 'function': self._task_satellite_scanner},
            {'name': 'Linguistic Matcher', 'function': self._task_linguistic_matcher},
            {'name': 'Health Monitor', 'function': self._task_health_monitor},
            {'name': 'Testing Automator', 'function': self._task_testing_automator},
            {'name': 'UI Automated Testing', 'function': self._task_ui_testing},
            {'name': 'CAPA Analysis', 'function': self._task_capa_analysis}
        ]
        
        logger.info("Kagema Dragon AI Orchestrator initialized")
    
    async def run_daily_maintenance_cycle(self) -> Dict[str, Any]:
        """Execute complete daily maintenance cycle (7 tasks)"""
        self.status = 'running'
        self.cycle_count += 1
        cycle_start = datetime.utcnow()
        
        logger.info(f"🐉 Starting Dragon AI Maintenance Cycle #{self.cycle_count}")
        
        results = {
            'cycle_number': self.cycle_count,
            'started_at': cycle_start.isoformat(),
            'tasks': []
        }
        
        # Execute all 7 tasks in sequence
        for i, task in enumerate(self.tasks, 1):
            self.current_task = task['name']
            logger.info(f"Task {i}/7: {task['name']}")
            
            task_result = await task['function']()
            task_result['task_number'] = i
            task_result['task_name'] = task['name']
            results['tasks'].append(task_result)
            
            # Brief delay between tasks
            await asyncio.sleep(1)
        
        self.status = 'completed'
        self.last_run = datetime.utcnow()
        self.current_task = None
        
        duration = (datetime.utcnow() - cycle_start).total_seconds()
        results['completed_at'] = datetime.utcnow().isoformat()
        results['duration_seconds'] = duration
        results['status'] = 'success'
        
        # Store in database
        await self.db.orchestrator_history.insert_one(results)
        
        logger.info(f"✅ Dragon AI Cycle #{self.cycle_count} completed in {duration:.1f}s")
        
        return results
    
    async def _task_discovery_engine(self) -> Dict[str, Any]:
        """Task 1: Station Discovery - Dragon AI Crawler Integration"""
        try:
            from dragon_ai_crawler_system import get_crawler
            
            crawler = get_crawler()
            
            # Get current station count
            current_total = await self.db.radio_stations.count_documents({})
            
            # Smart discovery strategy
            if current_total < 1000:
                # Low stations - aggressive crawl
                logger.info("Low station count - starting aggressive crawl")
                target = 5000
                result = await self._run_aggressive_crawl(crawler, target)
            elif current_total < 5000:
                # Medium stations - moderate crawl
                logger.info("Medium station count - crawling 20 countries")
                result = await self._run_moderate_crawl(crawler, 20)
            elif current_total < 12500:
                # Approaching target - fill gaps
                logger.info("Approaching target - filling coverage gaps")
                result = await self._run_gap_filling_crawl(crawler)
            else:
                # Maintenance mode - refresh existing
                logger.info("Maintenance mode - refreshing top countries")
                result = await self._run_refresh_crawl(crawler, 10)
            
            return {
                'status': 'success',
                'mode': result.get('mode', 'unknown'),
                'stations_discovered': result.get('discovered', 0),
                'stations_saved': result.get('saved', 0),
                'countries_crawled': result.get('countries', 0),
                'total_in_db': current_total + result.get('saved', 0)
            }
        except Exception as e:
            logger.error(f"Discovery Engine error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _run_aggressive_crawl(self, crawler, target: int) -> Dict[str, Any]:
        """Aggressive crawl for rapid station discovery"""
        # Crawl multiple continents
        continents = ['africa', 'europe', 'asia']
        total_discovered = 0
        total_saved = 0
        countries_crawled = 0
        
        for continent in continents:
            result = await crawler.crawl_continent(continent)
            total_discovered += result.get('total_discovered', 0)
            total_saved += result.get('total_saved', 0)
            countries_crawled += result.get('countries_crawled', 0)
            
            # Check if we reached target
            current = await self.db.radio_stations.count_documents({})
            if current >= target:
                break
        
        return {
            'mode': 'aggressive',
            'discovered': total_discovered,
            'saved': total_saved,
            'countries': countries_crawled
        }
    
    async def _run_moderate_crawl(self, crawler, num_countries: int) -> Dict[str, Any]:
        """Moderate crawl for steady growth"""
        # Get countries with fewer stations
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': 1}},
            {'$limit': num_countries}
        ]
        
        countries_to_crawl = await self.db.radio_stations.aggregate(pipeline).to_list(length=num_countries)
        
        total_discovered = 0
        total_saved = 0
        
        for country_data in countries_to_crawl:
            country = country_data['_id']
            result = await crawler.crawl_specific_country(country)
            total_discovered += result.get('discovered', 0)
            total_saved += result.get('saved', 0)
        
        return {
            'mode': 'moderate',
            'discovered': total_discovered,
            'saved': total_saved,
            'countries': len(countries_to_crawl)
        }
    
    async def _run_gap_filling_crawl(self, crawler) -> Dict[str, Any]:
        """Fill coverage gaps in underrepresented regions"""
        # Find countries with < 5 stations
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$match': {'count': {'$lt': 5}}},
            {'$limit': 30}
        ]
        
        gap_countries = await self.db.radio_stations.aggregate(pipeline).to_list(length=30)
        
        total_discovered = 0
        total_saved = 0
        
        for country_data in gap_countries:
            country = country_data['_id']
            result = await crawler.crawl_specific_country(country)
            total_discovered += result.get('discovered', 0)
            total_saved += result.get('saved', 0)
        
        return {
            'mode': 'gap_filling',
            'discovered': total_discovered,
            'saved': total_saved,
            'countries': len(gap_countries)
        }
    
    async def _run_refresh_crawl(self, crawler, num_countries: int) -> Dict[str, Any]:
        """Refresh top countries for new stations"""
        # Get top countries by station count
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': num_countries}
        ]
        
        top_countries = await self.db.radio_stations.aggregate(pipeline).to_list(length=num_countries)
        
        total_discovered = 0
        total_saved = 0
        
        for country_data in top_countries:
            country = country_data['_id']
            result = await crawler.crawl_specific_country(country)
            total_discovered += result.get('discovered', 0)
            total_saved += result.get('saved', 0)
        
        return {
            'mode': 'refresh',
            'discovered': total_discovered,
            'saved': total_saved,
            'countries': len(top_countries)
        }
    
    async def _task_satellite_scanner(self) -> Dict[str, Any]:
        """Task 2: Stream Monitoring"""
        try:
            # Check health of random sample of stations
            from ai_radio_intelligence_bot import get_bot
            
            bot = get_bot()
            
            # Get 20 random stations
            stations = await self.db.radio_stations.aggregate([
                {'$sample': {'size': 20}}
            ]).to_list(length=20)
            
            validated = 0
            broken = 0
            
            for station in stations:
                validation = await bot.validate_station(station)
                if validation.get('accessible', False):
                    validated += 1
                else:
                    broken += 1
            
            return {
                'status': 'success',
                'stations_checked': len(stations),
                'operational': validated,
                'broken': broken
            }
        except Exception as e:
            logger.error(f"Satellite Scanner error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _task_linguistic_matcher(self) -> Dict[str, Any]:
        """Task 3: Metadata Enhancement"""
        try:
            # Enhance metadata for stations missing language or genre
            updated = 0
            
            # Find stations with missing metadata
            cursor = self.db.radio_stations.find({
                '$or': [
                    {'language': {'$in': [None, '']}},
                    {'genre': {'$in': [None, '']}}
                ]
            }).limit(50)
            
            async for station in cursor:
                # Simple enhancement logic
                updates = {}
                
                if not station.get('language'):
                    updates['language'] = 'en'  # Default to English
                
                if not station.get('genre'):
                    updates['genre'] = 'General'
                
                if updates:
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': updates}
                    )
                    updated += 1
            
            return {
                'status': 'success',
                'stations_enhanced': updated
            }
        except Exception as e:
            logger.error(f"Linguistic Matcher error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _task_health_monitor(self) -> Dict[str, Any]:
        """Task 4: System Health Checks"""
        try:
            # Check system health
            total_stations = await self.db.radio_stations.count_documents({})
            validated = await self.db.radio_stations.count_documents({'validated': True})
            operational = await self.db.radio_stations.count_documents({'health_status': 'OPERATIONAL'})
            
            # Check database connectivity
            await self.db.command('ping')
            
            health_status = 'healthy' if (validated / total_stations) > 0.8 else 'degraded'
            
            return {
                'status': 'success',
                'system_health': health_status,
                'total_stations': total_stations,
                'validated_stations': validated,
                'operational_stations': operational,
                'database': 'connected'
            }
        except Exception as e:
            logger.error(f"Health Monitor error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _task_testing_automator(self) -> Dict[str, Any]:
        """Task 5: Radio Bot Testing"""
        try:
            from ai_radio_intelligence_bot import get_bot
            
            bot = get_bot()
            status = await bot.get_status()
            
            return {
                'status': 'success',
                'bot_status': status['status'],
                'statistics': status['statistics']
            }
        except Exception as e:
            logger.error(f"Testing Automator error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _task_ui_testing(self) -> Dict[str, Any]:
        """Task 6: UI Automated Testing (Dragon Karau AI)"""
        try:
            from dragon_karau_ui_automator import dragon_ui_automator
            
            result = await dragon_ui_automator.run_full_ui_test_suite()
            
            return {
                'status': 'success',
                'total_tests': result.get('total_tests', 0),
                'passed_tests': result.get('passed_tests', 0),
                'failed_tests': result.get('failed_tests', 0),
                'success_rate': result.get('success_rate', 0)
            }
        except Exception as e:
            logger.error(f"UI Testing error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _task_capa_analysis(self) -> Dict[str, Any]:
        """Task 7: CAPA Analysis (Issue Resolution)"""
        try:
            # Analyze recent issues and create CAPA records
            issues_found = 0
            resolved = 0
            
            # Check for recent failures
            recent_history = await self.db.orchestrator_history.find(
                {'cycle_number': {'$gte': self.cycle_count - 5}}
            ).to_list(length=5)
            
            for history in recent_history:
                for task in history.get('tasks', []):
                    if task.get('status') == 'error':
                        issues_found += 1
                        
                        # Log to CAPA history
                        await self.db.capa_history.insert_one({
                            'task_name': task.get('task_name'),
                            'error': task.get('error'),
                            'cycle_number': history.get('cycle_number'),
                            'timestamp': datetime.utcnow(),
                            'status': 'open'
                        })
            
            return {
                'status': 'success',
                'issues_found': issues_found,
                'issues_resolved': resolved
            }
        except Exception as e:
            logger.error(f"CAPA Analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'status': self.status,
            'current_task': self.current_task,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'cycle_count': self.cycle_count,
            'total_tasks': len(self.tasks)
        }
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get orchestrator history"""
        cursor = self.db.orchestrator_history.find().sort('started_at', -1).limit(limit)
        history = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for JSON serialization
        for item in history:
            item.pop('_id', None)
        
        return history


# Global orchestrator instance
orchestrator_instance = None


def get_orchestrator() -> KagemaDragonAIOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator_instance
    if orchestrator_instance is None:
        orchestrator_instance = KagemaDragonAIOrchestrator()
    return orchestrator_instance


async def schedule_daily_maintenance():
    """Schedule daily maintenance at 3:00 AM"""
    orchestrator = get_orchestrator()
    
    while True:
        now = datetime.now()
        target_time = time(3, 0)  # 3:00 AM
        
        # Calculate seconds until 3:00 AM
        target_datetime = datetime.combine(now.date(), target_time)
        if now.time() > target_time:
            # If past 3 AM today, schedule for tomorrow
            from datetime import timedelta
            target_datetime += timedelta(days=1)
        
        seconds_until_run = (target_datetime - now).total_seconds()
        
        logger.info(f"Next Dragon AI maintenance cycle in {seconds_until_run/3600:.1f} hours")
        
        # Wait until 3:00 AM
        await asyncio.sleep(seconds_until_run)
        
        # Run maintenance cycle
        try:
            await orchestrator.run_daily_maintenance_cycle()
        except Exception as e:
            logger.error(f"Maintenance cycle error: {e}")
        
        # Sleep 1 minute to avoid running twice
        await asyncio.sleep(60)
