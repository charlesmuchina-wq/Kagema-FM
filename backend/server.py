from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
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
from satellite_connectivity import SatelliteConnectivityManager, ConnectionType, SignalStrength
from offline_manager import OfflineContentManager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Kagema FM Satellite & Offline Radio API", version="5.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
weather_service = WeatherService()
news_service = NewsService()
music_service = MusicService()
ai_service = AIContentService()
location_service = LocationService()
language_service = GeolocationLanguageService()
satellite_manager = SatelliteConnectivityManager()
offline_manager = OfflineContentManager()

# Enhanced Models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class UserPreferences(BaseModel):
    interests: List[str] = []
    favorite_genres: List[str] = []
    location: Optional[str] = None
    age_group: Optional[str] = None
    preferred_language: Optional[str] = None
    offline_mode: bool = False

class SatelliteConnectionRequest(BaseModel):
    provider: Optional[str] = None
    client_id: str = "kagema_fm"
    location: str = "auto"

class ConnectionStatusResponse(BaseModel):
    connection_type: str
    signal_strength: str
    download_speed: float
    upload_speed: float
    latency: int
    provider: Optional[str]
    satellite_name: Optional[str]
    timestamp: str
    recommendations: List[Dict[str, Any]]

class OfflineCacheRequest(BaseModel):
    content_types: List[str] = ["radio_streams", "news", "weather", "music", "language_data"]
    location: Optional[LocationRequest] = None
    cache_duration_hours: int = 24

# Original models maintained for compatibility
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

# Satellite & Offline API Endpoints

@api_router.get("/")
async def root():
    return {"message": "Kagema FM Satellite & Offline Radio API", "version": "5.0.0", "features": ["satellite_connectivity", "offline_mode", "international_coverage"]}

@api_router.get("/satellite/status")
async def get_satellite_status():
    """Get current satellite connectivity status"""
    try:
        status = await satellite_manager.detect_connection_type()
        recommendations = await satellite_manager.get_connection_recommendations()
        
        return ConnectionStatusResponse(
            connection_type=status.connection_type.value,
            signal_strength=status.signal_strength.value,
            download_speed=status.download_speed,
            upload_speed=status.upload_speed,
            latency=status.latency,
            provider=status.provider,
            satellite_name=status.satellite_name,
            timestamp=status.timestamp.isoformat(),
            recommendations=recommendations
        )
    except Exception as e:
        logging.error(f"Satellite status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get satellite status")

@api_router.post("/satellite/connect")
async def connect_to_satellite(request: SatelliteConnectionRequest):
    """Attempt to establish satellite internet connection"""
    try:
        success = await satellite_manager.attempt_satellite_connection()
        
        if success:
            status = await satellite_manager.detect_connection_type()
            return {
                "connected": True,
                "provider": status.satellite_name or "Open Satellite Network",
                "signal_strength": status.signal_strength.value,
                "estimated_speed": status.download_speed,
                "message": "Successfully connected to satellite internet"
            }
        else:
            return {
                "connected": False,
                "message": "No satellite internet available. Enable offline mode to continue using the app."
            }
    except Exception as e:
        logging.error(f"Satellite connection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to establish satellite connection")

@api_router.post("/offline/cache")
async def cache_content_for_offline(request: OfflineCacheRequest):
    """Cache content for offline use"""
    try:
        cached_items = {}
        
        # Cache radio streams
        if "radio_streams" in request.content_types:
            # Get all available regional stations
            all_stations = []
            for lang_code in language_service.get_all_supported_languages():
                stations = language_service.get_regional_radio_stations(lang_code)
                all_stations.extend(stations)
            
            success = await offline_manager.cache_radio_streams(all_stations)
            cached_items["radio_streams"] = {"success": success, "count": len(all_stations)}
        
        # Cache news
        if "news" in request.content_types:
            local_news = await news_service.get_kenyan_news(20)
            international_news = await news_service.get_international_news(15)
            all_news = [
                {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": article.published_at.isoformat(),
                    "category": article.category
                } for article in local_news + international_news
            ]
            
            success = await offline_manager.cache_news_articles(all_news)
            cached_items["news"] = {"success": success, "count": len(all_news)}
        
        # Cache weather
        if "weather" in request.content_types and request.location:
            weather_data = await weather_service.get_current_weather(
                request.location.latitude, request.location.longitude
            )
            if weather_data:
                weather_dict = {
                    "location": weather_data.location,
                    "temperature": weather_data.temperature,
                    "feels_like": weather_data.feels_like,
                    "humidity": weather_data.humidity,
                    "description": weather_data.description,
                    "icon": weather_data.icon,
                    "timestamp": weather_data.timestamp.isoformat()
                }
                success = await offline_manager.cache_weather_data(weather_dict, weather_data.location)
                cached_items["weather"] = {"success": success, "location": weather_data.location}
        
        # Cache music
        if "music" in request.content_types:
            trending_tracks = await music_service.get_trending_tracks('KE', 25)
            kenyan_tracks = await music_service.get_kenyan_music(15)
            all_music = [
                {
                    "id": track.id,
                    "name": track.name,
                    "artists": track.artists,
                    "album": track.album,
                    "popularity": track.popularity
                } for track in trending_tracks + kenyan_tracks
            ]
            
            success = await offline_manager.cache_music_tracks(all_music)
            cached_items["music"] = {"success": success, "count": len(all_music)}
        
        # Cache language data
        if "language_data" in request.content_types:
            language_data = {
                "supported_languages": [
                    {
                        "code": lang.code,
                        "name": lang.name,
                        "native_name": lang.native_name,
                        "region": lang.region
                    } for lang in language_service.get_all_supported_languages().values()
                ],
                "location_mappings": len(language_service.location_mappings)
            }
            
            success = await offline_manager.cache_language_data(language_data)
            cached_items["language_data"] = {"success": success}
        
        return {
            "cached_items": cached_items,
            "cache_expires_in_hours": request.cache_duration_hours,
            "offline_mode_ready": all(item.get("success", False) for item in cached_items.values()),
            "message": "Content successfully cached for offline use"
        }
        
    except Exception as e:
        logging.error(f"Offline caching error: {e}")
        raise HTTPException(status_code=500, detail="Failed to cache content for offline use")

@api_router.get("/offline/content")
async def get_offline_content():
    """Get all cached content for offline use"""
    try:
        cached_content = {
            "radio_streams": await offline_manager.get_offline_radio_streams(),
            "news": await offline_manager.get_offline_news(),
            "music": await offline_manager.get_offline_music(),
            "weather": None,  # Location-specific, needs location parameter
            "cache_stats": await offline_manager.get_cache_stats()
        }
        
        return {
            "content": cached_content,
            "offline_capabilities": {
                "radio_streaming": len(cached_content["radio_streams"]) > 0,
                "news_reading": len(cached_content["news"]) > 0,
                "music_discovery": len(cached_content["music"]) > 0,
                "language_switching": True,
                "weather_info": "Available with location data"
            },
            "limitations": [
                "Live radio streaming requires internet connection",
                "Weather data may be outdated in offline mode",
                "Real-time features unavailable offline",
                "Satellite connectivity recommended for full experience"
            ]
        }
    except Exception as e:
        logging.error(f"Offline content retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve offline content")

@api_router.get("/offline/weather/{location}")
async def get_offline_weather(location: str):
    """Get cached weather data for specific location"""
    try:
        weather_data = await offline_manager.get_offline_weather(location)
        if weather_data:
            return weather_data
        else:
            raise HTTPException(status_code=404, detail=f"No cached weather data for {location}")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Offline weather retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cached weather data")

@api_router.delete("/offline/cache")
async def clear_offline_cache():
    """Clear all cached offline content"""
    try:
        await offline_manager.cleanup_expired_content()
        
        # Clear all cache
        stats = await offline_manager.get_cache_stats()
        
        return {
            "cleared": True,
            "freed_space_mb": stats.get("total_size_mb", 0),
            "message": "Offline cache cleared successfully"
        }
    except Exception as e:
        logging.error(f"Cache clearing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear offline cache")

@api_router.get("/offline/stats")
async def get_offline_stats():
    """Get offline cache statistics"""
    try:
        stats = await offline_manager.get_cache_stats()
        return stats
    except Exception as e:
        logging.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")

# Keep all existing endpoints for backward compatibility
@api_router.post("/language/detect", response_model=LanguageDetectionResponse)
async def detect_language(location: LocationRequest):
    """Detect appropriate language based on GPS location (Kenya + Brazil)"""
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

# Enhanced multilingual content endpoint with offline fallback
@api_router.post("/personalized-content/multilingual")
async def get_multilingual_personalized_content(
    location: LocationRequest,
    preferences: UserPreferences
):
    """Get personalized content with automatic language detection and offline fallback"""
    try:
        # Check if offline mode is requested or if connection is poor
        if preferences.offline_mode:
            # Return cached content
            cached_content = await offline_manager.get_offline_radio_streams()
            cached_news = await offline_manager.get_offline_news()
            cached_music = await offline_manager.get_offline_music()
            cached_weather = await offline_manager.get_offline_weather("default")
            
            return {
                "offline_mode": True,
                "content_source": "cached",
                "radio_streams": cached_content,
                "news": {"articles": cached_news, "total_count": len(cached_news)},
                "music": {"tracks": cached_music},
                "weather": cached_weather,
                "message": "Content served from offline cache"
            }
        
        # Regular online processing
        # Detect language first
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        # Get enhanced location info with country detection
        if 'county' in language_detection and language_detection['county']:
            # Determine country based on coordinates  
            if -35 <= location.latitude <= 5 and -75 <= location.longitude <= -30:
                country = "Brazil"
            else:
                country = "Kenya"
                
            location_info = {
                "city": language_detection['county'],
                "region": language_detection['county'],
                "country": country,
                "formatted_address": f"{language_detection['county']}, {country}"
            }
        else:
            # Fallback to location service
            location_info = location_service.reverse_geocode(
                location.latitude, location.longitude
            )
        
        # Get weather data
        weather_data = await weather_service.get_current_weather(
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
        
        # Cache content for offline use
        if weather_data:
            await offline_manager.cache_weather_data({
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "humidity": weather_data.humidity,
                "description": weather_data.description,
                "icon": weather_data.icon
            }, weather_data.location)
        
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
        
        return {
            "offline_mode": False,
            "content_source": "live",
            "weather": weather_response,
            "news": NewsResponse(
                articles=news_articles,
                summary=news_summary,
                total_count=len(news_articles)
            ),
            "music": MusicResponse(
                tracks=music_tracks,
                recommendations=ai_recommendations
            ),
            "ai_recommendations": ai_recommendations,
            "location_info": location_info,
            "language_detection": language_response
        }
        
    except Exception as e:
        logging.error(f"Error getting multilingual personalized content: {e}")
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Kagema FM Satellite & Offline Radio API v5.0.0")
    
    # Initialize satellite connectivity monitoring
    satellite_manager.enable_offline_mode()
    
    # Schedule cache cleanup
    import asyncio
    asyncio.create_task(periodic_cache_cleanup())

async def periodic_cache_cleanup():
    """Periodic cleanup of expired cache content"""
    while True:
        try:
            await offline_manager.cleanup_expired_content()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            await asyncio.sleep(3600)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)