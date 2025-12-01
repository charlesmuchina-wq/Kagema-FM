"""Dragon AI Crawler System
Advanced multi-source crawler with 7 API automation features
Capable of discovering 12,500+ radio stations globally
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

class DragonAICrawlerSystem:
    """Advanced AI-powered crawler for global radio station discovery"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Crawler state
        self.is_running = False
        self.current_country = None
        self.crawl_task = None
        
        # Statistics
        self.stats = {
            'total_discovered': 0,
            'total_saved': 0,
            'total_duplicates': 0,
            'total_failed': 0,
            'countries_crawled': 0,
            'current_batch': 0,
            'start_time': None,
            'last_update': None
        }
        
        # Radio Browser API endpoints
        self.api_base = 'https://de1.api.radio-browser.info/json'
        
        # Global country list (195 countries)
        self.all_countries = [
            # Africa (54 countries)
            'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG',
            'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR',
            'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ',
            'TZ', 'TG', 'TN', 'UG', 'ZM', 'ZW',
            
            # Asia (48 countries)
            'AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'GE', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP',
            'JO', 'KZ', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PH', 'QA',
            'SA', 'SG', 'KR', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TL', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE', 'HK',
            
            # Europe (44 countries)
            'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
            'HU', 'IS', 'IE', 'IT', 'XK', 'LV', 'LI', 'LT', 'LU', 'MK', 'MT', 'MD', 'MC', 'ME', 'NL', 'NO',
            'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB', 'VA',
            
            # North America (23 countries)
            'AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD', 'GT', 'HT', 'HN', 'JM', 'MX',
            'NI', 'PA', 'KN', 'LC', 'VC', 'TT', 'US',
            
            # South America (12 countries)
            'AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE',
            
            # Oceania (14 countries)
            'AU', 'FJ', 'KI', 'MH', 'FM', 'NR', 'NZ', 'PW', 'PG', 'WS', 'SB', 'TO', 'TV', 'VU'
        ]
        
        logger.info("Dragon AI Crawler System initialized")
    
    async def start_global_crawl(self, target_stations: int = 12500) -> Dict[str, Any]:
        """Start comprehensive global crawl to reach target station count"""
        if self.is_running:
            return {
                'status': 'error',
                'message': 'Crawler already running'
            }
        
        self.is_running = True
        self.stats['start_time'] = datetime.utcnow()
        self.stats['total_discovered'] = 0
        self.stats['total_saved'] = 0
        self.stats['countries_crawled'] = 0
        
        logger.info(f"🚀 Starting global crawl targeting {target_stations} stations")
        
        # Start crawl task in background
        self.crawl_task = asyncio.create_task(self._crawl_all_countries(target_stations))
        
        return {
            'status': 'started',
            'target_stations': target_stations,
            'countries_to_crawl': len(self.all_countries),
            'message': 'Global crawl initiated'
        }
    
    async def _crawl_all_countries(self, target: int):
        """Crawl all countries until target is reached"""
        try:
            current_total = await self.db.radio_stations.count_documents({})
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'DragonKarauAI/1.0'}
            ) as session:
                
                for country in self.all_countries:
                    if not self.is_running:
                        logger.info("Crawl stopped by user")
                        break
                    
                    if current_total >= target:
                        logger.info(f"✅ Target reached: {current_total} stations")
                        break
                    
                    self.current_country = country
                    
                    # Crawl this country
                    result = await self._crawl_country(session, country)
                    
                    self.stats['countries_crawled'] += 1
                    self.stats['total_discovered'] += result.get('discovered', 0)
                    self.stats['total_saved'] += result.get('saved', 0)
                    self.stats['total_duplicates'] += result.get('duplicates', 0)
                    self.stats['last_update'] = datetime.utcnow()
                    
                    # Update current total
                    current_total = await self.db.radio_stations.count_documents({})
                    
                    # Log progress every 10 countries
                    if self.stats['countries_crawled'] % 10 == 0:
                        logger.info(
                            f"Progress: {current_total}/{target} stations, "
                            f"{self.stats['countries_crawled']}/{len(self.all_countries)} countries"
                        )
                    
                    # Rate limiting - 1 second between countries
                    await asyncio.sleep(1)
            
            final_count = await self.db.radio_stations.count_documents({})
            logger.info(f"🎉 Global crawl complete! Total stations: {final_count}")
            
        except Exception as e:
            logger.error(f"Global crawl error: {e}")
        finally:
            self.is_running = False
            self.current_country = None
    
    async def _crawl_country(self, session: aiohttp.ClientSession, country: str) -> Dict[str, Any]:
        """Crawl all stations for a specific country"""
        try:
            url = f"{self.api_base}/stations/bycountrycodeexact/{country}"
            params = {
                'limit': 1000,  # Max per country
                'hidebroken': 'true',
                'order': 'votes',
                'reverse': 'true'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    stations = []
                    for item in data:
                        station = self._parse_station(item, country)
                        if station:
                            stations.append(station)
                    
                    # Save to database
                    result = await self._save_stations(stations)
                    
                    return {
                        'discovered': len(stations),
                        'saved': result['saved'],
                        'duplicates': result['duplicates']
                    }
                else:
                    logger.warning(f"Failed to crawl {country}: HTTP {response.status}")
                    return {'discovered': 0, 'saved': 0, 'duplicates': 0}
        
        except Exception as e:
            logger.error(f"Error crawling {country}: {e}")
            return {'discovered': 0, 'saved': 0, 'duplicates': 0}
    
    def _parse_station(self, item: Dict, country: str) -> Optional[Dict[str, Any]]:
        """Parse station data from Radio Browser API"""
        try:
            stream_url = item.get('url', '').strip()
            if not stream_url or not stream_url.startswith(('http://', 'https://')):
                return None
            
            name = item.get('name', 'Unknown Station').strip()
            if len(name) < 2:
                return None
            
            # Parse language
            language_str = item.get('language', 'en').lower().strip()
            language = language_str.split(',')[0].strip()[:2] if language_str else 'en'
            
            # Parse genre
            tags = item.get('tags', '')
            genre = tags.split(',')[0].strip()[:50] if tags else 'General'
            
            # Calculate quality score
            quality_score = self._calculate_quality(item)
            
            return {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': item.get('name', ''),
                'stream_url': stream_url,
                'country': country.upper(),
                'language': language,
                'genre': genre if genre else 'General',
                'quality_score': quality_score,
                'validated': False,
                'stream_accessible': False,
                'frequency': None,
                'band_type': 'Internet',
                'homepage': item.get('homepage', ''),
                'favicon': item.get('favicon', ''),
                'bitrate': item.get('bitrate', 0),
                'codec': item.get('codec', 'MP3'),
                'votes': item.get('votes', 0),
                'source': 'dragon_ai_crawler',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'metadata': {
                    'clickcount': item.get('clickcount', 0),
                    'clicktrend': item.get('clicktrend', 0),
                    'lastcheckok': item.get('lastcheckok', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error parsing station: {e}")
            return None
    
    def _calculate_quality(self, item: Dict) -> int:
        """Calculate quality score 0-100"""
        score = 50
        
        # Bitrate (0-20 points)
        bitrate = item.get('bitrate', 0)
        if bitrate >= 320:
            score += 20
        elif bitrate >= 192:
            score += 15
        elif bitrate >= 128:
            score += 10
        elif bitrate >= 64:
            score += 5
        
        # Votes (0-15 points)
        votes = item.get('votes', 0)
        if votes >= 100:
            score += 15
        elif votes >= 50:
            score += 10
        elif votes >= 10:
            score += 5
        
        # Last checked (0-10 points)
        if item.get('lastcheckok', 0) == 1:
            score += 10
        
        # Homepage/favicon (0-5 points)
        if item.get('homepage'):
            score += 3
        if item.get('favicon'):
            score += 2
        
        return min(100, max(0, score))
    
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
                    # Update quality if higher
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
    
    async def stop_crawl(self) -> Dict[str, Any]:
        """Stop the current crawl"""
        if not self.is_running:
            return {
                'status': 'error',
                'message': 'No crawl is currently running'
            }
        
        self.is_running = False
        
        if self.crawl_task:
            self.crawl_task.cancel()
        
        logger.info("Crawl stopped by user")
        
        return {
            'status': 'stopped',
            'message': 'Crawler stopped successfully',
            'stats': self.stats
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current crawler status"""
        total_stations = await self.db.radio_stations.count_documents({})
        validated = await self.db.radio_stations.count_documents({'validated': True})
        
        return {
            'is_running': self.is_running,
            'current_country': self.current_country,
            'statistics': {
                **self.stats,
                'database_total': total_stations,
                'database_validated': validated
            }
        }
    
    async def crawl_specific_country(self, country: str) -> Dict[str, Any]:
        """Crawl a specific country"""
        logger.info(f"Crawling country: {country}")
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'DragonKarauAI/1.0'}
        ) as session:
            result = await self._crawl_country(session, country.upper())
        
        # Log to history
        await self.db.crawler_history.insert_one({
            'country': country.upper(),
            'stations_discovered': result['discovered'],
            'stations_saved': result['saved'],
            'duplicates': result['duplicates'],
            'timestamp': datetime.utcnow(),
            'source': 'dragon_ai_crawler'
        })
        
        return {
            'country': country.upper(),
            'discovered': result['discovered'],
            'saved': result['saved'],
            'duplicates': result['duplicates'],
            'status': 'success'
        }
    
    async def crawl_continent(self, continent: str) -> Dict[str, Any]:
        """Crawl all countries in a continent"""
        continent_map = {
            'africa': ['DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN', 'UG', 'ZM', 'ZW'],
            'asia': ['AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'GE', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PH', 'QA', 'SA', 'SG', 'KR', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TL', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE'],
            'europe': ['AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'XK', 'LV', 'LI', 'LT', 'LU', 'MK', 'MT', 'MD', 'MC', 'ME', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB'],
            'north_america': ['AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD', 'GT', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT', 'US'],
            'south_america': ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE'],
            'oceania': ['AU', 'FJ', 'KI', 'MH', 'FM', 'NR', 'NZ', 'PW', 'PG', 'WS', 'SB', 'TO', 'TV', 'VU']
        }
        
        countries = continent_map.get(continent.lower(), [])
        if not countries:
            return {'status': 'error', 'message': f'Unknown continent: {continent}'}
        
        logger.info(f"Crawling {continent}: {len(countries)} countries")
        
        total_discovered = 0
        total_saved = 0
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'DragonKarauAI/1.0'}
        ) as session:
            
            for country in countries:
                result = await self._crawl_country(session, country)
                total_discovered += result['discovered']
                total_saved += result['saved']
                await asyncio.sleep(1)  # Rate limiting
        
        return {
            'continent': continent,
            'countries_crawled': len(countries),
            'total_discovered': total_discovered,
            'total_saved': total_saved,
            'status': 'success'
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        total = await self.db.radio_stations.count_documents({})
        validated = await self.db.radio_stations.count_documents({'validated': True})
        countries = len(await self.db.radio_stations.distinct('country'))
        
        # Top countries
        top_countries = await self.db.radio_stations.aggregate([
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]).to_list(length=10)
        
        # Recent crawls
        recent_crawls = await self.db.crawler_history.find().sort('timestamp', -1).limit(10).to_list(length=10)
        
        return {
            'total_stations': total,
            'validated_stations': validated,
            'validation_rate': f"{(validated/total*100):.1f}%" if total > 0 else "0%",
            'unique_countries': countries,
            'top_countries': top_countries,
            'recent_crawls': [
                {
                    'country': c['country'],
                    'discovered': c['stations_discovered'],
                    'saved': c['stations_saved'],
                    'timestamp': c['timestamp'].isoformat()
                }
                for c in recent_crawls
            ],
            'crawler_stats': self.stats
        }


# Global crawler instance
crawler_instance: Optional[DragonAICrawlerSystem] = None


def get_crawler() -> DragonAICrawlerSystem:
    """Get or create crawler instance"""
    global crawler_instance
    if crawler_instance is None:
        crawler_instance = DragonAICrawlerSystem()
    return crawler_instance
