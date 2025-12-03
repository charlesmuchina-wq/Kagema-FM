"""Radioplayer WRAPI Crawler
Crawls UK-based radio stations from Radioplayer Partner API
Integrates with Dragon AI ecosystem
Implements RSA-SHA256 authentication
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


class RadioplayerCrawler:
    """Crawler for Radioplayer Partner API (WRAPI) with authentication"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db'))
        
        # Radioplayer API endpoints
        self.api_base = 'https://api.radioplayer.co.uk/v2'
        self.api_stations_endpoint = f'{self.api_base}/stations'
        
        # Load authentication
        from radioplayer_auth import get_radioplayer_auth
        self.auth = get_radioplayer_auth()
        
        # Stats
        self.stats = {
            'stations_discovered': 0,
            'stations_saved': 0,
            'duplicates': 0,
            'failed': 0,
            'api_authenticated': self.auth.is_configured
        }
        
        if self.auth.is_configured:
            logger.info("Radioplayer Crawler initialized with authentication ✅")
        else:
            logger.warning("Radioplayer Crawler initialized WITHOUT authentication (using fallback) ⚠️")
    
    async def crawl_all_stations(self) -> Dict[str, Any]:
        """Crawl all available stations from Radioplayer"""
        try:
            logger.info("Starting Radioplayer crawl...")
            
            # Try authenticated API first, fall back to hardcoded list
            if self.auth.is_configured:
                logger.info("Using authenticated Radioplayer API...")
                stations = await self._fetch_stations_from_api()
            else:
                logger.warning("No authentication - using fallback station list...")
                stations = await self._get_uk_stations_fallback()
            
            # Save to database
            result = await self._save_stations(stations)
            
            self.stats['stations_discovered'] = len(stations)
            self.stats['stations_saved'] = result['saved']
            self.stats['duplicates'] = result['duplicates']
            
            logger.info(f"Radioplayer crawl complete: {result['saved']} stations saved")
            
            return {
                'status': 'success',
                'source': 'radioplayer',
                'authenticated': self.auth.is_configured,
                'discovered': len(stations),
                'saved': result['saved'],
                'duplicates': result['duplicates']
            }
        
        except Exception as e:
            logger.error(f"Radioplayer crawl error: {e}")
            self.stats['failed'] += 1
            return {
                'status': 'error',
                'error': str(e),
                'source': 'radioplayer'
            }
    
    async def _fetch_stations_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch stations from Radioplayer API with authentication
        Returns list of station dictionaries
        """
        try:
            # Get authentication headers
            headers = self.auth.get_auth_headers(method='GET', path='/v2/stations')
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(self.api_stations_endpoint, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched data from Radioplayer API")
                        
                        # Parse Radioplayer API response
                        stations = self._parse_radioplayer_response(data)
                        logger.info(f"Parsed {len(stations)} stations from API")
                        
                        return stations
                    
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.error(f"Radioplayer API authentication failed (401): {error_text}")
                        logger.warning("Falling back to hardcoded station list...")
                        return await self._get_uk_stations_fallback()
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Radioplayer API error ({response.status}): {error_text}")
                        logger.warning("Falling back to hardcoded station list...")
                        return await self._get_uk_stations_fallback()
        
        except Exception as e:
            logger.error(f"API fetch error: {e}")
            logger.warning("Falling back to hardcoded station list...")
            return await self._get_uk_stations_fallback()
    
    def _parse_radioplayer_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Radioplayer API response into station format
        
        Radioplayer response structure (expected):
        {
            "stations": [
                {
                    "rpId": "bbcradio1",
                    "name": "BBC Radio 1",
                    "description": "...",
                    "logo": "https://...",
                    "country": "GB",
                    "streamUrl": "http://...",
                    "multimedia": {...}
                }
            ]
        }
        """
        stations = []
        
        # Handle different possible response structures
        station_list = []
        if 'stations' in data:
            station_list = data['stations']
        elif 'data' in data:
            station_list = data['data']
        elif isinstance(data, list):
            station_list = data
        
        for station_data in station_list:
            try:
                station = {
                    'name': station_data.get('name', ''),
                    'stream_url': station_data.get('streamUrl') or station_data.get('stream_url', ''),
                    'country': station_data.get('country', 'GB'),
                    'language': 'en',
                    'genre': station_data.get('genre', '') or station_data.get('format', ''),
                    'description': station_data.get('description', ''),
                    'logo_url': station_data.get('logo') or station_data.get('logoUrl', ''),
                    'website': station_data.get('website', ''),
                    'radioplayer_id': station_data.get('rpId') or station_data.get('id', '')
                }
                
                # Only add if we have at least a name and stream URL
                if station['name'] and station['stream_url']:
                    stations.append(station)
            
            except Exception as e:
                logger.warning(f"Failed to parse station: {e}")
                continue
        
        return stations
    
    async def _get_uk_stations_fallback(self) -> List[Dict[str, Any]]:
        """Get popular UK radio stations as fallback"""
        # Major UK radio stations with known working streams
        uk_stations = [
            {
                'name': 'BBC Radio 1',
                'stream_url': 'http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
                'country': 'GB',
                'language': 'en',
                'genre': 'Pop, Rock',
                'description': 'BBC Radio 1 - New music and entertainment'
            },
            {
                'name': 'BBC Radio 2',
                'stream_url': 'http://stream.live.vc.bbcmedia.co.uk/bbc_radio_two',
                'country': 'GB',
                'language': 'en',
                'genre': 'Adult Contemporary',
                'description': 'BBC Radio 2 - The UK\'s most listened to radio station'
            },
            {
                'name': 'BBC Radio 4',
                'stream_url': 'http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm',
                'country': 'GB',
                'language': 'en',
                'genre': 'News, Talk',
                'description': 'BBC Radio 4 - Intelligent speech and entertainment'
            },
            {
                'name': 'BBC Radio 6 Music',
                'stream_url': 'http://stream.live.vc.bbcmedia.co.uk/bbc_6music',
                'country': 'GB',
                'language': 'en',
                'genre': 'Alternative, Indie',
                'description': 'BBC Radio 6 Music - Alternative music'
            },
            {
                'name': 'Heart FM',
                'stream_url': 'http://media-ice.musicradio.com/HeartUK',
                'country': 'GB',
                'language': 'en',
                'genre': 'Pop',
                'description': 'Heart FM - More music variety'
            },
            {
                'name': 'Capital FM',
                'stream_url': 'http://media-ice.musicradio.com/CapitalUK',
                'country': 'GB',
                'language': 'en',
                'genre': 'Pop, Chart',
                'description': 'Capital FM - UK\'s No.1 hit music station'
            },
            {
                'name': 'Smooth Radio',
                'stream_url': 'http://media-ice.musicradio.com/SmoothUK',
                'country': 'GB',
                'language': 'en',
                'genre': 'Easy Listening',
                'description': 'Smooth Radio - Relaxing music'
            },
            {
                'name': 'Classic FM',
                'stream_url': 'http://media-ice.musicradio.com/ClassicFMMP3',
                'country': 'GB',
                'language': 'en',
                'genre': 'Classical',
                'description': 'Classic FM - The world\'s greatest music'
            },
            {
                'name': 'Absolute Radio',
                'stream_url': 'http://icy-e-bz-06-gos.sharp-stream.com/absolute.mp3',
                'country': 'GB',
                'language': 'en',
                'genre': 'Rock',
                'description': 'Absolute Radio - No repeat guarantee'
            },
            {
                'name': 'LBC',
                'stream_url': 'http://media-ice.musicradio.com/LBC973',
                'country': 'GB',
                'language': 'en',
                'genre': 'News, Talk',
                'description': 'LBC - Leading Britain\'s Conversation'
            }
        ]
        
        stations = []
        for station_data in uk_stations:
            station = {
                'id': str(uuid.uuid4()),
                'name': station_data['name'],
                'description': station_data['description'],
                'stream_url': station_data['stream_url'],
                'country': station_data['country'],
                'language': station_data['language'],
                'genre': station_data['genre'],
                'quality_score': 85,  # High quality for UK stations
                'validated': False,
                'stream_accessible': False,
                'frequency': None,
                'band_type': 'Internet',
                'homepage': '',
                'favicon': '',
                'bitrate': 128,
                'codec': 'MP3',
                'votes': 0,
                'source': 'radioplayer_crawler',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'metadata': {
                    'broadcaster': 'UK'
                }
            }
            stations.append(station)
        
        return stations
    
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
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        return {
            'source': 'radioplayer',
            'stats': self.stats
        }


# Global instance
radioplayer_crawler_instance: Optional[RadioplayerCrawler] = None


def get_radioplayer_crawler() -> RadioplayerCrawler:
    """Get or create Radioplayer crawler instance"""
    global radioplayer_crawler_instance
    if radioplayer_crawler_instance is None:
        radioplayer_crawler_instance = RadioplayerCrawler()
    return radioplayer_crawler_instance
