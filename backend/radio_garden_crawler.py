"""Radio Garden Crawler
Crawls global radio stations from Radio Garden platform
Discovers stations by exploring different countries and cities
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

logger = logging.getLogger(__name__)


class RadioGardenCrawler:
    """Crawler for Radio Garden global station discovery"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Radio Garden API endpoints
        self.api_base = 'https://radio.garden/api'
        
        # Stats
        self.stats = {
            'places_discovered': 0,
            'stations_discovered': 0,
            'stations_saved': 0,
            'duplicates': 0,
            'failed': 0
        }
        
        # Known popular locations
        self.popular_places = [
            {'id': 'london', 'name': 'London', 'country': 'GB'},
            {'id': 'new-york', 'name': 'New York', 'country': 'US'},
            {'id': 'paris', 'name': 'Paris', 'country': 'FR'},
            {'id': 'tokyo', 'name': 'Tokyo', 'country': 'JP'},
            {'id': 'nairobi', 'name': 'Nairobi', 'country': 'KE'},
            {'id': 'sydney', 'name': 'Sydney', 'country': 'AU'},
            {'id': 'mumbai', 'name': 'Mumbai', 'country': 'IN'},
            {'id': 'sao-paulo', 'name': 'São Paulo', 'country': 'BR'},
            {'id': 'lagos', 'name': 'Lagos', 'country': 'NG'},
            {'id': 'berlin', 'name': 'Berlin', 'country': 'DE'}
        ]
        
        logger.info("Radio Garden Crawler initialized")
    
    async def crawl_by_location(self, location_id: str) -> Dict[str, Any]:
        """Crawl stations for a specific location"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'DragonKarauAI/1.0'}
            ) as session:
                
                # Get place details
                url = f"{self.api_base}/ara/content/page/{location_id}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        stations = []
                        
                        # Parse stations from the response
                        content = data.get('data', {}).get('content', [])
                        
                        for item in content:
                            if item.get('type') == 'channel':
                                station = await self._parse_radio_garden_station(item, location_id)
                                if station:
                                    stations.append(station)
                        
                        # Save stations
                        result = await self._save_stations(stations)
                        
                        return {
                            'location': location_id,
                            'discovered': len(stations),
                            'saved': result['saved'],
                            'duplicates': result['duplicates']
                        }
        
        except Exception as e:
            logger.error(f"Error crawling location {location_id}: {e}")
            self.stats['failed'] += 1
        
        return {'location': location_id, 'discovered': 0, 'saved': 0}
    
    async def crawl_popular_locations(self) -> Dict[str, Any]:
        """Crawl stations from popular global locations"""
        try:
            logger.info("Starting Radio Garden popular locations crawl...")
            
            total_discovered = 0
            total_saved = 0
            total_duplicates = 0
            
            for place in self.popular_places:
                result = await self.crawl_by_location(place['id'])
                
                total_discovered += result.get('discovered', 0)
                total_saved += result.get('saved', 0)
                total_duplicates += result.get('duplicates', 0)
                
                self.stats['places_discovered'] += 1
                
                # Rate limiting
                await asyncio.sleep(2)
            
            self.stats['stations_discovered'] = total_discovered
            self.stats['stations_saved'] = total_saved
            self.stats['duplicates'] = total_duplicates
            
            logger.info(f"Radio Garden crawl complete: {total_saved} stations saved from {self.stats['places_discovered']} locations")
            
            return {
                'status': 'success',
                'source': 'radio_garden',
                'places': self.stats['places_discovered'],
                'discovered': total_discovered,
                'saved': total_saved,
                'duplicates': total_duplicates
            }
        
        except Exception as e:
            logger.error(f"Radio Garden crawl error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'source': 'radio_garden'
            }
    
    async def _parse_radio_garden_station(self, item: Dict, location: str) -> Optional[Dict[str, Any]]:
        """Parse station from Radio Garden API response"""
        try:
            channel_id = item.get('id', '')
            if not channel_id:
                return None
            
            # Construct stream URL
            stream_url = f"{self.api_base}/ara/content/listen/{channel_id}/channel.mp3"
            
            title = item.get('title', 'Unknown Station')
            
            return {
                'id': str(uuid.uuid4()),
                'name': title,
                'description': f"{title} from Radio Garden",
                'stream_url': stream_url,
                'country': 'XX',  # Will be updated by geocoding
                'language': 'en',
                'genre': 'General',
                'quality_score': 70,
                'validated': False,
                'stream_accessible': False,
                'frequency': None,
                'band_type': 'Internet',
                'homepage': f"https://radio.garden/listen/{channel_id}",
                'favicon': '',
                'bitrate': 128,
                'codec': 'MP3',
                'votes': 0,
                'source': 'radio_garden_crawler',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'metadata': {
                    'location': location,
                    'channel_id': channel_id
                }
            }
        
        except Exception as e:
            logger.error(f"Error parsing Radio Garden station: {e}")
            return None
    
    async def _save_stations(self, stations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save stations to database"""
        saved = 0
        duplicates = 0
        
        for station in stations:
            try:
                # Check for duplicate by stream URL
                existing = await self.db.radio_stations.find_one(
                    {'stream_url': station['stream_url']}
                )
                
                if existing:
                    duplicates += 1
                    # Update if needed
                    if station['quality_score'] > existing.get('quality_score', 0):
                        await self.db.radio_stations.update_one(
                            {'_id': existing['_id']},
                            {'$set': {
                                'quality_score': station['quality_score'],
                                'updated_at': datetime.utcnow()
                            }}
                        )
                else:
                    await self.db.radio_stations.insert_one(station)
                    saved += 1
            except Exception as e:
                logger.error(f"Error saving station: {e}")
        
        return {'saved': saved, 'duplicates': duplicates}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        return {
            'source': 'radio_garden',
            'stats': self.stats
        }


# Global instance
radio_garden_crawler_instance: Optional[RadioGardenCrawler] = None


def get_radio_garden_crawler() -> RadioGardenCrawler:
    """Get or create Radio Garden crawler instance"""
    global radio_garden_crawler_instance
    if radio_garden_crawler_instance is None:
        radio_garden_crawler_instance = RadioGardenCrawler()
    return radio_garden_crawler_instance
