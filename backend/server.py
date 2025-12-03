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
from favorites_manager import get_favorites_manager
from favorites_sharing import get_sharing_manager
from intelligent_search_engine import IntelligentSearchEngine
from traffic_integration import get_traffic_manager
from satellite_radio_research import router as satellite_router
from routing_directions import get_routing_manager
from station_geocoding_service import get_geocoding_service

# Import Dragon KARAU AI systems
from dragon_ai_search_api import router as dragon_search_router
from radio_intelligence_api import router as radio_intelligence_router
from dragon_ai_api import router as dragon_ai_router
from dragon_crawler_api import router as dragon_crawler_router
from orchestral_automation_api import router as orchestral_router

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

# ===================================
# Stations API
# ===================================

@api_router.get("/stations")
async def get_stations(
    country: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get radio stations with optional country filter"""
    try:
        filters = {}
        
        if country:
            filters['country'] = country.upper()
        
        # Query stations sorted by quality
        cursor = db.radio_stations.find(filters).sort('quality_score', -1).skip(skip).limit(limit)
        
        stations = []
        async for station in cursor:
            stations.append({
                'id': station.get('id', str(station['_id'])),
                'name': station.get('name', 'Unknown'),
                'call_sign': station.get('call_sign'),
                'standard_display_name': station.get('standard_display_name'),
                'stream_url': station.get('stream_url', ''),
                'country': station.get('country', 'UNKNOWN'),
                'quality_score': station.get('quality_score', 50),
                'division_level1': station.get('division_level1_name'),
                'division_level2': station.get('division_level2_name'),
            })
        
        return {
            "status": "success",
            "data": {
                "stations": stations,
                "total": len(stations)
            }
        }
    except Exception as e:
        logger.error(f"Get stations error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"stations": [], "total": 0}
        }


@api_router.get("/stations/search")
async def search_stations(
    q: str,
    limit: int = 50
):
    """Search stations by name or call sign"""
    try:
        # Search by name or call sign
        filters = {
            '$or': [
                {'name': {'$regex': q, '$options': 'i'}},
                {'call_sign': {'$regex': q, '$options': 'i'}},
                {'standard_display_name': {'$regex': q, '$options': 'i'}}
            ]
        }
        
        cursor = db.radio_stations.find(filters).sort('quality_score', -1).limit(limit)
        
        stations = []
        async for station in cursor:
            stations.append({
                'id': station.get('id', str(station['_id'])),
                'name': station.get('name', 'Unknown'),
                'call_sign': station.get('call_sign'),
                'standard_display_name': station.get('standard_display_name'),
                'stream_url': station.get('stream_url', ''),
                'country': station.get('country', 'UNKNOWN'),
                'quality_score': station.get('quality_score', 50),
            })
        
        return {
            "status": "success",
            "data": {
                "stations": stations,
                "total": len(stations)
            }
        }
    except Exception as e:
        logger.error(f"Search stations error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"stations": [], "total": 0}
        }

# ===================================
# Favorites API
# ===================================

@api_router.post("/favorites/add")
async def add_favorite_station(user_id: str, station_id: str):
    """Add a station to user's favorites"""
    try:
        favorites_mgr = get_favorites_manager()
        result = await favorites_mgr.add_favorite(user_id, station_id)
        
        if result['success']:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "error",
                "error": result.get('error', 'Failed to add favorite')
            }
    except Exception as e:
        logger.error(f"Add favorite error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.delete("/favorites/remove")
async def remove_favorite_station(user_id: str, station_id: str):
    """Remove a station from user's favorites"""
    try:
        favorites_mgr = get_favorites_manager()
        result = await favorites_mgr.remove_favorite(user_id, station_id)
        
        if result['success']:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "error",
                "error": result.get('error', 'Failed to remove favorite')
            }
    except Exception as e:
        logger.error(f"Remove favorite error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/favorites/{user_id}")
async def get_user_favorites(user_id: str, limit: int = 100):
    """Get all favorite stations for a user"""
    try:
        favorites_mgr = get_favorites_manager()
        result = await favorites_mgr.get_user_favorites(user_id, limit)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {
                "favorites": [],
                "total_count": 0
            }
        }


@api_router.get("/favorites/{user_id}/check/{station_id}")
async def check_favorite_status(user_id: str, station_id: str):
    """Check if a station is in user's favorites"""
    try:
        favorites_mgr = get_favorites_manager()
        is_favorite = await favorites_mgr.is_favorited(user_id, station_id)
        
        return {
            "status": "success",
            "data": {
                "is_favorite": is_favorite,
                "user_id": user_id,
                "station_id": station_id
            }
        }
    except Exception as e:
        logger.error(f"Check favorite error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.post("/favorites/play-stats")
async def update_play_statistics(user_id: str, station_id: str):
    """Update play count for a favorite station"""
    try:
        favorites_mgr = get_favorites_manager()
        result = await favorites_mgr.update_play_stats(user_id, station_id)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Update play stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/favorites/{user_id}/stats")
async def get_favorites_statistics(user_id: str):
    """Get statistics about user's favorites"""
    try:
        favorites_mgr = get_favorites_manager()
        result = await favorites_mgr.get_stats(user_id)
        
        return {
            "status": "success",
            "data": result.get('stats', {})
        }
    except Exception as e:
        logger.error(f"Get favorite stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Favorites Import/Export & Sharing API
# ===================================

@api_router.get("/favorites/{user_id}/export")
async def export_favorites(user_id: str, format: str = 'json'):
    """Export user's favorites to JSON or M3U format"""
    try:
        sharing_mgr = get_sharing_manager()
        result = await sharing_mgr.export_favorites(user_id, format)
        
        return {
            "status": "success" if result['success'] else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Export favorites error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.post("/favorites/{user_id}/import")
async def import_favorites(user_id: str, import_data: dict):
    """Import favorites from JSON export"""
    try:
        sharing_mgr = get_sharing_manager()
        result = await sharing_mgr.import_favorites(user_id, import_data)
        
        return {
            "status": "success" if result['success'] else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Import favorites error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.post("/favorites/{user_id}/share")
async def create_shared_collection(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    station_ids: Optional[List[str]] = None
):
    """Create a shareable collection of favorites"""
    try:
        sharing_mgr = get_sharing_manager()
        result = await sharing_mgr.create_shared_collection(
            user_id, title, description, station_ids
        )
        
        return {
            "status": "success" if result['success'] else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Create shared collection error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/shared/{share_code}")
async def get_shared_collection(share_code: str):
    """Get details of a shared collection"""
    try:
        sharing_mgr = get_sharing_manager()
        result = await sharing_mgr.get_shared_collection(share_code)
        
        return {
            "status": "success" if result['success'] else "error",
            "data": result.get('collection', {}) if result['success'] else result
        }
    except Exception as e:
        logger.error(f"Get shared collection error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.post("/favorites/{user_id}/import-shared")
async def import_shared_collection(user_id: str, share_code: str):
    """Import stations from a shared collection"""
    try:
        sharing_mgr = get_sharing_manager()
        result = await sharing_mgr.import_shared_collection(user_id, share_code)
        
        return {
            "status": "success" if result['success'] else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Import shared collection error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Intelligent AI Search API
# ===================================

@api_router.get("/search/intelligent")
async def intelligent_ai_search(
    q: str,
    user_id: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 50
):
    """AI-powered intelligent search with natural language understanding"""
    try:
        search_engine = IntelligentSearchEngine()
        result = await search_engine.ai_search(
            query=q,
            limit=limit
        )
        
        return {
            "status": result.get('status', 'success'),
            "data": result
        }
    except Exception as e:
        logger.error(f"Intelligent search error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"results": []}
        }


@api_router.get("/search/recommendations/{user_id}")
async def get_personalized_recommendations(
    user_id: str,
    based_on: str = 'favorites',
    limit: int = 20
):
    """Get AI-powered personalized station recommendations"""
    try:
        from intelligent_search_engine import IntelligentSearchEngine
        search_engine = IntelligentSearchEngine()
        
        # For now, use the existing ai_search with user preferences
        # In future, can implement full recommendation system
        result = await search_engine.ai_search(
            query="top quality stations",
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "recommendations": result.get('results', []),
                "total": len(result.get('results', [])),
                "based_on": based_on
            }
        }
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"recommendations": []}
        }


@api_router.get("/search/trending")
async def get_trending_stations(
    timeframe: str = 'day',
    limit: int = 20
):
    """Get trending stations based on global popularity"""
    try:
        # Get top quality validated stations as trending
        cursor = db.radio_stations.find({
            'validated': True,
            'quality_score': {'$gte': 70}
        }).sort('quality_score', -1).limit(limit)
        
        stations = []
        async for station in cursor:
            stations.append({
                'id': station.get('id', str(station['_id'])),
                'name': station.get('name', 'Unknown'),
                'call_sign': station.get('call_sign'),
                'standard_display_name': station.get('standard_display_name'),
                'stream_url': station.get('stream_url', ''),
                'country': station.get('country', 'UNKNOWN'),
                'language': station.get('language', 'en'),
                'genre': station.get('genre', 'General'),
                'quality_score': station.get('quality_score', 50),
                'validated': station.get('validated', False)
            })
        
        return {
            "status": "success",
            "data": {
                "trending": stations,
                "total": len(stations),
                "timeframe": timeframe
            }
        }
    except Exception as e:
        logger.error(f"Trending stations error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"trending": []}
        }


@api_router.get("/search/similar/{station_id}")
async def get_similar_stations_endpoint(
    station_id: str,
    limit: int = 10
):
    """Find stations similar to a given station"""
    try:
        # Get reference station
        station = await db.radio_stations.find_one({'id': station_id})
        
        if not station:
            return {
                "status": "error",
                "error": "Station not found",
                "data": {"similar": []}
            }
        
        # Find similar stations
        query = {
            'id': {'$ne': station_id},
            '$or': [
                {'country': station.get('country')},
                {'language': station.get('language')},
                {'genre': {'$regex': station.get('genre', 'General'), '$options': 'i'}}
            ]
        }
        
        cursor = db.radio_stations.find(query).sort('quality_score', -1).limit(limit)
        
        similar = []
        async for sim_station in cursor:
            similar.append({
                'id': sim_station.get('id'),
                'name': sim_station.get('name'),
                'call_sign': sim_station.get('call_sign'),
                'standard_display_name': sim_station.get('standard_display_name'),
                'stream_url': sim_station.get('stream_url'),
                'country': sim_station.get('country'),
                'language': sim_station.get('language'),
                'genre': sim_station.get('genre'),
                'quality_score': sim_station.get('quality_score')
            })
        
        return {
            "status": "success",
            "data": {
                "reference_station": station.get('name'),
                "similar": similar,
                "total": len(similar)
            }
        }
    except Exception as e:
        logger.error(f"Similar stations error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"similar": []}
        }


@api_router.get("/search/filters/languages")
async def get_available_search_languages():
    """Get list of available languages for filtering"""
    try:
        languages = await db.radio_stations.distinct('language')
        return {
            "status": "success",
            "data": {
                "languages": sorted([l for l in languages if l]),
                "total": len(languages)
            }
        }
    except Exception as e:
        logger.error(f"Get languages error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/search/filters/genres")
async def get_available_search_genres():
    """Get list of available genres for filtering"""
    try:
        genres = await db.radio_stations.distinct('genre')
        return {
            "status": "success",
            "data": {
                "genres": sorted([g for g in genres if g]),
                "total": len(genres)
            }
        }
    except Exception as e:
        logger.error(f"Get genres error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/search/filters/countries")
async def get_available_search_countries():
    """Get list of available countries with station counts"""
    try:
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 100}
        ]
        countries = await db.radio_stations.aggregate(pipeline).to_list(length=100)
        
        return {
            "status": "success",
            "data": {
                "countries": [
                    {'code': c['_id'], 'count': c['count']}
                    for c in countries if c['_id']
                ],
                "total": len(countries)
            }
        }
    except Exception as e:
        logger.error(f"Get countries error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Map & Traffic Integration API
# ===================================

@api_router.get("/map/config")
async def get_map_configuration():
    """Get map configuration and available providers"""
    try:
        traffic_mgr = get_traffic_manager()
        config = await traffic_mgr.get_map_config()
        
        return {
            "status": "success",
            "data": config
        }
    except Exception as e:
        logger.error(f"Map config error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/map/stations")
async def get_stations_for_map(
    country: Optional[str] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    limit: int = 500
):
    """Get station locations for map display with optional bounding box"""
    try:
        query = {}
        
        # Filter by country if specified
        if country:
            query['country'] = country.upper()
        
        # Filter by bounding box if all coordinates provided
        if all([min_lat, max_lat, min_lon, max_lon]):
            query['$and'] = [
                {'latitude': {'$gte': min_lat, '$lte': max_lat}},
                {'longitude': {'$gte': min_lon, '$lte': max_lon}}
            ]
        
        # Get stations with location data
        cursor = db.radio_stations.find(query).limit(limit)
        
        stations = []
        async for station in cursor:
            # Only include stations with valid coordinates
            lat = station.get('latitude')
            lon = station.get('longitude')
            
            if lat and lon:
                stations.append({
                    'id': station.get('id', str(station['_id'])),
                    'name': station.get('name', 'Unknown'),
                    'call_sign': station.get('call_sign'),
                    'standard_display_name': station.get('standard_display_name'),
                    'stream_url': station.get('stream_url'),
                    'country': station.get('country', 'UNKNOWN'),
                    'latitude': lat,
                    'longitude': lon,
                    'quality_score': station.get('quality_score', 50),
                    'genre': station.get('genre', 'General')
                })
        
        return {
            "status": "success",
            "data": {
                "stations": stations,
                "total": len(stations)
            }
        }
    except Exception as e:
        logger.error(f"Get stations for map error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "data": {"stations": [], "total": 0}
        }


@api_router.get("/traffic/incidents")
async def get_traffic_incidents(
    lat: float,
    lon: float,
    radius: int = 10,
    provider: str = 'tomtom'
):
    """Get traffic incidents around a location"""
    try:
        traffic_mgr = get_traffic_manager()
        result = await traffic_mgr.get_traffic_incidents(lat, lon, radius, provider)
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Traffic incidents error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.get("/traffic/flow")
async def get_traffic_flow_config(
    lat: float,
    lon: float,
    zoom: int = 12,
    provider: str = 'tomtom'
):
    """Get traffic flow tile configuration for map overlay"""
    try:
        traffic_mgr = get_traffic_manager()
        result = await traffic_mgr.get_traffic_flow(lat, lon, zoom, provider)
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Traffic flow error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@api_router.post("/traffic/announcement")
async def generate_traffic_announcement(
    lat: float,
    lon: float,
    radius: int = 10,
    location_name: Optional[str] = None,
    provider: str = 'tomtom'
):
    """Generate radio-ready traffic announcement"""
    try:
        traffic_mgr = get_traffic_manager()
        
        # Get incidents
        incidents_result = await traffic_mgr.get_traffic_incidents(lat, lon, radius, provider)
        
        if not incidents_result.get('success'):
            return {
                "status": "error",
                "error": "Failed to fetch traffic incidents"
            }
        
        # Generate announcement
        incidents = incidents_result.get('incidents', [])
        announcement = await traffic_mgr.generate_traffic_announcement(incidents, location_name)
        
        return {
            "status": "success" if announcement.get('success') else "error",
            "data": announcement
        }
    except Exception as e:
        logger.error(f"Traffic announcement error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# =====================================================
# ROUTING & NAVIGATION ENDPOINTS (Phase 1)
# =====================================================

@app.post("/api/routing/calculate")
async def calculate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    mode: str = 'drive',
    provider: str = 'geoapify'
):
    """
    Calculate route between two points
    
    Args:
        start_lat, start_lon: Starting coordinates
        end_lat, end_lon: Ending coordinates  
        mode: 'drive', 'walk', 'bicycle', 'transit'
        provider: 'geoapify', 'tomtom'
    """
    try:
        routing_mgr = get_routing_manager()
        result = await routing_mgr.get_route(
            start_lat, start_lon, end_lat, end_lon, mode, provider
        )
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Calculate route error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/routing/geocode")
async def geocode_address_endpoint(
    address: str,
    provider: str = 'geoapify'
):
    """
    Convert address to coordinates
    """
    try:
        routing_mgr = get_routing_manager()
        result = await routing_mgr.geocode_address(address, provider)
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Geocode error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/routing/reverse-geocode")
async def reverse_geocode_endpoint(
    lat: float,
    lon: float,
    provider: str = 'geoapify'
):
    """
    Convert coordinates to address
    """
    try:
        routing_mgr = get_routing_manager()
        result = await routing_mgr.reverse_geocode(lat, lon, provider)
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Reverse geocode error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/routing/isochrone")
async def calculate_isochrone_endpoint(
    lat: float,
    lon: float,
    time_minutes: int = 15,
    mode: str = 'drive',
    provider: str = 'geoapify'
):
    """
    Calculate travel time area (isochrone)
    Shows area reachable within given time
    """
    try:
        routing_mgr = get_routing_manager()
        result = await routing_mgr.calculate_isochrone(
            lat, lon, time_minutes, mode, provider
        )
        
        return {
            "status": "success" if result.get('success') else "error",
            "data": result
        }
    except Exception as e:
        logger.error(f"Isochrone error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/routing/station-directions")
async def get_station_directions(
    user_lat: float,
    user_lon: float,
    station_id: str,
    mode: str = 'drive'
):
    """
    Get directions from user location to radio station
    """
    try:
        # Get station coordinates from database
        stations_collection = db['radio_stations']
        station = await stations_collection.find_one({"id": station_id})
        
        if not station:
            return {
                "status": "error",
                "error": "Station not found"
            }
        
        if not station.get('latitude') or not station.get('longitude'):
            return {
                "status": "error",
                "error": "Station location not available"
            }
        
        # Calculate route
        routing_mgr = get_routing_manager()
        route_result = await routing_mgr.get_route(
            user_lat, user_lon,
            station['latitude'], station['longitude'],
            mode, 'geoapify'
        )
        
        if route_result.get('success'):
            return {
                "status": "success",
                "data": {
                    "station": {
                        "id": station_id,
                        "name": station.get('name'),
                        "latitude": station.get('latitude'),
                        "longitude": station.get('longitude'),
                        "address": station.get('address', 'Address not available')
                    },
                    "route": route_result.get('route'),
                    "user_location": {
                        "latitude": user_lat,
                        "longitude": user_lon
                    }
                }
            }
        else:
            return {
                "status": "error",
                "error": route_result.get('error', 'Failed to calculate route')
            }
            
    except Exception as e:
        logger.error(f"Station directions error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Include all routers in the main app
app.include_router(api_router)
app.include_router(dragon_search_router)
app.include_router(radio_intelligence_router)
app.include_router(dragon_ai_router)
app.include_router(dragon_crawler_router)
app.include_router(orchestral_router)
app.include_router(satellite_router)

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

# ===================================
# Dragon AI Multi-Source Crawler API
# ===================================

@app.post("/api/crawler/start-multi-source")
async def start_multi_source_crawl(target_stations: int = 15000):
    """Start multi-source crawler to discover stations from all sources"""
    try:
        from multi_source_crawler_manager import get_multi_crawler
        
        multi_crawler = get_multi_crawler()
        await multi_crawler.initialize_crawlers()
        
        result = await multi_crawler.crawl_all_sources(target_stations)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Multi-source crawl error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/crawler/start/{source}")
async def start_specific_crawler(source: str):
    """Start a specific crawler source"""
    try:
        from multi_source_crawler_manager import get_multi_crawler
        
        multi_crawler = get_multi_crawler()
        await multi_crawler.initialize_crawlers()
        
        result = await multi_crawler.crawl_source(source)
        
        return {
            "status": "success",
            "source": source,
            "data": result
        }
    except Exception as e:
        logger.error(f"Crawler error for {source}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Administrative Divisions API
# ===================================

# IMPORTANT: Specific routes must come before parameterized routes in FastAPI

@app.get("/api/divisions/countries")
async def get_all_countries():
    """Get list of all countries with division data"""
    try:
        from administrative_divisions_manager import get_admin_divisions_manager
        
        admin_manager = get_admin_divisions_manager()
        
        # Get unique countries from database
        countries = await admin_manager.db.administrative_divisions.distinct('country_code')
        
        return {
            "status": "success",
            "data": {
                "countries": sorted(countries),
                "total": len(countries)
            }
        }
    except Exception as e:
        logger.error(f"Get countries error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/divisions/stats")
async def get_divisions_stats():
    """Get statistics about administrative divisions"""
    try:
        from administrative_divisions_manager import get_admin_divisions_manager
        
        admin_manager = get_admin_divisions_manager()
        stats = await admin_manager.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/divisions/populate")
async def populate_all_divisions():
    """Populate database with administrative divisions for all countries"""
    try:
        from administrative_divisions_manager import get_admin_divisions_manager
        
        admin_manager = get_admin_divisions_manager()
        
        # Start population in background (this takes time)
        result = await admin_manager.populate_all_divisions()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Population error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/divisions/assign-all")
async def assign_divisions_to_all_stations():
    """Automatically assign administrative divisions to all stations"""
    try:
        from division_geocoder import get_division_geocoder
        
        geocoder = get_division_geocoder()
        result = await geocoder.process_all_stations()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Division assignment error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/divisions/geocoder-stats")
async def get_geocoder_stats():
    """Get statistics about division assignments"""
    try:
        from division_geocoder import get_division_geocoder
        
        geocoder = get_division_geocoder()
        stats = await geocoder.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Geocoder stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/divisions/{country_code}/hierarchy")
async def get_country_hierarchy(country_code: str):
    """Get complete hierarchical structure for a country"""
    try:
        from administrative_divisions_manager import get_admin_divisions_manager
        
        admin_manager = get_admin_divisions_manager()
        hierarchy = await admin_manager.get_division_hierarchy(country_code.upper())
        
        return {
            "status": "success",
            "data": hierarchy
        }
    except Exception as e:
        logger.error(f"Get hierarchy error for {country_code}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/divisions/{country_code}")
async def get_country_divisions(country_code: str, level: Optional[int] = None):
    """Get administrative divisions for a specific country"""
    try:
        from administrative_divisions_manager import get_admin_divisions_manager
        
        admin_manager = get_admin_divisions_manager()
        divisions = await admin_manager.get_divisions_by_country(country_code.upper(), level)
        
        return {
            "status": "success",
            "data": {
                "country_code": country_code.upper(),
                "divisions": divisions,
                "total": len(divisions)
            }
        }
    except Exception as e:
        logger.error(f"Get divisions error for {country_code}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/stations/by-division/{division_id}")
async def get_stations_by_division(division_id: str):
    """Get radio stations filtered by administrative division"""
    try:
        # Query stations by division
        stations = await db.radio_stations.find({
            '$or': [
                {'division_level1_id': division_id},
                {'division_level2_id': division_id}
            ]
        }).to_list(length=500)
        
        return {
            "status": "success",
            "data": {
                "division_id": division_id,
                "stations": [{
                    "id": str(s.get('id', s.get('_id'))),
                    "name": s.get('name'),
                    "stream_url": s.get('stream_url'),
                    "country": s.get('country'),
                    "division_level1": s.get('division_level1_name'),
                    "division_level2": s.get('division_level2_name'),
                    "quality_score": s.get('quality_score', 0)
                } for s in stations],
                "total": len(stations)
            }
        }
    except Exception as e:
        logger.error(f"Get stations by division error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Call Sign Standardization API
# ===================================

@app.post("/api/call-signs/standardize-all")
async def standardize_all_call_signs():
    """Standardize call signs for all radio stations"""
    try:
        from call_sign_standardizer import get_call_sign_standardizer
        
        standardizer = get_call_sign_standardizer()
        result = await standardizer.standardize_all_stations()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Call sign standardization error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/call-signs/stats")
async def get_call_sign_stats():
    """Get call sign standardization statistics"""
    try:
        from call_sign_standardizer import get_call_sign_standardizer
        
        standardizer = get_call_sign_standardizer()
        stats = await standardizer.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Call sign stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/call-signs/by-country/{country_code}")
async def get_call_signs_by_country(country_code: str):
    """Get call sign breakdown for a specific country"""
    try:
        from call_sign_standardizer import get_call_sign_standardizer
        
        standardizer = get_call_sign_standardizer()
        result = await standardizer.get_call_sign_by_country(country_code.upper())
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Call sign by country error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Non-Standard Station Formatting API
# ===================================

@app.post("/api/stations/format-non-standard")
async def format_non_standard_stations():
    """Format all stations without call signs using frequency/numeric/name standards"""
    try:
        from non_standard_station_formatter import get_non_standard_formatter
        
        formatter = get_non_standard_formatter()
        result = await formatter.format_all_non_standard_stations()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Non-standard formatting error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/stations/formatting-stats")
async def get_formatting_stats():
    """Get statistics about station formatting"""
    try:
        from non_standard_station_formatter import get_non_standard_formatter
        
        formatter = get_non_standard_formatter()
        stats = await formatter.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Formatting stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/stations/examples/{format_type}")
async def get_format_examples(format_type: str, limit: int = 10):
    """Get example stations for a specific format type"""
    try:
        from non_standard_station_formatter import get_non_standard_formatter
        
        formatter = get_non_standard_formatter()
        examples = await formatter.get_examples_by_format(format_type, limit)
        
        return {
            "status": "success",
            "data": {
                "format_type": format_type,
                "examples": examples,
                "total": len(examples)
            }
        }
    except Exception as e:
        logger.error(f"Format examples error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/crawler/stats")
async def get_crawler_stats():
    """Get statistics for all crawler sources"""
    try:
        from multi_source_crawler_manager import get_multi_crawler
        
        multi_crawler = get_multi_crawler()
        stats = await multi_crawler.get_source_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/crawler/discover-sources")
async def discover_new_sources():
    """Discover potential new radio data sources"""
    try:
        from multi_source_crawler_manager import get_multi_crawler
        
        multi_crawler = get_multi_crawler()
        sources = await multi_crawler.discover_new_sources()
        
        return {
            "status": "success",
            "data": sources
        }
    except Exception as e:
        logger.error(f"Source discovery error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ===================================
# Automated Testing & Scheduler API
# ===================================

@app.post("/api/automation/test-all")
async def run_automated_tests():
    """Run full automated test suite"""
    try:
        from automated_testing_orchestrator import get_testing_orchestrator
        
        orchestrator = get_testing_orchestrator()
        result = await orchestrator.run_full_test_suite()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Automated testing error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/automation/restart-services")
async def restart_all_services():
    """Restart all system services"""
    try:
        from automated_testing_orchestrator import get_testing_orchestrator
        
        orchestrator = get_testing_orchestrator()
        result = await orchestrator.restart_all_services()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Service restart error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/automation/health")
async def get_system_health():
    """Get overall system health"""
    try:
        from automated_testing_orchestrator import get_testing_orchestrator
        
        orchestrator = get_testing_orchestrator()
        health = await orchestrator.get_system_health()
        
        return {
            "status": "success",
            "data": health
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/automation/scheduler/start")
async def start_scheduler():
    """Start the 6-hour automated scheduler"""
    try:
        from automated_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        asyncio.create_task(scheduler.start())
        
        return {
            "status": "success",
            "message": "Scheduler started (runs every 6 hours)"
        }
    except Exception as e:
        logger.error(f"Scheduler start error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/automation/scheduler/stop")
async def stop_scheduler():
    """Stop the automated scheduler"""
    try:
        from automated_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        await scheduler.stop()
        
        return {
            "status": "success",
            "message": "Scheduler stopped"
        }
    except Exception as e:
        logger.error(f"Scheduler stop error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/automation/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    try:
        from automated_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        status = await scheduler.get_status()
        
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Scheduler status error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/api/automation/maintenance-cycle")
async def run_maintenance_cycle():
    """Manually trigger a maintenance cycle"""
    try:
        from automated_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        result = await scheduler.run_maintenance_cycle()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Maintenance cycle error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/api/automation/maintenance-history")
async def get_maintenance_history(limit: int = 10):
    """Get recent maintenance cycles"""
    try:
        from automated_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        cycles = await scheduler.get_recent_cycles(limit)
        
        return {
            "status": "success",
            "data": {
                "cycles": cycles,
                "total": len(cycles)
            }
        }
    except Exception as e:
        logger.error(f"Maintenance history error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Kagema FM Dragon KARAU AI Radio API v5.0.0")
    satellite_manager.enable_offline_mode()
    asyncio.create_task(periodic_cache_cleanup())
    
    # NOTE: Scheduler auto-start disabled - use API to start manually
    # POST /api/automation/scheduler/start to enable 6-hour maintenance
    logger.info("💡 Automated scheduler available - start via API: POST /api/automation/scheduler/start")

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