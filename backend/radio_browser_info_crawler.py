"""
Radio-Browser.info Crawler
Free and open-source community-driven internet radio directory
No API key required - https://www.radio-browser.info/
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from radio_browser_client import PRIMARY_BASE_URL, USER_AGENT

logger = logging.getLogger(__name__)


class RadioBrowserInfoCrawler:
    """
    Crawler for Radio-Browser.info API
    Access to 40,000+ internet radio stations worldwide
    Free and open-source, no authentication required
    """
    
    def __init__(self):
        self.base_url = PRIMARY_BASE_URL  # centralized; supports mirror failover
        self.user_agent = USER_AGENT
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.client = None
        self.db = None
        self.source_name = "radio-browser.info"
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info(f"✅ Connected to MongoDB for {self.source_name} crawler")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to Radio-Browser.info"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"❌ Radio-Browser API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Error making request to {endpoint}: {e}")
            return None
            
    def _transform_station(self, raw_station: Dict) -> Dict[str, Any]:
        """Transform Radio-Browser station data to our schema"""
        try:
            # Extract basic info
            station = {
                'name': raw_station.get('name', 'Unknown Station'),
                'country': raw_station.get('countrycode', 'Unknown'),
                'language': raw_station.get('language', 'Unknown'),
                'stream_url': raw_station.get('url_resolved') or raw_station.get('url', ''),
                'homepage': raw_station.get('homepage', ''),
                'favicon': raw_station.get('favicon', ''),
                
                # Tags and metadata
                'tags': [tag.strip() for tag in raw_station.get('tags', '').split(',') if tag.strip()],
                'genre': raw_station.get('tags', ''),  # Tags often contain genres
                
                # Location data
                'state': raw_station.get('state', ''),
                'codec': raw_station.get('codec', ''),
                'bitrate': raw_station.get('bitrate', 0),
                
                # Source tracking
                'source': self.source_name,
                'source_id': raw_station.get('stationuuid', ''),
                'source_url': raw_station.get('url', ''),
                'discovered_at': datetime.utcnow(),
                'last_updated': datetime.utcnow(),
                
                # Radio-Browser specific fields
                'votes': raw_station.get('votes', 0),
                'clickcount': raw_station.get('clickcount', 0),
                'lastcheckok': raw_station.get('lastcheckok', 0),
                'lastchecktime': raw_station.get('lastchecktime', ''),
                
                # Quality indicators
                'quality_score': self._calculate_quality_score(raw_station),
                'is_active': True
            }
            
            # Add coordinates if available
            if raw_station.get('geo_lat') and raw_station.get('geo_long'):
                try:
                    lat = float(raw_station['geo_lat'])
                    lon = float(raw_station['geo_long'])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        station['latitude'] = lat
                        station['longitude'] = lon
                        station['coordinates'] = [lon, lat]  # GeoJSON format
                        station['has_coordinates'] = True
                except (ValueError, TypeError):
                    pass
            
            return station
            
        except Exception as e:
            logger.error(f"❌ Error transforming station: {e}")
            return None
            
    def _calculate_quality_score(self, raw_station: Dict) -> int:
        """Calculate quality score (0-100) based on Radio-Browser metrics"""
        score = 50  # Base score
        
        # Boost for votes (up to +20)
        votes = raw_station.get('votes', 0)
        score += min(votes, 20)
        
        # Boost for clickcount (up to +10)
        clicks = raw_station.get('clickcount', 0)
        if clicks > 1000:
            score += 10
        elif clicks > 500:
            score += 7
        elif clicks > 100:
            score += 5
        elif clicks > 10:
            score += 3
        
        # Boost for working stream (up to +15)
        if raw_station.get('lastcheckok') == 1:
            score += 15
        
        # Boost for recent check (up to +5)
        lastcheck = raw_station.get('lastchecktime', '')
        if lastcheck:
            try:
                # Check if checked within last 7 days
                check_time = datetime.fromisoformat(lastcheck.replace('Z', '+00:00'))
                days_ago = (datetime.utcnow() - check_time.replace(tzinfo=None)).days
                if days_ago <= 7:
                    score += 5
            except:
                pass
        
        # Cap at 100
        return min(score, 100)
        
    async def search_stations(self, 
                             country: Optional[str] = None,
                             language: Optional[str] = None,
                             tag: Optional[str] = None,
                             limit: int = 100,
                             order: str = 'votes') -> List[Dict]:
        """
        Search stations with filters
        
        Args:
            country: Country code (e.g., 'US', 'GB', 'KE')
            language: Language (e.g., 'english', 'spanish')
            tag: Genre/tag (e.g., 'rock', 'news')
            limit: Maximum number of results
            order: Sort order (votes, clickcount, name)
        """
        logger.info(f"🔍 Searching Radio-Browser.info: country={country}, language={language}, tag={tag}")
        
        params = {
            'limit': limit,
            'order': order,
            'reverse': 'true',  # Get highest first
            'hidebroken': 'true'  # Only working streams
        }
        
        # Build search endpoint
        if country:
            endpoint = f"json/stations/bycountrycodeexact/{country.upper()}"
        elif language:
            endpoint = f"json/stations/bylanguageexact/{language.lower()}"
        elif tag:
            endpoint = f"json/stations/bytagexact/{tag.lower()}"
        else:
            endpoint = "json/stations/search"
        
        raw_stations = await self._make_request(endpoint, params)
        
        if not raw_stations:
            return []
        
        # Transform stations
        stations = []
        for raw in raw_stations[:limit]:
            station = self._transform_station(raw)
            if station and station.get('stream_url'):
                stations.append(station)
        
        logger.info(f"✅ Found {len(stations)} stations from Radio-Browser.info")
        return stations
        
    async def get_top_stations(self, limit: int = 100) -> List[Dict]:
        """Get top-voted stations"""
        return await self.search_stations(limit=limit, order='votes')
        
    async def get_popular_stations(self, limit: int = 100) -> List[Dict]:
        """Get most popular (by clicks) stations"""
        params = {
            'limit': limit,
            'order': 'clickcount',
            'reverse': 'true',
            'hidebroken': 'true'
        }
        raw_stations = await self._make_request("json/stations/search", params)
        
        if not raw_stations:
            return []
        
        stations = []
        for raw in raw_stations[:limit]:
            station = self._transform_station(raw)
            if station and station.get('stream_url'):
                stations.append(station)
        
        return stations
        
    async def get_countries(self) -> List[Dict]:
        """Get list of available countries"""
        countries = await self._make_request("json/countries")
        if countries:
            logger.info(f"✅ Retrieved {len(countries)} countries from Radio-Browser.info")
        return countries or []
        
    async def get_languages(self) -> List[Dict]:
        """Get list of available languages"""
        languages = await self._make_request("json/languages")
        if languages:
            logger.info(f"✅ Retrieved {len(languages)} languages from Radio-Browser.info")
        return languages or []
        
    async def get_tags(self) -> List[Dict]:
        """Get list of available tags/genres"""
        tags = await self._make_request("json/tags")
        if tags:
            logger.info(f"✅ Retrieved {len(tags)} tags from Radio-Browser.info")
        return tags or []
        
    async def crawl_and_save(self, 
                            countries: Optional[List[str]] = None,
                            languages: Optional[List[str]] = None,
                            tags: Optional[List[str]] = None,
                            limit_per_search: int = 100) -> Dict[str, Any]:
        """
        Crawl stations and save to database
        
        Args:
            countries: List of country codes to crawl (if None, gets top stations)
            languages: List of languages to crawl
            tags: List of tags/genres to crawl
            limit_per_search: Number of stations per search
        """
        try:
            await self.connect()
            
            stats = {
                'total_found': 0,
                'new_stations': 0,
                'updated_stations': 0,
                'errors': 0,
                'start_time': datetime.utcnow()
            }
            
            all_stations = []
            
            # Crawl by countries
            if countries:
                for country in countries:
                    logger.info(f"🌍 Crawling {country} stations...")
                    stations = await self.search_stations(country=country, limit=limit_per_search)
                    all_stations.extend(stations)
                    await asyncio.sleep(1)  # Be respectful to the API
            
            # Crawl by languages
            elif languages:
                for language in languages:
                    logger.info(f"💬 Crawling {language} stations...")
                    stations = await self.search_stations(language=language, limit=limit_per_search)
                    all_stations.extend(stations)
                    await asyncio.sleep(1)
            
            # Crawl by tags
            elif tags:
                for tag in tags:
                    logger.info(f"🎵 Crawling {tag} stations...")
                    stations = await self.search_stations(tag=tag, limit=limit_per_search)
                    all_stations.extend(stations)
                    await asyncio.sleep(1)
            
            # Default: Get top voted stations
            else:
                logger.info("🏆 Getting top voted stations...")
                all_stations = await self.get_top_stations(limit=limit_per_search)
            
            stats['total_found'] = len(all_stations)
            
            # Save to database
            for station in all_stations:
                try:
                    # Check if station already exists
                    existing = await self.db.radio_stations.find_one({
                        'source': self.source_name,
                        'source_id': station['source_id']
                    })
                    
                    if existing:
                        # Update existing station
                        await self.db.radio_stations.update_one(
                            {'_id': existing['_id']},
                            {'$set': station}
                        )
                        stats['updated_stations'] += 1
                    else:
                        # Insert new station
                        await self.db.radio_stations.insert_one(station)
                        stats['new_stations'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error saving station {station.get('name')}: {e}")
                    stats['errors'] += 1
            
            stats['end_time'] = datetime.utcnow()
            stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
            
            logger.info(f"✅ Radio-Browser.info crawl complete: {stats['new_stations']} new, "
                       f"{stats['updated_stations']} updated, {stats['errors']} errors")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in crawl_and_save: {e}")
            return {'error': str(e)}
        finally:
            await self.close()


# Convenience function
async def crawl_radio_browser_info(countries: Optional[List[str]] = None,
                                   languages: Optional[List[str]] = None,
                                   tags: Optional[List[str]] = None,
                                   limit: int = 100) -> Dict[str, Any]:
    """
    Convenience function to crawl Radio-Browser.info
    
    Examples:
        # Get top 200 stations
        await crawl_radio_browser_info(limit=200)
        
        # Get stations from specific countries
        await crawl_radio_browser_info(countries=['US', 'GB', 'KE'], limit=50)
        
        # Get stations in specific languages
        await crawl_radio_browser_info(languages=['english', 'spanish'], limit=100)
        
        # Get stations by genre
        await crawl_radio_browser_info(tags=['rock', 'jazz', 'news'], limit=50)
    """
    crawler = RadioBrowserInfoCrawler()
    return await crawler.crawl_and_save(countries, languages, tags, limit)
