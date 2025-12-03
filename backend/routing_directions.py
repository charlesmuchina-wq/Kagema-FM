"""
Routing & Directions for Dragon KARAU AI Radio
Multi-provider routing with Geoapify, TomTom, and Apple MapKit
"""

import aiohttp
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)


class RoutingDirectionsManager:
    def __init__(self):
        # API Keys
        self.geoapify_routing_key = os.getenv('GEOAPIFY_ROUTING_KEY', '')
        self.geoapify_geocoding_key = os.getenv('GEOAPIFY_GEOCODING_KEY', '')
        self.tomtom_key = os.getenv('TOMTOM_API_KEY', '')
        
        # Base URLs
        self.geoapify_base = "https://api.geoapify.com/v1"
        self.tomtom_base = "https://api.tomtom.com"
        
    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = 'drive',
        provider: str = 'geoapify'
    ) -> Dict[str, Any]:
        """
        Get route between two points
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            mode: 'drive', 'walk', 'bicycle', 'transit'
            provider: 'geoapify', 'tomtom'
        """
        try:
            if provider == 'geoapify' and self.geoapify_routing_key:
                return await self._get_geoapify_route(
                    start_lat, start_lon, end_lat, end_lon, mode
                )
            elif provider == 'tomtom' and self.tomtom_key:
                return await self._get_tomtom_route(
                    start_lat, start_lon, end_lat, end_lon, mode
                )
            else:
                return {
                    'success': False,
                    'error': f'Provider {provider} not configured'
                }
        except Exception as e:
            logger.error(f"Get route error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_geoapify_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str
    ) -> Dict[str, Any]:
        """Get route from Geoapify Routing API"""
        try:
            # Geoapify mode mapping
            mode_map = {
                'drive': 'drive',
                'walk': 'walk',
                'bicycle': 'bicycle',
                'transit': 'approximated_transit'
            }
            
            geoapify_mode = mode_map.get(mode, 'drive')
            
            url = f"{self.geoapify_base}/routing"
            params = {
                'waypoints': f"{start_lat},{start_lon}|{end_lat},{end_lon}",
                'mode': geoapify_mode,
                'apiKey': self.geoapify_routing_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'features' in data and len(data['features']) > 0:
                            feature = data['features'][0]
                            properties = feature['properties']
                            
                            return {
                                'success': True,
                                'provider': 'geoapify',
                                'route': {
                                    'distance_meters': properties.get('distance'),
                                    'duration_seconds': properties.get('time'),
                                    'distance_km': round(properties.get('distance', 0) / 1000, 2),
                                    'duration_minutes': round(properties.get('time', 0) / 60, 1),
                                    'mode': mode,
                                    'geometry': feature.get('geometry'),
                                    'legs': properties.get('legs', []),
                                    'waypoints': properties.get('waypoints', [])
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'No route found'
                            }
                    else:
                        error_data = await response.text()
                        logger.error(f"Geoapify routing error: {response.status} - {error_data}")
                        return {
                            'success': False,
                            'error': f'Routing API error: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Geoapify routing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_tomtom_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str
    ) -> Dict[str, Any]:
        """Get route from TomTom Routing API"""
        try:
            url = f"{self.tomtom_base}/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
            
            params = {
                'key': self.tomtom_key,
                'travelMode': 'car' if mode == 'drive' else mode,
                'traffic': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'routes' in data and len(data['routes']) > 0:
                            route = data['routes'][0]
                            summary = route['summary']
                            
                            return {
                                'success': True,
                                'provider': 'tomtom',
                                'route': {
                                    'distance_meters': summary.get('lengthInMeters'),
                                    'duration_seconds': summary.get('travelTimeInSeconds'),
                                    'distance_km': round(summary.get('lengthInMeters', 0) / 1000, 2),
                                    'duration_minutes': round(summary.get('travelTimeInSeconds', 0) / 60, 1),
                                    'traffic_delay_seconds': summary.get('trafficDelayInSeconds', 0),
                                    'mode': mode,
                                    'legs': route.get('legs', [])
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'No route found'
                            }
                    else:
                        return {
                            'success': False,
                            'error': f'TomTom routing error: {response.status}'
                        }
        except Exception as e:
            logger.error(f"TomTom routing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def geocode_address(
        self,
        address: str,
        provider: str = 'geoapify'
    ) -> Dict[str, Any]:
        """
        Convert address to coordinates
        """
        try:
            if provider == 'geoapify' and self.geoapify_geocoding_key:
                return await self._geocode_geoapify(address)
            else:
                return {
                    'success': False,
                    'error': 'Geocoding provider not configured'
                }
        except Exception as e:
            logger.error(f"Geocode error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _geocode_geoapify(self, address: str) -> Dict[str, Any]:
        """Geocode address using Geoapify"""
        try:
            url = f"{self.geoapify_base}/geocode/search"
            params = {
                'text': address,
                'apiKey': self.geoapify_geocoding_key,
                'limit': 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'features' in data and len(data['features']) > 0:
                            results = []
                            for feature in data['features']:
                                properties = feature['properties']
                                coords = feature['geometry']['coordinates']
                                
                                results.append({
                                    'formatted_address': properties.get('formatted'),
                                    'latitude': coords[1],
                                    'longitude': coords[0],
                                    'city': properties.get('city'),
                                    'country': properties.get('country'),
                                    'postcode': properties.get('postcode')
                                })
                            
                            return {
                                'success': True,
                                'results': results,
                                'total': len(results)
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'Address not found',
                                'results': []
                            }
                    else:
                        return {
                            'success': False,
                            'error': f'Geocoding error: {response.status}'
                        }
        except Exception as e:
            logger.error(f"Geoapify geocoding error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def reverse_geocode(
        self,
        lat: float,
        lon: float,
        provider: str = 'geoapify'
    ) -> Dict[str, Any]:
        """
        Convert coordinates to address
        """
        try:
            if provider == 'geoapify' and self.geoapify_geocoding_key:
                url = f"{self.geoapify_base}/geocode/reverse"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'apiKey': self.geoapify_geocoding_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if 'features' in data and len(data['features']) > 0:
                                properties = data['features'][0]['properties']
                                
                                return {
                                    'success': True,
                                    'address': {
                                        'formatted': properties.get('formatted'),
                                        'street': properties.get('street'),
                                        'city': properties.get('city'),
                                        'state': properties.get('state'),
                                        'country': properties.get('country'),
                                        'postcode': properties.get('postcode')
                                    }
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': 'Address not found'
                                }
                        else:
                            return {
                                'success': False,
                                'error': f'Reverse geocoding error: {response.status}'
                            }
            else:
                return {
                    'success': False,
                    'error': 'Geocoding provider not configured'
                }
        except Exception as e:
            logger.error(f"Reverse geocode error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def calculate_isochrone(
        self,
        lat: float,
        lon: float,
        time_minutes: int = 15,
        mode: str = 'drive',
        provider: str = 'geoapify'
    ) -> Dict[str, Any]:
        """
        Calculate travel time area (isochrone)
        Shows area reachable within given time
        """
        try:
            if provider == 'geoapify' and self.geoapify_routing_key:
                url = f"{self.geoapify_base}/isoline"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'type': 'time',
                    'mode': mode,
                    'range': time_minutes * 60,  # Convert to seconds
                    'apiKey': self.geoapify_routing_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            return {
                                'success': True,
                                'isochrone': data,
                                'time_minutes': time_minutes,
                                'mode': mode
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'Isochrone error: {response.status}'
                            }
            else:
                return {
                    'success': False,
                    'error': 'Isochrone provider not configured'
                }
        except Exception as e:
            logger.error(f"Isochrone error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_routing_manager = None

def get_routing_manager() -> RoutingDirectionsManager:
    """Get singleton instance of RoutingDirectionsManager"""
    global _routing_manager
    if _routing_manager is None:
        _routing_manager = RoutingDirectionsManager()
    return _routing_manager
