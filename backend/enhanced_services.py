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
        self.api_key = "demo_key"  # Replace with actual key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache = TTLCache(maxsize=100, ttl=1800)  # 30 minutes cache

    async def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        cache_key = f"weather_{latitude:.2f}_{longitude:.2f}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Mock weather data for demo
        weather_data = WeatherData(
            location="Nairobi",
            temperature=22.5,
            feels_like=24.0,
            humidity=65,
            description="Partly Cloudy",
            icon="02d",
            timestamp=datetime.now()
        )
        
        self.cache[cache_key] = weather_data
        return weather_data

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
        for source_name, feed_url in self.kenyan_news_sources.items():
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
        self.emergent_llm_key = "sk-emergent-e19D7A22f3f2b9f8a0"

    async def get_trending_tracks(self, country: str = 'KE', limit: int = 30) -> List[MusicTrack]:
        cache_key = f"trending_{country}_{limit}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Mock trending music data
        mock_tracks = [
            MusicTrack(
                id="track1",
                name="Nakupenda Kenya",
                artists=["Sauti Sol"],
                album="Live and Die in Afrika",
                duration_ms=240000,
                popularity=85,
                preview_url=None,
                image_url=None,
                explicit=False
            ),
            MusicTrack(
                id="track2",
                name="Mama Afrika",
                artists=["Diamond Platnumz"],
                album="A Boy from Tandale",
                duration_ms=220000,
                popularity=80,
                preview_url=None,
                image_url=None,
                explicit=False
            ),
            MusicTrack(
                id="track3",
                name="Jerusalema",
                artists=["Master KG", "Nomcebo Zikode"],
                album="Jerusalema",
                duration_ms=210000,
                popularity=95,
                preview_url=None,
                image_url=None,
                explicit=False
            ),
            MusicTrack(
                id="track4",
                name="Wamlambez",
                artists=["Sailors"],
                album="Wamlambez",
                duration_ms=180000,
                popularity=75,
                preview_url=None,
                image_url=None,
                explicit=False
            )
        ]
        
        self.cache[cache_key] = mock_tracks[:limit]
        return mock_tracks[:limit]

    async def get_kenyan_music(self, limit: int = 20) -> List[MusicTrack]:
        cache_key = f"kenyan_music_{limit}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Mock Kenyan music data
        kenyan_tracks = [
            MusicTrack(
                id="ken1",
                name="Tujiangalie",
                artists=["Nyashinski"],
                album="Lucky You",
                duration_ms=200000,
                popularity=90,
                preview_url=None,
                image_url=None,
                explicit=False
            ),
            MusicTrack(
                id="ken2",
                name="Mdundo",
                artists=["Nviiri The Storyteller"],
                album="Kitenge",
                duration_ms=195000,
                popularity=85,
                preview_url=None,
                image_url=None,
                explicit=False
            )
        ]
        
        self.cache[cache_key] = kenyan_tracks[:limit]
        return kenyan_tracks[:limit]

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