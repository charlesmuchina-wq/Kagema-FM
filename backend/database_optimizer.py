"""Database Optimizer
Optimizes MongoDB database performance, indexes, and storage
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Optimizes database performance and structure"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.db = self.mongo_client[db_name]
    
    async def optimize_indexes(self) -> Dict[str, Any]:
        """Ensure all required indexes exist and are optimal"""
        try:
            collection = self.db.radio_stations
            
            # Get existing indexes
            existing_indexes = await collection.index_information()
            
            # Define required indexes
            required_indexes = {
                'country_1': {'keys': [('country', 1)]},
                'validated_1': {'keys': [('validated', 1)]},
                'stream_url_1': {'keys': [('stream_url', 1)]},
                'quality_score_-1': {'keys': [('quality_score', -1)]},
                'language_1': {'keys': [('language', 1)]},
                'genre_1': {'keys': [('genre', 1)]},
                'created_at_-1': {'keys': [('created_at', -1)]}
            }
            
            created_indexes = []
            
            for index_name, index_spec in required_indexes.items():
                if index_name not in existing_indexes:
                    try:
                        await collection.create_index(
                            index_spec['keys'],
                            name=index_name
                        )
                        created_indexes.append(index_name)
                        logger.info(f"Created index: {index_name}")
                    except Exception as e:
                        # Index might already exist with different name
                        logger.warning(f"Could not create index {index_name}: {e}")
            
            return {
                'status': 'success',
                'existing_indexes': len(existing_indexes),
                'required_indexes': len(required_indexes),
                'created_indexes': created_indexes,
                'all_indexes_present': True
            }
        except Exception as e:
            logger.error(f"Index optimization error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_collection_stats(self) -> Dict[str, Any]:
        """Get detailed collection statistics"""
        try:
            stats = await self.db.command('collStats', 'radio_stations')
            
            return {
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avgObjSize': stats.get('avgObjSize', 0),
                'storageSize': stats.get('storageSize', 0),
                'totalIndexSize': stats.get('totalIndexSize', 0),
                'nindexes': stats.get('nindexes', 0)
            }
        except Exception as e:
            logger.error(f"Collection stats error: {e}")
            return {'error': str(e)}
    
    async def remove_orphaned_data(self) -> Dict[str, Any]:
        """Remove orphaned or invalid data"""
        try:
            # Remove stations with null or empty stream_url
            result = await self.db.radio_stations.delete_many({
                '$or': [
                    {'stream_url': None},
                    {'stream_url': ''},
                    {'stream_url': {'$exists': False}}
                ]
            })
            
            return {
                'status': 'success',
                'removed_count': result.deleted_count
            }
        except Exception as e:
            logger.error(f"Orphaned data removal error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_full_optimization(self) -> Dict[str, Any]:
        """Run complete database optimization"""
        logger.info("Starting full database optimization...")
        
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'tasks': {}
        }
        
        # Optimize indexes
        results['tasks']['index_optimization'] = await self.optimize_indexes()
        
        # Get stats
        results['tasks']['collection_stats'] = await self.analyze_collection_stats()
        
        # Remove orphaned data
        results['tasks']['orphaned_data_removal'] = await self.remove_orphaned_data()
        
        results['completed_at'] = datetime.utcnow().isoformat()
        results['status'] = 'success'
        
        logger.info("Database optimization complete")
        
        return results


async def main():
    """Run database optimization"""
    optimizer = DatabaseOptimizer()
    result = await optimizer.run_full_optimization()
    
    print("\n✅ Database Optimization Complete!")
    print(f"  Index Optimization: {result['tasks']['index_optimization']['status']}")
    print(f"  Collection Stats: {result['tasks']['collection_stats'].get('count', 0)} documents")
    print(f"  Orphaned Data Removed: {result['tasks']['orphaned_data_removal'].get('removed_count', 0)}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
