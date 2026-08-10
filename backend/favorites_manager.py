"""
Favorites Manager for Dragon KARAU AI Radio
Handles user favorite stations with MongoDB storage
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)


class FavoritesManager:
    def __init__(self):
        self.mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        self.favorites_collection = self.db.user_favorites
        self.stations_collection = self.db.radio_stations
        
    async def add_favorite(self, user_id: str, station_id: str) -> Dict[str, Any]:
        """Add a station to user's favorites"""
        try:
            # Check if station exists
            station = await self.stations_collection.find_one({'id': station_id})
            if not station:
                return {
                    'success': False,
                    'error': 'Station not found'
                }
            
            # Check if already favorited
            existing = await self.favorites_collection.find_one({
                'user_id': user_id,
                'station_id': station_id
            })
            
            if existing:
                return {
                    'success': True,
                    'message': 'Station already in favorites',
                    'already_exists': True
                }
            
            # Add to favorites
            favorite_doc = {
                'user_id': user_id,
                'station_id': station_id,
                'station_name': station.get('name'),
                'station_country': station.get('country'),
                'station_call_sign': station.get('call_sign'),
                'added_at': datetime.now().isoformat(),
                'last_played': None,
                'play_count': 0
            }
            
            await self.favorites_collection.insert_one(favorite_doc)
            
            return {
                'success': True,
                'message': 'Station added to favorites',
                'favorite_id': str(favorite_doc['_id'])
            }
            
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def remove_favorite(self, user_id: str, station_id: str) -> Dict[str, Any]:
        """Remove a station from user's favorites"""
        try:
            result = await self.favorites_collection.delete_one({
                'user_id': user_id,
                'station_id': station_id
            })
            
            if result.deleted_count == 0:
                return {
                    'success': False,
                    'error': 'Favorite not found'
                }
            
            return {
                'success': True,
                'message': 'Station removed from favorites'
            }
            
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_favorites(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get all favorite stations for a user"""
        try:
            favorites = await self.favorites_collection.find({
                'user_id': user_id
            }).sort('added_at', -1).limit(limit).to_list(length=limit)
            
            # Fetch complete station details for each favorite
            favorite_stations = []
            for fav in favorites:
                station = await self.stations_collection.find_one({'id': fav['station_id']})
                if station:
                    favorite_stations.append({
                        'id': station.get('id'),
                        'name': station.get('name'),
                        'call_sign': station.get('call_sign'),
                        'standard_display_name': station.get('standard_display_name'),
                        'stream_url': station.get('stream_url'),
                        'country': station.get('country'),
                        'quality_score': station.get('quality_score', 0),
                        'division_level1': station.get('division_level1_name'),
                        'division_level2': station.get('division_level2_name'),
                        'added_at': fav.get('added_at'),
                        'play_count': fav.get('play_count', 0),
                        'last_played': fav.get('last_played')
                    })
            
            return {
                'success': True,
                'favorites': favorite_stations,
                'total_count': len(favorite_stations)
            }
            
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return {
                'success': False,
                'error': str(e),
                'favorites': [],
                'total_count': 0
            }
    
    async def is_favorited(self, user_id: str, station_id: str) -> bool:
        """Check if a station is in user's favorites"""
        try:
            count = await self.favorites_collection.count_documents({
                'user_id': user_id,
                'station_id': station_id
            })
            return count > 0
        except Exception as e:
            logger.error(f"Error checking favorite status: {e}")
            return False
    
    async def update_play_stats(self, user_id: str, station_id: str) -> Dict[str, Any]:
        """Update play count and last played timestamp for a favorite station"""
        try:
            result = await self.favorites_collection.update_one(
                {
                    'user_id': user_id,
                    'station_id': station_id
                },
                {
                    '$inc': {'play_count': 1},
                    '$set': {'last_played': datetime.now().isoformat()}
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Play stats updated'
                }
            else:
                return {
                    'success': False,
                    'message': 'Station not in favorites'
                }
                
        except Exception as e:
            logger.error(f"Error updating play stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's favorites"""
        try:
            total_favorites = await self.favorites_collection.count_documents({'user_id': user_id})
            
            # Get country breakdown
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': '$station_country',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            
            country_breakdown = []
            async for doc in self.favorites_collection.aggregate(pipeline):
                country_breakdown.append({
                    'country': doc['_id'],
                    'count': doc['count']
                })
            
            # Get most played
            most_played = await self.favorites_collection.find({
                'user_id': user_id,
                'play_count': {'$gt': 0}
            }).sort('play_count', -1).limit(5).to_list(length=5)
            
            return {
                'success': True,
                'stats': {
                    'total_favorites': total_favorites,
                    'countries_represented': len(country_breakdown),
                    'country_breakdown': country_breakdown,
                    'most_played_count': len(most_played),
                    'most_played_stations': [
                        {
                            'station_id': fav['station_id'],
                            'station_name': fav['station_name'],
                            'play_count': fav['play_count']
                        } for fav in most_played
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting favorite stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_favorites_manager = None

def get_favorites_manager() -> FavoritesManager:
    """Get singleton instance of FavoritesManager"""
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager()
    return _favorites_manager
