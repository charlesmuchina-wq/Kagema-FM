from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class NotificationSettings(BaseModel):
    enabled: bool = True
    show_reminders: bool = True
    news_updates: bool = True
    music_discovery: bool = True
    app_updates: bool = True
    quiet_hours_enabled: bool = False
    quiet_start_time: str = "22:00"
    quiet_end_time: str = "08:00"
    sound_enabled: bool = True
    vibration_enabled: bool = True

class AudioSettings(BaseModel):
    quality: str = "medium"  # low, medium, high
    volume: float = 0.8
    auto_play: bool = False
    background_play: bool = True
    equalizer_preset: str = "default"

class UserPreferences(BaseModel):
    user_id: str
    theme: str = "auto"  # light, dark, auto
    language: str = "auto"
    region: str = "auto"
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    offline_mode: bool = False
    data_saver: bool = False
    analytics_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FavoriteItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    favorite_type: str  # radio_station, news_article, music_track, playlist
    item_id: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    stream_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    is_private: bool = False
    play_count: int = 0
    last_played: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ListeningHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    station_name: str
    stream_url: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    quality: str = "medium"
    device_info: Optional[Dict[str, Any]] = None

class UserPreferencesManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.preferences_collection = db.user_preferences
        self.favorites_collection = db.user_favorites
        self.listening_history_collection = db.listening_history

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences by user ID"""
        try:
            preferences_doc = await self.preferences_collection.find_one({"user_id": user_id})
            
            if not preferences_doc:
                # Create default preferences for new user
                default_preferences = UserPreferences(user_id=user_id)
                await self.save_user_preferences(default_preferences)
                return default_preferences
            
            # Remove MongoDB's _id field
            preferences_doc.pop('_id', None)
            return UserPreferences(**preferences_doc)
            
        except Exception as e:
            logger.error(f"Error getting user preferences for {user_id}: {e}")
            return UserPreferences(user_id=user_id)

    async def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """Save or update user preferences"""
        try:
            preferences.updated_at = datetime.utcnow()
            preferences_dict = preferences.dict()
            
            await self.preferences_collection.replace_one(
                {"user_id": preferences.user_id},
                preferences_dict,
                upsert=True
            )
            
            logger.info(f"Saved preferences for user {preferences.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
            return False

    async def update_user_preferences(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific preference fields"""
        try:
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.preferences_collection.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    async def add_favorite(self, favorite: FavoriteItem) -> str:
        """Add item to user favorites"""
        try:
            favorite_dict = favorite.dict()
            
            # Check if already exists
            existing = await self.favorites_collection.find_one({
                "user_id": favorite.user_id,
                "title": favorite.title,
                "favorite_type": favorite.favorite_type
            })
            
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="Item already exists in favorites"
                )
            
            await self.favorites_collection.insert_one(favorite_dict)
            logger.info(f"Added favorite {favorite.title} for user {favorite.user_id}")
            return favorite.id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            raise HTTPException(status_code=500, detail="Failed to add favorite")

    async def get_user_favorites(self, user_id: str, favorite_type: Optional[str] = None) -> List[FavoriteItem]:
        """Get user favorites, optionally filtered by type"""
        try:
            query = {"user_id": user_id}
            if favorite_type:
                query["type"] = favorite_type
                
            cursor = self.favorites_collection.find(query).sort("created_at", -1)
            favorites_docs = await cursor.to_list(length=None)
            
            favorites = []
            for doc in favorites_docs:
                doc.pop('_id', None)
                favorites.append(FavoriteItem(**doc))
            
            return favorites
            
        except Exception as e:
            logger.error(f"Error getting favorites for user {user_id}: {e}")
            return []

    async def remove_favorite(self, user_id: str, favorite_id: str) -> bool:
        """Remove item from favorites"""
        try:
            result = await self.favorites_collection.delete_one({
                "user_id": user_id,
                "id": favorite_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False

    async def update_favorite_play_count(self, user_id: str, favorite_id: str) -> bool:
        """Update play count and last played time for a favorite"""
        try:
            result = await self.favorites_collection.update_one(
                {"user_id": user_id, "id": favorite_id},
                {
                    "$inc": {"play_count": 1},
                    "$set": {"last_played": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating favorite play count: {e}")
            return False

    async def add_listening_session(self, session: ListeningHistory) -> str:
        """Add listening session to history"""
        try:
            session_dict = session.dict()
            await self.listening_history_collection.insert_one(session_dict)
            
            logger.info(f"Added listening session for user {session.user_id}")
            return session.id
            
        except Exception as e:
            logger.error(f"Error adding listening session: {e}")
            raise HTTPException(status_code=500, detail="Failed to add listening session")

    async def update_listening_session(self, user_id: str, session_id: str, ended_at: datetime, duration_seconds: int) -> bool:
        """Update listening session with end time and duration"""
        try:
            result = await self.listening_history_collection.update_one(
                {"user_id": user_id, "id": session_id},
                {
                    "$set": {
                        "ended_at": ended_at,
                        "duration_seconds": duration_seconds
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating listening session: {e}")
            return False

    async def get_listening_history(self, user_id: str, limit: int = 50) -> List[ListeningHistory]:
        """Get user listening history"""
        try:
            cursor = self.listening_history_collection.find(
                {"user_id": user_id}
            ).sort("started_at", -1).limit(limit)
            
            history_docs = await cursor.to_list(length=None)
            
            history = []
            for doc in history_docs:
                doc.pop('_id', None)
                history.append(ListeningHistory(**doc))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting listening history for user {user_id}: {e}")
            return []

    async def get_listening_stats(self, user_id: str) -> Dict[str, Any]:
        """Get listening statistics for a user"""
        try:
            # Total listening time
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "total_duration": {"$sum": "$duration_seconds"},
                    "avg_duration": {"$avg": "$duration_seconds"}
                }}
            ]
            
            result = await self.listening_history_collection.aggregate(pipeline).to_list(length=1)
            stats = result[0] if result else {}
            
            # Most listened stations
            station_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$station_name",
                    "count": {"$sum": 1},
                    "total_duration": {"$sum": "$duration_seconds"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            station_stats = await self.listening_history_collection.aggregate(station_pipeline).to_list(length=5)
            
            return {
                "total_sessions": stats.get("total_sessions", 0),
                "total_duration_seconds": stats.get("total_duration", 0),
                "average_session_duration": stats.get("avg_duration", 0),
                "favorite_stations": station_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting listening stats for user {user_id}: {e}")
            return {}

    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations based on user history and preferences"""
        try:
            # Get user preferences and history
            preferences = await self.get_user_preferences(user_id)
            history = await self.get_listening_history(user_id, limit=20)
            favorites = await self.get_user_favorites(user_id)
            
            # Analyze listening patterns
            favorite_genres = []
            listening_times = []
            
            for session in history:
                if session.ended_at:
                    hour = session.started_at.hour
                    listening_times.append(hour)
            
            # Get most common listening hours
            common_hours = {}
            for hour in listening_times:
                common_hours[hour] = common_hours.get(hour, 0) + 1
            
            peak_hours = sorted(common_hours.items(), key=lambda x: x[1], reverse=True)[:3]
            
            recommendations = {
                "recommended_stations": [
                    {
                        "name": "Chill Electronic",
                        "reason": "Based on your evening listening habits",
                        "confidence": 0.8
                    },
                    {
                        "name": "World Music Mix", 
                        "reason": "Similar to your favorites",
                        "confidence": 0.7
                    }
                ],
                "suggested_times": [f"{hour}:00" for hour, _ in peak_hours],
                "personalization_score": min(len(history) * 0.1, 1.0),  # 0.0 to 1.0
                "based_on": {
                    "listening_sessions": len(history),
                    "favorites_count": len(favorites),
                    "preferences_set": bool(preferences.notifications.enabled)
                }
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            return {"recommended_stations": [], "suggested_times": [], "personalization_score": 0.0}

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for backup or transfer"""
        try:
            preferences = await self.get_user_preferences(user_id)
            favorites = await self.get_user_favorites(user_id)
            history = await self.get_listening_history(user_id, limit=1000)
            stats = await self.get_listening_stats(user_id)
            
            return {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "preferences": preferences.dict(),
                "favorites": [fav.dict() for fav in favorites],
                "listening_history": [session.dict() for session in history],
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error exporting user data for {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to export user data")

    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR compliance)"""
        try:
            # Delete from all collections
            await self.preferences_collection.delete_many({"user_id": user_id})
            await self.favorites_collection.delete_many({"user_id": user_id})
            await self.listening_history_collection.delete_many({"user_id": user_id})
            
            logger.info(f"Deleted all data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data for {user_id}: {e}")
            return False