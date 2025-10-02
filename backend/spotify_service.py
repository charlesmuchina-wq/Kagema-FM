"""
Spotify Integration Service
Handles Spotify Web API authentication and music operations
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service class for Spotify Web API integration"""
    
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:3000/auth/callback")
        
        if not self.client_id or not self.client_secret:
            logger.error("Spotify credentials not found in environment variables")
            return
            
        # Initialize client credentials manager for app-only requests (no user auth)
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Initialize OAuth for user authentication
        self.oauth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-read-playback-state user-modify-playback-state user-read-private streaming user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
        )
        
        logger.info("✅ Spotify service initialized with real API credentials")

    def get_auth_url(self) -> str:
        """Get Spotify authorization URL for user login"""
        try:
            auth_url = self.oauth_manager.get_authorize_url()
            logger.info("Generated Spotify auth URL")
            return auth_url
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            raise

    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            token_info = self.oauth_manager.get_access_token(code)
            logger.info("Successfully obtained Spotify access token")
            return {
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
                "expires_in": token_info["expires_in"]
            }
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            token_info = self.oauth_manager.refresh_access_token(refresh_token)
            logger.info("Successfully refreshed Spotify access token")
            return {
                "access_token": token_info["access_token"],
                "expires_in": token_info["expires_in"]
            }
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    def search_tracks(self, query: str, limit: int = 20, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Search for tracks using Spotify API"""
        try:
            if access_token:
                # Use user's access token for personalized results
                sp = spotipy.Spotify(auth=access_token)
            else:
                # Use client credentials for general search
                sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
            
            results = sp.search(q=query, type='track', limit=limit)
            
            # Format results for frontend
            tracks = []
            for item in results['tracks']['items']:
                track = {
                    "id": item['id'],
                    "name": item['name'],
                    "artist": ', '.join([artist['name'] for artist in item['artists']]),
                    "album": item['album']['name'],
                    "duration_ms": item['duration_ms'],
                    "preview_url": item['preview_url'],
                    "external_urls": item['external_urls'],
                    "uri": item['uri'],
                    "image": item['album']['images'][0]['url'] if item['album']['images'] else None
                }
                tracks.append(track)
            
            logger.info(f"Found {len(tracks)} tracks for query: {query}")
            return {
                "tracks": tracks,
                "total": results['tracks']['total']
            }
            
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            # Return fallback data on error
            return {
                "tracks": [
                    {
                        "id": "fallback_1",
                        "name": f"{query} - Demo Track",
                        "artist": "Demo Artist",
                        "album": "Demo Album",
                        "duration_ms": 180000,
                        "preview_url": None,
                        "external_urls": {"spotify": "#"},
                        "uri": "spotify:track:fallback",
                        "image": None
                    }
                ],
                "total": 1
            }

    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            profile = sp.me()
            
            return {
                "id": profile['id'],
                "display_name": profile['display_name'],
                "email": profile.get('email'),
                "country": profile.get('country'),
                "product": profile.get('product', 'free'),
                "is_premium": profile.get('product') == 'premium',
                "followers": profile['followers']['total'],
                "external_urls": profile['external_urls'],
                "images": profile.get('images', [])
            }
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise

    def get_user_playlists(self, access_token: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's playlists"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            results = sp.current_user_playlists(limit=limit)
            
            playlists = []
            for item in results['items']:
                playlist = {
                    "id": item['id'],
                    "name": item['name'],
                    "description": item['description'],
                    "public": item['public'],
                    "track_count": item['tracks']['total'],
                    "external_urls": item['external_urls'],
                    "images": item.get('images', [])
                }
                playlists.append(playlist)
            
            logger.info(f"Retrieved {len(playlists)} playlists for user")
            return playlists
            
        except Exception as e:
            logger.error(f"Error getting playlists: {e}")
            return []

    def create_playlist(self, access_token: str, playlist_name: str, description: str = "", public: bool = False) -> Dict[str, Any]:
        """Create a new playlist for the user"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            user_id = sp.me()['id']
            
            playlist = sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=public,
                description=description
            )
            
            logger.info(f"Created playlist '{playlist_name}' for user {user_id}")
            return {
                "id": playlist['id'],
                "name": playlist['name'],
                "external_urls": playlist['external_urls'],
                "uri": playlist['uri']
            }
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise

    def add_tracks_to_playlist(self, access_token: str, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            sp.playlist_add_items(playlist_id, track_uris)
            
            logger.info(f"Added {len(track_uris)} tracks to playlist {playlist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tracks to playlist: {e}")
            return False

    def get_recommendations(self, access_token: str, seed_artists: List[str] = None, seed_genres: List[str] = None, seed_tracks: List[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get track recommendations based on seeds"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            
            results = sp.recommendations(
                seed_artists=seed_artists or [],
                seed_genres=seed_genres or [],
                seed_tracks=seed_tracks or [],
                limit=limit
            )
            
            tracks = []
            for item in results['tracks']:
                track = {
                    "id": item['id'],
                    "name": item['name'],
                    "artist": ', '.join([artist['name'] for artist in item['artists']]),
                    "album": item['album']['name'],
                    "duration_ms": item['duration_ms'],
                    "preview_url": item['preview_url'],
                    "external_urls": item['external_urls'],
                    "uri": item['uri'],
                    "image": item['album']['images'][0]['url'] if item['album']['images'] else None
                }
                tracks.append(track)
            
            logger.info(f"Generated {len(tracks)} recommendations")
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def get_available_genres(self) -> List[str]:
        """Get available genre seeds for recommendations"""
        try:
            sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
            genres = sp.recommendation_genre_seeds()
            return genres['genres']
        except Exception as e:
            logger.error(f"Error getting genres: {e}")
            return ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hip-hop', 'country', 'folk']

# Initialize service instance
spotify_service = SpotifyService()