from fastapi import FastAPI, APIRouter, HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
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
from user_preferences import UserPreferencesManager, UserPreferences as UserPreferencesModel, FavoriteItem, ListeningHistory
from voice_ai_service import voice_ai_service, VoiceInterpretationRequest, VoiceInterpretationResponse
from spotify_service import spotify_service
from googlemaps_service import googlemaps_service
from accuradio_service import accuradio_service
from radio_browser_service import radio_browser_service
from hybrid_geolocation_service import hybrid_geolocation_service

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
user_preferences_manager = UserPreferencesManager(db)

# Enhanced Models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

# Combined request model for personalized content
class PersonalizedContentRequest(BaseModel):
    location: LocationRequest
    preferences: Optional[Dict[str, Any]] = None
    
# UserPreferences model is imported from user_preferences.py

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

@api_router.get("/app/info")
async def get_app_info():
    """Get application information"""
    return {
        "name": "Kagema FM Enhanced",
        "version": "5.0.0",
        "status": "active",
        "features": ["radio", "offline", "multilingual", "enhanced_ui", "real_time"]
    }

@api_router.get("/app/version")
async def get_app_version():
    """Get current app version for update checks"""
    return {
        "version": "5.0.0",
        "build": "2024010201",
        "release_date": "2024-01-02T00:00:00Z",
        "update_available": False,
        "minimum_version": "4.0.0",
        "external_sources": {
            "soma_fm": "https://somafm.com/channels.json",
            "bbc_world": "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
            "radio_garden": "https://radio.garden/api",
            "accuradio": "https://www.accuradio.com/channels",
            "radio_browser": "https://www.radio-browser.info/webservice",
            "last_updated": "2024-01-02T00:00:00Z"
        }
    }

@api_router.get("/station-info")
async def get_basic_station_info():
    """Get basic Kagema FM station information with stream URL"""
    return {
        "name": "Kagema FM",
        "description": "Your premier radio station with live streaming",
        "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
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
                "radio_streams": ["https://ice1.somafm.com/groovesalad-256-mp3"],
                "language_info": {
                    "code": "en",
                    "name": "English",
                    "native_name": "English"
                },
                "regional_stations": ["https://ice1.somafm.com/groovesalad-256-mp3"]
            }
            
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language from coordinates")

@api_router.post("/integrations/initialize")
async def initialize_integrations(request: dict):
    """Initialize platform integrations (Google Maps, Spotify, Voice Control, etc.)"""
    try:
        integration_type = request.get("type", "general")
        # config = request.get("config", {})  # Currently unused
        
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
        # regional_stations = language_service.get_regional_radio_stations(detected_lang)  # Currently unused
        
        # Select appropriate stream URL based on language
        primary_stream = language_detection['radio_streams'][0] if language_detection['radio_streams'] else 'https://ice1.somafm.com/groovesalad-256-mp3'
        
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
            streamUrl="https://ice1.somafm.com/groovesalad-256-mp3",
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
    request: PersonalizedContentRequest
):
    """Get personalized content with automatic language detection, compliance, and offline fallback"""
    try:
        location = request.location
        
        # Create default preferences if not provided
        preferences_dict = request.preferences or {}
        offline_mode = preferences_dict.get('offline_mode', False)
        preferred_language = preferences_dict.get('preferred_language', 'en')
        
        # Determine country for compliance
        if -35 <= location.latitude <= 5 and -75 <= location.longitude <= -30:
            country_code = "BR"
        elif -5 <= location.latitude <= 5 and 33 <= location.longitude <= 42:
            country_code = "KE"
        else:
            country_code = "GLOBAL"
        
        # Check if offline mode is requested
        if offline_mode:
            cached_content = await offline_manager.get_offline_radio_streams()
            cached_news = await offline_manager.get_offline_news()
            cached_music = await offline_manager.get_offline_music()
            
            # Get compliance info even for offline content
            compliance_info = compliance_manager.generate_content_warning_response(
                country_code,
                preferred_language,
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
        user_age = preferences_dict.get('user_age', None)
        if user_age:
            content_compliance_check = compliance_manager.check_content_rating_compliance(
                ContentRating.MATURE,  # Default rating for radio content
                user_age,
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
            "age_verification_required": user_age is None or user_age < compliance_info["regional_compliance"]["adult_age_threshold"],
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
                "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                "description": "Your premier radio station with live streaming",
                "frequency": "101.5 FM"
            },
            "regional_stations": language_detection.get('radio_streams', []),
            "alternative_streams": [
                {
                    "name": "SomaFM Groove Salad",
                    "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "description": "Ambient and downtempo music",
                    "frequency": "Online"
                },
                {
                    "name": "Radio Paradise AAC",
                    "streamUrl": "https://stream.radioparadise.com/aac-320",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online"
                },
                {
                    "name": "Radio Paradise MP3",
                    "streamUrl": "https://stream.radioparadise.com/mp3-192",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online"
                },
                {
                    "name": "FIP Radio France AAC",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-hifi.aac",
                    "description": "French eclectic and world music",
                    "frequency": "Online"
                },
                {
                    "name": "FIP Radio France MP3",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-midfi.mp3",
                    "description": "French eclectic and world music",
                    "frequency": "Online"
                },
                {
                    "name": "SomaFM Drone Zone",
                    "streamUrl": "http://ice1.somafm.com/dronezone-256-mp3",
                    "description": "Ambient space music",
                    "frequency": "Online"
                },
                {
                    "name": "SomaFM DEF CON Radio",
                    "streamUrl": "http://ice1.somafm.com/defcon-256-mp3",
                    "description": "Hacker culture and electronic music",
                    "frequency": "Online"
                }
            ]
        }
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting multilingual personalized content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personalized content")

# Dedicated Radio API Endpoints
@api_router.get("/radio/streams")
async def get_radio_streams():
    """Get all available radio streams"""
    try:
        return {
            "main_station": {
                "name": "Kagema FM",
                "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                "description": "Your premier radio station with live streaming",
                "frequency": "101.5 FM"
            },
            "alternative_streams": [
                {
                    "name": "SomaFM Groove Salad",
                    "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "description": "Ambient and downtempo music",
                    "frequency": "Online"
                },
                {
                    "name": "Radio Paradise AAC",
                    "streamUrl": "https://stream.radioparadise.com/aac-320",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online"
                },
                {
                    "name": "Radio Paradise MP3",
                    "streamUrl": "https://stream.radioparadise.com/mp3-192",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online"
                },
                {
                    "name": "FIP Radio France AAC",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-hifi.aac",
                    "description": "French eclectic and world music",
                    "frequency": "Online"
                },
                {
                    "name": "FIP Radio France MP3",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-midfi.mp3",
                    "description": "French eclectic and world music",
                    "frequency": "Online"
                },
                {
                    "name": "SomaFM Drone Zone",
                    "streamUrl": "http://ice1.somafm.com/dronezone-256-mp3",
                    "description": "Ambient space music",
                    "frequency": "Online"
                },
                {
                    "name": "SomaFM DEF CON Radio",
                    "streamUrl": "http://ice1.somafm.com/defcon-256-mp3",
                    "description": "Hacker culture and electronic music",
                    "frequency": "Online"
                }
            ]
        }
    except Exception as e:
        logging.error(f"Error getting radio streams: {e}")
        raise HTTPException(status_code=500, detail="Failed to get radio streams")

@api_router.get("/radio/stations")
async def get_radio_stations():
    """Get all available radio stations"""
    try:
        return {
            "stations": [
                {
                    "id": "kagema-fm",
                    "name": "Kagema FM",
                    "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "description": "Your premier radio station with live streaming",
                    "frequency": "101.5 FM",
                    "genre": "Mixed",
                    "location": "Global"
                },
                {
                    "id": "soma-groove",
                    "name": "SomaFM Groove Salad",
                    "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "description": "Ambient and downtempo music",
                    "frequency": "Online",
                    "genre": "Ambient",
                    "location": "San Francisco, CA"
                },
                {
                    "id": "radio-paradise-aac",
                    "name": "Radio Paradise AAC",
                    "streamUrl": "https://stream.radioparadise.com/aac-320",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online",
                    "genre": "Rock",
                    "location": "Paradise, CA"
                },
                {
                    "id": "radio-paradise-mp3",
                    "name": "Radio Paradise MP3",
                    "streamUrl": "https://stream.radioparadise.com/mp3-192",
                    "description": "Eclectic rock and alternative music",
                    "frequency": "Online",
                    "genre": "Rock",
                    "location": "Paradise, CA"
                },
                {
                    "id": "fip-aac",
                    "name": "FIP Radio France AAC",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-hifi.aac",
                    "description": "French eclectic and world music",
                    "frequency": "Online",
                    "genre": "World",
                    "location": "France"
                },
                {
                    "id": "fip-mp3",
                    "name": "FIP Radio France MP3",
                    "streamUrl": "https://icecast.radiofrance.fr/fip-midfi.mp3",
                    "description": "French eclectic and world music",
                    "frequency": "Online",
                    "genre": "World",
                    "location": "France"
                },
                {
                    "id": "soma-drone",
                    "name": "SomaFM Drone Zone",
                    "streamUrl": "http://ice1.somafm.com/dronezone-256-mp3",
                    "description": "Ambient space music",
                    "frequency": "Online",
                    "genre": "Ambient",
                    "location": "San Francisco, CA"
                },
                {
                    "id": "soma-defcon",
                    "name": "SomaFM DEF CON Radio",
                    "streamUrl": "http://ice1.somafm.com/defcon-256-mp3",
                    "description": "Hacker culture and electronic music",
                    "frequency": "Online",
                    "genre": "Electronic",
                    "location": "San Francisco, CA"
                }
            ]
        }
    except Exception as e:
        logging.error(f"Error getting radio stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get radio stations")

# AccuRadio API Endpoints
@api_router.get("/accuradio/channels")
async def get_accuradio_channels(genre: Optional[str] = None, featured: Optional[bool] = None):
    """Get AccuRadio channels, optionally filtered by genre or featured status"""
    try:
        if featured:
            channels = await accuradio_service.get_featured_channels()
        elif genre:
            channels = await accuradio_service.get_channels_by_genre(genre)
        else:
            channels = await accuradio_service.get_all_channels()
        
        return {
            "status": "success",
            "channels": channels,
            "count": len(channels)
        }
    except Exception as e:
        logging.error(f"Error getting AccuRadio channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AccuRadio channels")

@api_router.get("/accuradio/search")
async def search_accuradio_channels(q: str):
    """Search AccuRadio channels by name, genre, or description"""
    try:
        channels = await accuradio_service.search_channels(q)
        return {
            "status": "success",
            "query": q,
            "channels": channels,
            "count": len(channels)
        }
    except Exception as e:
        logging.error(f"Error searching AccuRadio channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to search AccuRadio channels")

@api_router.get("/accuradio/genres")
async def get_accuradio_genres():
    """Get all available AccuRadio genres"""
    try:
        genres = await accuradio_service.get_genres()
        return {
            "status": "success",
            "genres": genres,
            "count": len(genres)
        }
    except Exception as e:
        logging.error(f"Error getting AccuRadio genres: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AccuRadio genres")

@api_router.get("/accuradio/channel/{channel_id}")
async def get_accuradio_channel(channel_id: str):
    """Get specific AccuRadio channel by ID"""
    try:
        channel = await accuradio_service.get_channel_by_id(channel_id)
        if channel:
            return {
                "status": "success",
                "channel": channel
            }
        else:
            raise HTTPException(status_code=404, detail="AccuRadio channel not found")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting AccuRadio channel: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AccuRadio channel")

@api_router.get("/accuradio/info")
async def get_accuradio_info():
    """Get AccuRadio service information and statistics"""
    try:
        info = await accuradio_service.get_service_info()
        return {
            "status": "success",
            "info": info
        }
    except Exception as e:
        logging.error(f"Error getting AccuRadio service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AccuRadio service info")

# Radio Browser API Endpoints
@api_router.get("/radio-browser/search")
async def search_radio_browser_stations(q: str, limit: int = 50):
    """Search Radio Browser stations by name"""
    try:
        stations = await radio_browser_service.search_stations(q, limit)
        return {
            "status": "success",
            "query": q,
            "stations": stations,
            "count": len(stations),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error searching Radio Browser stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to search Radio Browser stations")

@api_router.get("/radio-browser/country/{country}")
async def get_radio_browser_stations_by_country(country: str, limit: int = 50):
    """Get Radio Browser stations by country"""
    try:
        stations = await radio_browser_service.get_stations_by_country(country, limit)
        return {
            "status": "success",
            "country": country,
            "stations": stations,
            "count": len(stations),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser stations by country: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser stations by country")

@api_router.get("/radio-browser/language/{language}")
async def get_radio_browser_stations_by_language(language: str, limit: int = 50):
    """Get Radio Browser stations by language"""
    try:
        stations = await radio_browser_service.get_stations_by_language(language, limit)
        return {
            "status": "success",
            "language": language,
            "stations": stations,
            "count": len(stations),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser stations by language: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser stations by language")

@api_router.get("/radio-browser/tag/{tag}")
async def get_radio_browser_stations_by_tag(tag: str, limit: int = 50):
    """Get Radio Browser stations by tag/genre"""
    try:
        stations = await radio_browser_service.get_stations_by_tag(tag, limit)
        return {
            "status": "success",
            "tag": tag,
            "stations": stations,
            "count": len(stations),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser stations by tag: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser stations by tag")

@api_router.get("/radio-browser/popular")
async def get_popular_radio_browser_stations(limit: int = 100):
    """Get most popular Radio Browser stations worldwide"""
    try:
        stations = await radio_browser_service.get_popular_stations(limit)
        return {
            "status": "success",
            "stations": stations,
            "count": len(stations),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting popular Radio Browser stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular Radio Browser stations")

@api_router.get("/radio-browser/tags")
async def get_radio_browser_tags(limit: int = 50):
    """Get top tags/genres from Radio Browser"""
    try:
        tags = await radio_browser_service.get_top_tags(limit)
        return {
            "status": "success",
            "tags": tags,
            "count": len(tags),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser tags")

@api_router.get("/radio-browser/countries")
async def get_radio_browser_countries(limit: int = 50):
    """Get countries with radio stations"""
    try:
        countries = await radio_browser_service.get_countries(limit)
        return {
            "status": "success",
            "countries": countries,
            "count": len(countries),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser countries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser countries")

@api_router.get("/radio-browser/languages")
async def get_radio_browser_languages(limit: int = 50):
    """Get languages available in Radio Browser"""
    try:
        languages = await radio_browser_service.get_languages(limit)
        return {
            "status": "success",
            "languages": languages,
            "count": len(languages),
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser languages")

@api_router.get("/radio-browser/station/{uuid}")
async def get_radio_browser_station_by_uuid(uuid: str):
    """Get specific Radio Browser station by UUID"""
    try:
        station = await radio_browser_service.get_station_by_uuid(uuid)
        if station:
            return {
                "status": "success",
                "station": station,
                "source": "Radio Browser"
            }
        else:
            raise HTTPException(status_code=404, detail="Radio Browser station not found")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting Radio Browser station by UUID: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser station")

@api_router.get("/radio-browser/info")
async def get_radio_browser_info():
    """Get Radio Browser service information"""
    try:
        info = await radio_browser_service.get_service_info()
        return {
            "status": "success",
            "info": info,
            "source": "Radio Browser"
        }
    except Exception as e:
        logging.error(f"Error getting Radio Browser service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Radio Browser service info")

# Hybrid Geolocation API Endpoints  
@api_router.get("/geolocation/ip")
async def get_ip_location(request: Request):
    """Get location based on client IP address (immediate, no permission required)"""
    try:
        client_ip = await hybrid_geolocation_service.get_client_ip(request)
        ip_location = await hybrid_geolocation_service.get_ip_geolocation(client_ip)
        
        return {
            "status": "success", 
            "location": ip_location,
            "client_ip": client_ip,
            "source": "ip_geolocation"
        }
    except Exception as e:
        logging.error(f"Error getting IP location: {e}")
        raise HTTPException(status_code=500, detail="Failed to get IP-based location")

@api_router.post("/geolocation/hybrid")
async def get_hybrid_location(request: Request, gps_data: Optional[dict] = None):
    """Get location using hybrid approach (IP + GPS)"""
    try:
        # Get request body if provided
        if not gps_data:
            try:
                body = await request.json()
                gps_data = body.get('gps_data')
            except:
                gps_data = None
        
        hybrid_location = await hybrid_geolocation_service.get_hybrid_location(request, gps_data)
        suggestions = await hybrid_geolocation_service.get_location_suggestions(hybrid_location, 'radio')
        
        return {
            "status": "success",
            "location": hybrid_location,
            "suggestions": suggestions,
            "source": "hybrid_geolocation"
        }
    except Exception as e:
        logging.error(f"Error getting hybrid location: {e}")
        raise HTTPException(status_code=500, detail="Failed to get hybrid location")

@api_router.get("/geolocation/suggestions")
async def get_location_suggestions(request: Request, context: str = "radio"):
    """Get location-based suggestions for radio stations, services, etc."""
    try:
        # Get IP-based location first
        client_ip = await hybrid_geolocation_service.get_client_ip(request)
        ip_location = await hybrid_geolocation_service.get_ip_geolocation(client_ip)
        
        # Get suggestions based on location
        suggestions = await hybrid_geolocation_service.get_location_suggestions(ip_location, context)
        
        return {
            "status": "success",
            "location": {
                "country": ip_location.get('country'),
                "city": ip_location.get('city'),
                "accuracy": ip_location.get('accuracy')
            },
            "suggestions": suggestions,
            "source": "location_suggestions"
        }
    except Exception as e:
        logging.error(f"Error getting location suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get location suggestions")

@api_router.get("/geolocation/info")
async def get_geolocation_service_info():
    """Get hybrid geolocation service information"""
    try:
        info = await hybrid_geolocation_service.get_service_info()
        return {
            "status": "success",
            "info": info,
            "source": "hybrid_geolocation"
        }
    except Exception as e:
        logging.error(f"Error getting geolocation service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get geolocation service info")

@api_router.get("/satellite/main_stations")
async def get_satellite_main_stations():
    """Get main satellite radio stations"""
    try:
        # Get satellite connection status
        connection_status = await satellite_manager.detect_connection_type()
        
        return {
            "satellite_status": {
                "connection_type": connection_status.connection_type.value,
                "signal_strength": connection_status.signal_strength.value,
                "provider": connection_status.provider,
                "satellite_name": connection_status.satellite_name
            },
            "main_stations": [
                {
                    "id": "satellite-main",
                    "name": "Kagema FM Satellite",
                    "description": "Main satellite radio stream",
                    "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "frequency": "Satellite Band 1",
                    "signal_strength": connection_status.signal_strength.value,
                    "location": "Global Coverage"
                },
                {
                    "id": "satellite-backup",
                    "name": "Kagema FM Backup",
                    "description": "Backup satellite radio stream",
                    "streamUrl": "https://stream.radioparadise.com/aac-320",
                    "frequency": "Satellite Band 2", 
                    "signal_strength": connection_status.signal_strength.value,
                    "location": "Global Coverage"
                }
            ]
        }
    except Exception as e:
        logging.error(f"Error getting satellite main stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get satellite main stations")

# User Preferences and Enhanced Features API Endpoints

@api_router.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    try:
        preferences = await user_preferences_manager.get_user_preferences(user_id)
        return preferences.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")

@api_router.put("/user/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: UserPreferencesModel):
    """Update user preferences"""
    try:
        preferences.user_id = user_id  # Ensure user_id is set
        success = await user_preferences_manager.save_user_preferences(preferences)
        if success:
            return {"message": "Preferences updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@api_router.post("/user/{user_id}/favorites")
async def add_favorite(user_id: str, favorite: FavoriteItem):
    """Add item to user favorites"""
    try:
        favorite.user_id = user_id
        favorite_id = await user_preferences_manager.add_favorite(favorite)
        return {"message": "Added to favorites", "favorite_id": favorite_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add favorite: {str(e)}")

@api_router.get("/user/{user_id}/favorites")
async def get_user_favorites(user_id: str, favorite_type: Optional[str] = None):
    """Get user favorites"""
    try:
        favorites = await user_preferences_manager.get_user_favorites(user_id, favorite_type)
        return {"favorites": [fav.dict() for fav in favorites]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get favorites: {str(e)}")

@api_router.delete("/user/{user_id}/favorites/{favorite_id}")
async def remove_favorite(user_id: str, favorite_id: str):
    """Remove item from favorites"""
    try:
        success = await user_preferences_manager.remove_favorite(user_id, favorite_id)
        if success:
            return {"message": "Removed from favorites"}
        else:
            raise HTTPException(status_code=404, detail="Favorite not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove favorite: {str(e)}")

@api_router.post("/user/{user_id}/listening-session")
async def start_listening_session(user_id: str, session: ListeningHistory):
    """Start a new listening session"""
    try:
        session.user_id = user_id
        session_id = await user_preferences_manager.add_listening_session(session)
        return {"message": "Listening session started", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@api_router.put("/user/{user_id}/listening-session/{session_id}")
async def end_listening_session(
    user_id: str, 
    session_id: str, 
    ended_at: datetime, 
    duration_seconds: int
):
    """End a listening session"""
    try:
        success = await user_preferences_manager.update_listening_session(
            user_id, session_id, ended_at, duration_seconds
        )
        if success:
            return {"message": "Listening session ended"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@api_router.get("/user/{user_id}/listening-history")
async def get_listening_history(user_id: str, limit: int = 50):
    """Get user listening history"""
    try:
        history = await user_preferences_manager.get_listening_history(user_id, limit)
        return {"history": [session.dict() for session in history]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@api_router.get("/user/{user_id}/stats")
async def get_listening_stats(user_id: str):
    """Get user listening statistics"""
    try:
        stats = await user_preferences_manager.get_listening_stats(user_id)
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@api_router.get("/user/{user_id}/recommendations")
async def get_personalized_recommendations(user_id: str):
    """Get personalized recommendations for user"""
    try:
        recommendations = await user_preferences_manager.get_personalized_recommendations(user_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@api_router.get("/user/{user_id}/export")
async def export_user_data(user_id: str):
    """Export all user data"""
    try:
        data = await user_preferences_manager.export_user_data(user_id)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

@api_router.delete("/user/{user_id}/data")
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR compliance)"""
    try:
        success = await user_preferences_manager.delete_user_data(user_id)
        if success:
            return {"message": "User data deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")

# Enhanced Station Info with Personalization
@api_router.get("/station-info/enhanced/{user_id}")
async def get_enhanced_station_info(user_id: str):
    """Get enhanced station info with personalization"""
    try:
        # Get user preferences
        preferences = await user_preferences_manager.get_user_preferences(user_id)
        
        # Get listening history
        history = await user_preferences_manager.get_listening_history(user_id, limit=10)
        
        # Get recommendations
        recommendations = await user_preferences_manager.get_personalized_recommendations(user_id)
        
        # Base station info
        station_info = {
            "name": "Kagema FM Enhanced",
            "description": "Your Personalized International Radio Experience",
            "streamUrl": "https://ice1.somafm.com/groovesalad-256-mp3",
            "currentShow": "Live Radio - Personalized Mix",
            "frequency": "101.5 FM",
            "quality": preferences.audio.quality,
            "volume": preferences.audio.volume,
            "theme": preferences.theme,
            "personalization": {
                "enabled": True,
                "score": recommendations.get("personalization_score", 0.0),
                "recent_sessions": len(history),
                "recommendations": recommendations.get("recommended_stations", [])
            }
        }
        
        return station_info
        
    except Exception as e:
        logger.error(f"Error getting enhanced station info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enhanced station info")

# Voice AI endpoints
@api_router.post("/voice/interpret", response_model=VoiceInterpretationResponse)
async def interpret_voice_command(request: VoiceInterpretationRequest) -> VoiceInterpretationResponse:
    """
    Interpret voice command using AI and pattern matching
    """
    try:
        logger.info(f"Interpreting voice command: {request.text}")
        result = await voice_ai_service.interpret_voice_command(request)
        return result
    except Exception as e:
        logger.error(f"Voice interpretation error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice interpretation failed: {str(e)}")

@api_router.get("/voice/intents")
async def get_voice_intents():
    """
    Get available voice command intents and their descriptions
    """
    try:
        return voice_ai_service.get_available_intents()
    except Exception as e:
        logger.error(f"Error getting voice intents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice intents")

@api_router.get("/voice/help")
async def get_voice_help():
    """
    Get help information for voice commands
    """
    try:
        return {
            "commands": voice_ai_service.get_voice_commands_help(),
            "available_intents": list(voice_ai_service.get_available_intents().keys()),
            "usage_tips": [
                "Speak clearly and at normal speed",
                "Use simple, direct commands",
                "Try commands like 'play radio', 'pause', 'next station'",
                "For station changes, say 'play station [name]' or 'tune to [name]'",
                "For searches, say 'search for [artist or song]' or 'find [music type]'",
                "For external sources, say 'browse [source name]' or 'open [source]'"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting voice help: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice help")

# Spotify Integration Models
class SpotifySearchRequest(BaseModel):
    query: str
    limit: int = 20
    access_token: Optional[str] = None

class SpotifyPlaylistRequest(BaseModel):
    name: str
    description: str = ""
    public: bool = False
    access_token: str

class SpotifyAddTracksRequest(BaseModel):
    playlist_id: str
    track_uris: List[str]
    access_token: str

# Spotify API Endpoints
@api_router.get("/spotify/auth/login")
async def spotify_auth_login():
    """Get Spotify authorization URL"""
    try:
        auth_url = spotify_service.get_auth_url()
        return {"auth_url": auth_url, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify auth URL error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Spotify auth URL")

@api_router.post("/spotify/auth/callback")
async def spotify_auth_callback(code: str):
    """Handle Spotify OAuth callback"""
    try:
        token_info = spotify_service.get_access_token(code)
        return {
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "expires_in": token_info["expires_in"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Spotify auth callback error: {e}")
        raise HTTPException(status_code=401, detail="Failed to authenticate with Spotify")

@api_router.post("/spotify/auth/refresh")
async def spotify_refresh_token(refresh_token: str):
    """Refresh Spotify access token"""
    try:
        token_info = spotify_service.refresh_access_token(refresh_token)
        return {
            "access_token": token_info["access_token"],
            "expires_in": token_info["expires_in"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Spotify token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Failed to refresh Spotify token")

@api_router.post("/spotify/search")
async def spotify_search_tracks(request: SpotifySearchRequest):
    """Search for tracks on Spotify"""
    try:
        results = spotify_service.search_tracks(
            query=request.query,
            limit=request.limit,
            access_token=request.access_token
        )
        return {
            "tracks": results["tracks"],
            "total": results["total"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Spotify search error: {e}")
        # Return fallback data on error
        return {
            "tracks": [
                {
                    "id": "fallback_1",
                    "name": f"{request.query} - Demo Track",
                    "artist": "Demo Artist",
                    "album": "Demo Album",
                    "duration_ms": 180000,
                    "preview_url": None,
                    "external_urls": {"spotify": "#"},
                    "uri": "spotify:track:fallback",
                    "image": None
                }
            ],
            "total": 1,
            "status": "fallback"
        }

@api_router.get("/spotify/user/profile")
async def spotify_get_user_profile(access_token: str):
    """Get Spotify user profile"""
    try:
        profile = spotify_service.get_user_profile(access_token)
        return {"profile": profile, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify profile error: {e}")
        raise HTTPException(status_code=401, detail="Failed to get Spotify profile")

@api_router.get("/spotify/user/playlists")
async def spotify_get_user_playlists(access_token: str, limit: int = 20):
    """Get user's Spotify playlists"""
    try:
        playlists = spotify_service.get_user_playlists(access_token, limit)
        return {"playlists": playlists, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify playlists error: {e}")
        return {"playlists": [], "status": "error", "message": str(e)}

@api_router.post("/spotify/playlists/create")
async def spotify_create_playlist(request: SpotifyPlaylistRequest):
    """Create a new Spotify playlist"""
    try:
        playlist = spotify_service.create_playlist(
            access_token=request.access_token,
            playlist_name=request.name,
            description=request.description,
            public=request.public
        )
        return {"playlist": playlist, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify playlist creation error: {e}")
        raise HTTPException(status_code=400, detail="Failed to create Spotify playlist")

@api_router.post("/spotify/playlists/add-tracks")
async def spotify_add_tracks_to_playlist(request: SpotifyAddTracksRequest):
    """Add tracks to a Spotify playlist"""
    try:
        success = spotify_service.add_tracks_to_playlist(
            access_token=request.access_token,
            playlist_id=request.playlist_id,
            track_uris=request.track_uris
        )
        return {"success": success, "status": "success" if success else "error"}
    except Exception as e:
        logger.error(f"Spotify add tracks error: {e}")
        raise HTTPException(status_code=400, detail="Failed to add tracks to playlist")

@api_router.get("/spotify/recommendations")
async def spotify_get_recommendations(
    access_token: str,
    seed_genres: Optional[str] = None,
    seed_artists: Optional[str] = None,
    seed_tracks: Optional[str] = None,
    limit: int = 20
):
    """Get Spotify track recommendations"""
    try:
        recommendations = spotify_service.get_recommendations(
            access_token=access_token,
            seed_genres=seed_genres.split(',') if seed_genres else None,
            seed_artists=seed_artists.split(',') if seed_artists else None,
            seed_tracks=seed_tracks.split(',') if seed_tracks else None,
            limit=limit
        )
        return {"recommendations": recommendations, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify recommendations error: {e}")
        return {"recommendations": [], "status": "error", "message": str(e)}

@api_router.get("/spotify/genres")
async def spotify_get_available_genres():
    """Get available genre seeds for recommendations"""
    try:
        genres = spotify_service.get_available_genres()
        return {"genres": genres, "status": "success"}
    except Exception as e:
        logger.error(f"Spotify genres error: {e}")
        return {"genres": ['pop', 'rock', 'jazz', 'classical', 'electronic'], "status": "fallback"}

# Google Maps Integration Models
class NearbyPlacesRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 5000
    place_type: Optional[str] = None
    keyword: Optional[str] = None

class DirectionsRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "driving"
    avoid: List[str] = []

class GeocodeRequest(BaseModel):
    address: str

class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float

# Google Maps API Endpoints
@api_router.post("/googlemaps/places/nearby")
async def googlemaps_nearby_places(request: NearbyPlacesRequest):
    """Search for nearby places using Google Places API"""
    try:
        places = googlemaps_service.search_nearby_places(
            latitude=request.latitude,
            longitude=request.longitude,
            radius=request.radius,
            place_type=request.place_type,
            keyword=request.keyword
        )
        return {"places": places, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps nearby places error: {e}")
        fallback_places = googlemaps_service.get_fallback_places(request.latitude, request.longitude)
        return {"places": fallback_places, "status": "fallback", "message": str(e)}

@api_router.get("/googlemaps/places/{place_id}")
async def googlemaps_place_details(place_id: str):
    """Get detailed information about a specific place"""
    try:
        details = googlemaps_service.get_place_details(place_id)
        return {"details": details, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps place details error: {e}")
        fallback_details = googlemaps_service.get_fallback_place_details(place_id)
        return {"details": fallback_details, "status": "fallback", "message": str(e)}

@api_router.post("/googlemaps/directions")
async def googlemaps_directions(request: DirectionsRequest):
    """Get directions between two locations"""
    try:
        directions = googlemaps_service.get_directions(
            origin=request.origin,
            destination=request.destination,
            mode=request.mode,
            avoid=request.avoid
        )
        return {"directions": directions, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps directions error: {e}")
        fallback_directions = googlemaps_service.get_fallback_directions(request.origin, request.destination)
        return {"directions": fallback_directions, "status": "fallback", "message": str(e)}

@api_router.post("/googlemaps/traffic")
async def googlemaps_traffic_conditions(latitude: float, longitude: float, radius: int = 2000):
    """Get traffic conditions for a location"""
    try:
        traffic = googlemaps_service.get_traffic_conditions(latitude, longitude, radius)
        return {"traffic": traffic, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps traffic conditions error: {e}")
        fallback_traffic = googlemaps_service.get_fallback_traffic_conditions()
        return {"traffic": fallback_traffic, "status": "fallback", "message": str(e)}

@api_router.post("/googlemaps/geocode")
async def googlemaps_geocode_address(request: GeocodeRequest):
    """Convert an address to coordinates"""
    try:
        result = googlemaps_service.geocode_address(request.address)
        return {"location": result, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps geocoding error: {e}")
        return {"location": {"lat": 0, "lng": 0, "formatted_address": request.address}, "status": "fallback", "message": str(e)}

@api_router.post("/googlemaps/reverse-geocode")
async def googlemaps_reverse_geocode(request: ReverseGeocodeRequest):
    """Convert coordinates to an address"""
    try:
        result = googlemaps_service.reverse_geocode(request.latitude, request.longitude)
        return {"address": result, "status": "success"}
    except Exception as e:
        logger.error(f"Google Maps reverse geocoding error: {e}")
        return {"address": {"formatted_address": f"{request.latitude}, {request.longitude}"}, "status": "fallback", "message": str(e)}

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