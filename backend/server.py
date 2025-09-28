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
from language_service import GeolocationLanguageService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Kagema FM Multilingual Radio API", version="3.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
weather_service = WeatherService()
news_service = NewsService()
music_service = MusicService()
ai_service = AIContentService()
location_service = LocationService()
language_service = GeolocationLanguageService()

# Define Models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class UserPreferences(BaseModel):
    interests: List[str] = []
    favorite_genres: List[str] = []
    location: Optional[str] = None
    age_group: Optional[str] = None
    preferred_language: Optional[str] = None

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    alternative_languages: List[str]
    county: str
    distance_km: float
    confidence: float
    language_info: Dict[str, Any]
    radio_streams: List[str]
    regional_stations: List[Dict[str, str]]
    localized_content: Dict[str, Any]

class MultilingualStationInfo(BaseModel):
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    genre: Optional[str] = None
    location: Optional[str] = None
    frequency: Optional[str] = None
    detected_language: Optional[str] = None
    alternative_streams: Optional[List[Dict[str, str]]] = None
    localized_content: Optional[Dict[str, Any]] = None

# Original models
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
    language_detection: Optional[LanguageDetectionResponse] = None

# Enhanced API Endpoints

@api_router.get("/")
async def root():
    return {"message": "Kagema FM Multilingual Radio API", "version": "3.0.0"}

@api_router.post("/language/detect", response_model=LanguageDetectionResponse)
async def detect_language(location: LocationRequest):
    """Detect appropriate language based on GPS location"""
    try:
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        # Get regional radio stations for detected language
        regional_stations = language_service.get_regional_radio_stations(
            language_detection['detected_language']
        )
        
        # Get localized content
        localized_content = language_service.get_language_specific_content(
            language_detection['detected_language']
        )
        
        return LanguageDetectionResponse(
            detected_language=language_detection['detected_language'],
            alternative_languages=language_detection['alternative_languages'],
            county=language_detection['county'],
            distance_km=language_detection['distance_km'],
            confidence=language_detection['confidence'],
            language_info=language_detection['language_info'].__dict__ if language_detection['language_info'] else {},
            radio_streams=language_detection['radio_streams'],
            regional_stations=regional_stations,
            localized_content=localized_content
        )
        
    except Exception as e:
        logging.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language")

@api_router.post("/station-info/multilingual", response_model=MultilingualStationInfo)
async def get_multilingual_station_info(location: LocationRequest):
    """Get station information with automatic language detection"""
    try:
        # Detect language based on location
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        detected_lang = language_detection['detected_language']
        
        # Get localized content
        localized_content = language_service.get_language_specific_content(detected_lang)
        
        # Get regional stations for the detected language
        regional_stations = language_service.get_regional_radio_stations(detected_lang)
        
        # Select appropriate stream URL based on language
        primary_stream = language_detection['radio_streams'][0] if language_detection['radio_streams'] else 'http://ice1.somafm.com/groovesalad-256-mp3'
        
        # Get localized station description
        lang_content = localized_content['content']
        station_description = f"{lang_content['greeting']} - Your local radio station with content in {localized_content['language_info'].native_name}"
        
        return MultilingualStationInfo(
            name="Kagema FM",
            description=station_description,
            streamUrl=primary_stream,
            currentShow=f"{lang_content['greeting']} - Live Radio",
            genre="Talk, Music & News",
            location=f"{language_detection['county']}, Kenya",
            frequency="FM 103.5",
            detected_language=detected_lang,
            alternative_streams=regional_stations,
            localized_content=localized_content
        )
        
    except Exception as e:
        logging.error(f"Error getting multilingual station info: {e}")
        # Fallback to English
        return MultilingualStationInfo(
            name="Kagema FM",
            description="Your enhanced multilingual radio experience",
            streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
            currentShow="Live Radio",
            detected_language="en"
        )

@api_router.get("/station-info", response_model=MultilingualStationInfo)
async def get_station_info():
    """Get current station information for Kagema FM (backwards compatibility)"""
    try:
        # Check if we have station info in database
        station = await db.radio_stations.find_one({"name": "Kagema FM", "isActive": True})
        
        if station:
            return MultilingualStationInfo(
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
            return MultilingualStationInfo(
                name="Kagema FM",
                description="Your favorite local radio station with automatic language detection based on your location",
                streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
                currentShow="Live Radio with Multilingual Support",
                genre="Talk, Music & News",
                location="Kenya",
                frequency="FM 103.5"
            )
    except Exception as e:
        logging.error(f"Error fetching station info: {e}")
        return MultilingualStationInfo(
            name="Kagema FM",
            description="Your multilingual radio experience",
            streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
            currentShow="Live Radio"
        )

@api_router.get("/languages")
async def get_supported_languages():
    """Get all supported languages"""
    try:
        languages = language_service.get_all_supported_languages()
        return {
            "supported_languages": [
                {
                    "code": lang.code,
                    "name": lang.name,
                    "native_name": lang.native_name,
                    "region": lang.region
                } for lang in languages.values()
            ],
            "total_count": len(languages)
        }
    except Exception as e:
        logging.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")

@api_router.get("/regional-stations/{language_code}")
async def get_regional_stations(language_code: str):
    """Get regional radio stations for specific language"""
    try:
        stations = language_service.get_regional_radio_stations(language_code)
        language_info = language_service.get_language_specific_content(language_code)
        
        return {
            "language_code": language_code,
            "language_name": language_info['language_info'].name,
            "native_name": language_info['language_info'].native_name,
            "stations": stations,
            "total_count": len(stations)
        }
    except Exception as e:
        logging.error(f"Error getting regional stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get regional stations")

# Keep all existing endpoints from previous version
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

@api_router.post("/personalized-content/multilingual", response_model=EnhancedContentResponse)
async def get_multilingual_personalized_content(
    location: LocationRequest,
    preferences: UserPreferences
):
    """Get personalized content with automatic language detection"""
    try:
        # Detect language first
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        # Get weather data
        weather_data = await weather_service.get_current_weather(
            location.latitude, location.longitude
        )
        
        # Get enhanced location info from language detection
        location_info = {
            "city": language_detection['county'],
            "region": language_detection['county'],
            "country": "Kenya",
            "formatted_address": f"{language_detection['county']}, Kenya"
        }
        
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
        
        # Format responses with language detection
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
        
        # Create language detection response
        regional_stations = language_service.get_regional_radio_stations(
            language_detection['detected_language']
        )
        
        localized_content = language_service.get_language_specific_content(
            language_detection['detected_language']
        )
        
        language_response = LanguageDetectionResponse(
            detected_language=language_detection['detected_language'],
            alternative_languages=language_detection['alternative_languages'],
            county=language_detection['county'],
            distance_km=language_detection['distance_km'],
            confidence=language_detection['confidence'],
            language_info=language_detection['language_info'].__dict__ if language_detection['language_info'] else {},
            radio_streams=language_detection['radio_streams'],
            regional_stations=regional_stations,
            localized_content=localized_content
        )
        
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
            location_info=location_info,
            language_detection=language_response
        )
        
    except Exception as e:
        logging.error(f"Error getting multilingual personalized content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personalized content")

# Keep original personalized content endpoint for backwards compatibility
@api_router.post("/personalized-content", response_model=EnhancedContentResponse)
async def get_personalized_content(
    location: LocationRequest,
    preferences: UserPreferences
):
    """Get personalized content based on location and preferences (backwards compatibility)"""
    return await get_multilingual_personalized_content(location, preferences)

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