"""
Stream Validation Service
Tests radio stream URLs, detects broken streams, and maintains stream health
"""
import asyncio
import os
import logging
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StreamValidationService:
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.client = None
        self.db = None
        
        # Validation settings - increased for better reliability
        self.timeout = 15  # seconds (increased from 10)
        self.retry_attempts = 3  # increased from 2
        self.chunk_size = 4096  # bytes to test stream (reduced for faster tests)
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info("✅ Connected to MongoDB for stream validation")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    async def validate_stream_url(self, stream_url: str) -> Dict[str, Any]:
        """
        Validate a single stream URL
        Returns stream status, response time, content type, etc.
        """
        result = {
            'url': stream_url,
            'status': 'unknown',
            'is_valid': False,
            'response_time_ms': None,
            'content_type': None,
            'error': None,
            'tested_at': datetime.utcnow()
        }
        
        for attempt in range(self.retry_attempts):
            try:
                start_time = datetime.utcnow()
                
                # Add User-Agent header to avoid blocking
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; DragonKARAU-AI/1.0; +https://dragon-karau.com)'
                }
                
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(
                        stream_url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        allow_redirects=True
                    ) as response:
                        # Calculate response time
                        end_time = datetime.utcnow()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        
                        # Get content type
                        content_type = response.headers.get('Content-Type', '')
                        
                        # Check if it's a valid audio stream
                        valid_audio_types = [
                            'audio/', 'application/ogg', 'application/x-mpegurl',
                            'application/vnd.apple.mpegurl', 'video/mp2t'
                        ]
                        is_audio_stream = any(
                            audio_type in content_type.lower() 
                            for audio_type in valid_audio_types
                        )
                        
                        # Try to read a small chunk to ensure stream is active
                        try:
                            chunk = await response.content.read(self.chunk_size)
                            has_data = len(chunk) > 0
                        except Exception:
                            has_data = False
                        
                        # Determine status
                        if response.status == 200 and (is_audio_stream or has_data):
                            result.update({
                                'status': 'online',
                                'is_valid': True,
                                'response_time_ms': round(response_time, 2),
                                'content_type': content_type,
                                'http_status': response.status
                            })
                            return result
                        else:
                            result.update({
                                'status': 'error',
                                'error': f'Invalid response: HTTP {response.status}',
                                'http_status': response.status,
                                'content_type': content_type
                            })
                            
            except asyncio.TimeoutError:
                result.update({
                    'status': 'timeout',
                    'error': 'Connection timeout'
                })
            except Exception as e:
                result.update({
                    'status': 'error',
                    'error': str(e)[:200]
                })
            
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(1)
        
        return result
    
    async def validate_station(self, station_id: str) -> Dict[str, Any]:
        """Validate a station's stream and update database"""
        try:
            station = await self.db.radio_stations.find_one({'_id': station_id})
            if not station:
                return {'status': 'error', 'message': 'Station not found'}
            
            stream_url = station.get('stream_url', '')
            if not stream_url:
                return {'status': 'error', 'message': 'No stream URL'}
            
            # Validate stream
            validation_result = await self.validate_stream_url(stream_url)
            
            # Update station with validation results
            update_data = {
                'stream_status': validation_result['status'],
                'stream_is_valid': validation_result['is_valid'],
                'stream_last_checked': validation_result['tested_at'],
                'stream_content_type': validation_result.get('content_type'),
                'stream_response_time_ms': validation_result.get('response_time_ms')
            }
            
            # FIXED: Separate operations to avoid conflict
            # First, update the stream status fields
            await self.db.radio_stations.update_one(
                {'_id': station_id},
                {'$set': update_data}
            )
            
            # Then, push to validation history (separate operation)
            await self.db.radio_stations.update_one(
                {'_id': station_id},
                {
                    '$push': {
                        'stream_validation_history': {
                            '$each': [validation_result],
                            '$slice': -10  # Keep last 10 validations
                        }
                    }
                }
            )
            
            return {
                'status': 'success',
                'station_name': station.get('name'),
                'validation': validation_result
            }
            
        except Exception as e:
            logger.error(f"Error validating station {station_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def validate_batch(self, limit: int = 50) -> Dict[str, Any]:
        """Validate a batch of stations"""
        try:
            # Priority order:
            # 1. Stations never validated
            # 2. Stations with failed last validation
            # 3. Stations not checked in last 7 days
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            # Find stations to validate
            query = {
                '$or': [
                    {'stream_last_checked': {'$exists': False}},
                    {'stream_is_valid': False},
                    {'stream_last_checked': {'$lt': week_ago}}
                ]
            }
            
            cursor = self.db.radio_stations.find(query).limit(limit)
            
            online_count = 0
            offline_count = 0
            error_count = 0
            
            async for station in cursor:
                result = await self.validate_station(station['_id'])
                
                if result['status'] == 'success':
                    validation = result['validation']
                    if validation['status'] == 'online':
                        online_count += 1
                    elif validation['status'] in ['timeout', 'error']:
                        offline_count += 1
                else:
                    error_count += 1
                
                # Small delay to avoid overwhelming servers
                await asyncio.sleep(0.5)
            
            logger.info(f"✅ Validated {online_count + offline_count + error_count} streams: "
                       f"{online_count} online, {offline_count} offline, {error_count} errors")
            
            return {
                'status': 'success',
                'validated': online_count + offline_count + error_count,
                'online': online_count,
                'offline': offline_count,
                'errors': error_count
            }
            
        except Exception as e:
            logger.error(f"Error in batch validation: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get stream validation statistics"""
        try:
            total = await self.db.radio_stations.count_documents({})
            
            # Validated stations
            validated = await self.db.radio_stations.count_documents({
                'stream_last_checked': {'$exists': True}
            })
            
            # Online streams
            online = await self.db.radio_stations.count_documents({
                'stream_status': 'online',
                'stream_is_valid': True
            })
            
            # Offline streams
            offline = await self.db.radio_stations.count_documents({
                '$or': [
                    {'stream_status': 'timeout'},
                    {'stream_status': 'error'},
                    {'stream_is_valid': False}
                ]
            })
            
            # Never validated
            never_validated = await self.db.radio_stations.count_documents({
                'stream_last_checked': {'$exists': False}
            })
            
            # Needs revalidation (>7 days old)
            week_ago = datetime.utcnow() - timedelta(days=7)
            needs_revalidation = await self.db.radio_stations.count_documents({
                'stream_last_checked': {'$lt': week_ago}
            })
            
            return {
                'total_stations': total,
                'validated': validated,
                'never_validated': never_validated,
                'online': online,
                'offline': offline,
                'needs_revalidation': needs_revalidation,
                'validation_percentage': round((validated / total * 100), 2) if total > 0 else 0,
                'uptime_percentage': round((online / validated * 100), 2) if validated > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting validation stats: {e}")
            return {'error': str(e)}

# Singleton instance
_validation_service = None

def get_validation_service():
    """Get singleton instance of validation service"""
    global _validation_service
    if _validation_service is None:
        _validation_service = StreamValidationService()
    return _validation_service
