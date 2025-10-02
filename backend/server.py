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
from user_preferences import UserPreferencesManager, UserPreferences as UserPreferencesModel, FavoriteItem, ListeningHistory
from voice_ai_service import voice_ai_service, VoiceInterpretationRequest, VoiceInterpretationResponse
from spotify_service import spotify_service

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
    location: LocationRequest,
    preferences: UserPreferencesModel
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
        user_age = getattr(preferences, 'user_age', None)
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