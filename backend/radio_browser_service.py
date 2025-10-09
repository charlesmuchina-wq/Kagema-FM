"""
Radio Browser Service
Integrates with Radio Browser API (radio-browser.info) - a community-driven 
database of radio stations worldwide with 70,000+ stations
"""

import aiohttp
import logging
from typing import List, Dict, Any, Optional
import asyncio
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RadioBrowserService:
    """
    Radio Browser API Service
    
    Provides access to thousands of radio stations worldwide through
    the community-driven Radio Browser database
    """
    
    def __init__(self):
        self.base_url = "https://de1.api.radio-browser.info"  # Primary server
        self.backup_servers = [
            "https://fr1.api.radio-browser.info",
            "https://nl1.api.radio-browser.info",
            "https://at1.api.radio-browser.info"
        ]
        self.timeout = aiohttp.ClientTimeout(total=10)
        logger.info("✅ Radio Browser Service initialized")
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Make API request with fallback to backup servers"""
        urls = [self.base_url] + self.backup_servers
        
        for url in urls:
            try:
                full_url = f"{url}{endpoint}"
                
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(full_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list):
                                return data
                            return []
                        else:
                            logger.warning(f"Radio Browser API returned status {response.status} for {full_url}")
                            
            except Exception as e:
                logger.warning(f"Radio Browser API request failed for {url}: {e}")
                continue
        
        logger.error(f"All Radio Browser API servers failed for endpoint: {endpoint}")
        return []
    
    async def search_stations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search radio stations by name"""
        try:
            endpoint = "/json/stations/search"
            params = {
                "name": query,
                "limit": limit,
                "hidebroken": "true",  # Hide broken stations
                "order": "votes",      # Order by votes (popularity)
                "reverse": "true"      # Highest votes first
            }
            
            stations = await self._make_request(endpoint, params)
            
            # Filter and format stations
            formatted_stations = []
            for station in stations:
                if station.get('url_resolved') and station.get('name'):
                    formatted_station = {
                        "id": f"rb-{station.get('stationuuid', '')}",
                        "name": station.get('name', ''),
                        "country": station.get('country', ''),
                        "language": station.get('language', ''),
                        "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                        "genre": self._extract_primary_genre(station.get('tags', '')),
                        "stream_url": station.get('url_resolved', ''),
                        "homepage": station.get('homepage', ''),
                        "favicon": station.get('favicon', ''),
                        "bitrate": station.get('bitrate', 0),
                        "votes": station.get('votes', 0),
                        "clickcount": station.get('clickcount', 0),
                        "source": "Radio Browser",
                        "description": f"{station.get('country', '')} - {self._extract_primary_genre(station.get('tags', ''))}"
                    }
                    formatted_stations.append(formatted_station)
            
            logger.info(f"🔍 Found {len(formatted_stations)} Radio Browser stations for: {query}")
            return formatted_stations
            
        except Exception as e:
            logger.error(f"❌ Error searching Radio Browser stations: {e}")
            return []
    
    async def get_stations_by_country(self, country: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get stations by country"""
        try:
            endpoint = f"/json/stations/bycountryexact/{quote(country)}"
            params = {
                "limit": limit,
                "hidebroken": "true",
                "order": "votes",
                "reverse": "true"
            }
            
            stations = await self._make_request(endpoint, params)
            
            # Format stations
            formatted_stations = []
            for station in stations[:limit]:
                if station.get('url_resolved') and station.get('name'):
                    formatted_station = {
                        "id": f"rb-{station.get('stationuuid', '')}",
                        "name": station.get('name', ''),
                        "country": station.get('country', ''),
                        "language": station.get('language', ''),
                        "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                        "genre": self._extract_primary_genre(station.get('tags', '')),
                        "stream_url": station.get('url_resolved', ''),
                        "bitrate": station.get('bitrate', 0),
                        "votes": station.get('votes', 0),
                        "source": "Radio Browser",
                        "description": f"{country} - {self._extract_primary_genre(station.get('tags', ''))}"
                    }
                    formatted_stations.append(formatted_station)
            
            logger.info(f"🌍 Found {len(formatted_stations)} Radio Browser stations for country: {country}")
            return formatted_stations
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser stations by country: {e}")
            return []
    
    async def get_stations_by_language(self, language: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get stations by language"""
        try:
            endpoint = f"/json/stations/bylanguage/{quote(language)}"
            params = {
                "limit": limit,
                "hidebroken": "true",
                "order": "votes",
                "reverse": "true"
            }
            
            stations = await self._make_request(endpoint, params)
            
            # Format stations
            formatted_stations = []
            for station in stations[:limit]:
                if station.get('url_resolved') and station.get('name'):
                    formatted_station = {
                        "id": f"rb-{station.get('stationuuid', '')}",
                        "name": station.get('name', ''),
                        "country": station.get('country', ''),
                        "language": station.get('language', ''),
                        "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                        "genre": self._extract_primary_genre(station.get('tags', '')),
                        "stream_url": station.get('url_resolved', ''),
                        "bitrate": station.get('bitrate', 0),
                        "votes": station.get('votes', 0),
                        "source": "Radio Browser",
                        "description": f"{station.get('country', '')} - {language}"
                    }
                    formatted_stations.append(formatted_station)
            
            logger.info(f"🗣️ Found {len(formatted_stations)} Radio Browser stations for language: {language}")
            return formatted_stations
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser stations by language: {e}")
            return []
    
    async def get_stations_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get stations by tag/genre"""
        try:
            endpoint = f"/json/stations/bytag/{quote(tag)}"
            params = {
                "limit": limit,
                "hidebroken": "true",
                "order": "votes",
                "reverse": "true"
            }
            
            stations = await self._make_request(endpoint, params)
            
            # Format stations
            formatted_stations = []
            for station in stations[:limit]:
                if station.get('url_resolved') and station.get('name'):
                    formatted_station = {
                        "id": f"rb-{station.get('stationuuid', '')}",
                        "name": station.get('name', ''),
                        "country": station.get('country', ''),
                        "language": station.get('language', ''),
                        "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                        "genre": self._extract_primary_genre(station.get('tags', '')),
                        "stream_url": station.get('url_resolved', ''),
                        "bitrate": station.get('bitrate', 0),
                        "votes": station.get('votes', 0),
                        "source": "Radio Browser",
                        "description": f"{station.get('country', '')} - {tag}"
                    }
                    formatted_stations.append(formatted_station)
            
            logger.info(f"🏷️ Found {len(formatted_stations)} Radio Browser stations for tag: {tag}")
            return formatted_stations
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser stations by tag: {e}")
            return []
    
    async def get_popular_stations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get most popular stations worldwide"""
        try:
            endpoint = "/json/stations"
            params = {
                "limit": limit,
                "hidebroken": "true",
                "order": "votes",
                "reverse": "true"
            }
            
            stations = await self._make_request(endpoint, params)
            
            # Format stations
            formatted_stations = []
            for station in stations[:limit]:
                if station.get('url_resolved') and station.get('name'):
                    formatted_station = {
                        "id": f"rb-{station.get('stationuuid', '')}",
                        "name": station.get('name', ''),
                        "country": station.get('country', ''),
                        "language": station.get('language', ''),
                        "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                        "genre": self._extract_primary_genre(station.get('tags', '')),
                        "stream_url": station.get('url_resolved', ''),
                        "bitrate": station.get('bitrate', 0),
                        "votes": station.get('votes', 0),
                        "clickcount": station.get('clickcount', 0),
                        "source": "Radio Browser",
                        "description": f"{station.get('country', '')} - Popular station"
                    }
                    formatted_stations.append(formatted_station)
            
            logger.info(f"⭐ Found {len(formatted_stations)} popular Radio Browser stations")
            return formatted_stations
            
        except Exception as e:
            logger.error(f"❌ Error getting popular Radio Browser stations: {e}")
            return []
    
    async def get_top_tags(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top tags/genres from Radio Browser"""
        try:
            endpoint = "/json/tags"
            params = {"limit": limit}
            
            tags = await self._make_request(endpoint, params)
            
            # Format tags
            formatted_tags = []
            for tag in tags:
                if tag.get('name') and tag.get('stationcount', 0) > 0:
                    formatted_tag = {
                        "name": tag.get('name', ''),
                        "station_count": tag.get('stationcount', 0)
                    }
                    formatted_tags.append(formatted_tag)
            
            logger.info(f"🏷️ Found {len(formatted_tags)} Radio Browser tags")
            return formatted_tags
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser tags: {e}")
            return []
    
    async def get_countries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get countries with radio stations"""
        try:
            endpoint = "/json/countries"
            params = {"limit": limit}
            
            countries = await self._make_request(endpoint, params)
            
            # Format countries
            formatted_countries = []
            for country in countries:
                if country.get('name') and country.get('stationcount', 0) > 0:
                    formatted_country = {
                        "name": country.get('name', ''),
                        "iso_3166_1": country.get('iso_3166_1', ''),
                        "station_count": country.get('stationcount', 0)
                    }
                    formatted_countries.append(formatted_country)
            
            logger.info(f"🌍 Found {len(formatted_countries)} Radio Browser countries")
            return formatted_countries
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser countries: {e}")
            return []
    
    async def get_languages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get languages available in Radio Browser"""
        try:
            endpoint = "/json/languages"
            params = {"limit": limit}
            
            languages = await self._make_request(endpoint, params)
            
            # Format languages
            formatted_languages = []
            for language in languages:
                if language.get('name') and language.get('stationcount', 0) > 0:
                    formatted_language = {
                        "name": language.get('name', ''),
                        "iso_639": language.get('iso_639', ''),
                        "station_count": language.get('stationcount', 0)
                    }
                    formatted_languages.append(formatted_language)
            
            logger.info(f"🗣️ Found {len(formatted_languages)} Radio Browser languages")
            return formatted_languages
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser languages: {e}")
            return []
    
    async def get_station_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get specific station by UUID"""
        try:
            endpoint = f"/json/stations/byuuid/{uuid}"
            
            stations = await self._make_request(endpoint)
            
            if stations and len(stations) > 0:
                station = stations[0]
                formatted_station = {
                    "id": f"rb-{station.get('stationuuid', '')}",
                    "name": station.get('name', ''),
                    "country": station.get('country', ''),
                    "language": station.get('language', ''),
                    "tags": station.get('tags', '').split(',') if station.get('tags') else [],
                    "genre": self._extract_primary_genre(station.get('tags', '')),
                    "stream_url": station.get('url_resolved', ''),
                    "homepage": station.get('homepage', ''),
                    "favicon": station.get('favicon', ''),
                    "bitrate": station.get('bitrate', 0),
                    "votes": station.get('votes', 0),
                    "clickcount": station.get('clickcount', 0),
                    "source": "Radio Browser",
                    "description": station.get('country', '')
                }
                
                logger.info(f"📻 Found Radio Browser station: {formatted_station['name']}")
                return formatted_station
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser station by UUID: {e}")
            return None
    
    def _extract_primary_genre(self, tags: str) -> str:
        """Extract primary genre from tags string"""
        if not tags:
            return "General"
        
        # Common genre mapping
        genre_map = {
            'rock': 'Rock',
            'pop': 'Pop', 
            'jazz': 'Jazz',
            'classical': 'Classical',
            'electronic': 'Electronic',
            'country': 'Country',
            'hip hop': 'Hip-Hop',
            'hiphop': 'Hip-Hop',
            'rap': 'Hip-Hop',
            'dance': 'Dance',
            'folk': 'Folk',
            'blues': 'Blues',
            'reggae': 'Reggae',
            'ambient': 'Ambient',
            'news': 'News',
            'talk': 'Talk',
            'sports': 'Sports'
        }
        
        tags_lower = tags.lower()
        for key, value in genre_map.items():
            if key in tags_lower:
                return value
        
        # Return first tag if no mapping found
        first_tag = tags.split(',')[0].strip()
        return first_tag.title() if first_tag else "General"
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get Radio Browser service information"""
        try:
            # Get basic stats
            popular_stations = await self.get_popular_stations(1)  # Just to test API
            
            return {
                "service_name": "Radio Browser",
                "description": "Community-driven database of radio stations worldwide",
                "website": "https://www.radio-browser.info",
                "api_url": self.base_url,
                "status": "active" if popular_stations else "error",
                "estimated_stations": "70000+",
                "features": [
                    "Global station database",
                    "Search by country/language/genre",
                    "Community-maintained",
                    "Free and open source"
                ],
                "version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"❌ Error getting Radio Browser service info: {e}")
            return {
                "service_name": "Radio Browser",
                "status": "error",
                "message": str(e)
            }

# Create singleton instance
radio_browser_service = RadioBrowserService()