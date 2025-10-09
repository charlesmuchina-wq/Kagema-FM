"""
Hybrid Geolocation Service
Combines client-side GPS geolocation with server-side IP-based geolocation
for comprehensive location detection with graceful fallbacks
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Tuple
from fastapi import Request
import json
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class HybridGeolocationService:
    """
    Hybrid Geolocation Service combining client-side and server-side methods
    
    Features:
    - IP-based geolocation (immediate, no permission required)
    - Client-side GPS integration (high accuracy with permission)
    - Graceful fallback mechanisms
    - Location caching for performance
    - Multiple IP geolocation providers for reliability
    """
    
    def __init__(self):
        # Cache for 1 hour to avoid repeated API calls
        self.ip_location_cache = TTLCache(maxsize=1000, ttl=3600)
        self.coordinate_cache = TTLCache(maxsize=500, ttl=1800)  # 30 minutes
        
        # Multiple IP geolocation services for redundancy
        self.ip_geolocation_services = [
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/{ip}/json/',
                'free_tier': True,
                'accuracy': 'city'
            },
            {
                'name': 'ip-api.com', 
                'url': 'http://ip-api.com/json/{ip}',
                'free_tier': True,
                'accuracy': 'city'
            },
            {
                'name': 'freegeoip.live',
                'url': 'https://freegeoip.live/json/{ip}',
                'free_tier': True,
                'accuracy': 'region'
            }
        ]
        
        logger.info("✅ Hybrid Geolocation Service initialized")
    
    async def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers with proxy support"""
        try:
            # Check for forwarded IP (common with proxies/load balancers)
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                # Take the first IP in the chain
                client_ip = forwarded_for.split(',')[0].strip()
                return client_ip
            
            # Check for real IP header
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
            
            # Fallback to direct client IP
            if hasattr(request, 'client') and request.client:
                return request.client.host
            
            # Default fallback for testing
            return '8.8.8.8'  # Google DNS for testing
            
        except Exception as e:
            logger.error(f"❌ Error extracting client IP: {e}")
            return '8.8.8.8'
    
    async def get_ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Get location information from IP address using multiple providers"""
        try:
            # Check cache first
            cache_key = f"ip_{ip_address}"
            if cache_key in self.ip_location_cache:
                logger.info(f"📍 IP geolocation cache hit for: {ip_address}")
                return self.ip_location_cache[cache_key]
            
            # Try each IP geolocation service
            for service in self.ip_geolocation_services:
                try:
                    location_data = await self._query_ip_service(service, ip_address)
                    if location_data:
                        # Cache successful result
                        self.ip_location_cache[cache_key] = location_data
                        logger.info(f"✅ IP geolocation success via {service['name']}: {location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}")
                        return location_data
                        
                except Exception as e:
                    logger.warning(f"⚠️ IP geolocation failed for {service['name']}: {e}")
                    continue
            
            # All services failed, return fallback
            logger.warning(f"❌ All IP geolocation services failed for {ip_address}")
            return self._get_fallback_location(ip_address)
            
        except Exception as e:
            logger.error(f"❌ Error in IP geolocation: {e}")
            return self._get_fallback_location(ip_address)
    
    async def _query_ip_service(self, service: Dict[str, Any], ip_address: str) -> Optional[Dict[str, Any]]:
        """Query a specific IP geolocation service"""
        try:
            url = service['url'].format(ip=ip_address)
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_ip_response(data, service['name'])
                    else:
                        logger.warning(f"⚠️ {service['name']} returned status {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"⚠️ Error querying {service['name']}: {e}")
            return None
    
    def _normalize_ip_response(self, data: Dict[str, Any], service_name: str) -> Dict[str, Any]:
        """Normalize different IP geolocation service responses to common format"""
        try:
            if service_name == 'ipapi.co':
                return {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'country_code': data.get('country_code', ''),
                    'timezone': data.get('timezone', ''),
                    'accuracy': 'city',
                    'source': 'ip_geolocation',
                    'provider': service_name
                }
            
            elif service_name == 'ip-api.com':
                return {
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', ''),
                    'timezone': data.get('timezone', ''),
                    'accuracy': 'city',
                    'source': 'ip_geolocation',
                    'provider': service_name
                }
            
            elif service_name == 'freegeoip.live':
                return {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region_name', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'country_code': data.get('country_code', ''),
                    'timezone': data.get('time_zone', ''),
                    'accuracy': 'region',
                    'source': 'ip_geolocation',
                    'provider': service_name
                }
            
            else:
                # Generic normalization
                return {
                    'latitude': data.get('latitude') or data.get('lat'),
                    'longitude': data.get('longitude') or data.get('lon'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('country_code', ''),
                    'timezone': data.get('timezone', ''),
                    'accuracy': 'region',
                    'source': 'ip_geolocation',
                    'provider': service_name
                }
                
        except Exception as e:
            logger.error(f"❌ Error normalizing {service_name} response: {e}")
            return None
    
    def _get_fallback_location(self, ip_address: str = None) -> Dict[str, Any]:
        """Provide fallback location when all IP services fail"""
        # Default to a major city if no other information available
        return {
            'latitude': 40.7128,  # New York City
            'longitude': -74.0060,
            'city': 'New York',
            'region': 'New York',
            'country': 'United States',
            'country_code': 'US',
            'timezone': 'America/New_York',
            'accuracy': 'fallback',
            'source': 'fallback',
            'provider': 'system_fallback',
            'note': f'Fallback location used for IP: {ip_address}'
        }
    
    async def enhance_with_gps_data(self, ip_location: Dict[str, Any], gps_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine IP-based location with GPS data for enhanced accuracy"""
        try:
            if not gps_data or not gps_data.get('latitude') or not gps_data.get('longitude'):
                logger.info("📍 No GPS data available, using IP location only")
                return ip_location
            
            # Calculate distance between IP and GPS locations
            distance_km = self._calculate_distance(
                ip_location.get('latitude', 0),
                ip_location.get('longitude', 0),
                gps_data.get('latitude'),
                gps_data.get('longitude')
            )
            
            # If GPS and IP are very far apart, log for analysis but prefer GPS
            if distance_km > 100:  # More than 100km difference
                logger.info(f"📍 Large distance between IP ({ip_location.get('city')}) and GPS location: {distance_km:.1f}km")
            
            # Create enhanced location combining both sources
            enhanced_location = {
                'latitude': gps_data.get('latitude'),
                'longitude': gps_data.get('longitude'),
                'city': gps_data.get('city', ip_location.get('city', 'Unknown')),
                'region': gps_data.get('region', ip_location.get('region', 'Unknown')),
                'country': gps_data.get('country', ip_location.get('country', 'Unknown')),
                'country_code': gps_data.get('country_code', ip_location.get('country_code', '')),
                'timezone': ip_location.get('timezone', ''),  # IP often has better timezone data
                'accuracy': 'gps_enhanced',
                'source': 'hybrid_gps_ip',
                'provider': 'hybrid_service',
                'gps_available': True,
                'ip_fallback': ip_location,
                'distance_difference_km': round(distance_km, 2) if distance_km else 0
            }
            
            logger.info(f"✅ Enhanced location with GPS: {enhanced_location.get('city')}, accuracy: GPS")
            return enhanced_location
            
        except Exception as e:
            logger.error(f"❌ Error enhancing with GPS data: {e}")
            return ip_location
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        try:
            import math
            
            # Convert to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Haversine formula
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth radius in kilometers
            earth_radius_km = 6371
            distance = earth_radius_km * c
            
            return distance
            
        except Exception as e:
            logger.error(f"❌ Error calculating distance: {e}")
            return 0
    
    async def get_hybrid_location(self, request: Request, gps_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main method to get location using hybrid approach"""
        try:
            # Step 1: Always get IP-based location first (immediate, no permission needed)
            client_ip = await self.get_client_ip(request)
            ip_location = await self.get_ip_geolocation(client_ip)
            
            logger.info(f"📍 IP-based location: {ip_location.get('city')}, {ip_location.get('country')} (IP: {client_ip})")
            
            # Step 2: If GPS data is provided, enhance with it
            if gps_data:
                enhanced_location = await self.enhance_with_gps_data(ip_location, gps_data)
                return enhanced_location
            else:
                # Return IP location as fallback
                return ip_location
                
        except Exception as e:
            logger.error(f"❌ Error in hybrid geolocation: {e}")
            return self._get_fallback_location()
    
    async def get_location_suggestions(self, location_data: Dict[str, Any], context: str = 'radio') -> Dict[str, Any]:
        """Get location-based suggestions for radio stations, services, etc."""
        try:
            country = location_data.get('country', 'Unknown')
            city = location_data.get('city', 'Unknown')
            
            suggestions = {
                'country': country,
                'city': city,
                'local_services': [],
                'radio_suggestions': [],
                'language_suggestions': []
            }
            
            # Country-specific suggestions
            if context == 'radio':
                if 'Brazil' in country:
                    suggestions['radio_suggestions'] = ['Brazilian stations', 'Portuguese language', 'Samba/Bossa Nova']
                    suggestions['language_suggestions'] = ['Portuguese']
                elif 'Germany' in country:
                    suggestions['radio_suggestions'] = ['German stations', 'Classical music', 'News in German']
                    suggestions['language_suggestions'] = ['German']
                elif 'Kenya' in country:
                    suggestions['radio_suggestions'] = ['Kenyan stations', 'Swahili language', 'African music']
                    suggestions['language_suggestions'] = ['Swahili', 'English']
                elif 'United States' in country:
                    suggestions['radio_suggestions'] = ['US stations', 'Top 40', 'Country music']
                    suggestions['language_suggestions'] = ['English']
                elif 'United Kingdom' in country:
                    suggestions['radio_suggestions'] = ['BBC stations', 'British music', 'News']
                    suggestions['language_suggestions'] = ['English']
                else:
                    suggestions['radio_suggestions'] = ['International stations', 'Global music', 'News']
                    suggestions['language_suggestions'] = ['English']
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error getting location suggestions: {e}")
            return {'country': 'Unknown', 'city': 'Unknown', 'suggestions': []}
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and statistics"""
        return {
            'service_name': 'Hybrid Geolocation Service',
            'description': 'Combines IP-based and GPS geolocation with graceful fallbacks',
            'features': [
                'IP-based geolocation (immediate, no permission)',
                'GPS enhancement (high accuracy with permission)',
                'Multiple provider redundancy',
                'Intelligent fallback system',
                'Location-based suggestions'
            ],
            'ip_providers': len(self.ip_geolocation_services),
            'cache_size': {
                'ip_locations': len(self.ip_location_cache),
                'coordinates': len(self.coordinate_cache)
            },
            'accuracy_levels': ['gps', 'city', 'region', 'fallback'],
            'version': '1.0.0'
        }

# Create singleton instance
hybrid_geolocation_service = HybridGeolocationService()