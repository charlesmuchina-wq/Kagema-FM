"""
Traffic Integration for Dragon KARAU AI Radio
Supports multiple map providers: Google Maps, TomTom, Mapbox, OpenStreetMap
"""

import aiohttp
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)


class TrafficIntegrationManager:
    def __init__(self):
        # API Keys (optional - will use free tiers)
        self.google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.tomtom_key = os.getenv('TOMTOM_API_KEY', '')
        self.mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN', '')
        self.apple_mapkit_jwt = os.getenv('APPLE_MAPKIT_JWT', '')
        self.geoapify_key = os.getenv('GEOAPIFY_API_KEY', '')
        
        # TomTom free tier: 2,500 requests/day
        self.tomtom_base_url = "https://api.tomtom.com"
        
        # Mapbox free tier: 50,000 requests/month
        self.mapbox_base_url = "https://api.mapbox.com"
        
        # Geoapify free tier: 3,000 requests/day
        self.geoapify_base_url = "https://api.geoapify.com/v1"
        
        # Apple MapKit JS
        self.mapkit_enabled = bool(self.apple_mapkit_jwt)
        
    async def get_traffic_incidents(
        self,
        lat: float,
        lon: float,
        radius: int = 10,
        provider: str = 'tomtom'
    ) -> Dict[str, Any]:
        """
        Get traffic incidents around a location
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in km
            provider: 'tomtom', 'google', or 'mapbox'
        """
        try:
            if provider == 'tomtom' and self.tomtom_key:
                return await self._get_tomtom_incidents(lat, lon, radius)
            elif provider == 'google' and self.google_maps_key:
                return await self._get_google_traffic(lat, lon, radius)
            else:
                # Fallback to mock data for demo
                return self._get_mock_incidents(lat, lon, radius)
                
        except Exception as e:
            logger.error(f"Traffic incidents error: {e}")
            return {
                'success': False,
                'error': str(e),
                'incidents': []
            }
    
    async def _get_tomtom_incidents(
        self,
        lat: float,
        lon: float,
        radius: int
    ) -> Dict[str, Any]:
        """Get traffic incidents from TomTom API"""
        try:
            # TomTom Traffic Incidents API
            url = f"{self.tomtom_base_url}/traffic/services/5/incidentDetails"
            
            # Bounding box around point
            bbox_size = radius / 111  # Approx km to degrees
            min_lat = lat - bbox_size
            max_lat = lat + bbox_size
            min_lon = lon - bbox_size
            max_lon = lon + bbox_size
            
            params = {
                'key': self.tomtom_key,
                'bbox': f"{min_lon},{min_lat},{max_lon},{max_lat}",
                'fields': '{incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description,code},startTime,endTime}}}',
                'language': 'en-US',
                'categoryFilter': '0,1,2,3,4,5,6,7,8,9,10,11,14'  # All categories
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        incidents = self._parse_tomtom_incidents(data)
                        
                        return {
                            'success': True,
                            'provider': 'tomtom',
                            'incidents': incidents,
                            'total': len(incidents),
                            'center': {'lat': lat, 'lon': lon},
                            'radius_km': radius
                        }
                    else:
                        logger.error(f"TomTom API error: {response.status}")
                        return self._get_mock_incidents(lat, lon, radius)
                        
        except Exception as e:
            logger.error(f"TomTom incidents error: {e}")
            return self._get_mock_incidents(lat, lon, radius)
    
    def _parse_tomtom_incidents(self, data: Dict) -> List[Dict]:
        """Parse TomTom incident data"""
        incidents = []
        
        if 'incidents' in data:
            for incident in data['incidents']:
                props = incident.get('properties', {})
                geometry = incident.get('geometry', {})
                
                incidents.append({
                    'id': incident.get('id', ''),
                    'type': props.get('iconCategory', 0),
                    'severity': self._map_severity(props.get('magnitudeOfDelay', 0)),
                    'description': self._get_incident_description(props),
                    'location': self._extract_location(geometry),
                    'start_time': props.get('startTime'),
                    'end_time': props.get('endTime'),
                    'delay_minutes': props.get('delay', 0)
                })
        
        return incidents
    
    def _map_severity(self, magnitude: int) -> str:
        """Map magnitude to severity level"""
        if magnitude >= 4:
            return 'critical'
        elif magnitude >= 2:
            return 'major'
        elif magnitude >= 1:
            return 'moderate'
        else:
            return 'minor'
    
    def _get_incident_description(self, props: Dict) -> str:
        """Extract incident description"""
        events = props.get('events', [])
        if events and len(events) > 0:
            return events[0].get('description', 'Traffic incident')
        return 'Traffic incident'
    
    def _extract_location(self, geometry: Dict) -> Dict:
        """Extract coordinates from geometry"""
        coords = geometry.get('coordinates', [])
        if coords and len(coords) > 0:
            if isinstance(coords[0], list):
                # LineString - use first point
                return {'lat': coords[0][1], 'lon': coords[0][0]}
            else:
                # Point
                return {'lat': coords[1], 'lon': coords[0]}
        return {'lat': 0, 'lon': 0}
    
    async def get_traffic_flow(
        self,
        lat: float,
        lon: float,
        zoom: int = 12,
        provider: str = 'tomtom'
    ) -> Dict[str, Any]:
        """
        Get traffic flow tile URL for map overlay
        """
        try:
            if provider == 'tomtom' and self.tomtom_key:
                # TomTom Traffic Flow Tiles
                style = 'relative'  # or 'absolute'
                tile_url = f"{self.tomtom_base_url}/traffic/map/4/tile/flow/{style}/{{z}}/{{x}}/{{y}}.png?key={self.tomtom_key}"
                
                return {
                    'success': True,
                    'provider': 'tomtom',
                    'tile_url': tile_url,
                    'attribution': '© TomTom',
                    'zoom_levels': [0, 22]
                }
            
            elif provider == 'google' and self.google_maps_key:
                # Google Maps has built-in traffic layer
                return {
                    'success': True,
                    'provider': 'google',
                    'traffic_layer': 'builtin',
                    'note': 'Use Google Maps Traffic Layer directly'
                }
            
            else:
                return {
                    'success': False,
                    'error': 'No API key configured for traffic flow'
                }
                
        except Exception as e:
            logger.error(f"Traffic flow error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_mock_incidents(self, lat: float, lon: float, radius: int) -> Dict[str, Any]:
        """Generate mock traffic incidents for demo"""
        incidents = [
            {
                'id': 'demo_1',
                'type': 1,  # Accident
                'severity': 'major',
                'description': 'Multi-vehicle accident causing delays',
                'location': {'lat': lat + 0.01, 'lon': lon + 0.01},
                'delay_minutes': 15,
                'start_time': datetime.now().isoformat()
            },
            {
                'id': 'demo_2',
                'type': 2,  # Construction
                'severity': 'moderate',
                'description': 'Road construction - lane closures',
                'location': {'lat': lat - 0.02, 'lon': lon + 0.02},
                'delay_minutes': 8,
                'start_time': datetime.now().isoformat()
            },
            {
                'id': 'demo_3',
                'type': 0,  # Unknown
                'severity': 'minor',
                'description': 'Heavy traffic congestion',
                'location': {'lat': lat + 0.03, 'lon': lon - 0.01},
                'delay_minutes': 5,
                'start_time': datetime.now().isoformat()
            }
        ]
        
        return {
            'success': True,
            'provider': 'mock',
            'incidents': incidents,
            'total': len(incidents),
            'center': {'lat': lat, 'lon': lon},
            'radius_km': radius,
            'note': 'Demo data - Configure API keys for real traffic data'
        }
    
    async def generate_traffic_announcement(
        self,
        incidents: List[Dict],
        location_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate human-readable traffic announcements for radio
        """
        try:
            if not incidents:
                return {
                    'success': True,
                    'announcement': 'Traffic is flowing smoothly in your area.',
                    'severity': 'none'
                }
            
            # Sort by severity
            severity_order = {'critical': 0, 'major': 1, 'moderate': 2, 'minor': 3}
            sorted_incidents = sorted(
                incidents,
                key=lambda x: severity_order.get(x['severity'], 4)
            )
            
            # Generate announcement
            parts = []
            
            if location_name:
                parts.append(f"Traffic update for {location_name}:")
            else:
                parts.append("Traffic update:")
            
            for incident in sorted_incidents[:5]:  # Top 5 incidents
                desc = incident['description']
                delay = incident.get('delay_minutes', 0)
                
                if delay > 0:
                    parts.append(f"{desc}, causing approximately {delay} minute delays.")
                else:
                    parts.append(f"{desc}.")
            
            announcement = " ".join(parts)
            
            # Determine overall severity
            max_severity = sorted_incidents[0]['severity'] if sorted_incidents else 'none'
            
            return {
                'success': True,
                'announcement': announcement,
                'severity': max_severity,
                'incident_count': len(incidents),
                'total_delay_minutes': sum(i.get('delay_minutes', 0) for i in incidents)
            }
            
        except Exception as e:
            logger.error(f"Traffic announcement error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_map_config(self) -> Dict[str, Any]:
        """Get map configuration with available providers"""
        return {
            'success': True,
            'providers': {
                'apple_mapkit': {
                    'enabled': bool(self.apple_mapkit_jwt),
                    'features': ['3d_maps', 'turn_by_turn', 'traffic', 'directions', 'look_around'],
                    'free_tier': '250,000 requests/day',
                    'api_key_required': True,
                    'priority': 1
                },
                'google_maps': {
                    'enabled': bool(self.google_maps_key),
                    'features': ['base_map', 'traffic_layer', 'places'],
                    'free_tier': '$200/month credit',
                    'api_key_required': True,
                    'priority': 2
                },
                'tomtom': {
                    'enabled': bool(self.tomtom_key),
                    'features': ['traffic_incidents', 'traffic_flow', 'routing'],
                    'free_tier': '2,500 requests/day',
                    'api_key_required': True,
                    'priority': 3
                },
                'mapbox': {
                    'enabled': bool(self.mapbox_token),
                    'features': ['custom_styles', 'base_map', 'geocoding'],
                    'free_tier': '50,000 requests/month',
                    'api_key_required': True,
                    'priority': 4
                },
                'openstreetmap': {
                    'enabled': True,
                    'features': ['base_map', 'free_tiles'],
                    'free_tier': 'Unlimited (rate limited)',
                    'api_key_required': False,
                    'priority': 5
                }
            },
            'recommended': 'apple_mapkit' if self.apple_mapkit_jwt else ('tomtom' if self.tomtom_key else 'openstreetmap'),
            'jwt_token': self.apple_mapkit_jwt if self.apple_mapkit_jwt else None
        }


# Singleton instance
_traffic_manager = None

def get_traffic_manager() -> TrafficIntegrationManager:
    """Get singleton instance of TrafficIntegrationManager"""
    global _traffic_manager
    if _traffic_manager is None:
        _traffic_manager = TrafficIntegrationManager()
    return _traffic_manager
