import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass
import feedparser
import requests
from cachetools import TTLCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    location: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    timestamp: datetime

@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    author: Optional[str]
    published_at: datetime
    image_url: Optional[str]
    category: Optional[str]

@dataclass
class MusicTrack:
    id: str
    name: str
    artists: List[str]
    album: str
    duration_ms: int
    popularity: int
    preview_url: Optional[str]
    image_url: Optional[str]
    explicit: bool

class WeatherService:
    def __init__(self):
        # Using Open-Meteo API (free, no API key required)
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.cache = TTLCache(maxsize=100, ttl=1800)  # 30 minutes cache

    async def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        cache_key = f"weather_{latitude:.2f}_{longitude:.2f}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Get location name from coordinates
            location_name = await self._get_location_name(latitude, longitude)
            
            # Fetch real-time weather from Open-Meteo
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code',
                'timezone': 'auto'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get('current', {})
                        
                        # Map weather code to description
                        weather_desc = self._get_weather_description(current.get('weather_code', 0))
                        
                        weather_data = WeatherData(
                            location=location_name,
                            temperature=current.get('temperature_2m', 0),
                            feels_like=current.get('apparent_temperature', 0),
                            humidity=current.get('relative_humidity_2m', 0),
                            description=weather_desc,
                            icon=self._get_weather_icon(current.get('weather_code', 0)),
                            timestamp=datetime.now()
                        )
                        
                        self.cache[cache_key] = weather_data
                        return weather_data
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return None
    
    async def _get_location_name(self, latitude: float, longitude: float) -> str:
        """Get location name from coordinates using Open-Meteo geocoding"""
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'count': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.geocoding_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        if results:
                            return results[0].get('name', 'Unknown Location')
            return f"{latitude:.2f}, {longitude:.2f}"
        except:
            return f"{latitude:.2f}, {longitude:.2f}"
    
    def _get_weather_description(self, code: int) -> str:
        """Map WMO weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def _get_weather_icon(self, code: int) -> str:
        """Map weather code to icon code"""
        if code == 0:
            return "01d"  # Clear
        elif code in [1, 2]:
            return "02d"  # Partly cloudy
        elif code == 3:
            return "03d"  # Cloudy
        elif code in [45, 48]:
            return "50d"  # Fog
        elif code in [51, 53, 55, 61, 63, 80, 81]:
            return "10d"  # Rain
        elif code == 65 or code == 82:
            return "09d"  # Heavy rain
        elif code in [71, 73, 75]:
            return "13d"  # Snow
        elif code in [95, 96, 99]:
            return "11d"  # Thunderstorm
        return "01d"

class NewsService:
    def __init__(self):
        self.cache = TTLCache(maxsize=200, ttl=900)  # 15 minutes cache
        self.kenyan_feeds = {
            'Capital FM Kenya': 'https://www.capitalfm.co.ke/news/feed/',
            'The Star Kenya': 'https://www.the-star.co.ke/feed',
            'Daily Nation': 'https://www.nation.co.ke/kenya/news/rss',
            'Standard Digital': 'https://www.standardmedia.co.ke/rss/headlines.php',
        }

    async def get_kenyan_news(self, limit: int = 20) -> List[NewsArticle]:
        cache_key = "kenyan_news"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_articles = []
        
        # Fetch real news from RSS feeds
        for source_name, feed_url in self.kenyan_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Get top 5 from each source
                    # Parse published date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    # Get description
                    description = entry.get('summary', entry.get('description', ''))
                    if description:
                        # Clean HTML tags if present
                        import re
                        description = re.sub('<[^<]+?>', '', description)
                    
                    # Get image URL
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'enclosures') and entry.enclosures:
                        image_url = entry.enclosures[0].get('url')
                    
                    article = NewsArticle(
                        title=entry.get('title', 'No Title'),
                        description=description[:300] if description else 'No description available',
                        url=entry.get('link', ''),
                        source=source_name,
                        author=entry.get('author', 'Staff Writer'),
                        published_at=published,
                        image_url=image_url,
                        category='news'
                    )
                    all_articles.append(article)
            except Exception as e:
                logger.error(f"Error fetching news from {source_name}: {str(e)}")
                continue
        
        # Sort by published date
        all_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        self.cache[cache_key] = all_articles[:limit]
        return all_articles[:limit]

    async def get_international_news(self, limit: int = 15) -> List[NewsArticle]:
        cache_key = "international_news"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Use BBC World News RSS feed for international news
        international_feeds = {
            'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
        }
        
        all_articles = []
        
        for source_name, feed_url in international_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:8]:  # Get top 8 from each source
                    # Parse published date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    # Get description
                    description = entry.get('summary', entry.get('description', ''))
                    if description:
                        import re
                        description = re.sub('<[^<]+?>', '', description)
                    
                    # Get image URL
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                        image_url = entry.media_thumbnail[0].get('url')
                    
                    article = NewsArticle(
                        title=entry.get('title', 'No Title'),
                        description=description[:300] if description else 'No description available',
                        url=entry.get('link', ''),
                        source=source_name,
                        author=entry.get('author', 'Staff Writer'),
                        published_at=published,
                        image_url=image_url,
                        category='international'
                    )
                    all_articles.append(article)
            except Exception as e:
                logger.error(f"Error fetching international news from {source_name}: {str(e)}")
                continue
        
        # Sort by published date
        all_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        self.cache[cache_key] = all_articles[:limit]
        return all_articles[:limit]

class MusicService:
    def __init__(self):
        self.cache = TTLCache(maxsize=300, ttl=3600)  # 1 hour cache
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.access_token = None
        self.token_expiry = None
        
        logger.info("Music Service initialized with Spotify API integration")

    async def _get_access_token(self) -> Optional[str]:
        """Get Spotify API access token using client credentials flow"""
        # Check if we have a valid cached token
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry:
                return self.access_token
        
        try:
            # Get new token
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            import base64
            auth_str = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_str.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data['access_token']
                        # Token expires in 3600 seconds, we'll refresh 5 min early
                        self.token_expiry = datetime.now() + timedelta(seconds=data['expires_in'] - 300)
                        logger.info("Successfully obtained Spotify access token")
                        return self.access_token
                    else:
                        logger.error(f"Spotify auth error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting Spotify token: {str(e)}")
            return None

    async def get_trending_tracks(self, country: str = 'KE', limit: int = 30) -> List[MusicTrack]:
        cache_key = f"trending_{country}_{limit}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            token = await self._get_access_token()
            if not token:
                logger.error("Could not get Spotify access token")
                return []
            
            # Get playlist ID for country (using "Top 50" playlists)
            playlist_ids = {
                'KE': '37i9dQZEVXbMH2jvi6jvjk',  # Kenya Top 50
                'US': '37i9dQZEVXbLRQDuF5jeBp',  # US Top 50
                'GB': '37i9dQZEVXbLnolsZ8PSNw',  # UK Top 50
                'NG': '37i9dQZEVXbKY7jLzlJ11V',  # Nigeria Top 50
                'ZA': '37i9dQZEVXbMH2jvi6jvjk',  # South Africa Top 50
                'GLOBAL': '37i9dQZEVXbMDoHDwVN2tF',  # Global Top 50
            }
            
            playlist_id = playlist_ids.get(country, playlist_ids['GLOBAL'])
            
            # Fetch playlist tracks
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            headers = {
                'Authorization': f'Bearer {token}'
            }
            params = {
                'limit': min(limit, 50),
                'fields': 'items(track(id,name,artists(name),album(name,images),duration_ms,popularity,preview_url,explicit))'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for item in data.get('items', []):
                            track = item.get('track')
                            if track:
                                # Get album image
                                image_url = None
                                if track.get('album', {}).get('images'):
                                    image_url = track['album']['images'][0]['url']
                                
                                music_track = MusicTrack(
                                    id=track['id'],
                                    name=track['name'],
                                    artists=[artist['name'] for artist in track.get('artists', [])],
                                    album=track.get('album', {}).get('name', ''),
                                    duration_ms=track.get('duration_ms', 0),
                                    popularity=track.get('popularity', 0),
                                    preview_url=track.get('preview_url'),
                                    image_url=image_url,
                                    explicit=track.get('explicit', False)
                                )
                                tracks.append(music_track)
                        
                        self.cache[cache_key] = tracks
                        logger.info(f"Fetched {len(tracks)} trending tracks for {country}")
                        return tracks
                    else:
                        logger.error(f"Spotify API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching trending tracks: {str(e)}")
            return []

    async def get_kenyan_music(self, limit: int = 20) -> List[MusicTrack]:
        """Get Kenyan music - uses Kenya trending tracks"""
        return await self.get_trending_tracks(country='KE', limit=limit)

class AIContentService:
    def __init__(self):
        self.api_key = "sk-emergent-e19D7A22f3f2b9f8a0"
        self.base_url = "https://api.emergentmethods.ai/v1"
        self.cache = TTLCache(maxsize=100, ttl=1800)

    async def summarize_news(self, articles: List[NewsArticle], user_location: str = None) -> str:
        """Summarize news articles using AI"""
        cache_key = f"news_summary_{len(articles)}_{user_location}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Mock AI summary for demo
        summary = f"Today's key news highlights include economic growth in Kenya, new traffic solutions in Nairobi, and upcoming entertainment events. Local developments show positive trends in technology and infrastructure. {len(articles)} stories are shaping the day's narrative."
        
        self.cache[cache_key] = summary
        return summary

    async def get_music_recommendations(self, user_preferences: Dict[str, Any], weather_data: WeatherData = None) -> Dict[str, Any]:
        """Generate music recommendations based on user preferences and context"""
        cache_key = f"music_rec_{hash(str(user_preferences))}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Mock AI recommendations
        weather_context = ""
        if weather_data:
            if "rain" in weather_data.description.lower():
                weather_context = "Perfect weather for mellow tunes and acoustic music."
            elif "sunny" in weather_data.description.lower():
                weather_context = "Bright weather calls for upbeat and energetic music."
            else:
                weather_context = "Great weather for any type of music."

        recommendations = {
            "genres": ["Afrobeats", "East African Hip Hop", "Benga", "Gospel"],
            "mood_recommendations": ["Uplifting Kenyan hits", "Chill East African vibes"],
            "weather_based": weather_context,
            "explanation": f"Based on your location and current weather ({weather_data.description if weather_data else 'unknown'}), we recommend a mix of local and popular African music."
        }
        
        self.cache[cache_key] = recommendations
        return recommendations

class LocationService:
    @staticmethod
    def reverse_geocode(latitude: float, longitude: float) -> Dict[str, str]:
        """Reverse geocode coordinates to location info for Kenya and Brazil"""
        # Check if coordinates are in Kenya
        if -5 <= latitude <= 5 and 33 <= longitude <= 42:
            # Kenya coordinates
            if -1.5 <= latitude <= -1.0 and 36.5 <= longitude <= 37.0:
                return {
                    "city": "Nairobi",
                    "region": "Nairobi County",
                    "country": "Kenya",
                    "formatted_address": "Nairobi, Kenya"
                }
            else:
                return {
                    "city": "Unknown City",
                    "region": "Unknown Region", 
                    "country": "Kenya",
                    "formatted_address": "Kenya"
                }
        
        # Check if coordinates are in Brazil
        elif -35 <= latitude <= 5 and -75 <= longitude <= -30:
            # Brazil coordinates
            if -24 <= latitude <= -23 and -47 <= longitude <= -46:
                return {
                    "city": "São Paulo",
                    "region": "São Paulo",
                    "country": "Brazil",
                    "formatted_address": "São Paulo, Brazil"
                }
            elif -23.5 <= latitude <= -22.5 and -44 <= longitude <= -43:
                return {
                    "city": "Rio de Janeiro", 
                    "region": "Rio de Janeiro",
                    "country": "Brazil",
                    "formatted_address": "Rio de Janeiro, Brazil"
                }
            elif -20.5 <= latitude <= -19 and -44.5 <= longitude <= -43:
                return {
                    "city": "Belo Horizonte",
                    "region": "Minas Gerais",
                    "country": "Brazil",
                    "formatted_address": "Belo Horizonte, Brazil"
                }
            elif -30.5 <= latitude <= -29.5 and -52 <= longitude <= -51:
                return {
                    "city": "Porto Alegre",
                    "region": "Rio Grande do Sul", 
                    "country": "Brazil",
                    "formatted_address": "Porto Alegre, Brazil"
                }
            elif -16.5 <= latitude <= -15 and -48.5 <= longitude <= -47.5:
                return {
                    "city": "Brasília",
                    "region": "Distrito Federal",
                    "country": "Brazil", 
                    "formatted_address": "Brasília, Brazil"
                }
            elif -13.5 <= latitude <= -12 and -39 <= longitude <= -38:
                return {
                    "city": "Salvador",
                    "region": "Bahia",
                    "country": "Brazil",
                    "formatted_address": "Salvador, Brazil"
                }
            elif -8.5 <= latitude <= -7.5 and -35.5 <= longitude <= -34.5:
                return {
                    "city": "Recife",
                    "region": "Pernambuco",
                    "country": "Brazil",
                    "formatted_address": "Recife, Brazil"
                }
            else:
                return {
                    "city": "Unknown City",
                    "region": "Unknown Region",
                    "country": "Brazil", 
                    "formatted_address": "Brazil"
                }
        
        # Default fallback
        else:
            return {
                "city": "Unknown City",
                "region": "Unknown Region",
                "country": "Unknown",
                "formatted_address": "Unknown Location"
            }