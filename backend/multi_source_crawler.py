"""Multi-Source Radio Station Crawler
Crawls radio stations from multiple public sources worldwide
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid
import re

load_dotenv()

logger = logging.getLogger(__name__)

class MultiSourceCrawler:
    """Crawls radio stations from multiple public APIs and sources"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        self.stations_collection = self.db.radio_stations
        self.crawler_history = self.db.crawler_history
        
        # Public radio station sources
        self.sources = {
            'radio_browser': 'https://de1.api.radio-browser.info/json',
            'community_stations': True  # Flag for community-sourced stations
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            'discovered': 0,
            'validated': 0,
            'failed': 0,
            'duplicates': 0
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'KagemaFM/5.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def crawl_radio_browser(self, country: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Crawl stations from Radio Browser API"""
        try:
            url = f"{self.sources['radio_browser']}/stations"
            params = {'limit': limit, 'hidebroken': 'true'}
            
            if country:
                params['countrycode'] = country
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stations = []
                    
                    for item in data:
                        station = self._parse_radio_browser_station(item)
                        if station:
                            stations.append(station)
                    
                    logger.info(f"Crawled {len(stations)} stations from Radio Browser")
                    return stations
                else:
                    logger.error(f"Radio Browser API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error crawling Radio Browser: {e}")
            return []
    
    def _parse_radio_browser_station(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Parse Radio Browser station data into our schema"""
        try:
            # Clean and validate stream URL
            stream_url = item.get('url', '').strip()
            if not stream_url or not stream_url.startswith(('http://', 'https://')):
                return None
            
            # Parse language (can be comma-separated)
            language_str = item.get('language', 'en').lower().strip()
            language = language_str.split(',')[0].strip() if language_str else 'en'
            
            # Parse tags for genre
            tags = item.get('tags', '')
            genre = tags.split(',')[0].strip() if tags else 'General'
            
            station = {
                'id': str(uuid.uuid4()),
                'name': item.get('name', 'Unknown Station').strip(),
                'description': item.get('name', ''),
                'stream_url': stream_url,
                'country': item.get('countrycode', 'UNKNOWN').upper(),
                'language': language[:2],  # ISO 639-1 two-letter code
                'genre': genre[:50],  # Limit genre length
                'quality_score': self._calculate_quality_score(item),
                'validated': False,
                'stream_accessible': False,
                'frequency': None,
                'band_type': 'Internet',
                'homepage': item.get('homepage', ''),
                'favicon': item.get('favicon', ''),
                'bitrate': item.get('bitrate', 0),
                'codec': item.get('codec', 'MP3'),
                'votes': item.get('votes', 0),
                'source': 'radio_browser',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'metadata': {
                    'clickcount': item.get('clickcount', 0),
                    'clicktrend': item.get('clicktrend', 0),
                    'lastcheckok': item.get('lastcheckok', 0)
                }
            }
            
            return station
        except Exception as e:
            logger.error(f"Error parsing station: {e}")
            return None
    
    def _calculate_quality_score(self, item: Dict) -> int:
        """Calculate quality score 0-100 based on station metadata"""
        score = 50  # Base score
        
        # Bitrate bonus (0-20 points)
        bitrate = item.get('bitrate', 0)
        if bitrate >= 320:
            score += 20
        elif bitrate >= 192:
            score += 15
        elif bitrate >= 128:
            score += 10
        elif bitrate >= 64:
            score += 5
        
        # Votes/popularity bonus (0-15 points)
        votes = item.get('votes', 0)
        if votes >= 100:
            score += 15
        elif votes >= 50:
            score += 10
        elif votes >= 10:
            score += 5
        
        # Last checked ok bonus (0-10 points)
        if item.get('lastcheckok', 0) == 1:
            score += 10
        
        # Homepage/favicon bonus (0-5 points)
        if item.get('homepage'):
            score += 3
        if item.get('favicon'):
            score += 2
        
        return min(100, max(0, score))
    
    async def save_stations(self, stations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save stations to database, avoiding duplicates"""
        saved = 0
        duplicates = 0
        failed = 0
        
        for station in stations:
            try:
                # Check for duplicate by stream URL
                existing = await self.stations_collection.find_one(
                    {'stream_url': station['stream_url']}
                )
                
                if existing:
                    duplicates += 1
                    # Update quality score if higher
                    if station['quality_score'] > existing.get('quality_score', 0):
                        await self.stations_collection.update_one(
                            {'_id': existing['_id']},
                            {'$set': {
                                'quality_score': station['quality_score'],
                                'updated_at': datetime.utcnow()
                            }}
                        )
                else:
                    await self.stations_collection.insert_one(station)
                    saved += 1
                    self.stats['discovered'] += 1
            except Exception as e:
                logger.error(f"Error saving station: {e}")
                failed += 1
        
        return {
            'saved': saved,
            'duplicates': duplicates,
            'failed': failed
        }
    
    async def crawl_by_country(self, country_code: str) -> Dict[str, Any]:
        """Crawl stations for a specific country"""
        logger.info(f"Starting crawl for country: {country_code}")
        
        stations = await self.crawl_radio_browser(country=country_code, limit=500)
        results = await self.save_stations(stations)
        
        # Log to crawler history
        await self.crawler_history.insert_one({
            'country': country_code,
            'stations_discovered': len(stations),
            'stations_saved': results['saved'],
            'duplicates': results['duplicates'],
            'timestamp': datetime.utcnow(),
            'source': 'radio_browser'
        })
        
        return {
            'country': country_code,
            'discovered': len(stations),
            **results
        }
    
    async def crawl_global(self, top_n_countries: int = 50) -> Dict[str, Any]:
        """Crawl top N countries globally"""
        # Top 50 countries by internet radio presence
        countries = [
            'US', 'GB', 'DE', 'FR', 'CA', 'AU', 'IT', 'ES', 'NL', 'BR',
            'MX', 'AR', 'JP', 'KR', 'IN', 'CN', 'RU', 'PL', 'SE', 'NO',
            'DK', 'FI', 'AT', 'CH', 'BE', 'IE', 'NZ', 'ZA', 'SG', 'MY',
            'TH', 'ID', 'PH', 'VN', 'CL', 'CO', 'PE', 'VE', 'EC', 'UY',
            'CR', 'PA', 'CU', 'DO', 'PR', 'JM', 'TT', 'KE', 'NG', 'EG'
        ][:top_n_countries]
        
        total_discovered = 0
        total_saved = 0
        total_duplicates = 0
        
        for country in countries:
            try:
                result = await self.crawl_by_country(country)
                total_discovered += result['discovered']
                total_saved += result['saved']
                total_duplicates += result['duplicates']
                
                # Rate limiting
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error crawling {country}: {e}")
        
        return {
            'countries_crawled': len(countries),
            'total_discovered': total_discovered,
            'total_saved': total_saved,
            'total_duplicates': total_duplicates
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        total = await self.stations_collection.count_documents({})
        validated = await self.stations_collection.count_documents({'validated': True})
        by_country = await self.stations_collection.aggregate([
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]).to_list(length=10)
        
        return {
            'total_stations': total,
            'validated_stations': validated,
            'validation_rate': f"{(validated/total*100):.1f}%" if total > 0 else "0%",
            'top_countries': by_country,
            'crawler_stats': self.stats
        }


async def main():
    """Main crawler execution"""
    async with MultiSourceCrawler() as crawler:
        print("🌍 Starting Global Radio Station Crawler...")
        
        # Crawl global stations
        result = await crawler.crawl_global(top_n_countries=50)
        
        print(f"\n✅ Crawl Complete!")
        print(f"  Countries: {result['countries_crawled']}")
        print(f"  Discovered: {result['total_discovered']}")
        print(f"  Saved: {result['total_saved']}")
        print(f"  Duplicates: {result['total_duplicates']}")
        
        # Get final stats
        stats = await crawler.get_stats()
        print(f"\n📊 Database Stats:")
        print(f"  Total Stations: {stats['total_stations']}")
        print(f"  Validated: {stats['validated_stations']}")
        print(f"  Validation Rate: {stats['validation_rate']}")


if __name__ == '__main__':
    asyncio.run(main())
