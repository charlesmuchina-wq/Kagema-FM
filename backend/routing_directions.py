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
        self.geoapify_places_key = os.getenv('GEOAPIFY_PLACES_KEY', '')
        self.distance_matrix_key = os.getenv('DISTANCE_MATRIX_API_KEY', '') or self.geoapify_routing_key
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
    
    async def calculate_distance_matrix(
        self,
        sources: List[Tuple[float, float]],
        targets: List[Tuple[float, float]],
        mode: str = 'drive',
        provider: str = 'geoapify'
    ) -> Dict[str, Any]:
        """
        Calculate distance matrix between multiple origins and destinations
        Args:
            sources: List of (lat, lon) tuples for origin points
            targets: List of (lat, lon) tuples for destination points
            mode: 'drive', 'walk', 'bicycle', 'transit'
            provider: 'geoapify' (default)
        Returns:
            Matrix with distances and durations for each source-target pair
        """
        try:
            if provider == 'geoapify' and (self.distance_matrix_key or self.geoapify_routing_key):
                return await self._get_geoapify_distance_matrix(
                    sources, targets, mode
                )
            else:
                return {
                    'success': False,
                    'error': f'Distance Matrix provider {provider} not configured'
                }
        except Exception as e:
            logger.error(f"Distance matrix error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_geoapify_distance_matrix(
        self,
        sources: List[Tuple[float, float]],
        targets: List[Tuple[float, float]],
        mode: str
    ) -> Dict[str, Any]:
        """Calculate distance matrix using Geoapify Route Matrix API"""
        try:
            url = f"{self.geoapify_base}/routematrix"
            # Use routing key for Route Matrix API (same key works for both)
            api_key = self.geoapify_routing_key
            params = {
                'apiKey': api_key
            }
            
            # Prepare request body
            body = {
                'mode': mode,
                'sources': [
                    {'location': [lon, lat]} 
                    for lat, lon in sources
                ],
                'targets': [
                    {'location': [lon, lat]} 
                    for lat, lon in targets
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, json=body) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse the matrix response
                        matrix = []
                        if 'sources_to_targets' in data:
                            for source_idx, source_data in enumerate(data['sources_to_targets']):
                                source_results = []
                                for target_idx, target_data in enumerate(source_data):
                                    source_results.append({
                                        'source_index': source_idx,
                                        'target_index': target_idx,
                                        'distance_meters': target_data.get('distance'),
                                        'duration_seconds': target_data.get('time'),
                                        'distance_km': round(target_data.get('distance', 0) / 1000, 2) if target_data.get('distance') else None,
                                        'duration_minutes': round(target_data.get('time', 0) / 60, 1) if target_data.get('time') else None,
                                        'reachable': target_data.get('distance') is not None
                                    })
                                matrix.append(source_results)
                        
                        return {
                            'success': True,
                            'provider': 'geoapify',
                            'mode': mode,
                            'sources_count': len(sources),
                            'targets_count': len(targets),
                            'matrix': matrix,
                            'raw_data': data
                        }
                    else:
                        error_data = await response.text()
                        logger.error(f"Geoapify Distance Matrix error: {response.status} - {error_data}")
                        return {
                            'success': False,
                            'error': f'Distance Matrix API error: {response.status}',
                            'details': error_data
                        }
        except Exception as e:
            logger.error(f"Geoapify Distance Matrix error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def find_nearest_locations(
        self,
        origin_lat: float,
        origin_lon: float,
        target_locations: List[Dict[str, Any]],
        mode: str = 'drive',
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Find nearest locations to an origin point
        Args:
            origin_lat, origin_lon: Origin coordinates
            target_locations: List of dicts with 'lat', 'lon', and optional metadata
            mode: Travel mode
            limit: Maximum number of results to return
        Returns:
            Sorted list of nearest locations with distances
        """
        try:
            if not target_locations:
                return {
                    'success': False,
                    'error': 'No target locations provided'
                }
            
            # Prepare sources and targets
            sources = [(origin_lat, origin_lon)]
            targets = [(loc['lat'], loc['lon']) for loc in target_locations]
            
            # Calculate distance matrix
            matrix_result = await self.calculate_distance_matrix(
                sources, targets, mode
            )
            
            if not matrix_result.get('success'):
                return matrix_result
            
            # Combine distances with location metadata
            results = []
            if matrix_result.get('matrix') and len(matrix_result['matrix']) > 0:
                source_row = matrix_result['matrix'][0]
                
                for idx, distance_data in enumerate(source_row):
                    if distance_data.get('reachable'):
                        location = target_locations[idx].copy()
                        location.update({
                            'distance_meters': distance_data['distance_meters'],
                            'distance_km': distance_data['distance_km'],
                            'duration_seconds': distance_data['duration_seconds'],
                            'duration_minutes': distance_data['duration_minutes']
                        })
                        results.append(location)
            
            # Sort by distance
            results.sort(key=lambda x: x.get('distance_meters', float('inf')))
            
            # Limit results
            results = results[:limit]
            
            return {
                'success': True,
                'origin': {
                    'lat': origin_lat,
                    'lon': origin_lon
                },
                'nearest_locations': results,
                'count': len(results),
                'mode': mode
            }
        except Exception as e:
            logger.error(f"Find nearest locations error: {e}")
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
