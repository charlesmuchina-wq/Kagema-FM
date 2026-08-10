"""Automated Scheduler
Runs self-healing, self-maintenance, and data discovery every 6 hours
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
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
        
        # Schedule interval (12 hours)
        self.interval_hours = 12
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
        logger.info("🔧 AUTOMATED MAINTENANCE CYCLE STARTED")
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
            
            # Task 7: Station Geocoding (NEW - Phase 1 Integration)
            logger.info("7️⃣  Running station geocoding...")
            geocoding_result = await self.run_station_geocoding()
            results['tasks']['station_geocoding'] = geocoding_result
            
            # Task 8: Routing & Navigation Integration (NEW)
            logger.info("8️⃣  Validating routing & navigation...")
            routing_result = await self.validate_routing_integration()
            results['tasks']['routing_validation'] = routing_result
            
            # Task 9: Satellite Connectivity Check (NEW)
            logger.info("9️⃣  Checking satellite connectivity...")
            satellite_result = await self.check_satellite_connectivity()
            results['tasks']['satellite_check'] = satellite_result
            
            # Task 10: Distance Matrix Updates (NEW - Distance Matrix Integration)
            logger.info("🔟  Updating station distances...")
            distance_result = await self.update_station_distances()
            results['tasks']['distance_matrix_update'] = distance_result
            
            # Task 11: Metadata Enrichment (NEW - Genres, Languages, Descriptions)
            logger.info("1️⃣1️⃣  Enriching station metadata...")
            metadata_result = await self.enrich_station_metadata()
            results['tasks']['metadata_enrichment'] = metadata_result
            
            # Task 12: Stream Validation (NEW - Verify stream URLs)
            logger.info("1️⃣2️⃣  Validating radio streams...")
            stream_result = await self.validate_radio_streams()
            results['tasks']['stream_validation'] = stream_result
            
            # Task 13: Radio-Browser.info Integration (NEW - Expand station database)
            logger.info("1️⃣3️⃣  Crawling Radio-Browser.info...")
            radio_browser_result = await self.crawl_radio_browser_info()
            results['tasks']['radio_browser_crawl'] = radio_browser_result
            
            # Task 14: CAPA Execution (NEW - Corrective & Preventive Actions)
            logger.info("1️⃣4️⃣  Running CAPA (Corrective & Preventive Actions)...")
            capa_result = await self.run_capa_actions()
            results['tasks']['capa_execution'] = capa_result
            
            # Task 15: UI Feature Testing (NEW - Automated UI testing)
            logger.info("1️⃣5️⃣  Testing UI features...")
            ui_result = await self.run_ui_testing()
            results['tasks']['ui_testing'] = ui_result
            
            # Task 16: Content Compliance Automation (NEW - Content rating)
            logger.info("1️⃣6️⃣  Running content compliance checks...")
            compliance_result = await self.run_content_compliance()
            results['tasks']['content_compliance'] = compliance_result
            
            # Task 17: Duplicate Detection (NEW - Deduplication)
            logger.info("1️⃣7️⃣  Detecting and removing duplicates...")
            dedup_result = await self.run_duplicate_detection()
            results['tasks']['duplicate_detection'] = dedup_result
            
            # Task 18: Enhanced Standards (NEW - Bitrate, reliability, broadcasting)
            logger.info("1️⃣8️⃣  Enhancing station standards...")
            standards_result = await self.enhance_station_standards()
            results['tasks']['enhanced_standards'] = standards_result
            
            # Task 19: Mobile Platform Testing (NEW - iOS/Android automation)
            logger.info("1️⃣9️⃣  Testing mobile platforms (iOS/Android)...")
            mobile_result = await self.run_mobile_platform_testing()
            results['tasks']['mobile_testing'] = mobile_result
            
            # Task 20: Performance Optimization (NEW - API/DB optimization)
            logger.info("2️⃣0️⃣  Running performance optimization...")
            perf_result = await self.run_performance_optimization()
            results['tasks']['performance_optimization'] = perf_result
            
            # Task 21: Analytics Dashboard (PHASE 2 - Real-time analytics)
            logger.info("2️⃣1️⃣  Collecting analytics data...")
            analytics_result = await self.run_analytics_collection()
            results['tasks']['analytics_collection'] = analytics_result
            
            # Task 22: Real-Time Monitoring (PHASE 2 - System monitoring)
            logger.info("2️⃣2️⃣  Running real-time monitoring...")
            monitoring_result = await self.run_real_time_monitoring()
            results['tasks']['real_time_monitoring'] = monitoring_result
            
            # Task 23: A/B Testing Framework (PHASE 2 - Experimentation)
            logger.info("2️⃣3️⃣  Managing A/B experiments...")
            ab_test_result = await self.run_ab_testing()
            results['tasks']['ab_testing'] = ab_test_result
            
            # Task 24: Content Compliance (PHASE 2 - Policy enforcement)
            logger.info("2️⃣4️⃣  Running content compliance checks...")
            compliance_result = await self.run_content_compliance()
            results['tasks']['content_compliance'] = compliance_result
            
            # Task 25: User Feedback Processing (PHASE 2 - Feedback management)
            logger.info("2️⃣5️⃣  Processing user feedback...")
            feedback_result = await self.run_user_feedback_processing()
            results['tasks']['user_feedback'] = feedback_result
            
            results['status'] = 'completed'
            results['completed_at'] = datetime.utcnow().isoformat()
            results['duration_seconds'] = (datetime.utcnow() - cycle_start).total_seconds()
            
            self.last_run = cycle_start
            
            # Save cycle results
            await self.db.maintenance_cycles.insert_one(results)
            
            logger.info(f"\n{'='*60}")
            logger.info("✅ MAINTENANCE CYCLE COMPLETED")
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
            from ai_radio_intelligence_bot import get_bot
            
            healing_bot = get_bot()
            
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
        """Run comprehensive AI-powered data discovery"""
        logger.info("   🤖 Running AI Crawler for station updates...")
        
        try:
            from multi_source_crawler_manager import get_multi_crawler
            from dragon_ai_crawler_system import get_crawler
            from call_sign_standardizer import get_call_sign_standardizer
            from non_standard_station_formatter import get_non_standard_formatter
            from division_geocoder import get_division_geocoder
            
            results = {
                'multi_source_crawl': {},
                'dragon_ai_crawl': {},
                'standardization': {},
                'division_assignment': {}
            }
            
            # Get current count and stats
            current_count = await self.db.radio_stations.count_documents({})
            countries_before = len(await self.db.radio_stations.distinct('country'))
            
            logger.info(f"   Current: {current_count} stations, {countries_before} countries")
            
            # Step 1: Multi-Source Discovery (1000 new stations)
            logger.info("   Step 1: Multi-source discovery...")
            multi_crawler = get_multi_crawler()
            await multi_crawler.initialize_crawlers()
            
            target = current_count + 1000
            multi_result = await multi_crawler.crawl_all_sources(target)
            
            results['multi_source_crawl'] = {
                'status': 'success',
                'new_stations': multi_result.get('final_count', current_count) - current_count,
                'sources': multi_result.get('sources', {})
            }
            
            # Step 2: Dragon AI Crawler for comprehensive updates
            logger.info("   Step 2: Dragon AI crawler update...")
            dragon_crawler = get_crawler()
            
            # Start global crawl for comprehensive coverage
            await dragon_crawler.start_global_crawl(target_stations=target + 500)
            
            # Wait for completion (with timeout)
            max_wait = 180  # 3 minutes
            elapsed = 0
            while elapsed < max_wait:
                status = await dragon_crawler.get_status()
                if not status['is_running']:
                    break
                await asyncio.sleep(10)
                elapsed += 10
            
            dragon_stats = await dragon_crawler.get_statistics()
            
            results['dragon_ai_crawl'] = {
                'status': 'completed',
                'stations_crawled': dragon_stats.get('total_stations', 0),
                'countries_covered': dragon_stats.get('unique_countries', 0)
            }
            
            # Step 3: Auto-standardize new stations
            logger.info("   Step 3: Auto-standardizing new stations...")
            
            # Get unstandardized stations
            unstandardized = await self.db.radio_stations.count_documents({
                '$or': [
                    {'call_sign': {'$exists': False}},
                    {'standard_id': {'$exists': False}}
                ]
            })
            
            if unstandardized > 0:
                # Call sign standardization
                call_sign_std = get_call_sign_standardizer()
                
                # Process in batches
                stations = await self.db.radio_stations.find({
                    'call_sign': {'$exists': False}
                }).limit(500).to_list(length=500)
                
                standardized_count = 0
                for station in stations:
                    await call_sign_std.standardize_station(station)
                    standardized_count += 1
                
                # Non-standard formatting
                formatter = get_non_standard_formatter()
                stations_without_callsign = await self.db.radio_stations.find({
                    '$and': [
                        {'call_sign': {'$exists': False}},
                        {'standard_id': {'$exists': False}}
                    ]
                }).limit(500).to_list(length=500)
                
                formatted_count = 0
                for station in stations_without_callsign:
                    await formatter.format_station(station)
                    formatted_count += 1
                
                results['standardization'] = {
                    'status': 'success',
                    'call_signs_added': standardized_count,
                    'custom_formats_added': formatted_count
                }
            else:
                results['standardization'] = {
                    'status': 'skipped',
                    'reason': 'all_stations_standardized'
                }
            
            # Step 4: Assign divisions to new stations
            logger.info("   Step 4: Assigning geographic divisions...")
            
            geocoder = get_division_geocoder()
            
            # Get stations without divisions
            stations_no_division = await self.db.radio_stations.find({
                'division_level1_id': {'$exists': False}
            }).limit(200).to_list(length=200)
            
            division_assigned = 0
            for station in stations_no_division:
                result = await geocoder.assign_division_to_station(station)
                if result.get('status') == 'success':
                    division_assigned += 1
            
            results['division_assignment'] = {
                'status': 'success',
                'divisions_assigned': division_assigned,
                'processed': len(stations_no_division)
            }
            
            # Final stats
            final_count = await self.db.radio_stations.count_documents({})
            countries_after = len(await self.db.radio_stations.distinct('country'))
            
            total_new = final_count - current_count
            new_countries = countries_after - countries_before
            
            logger.info(f"   ✅ Discovery complete: +{total_new} stations, +{new_countries} countries")
            logger.info(f"   Total: {final_count} stations, {countries_after} countries")
            
            return {
                'status': 'success',
                'summary': {
                    'new_stations': total_new,
                    'new_countries': new_countries,
                    'total_stations': final_count,
                    'total_countries': countries_after
                },
                'details': results
            }
        
        except Exception as e:
            logger.error(f"   AI Crawler error: {e}")
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


    
    async def run_station_geocoding(self) -> Dict[str, Any]:
        """
        Task 7: Add latitude/longitude coordinates to stations
        Integrates with Geoapify Geocoding API
        """
        try:
            from station_geocoding_service import get_geocoding_service
            
            logger.info("   Running station geocoding service...")
            
            geocoding_service = get_geocoding_service()
            
            # Get current stats
            stats_before = await geocoding_service.get_geocoding_stats()
            not_geocoded_before = stats_before['stats']['not_geocoded']
            
            if not_geocoded_before > 0:
                logger.info(f"   Found {not_geocoded_before} stations without coordinates")
                
                # Geocode batch (200 stations per maintenance cycle - accelerated)
                result = await geocoding_service.geocode_stations_batch(
                    limit=200,
                    skip_geocoded=True
                )
                
                # Get updated stats
                stats_after = await geocoding_service.get_geocoding_stats()
                
                logger.info(f"   ✅ Geocoded: {result['stats']['successful_geocodes']} stations")
                logger.info(f"   📍 Total geocoded: {stats_after['stats']['geocoded']}/{stats_after['stats']['total_stations']}")
                
                return {
                    'status': 'success',
                    'geocoded_this_cycle': result['stats']['successful_geocodes'],
                    'total_geocoded': stats_after['stats']['geocoded'],
                    'percentage_complete': stats_after['stats']['percentage_geocoded']
                }
            else:
                logger.info("   ✅ All stations already have coordinates")
                return {
                    'status': 'success',
                    'message': 'All stations geocoded',
                    'percentage_complete': 100
                }
                
        except Exception as e:
            logger.error(f"   Geocoding error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def validate_routing_integration(self) -> Dict[str, Any]:
        """
        Task 8: Validate routing & navigation integration
        Ensures all APIs are working correctly
        """
        try:
            from routing_directions import get_routing_manager
            
            logger.info("   Validating routing & navigation APIs...")
            
            routing_mgr = get_routing_manager()
            
            # Test geocoding
            geocode_test = await routing_mgr.geocode_address(
                "New York City",
                provider='geoapify'
            )
            
            # Test route calculation (NYC to Boston)
            route_test = await routing_mgr.get_route(
                40.7128, -74.0060,  # New York
                42.3601, -71.0589,  # Boston
                mode='drive',
                provider='geoapify'
            )
            
            validation_results = {
                'geocoding_api': 'working' if geocode_test.get('success') else 'failed',
                'routing_api': 'working' if route_test.get('success') else 'failed',
                'geoapify_configured': bool(routing_mgr.geoapify_routing_key),
                'tomtom_configured': bool(routing_mgr.tomtom_key)
            }
            
            all_working = all(
                v == 'working' for k, v in validation_results.items() 
                if k.endswith('_api')
            )
            
            if all_working:
                logger.info("   ✅ All routing APIs working")
            else:
                logger.warning(f"   ⚠️ Some routing APIs failed: {validation_results}")
            
            return {
                'status': 'success' if all_working else 'warning',
                'validation': validation_results
            }
            
        except Exception as e:
            logger.error(f"   Routing validation error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_satellite_connectivity(self) -> Dict[str, Any]:
        """
        Task 9: Check satellite connectivity status
        Monitors satellite provider availability
        """
        try:
            from satellite_radio_research import get_satellite_research
            
            logger.info("   Checking satellite connectivity...")
            
            satellite_research = get_satellite_research()
            
            # Get provider status
            providers_status = await satellite_research.get_satellite_providers()
            
            # Get satellite research status
            research_status = await satellite_research.get_satellite_radio_status()
            
            active_providers = len([
                p for p in providers_status['data']['providers'].values()
                if p.get('status') == 'operational'
            ])
            
            logger.info(f"   ✅ {active_providers} satellite providers operational")
            
            return {
                'status': 'success',
                'active_providers': active_providers,
                'research_status': research_status['data']['research_status']
            }
            
        except Exception as e:
            logger.error(f"   Satellite check error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def update_station_distances(self) -> Dict[str, Any]:
        """
        Task 10: Update station distance calculations
        Uses Distance Matrix API to calculate and cache distances between popular locations
        """
        try:
            from routing_directions import get_routing_manager
            
            logger.info("   Running Distance Matrix updates...")
            
            routing_mgr = get_routing_manager()
            
            # Check if Distance Matrix API is configured
            if not routing_mgr.distance_matrix_key:
                logger.warning("   ⚠️ Distance Matrix API key not configured")
                return {
                    'status': 'skipped',
                    'reason': 'API key not configured'
                }
            
            # Get sample of geocoded stations (limit to avoid excessive API calls)
            stations_with_coords = await self.db.radio_stations.find({
                'latitude': {'$exists': True, '$ne': None},
                'longitude': {'$exists': True, '$ne': None}
            }).limit(50).to_list(length=50)
            
            if len(stations_with_coords) < 2:
                logger.info("   ℹ️ Not enough geocoded stations for distance calculations")
                return {
                    'status': 'skipped',
                    'reason': 'insufficient_geocoded_stations',
                    'geocoded_count': len(stations_with_coords)
                }
            
            # Test Distance Matrix API with a small sample
            test_stations = stations_with_coords[:5]
            test_sources = [(s['latitude'], s['longitude']) for s in test_stations[:2]]
            test_targets = [(s['latitude'], s['longitude']) for s in test_stations[2:5]]
            
            logger.info(f"   Testing Distance Matrix API with {len(test_sources)} sources and {len(test_targets)} targets...")
            
            matrix_result = await routing_mgr.calculate_distance_matrix(
                sources=test_sources,
                targets=test_targets,
                mode='drive'
            )
            
            if matrix_result.get('success'):
                logger.info(f"   ✅ Distance Matrix API working - calculated {len(test_sources)}x{len(test_targets)} matrix")
                
                # Store distance matrix metadata in database with TTL (7 days)
                await self.db.distance_matrix_cache.insert_one({
                    'created_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(days=7),
                    'sources_count': len(test_sources),
                    'targets_count': len(test_targets),
                    'mode': 'drive',
                    'provider': 'geoapify',
                    'matrix_size': len(test_sources) * len(test_targets),
                    'status': 'success',
                    'ttl_days': 7
                })
                
                # Clean up expired cache entries (older than 7 days)
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                deleted = await self.db.distance_matrix_cache.delete_many({
                    'created_at': {'$lt': cutoff_date}
                })
                
                if deleted.deleted_count > 0:
                    logger.info(f"   🗑️ Cleaned {deleted.deleted_count} expired cache entries")
                
                return {
                    'status': 'success',
                    'api_status': 'operational',
                    'test_matrix_size': f"{len(test_sources)}x{len(test_targets)}",
                    'geocoded_stations': len(stations_with_coords)
                }
            else:
                logger.error(f"   ❌ Distance Matrix API test failed: {matrix_result.get('error')}")
                return {
                    'status': 'error',
                    'error': matrix_result.get('error'),
                    'geocoded_stations': len(stations_with_coords)
                }
            
        except Exception as e:
            logger.error(f"   Distance Matrix update error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def enrich_station_metadata(self) -> Dict[str, Any]:
        """
        Task 11: Enrich station metadata
        Adds genres, languages, bitrate, and descriptions to stations
        """
        try:
            from station_metadata_enrichment import get_enrichment_service
            
            logger.info("   Running metadata enrichment...")
            
            enrichment = get_enrichment_service()
            await enrichment.connect()
            
            # Enrich batch of 100 stations
            result = await enrichment.enrich_batch(limit=100)
            
            await enrichment.close()
            
            if result.get('status') == 'success':
                enriched = result.get('enriched', 0)
                logger.info(f"   ✅ Enriched {enriched} stations with metadata")
                return {
                    'status': 'success',
                    'enriched': enriched,
                    'failed': result.get('failed', 0)
                }
            else:
                logger.error(f"   ❌ Metadata enrichment failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"   Metadata enrichment error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def validate_radio_streams(self) -> Dict[str, Any]:
        """
        Task 12: Validate radio stream URLs
        Tests stream health, identifies broken streams
        """
        try:
            from stream_validation_service import get_validation_service
            
            logger.info("   Running stream validation...")
            
            validation = get_validation_service()
            await validation.connect()
            
            # Validate batch of 50 streams (to avoid overloading)
            result = await validation.validate_batch(limit=50)
            
            await validation.close()
            
            if result.get('status') == 'success':
                online = result.get('online', 0)
                offline = result.get('offline', 0)
                logger.info(f"   ✅ Validated {online + offline} streams: {online} online, {offline} offline")
                return {
                    'status': 'success',
                    'online': online,
                    'offline': offline,
                    'total_validated': online + offline
                }
            else:
                logger.error(f"   ❌ Stream validation failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"   Stream validation error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def crawl_radio_browser_info(self) -> Dict[str, Any]:
        """
        Task 13: Radio-Browser.info Integration
        Crawl stations from Radio-Browser.info (free, no API key)
        """
        try:
            from radio_browser_info_crawler import crawl_radio_browser_info
            
            # Crawl top 100 stations from Radio-Browser.info
            result = await crawl_radio_browser_info(limit=100)
            
            logger.info(f"   Radio-Browser.info: {result.get('new_stations', 0)} new stations")
            
            return {
                'status': 'success',
                'new_stations': result.get('new_stations', 0),
                'updated_stations': result.get('updated_stations', 0),
                'total_found': result.get('total_found', 0)
            }
        except Exception as e:
            logger.error(f"   Radio-Browser.info crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_capa_actions(self) -> Dict[str, Any]:
        """
        Task 14: CAPA (Corrective & Preventive Actions)
        Automated system health maintenance and optimization
        """
        try:
            from capa_comprehensive_fix import get_capa_manager
            
            capa = get_capa_manager()
            results = await capa.run_comprehensive_capa()
            
            success_rate = results.get('success_rate', 0)
            logger.info(f"   CAPA execution: {success_rate:.1f}% success rate")
            
            return {
                'status': 'success',
                'success_rate': success_rate,
                'actions_executed': results.get('actions_executed', 0),
                'successful_actions': results.get('successful_actions', 0)
            }
        except Exception as e:
            logger.error(f"   CAPA execution error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    
    async def run_ui_testing(self) -> Dict[str, Any]:
        """
        Task 15: UI Feature Testing
        Automated testing of all UI features and components
        """
        try:
            from dragon_karau_ui_automator import DragonKarauUIAutomator
            
            ui_automator = DragonKarauUIAutomator()
            results = await ui_automator.run_full_ui_test_suite()
            
            success_rate = results.get('success_rate', 0)
            passed = results.get('passed_tests', 0)
            total = results.get('total_tests', 0)
            
            logger.info(f"   UI Tests: {passed}/{total} passed ({success_rate:.1f}%)")
            
            return {
                'status': 'success',
                'success_rate': success_rate,
                'tests_passed': passed,
                'tests_total': total,
                'warnings': results.get('warnings', 0)
            }
        except Exception as e:
            logger.error(f"   UI testing error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_content_compliance(self) -> Dict[str, Any]:
        """
        Task 16: Content Compliance Automation
        Automated content rating and compliance checking
        """
        try:
            from content_compliance_manager import get_compliance_manager
            
            compliance_mgr = get_compliance_manager()
            
            # Check stations without compliance rating
            unrated_count = await self.db.radio_stations.count_documents({
                'compliance_rating': {'$exists': False}
            })
            
            if unrated_count > 0:
                # Rate up to 200 stations per cycle
                stations = await self.db.radio_stations.find({
                    'compliance_rating': {'$exists': False}
                }).limit(200).to_list(length=200)
                
                rated_count = 0
                flagged_count = 0
                
                for station in stations:
                    result = await compliance_mgr.rate_station(station)
                    if result.get('status') == 'rated':
                        rated_count += 1
                        if result.get('flagged', False):
                            flagged_count += 1
                
                logger.info(f"   Content Compliance: {rated_count} rated, {flagged_count} flagged")
                
                return {
                    'status': 'success',
                    'stations_rated': rated_count,
                    'stations_flagged': flagged_count,
                    'unrated_remaining': unrated_count - rated_count
                }
            else:
                logger.info("   Content Compliance: All stations rated")
                return {
                    'status': 'success',
                    'message': 'all_stations_rated'
                }
                
        except Exception as e:
            logger.error(f"   Content compliance error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_duplicate_detection(self) -> Dict[str, Any]:
        """
        Task 17: Duplicate Detection & Removal
        Identifies and removes duplicate station entries
        """
        try:
            logger.info("   Detecting duplicate stations...")
            
            # Find duplicates by stream URL
            pipeline = [
                {
                    '$group': {
                        '_id': '$stream_url',
                        'count': {'$sum': 1},
                        'ids': {'$push': '$_id'},
                        'names': {'$push': '$name'}
                    }
                },
                {
                    '$match': {
                        'count': {'$gt': 1}
                    }
                }
            ]
            
            duplicates = await self.db.radio_stations.aggregate(pipeline).to_list(length=1000)
            
            removed_count = 0
            
            for dup in duplicates:
                # Keep the first one, remove the rest
                ids_to_remove = dup['ids'][1:]
                
                result = await self.db.radio_stations.delete_many({
                    '_id': {'$in': ids_to_remove}
                })
                
                removed_count += result.deleted_count
            
            logger.info(f"   Duplicates: {removed_count} removed from {len(duplicates)} groups")
            
            return {
                'status': 'success',
                'duplicate_groups': len(duplicates),
                'stations_removed': removed_count
            }
            
        except Exception as e:
            logger.error(f"   Duplicate detection error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def enhance_station_standards(self) -> Dict[str, Any]:
        """
        Task 18: Enhanced Standards Implementation
        Bitrate classification, reliability scoring, broadcasting standards
        """
        try:
            logger.info("   Enhancing station standards...")
            
            updated_count = 0
            
            # Get stations without enhanced standards
            stations = await self.db.radio_stations.find({
                '$or': [
                    {'bitrate_tier': {'$exists': False}},
                    {'reliability_score': {'$exists': False}}
                ]
            }).limit(500).to_list(length=500)
            
            for station in stations:
                updates = {}
                
                # Bitrate Classification
                bitrate = station.get('bitrate', 0)
                if bitrate > 0:
                    if bitrate < 64:
                        updates['bitrate_tier'] = 'low'
                    elif bitrate < 128:
                        updates['bitrate_tier'] = 'medium'
                    elif bitrate < 320:
                        updates['bitrate_tier'] = 'high'
                    else:
                        updates['bitrate_tier'] = 'lossless'
                
                # Reliability Score (based on validation history)
                validation_history = station.get('stream_validation_history', [])
                if len(validation_history) > 0:
                    online_count = sum(1 for v in validation_history if v.get('status') == 'online')
                    reliability_score = (online_count / len(validation_history)) * 100
                    updates['reliability_score'] = round(reliability_score, 2)
                else:
                    # Default to stream_status if available
                    if station.get('stream_status') == 'online':
                        updates['reliability_score'] = 90.0
                    else:
                        updates['reliability_score'] = 0.0
                
                # Broadcasting Standard (if we have frequency info)
                if 'frequency' in station:
                    freq = station['frequency']
                    if freq < 30:
                        updates['broadcast_standard'] = 'AM'
                    elif freq < 108:
                        updates['broadcast_standard'] = 'FM'
                    else:
                        updates['broadcast_standard'] = 'DAB'
                
                if updates:
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': updates}
                    )
                    updated_count += 1
            
            logger.info(f"   Standards: {updated_count} stations enhanced")
            
            return {
                'status': 'success',
                'stations_enhanced': updated_count
            }
            
        except Exception as e:
            logger.error(f"   Standards enhancement error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_mobile_platform_testing(self) -> Dict[str, Any]:
        """
        Task 19: Mobile Platform Testing
        Automated iOS and Android testing suite
        """
        try:
            from mobile_platform_tester import get_mobile_tester
            
            mobile_tester = get_mobile_tester()
            results = await mobile_tester.run_full_mobile_test_suite()
            
            success_rate = results.get('success_rate', 0)
            total_tests = results.get('total_tests', 0)
            passed_tests = results.get('passed_tests', 0)
            
            logger.info(f"   Mobile Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
            
            return {
                'status': 'success',
                'success_rate': success_rate,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'ios_tests': results['tests']['ios'].get('tests_passed', 0),
                'android_tests': results['tests']['android'].get('tests_passed', 0),
                'execution_time': results.get('execution_time_seconds', 0)
            }
        except Exception as e:
            logger.error(f"   Mobile platform testing error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_performance_optimization(self) -> Dict[str, Any]:
        """
        Task 20: Performance Optimization
        Automated performance monitoring and optimization
        """
        try:
            from performance_optimizer import get_performance_optimizer
            
            optimizer = get_performance_optimizer()
            results = await optimizer.run_performance_optimization()
            
            score = results.get('overall_performance_score', 0)
            
            logger.info(f"   Performance Score: {score}/100")
            
            # Log individual optimization scores
            optimizations = results.get('optimizations', {})
            for key, opt in optimizations.items():
                if isinstance(opt, dict) and 'score' in opt:
                    logger.info(f"     {key}: {opt['score']}/100")
            
            return {
                'status': 'success',
                'performance_score': score,
                'database_score': optimizations.get('database', {}).get('score', 0),
                'api_response_score': optimizations.get('api_response', {}).get('score', 0),
                'caching_score': optimizations.get('caching', {}).get('score', 0),
                'execution_time': results.get('execution_time_seconds', 0)
            }
        except Exception as e:
            logger.error(f"   Performance optimization error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_analytics_collection(self) -> Dict[str, Any]:
        """Task 21: Analytics Dashboard"""
        try:
            from analytics_dashboard import get_analytics_dashboard
            dashboard = get_analytics_dashboard()
            results = await dashboard.run_analytics_collection()
            logger.info(f"   Analytics: {len(results.get('analytics', {}))} metrics collected")
            return {'status': 'success', 'metrics_collected': len(results.get('analytics', {}))}
        except Exception as e:
            logger.error(f"   Analytics error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_real_time_monitoring(self) -> Dict[str, Any]:
        """Task 22: Real-Time Monitoring"""
        try:
            from real_time_monitor import get_real_time_monitor
            monitor = get_real_time_monitor()
            results = await monitor.run_monitoring_cycle()
            alerts = results.get('alerts_count', 0)
            logger.info(f"   Monitoring: {alerts} alerts generated")
            return {'status': 'success', 'alerts': alerts}
        except Exception as e:
            logger.error(f"   Monitoring error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_ab_testing(self) -> Dict[str, Any]:
        """Task 23: A/B Testing Framework"""
        try:
            from ab_testing_framework import get_ab_testing_framework
            framework = get_ab_testing_framework()
            results = await framework.run_ab_testing_cycle()
            experiments = len(results.get('experiments', {}).get('active', {}).get('active_experiments', 0))
            logger.info(f"   A/B Testing: {experiments} active experiments")
            return {'status': 'success', 'active_experiments': experiments}
        except Exception as e:
            logger.error(f"   A/B testing error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_content_compliance(self) -> Dict[str, Any]:
        """Task 24: Content Compliance Engine"""
        try:
            from content_compliance_engine import get_content_compliance_engine
            engine = get_content_compliance_engine()
            results = await engine.run_compliance_cycle()
            compliance_rate = results.get('report', {}).get('compliance_rate_percent', 0)
            logger.info(f"   Content Compliance: {compliance_rate}% compliant")
            return {'status': 'success', 'compliance_rate': compliance_rate}
        except Exception as e:
            logger.error(f"   Content compliance error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_user_feedback_processing(self) -> Dict[str, Any]:
        """Task 25: User Feedback API"""
        try:
            from user_feedback_api import get_user_feedback_api
            feedback_api = get_user_feedback_api()
            results = await feedback_api.run_feedback_cycle()
            feedback_count = results.get('processing', {}).get('new_feedback', {}).get('new_feedback_count', 0)
            logger.info(f"   User Feedback: {feedback_count} new feedback items")
            return {'status': 'success', 'new_feedback': feedback_count}
        except Exception as e:
            logger.error(f"   User feedback error: {e}")
            return {'status': 'error', 'error': str(e)}


# Global instance
scheduler_instance = None


def get_scheduler() -> AutomatedScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = AutomatedScheduler()
    return scheduler_instance
