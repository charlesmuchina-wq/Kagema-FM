from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
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
from content_compliance import ContentComplianceManager, ContentRating

# Import Dragon KARAU AI systems
from dragon_ai_search_api import router as dragon_search_router
from radio_intelligence_api import router as radio_intelligence_router

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
compliance_manager = ContentComplianceManager()

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
    user_age: Optional[int] = None
    accept_adult_content: bool = False

class ContentComplianceRequest(BaseModel):
    country_code: str
    language_code: str = "en"
    content_types: List[str] = ["radio_streams", "music", "news"]
    user_age: Optional[int] = None

class UserAcknowledgmentRequest(BaseModel):
    disclaimer_ids: List[str]
    user_id: str
    timestamp: str
    user_age: int
    country_code: str

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

# Enhanced response models with compliance
class EnhancedStationResponse(BaseModel):
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    detected_language: Optional[str] = None
    location: Optional[str] = None
    content_rating: str = "general"
    content_disclaimers: List[Dict[str, Any]] = []
    compliance_info: Dict[str, Any] = {}
    requires_age_verification: bool = False

# Content Compliance API Endpoints

@api_router.get("/")
async def root():
    return {
        "message": "Kagema FM Satellite & Offline Radio API", 
        "version": "5.0.0", 
        "features": ["satellite_connectivity", "offline_mode", "international_coverage", "content_compliance"],
        "disclaimer": "Content compliance and local regulations are the responsibility of broadcasters and listeners"
    }

@api_router.get("/station-info")
async def get_basic_station_info():
    """Get basic Kagema FM station information with stream URL"""
    return {
        "name": "Kagema FM",
        "description": "Your premier radio station with live streaming",
        "streamUrl": "http://ice1.somafm.com/groovesalad-256-mp3",
        "currentShow": "Live Radio",
        "frequency": "101.5 FM",
        "location": "Nairobi, Kenya",
        "website": "https://kagema-fm.com",
        "contact": "info@kagema-fm.com"
    }

@api_router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "sw", "name": "Swahili", "native_name": "Kiswahili"},
            {"code": "pt-br", "name": "Portuguese (Brazil)", "native_name": "Português (Brasil)"},
            {"code": "ki", "name": "Kikuyu", "native_name": "Gĩkũyũ"},
            {"code": "luo", "name": "Luo", "native_name": "Dholuo"},
            {"code": "luy", "name": "Luhya", "native_name": "Luluhya"},
            {"code": "kam", "name": "Kamba", "native_name": "Kikamba"},
            {"code": "kln", "name": "Kalenjin", "native_name": "Kalenjin"}
        ],
        "total_count": 8,
        "supported_countries": ["KE", "BR", "GLOBAL"]
    }

@api_router.post("/language/detect")
async def detect_language_from_location(location: LocationRequest):
    """Detect language based on GPS coordinates"""
    try:
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude,
            location.longitude
        )
        
        if language_detection:
            return {
                "detected_language": language_detection.get("detected_language", "en"),
                "county": language_detection.get("county", "Unknown"),
                "region": language_detection.get("region", "Unknown"),
                "confidence": language_detection.get("confidence", 1.0),
                "alternative_languages": language_detection.get("alternative_languages", []),
                "radio_streams": language_detection.get("radio_streams", []),
                "language_info": language_detection.get("language_info", {}),
                "regional_stations": language_detection.get("radio_streams", [])
            }
        else:
            # Return default English fallback
            return {
                "detected_language": "en",
                "county": "Unknown",
                "region": "Global", 
                "confidence": 0.5,
                "alternative_languages": ["sw"],
                "radio_streams": ["http://ice1.somafm.com/groovesalad-256-mp3"],
                "language_info": {
                    "code": "en",
                    "name": "English",
                    "native_name": "English"
                },
                "regional_stations": ["http://ice1.somafm.com/groovesalad-256-mp3"]
            }
            
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language from coordinates")

@api_router.post("/integrations/initialize")
async def initialize_integrations(request: dict):
    """Initialize platform integrations (Google Maps, Spotify, Voice Control, etc.)"""
    try:
        integration_type = request.get("type", "general")
        config = request.get("config", {})
        
        # Mock successful initialization for web preview
        if integration_type == "google_maps":
            return {
                "integration": "google_maps",
                "status": "initialized",
                "config": {
                    "maps_api_available": False,  # Not available on web preview
                    "places_api_available": False,
                    "geocoding_api_available": False
                },
                "message": "Google Maps integration initialized (web preview mode)"
            }
        elif integration_type == "spotify":
            return {
                "integration": "spotify",
                "status": "initialized", 
                "config": {
                    "api_available": False,  # Not available on web preview
                    "client_id": None,
                    "scopes": ["user-read-playback-state", "user-modify-playback-state"]
                },
                "message": "Spotify integration initialized (web preview mode)"
            }
        elif integration_type == "voice_control":
            return {
                "integration": "voice_control",
                "status": "initialized",
                "config": {
                    "speech_recognition_available": False,  # Not available on web
                    "text_to_speech_available": False,
                    "supported_languages": ["en", "sw", "pt-br"]
                },
                "message": "Voice control integration initialized (web preview mode)"
            }
        else:
            # General integration initialization
            return {
                "integration": "general",
                "status": "initialized",
                "config": {
                    "platform": "web_preview",
                    "location_services": True,
                    "audio_playback": True,
                    "network_requests": True
                },
                "available_integrations": [
                    "google_maps", "spotify", "voice_control", "emergency_alerts"
                ],
                "message": "Platform integrations initialized successfully"
            }
            
    except Exception as e:
        logger.error(f"Integration initialization error: {e}")
        return {
            "integration": integration_type,
            "status": "error",
            "message": f"Failed to initialize integration: {str(e)}"
        }

@api_router.post("/compliance/disclaimers")
async def get_content_disclaimers(request: ContentComplianceRequest):
    """Get applicable content disclaimers for user's location and content types"""
    try:
        disclaimers = compliance_manager.generate_content_warning_response(
            request.country_code,
            request.language_code, 
            request.content_types
        )
        return disclaimers
    except Exception as e:
        logging.error(f"Content disclaimers error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content disclaimers")

@api_router.post("/compliance/acknowledge")
async def acknowledge_disclaimers(request: UserAcknowledgmentRequest):
    """Record user acknowledgment of content disclaimers"""
    try:
        # Store user acknowledgment in database
        acknowledgment_record = {
            "user_id": request.user_id,
            "disclaimer_ids": request.disclaimer_ids,
            "timestamp": request.timestamp,
            "user_age": request.user_age,
            "country_code": request.country_code,
            "acknowledged_at": datetime.now().isoformat()
        }
        
        await db.user_acknowledgments.insert_one(acknowledgment_record)
        
        return {
            "acknowledgment_recorded": True,
            "valid_until": (datetime.now().replace(hour=23, minute=59, second=59)).isoformat(),
            "message": "Content disclaimers acknowledged successfully"
        }
    except Exception as e:
        logging.error(f"Disclaimer acknowledgment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record disclaimer acknowledgment")

@api_router.post("/compliance/check-content")
async def check_content_compliance(
    country_code: str,
    content_rating: str,
    user_age: Optional[int] = None,
    current_hour: Optional[int] = None
):
    """Check if content is compliant with regional regulations"""
    try:
        if current_hour is None:
            current_hour = datetime.now().hour
        
        rating_enum = ContentRating(content_rating) if content_rating in [r.value for r in ContentRating] else ContentRating.GENERAL
        
        compliance_result = compliance_manager.check_content_rating_compliance(
            rating_enum, 
            user_age or 18, 
            country_code, 
            current_hour
        )
        
        return compliance_result
    except Exception as e:
        logging.error(f"Content compliance check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check content compliance")

# Enhanced station info with compliance
@api_router.post("/station-info/multilingual", response_model=EnhancedStationResponse)
async def get_multilingual_station_info_with_compliance(location: LocationRequest):
    """Get station information with automatic language detection and compliance info"""
    try:
        # Detect language based on location
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        detected_lang = language_detection['detected_language']
        
        # Determine country for compliance
        if -35 <= location.latitude <= 5 and -75 <= location.longitude <= -30:
            country_code = "BR"
        elif -5 <= location.latitude <= 5 and 33 <= location.longitude <= 42:
            country_code = "KE"
        else:
            country_code = "GLOBAL"
        
        # Get compliance information
        compliance_info = compliance_manager.generate_content_warning_response(
            country_code,
            detected_lang,
            ["radio_streams", "music"]
        )
        
        # Get localized content
        localized_content = language_service.get_language_specific_content(detected_lang)
        
        # Get regional stations for the detected language
        regional_stations = language_service.get_regional_radio_stations(detected_lang)
        
        # Select appropriate stream URL based on language
        primary_stream = language_detection['radio_streams'][0] if language_detection['radio_streams'] else 'http://ice1.somafm.com/groovesalad-256-mp3'
        
        # Get localized station description
        lang_content = localized_content['content']
        station_description = f"{lang_content['greeting']} - Your local radio station with content in {localized_content['language_info'].native_name}"
        
        return EnhancedStationResponse(
            name="Kagema FM",
            description=station_description,
            streamUrl=primary_stream,
            currentShow=f"{lang_content['greeting']} - Live Radio",
            detected_language=detected_lang,
            location=f"{language_detection['county']}, {country_code}",
            content_rating="mature",  # Default to mature for radio content
            content_disclaimers=[
                {
                    "id": disclaimer["id"],
                    "title": disclaimer["title"], 
                    "severity": disclaimer["severity"]
                } for disclaimer in compliance_info["content_disclaimers"]
            ],
            compliance_info=compliance_info["regional_compliance"],
            requires_age_verification=True
        )
        
    except Exception as e:
        logging.error(f"Error getting multilingual station info with compliance: {e}")
        # Fallback response with basic compliance
        return EnhancedStationResponse(
            name="Kagema FM",
            description="Your enhanced multilingual radio experience",
            streamUrl="http://ice1.somafm.com/groovesalad-256-mp3",
            currentShow="Live Radio",
            content_rating="mature",
            content_disclaimers=[
                {
                    "id": "general_responsibility",
                    "title": "Content Responsibility Notice",
                    "severity": "critical"
                }
            ],
            compliance_info={"adult_age_threshold": 18, "content_warnings_required": True},
            requires_age_verification=True
        )

# Keep existing satellite and offline endpoints...
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
                "message": "Successfully connected to satellite internet",
                "compliance_notice": "Content broadcast via satellite must comply with local regulations"
            }
        else:
            return {
                "connected": False,
                "message": "No satellite internet available. Enable offline mode to continue using the app.",
                "offline_disclaimer": "Offline mode content subject to caching limitations and compliance requirements"
            }
    except Exception as e:
        logging.error(f"Satellite connection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to establish satellite connection")

@api_router.post("/offline/cache")
async def cache_content_for_offline(request: OfflineCacheRequest):
    """Cache content for offline use with compliance warnings"""
    try:
        cached_items = {}
        
        # Cache radio streams
        if "radio_streams" in request.content_types:
            all_stations = []
            for lang_code in language_service.get_all_supported_languages():
                stations = language_service.get_regional_radio_stations(lang_code)
                all_stations.extend(stations)
            
            success = await offline_manager.cache_radio_streams(all_stations)
            cached_items["radio_streams"] = {"success": success, "count": len(all_stations)}
        
        # Cache other content types (news, weather, music)...
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
        
        return {
            "cached_items": cached_items,
            "cache_expires_in_hours": request.cache_duration_hours,
            "offline_mode_ready": all(item.get("success", False) for item in cached_items.values()),
            "compliance_warning": "Cached content must still comply with local regulations when accessed offline",
            "disclaimer": "Users remain responsible for content compliance regardless of connection method",
            "message": "Content successfully cached for offline use"
        }
        
    except Exception as e:
        logging.error(f"Offline caching error: {e}")
        raise HTTPException(status_code=500, detail="Failed to cache content for offline use")

# Enhanced multilingual content endpoint with compliance
@api_router.post("/personalized-content/multilingual")
async def get_multilingual_personalized_content(
    location: LocationRequest,
    preferences: UserPreferences
):
    """Get personalized content with automatic language detection, compliance, and offline fallback"""
    try:
        # Determine country for compliance
        if -35 <= location.latitude <= 5 and -75 <= location.longitude <= -30:
            country_code = "BR"
        elif -5 <= location.latitude <= 5 and 33 <= location.longitude <= 42:
            country_code = "KE"
        else:
            country_code = "GLOBAL"
        
        # Check if offline mode is requested
        if preferences.offline_mode:
            cached_content = await offline_manager.get_offline_radio_streams()
            cached_news = await offline_manager.get_offline_news()
            cached_music = await offline_manager.get_offline_music()
            
            # Get compliance info even for offline content
            compliance_info = compliance_manager.generate_content_warning_response(
                country_code,
                preferences.preferred_language or "en",
                ["radio_streams", "news", "music"]
            )
            
            return {
                "offline_mode": True,
                "content_source": "cached",
                "radio_streams": cached_content,
                "news": {"articles": cached_news, "total_count": len(cached_news)},
                "music": {"tracks": cached_music},
                "content_disclaimers": compliance_info["content_disclaimers"],
                "compliance_info": compliance_info["regional_compliance"],
                "message": "Content served from offline cache - compliance requirements still apply"
            }
        
        # Regular online processing with compliance
        language_detection = language_service.detect_language_from_coordinates(
            location.latitude, location.longitude
        )
        
        # Get compliance information
        compliance_info = compliance_manager.generate_content_warning_response(
            country_code,
            language_detection['detected_language'],
            ["radio_streams", "news", "music"]
        )
        
        # Check content rating compliance if user age provided
        content_compliance_check = None
        if preferences.user_age:
            content_compliance_check = compliance_manager.check_content_rating_compliance(
                ContentRating.MATURE,  # Default rating for radio content
                preferences.user_age,
                country_code,
                datetime.now().hour
            )
        
        # Get enhanced location info with country detection
        if 'county' in language_detection and language_detection['county']:
            location_info = {
                "city": language_detection['county'],
                "region": language_detection['county'],
                "country": "Brazil" if country_code == "BR" else "Kenya" if country_code == "KE" else "Unknown",
                "formatted_address": f"{language_detection['county']}, {country_code}"
            }
        else:
            location_info = location_service.reverse_geocode(
                location.latitude, location.longitude
            )
        
        # Get content data (weather, news, music)...
        weather_data = await weather_service.get_current_weather(
            location.latitude, location.longitude
        )
        local_news = await news_service.get_kenyan_news(10)
        international_news = await news_service.get_international_news(5)
        all_news = local_news + international_news
        trending_tracks = await music_service.get_trending_tracks('KE', 15)
        kenyan_tracks = await music_service.get_kenyan_music(10)
        
        # Format response with compliance information
        response = {
            "offline_mode": False,
            "content_source": "live",
            "location_info": location_info,
            "content_disclaimers": compliance_info["content_disclaimers"],
            "compliance_info": compliance_info["regional_compliance"],
            "user_acknowledgment_required": compliance_info["user_acknowledgment_required"],
            "content_rating_check": content_compliance_check,
            "age_verification_required": preferences.user_age is None or preferences.user_age < compliance_info["regional_compliance"]["adult_age_threshold"],
            "language_detection": {
                "detected_language": language_detection['detected_language'],
                "county": language_detection['county'],
                "confidence": language_detection['confidence']
            },
            "content_warning": "This platform may contain mature content. User discretion advised."
        }
        
        # Add content data
        if weather_data:
            response["weather"] = {
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "description": weather_data.description
            }
        
        response["news"] = {
            "articles": [
                {
                    "title": article.title,
                    "description": article.description,
                    "source": article.source,
                    "category": article.category
                } for article in all_news
            ],
            "total_count": len(all_news)
        }
        
        response["music"] = {
            "tracks": [
                {
                    "name": track.name,
                    "artists": track.artists,
                    "popularity": track.popularity
                } for track in trending_tracks + kenyan_tracks
            ]
        }

        # Add radio streams data - CRITICAL for frontend radio functionality
        response["radio_streams"] = {
            "main_station": {
                "name": "Kagema FM",
                "streamUrl": "http://ice1.somafm.com/groovesalad-256-mp3",
                "description": "Your premier radio station with live streaming",
                "frequency": "101.5 FM"
            },
            "regional_stations": language_detection.get('radio_streams', []),
            "alternative_streams": [
                {
                    "name": "SomaFM Groove Salad",
                    "streamUrl": "http://ice1.somafm.com/groovesalad-256-mp3",
                    "description": "Ambient and downtempo music",
                    "frequency": "Online"
                },
                {
                    "name": "SomaFM Lush",
                    "streamUrl": "http://ice1.somafm.com/lush-256-mp3",
                    "description": "Sensual and mellow electronica",
                    "frequency": "Online"
                }
            ]
        }
        
        return response
        
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
    logger.info("Starting Kagema FM Satellite & Offline Radio API v5.0.0 with Content Compliance")
    satellite_manager.enable_offline_mode()
    asyncio.create_task(periodic_cache_cleanup())

async def periodic_cache_cleanup():
    """Periodic cleanup of expired cache content"""
    while True:
        try:
            await offline_manager.cleanup_expired_content()
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            await asyncio.sleep(3600)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)