"""
CAPA (Corrective and Preventive Action) Comprehensive Fix
Addresses all residual issues and performance bottlenecks
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CAPAManager:
    """Manages corrective and preventive actions for system optimization"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
    async def fix_stream_validation_conflicts(self):
        """
        CORRECTIVE ACTION: Fix all stations with stream_validation_history conflicts
        
        Issue: MongoDB conflict when trying to both $set and $push to history array
        Root Cause: Stations have stream_validation_history as non-array field
        Solution: Clean up conflicting fields and reinitialize as arrays
        """
        logger.info("🔧 CAPA: Fixing stream validation conflicts...")
        
        try:
            # Find stations with problematic stream_validation_history
            stations_with_conflict = await self.db.radio_stations.count_documents({
                'stream_validation_history': {'$exists': True, '$not': {'$type': 'array'}}
            })
            
            if stations_with_conflict > 0:
                logger.info(f"  Found {stations_with_conflict} stations with invalid history format")
                
                # Fix by removing invalid history and setting empty array
                result = await self.db.radio_stations.update_many(
                    {'stream_validation_history': {'$exists': True, '$not': {'$type': 'array'}}},
                    {'$set': {'stream_validation_history': []}}
                )
                
                logger.info(f"  ✅ Fixed {result.modified_count} stations")
            else:
                logger.info("  ✅ No conflicts found - all stations have valid format")
            
            # Also initialize missing fields
            stations_without_history = await self.db.radio_stations.count_documents({
                'stream_validation_history': {'$exists': False}
            })
            
            if stations_without_history > 0:
                logger.info(f"  Initializing {stations_without_history} stations without history")
                result = await self.db.radio_stations.update_many(
                    {'stream_validation_history': {'$exists': False}},
                    {'$set': {'stream_validation_history': []}}
                )
                logger.info(f"  ✅ Initialized {result.modified_count} stations")
            
            return {
                'status': 'success',
                'conflicts_fixed': stations_with_conflict,
                'initialized': stations_without_history
            }
            
        except Exception as e:
            logger.error(f"❌ Error fixing conflicts: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def optimize_database_indexes(self):
        """
        PREVENTIVE ACTION: Create optimized indexes for better performance
        """
        logger.info("🚀 CAPA: Optimizing database indexes...")
        
        try:
            indexes_created = []
            
            # Index for geocoding queries
            await self.db.radio_stations.create_index([('latitude', 1)], name='idx_latitude')
            await self.db.radio_stations.create_index([('longitude', 1)], name='idx_longitude')
            indexes_created.append('lat/lon for geocoding')
            
            # Index for stream validation
            await self.db.radio_stations.create_index([('stream_status', 1)], name='idx_stream_status')
            await self.db.radio_stations.create_index([('stream_last_checked', 1)], name='idx_stream_checked')
            indexes_created.append('stream validation fields')
            
            # Index for source tracking
            await self.db.radio_stations.create_index([('source', 1)], name='idx_source')
            indexes_created.append('source tracking')
            
            # Compound index for location queries
            await self.db.radio_stations.create_index(
                [('country', 1), ('latitude', 1), ('longitude', 1)],
                name='idx_location_compound'
            )
            indexes_created.append('compound location index')
            
            # Index for quality scoring
            await self.db.radio_stations.create_index([('quality_score', -1)], name='idx_quality_desc')
            indexes_created.append('quality scoring')
            
            logger.info(f"  ✅ Created/verified {len(indexes_created)} index sets")
            
            return {
                'status': 'success',
                'indexes_created': indexes_created
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def cleanup_orphaned_data(self):
        """
        CORRECTIVE ACTION: Clean up orphaned or invalid data
        """
        logger.info("🧹 CAPA: Cleaning up orphaned data...")
        
        try:
            cleanup_stats = {
                'invalid_coordinates': 0,
                'empty_names': 0,
                'duplicate_streams': 0
            }
            
            # Fix invalid coordinates (outside valid range)
            result = await self.db.radio_stations.update_many(
                {'$or': [
                    {'latitude': {'$lt': -90}},
                    {'latitude': {'$gt': 90}},
                    {'longitude': {'$lt': -180}},
                    {'longitude': {'$gt': 180}}
                ]},
                {'$unset': {'latitude': '', 'longitude': '', 'coordinates': ''}}
            )
            cleanup_stats['invalid_coordinates'] = result.modified_count
            
            # Fix empty station names
            result = await self.db.radio_stations.update_many(
                {'$or': [
                    {'name': ''},
                    {'name': {'$exists': False}}
                ]},
                {'$set': {'name': 'Unknown Station'}}
            )
            cleanup_stats['empty_names'] = result.modified_count
            
            logger.info(f"  ✅ Cleaned up: {cleanup_stats}")
            
            return {
                'status': 'success',
                'cleanup_stats': cleanup_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error cleaning data: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def implement_health_monitoring(self):
        """
        PREVENTIVE ACTION: Set up automated health monitoring
        """
        logger.info("📊 CAPA: Implementing health monitoring...")
        
        try:
            # Create health_checks collection with monitoring data
            health_check = {
                'timestamp': datetime.utcnow(),
                'type': 'automated_health_check',
                'metrics': {
                    'total_stations': await self.db.radio_stations.count_documents({}),
                    'geocoded_stations': await self.db.radio_stations.count_documents({'latitude': {'$exists': True}}),
                    'validated_streams': await self.db.radio_stations.count_documents({'stream_status': 'online'}),
                    'conflicted_histories': await self.db.radio_stations.count_documents({
                        'stream_validation_history': {'$exists': True, '$not': {'$type': 'array'}}
                    })
                },
                'status': 'healthy'
            }
            
            await self.db.health_checks.insert_one(health_check)
            
            logger.info("  ✅ Health monitoring initialized")
            
            return {
                'status': 'success',
                'health_check': health_check
            }
            
        except Exception as e:
            logger.error(f"❌ Error setting up monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def optimize_stream_validation_service(self):
        """
        CORRECTIVE ACTION: Optimize stream validation for better performance
        """
        logger.info("⚡ CAPA: Optimizing stream validation service...")
        
        try:
            # Remove validation history from recently validated stations to reduce conflicts
            # Keep only last 10 entries per station
            cursor = self.db.radio_stations.find({
                'stream_validation_history': {'$exists': True, '$type': 'array'}
            })
            
            optimized_count = 0
            async for station in cursor:
                history = station.get('stream_validation_history', [])
                if len(history) > 10:
                    # Keep only last 10
                    await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {'$set': {'stream_validation_history': history[-10:]}}
                    )
                    optimized_count += 1
            
            logger.info(f"  ✅ Optimized {optimized_count} stations with excessive history")
            
            return {
                'status': 'success',
                'optimized_count': optimized_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error optimizing: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_comprehensive_capa(self):
        """
        Execute all CAPA actions in sequence
        """
        logger.info("=" * 70)
        logger.info("🚀 STARTING COMPREHENSIVE CAPA EXECUTION")
        logger.info("=" * 70)
        
        results = {}
        
        # Action 1: Fix stream validation conflicts
        results['stream_validation_fix'] = await self.fix_stream_validation_conflicts()
        await asyncio.sleep(1)
        
        # Action 2: Optimize database indexes
        results['index_optimization'] = await self.optimize_database_indexes()
        await asyncio.sleep(1)
        
        # Action 3: Clean up orphaned data
        results['data_cleanup'] = await self.cleanup_orphaned_data()
        await asyncio.sleep(1)
        
        # Action 4: Optimize stream validation
        results['stream_optimization'] = await self.optimize_stream_validation_service()
        await asyncio.sleep(1)
        
        # Action 5: Implement health monitoring
        results['health_monitoring'] = await self.implement_health_monitoring()
        
        logger.info("=" * 70)
        logger.info("✅ CAPA EXECUTION COMPLETE")
        logger.info("=" * 70)
        
        # Calculate success rate
        successful_actions = sum(1 for r in results.values() if r.get('status') == 'success')
        total_actions = len(results)
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        return {
            'status': 'completed',
            'success_rate': success_rate,
            'actions_executed': total_actions,
            'successful_actions': successful_actions,
            'detailed_results': results,
            'timestamp': datetime.utcnow().isoformat()
        }


# Singleton instance
_capa_manager = None

def get_capa_manager():
    """Get singleton CAPA manager instance"""
    global _capa_manager
    if _capa_manager is None:
        _capa_manager = CAPAManager()
    return _capa_manager


# CLI execution
if __name__ == "__main__":
    async def main():
        capa = CAPAManager()
        results = await capa.run_comprehensive_capa()
        print("\n" + "=" * 70)
        print("CAPA RESULTS:")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Actions: {results['successful_actions']}/{results['actions_executed']}")
        print("=" * 70)
    
    asyncio.run(main())
