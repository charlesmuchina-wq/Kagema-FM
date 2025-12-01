"""Division Geocoder
Automatically detects and assigns administrative divisions to radio stations
Uses geolocation, metadata parsing, and AI-powered detection
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import math

load_dotenv()

logger = logging.getLogger(__name__)


class DivisionGeocoder:
    """Automatically assigns administrative divisions to radio stations"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Stats
        self.stats = {
            'stations_processed': 0,
            'divisions_assigned': 0,
            'failed_assignments': 0
        }
        
        logger.info("Division Geocoder initialized")
    
    async def assign_division_to_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Assign administrative division to a station based on location"""
        try:
            country_code = station.get('country', '').upper()
            if not country_code or len(country_code) != 2:
                return {'status': 'no_country', 'station_id': station.get('id')}
            
            # Try multiple methods to detect division
            result = None
            
            # Method 1: Use lat/lon if available
            lat = station.get('lat') or station.get('metadata', {}).get('latitude')
            lon = station.get('lon') or station.get('metadata', {}).get('longitude')
            
            if lat and lon:
                result = await self._assign_by_coordinates(country_code, float(lat), float(lon))
            
            # Method 2: Parse station name/description for location hints
            if not result:
                station_name = station.get('name', '')
                description = station.get('description', '')
                result = await self._assign_by_name_parsing(country_code, station_name, description)
            
            # Method 3: Use homepage/URL parsing
            if not result:
                homepage = station.get('homepage', '')
                if homepage:
                    result = await self._assign_by_url_parsing(country_code, homepage)
            
            # Update station with division info
            if result:
                update_data = {
                    'division_level1_id': result.get('level1_id'),
                    'division_level1_name': result.get('level1_name'),
                    'division_level1_type': result.get('level1_type')
                }
                
                if result.get('level2_id'):
                    update_data.update({
                        'division_level2_id': result['level2_id'],
                        'division_level2_name': result['level2_name'],
                        'division_level2_type': result.get('level2_type')
                    })
                
                # Update in database
                await self.db.radio_stations.update_one(
                    {'_id': station['_id']},
                    {'$set': update_data}
                )
                
                self.stats['divisions_assigned'] += 1
                self.stats['stations_processed'] += 1
                
                return {
                    'status': 'success',
                    'station_id': station.get('id'),
                    'divisions': update_data
                }
            else:
                self.stats['failed_assignments'] += 1
                self.stats['stations_processed'] += 1
                return {
                    'status': 'no_division_found',
                    'station_id': station.get('id')
                }
        
        except Exception as e:
            logger.error(f"Error assigning division to station: {e}")
            self.stats['failed_assignments'] += 1
            return {
                'status': 'error',
                'station_id': station.get('id'),
                'error': str(e)
            }
    
    async def _assign_by_coordinates(self, country_code: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Assign division based on lat/lon coordinates"""
        try:
            # Get all divisions for this country with coordinates
            divisions = await self.db.administrative_divisions.find({
                'country_code': country_code,
                'lat': {'$exists': True},
                'lon': {'$exists': True}
            }).to_list(length=None)
            
            if not divisions:
                return None
            
            # Find closest division using Haversine distance
            closest_level1 = None
            closest_level2 = None
            min_distance_l1 = float('inf')
            min_distance_l2 = float('inf')
            
            for div in divisions:
                div_lat = div.get('lat')
                div_lon = div.get('lon')
                
                if div_lat is None or div_lon is None:
                    continue
                
                distance = self._haversine_distance(lat, lon, float(div_lat), float(div_lon))
                
                if div['level'] == 1 and distance < min_distance_l1:
                    min_distance_l1 = distance
                    closest_level1 = div
                elif div['level'] == 2 and distance < min_distance_l2:
                    min_distance_l2 = distance
                    closest_level2 = div
            
            if closest_level1:
                result = {
                    'level1_id': closest_level1['id'],
                    'level1_name': closest_level1['name'],
                    'level1_type': closest_level1.get('type', ''),
                    'method': 'coordinates',
                    'distance_km': round(min_distance_l1, 2)
                }
                
                if closest_level2:
                    result.update({
                        'level2_id': closest_level2['id'],
                        'level2_name': closest_level2['name'],
                        'level2_type': closest_level2.get('type', '')
                    })
                
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"Error in coordinate-based assignment: {e}")
            return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in km)"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def _assign_by_name_parsing(self, country_code: str, name: str, description: str) -> Optional[Dict[str, Any]]:
        """Assign division by parsing station name and description"""
        try:
            # Get all divisions for this country
            divisions = await self.db.administrative_divisions.find({
                'country_code': country_code
            }).to_list(length=None)
            
            if not divisions:
                return None
            
            # Combine name and description for searching
            search_text = f"{name} {description}".lower()
            
            # Try to find division name in the text
            best_match_l1 = None
            best_match_l2 = None
            max_score_l1 = 0
            max_score_l2 = 0
            
            for div in divisions:
                div_name = div['name'].lower()
                
                # Simple substring match with scoring
                if div_name in search_text:
                    score = len(div_name)  # Longer matches get higher scores
                    
                    if div['level'] == 1 and score > max_score_l1:
                        max_score_l1 = score
                        best_match_l1 = div
                    elif div['level'] == 2 and score > max_score_l2:
                        max_score_l2 = score
                        best_match_l2 = div
            
            if best_match_l1:
                result = {
                    'level1_id': best_match_l1['id'],
                    'level1_name': best_match_l1['name'],
                    'level1_type': best_match_l1.get('type', ''),
                    'method': 'name_parsing',
                    'confidence': min(max_score_l1 / 10, 1.0)  # Normalize confidence
                }
                
                if best_match_l2:
                    result.update({
                        'level2_id': best_match_l2['id'],
                        'level2_name': best_match_l2['name'],
                        'level2_type': best_match_l2.get('type', '')
                    })
                
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"Error in name-based assignment: {e}")
            return None
    
    async def _assign_by_url_parsing(self, country_code: str, url: str) -> Optional[Dict[str, Any]]:
        """Assign division by parsing homepage URL"""
        try:
            # Get all divisions for this country
            divisions = await self.db.administrative_divisions.find({
                'country_code': country_code
            }).to_list(length=None)
            
            if not divisions:
                return None
            
            url_lower = url.lower()
            
            # Try to find division name in URL
            for div in divisions:
                div_name = div['name'].lower().replace(' ', '')
                
                if div_name in url_lower.replace('-', '').replace('_', ''):
                    if div['level'] == 1:
                        return {
                            'level1_id': div['id'],
                            'level1_name': div['name'],
                            'level1_type': div.get('type', ''),
                            'method': 'url_parsing'
                        }
            
            return None
        
        except Exception as e:
            logger.error(f"Error in URL-based assignment: {e}")
            return None
    
    async def process_all_stations(self, batch_size: int = 100) -> Dict[str, Any]:
        """Process all stations and assign divisions"""
        logger.info("Starting division assignment for all stations")
        
        # Get all stations without division assignments
        stations = await self.db.radio_stations.find({
            '$or': [
                {'division_level1_id': {'$exists': False}},
                {'division_level1_id': None}
            ]
        }).to_list(length=None)
        
        total_stations = len(stations)
        logger.info(f"Found {total_stations} stations needing division assignment")
        
        # Process in batches
        for i in range(0, total_stations, batch_size):
            batch = stations[i:i + batch_size]
            
            for station in batch:
                await self.assign_division_to_station(station)
            
            if (i + batch_size) % 500 == 0:
                logger.info(f"Processed {i + batch_size}/{total_stations} stations")
            
            # Small delay to avoid overwhelming the system
            await asyncio.sleep(0.1)
        
        logger.info(f"Division assignment complete: {self.stats}")
        
        return {
            'status': 'success',
            'stats': self.stats,
            'total_processed': self.stats['stations_processed']
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get division geocoder statistics"""
        # Count stations with and without divisions
        with_divisions = await self.db.radio_stations.count_documents({
            'division_level1_id': {'$exists': True, '$ne': None}
        })
        
        without_divisions = await self.db.radio_stations.count_documents({
            '$or': [
                {'division_level1_id': {'$exists': False}},
                {'division_level1_id': None}
            ]
        })
        
        total = await self.db.radio_stations.count_documents({})
        
        return {
            'total_stations': total,
            'with_divisions': with_divisions,
            'without_divisions': without_divisions,
            'coverage_percentage': round((with_divisions / total * 100), 2) if total > 0 else 0,
            'processing_stats': self.stats
        }


# Global instance
division_geocoder_instance = None


def get_division_geocoder() -> DivisionGeocoder:
    """Get or create division geocoder instance"""
    global division_geocoder_instance
    if division_geocoder_instance is None:
        division_geocoder_instance = DivisionGeocoder()
    return division_geocoder_instance
