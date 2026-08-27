"""
Favorites Sharing & Import/Export for Dragon KARAU AI Radio
Advanced features for sharing and managing favorites
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import hashlib
from dotenv import load_dotenv
from pathlib import Path
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)


class FavoritesSharingManager:
    def __init__(self):
        self.mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        self.favorites_collection = self.db.user_favorites
        self.shared_collections = self.db.shared_favorites_collections
        self.stations_collection = self.db.radio_stations
        
    async def export_favorites(self, user_id: str, format: str = 'json') -> Dict[str, Any]:
        """Export user's favorites to JSON or M3U playlist format"""
        try:
            # Get all favorites
            favorites = await self.favorites_collection.find({
                'user_id': user_id
            }).to_list(length=1000)
            
            if not favorites:
                return {
                    'success': False,
                    'error': 'No favorites to export'
                }
            
            # Get complete station details
            station_ids = [fav['station_id'] for fav in favorites]
            stations = await self.stations_collection.find({
                'id': {'$in': station_ids}
            }).to_list(length=1000)
            
            station_map = {s['id']: s for s in stations}
            
            if format == 'json':
                # JSON export with metadata
                export_data = {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'user_id': user_id,
                    'total_favorites': len(favorites),
                    'favorites': []
                }
                
                for fav in favorites:
                    station = station_map.get(fav['station_id'])
                    if station:
                        export_data['favorites'].append({
                            'station_id': fav['station_id'],
                            'station_name': station.get('name'),
                            'call_sign': station.get('call_sign'),
                            'stream_url': station.get('stream_url'),
                            'country': station.get('country'),
                            'quality_score': station.get('quality_score'),
                            'added_at': fav.get('added_at'),
                            'play_count': fav.get('play_count', 0)
                        })
                
                return {
                    'success': True,
                    'format': 'json',
                    'data': export_data,
                    'filename': f'dragon_karau_favorites_{user_id}_{datetime.now().strftime("%Y%m%d")}.json'
                }
            
            elif format == 'm3u':
                # M3U playlist export
                m3u_content = "#EXTM3U\n"
                m3u_content += "# Dragon KARAU AI Radio - Favorites Playlist\n"
                m3u_content += f"# Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                m3u_content += f"# Total Stations: {len(favorites)}\n\n"
                
                for fav in favorites:
                    station = station_map.get(fav['station_id'])
                    if station and station.get('stream_url'):
                        station_name = station.get('standard_display_name') or station.get('name', 'Unknown')
                        m3u_content += f"#EXTINF:-1,{station_name} - {station.get('country', 'UNKNOWN')}\n"
                        m3u_content += f"{station.get('stream_url')}\n\n"
                
                return {
                    'success': True,
                    'format': 'm3u',
                    'data': m3u_content,
                    'filename': f'dragon_karau_favorites_{user_id}_{datetime.now().strftime("%Y%m%d")}.m3u'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format}'
                }
                
        except Exception as e:
            logger.error(f"Error exporting favorites: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def import_favorites(self, user_id: str, import_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import favorites from JSON export"""
        try:
            if not import_data.get('favorites'):
                return {
                    'success': False,
                    'error': 'Invalid import data'
                }
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for fav_data in import_data['favorites']:
                station_id = fav_data.get('station_id')
                
                if not station_id:
                    skipped_count += 1
                    continue
                
                # Check if station exists
                station = await self.stations_collection.find_one({'id': station_id})
                if not station:
                    errors.append(f"Station not found: {fav_data.get('station_name', station_id)}")
                    skipped_count += 1
                    continue
                
                # Check if already favorited
                existing = await self.favorites_collection.find_one({
                    'user_id': user_id,
                    'station_id': station_id
                })
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Import favorite
                favorite_doc = {
                    'user_id': user_id,
                    'station_id': station_id,
                    'station_name': station.get('name'),
                    'station_country': station.get('country'),
                    'station_call_sign': station.get('call_sign'),
                    'added_at': datetime.now().isoformat(),
                    'last_played': None,
                    'play_count': 0,
                    'imported': True,
                    'original_added_at': fav_data.get('added_at')
                }
                
                await self.favorites_collection.insert_one(favorite_doc)
                imported_count += 1
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'errors': errors,
                'message': f'Imported {imported_count} favorites, skipped {skipped_count}'
            }
            
        except Exception as e:
            logger.error(f"Error importing favorites: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_shared_collection(
        self, 
        user_id: str, 
        title: str, 
        description: Optional[str] = None,
        station_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a shareable collection of favorite stations"""
        try:
            # If no station_ids provided, use all user's favorites
            if not station_ids:
                favorites = await self.favorites_collection.find({
                    'user_id': user_id
                }).to_list(length=1000)
                station_ids = [fav['station_id'] for fav in favorites]
            
            if not station_ids:
                return {
                    'success': False,
                    'error': 'No stations to share'
                }
            
            # Generate unique share code
            share_code = hashlib.md5(
                f"{user_id}{title}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Create shared collection
            collection_doc = {
                'share_code': share_code,
                'owner_user_id': user_id,
                'title': title,
                'description': description,
                'station_ids': station_ids,
                'station_count': len(station_ids),
                'created_at': datetime.now().isoformat(),
                'views': 0,
                'imports': 0,
                'is_public': True
            }
            
            await self.shared_collections.insert_one(collection_doc)
            
            return {
                'success': True,
                'share_code': share_code,
                'share_url': f'/shared/{share_code}',
                'message': 'Collection created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating shared collection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_shared_collection(self, share_code: str) -> Dict[str, Any]:
        """Get details of a shared collection"""
        try:
            collection = await self.shared_collections.find_one({
                'share_code': share_code
            })
            
            if not collection:
                return {
                    'success': False,
                    'error': 'Collection not found'
                }
            
            # Increment view count
            await self.shared_collections.update_one(
                {'share_code': share_code},
                {'$inc': {'views': 1}}
            )
            
            # Get station details
            stations = await self.stations_collection.find({
                'id': {'$in': collection['station_ids']}
            }).to_list(length=1000)
            
            return {
                'success': True,
                'collection': {
                    'share_code': share_code,
                    'title': collection['title'],
                    'description': collection['description'],
                    'station_count': collection['station_count'],
                    'created_at': collection['created_at'],
                    'views': collection['views'] + 1,
                    'imports': collection['imports'],
                    'stations': [{
                        'id': s.get('id'),
                        'name': s.get('name'),
                        'call_sign': s.get('call_sign'),
                        'standard_display_name': s.get('standard_display_name'),
                        'stream_url': s.get('stream_url'),
                        'country': s.get('country'),
                        'quality_score': s.get('quality_score', 0)
                    } for s in stations]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting shared collection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def import_shared_collection(self, user_id: str, share_code: str) -> Dict[str, Any]:
        """Import stations from a shared collection"""
        try:
            collection = await self.shared_collections.find_one({
                'share_code': share_code
            })
            
            if not collection:
                return {
                    'success': False,
                    'error': 'Collection not found'
                }
            
            # Increment import count
            await self.shared_collections.update_one(
                {'share_code': share_code},
                {'$inc': {'imports': 1}}
            )
            
            imported_count = 0
            skipped_count = 0
            
            for station_id in collection['station_ids']:
                # Check if already favorited
                existing = await self.favorites_collection.find_one({
                    'user_id': user_id,
                    'station_id': station_id
                })
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Get station details
                station = await self.stations_collection.find_one({'id': station_id})
                if not station:
                    skipped_count += 1
                    continue
                
                # Add to favorites
                favorite_doc = {
                    'user_id': user_id,
                    'station_id': station_id,
                    'station_name': station.get('name'),
                    'station_country': station.get('country'),
                    'station_call_sign': station.get('call_sign'),
                    'added_at': datetime.now().isoformat(),
                    'last_played': None,
                    'play_count': 0,
                    'imported_from_share': share_code
                }
                
                await self.favorites_collection.insert_one(favorite_doc)
                imported_count += 1
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'message': f'Imported {imported_count} stations from "{collection["title"]}"'
            }
            
        except Exception as e:
            logger.error(f"Error importing shared collection: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_sharing_manager = None

def get_sharing_manager() -> FavoritesSharingManager:
    """Get singleton instance of FavoritesSharingManager"""
    global _sharing_manager
    if _sharing_manager is None:
        _sharing_manager = FavoritesSharingManager()
    return _sharing_manager
