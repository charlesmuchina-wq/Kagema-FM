import aiofiles
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import sqlite3
import gzip
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)

@dataclass
class CachedContent:
    content_id: str
    content_type: str
    data: Dict[str, Any]
    cached_at: datetime
    expires_at: Optional[datetime]
    size_bytes: int
    access_count: int
    last_accessed: datetime

class OfflineContentManager:
    def __init__(self, cache_dir: str = "/tmp/kagema_fm_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "offline_cache.db"
        self.max_cache_size = 500 * 1024 * 1024  # 500MB max cache
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize SQLite database for offline cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cached_content (
                        content_id TEXT PRIMARY KEY,
                        content_type TEXT NOT NULL,
                        data TEXT NOT NULL,
                        cached_at TEXT NOT NULL,
                        expires_at TEXT,
                        size_bytes INTEGER NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cached_media (
                        media_id TEXT PRIMARY KEY,
                        media_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        original_url TEXT,
                        cached_at TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        access_count INTEGER DEFAULT 0
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS offline_settings (
                        setting_key TEXT PRIMARY KEY,
                        setting_value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                logger.info("Offline cache database initialized")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    async def cache_radio_streams(self, streams: List[Dict[str, str]]) -> bool:
        """Cache radio stream information for offline access"""
        try:
            content_id = "radio_streams"
            data = {
                'streams': streams,
                'cached_timestamp': datetime.now().isoformat()
            }
            
            await self._cache_content(
                content_id=content_id,
                content_type='radio_streams',
                data=data,
                expires_in_hours=24
            )
            
            logger.info(f"Cached {len(streams)} radio streams for offline access")
            return True
            
        except Exception as e:
            logger.error(f"Radio streams caching error: {e}")
            return False
    
    async def cache_news_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Cache news articles for offline reading"""
        try:
            content_id = f"news_articles_{datetime.now().strftime('%Y%m%d')}"
            data = {
                'articles': articles,
                'cached_timestamp': datetime.now().isoformat()
            }
            
            await self._cache_content(
                content_id=content_id,
                content_type='news_articles',
                data=data,
                expires_in_hours=6  # News expires after 6 hours
            )
            
            logger.info(f"Cached {len(articles)} news articles for offline access")
            return True
            
        except Exception as e:
            logger.error(f"News caching error: {e}")
            return False
    
    async def cache_weather_data(self, weather_data: Dict[str, Any], location: str) -> bool:
        """Cache weather data for offline access"""
        try:
            content_id = f"weather_{location}"
            data = {
                'weather': weather_data,
                'location': location,
                'cached_timestamp': datetime.now().isoformat()
            }
            
            await self._cache_content(
                content_id=content_id,
                content_type='weather_data',
                data=data,
                expires_in_hours=1  # Weather expires after 1 hour
            )
            
            logger.info(f"Cached weather data for {location}")
            return True
            
        except Exception as e:
            logger.error(f"Weather caching error: {e}")
            return False
    
    async def cache_music_tracks(self, tracks: List[Dict[str, Any]]) -> bool:
        """Cache music track information for offline access"""
        try:
            content_id = f"music_tracks_{datetime.now().strftime('%Y%m%d')}"
            data = {
                'tracks': tracks,
                'cached_timestamp': datetime.now().isoformat()
            }
            
            await self._cache_content(
                content_id=content_id,
                content_type='music_tracks',
                data=data,
                expires_in_hours=12  # Music tracks expire after 12 hours
            )
            
            logger.info(f"Cached {len(tracks)} music tracks for offline access")
            return True
            
        except Exception as e:
            logger.error(f"Music caching error: {e}")
            return False
    
    async def cache_language_data(self, language_data: Dict[str, Any]) -> bool:
        """Cache language detection and localization data"""
        try:
            content_id = "language_data"
            data = {
                'language_data': language_data,
                'cached_timestamp': datetime.now().isoformat()
            }
            
            await self._cache_content(
                content_id=content_id,
                content_type='language_data',
                data=data,
                expires_in_hours=48  # Language data expires after 48 hours
            )
            
            logger.info("Cached language data for offline access")
            return True
            
        except Exception as e:
            logger.error(f"Language data caching error: {e}")
            return False
    
    async def cache_audio_stream(self, stream_url: str, duration_minutes: int = 30) -> Optional[str]:
        """Cache audio stream for offline playback"""
        try:
            # Generate cache file path
            stream_hash = hashlib.md5(stream_url.encode()).hexdigest()
            cache_file = self.cache_dir / f"audio_{stream_hash}.mp3"
            
            # Download and cache audio stream
            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        # Cache limited duration to save space
                        cached_size = 0
                        max_size = duration_minutes * 1024 * 1024  # Roughly 1MB per minute
                        
                        async with aiofiles.open(cache_file, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                if cached_size >= max_size:
                                    break
                                await f.write(chunk)
                                cached_size += len(chunk)
                        
                        # Store in database
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute("""
                                INSERT OR REPLACE INTO cached_media 
                                (media_id, media_type, file_path, original_url, cached_at, size_bytes, access_count)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                stream_hash,
                                'audio_stream',
                                str(cache_file),
                                stream_url,
                                datetime.now().isoformat(),
                                cached_size,
                                0
                            ))
                            conn.commit()
                        
                        logger.info(f"Cached {cached_size} bytes of audio stream")
                        return str(cache_file)
            
            return None
            
        except Exception as e:
            logger.error(f"Audio stream caching error: {e}")
            return None
    
    async def get_cached_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached content by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT data, expires_at FROM cached_content 
                    WHERE content_id = ?
                """, (content_id,))
                
                result = cursor.fetchone()
                if result:
                    data_json, expires_at = result
                    
                    # Check if content has expired
                    if expires_at:
                        expires_datetime = datetime.fromisoformat(expires_at)
                        if datetime.now() > expires_datetime:
                            await self.remove_cached_content(content_id)
                            return None
                    
                    # Update access count
                    conn.execute("""
                        UPDATE cached_content 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE content_id = ?
                    """, (datetime.now().isoformat(), content_id))
                    conn.commit()
                    
                    return json.loads(data_json)
                
                return None
                
        except Exception as e:
            logger.error(f"Content retrieval error: {e}")
            return None
    
    async def get_cached_audio(self, stream_url: str) -> Optional[str]:
        """Get cached audio file path for stream URL"""
        try:
            stream_hash = hashlib.md5(stream_url.encode()).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path FROM cached_media 
                    WHERE media_id = ? AND media_type = 'audio_stream'
                """, (stream_hash,))
                
                result = cursor.fetchone()
                if result:
                    file_path = result[0]
                    if Path(file_path).exists():
                        # Update access count
                        conn.execute("""
                            UPDATE cached_media 
                            SET access_count = access_count + 1
                            WHERE media_id = ?
                        """, (stream_hash,))
                        conn.commit()
                        
                        return file_path
                
                return None
                
        except Exception as e:
            logger.error(f"Cached audio retrieval error: {e}")
            return None
    
    async def get_offline_radio_streams(self) -> List[Dict[str, str]]:
        """Get cached radio streams for offline use"""
        try:
            cached_data = await self.get_cached_content("radio_streams")
            if cached_data:
                return cached_data.get('streams', [])
            return []
        except:
            return []
    
    async def get_offline_news(self) -> List[Dict[str, Any]]:
        """Get cached news articles for offline reading"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            cached_data = await self.get_cached_content(f"news_articles_{today}")
            if cached_data:
                return cached_data.get('articles', [])
            return []
        except:
            return []
    
    async def get_offline_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get cached weather data for location"""
        try:
            cached_data = await self.get_cached_content(f"weather_{location}")
            if cached_data:
                return cached_data.get('weather')
            return None
        except:
            return None
    
    async def get_offline_music(self) -> List[Dict[str, Any]]:
        """Get cached music tracks"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            cached_data = await self.get_cached_content(f"music_tracks_{today}")
            if cached_data:
                return cached_data.get('tracks', [])
            return []
        except:
            return []
    
    async def cleanup_expired_content(self):
        """Remove expired content from cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Remove expired content
                conn.execute("""
                    DELETE FROM cached_content 
                    WHERE expires_at IS NOT NULL 
                    AND datetime(expires_at) < datetime('now')
                """)
                
                # Remove old cached files
                cursor = conn.execute("""
                    SELECT file_path FROM cached_media
                    WHERE datetime(cached_at) < datetime('now', '-7 days')
                """)
                
                old_files = cursor.fetchall()
                for (file_path,) in old_files:
                    try:
                        Path(file_path).unlink()
                    except:
                        pass
                
                # Remove old media records
                conn.execute("""
                    DELETE FROM cached_media
                    WHERE datetime(cached_at) < datetime('now', '-7 days')
                """)
                
                conn.commit()
                logger.info("Cleaned up expired cached content")
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get content statistics
                content_cursor = conn.execute("""
                    SELECT content_type, COUNT(*), SUM(size_bytes)
                    FROM cached_content
                    GROUP BY content_type
                """)
                content_stats = content_cursor.fetchall()
                
                # Get media statistics  
                media_cursor = conn.execute("""
                    SELECT media_type, COUNT(*), SUM(size_bytes)
                    FROM cached_media
                    GROUP BY media_type
                """)
                media_stats = media_cursor.fetchall()
                
                # Get total size
                total_cursor = conn.execute("""
                    SELECT 
                        (SELECT COALESCE(SUM(size_bytes), 0) FROM cached_content) +
                        (SELECT COALESCE(SUM(size_bytes), 0) FROM cached_media) as total_size
                """)
                total_size = total_cursor.fetchone()[0]
                
                return {
                    'content_stats': [
                        {'type': row[0], 'count': row[1], 'size_bytes': row[2]}
                        for row in content_stats
                    ],
                    'media_stats': [
                        {'type': row[0], 'count': row[1], 'size_bytes': row[2]}
                        for row in media_stats
                    ],
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / 1024 / 1024, 2),
                    'cache_limit_mb': round(self.max_cache_size / 1024 / 1024, 2),
                    'cache_usage_percent': round((total_size / self.max_cache_size) * 100, 2)
                }
                
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}
    
    async def _cache_content(self, content_id: str, content_type: str, data: Dict[str, Any], expires_in_hours: Optional[int] = None):
        """Internal method to cache content"""
        try:
            data_json = json.dumps(data, default=str)
            data_compressed = gzip.compress(data_json.encode())
            size_bytes = len(data_compressed)
            
            expires_at = None
            if expires_in_hours:
                expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cached_content 
                    (content_id, content_type, data, cached_at, expires_at, size_bytes, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content_id,
                    content_type,
                    base64.b64encode(data_compressed).decode(),
                    datetime.now().isoformat(),
                    expires_at,
                    size_bytes,
                    0,
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            # Check if we're over cache limit
            await self._enforce_cache_limit()
            
        except Exception as e:
            logger.error(f"Content caching error: {e}")
            raise
    
    async def _enforce_cache_limit(self):
        """Enforce cache size limits by removing least accessed content"""
        try:
            stats = await self.get_cache_stats()
            if stats.get('total_size_bytes', 0) > self.max_cache_size:
                with sqlite3.connect(self.db_path) as conn:
                    # Remove least accessed content
                    conn.execute("""
                        DELETE FROM cached_content 
                        WHERE content_id IN (
                            SELECT content_id FROM cached_content
                            ORDER BY access_count ASC, last_accessed ASC
                            LIMIT 10
                        )
                    """)
                    conn.commit()
                    logger.info("Enforced cache size limit by removing old content")
        except Exception as e:
            logger.error(f"Cache limit enforcement error: {e}")
    
    async def remove_cached_content(self, content_id: str):
        """Remove specific cached content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cached_content WHERE content_id = ?", (content_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Content removal error: {e}")