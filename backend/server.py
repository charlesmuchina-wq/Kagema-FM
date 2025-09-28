from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Import enhanced services
from enhanced_services import (
    WeatherService, NewsService, MusicService, 
    AIContentService, LocationService
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Kagema FM Enhanced Radio API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
weather_service = WeatherService()
news_service = NewsService()
music_service = MusicService()
ai_service = AIContentService()
location_service = LocationService()

# Define Models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class UserPreferences(BaseModel):
    interests: List[str] = []
    favorite_genres: List[str] = []
    location: Optional[str] = None
    age_group: Optional[str] = None

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    timestamp: str

class NewsResponse(BaseModel):
    articles: List[Dict[str, Any]]
    summary: Optional[str] = None
    total_count: int

class MusicResponse(BaseModel):
    tracks: List[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]] = None

class EnhancedContentResponse(BaseModel):
    weather: Optional[WeatherResponse]
    news: NewsResponse
    music: MusicResponse
    ai_recommendations: Dict[str, Any]
    location_info: Dict[str, str]

# Original radio station models
class StationInfo(BaseModel):
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    genre: Optional[str] = None
    location: Optional[str] = None
    frequency: Optional[str] = None

# Enhanced API Endpoints

@api_router.get("/")
async def root():
    return {"message": "Kagema FM Enhanced Radio API", "version": "2.0.0"}

@api_router.get("/station-info", response_model=StationInfo)
async def get_station_info():
    """Get current station information for Kagema FM"""
    try:
        # Check if we have station info in database
        station = await db.radio_stations.find_one({"name": "Kagema FM", "isActive": True})
        
        if station:
            return StationInfo(
                name=station["name"],
                description=station["description"],
                streamUrl=station["streamUrl"],
                currentShow=station.get("currentShow"),
                genre=station.get("genre"),
                location=station.get("location"),
                frequency=station.get("frequency")
            )
        else:
            # Return enhanced default Kagema FM info
            return StationInfo(
                name="Kagema FM",
                description="Your favorite local radio station with personalized content, weather updates, and trending music",
                streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
                currentShow="Live Radio with Enhanced Features",
                genre="Talk, Music & News",
                location="Kenya",
                frequency="FM 103.5"
            )
    except Exception as e:
        logging.error(f"Error fetching station info: {e}")
        return StationInfo(
            name="Kagema FM",
            description="Your enhanced radio experience",
            streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
            currentShow="Live Radio"
        )

@api_router.post("/location/weather", response_model=WeatherResponse)
async def get_weather(location: LocationRequest):
    """Get weather data for user's location"""
    try:
        weather_data = await weather_service.get_current_weather(
            location.latitude, location.longitude
        )
        
        if weather_data:
            return WeatherResponse(
                location=weather_data.location,
                temperature=weather_data.temperature,
                feels_like=weather_data.feels_like,
                humidity=weather_data.humidity,
                description=weather_data.description,
                icon=weather_data.icon,
                timestamp=weather_data.timestamp.isoformat()
            )
        else:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
            
    except Exception as e:
        logging.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weather data")

@api_router.post("/location/geocode")
async def geocode_location(location: LocationRequest):
    """Get location information from coordinates"""
    try:
        location_info = location_service.reverse_geocode(
            location.latitude, location.longitude
        )
        return location_info
    except Exception as e:
        logging.error(f"Error geocoding: {e}")
        raise HTTPException(status_code=500, detail="Failed to geocode location")

@api_router.get("/news/local", response_model=NewsResponse)
async def get_local_news(limit: int = 20):
    """Get local Kenyan news"""
    try:
        articles = await news_service.get_kenyan_news(limit)
        news_summary = await ai_service.summarize_news(articles, "Kenya")
        
        articles_data = []
        for article in articles:
            articles_data.append({
                "title": article.title,
                "description": article.description,
                "url": article.url,
                "source": article.source,
                "author": article.author,
                "published_at": article.published_at.isoformat(),
                "image_url": article.image_url,
                "category": article.category
            })
        
        return NewsResponse(
            articles=articles_data,
            summary=news_summary,
            total_count=len(articles_data)
        )
    except Exception as e:
        logging.error(f"Error getting local news: {e}")
        raise HTTPException(status_code=500, detail="Failed to get local news")

@api_router.get("/news/international", response_model=NewsResponse)
async def get_international_news(limit: int = 15):
    """Get international news"""
    try:
        articles = await news_service.get_international_news(limit)
        news_summary = await ai_service.summarize_news(articles, "International")
        
        articles_data = []
        for article in articles:
            articles_data.append({
                "title": article.title,
                "description": article.description,
                "url": article.url,
                "source": article.source,
                "author": article.author,
                "published_at": article.published_at.isoformat(),
                "image_url": article.image_url,
                "category": article.category
            })
        
        return NewsResponse(
            articles=articles_data,
            summary=news_summary,
            total_count=len(articles_data)
        )
    except Exception as e:
        logging.error(f"Error getting international news: {e}")
        raise HTTPException(status_code=500, detail="Failed to get international news")

@api_router.get("/music/trending", response_model=MusicResponse)
async def get_trending_music(country: str = 'KE', limit: int = 30):
    """Get trending music"""
    try:
        tracks = await music_service.get_trending_tracks(country, limit)
        
        tracks_data = []
        for track in tracks:
            tracks_data.append({
                "id": track.id,
                "name": track.name,
                "artists": track.artists,
                "album": track.album,
                "duration_ms": track.duration_ms,
                "popularity": track.popularity,
                "preview_url": track.preview_url,
                "image_url": track.image_url,
                "explicit": track.explicit
            })
        
        return MusicResponse(
            tracks=tracks_data,
            recommendations=None
        )
    except Exception as e:
        logging.error(f"Error getting trending music: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending music")

@api_router.get("/music/kenyan", response_model=MusicResponse)
async def get_kenyan_music(limit: int = 20):
    """Get Kenyan music"""
    try:
        tracks = await music_service.get_kenyan_music(limit)
        
        tracks_data = []
        for track in tracks:
            tracks_data.append({
                "id": track.id,
                "name": track.name,
                "artists": track.artists,
                "album": track.album,
                "duration_ms": track.duration_ms,
                "popularity": track.popularity,
                "preview_url": track.preview_url,
                "image_url": track.image_url,
                "explicit": track.explicit
            })
        
        return MusicResponse(
            tracks=tracks_data,
            recommendations=None
        )
    except Exception as e:
        logging.error(f"Error getting Kenyan music: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Kenyan music")

@api_router.post("/personalized-content", response_model=EnhancedContentResponse)
async def get_personalized_content(
    location: LocationRequest,
    preferences: UserPreferences
):
    """Get personalized content based on location and preferences"""
    try:
        # Get weather data
        weather_data = await weather_service.get_current_weather(
            location.latitude, location.longitude
        )
        
        # Get location info
        location_info = location_service.reverse_geocode(
            location.latitude, location.longitude
        )
        
        # Get news
        local_news = await news_service.get_kenyan_news(10)
        international_news = await news_service.get_international_news(5)
        all_news = local_news + international_news
        news_summary = await ai_service.summarize_news(all_news, location_info["city"])
        
        # Get music
        trending_tracks = await music_service.get_trending_tracks('KE', 15)
        kenyan_tracks = await music_service.get_kenyan_music(10)
        
        # Get AI recommendations
        ai_recommendations = await ai_service.get_music_recommendations(
            user_preferences=preferences.dict(),
            weather_data=weather_data
        )
        
        # Format responses
        weather_response = None
        if weather_data:
            weather_response = WeatherResponse(
                location=weather_data.location,
                temperature=weather_data.temperature,
                feels_like=weather_data.feels_like,
                humidity=weather_data.humidity,
                description=weather_data.description,
                icon=weather_data.icon,
                timestamp=weather_data.timestamp.isoformat()
            )
        
        news_articles = []
        for article in all_news:
            news_articles.append({
                "title": article.title,
                "description": article.description,
                "url": article.url,
                "source": article.source,
                "author": article.author,
                "published_at": article.published_at.isoformat(),
                "category": article.category
            })
        
        all_tracks = trending_tracks + kenyan_tracks
        music_tracks = []
        for track in all_tracks:
            music_tracks.append({
                "id": track.id,
                "name": track.name,
                "artists": track.artists,
                "album": track.album,
                "popularity": track.popularity
            })
        
        return EnhancedContentResponse(
            weather=weather_response,
            news=NewsResponse(
                articles=news_articles,
                summary=news_summary,
                total_count=len(news_articles)
            ),
            music=MusicResponse(
                tracks=music_tracks,
                recommendations=ai_recommendations
            ),
            ai_recommendations=ai_recommendations,
            location_info=location_info
        )
        
    except Exception as e:
        logging.error(f"Error getting personalized content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personalized content")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()