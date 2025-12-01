"""Dragon Orchestral Automation
Complete integration of all APIs with intelligent automation
Manages the entire Dragon KARAU AI ecosystem
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

class DragonOrchestralAutomation:
    """Complete orchestral automation system"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Automation settings
        self.settings = {
            'auto_crawl_enabled': True,
            'auto_validate_enabled': True,
            'auto_heal_enabled': True,
            'auto_optimize_enabled': True,
            'min_stations_threshold': 10000,
            'max_stations_target': 15000,
            'validation_interval_hours': 6,
            'heal_interval_hours': 12,
            'optimize_interval_hours': 24,
            'crawl_interval_hours': 168  # Weekly
        }
        
        # State tracking
        self.state = {
            'last_crawl': None,
            'last_validation': None,
            'last_heal': None,
            'last_optimize': None,
            'is_auto_mode': True
        }
        
        logger.info("Dragon Orchestral Automation initialized")
    
    async def run_full_automation_cycle(self) -> Dict[str, Any]:
        """Execute complete automation cycle"""
        cycle_start = datetime.utcnow()
        logger.info("🎼 Starting Full Orchestral Automation Cycle")
        
        results = {
            'started_at': cycle_start.isoformat(),
            'tasks': {}
        }
        
        try:
            # Task 1: Check and maintain station count
            results['tasks']['station_maintenance'] = await self._maintain_station_count()
            
            # Task 2: Auto-validation
            results['tasks']['auto_validation'] = await self._auto_validation()
            
            # Task 3: Auto-healing
            results['tasks']['auto_healing'] = await self._auto_healing()
            
            # Task 4: Database optimization
            results['tasks']['database_optimization'] = await self._auto_optimization()
            
            # Task 5: Quality control
            results['tasks']['quality_control'] = await self._quality_control()
            
            # Task 6: Coverage analysis
            results['tasks']['coverage_analysis'] = await self._coverage_analysis()
            
            # Task 7: Performance monitoring
            results['tasks']['performance_monitoring'] = await self._performance_monitoring()
            
            duration = (datetime.utcnow() - cycle_start).total_seconds()
            results['completed_at'] = datetime.utcnow().isoformat()
            results['duration_seconds'] = duration
            results['status'] = 'success'
            
            # Save to history
            await self.db.automation_history.insert_one(results)
            
            logger.info(f"✅ Orchestral automation cycle completed in {duration:.1f}s")
            
        except Exception as e:
            logger.error(f"Orchestral automation error: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    async def _maintain_station_count(self) -> Dict[str, Any]:
        """Intelligent station count maintenance"""
        try:
            total_stations = await self.db.radio_stations.count_documents({})
            
            result = {
                'current_stations': total_stations,
                'action': 'none'
            }
            
            # Check if below threshold
            if total_stations < self.settings['min_stations_threshold']:
                logger.warning(f"Station count below threshold: {total_stations} < {self.settings['min_stations_threshold']}")
                
                if self.settings['auto_crawl_enabled']:
                    from dragon_ai_crawler_system import get_crawler
                    crawler = get_crawler()
                    
                    # Start aggressive crawl
                    target = self.settings['max_stations_target']
                    crawl_result = await crawler.start_global_crawl(target)
                    
                    result['action'] = 'crawl_initiated'
                    result['target'] = target
                    result['crawl_status'] = crawl_result
            
            # Check if approaching max
            elif total_stations > self.settings['max_stations_target']:
                logger.info(f"Station count optimal: {total_stations}")
                result['action'] = 'maintenance_mode'
            
            else:
                logger.info(f"Station count healthy: {total_stations}")
                result['action'] = 'healthy'
            
            return {'status': 'success', 'data': result}
        
        except Exception as e:
            logger.error(f"Station maintenance error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _auto_validation(self) -> Dict[str, Any]:
        """Automatic station validation"""
        try:
            if not self.settings['auto_validate_enabled']:
                return {'status': 'skipped', 'reason': 'Auto-validation disabled'}
            
            # Check if validation is due
            if self.state['last_validation']:
                time_since = datetime.utcnow() - self.state['last_validation']
                if time_since < timedelta(hours=self.settings['validation_interval_hours']):
                    return {'status': 'skipped', 'reason': 'Not due yet'}
            
            from relaxed_station_validator import RelaxedStationValidator
            
            validator = RelaxedStationValidator()
            result = await validator.validate_all_stations()
            
            self.state['last_validation'] = datetime.utcnow()
            
            return {'status': 'success', 'data': result}
        
        except Exception as e:
            logger.error(f"Auto-validation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _auto_healing(self) -> Dict[str, Any]:
        """Automatic station healing"""
        try:
            if not self.settings['auto_heal_enabled']:
                return {'status': 'skipped', 'reason': 'Auto-healing disabled'}
            
            # Check if healing is due
            if self.state['last_heal']:
                time_since = datetime.utcnow() - self.state['last_heal']
                if time_since < timedelta(hours=self.settings['heal_interval_hours']):
                    return {'status': 'skipped', 'reason': 'Not due yet'}
            
            from ai_radio_intelligence_bot import get_bot
            
            bot = get_bot()
            
            # Scan random sample of 50 stations
            stations = await self.db.radio_stations.aggregate([
                {'$sample': {'size': 50}}
            ]).to_list(length=50)
            
            validated = 0
            healed = 0
            
            for station in stations:
                validation = await bot.validate_station(station)
                
                if not validation.get('accessible', False):
                    # Try to heal
                    heal_result = await bot.heal_station(station)
                    if heal_result.get('status') == 'healed':
                        healed += 1
                else:
                    validated += 1
            
            self.state['last_heal'] = datetime.utcnow()
            
            return {
                'status': 'success',
                'data': {
                    'stations_checked': len(stations),
                    'operational': validated,
                    'healed': healed
                }
            }
        
        except Exception as e:
            logger.error(f"Auto-healing error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _auto_optimization(self) -> Dict[str, Any]:
        """Automatic database optimization"""
        try:
            if not self.settings['auto_optimize_enabled']:
                return {'status': 'skipped', 'reason': 'Auto-optimization disabled'}
            
            # Check if optimization is due
            if self.state['last_optimize']:
                time_since = datetime.utcnow() - self.state['last_optimize']
                if time_since < timedelta(hours=self.settings['optimize_interval_hours']):
                    return {'status': 'skipped', 'reason': 'Not due yet'}
            
            from database_optimizer import DatabaseOptimizer
            
            optimizer = DatabaseOptimizer()
            result = await optimizer.run_full_optimization()
            
            self.state['last_optimize'] = datetime.utcnow()
            
            return {'status': 'success', 'data': result}
        
        except Exception as e:
            logger.error(f"Auto-optimization error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _quality_control(self) -> Dict[str, Any]:
        """Quality control checks"""
        try:
            # Check quality distribution
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
            
            quality_dist = await self.db.radio_stations.aggregate(quality_pipeline).to_list(length=10)
            
            # Check for low-quality stations
            low_quality = await self.db.radio_stations.count_documents({'quality_score': {'$lt': 40}})
            
            return {
                'status': 'success',
                'data': {
                    'quality_distribution': quality_dist,
                    'low_quality_stations': low_quality,
                    'recommendation': 'review_low_quality' if low_quality > 100 else 'quality_good'
                }
            }
        
        except Exception as e:
            logger.error(f"Quality control error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _coverage_analysis(self) -> Dict[str, Any]:
        """Geographic coverage analysis"""
        try:
            from country_coverage_analysis import CountryCoverageAnalyzer
            
            analyzer = CountryCoverageAnalyzer()
            coverage = await analyzer.analyze_coverage()
            
            # Find underrepresented regions
            countries_needing_stations = await analyzer.get_countries_needing_stations(min_stations=10)
            
            return {
                'status': 'success',
                'data': {
                    **coverage,
                    'underrepresented_countries': len(countries_needing_stations)
                }
            }
        
        except Exception as e:
            logger.error(f"Coverage analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _performance_monitoring(self) -> Dict[str, Any]:
        """Monitor system performance"""
        try:
            # Get database stats
            stats = await self.db.command('dbStats')
            
            # Get collection sizes
            collections_stats = {}
            for collection in ['radio_stations', 'orchestrator_history', 'crawler_history']:
                count = await self.db[collection].count_documents({})
                collections_stats[collection] = count
            
            return {
                'status': 'success',
                'data': {
                    'database_size_mb': stats.get('dataSize', 0) / 1024 / 1024,
                    'collections': collections_stats,
                    'indexes': stats.get('indexes', 0)
                }
            }
        
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return {
            'settings': self.settings,
            'state': {
                **self.state,
                'last_crawl': self.state['last_crawl'].isoformat() if self.state['last_crawl'] else None,
                'last_validation': self.state['last_validation'].isoformat() if self.state['last_validation'] else None,
                'last_heal': self.state['last_heal'].isoformat() if self.state['last_heal'] else None,
                'last_optimize': self.state['last_optimize'].isoformat() if self.state['last_optimize'] else None
            },
            'current_status': 'active' if self.state['is_auto_mode'] else 'manual'
        }
    
    async def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation settings"""
        try:
            self.settings.update(new_settings)
            
            # Save to database
            await self.db.automation_settings.update_one(
                {'_id': 'default'},
                {'$set': {**self.settings, 'updated_at': datetime.utcnow()}},
                upsert=True
            )
            
            return {'status': 'success', 'settings': self.settings}
        except Exception as e:
            logger.error(f"Settings update error: {e}")
            return {'status': 'error', 'error': str(e)}


# Global automation instance
automation_instance = None

def get_automation() -> DragonOrchestralAutomation:
    """Get or create automation instance"""
    global automation_instance
    if automation_instance is None:
        automation_instance = DragonOrchestralAutomation()
    return automation_instance
