"""
Enhanced Geolocation Service with Multi-Tier Fallback Strategy
Implements best practices for radio station geolocation
"""

import json
import re
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedGeolocationService:
    """
    Multi-tier geolocation fallback system for radio stations
    
    Tier 1: Direct Geocoding (via existing service)
    Tier 2: Country Capital Fallback
    Tier 3: URL-Based Location Extraction
    Tier 4: Country Centroid Fallback
    """
    
    def __init__(self):
        # Load country capitals database
        capitals_path = Path(__file__).parent / 'country_capitals.json'
        with open(capitals_path, 'r') as f:
            self.country_capitals = json.load(f)
        
        # Common city name patterns in URLs
        self.city_patterns = self._build_city_patterns()
        
        logger.info("Enhanced Geolocation Service initialized with multi-tier fallback")
    
    def _build_city_patterns(self) -> Dict[str, Tuple[float, float]]:
        """Build dictionary of city names and their coordinates for URL parsing"""
        return {
            # Major US cities
            'newyork': (40.7128, -74.0060),
            'nyc': (40.7128, -74.0060),
            'losangeles': (34.0522, -118.2437),
            'la': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'houston': (29.7604, -95.3698),
            'phoenix': (33.4484, -112.0740),
            'philadelphia': (39.9526, -75.1652),
            'sanantonio': (29.4241, -98.4936),
            'sandiego': (32.7157, -117.1611),
            'dallas': (32.7767, -96.7970),
            'miami': (25.7617, -80.1918),
            'atlanta': (33.7490, -84.3880),
            'boston': (42.3601, -71.0589),
            'seattle': (47.6062, -122.3321),
            'denver': (39.7392, -104.9903),
            'lasvegas': (36.1699, -115.1398),
            'portland': (45.5152, -122.6784),
            'nashville': (36.1627, -86.7816),
            'detroit': (42.3314, -83.0458),
            
            # Major European cities
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'berlin': (52.5200, 13.4050),
            'madrid': (40.4168, -3.7038),
            'rome': (41.9028, 12.4964),
            'amsterdam': (52.3676, 4.9041),
            'vienna': (48.2082, 16.3738),
            'barcelona': (41.3851, 2.1734),
            'munich': (48.1351, 11.5820),
            'milan': (45.4642, 9.1900),
            'prague': (50.0755, 14.4378),
            'budapest': (47.4979, 19.0402),
            'warsaw': (52.2297, 21.0122),
            'brussels': (50.8503, 4.3517),
            'stockholm': (59.3293, 18.0686),
            'copenhagen': (55.6761, 12.5683),
            'oslo': (59.9139, 10.7522),
            'dublin': (53.3498, -6.2603),
            'lisbon': (38.7223, -9.1393),
            'athens': (37.9838, 23.7275),
            
            # Asian cities
            'tokyo': (35.6762, 139.6503),
            'beijing': (39.9042, 116.4074),
            'shanghai': (31.2304, 121.4737),
            'seoul': (37.5665, 126.9780),
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
            'bangkok': (13.7563, 100.5018),
            'singapore': (1.3521, 103.8198),
            'hongkong': (22.3193, 114.1694),
            'taipei': (25.0330, 121.5654),
            'manila': (14.5995, 120.9842),
            'jakarta': (6.2088, 106.8456),
            
            # Other major cities
            'sydney': (-33.8688, 151.2093),
            'melbourne': (-37.8136, 144.9631),
            'toronto': (43.6532, -79.3832),
            'vancouver': (49.2827, -123.1207),
            'montreal': (45.5017, -73.5673),
            'saopaulo': (-23.5505, -46.6333),
            'riodejaneiro': (-22.9068, -43.1729),
            'buenosaires': (-34.6037, -58.3816),
            'mexico': (19.4326, -99.1332),
            'lima': (-12.0464, -77.0428),
            'cairo': (30.0444, 31.2357),
            'johannesburg': (-26.2041, 28.0473),
            'lagos': (6.5244, 3.3792),
            'nairobi': (-1.2921, 36.8219),
            'moscow': (55.7558, 37.6173),
            'istanbul': (41.0082, 28.9784),
        }
    
    def get_coordinates_with_fallback(
        self,
        station: Dict[str, Any],
        direct_geocode_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get coordinates using multi-tier fallback strategy
        
        Args:
            station: Station dictionary with name, country, stream_url, etc.
            direct_geocode_result: Result from direct geocoding attempt (Tier 1)
        
        Returns:
            Dictionary with latitude, longitude, source, accuracy_level, and metadata
        """
        country_code = station.get('country', '').upper()
        
        # Tier 1: Direct Geocoding (already attempted)
        if direct_geocode_result and direct_geocode_result.get('latitude'):
            return {
                'latitude': direct_geocode_result['latitude'],
                'longitude': direct_geocode_result['longitude'],
                'source': 'direct_geocoding',
                'accuracy_level': 'high',
                'geocoded_address': direct_geocode_result.get('formatted_address', ''),
                'geocoded_at': datetime.utcnow().isoformat(),
                'fallback_tier': 1
            }
        
        # Tier 2: Country Capital Fallback
        if country_code in self.country_capitals:
            capital_data = self.country_capitals[country_code]
            logger.info(f"Using capital fallback for {station.get('name')}: {capital_data['capital']}")
            return {
                'latitude': capital_data['lat'],
                'longitude': capital_data['lon'],
                'source': 'country_capital',
                'accuracy_level': 'medium',
                'geocoded_address': f"{capital_data['capital']}, {country_code}",
                'geocoded_at': datetime.utcnow().isoformat(),
                'fallback_tier': 2,
                'note': f"Using {capital_data['capital']} coordinates as country fallback"
            }
        
        # Tier 3: URL-Based Location Extraction
        url_coords = self._extract_location_from_url(station.get('stream_url', ''))
        if url_coords:
            logger.info(f"Extracted location from URL for {station.get('name')}: {url_coords['city']}")
            return {
                'latitude': url_coords['lat'],
                'longitude': url_coords['lon'],
                'source': 'url_extraction',
                'accuracy_level': 'medium',
                'geocoded_address': f"{url_coords['city']}, {country_code}",
                'geocoded_at': datetime.utcnow().isoformat(),
                'fallback_tier': 3,
                'note': f"Location extracted from URL pattern: {url_coords['city']}"
            }
        
        # Tier 4: Country Centroid Fallback (geographic center)
        centroid = self._get_country_centroid(country_code)
        if centroid:
            logger.info(f"Using country centroid for {station.get('name')}: {country_code}")
            return {
                'latitude': centroid['lat'],
                'longitude': centroid['lon'],
                'source': 'country_centroid',
                'accuracy_level': 'low',
                'geocoded_address': f"Geographic center of {country_code}",
                'geocoded_at': datetime.utcnow().isoformat(),
                'fallback_tier': 4,
                'note': f"Using geographic center of {country_code} as last resort"
            }
        
        # No fallback available
        logger.warning(f"No geolocation fallback available for {station.get('name')}")
        return {
            'latitude': None,
            'longitude': None,
            'source': 'none',
            'accuracy_level': 'none',
            'geocoded_address': '',
            'geocoded_at': datetime.utcnow().isoformat(),
            'fallback_tier': 0,
            'error': 'No geolocation fallback available'
        }
    
    def _extract_location_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract city name from URL and return coordinates"""
        if not url:
            return None
        
        # Convert to lowercase and remove protocol
        url_clean = url.lower().replace('https://', '').replace('http://', '')
        
        # Check for city patterns
        for city, coords in self.city_patterns.items():
            if city in url_clean:
                return {
                    'city': city.capitalize(),
                    'lat': coords[0],
                    'lon': coords[1]
                }
        
        return None
    
    def _get_country_centroid(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get approximate geographic center of country"""
        # Approximate centroids for common countries
        # Note: These are simplified centroids, not exact geographic centers
        centroids = {
            'US': {'lat': 39.8283, 'lon': -98.5795},  # Continental US center
            'GB': {'lat': 54.7024, 'lon': -3.2766},
            'FR': {'lat': 46.2276, 'lon': 2.2137},
            'DE': {'lat': 51.1657, 'lon': 10.4515},
            'IT': {'lat': 41.8719, 'lon': 12.5674},
            'ES': {'lat': 40.4637, 'lon': -3.7492},
            'CA': {'lat': 56.1304, 'lon': -106.3468},
            'AU': {'lat': -25.2744, 'lon': 133.7751},
            'BR': {'lat': -14.2350, 'lon': -51.9253},
            'IN': {'lat': 20.5937, 'lon': 78.9629},
            'CN': {'lat': 35.8617, 'lon': 104.1954},
            'RU': {'lat': 61.5240, 'lon': 105.3188},
            'MX': {'lat': 23.6345, 'lon': -102.5528},
            'JP': {'lat': 36.2048, 'lon': 138.2529},
            'AR': {'lat': -38.4161, 'lon': -63.6167},
        }
        
        return centroids.get(country_code.upper())
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get statistics about available fallback options"""
        return {
            'country_capitals_available': len(self.country_capitals),
            'city_patterns_available': len(self.city_patterns),
            'country_centroids_available': 15,  # Hardcoded count
            'total_coverage_countries': len(self.country_capitals)
        }


# Singleton instance
_enhanced_geolocation_service = None

def get_enhanced_geolocation_service() -> EnhancedGeolocationService:
    """Get singleton instance of Enhanced Geolocation Service"""
    global _enhanced_geolocation_service
    if _enhanced_geolocation_service is None:
        _enhanced_geolocation_service = EnhancedGeolocationService()
    return _enhanced_geolocation_service
