from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid
from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
import jwt
import base64
import xml.etree.ElementTree as ET

# Integration Service Classes

class IntegrationType(Enum):
    GOOGLE_MAPS = "google_maps"
    WAZE = "waze"
    ANDROID_AUTO = "android_auto"
    APPLE_CARPLAY = "apple_carplay"
    APPLE_MUSIC = "apple_music"
    EMERGENCY_ALERTS = "emergency_alerts"
    VOICE_CONTROL = "voice_control"

class PlatformIntegrationManager:
    def __init__(self):
        self.active_integrations = {}
        self.webhook_callbacks = {}
        self.realtime_connections: List[WebSocket] = []
    
    async def initialize_integration(self, integration_type: IntegrationType, config: Dict):
        """Initialize a platform integration with provided configuration"""
        try:
            if integration_type == IntegrationType.GOOGLE_MAPS:
                integration = GoogleMapsIntegration(config)
            elif integration_type == IntegrationType.WAZE:
                integration = WazeIntegration(config)
            elif integration_type == IntegrationType.APPLE_MUSIC:
                integration = AppleMusicIntegration(config)
            elif integration_type == IntegrationType.EMERGENCY_ALERTS:
                integration = EmergencyAlertIntegration(config)
            elif integration_type == IntegrationType.VOICE_CONTROL:
                integration = VoiceControlIntegration(config)
            else:
                raise ValueError(f"Unsupported integration type: {integration_type}")
            
            await integration.initialize()
            self.active_integrations[integration_type.value] = integration
            
            return {"status": "initialized", "integration": integration_type.value}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Integration initialization failed: {e}")

class GoogleMapsIntegration:
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key')
        self.client = httpx.AsyncClient()
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def initialize(self):
        """Initialize Google Maps services"""
        self.places_service = GooglePlacesService(self.api_key)
        self.directions_service = GoogleDirectionsService(self.api_key)
        self.traffic_service = GoogleTrafficService(self.api_key)
    
    async def get_nearby_points_of_interest(self, lat: float, lng: float, radius: int = 5000):
        """Get nearby points of interest for content personalization"""
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': 'point_of_interest',
            'key': self.api_key
        }
        
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def get_traffic_conditions(self, lat: float, lng: float):
        """Get real-time traffic conditions"""
        url = f"{self.base_url}/directions/json"
        params = {
            'origin': f"{lat},{lng}",
            'destination': f"{lat + 0.01},{lng + 0.01}",
            'departure_time': 'now',
            'traffic_model': 'optimistic',
            'key': self.api_key
        }
        
        response = await self.client.get(url, params=params)
        return response.json()

class SpotifyIntegration:
    def __init__(self, config: Dict):
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.redirect_uri = config.get('redirect_uri')
        self.access_token = None
        self.refresh_token = None
    
    async def initialize(self):
        """Initialize Spotify Web API client"""
        self.client = httpx.AsyncClient(
            base_url="https://api.spotify.com/v1",
            timeout=30.0
        )
    
    async def authenticate_user(self, auth_code: str):
        """Exchange authorization code for access token"""
        token_url = "https://accounts.spotify.com/api/token"
        
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens['access_token']
                self.refresh_token = tokens['refresh_token']
                return tokens
            else:
                raise HTTPException(status_code=400, detail="Authentication failed")
    
    async def search_tracks(self, query: str, limit: int = 20):
        """Search for tracks on Spotify"""
        if not self.access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {
            'q': query,
            'type': 'track',
            'limit': limit,
            'market': 'KE'
        }
        
        response = await self.client.get('/search', headers=headers, params=params)
        return response.json()
    
    async def create_playlist_from_radio(self, user_id: str, playlist_name: str, track_uris: List[str]):
        """Create a Spotify playlist from radio tracks"""
        if not self.access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Create playlist
        playlist_data = {
            'name': playlist_name,
            'description': 'Created from Kagema FM radio tracks',
            'public': False
        }
        
        response = await self.client.post(
            f'/users/{user_id}/playlists',
            headers=headers,
            json=playlist_data
        )
        
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create playlist")
        
        playlist = response.json()
        
        # Add tracks to playlist
        if track_uris:
            tracks_data = {'uris': track_uris}
            await self.client.post(
                f'/playlists/{playlist["id"]}/tracks',
                headers=headers,
                json=tracks_data
            )
        
        return playlist

class EmergencyAlertIntegration:
    def __init__(self, config: Dict):
        self.alert_sources = config.get('sources', [])
        self.active_alerts = {}
        self.subscribers = []
    
    async def initialize(self):
        """Initialize emergency alert monitoring"""
        asyncio.create_task(self.monitor_emergency_feeds())
    
    async def monitor_emergency_feeds(self):
        """Continuously monitor emergency alert feeds"""
        while True:
            try:
                await self.check_weather_alerts()
                await self.check_traffic_emergencies()
                await self.check_amber_alerts()
                
                # Wait 5 minutes before next check
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"Emergency monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def check_weather_alerts(self):
        """Check for severe weather alerts"""
        try:
            async with httpx.AsyncClient() as client:
                # Kenya Meteorological Department API (mock endpoint)
                response = await client.get("https://api.meteo.go.ke/alerts/active")
                
                if response.status_code == 200:
                    alerts = response.json()
                    for alert in alerts:
                        await self.process_emergency_alert({
                            'id': alert.get('id'),
                            'type': 'weather',
                            'severity': alert.get('severity', 'moderate'),
                            'title': alert.get('headline'),
                            'description': alert.get('description'),
                            'area': alert.get('area'),
                            'effective': alert.get('effective'),
                            'expires': alert.get('expires')
                        })
        except Exception as e:
            print(f"Weather alerts error: {e}")
    
    async def check_traffic_emergencies(self):
        """Check for traffic emergencies and road closures"""
        try:
            async with httpx.AsyncClient() as client:
                # Kenya Roads Authority API (mock endpoint)
                response = await client.get("https://api.kra.go.ke/traffic/emergencies")
                
                if response.status_code == 200:
                    emergencies = response.json()
                    for emergency in emergencies:
                        await self.process_emergency_alert({
                            'id': emergency.get('id'),
                            'type': 'traffic',
                            'severity': 'severe',
                            'title': f"Traffic Emergency - {emergency.get('road')}",
                            'description': emergency.get('description'),
                            'area': emergency.get('location'),
                            'effective': emergency.get('reported_time'),
                            'expires': emergency.get('estimated_clearance')
                        })
        except Exception as e:
            print(f"Traffic emergency error: {e}")
    
    async def process_emergency_alert(self, alert_data: Dict):
        """Process and broadcast emergency alert"""
        alert_id = alert_data.get('id')
        
        if alert_id not in self.active_alerts:
            self.active_alerts[alert_id] = alert_data
            
            # Broadcast to all subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber.send_json({
                        'type': 'emergency_alert',
                        'data': alert_data
                    })
                except:
                    self.subscribers.remove(subscriber)

class VoiceControlIntegration:
    def __init__(self, config: Dict):
        self.supported_commands = [
            'play_station', 'pause', 'resume', 'stop',
            'volume_up', 'volume_down', 'set_volume',
            'traffic_update', 'weather_update',
            'create_playlist', 'search_music'
        ]
        self.command_patterns = self.load_command_patterns()
    
    async def initialize(self):
        """Initialize voice command processing"""
        print("Voice control integration initialized")
    
    def load_command_patterns(self) -> Dict:
        """Load voice command patterns for different languages"""
        return {
            'en': {
                'play_station': [
                    r'play\s+(.*?)\s*(?:radio|station|fm)?',
                    r'tune\s+to\s+(.*?)(?:\s+station)?',
                    r'listen\s+to\s+(.*?)(?:\s+radio)?'
                ],
                'pause': [r'pause', r'stop\s+playing', r'hold\s+on'],
                'resume': [r'resume', r'continue', r'play\s+again'],
                'volume_up': [r'volume\s+up', r'louder', r'increase\s+volume'],
                'volume_down': [r'volume\s+down', r'quieter', r'decrease\s+volume']
            },
            'sw': {
                'play_station': [r'cheza\s+(.*)', r'sikiliza\s+(.*)', r'weka\s+(.*)'],
                'pause': [r'simama', r'acha', r'kimya'],
                'resume': [r'endelea', r'rudi', r'cheza\s+tena']
            }
        }
    
    async def process_voice_command(self, command: str, language: str = 'en') -> Dict:
        """Process voice command and return action"""
        import re
        
        command = command.lower().strip()
        patterns = self.command_patterns.get(language, self.command_patterns['en'])
        
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    return {
                        'success': True,
                        'intent': intent,
                        'entities': match.groups() if match.groups() else [],
                        'response': self.generate_response(intent, language)
                    }
        
        return {
            'success': False,
            'error': 'Command not recognized',
            'response': 'I didn\'t understand that command'
        }
    
    def generate_response(self, intent: str, language: str) -> str:
        """Generate appropriate response for the command"""
        responses = {
            'en': {
                'play_station': 'Playing station',
                'pause': 'Pausing playback',
                'resume': 'Resuming playback',
                'volume_up': 'Increasing volume',
                'volume_down': 'Decreasing volume'
            },
            'sw': {
                'play_station': 'Nacheza kituo',
                'pause': 'Nasimamisha',
                'resume': 'Naendelea',
                'volume_up': 'Naongeza sauti',
                'volume_down': 'Napunguza sauti'
            }
        }
        
        lang_responses = responses.get(language, responses['en'])
        return lang_responses.get(intent, 'Processing request')

# FastAPI Application Setup
app = FastAPI(title="Kagema FM Platform Integrations", version="4.0.0")

# Initialize integration manager
integration_manager = PlatformIntegrationManager()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Models
class IntegrationRequest(BaseModel):
    integration_type: str
    config: Dict[str, Any]

class VoiceCommandRequest(BaseModel):
    command: str
    language: str = "en"
    user_id: Optional[str] = None

class LocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: float
    timestamp: str
    user_id: str

class EmergencyAlertRequest(BaseModel):
    title: str
    description: str
    severity: str
    area: str
    alert_type: str

# API Endpoints

@app.get("/api/integrations")
async def get_active_integrations():
    """Get list of active integrations"""
    return {
        "active_integrations": list(integration_manager.active_integrations.keys()),
        "total_count": len(integration_manager.active_integrations)
    }

@app.post("/api/integrations/initialize")
async def initialize_integration(request: IntegrationRequest):
    """Initialize a platform integration"""
    try:
        integration_type = IntegrationType(request.integration_type)
        result = await integration_manager.initialize_integration(integration_type, request.config)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/google-maps/nearby-places")
async def get_nearby_places(lat: float, lng: float, radius: int = 5000):
    """Get nearby places from Google Maps"""
    if 'google_maps' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Google Maps integration not initialized")
    
    integration = integration_manager.active_integrations['google_maps']
    result = await integration.get_nearby_points_of_interest(lat, lng, radius)
    return result

@app.post("/api/google-maps/traffic")
async def get_traffic_conditions(lat: float, lng: float):
    """Get traffic conditions from Google Maps"""
    if 'google_maps' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Google Maps integration not initialized")
    
    integration = integration_manager.active_integrations['google_maps']
    result = await integration.get_traffic_conditions(lat, lng)
    return result

@app.post("/api/spotify/authenticate")
async def authenticate_spotify(auth_code: str):
    """Authenticate with Spotify"""
    if 'spotify' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Spotify integration not initialized")
    
    integration = integration_manager.active_integrations['spotify']
    result = await integration.authenticate_user(auth_code)
    return result

@app.post("/api/spotify/search")
async def search_spotify(query: str, limit: int = 20):
    """Search Spotify for tracks"""
    if 'spotify' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Spotify integration not initialized")
    
    integration = integration_manager.active_integrations['spotify']
    result = await integration.search_tracks(query, limit)
    return result

@app.post("/api/spotify/create-playlist")
async def create_spotify_playlist(user_id: str, playlist_name: str, track_uris: List[str]):
    """Create a Spotify playlist from radio tracks"""
    if 'spotify' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Spotify integration not initialized")
    
    integration = integration_manager.active_integrations['spotify']
    result = await integration.create_playlist_from_radio(user_id, playlist_name, track_uris)
    return result

@app.post("/api/voice/process-command")
async def process_voice_command(request: VoiceCommandRequest):
    """Process voice command"""
    if 'voice_control' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Voice control integration not initialized")
    
    integration = integration_manager.active_integrations['voice_control']
    result = await integration.process_voice_command(request.command, request.language)
    return result

@app.post("/api/location/update")
async def update_user_location(request: LocationUpdateRequest):
    """Update user location for location-based services"""
    try:
        # Store location update
        location_data = {
            'user_id': request.user_id,
            'latitude': request.latitude,
            'longitude': request.longitude,
            'accuracy': request.accuracy,
            'timestamp': request.timestamp,
            'processed_at': datetime.now().isoformat()
        }
        
        # Process location triggers
        triggers = await process_location_triggers(location_data)
        
        return {
            'status': 'updated',
            'triggers': triggers,
            'location': location_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location update failed: {e}")

@app.websocket("/ws/emergency-alerts")
async def emergency_alerts_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time emergency alerts"""
    await websocket.accept()
    
    if 'emergency_alerts' in integration_manager.active_integrations:
        integration = integration_manager.active_integrations['emergency_alerts']
        integration.subscribers.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if 'emergency_alerts' in integration_manager.active_integrations:
            integration = integration_manager.active_integrations['emergency_alerts']
            if websocket in integration.subscribers:
                integration.subscribers.remove(websocket)

@app.post("/api/emergency/broadcast")
async def broadcast_emergency_alert(alert: EmergencyAlertRequest):
    """Broadcast custom emergency alert"""
    if 'emergency_alerts' not in integration_manager.active_integrations:
        raise HTTPException(status_code=503, detail="Emergency alerts integration not initialized")
    
    integration = integration_manager.active_integrations['emergency_alerts']
    alert_data = {
        'id': str(uuid.uuid4()),
        'type': alert.alert_type,
        'severity': alert.severity,
        'title': alert.title,
        'description': alert.description,
        'area': alert.area,
        'effective': datetime.now().isoformat(),
        'expires': None
    }
    
    await integration.process_emergency_alert(alert_data)
    return {"status": "broadcast", "alert_id": alert_data['id']}

async def process_location_triggers(location_data: Dict) -> List[Dict]:
    """Process location-based triggers for content switching and alerts"""
    triggers = []
    
    # Example: Check if user entered a new city
    # This would integrate with the language detection service
    try:
        # Mock trigger processing
        lat, lng = location_data['latitude'], location_data['longitude']
        
        # Check for city boundaries
        if -1.5 <= lat <= -1.0 and 36.5 <= lng <= 37.0:  # Nairobi area
            triggers.append({
                'type': 'language_switch',
                'action': 'switch_to_english',
                'location': 'Nairobi'
            })
        elif -0.2 <= lat <= 0.2 and 34.5 <= lng <= 35.0:  # Kisumu area
            triggers.append({
                'type': 'language_switch',
                'action': 'switch_to_luo',
                'location': 'Kisumu'
            })
        
    except Exception as e:
        print(f"Location trigger processing error: {e}")
    
    return triggers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)