"""
Station Geocoding Service
Automatically add latitude/longitude coordinates to radio stations
Integrates with Geoapify Geocoding API
"""

import asyncio
import aiohttp
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

logger = logging.getLogger(__name__)


class StationGeocodingService:
    """Service to add geographic coordinates to radio stations"""
    
    def __init__(self):
        self.geoapify_key = os.getenv('GEOAPIFY_GEOCODING_KEY', '')
        self.base_url = "https://api.geoapify.com/v1/geocode/search"
        
        # MongoDB connection
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Rate limiting
        self.max_requests_per_second = 5
        self.delay_between_requests = 1.0 / self.max_requests_per_second
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful_geocodes': 0,
            'failed_geocodes': 0,
            'already_geocoded': 0,
            'coordinates_added': 0
        }
        
        logger.info("Station Geocoding Service initialized")
    
    async def geocode_station(self, station: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Geocode a single station using available location information
        Returns: {'latitude': float, 'longitude': float} or None
        """
        try:
            # Build search query from station information
            search_parts = []
            
            # Priority 1: Use address if available
            if station.get('address'):
                search_parts.append(station['address'])
            
            # Priority 2: Use name + country
            if station.get('name'):
                search_parts.append(station['name'])
            
            # Priority 3: Add country
            if station.get('country'):
                search_parts.append(station['country'])
            
            # Priority 4: Add city/state if available
            if station.get('division_level1'):  # State/Region
                search_parts.append(station['division_level1'])
            if station.get('division_level2'):  # City
                search_parts.append(station['division_level2'])
            
            if not search_parts:
                logger.warning(f"No location data for station {station.get('id')}")
                return None
            
            # Create search query
            search_query = ', '.join(filter(None, search_parts))
            
            # Call Geoapify API
            params = {
                'text': search_query,
                'apiKey': self.geoapify_key,
                'limit': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'features' in data and len(data['features']) > 0:
                            feature = data['features'][0]
                            coords = feature['geometry']['coordinates']
                            
                            # Geoapify returns [longitude, latitude]
                            return {
                                'latitude': coords[1],
                                'longitude': coords[0],
                                'formatted_address': feature['properties'].get('formatted', ''),
                                'geocoded_at': datetime.utcnow().isoformat()
                            }
                    else:
                        logger.error(f"Geocoding API error: {response.status}")
                        return None
            
            # Rate limiting
            await asyncio.sleep(self.delay_between_requests)
            
        except Exception as e:
            logger.error(f"Geocoding error for station {station.get('id')}: {e}")
            return None
    
    async def geocode_stations_batch(
        self, 
        limit: int = 100,
        skip_geocoded: bool = True
    ) -> Dict[str, Any]:
        """
        Geocode a batch of stations from the database
        
        Args:
            limit: Maximum number of stations to process
            skip_geocoded: Skip stations that already have coordinates
        """
        logger.info(f"Starting batch geocoding (limit: {limit})")
        
        try:
            # Build query
            query = {}
            if skip_geocoded:
                query = {
                    '$or': [
                        {'latitude': {'$exists': False}},
                        {'longitude': {'$exists': False}},
                        {'latitude': None},
                        {'longitude': None}
                    ]
                }
            
            # Get stations needing geocoding
            stations_cursor = self.db.radio_stations.find(query).limit(limit)
            stations = await stations_cursor.to_list(length=limit)
            
            logger.info(f"Found {len(stations)} stations to geocode")
            
            # Process each station
            for station in stations:
                self.stats['total_processed'] += 1
                
                # Check if already has coordinates
                if station.get('latitude') and station.get('longitude'):
                    self.stats['already_geocoded'] += 1
                    continue
                
                # Geocode
                coords = await self.geocode_station(station)
                
                if coords:
                    # Update database
                    update_result = await self.db.radio_stations.update_one(
                        {'_id': station['_id']},
                        {
                            '$set': {
                                'latitude': coords['latitude'],
                                'longitude': coords['longitude'],
                                'formatted_address': coords.get('formatted_address'),
                                'geocoded_at': coords['geocoded_at']
                            }
                        }
                    )
                    
                    if update_result.modified_count > 0:
                        self.stats['successful_geocodes'] += 1
                        self.stats['coordinates_added'] += 1
                        logger.info(
                            f"✅ Geocoded: {station.get('name')} - "
                            f"({coords['latitude']}, {coords['longitude']})"
                        )
                else:
                    self.stats['failed_geocodes'] += 1
                    logger.warning(f"❌ Failed to geocode: {station.get('name')}")
            
            return {
                'status': 'success',
                'stats': self.stats,
                'message': f"Processed {self.stats['total_processed']} stations"
            }
            
        except Exception as e:
            logger.error(f"Batch geocoding error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'stats': self.stats
            }
    
    async def geocode_all_stations(
        self,
        batch_size: int = 100,
        max_batches: int = 200
    ) -> Dict[str, Any]:
        """
        Geocode all stations in the database in batches
        
        Args:
            batch_size: Stations per batch
            max_batches: Maximum number of batches to process
        """
        logger.info(f"Starting full database geocoding (batch_size: {batch_size})")
        
        total_stats = {
            'batches_processed': 0,
            'total_geocoded': 0,
            'total_failed': 0,
            'started_at': datetime.utcnow().isoformat()
        }
        
        try:
            for batch_num in range(max_batches):
                logger.info(f"Processing batch {batch_num + 1}/{max_batches}")
                
                # Geocode batch
                result = await self.geocode_stations_batch(
                    limit=batch_size,
                    skip_geocoded=True
                )
                
                if result['status'] == 'success':
                    total_stats['batches_processed'] += 1
                    total_stats['total_geocoded'] += result['stats']['successful_geocodes']
                    total_stats['total_failed'] += result['stats']['failed_geocodes']
                
                # Check if we're done
                remaining = await self.db.radio_stations.count_documents({
                    '$or': [
                        {'latitude': {'$exists': False}},
                        {'longitude': {'$exists': False}},
                        {'latitude': None},
                        {'longitude': None}
                    ]
                })
                
                logger.info(f"Stations remaining without coordinates: {remaining}")
                
                if remaining == 0:
                    logger.info("✅ All stations geocoded!")
                    break
                
                # Delay between batches
                await asyncio.sleep(2)
            
            total_stats['completed_at'] = datetime.utcnow().isoformat()
            
            return {
                'status': 'success',
                'stats': total_stats,
                'message': f"Geocoding complete: {total_stats['total_geocoded']} stations updated"
            }
            
        except Exception as e:
            logger.error(f"Full geocoding error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'stats': total_stats
            }
    
    async def get_geocoding_stats(self) -> Dict[str, Any]:
        """Get statistics about geocoded stations"""
        try:
            total_stations = await self.db.radio_stations.count_documents({})
            
            geocoded_stations = await self.db.radio_stations.count_documents({
                'latitude': {'$exists': True, '$ne': None},
                'longitude': {'$exists': True, '$ne': None}
            })
            
            not_geocoded = total_stations - geocoded_stations
            percentage_geocoded = (geocoded_stations / total_stations * 100) if total_stations > 0 else 0
            
            return {
                'status': 'success',
                'stats': {
                    'total_stations': total_stations,
                    'geocoded': geocoded_stations,
                    'not_geocoded': not_geocoded,
                    'percentage_geocoded': round(percentage_geocoded, 2),
                    'api_configured': bool(self.geoapify_key)
                }
            }
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Singleton instance
_geocoding_service = None

def get_geocoding_service() -> StationGeocodingService:
    """Get singleton instance of StationGeocodingService"""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = StationGeocodingService()
    return _geocoding_service
