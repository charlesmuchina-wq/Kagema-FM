"""Multi-Source Crawler Manager
Unified management system for all radio station crawlers
Orchestrates Dragon AI Crawler, Radioplayer, Radio Garden, and future sources
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MultiSourceCrawlerManager:
    """Manages multiple radio station data sources"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Available crawlers
        self.crawlers = {
            'dragon_ai': None,  # Radio Browser API
            'radioplayer': None,  # UK stations
            'radio_garden': None,  # Global stations
            'radio_browser_info': None,  # Radio-Browser.info - Free community directory
        }
        
        # Statistics
        self.global_stats = {
            'total_sources': 0,
            'total_discovered': 0,
            'total_saved': 0,
            'total_duplicates': 0,
            'sources_active': [],
            'last_full_crawl': None
        }
        
        logger.info("Multi-Source Crawler Manager initialized")
    
    async def initialize_crawlers(self):
        """Initialize all available crawlers"""
        try:
            # Import crawlers
            from dragon_ai_crawler_system import get_crawler
            from radioplayer_crawler import get_radioplayer_crawler
            from radio_garden_crawler import get_radio_garden_crawler
            from radio_browser_info_crawler import RadioBrowserInfoCrawler
            
            self.crawlers['dragon_ai'] = get_crawler()
            self.crawlers['radioplayer'] = get_radioplayer_crawler()
            self.crawlers['radio_garden'] = get_radio_garden_crawler()
            self.crawlers['radio_browser_info'] = RadioBrowserInfoCrawler()
            
            self.global_stats['sources_active'] = list(self.crawlers.keys())
            self.global_stats['total_sources'] = len(self.crawlers)
            
            logger.info(f"Initialized {self.global_stats['total_sources']} crawler sources")
            
        except Exception as e:
            logger.error(f"Error initializing crawlers: {e}")
    
    async def crawl_all_sources(self, target_stations: int = 15000) -> Dict[str, Any]:
        """Crawl from all available sources"""
        logger.info(f"🌍 Starting multi-source crawl (target: {target_stations} stations)")
        
        start_time = datetime.utcnow()
        
        # Initialize crawlers if not done
        if not self.crawlers['dragon_ai']:
            await self.initialize_crawlers()
        
        results = {
            'started_at': start_time.isoformat(),
            'sources': {}
        }
        
        try:
            # Check current database count
            current_count = await self.db.radio_stations.count_documents({})
            logger.info(f"Current database: {current_count} stations")
            
            if current_count >= target_stations:
                return {
                    'status': 'target_already_met',
                    'current_count': current_count,
                    'target': target_stations,
                    'message': 'Station target already achieved'
                }
            
            # Source 1: Dragon AI Crawler (Radio Browser) - PRIMARY SOURCE
            logger.info("📡 Crawling Radio Browser API...")
            dragon_result = await self._crawl_dragon_ai(target_stations)
            results['sources']['dragon_ai'] = dragon_result
            
            # Check if target met
            current_count = await self.db.radio_stations.count_documents({})
            if current_count >= target_stations:
                results['status'] = 'target_met'
                results['final_count'] = current_count
                return results
            
            # Source 2: Radioplayer (UK stations)
            logger.info("🇬🇧 Crawling Radioplayer UK stations...")
            radioplayer_result = await self._crawl_radioplayer()
            results['sources']['radioplayer'] = radioplayer_result
            
            # Source 3: Radio Garden (Global discovery)
            logger.info("🌐 Crawling Radio Garden global stations...")
            radio_garden_result = await self._crawl_radio_garden()
            results['sources']['radio_garden'] = radio_garden_result
            
            # Source 4: Radio-Browser.info (Free community directory)
            logger.info("🆓 Crawling Radio-Browser.info stations...")
            radio_browser_info_result = await self._crawl_radio_browser_info(200)
            results['sources']['radio_browser_info'] = radio_browser_info_result
            
            # Final count
            final_count = await self.db.radio_stations.count_documents({})
            
            # Update global stats
            self.global_stats['last_full_crawl'] = datetime.utcnow()
            self.global_stats['total_discovered'] = sum(
                r.get('discovered', 0) for r in results['sources'].values()
            )
            self.global_stats['total_saved'] = sum(
                r.get('saved', 0) for r in results['sources'].values()
            )
            self.global_stats['total_duplicates'] = sum(
                r.get('duplicates', 0) for r in results['sources'].values()
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            results.update({
                'status': 'completed',
                'final_count': final_count,
                'target': target_stations,
                'target_met': final_count >= target_stations,
                'duration_seconds': duration,
                'completed_at': datetime.utcnow().isoformat()
            })
            
            # Save to history
            await self.db.multi_crawler_history.insert_one(results)
            
            logger.info(f"✅ Multi-source crawl complete: {final_count} stations in {duration:.1f}s")
            
            return results
        
        except Exception as e:
            logger.error(f"Multi-source crawl error: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            return results
    
    async def _crawl_dragon_ai(self, target: int) -> Dict[str, Any]:
        """Crawl from Dragon AI Crawler (Radio Browser)"""
        try:
            crawler = self.crawlers['dragon_ai']
            
            # Start global crawl
            result = await crawler.start_global_crawl(target)
            
            # Wait for completion (with timeout)
            max_wait = 300  # 5 minutes max
            elapsed = 0
            
            while elapsed < max_wait:
                status = await crawler.get_status()
                
                if not status['is_running']:
                    break
                
                await asyncio.sleep(10)
                elapsed += 10
            
            # Get final stats
            stats = await crawler.get_statistics()
            
            return {
                'status': 'completed',
                'discovered': stats.get('total_stations', 0),
                'saved': stats.get('total_stations', 0),
                'duplicates': 0,
                'countries': stats.get('unique_countries', 0)
            }
        
        except Exception as e:
            logger.error(f"Dragon AI crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'discovered': 0,
                'saved': 0
            }
    
    async def _crawl_radioplayer(self) -> Dict[str, Any]:
        """Crawl from Radioplayer"""
        try:
            crawler = self.crawlers['radioplayer']
            result = await crawler.crawl_all_stations()
            return result
        except Exception as e:
            logger.error(f"Radioplayer crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'discovered': 0,
                'saved': 0
            }
    
    async def _crawl_radio_garden(self) -> Dict[str, Any]:
        """Crawl from Radio Garden"""
        try:
            crawler = self.crawlers['radio_garden']
            result = await crawler.crawl_popular_locations()
            return result
        except Exception as e:
            logger.error(f"Radio Garden crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'discovered': 0,
                'saved': 0
            }
    
    async def _crawl_radio_browser_info(self, limit: int = 200) -> Dict[str, Any]:
        """Crawl from Radio-Browser.info"""
        try:
            crawler = self.crawlers['radio_browser_info']
            # Get top voted stations globally
            result = await crawler.crawl_and_save(limit_per_search=limit)
            return {
                'status': 'completed',
                'discovered': result.get('total_found', 0),
                'saved': result.get('new_stations', 0) + result.get('updated_stations', 0),
                'duplicates': result.get('updated_stations', 0),
                'errors': result.get('errors', 0)
            }
        except Exception as e:
            logger.error(f"Radio-Browser.info crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'discovered': 0,
                'saved': 0
            }
    
    async def crawl_source(self, source_name: str) -> Dict[str, Any]:
        """Crawl from a specific source"""
        if source_name not in self.crawlers:
            return {
                'status': 'error',
                'error': f'Unknown source: {source_name}',
                'available_sources': list(self.crawlers.keys())
            }
        
        # Initialize if needed
        if not self.crawlers[source_name]:
            await self.initialize_crawlers()
        
        if source_name == 'dragon_ai':
            return await self._crawl_dragon_ai(15000)
        elif source_name == 'radioplayer':
            return await self._crawl_radioplayer()
        elif source_name == 'radio_garden':
            return await self._crawl_radio_garden()
        elif source_name == 'radio_browser_info':
            return await self._crawl_radio_browser_info(200)
    
    async def get_source_stats(self) -> Dict[str, Any]:
        """Get statistics for all sources"""
        try:
            # Get stats by source
            pipeline = [
                {
                    '$group': {
                        '_id': '$source',
                        'count': {'$sum': 1},
                        'validated': {
                            '$sum': {'$cond': [{'$eq': ['$validated', True]}, 1, 0]}
                        }
                    }
                },
                {'$sort': {'count': -1}}
            ]
            
            source_breakdown = await self.db.radio_stations.aggregate(pipeline).to_list(length=100)
            
            total_stations = await self.db.radio_stations.count_documents({})
            
            return {
                'total_stations': total_stations,
                'sources': {
                    item['_id']: {
                        'count': item['count'],
                        'validated': item['validated'],
                        'percentage': f"{(item['count']/total_stations*100):.1f}%" if total_stations > 0 else "0%"
                    }
                    for item in source_breakdown
                },
                'available_crawlers': list(self.crawlers.keys()),
                'active_sources': self.global_stats['sources_active'],
                'last_full_crawl': self.global_stats['last_full_crawl'].isoformat() if self.global_stats['last_full_crawl'] else None
            }
        
        except Exception as e:
            logger.error(f"Error getting source stats: {e}")
            return {'error': str(e)}
    
    async def discover_new_sources(self) -> Dict[str, Any]:
        """Discover and suggest new radio data sources"""
        # List of potential sources to explore
        potential_sources = [
            {
                'name': 'TuneIn API',
                'description': 'Global radio directory with millions of stations',
                'status': 'research_needed',
                'requires_api_key': True
            },
            {
                'name': 'SHOUTcast Directory',
                'description': 'Popular internet radio platform',
                'status': 'research_needed',
                'requires_api_key': False
            },
            {
                'name': 'Icecast Directory',
                'description': 'Open-source streaming directory',
                'status': 'research_needed',
                'requires_api_key': False
            },
            {
                'name': 'Community Radio Browser',
                'description': 'Community-maintained radio database',
                'status': 'research_needed',
                'requires_api_key': False
            }
        ]
        
        return {
            'current_sources': list(self.crawlers.keys()),
            'potential_sources': potential_sources,
            'recommendation': 'Research and implement TuneIn and SHOUTcast for broader coverage'
        }


# Global instance
multi_crawler_instance = None


def get_multi_crawler() -> MultiSourceCrawlerManager:
    """Get or create multi-crawler instance"""
    global multi_crawler_instance
    if multi_crawler_instance is None:
        multi_crawler_instance = MultiSourceCrawlerManager()
    return multi_crawler_instance
