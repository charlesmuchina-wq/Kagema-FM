"""
Automated Monitoring & Validation Service
Runs continuously to monitor, validate, and report on all system components
"""
import asyncio
import os
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List
import aiohttp
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedMonitoringService:
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.client = None
        self.db = None
        
        # Monitoring intervals (in seconds)
        self.station_monitor_interval = 3600  # 1 hour
        self.geocoding_monitor_interval = 1800  # 30 minutes
        self.performance_monitor_interval = 600  # 10 minutes
        self.web_validation_interval = 3600  # 1 hour
        
        # Thresholds and alerts
        self.alert_thresholds = {
            'low_geocoding_rate': 50,  # stations/day
            'high_response_time': 1000,  # ms
            'low_station_growth': 50,  # stations/day
            'high_error_rate': 0.05  # 5%
        }
        
        # Historical data
        self.history = {
            'station_counts': [],
            'geocoding_progress': [],
            'performance_metrics': [],
            'validation_results': []
        }
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info("✅ Connected to MongoDB")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Closed MongoDB connection")
    
    # ===== STATION GROWTH MONITORING =====
    
    async def monitor_station_growth(self) -> Dict[str, Any]:
        """Monitor and report station database growth"""
        try:
            total = await self.db.radio_stations.count_documents({})
            
            # Get source breakdown
            sources = await self.db.radio_stations.aggregate([
                {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]).to_list(length=None)
            
            # Get country distribution
            countries = await self.db.radio_stations.aggregate([
                {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]).to_list(length=None)
            
            # Calculate growth rate
            if len(self.history['station_counts']) > 0:
                last_count = self.history['station_counts'][-1]['count']
                last_time = self.history['station_counts'][-1]['timestamp']
                time_diff = (datetime.now() - last_time).total_seconds() / 3600  # hours
                growth_rate = (total - last_count) / time_diff if time_diff > 0 else 0
            else:
                growth_rate = 0
            
            result = {
                'timestamp': datetime.now(),
                'count': total,
                'growth_rate_per_hour': round(growth_rate, 2),
                'sources': sources,
                'top_countries': countries[:5],
                'status': 'healthy' if growth_rate >= 8.3 else 'warning'  # 200/day = 8.3/hour
            }
            
            # Store in history
            self.history['station_counts'].append(result)
            if len(self.history['station_counts']) > 168:  # Keep 7 days (hourly)
                self.history['station_counts'].pop(0)
            
            logger.info(f"📻 Station Growth: {total:,} stations (+ {growth_rate:.1f}/hour)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error monitoring station growth: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ===== GEOCODING MONITORING =====
    
    async def monitor_geocoding_progress(self) -> Dict[str, Any]:
        """Monitor geocoding progress and performance"""
        try:
            total = await self.db.radio_stations.count_documents({})
            geocoded = await self.db.radio_stations.count_documents({
                'latitude': {'$ne': None, '$exists': True},
                'longitude': {'$ne': None, '$exists': True}
            })
            
            remaining = total - geocoded
            percentage = (geocoded / total * 100) if total > 0 else 0
            
            # Calculate geocoding rate
            if len(self.history['geocoding_progress']) > 0:
                last_geocoded = self.history['geocoding_progress'][-1]['geocoded']
                last_time = self.history['geocoding_progress'][-1]['timestamp']
                time_diff = (datetime.now() - last_time).total_seconds() / 3600  # hours
                geocoding_rate = (geocoded - last_geocoded) / time_diff if time_diff > 0 else 0
            else:
                geocoding_rate = 0
            
            # Estimate completion
            daily_rate = geocoding_rate * 24
            days_to_completion = remaining / daily_rate if daily_rate > 0 else 0
            
            result = {
                'timestamp': datetime.now(),
                'total': total,
                'geocoded': geocoded,
                'remaining': remaining,
                'percentage': round(percentage, 2),
                'rate_per_hour': round(geocoding_rate, 2),
                'daily_rate': round(daily_rate, 0),
                'estimated_days': round(days_to_completion, 1),
                'status': 'healthy' if daily_rate >= 50 else 'warning'
            }
            
            # Store in history
            self.history['geocoding_progress'].append(result)
            if len(self.history['geocoding_progress']) > 336:  # Keep 7 days (30min intervals)
                self.history['geocoding_progress'].pop(0)
            
            logger.info(f"📍 Geocoding: {geocoded:,}/{total:,} ({percentage:.2f}%) at {daily_rate:.0f}/day")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error monitoring geocoding: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ===== PERFORMANCE MONITORING =====
    
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor system performance metrics"""
        try:
            # Test API response times
            start_time = datetime.now()
            
            async with aiohttp.ClientSession() as session:
                # Test root endpoint
                async with session.get('http://localhost:8001/api/') as response:
                    root_time = (datetime.now() - start_time).total_seconds() * 1000
                    root_status = response.status
                
                # Test stations endpoint
                start_time = datetime.now()
                async with session.get('http://localhost:8001/api/stations?limit=10') as response:
                    stations_time = (datetime.now() - start_time).total_seconds() * 1000
                    stations_status = response.status
                
                # Test geocoding stats
                start_time = datetime.now()
                async with session.get('http://localhost:8001/api/geocoding/stats') as response:
                    geo_time = (datetime.now() - start_time).total_seconds() * 1000
                    geo_status = response.status
            
            # Database performance
            db_stats = await self.db.command('dbStats')
            
            result = {
                'timestamp': datetime.now(),
                'api_responses': {
                    'root': {'time_ms': round(root_time, 2), 'status': root_status},
                    'stations': {'time_ms': round(stations_time, 2), 'status': stations_status},
                    'geocoding': {'time_ms': round(geo_time, 2), 'status': geo_status}
                },
                'database': {
                    'size_mb': round(db_stats['dataSize'] / (1024 * 1024), 2),
                    'storage_mb': round(db_stats['storageSize'] / (1024 * 1024), 2),
                    'collections': db_stats['collections'],
                    'indexes': db_stats['indexes']
                },
                'avg_response_time': round((root_time + stations_time + geo_time) / 3, 2),
                'status': 'healthy' if root_time < 500 else 'warning'
            }
            
            # Store in history
            self.history['performance_metrics'].append(result)
            if len(self.history['performance_metrics']) > 1008:  # Keep 7 days (10min intervals)
                self.history['performance_metrics'].pop(0)
            
            logger.info(f"⚡ Performance: Avg response {result['avg_response_time']:.0f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error monitoring performance: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ===== WEB ENHANCEMENT VALIDATION =====
    
    async def validate_web_enhancements(self) -> Dict[str, Any]:
        """Validate web map and globe functionality"""
        try:
            results = {
                'timestamp': datetime.now(),
                'homepage': {'status': 'unknown'},
                'map': {'status': 'unknown'},
                'globe': {'status': 'unknown'}
            }
            
            async with aiohttp.ClientSession() as session:
                # Test homepage
                try:
                    async with session.get('http://localhost:3000', timeout=aiohttp.ClientTimeout(total=10)) as response:
                        results['homepage'] = {
                            'status': 'healthy' if response.status == 200 else 'error',
                            'status_code': response.status,
                            'load_time_ms': 0  # Would need browser automation for accurate timing
                        }
                except Exception as e:
                    results['homepage'] = {'status': 'error', 'error': str(e)}
                
                # Test map HTML
                try:
                    async with session.get('http://localhost:3000/map.html', timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        has_leaflet = 'leaflet' in content.lower()
                        has_clustering = 'markercluster' in content.lower()
                        
                        results['map'] = {
                            'status': 'healthy' if (response.status == 200 and has_leaflet) else 'warning',
                            'status_code': response.status,
                            'leaflet_present': has_leaflet,
                            'clustering_present': has_clustering
                        }
                except Exception as e:
                    results['map'] = {'status': 'error', 'error': str(e)}
                
                # Test globe HTML
                try:
                    async with session.get('http://localhost:3000/globe.html', timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        has_globe_gl = 'globe.gl' in content.lower()
                        has_three = 'three' in content.lower()
                        
                        results['globe'] = {
                            'status': 'healthy' if (response.status == 200 and has_globe_gl) else 'warning',
                            'status_code': response.status,
                            'globe_gl_present': has_globe_gl,
                            'three_js_present': has_three
                        }
                except Exception as e:
                    results['globe'] = {'status': 'error', 'error': str(e)}
            
            # Overall status
            all_healthy = all(
                results[key]['status'] == 'healthy' 
                for key in ['homepage', 'map', 'globe']
            )
            results['overall_status'] = 'healthy' if all_healthy else 'warning'
            
            # Store in history
            self.history['validation_results'].append(results)
            if len(self.history['validation_results']) > 168:  # Keep 7 days (hourly)
                self.history['validation_results'].pop(0)
            
            logger.info(f"🌐 Web Validation: {results['overall_status'].upper()}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error validating web enhancements: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ===== COMPREHENSIVE REPORT =====
    
    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        station_data = await self.monitor_station_growth()
        geocoding_data = await self.monitor_geocoding_progress()
        performance_data = await self.monitor_performance()
        web_data = await self.validate_web_enhancements()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'station_growth': station_data,
            'geocoding_progress': geocoding_data,
            'performance': performance_data,
            'web_enhancements': web_data,
            'overall_health': self._calculate_overall_health(
                station_data, geocoding_data, performance_data, web_data
            )
        }
        
        return report
    
    def _calculate_overall_health(self, *components) -> str:
        """Calculate overall system health from component statuses"""
        statuses = [comp.get('status', 'unknown') for comp in components]
        
        if all(s == 'healthy' for s in statuses):
            return 'healthy'
        elif any(s == 'error' for s in statuses):
            return 'error'
        else:
            return 'warning'
    
    async def print_report(self):
        """Print formatted monitoring report"""
        report = await self.generate_report()
        
        print("\n" + "="*80)
        print(" "*15 + "🎯 AUTOMATED MONITORING REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Health: {report['overall_health'].upper()}")
        print("="*80)
        
        # Station Growth
        sg = report['station_growth']
        print(f"\n📻 STATION DATABASE")
        print(f"Total Stations: {sg.get('count', 0):,}")
        print(f"Growth Rate: {sg.get('growth_rate_per_hour', 0):.2f} stations/hour")
        print(f"Status: {sg.get('status', 'unknown').upper()}")
        
        # Geocoding
        gp = report['geocoding_progress']
        print(f"\n📍 GEOCODING PROGRESS")
        print(f"Geocoded: {gp.get('geocoded', 0):,} / {gp.get('total', 0):,}")
        print(f"Percentage: {gp.get('percentage', 0):.2f}%")
        print(f"Daily Rate: {gp.get('daily_rate', 0):.0f} stations/day")
        print(f"Estimated Completion: {gp.get('estimated_days', 0):.1f} days")
        print(f"Status: {gp.get('status', 'unknown').upper()}")
        
        # Performance
        perf = report['performance']
        print(f"\n⚡ PERFORMANCE")
        print(f"Avg Response Time: {perf.get('avg_response_time', 0):.0f}ms")
        print(f"Database Size: {perf.get('database', {}).get('size_mb', 0):.2f} MB")
        print(f"Status: {perf.get('status', 'unknown').upper()}")
        
        # Web Enhancements
        web = report['web_enhancements']
        print(f"\n🌐 WEB ENHANCEMENTS")
        print(f"Homepage: {web.get('homepage', {}).get('status', 'unknown').upper()}")
        print(f"Map (Leaflet): {web.get('map', {}).get('status', 'unknown').upper()}")
        print(f"Globe (Globe.GL): {web.get('globe', {}).get('status', 'unknown').upper()}")
        print(f"Overall: {web.get('overall_status', 'unknown').upper()}")
        
        print("\n" + "="*80)
        print("✅ Report complete")
        print("="*80 + "\n")
    
    # ===== AUTOMATION LOOP =====
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        logger.info("🚀 Starting automated monitoring service...")
        
        await self.connect()
        
        try:
            # Initial report
            await self.print_report()
            
            # Track last execution times
            last_station_check = datetime.now() - timedelta(hours=1)
            last_geocoding_check = datetime.now() - timedelta(minutes=30)
            last_performance_check = datetime.now() - timedelta(minutes=10)
            last_web_check = datetime.now() - timedelta(hours=1)
            
            while True:
                now = datetime.now()
                
                # Station growth monitoring
                if (now - last_station_check).total_seconds() >= self.station_monitor_interval:
                    await self.monitor_station_growth()
                    last_station_check = now
                
                # Geocoding monitoring
                if (now - last_geocoding_check).total_seconds() >= self.geocoding_monitor_interval:
                    await self.monitor_geocoding_progress()
                    last_geocoding_check = now
                
                # Performance monitoring
                if (now - last_performance_check).total_seconds() >= self.performance_monitor_interval:
                    await self.monitor_performance()
                    last_performance_check = now
                
                # Web validation
                if (now - last_web_check).total_seconds() >= self.web_validation_interval:
                    await self.validate_web_enhancements()
                    last_web_check = now
                
                # Print comprehensive report every hour
                if now.minute == 0 and now.second < 60:
                    await self.print_report()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️  Monitoring service stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in monitoring loop: {e}")
        finally:
            await self.close()

# Main execution
async def main():
    service = AutomatedMonitoringService()
    await service.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
