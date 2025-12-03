"""
Station Metadata Enrichment Service
Adds genres, languages, logos, bitrate, and descriptions to stations
"""
import asyncio
import os
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class StationMetadataEnrichment:
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.client = None
        self.db = None
        
        # Common radio genres
        self.genre_keywords = {
            'news': ['news', 'information', 'talk', 'actualite'],
            'music': ['music', 'hits', 'top', 'chart'],
            'rock': ['rock', 'metal', 'alternative'],
            'pop': ['pop', 'popular', 'hit'],
            'classical': ['classical', 'classic', 'symphony'],
            'jazz': ['jazz', 'blues', 'swing'],
            'electronic': ['electronic', 'edm', 'techno', 'house'],
            'country': ['country', 'folk', 'bluegrass'],
            'hip-hop': ['hip hop', 'rap', 'urban'],
            'latin': ['latin', 'salsa', 'reggaeton'],
            'religious': ['christian', 'gospel', 'religious', 'catholic'],
            'sports': ['sports', 'sport', 'football', 'soccer'],
            'variety': ['variety', 'mix', 'general']
        }
        
        # Language detection keywords
        self.language_keywords = {
            'en': ['english', 'uk', 'us', 'usa', 'gb', 'au', 'nz', 'ca'],
            'es': ['spanish', 'español', 'spain', 'mexico', 'argentina'],
            'fr': ['french', 'français', 'france', 'quebec'],
            'de': ['german', 'deutsch', 'germany', 'austria'],
            'it': ['italian', 'italiano', 'italy'],
            'pt': ['portuguese', 'português', 'brazil', 'portugal'],
            'ru': ['russian', 'русский', 'russia'],
            'ar': ['arabic', 'العربية', 'arab'],
            'zh': ['chinese', '中文', 'china'],
            'ja': ['japanese', '日本語', 'japan']
        }
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info("✅ Connected to MongoDB for metadata enrichment")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            
    def detect_genre(self, station_name: str, description: str = '') -> List[str]:
        """Detect genre(s) from station name and description"""
        text = f"{station_name} {description}".lower()
        detected_genres = []
        
        for genre, keywords in self.genre_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_genres.append(genre)
        
        # Default to variety if no genre detected
        if not detected_genres:
            detected_genres = ['variety']
            
        return detected_genres[:3]  # Return max 3 genres
    
    def detect_language(self, station_name: str, country: str = '') -> str:
        """Detect primary language from station name and country"""
        text = f"{station_name} {country}".lower()
        
        for lang, keywords in self.language_keywords.items():
            if any(keyword in text for keyword in keywords):
                return lang
        
        # Country-based fallback
        country_lang_map = {
            'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en', 'NZ': 'en', 'IE': 'en',
            'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es', 'CL': 'es',
            'FR': 'fr', 'BE': 'fr', 'CH': 'fr',
            'DE': 'de', 'AT': 'de',
            'IT': 'it',
            'BR': 'pt', 'PT': 'pt',
            'RU': 'ru', 'UA': 'ru',
            'SA': 'ar', 'AE': 'ar', 'EG': 'ar',
            'CN': 'zh', 'TW': 'zh',
            'JP': 'ja'
        }
        
        return country_lang_map.get(country.upper(), 'en')  # Default to English
    
    def estimate_bitrate(self, stream_url: str) -> Optional[int]:
        """Estimate bitrate from stream URL patterns"""
        url_lower = stream_url.lower()
        
        # Common bitrate indicators in URLs
        if '320' in url_lower or 'high' in url_lower:
            return 320
        elif '256' in url_lower:
            return 256
        elif '192' in url_lower:
            return 192
        elif '128' in url_lower or 'medium' in url_lower:
            return 128
        elif '96' in url_lower:
            return 96
        elif '64' in url_lower or 'low' in url_lower:
            return 64
        
        # Default medium quality
        return 128
    
    def generate_description(self, station_name: str, country: str, genres: List[str]) -> str:
        """Generate a basic description for the station"""
        genre_text = ', '.join(genres) if genres else 'variety'
        return f"{station_name} is a {genre_text} radio station broadcasting from {country or 'worldwide'}."
    
    async def enrich_station_metadata(self, station_id: str) -> Dict[str, Any]:
        """Enrich a single station with metadata"""
        try:
            station = await self.db.radio_stations.find_one({'_id': station_id})
            if not station:
                return {'status': 'error', 'message': 'Station not found'}
            
            name = station.get('name', '')
            country = station.get('country', '')
            stream_url = station.get('stream_url', '')
            
            # Detect metadata
            genres = self.detect_genre(name)
            language = self.detect_language(name, country)
            bitrate = self.estimate_bitrate(stream_url)
            description = self.generate_description(name, country, genres)
            
            # Update station
            update_data = {
                'genres': genres,
                'language': language,
                'bitrate_kbps': bitrate,
                'description': description,
                'metadata_enriched': True,
                'metadata_updated_at': datetime.utcnow()
            }
            
            await self.db.radio_stations.update_one(
                {'_id': station_id},
                {'$set': update_data}
            )
            
            return {
                'status': 'success',
                'station_name': name,
                'enriched': update_data
            }
            
        except Exception as e:
            logger.error(f"Error enriching station {station_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def enrich_batch(self, limit: int = 100) -> Dict[str, Any]:
        """Enrich a batch of stations without metadata"""
        try:
            # Find stations without metadata enrichment
            cursor = self.db.radio_stations.find(
                {
                    '$or': [
                        {'metadata_enriched': {'$ne': True}},
                        {'metadata_enriched': {'$exists': False}}
                    ]
                }
            ).limit(limit)
            
            enriched_count = 0
            failed_count = 0
            
            async for station in cursor:
                result = await self.enrich_station_metadata(station['_id'])
                if result['status'] == 'success':
                    enriched_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"✅ Enriched {enriched_count} stations with metadata")
            
            return {
                'status': 'success',
                'enriched': enriched_count,
                'failed': failed_count,
                'total_processed': enriched_count + failed_count
            }
            
        except Exception as e:
            logger.error(f"Error in batch enrichment: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get metadata enrichment statistics"""
        try:
            total = await self.db.radio_stations.count_documents({})
            enriched = await self.db.radio_stations.count_documents({
                'metadata_enriched': True
            })
            
            # Genre distribution
            genres_pipeline = [
                {'$unwind': '$genres'},
                {'$group': {'_id': '$genres', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            top_genres = await self.db.radio_stations.aggregate(genres_pipeline).to_list(length=10)
            
            # Language distribution
            languages_pipeline = [
                {'$group': {'_id': '$language', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            top_languages = await self.db.radio_stations.aggregate(languages_pipeline).to_list(length=10)
            
            return {
                'total_stations': total,
                'enriched': enriched,
                'not_enriched': total - enriched,
                'percentage': round((enriched / total * 100), 2) if total > 0 else 0,
                'top_genres': top_genres,
                'top_languages': top_languages
            }
            
        except Exception as e:
            logger.error(f"Error getting enrichment stats: {e}")
            return {'error': str(e)}

# Singleton instance
_enrichment_service = None

def get_enrichment_service():
    """Get singleton instance of enrichment service"""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = StationMetadataEnrichment()
    return _enrichment_service
