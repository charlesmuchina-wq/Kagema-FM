"""Intelligent AI Search Engine
AI-powered search that understands natural language queries for radio stations
Searches by country, state, region, language, genre, frequency, and more
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import re
from bson import ObjectId

load_dotenv()

logger = logging.getLogger(__name__)


class IntelligentSearchEngine:
    """AI-powered search engine for radio stations"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Search intent patterns
        self.intent_patterns = {
            'country': r'\b(in|from|country)\s+([A-Z]{2}|[A-Za-z\s]+)\b',
            'language': r'\b(language|speaking|in)\s+([A-Za-z]+)\b',
            'genre': r'\b(genre|type|kind|music|playing)\s+([A-Za-z\s]+)\b',
            'frequency': r'\b(\d+\.?\d*)\s*(FM|AM|MHz|KHz)\b',
            'region': r'\b(region|state|province|area)\s+([A-Za-z\s]+)\b',
            'quality': r'\b(quality|best|top|popular)\b',
        }
        
        # Country name to code mapping (common ones)
        self.country_mapping = {
            'united states': 'US', 'usa': 'US', 'america': 'US',
            'united kingdom': 'GB', 'uk': 'GB', 'britain': 'GB',
            'canada': 'CA', 'france': 'FR', 'germany': 'DE',
            'japan': 'JP', 'china': 'CN', 'india': 'IN',
            'brazil': 'BR', 'mexico': 'MX', 'australia': 'AU',
            'kenya': 'KE', 'nigeria': 'NG', 'south africa': 'ZA',
            'egypt': 'EG', 'argentina': 'AR', 'spain': 'ES',
            'italy': 'IT', 'netherlands': 'NL', 'sweden': 'SE',
        }
        
        logger.info("Intelligent Search Engine initialized")
    
    def _serialize_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to JSON-serializable format"""
        serialized = {}
        for key, value in station.items():
            if isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif key == '_id':
                # Skip MongoDB _id field or convert to string
                serialized['id'] = str(value) if value else None
            else:
                serialized[key] = value
        return serialized
    
    async def ai_search(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """AI-powered intelligent search with natural language understanding"""
        try:
            query_lower = query.lower().strip()
            
            logger.info(f"AI Search Query: '{query}'")
            
            # Parse intent and extract entities
            search_params = await self._parse_search_intent(query_lower)
            
            # Build MongoDB query
            mongo_query = await self._build_mongo_query(search_params)
            
            # Execute search
            stations = await self.db.radio_stations.find(mongo_query).limit(limit).to_list(length=limit)
            
            # Rank results by relevance
            ranked_stations = await self._rank_results(stations, search_params, query_lower)
            
            return {
                'status': 'success',
                'query': query,
                'parsed_intent': search_params,
                'results': ranked_stations[:limit],
                'total_found': len(ranked_stations),
                'search_type': 'ai_powered'
            }
        
        except Exception as e:
            logger.error(f"AI search error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'results': []
            }
    
    async def _parse_search_intent(self, query: str) -> Dict[str, Any]:
        """Parse search intent using pattern matching and NLP"""
        intent = {
            'raw_query': query,
            'country': None,
            'language': None,
            'genre': None,
            'frequency': None,
            'region': None,
            'quality_filter': False,
            'keywords': []
        }
        
        # Extract country
        for pattern in [r'\b([A-Z]{2})\b', r'\b(in|from)\s+([A-Za-z\s]+)']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                country_text = match.group(2) if 'in|from' in pattern else match.group(1)
                country_code = self._resolve_country(country_text.strip().lower())
                if country_code:
                    intent['country'] = country_code
                    break
        
        # Extract language
        lang_match = re.search(r'\b(english|spanish|french|german|portuguese|chinese|japanese|arabic|hindi|swahili)\b', query, re.IGNORECASE)
        if lang_match:
            intent['language'] = lang_match.group(1).lower()
        
        # Extract genre
        genre_keywords = ['rock', 'pop', 'jazz', 'classical', 'hip hop', 'country', 'electronic', 'dance', 'news', 'talk', 'sports']
        for genre in genre_keywords:
            if genre in query:
                intent['genre'] = genre
                break
        
        # Extract frequency
        freq_match = re.search(r'(\d+\.?\d*)\s*(FM|AM|MHz|KHz)', query, re.IGNORECASE)
        if freq_match:
            intent['frequency'] = float(freq_match.group(1))
        
        # Quality filter
        if any(word in query for word in ['best', 'top', 'popular', 'quality']):
            intent['quality_filter'] = True
        
        # Extract keywords (remaining words)
        keywords = [word for word in query.split() if len(word) > 3 and word not in ['from', 'with', 'station', 'radio']]
        intent['keywords'] = keywords[:5]  # Top 5 keywords
        
        return intent
    
    def _resolve_country(self, country_text: str) -> Optional[str]:
        """Resolve country name to ISO code"""
        # Check if already ISO code
        if len(country_text) == 2 and country_text.upper().isalpha():
            return country_text.upper()
        
        # Check mapping
        return self.country_mapping.get(country_text.lower())
    
    async def _build_mongo_query(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query from search parameters"""
        query = {}
        
        # Country filter
        if search_params['country']:
            query['country'] = search_params['country']
        
        # Language filter
        if search_params['language']:
            query['language'] = {'$regex': search_params['language'], '$options': 'i'}
        
        # Genre filter
        if search_params['genre']:
            query['genre'] = {'$regex': search_params['genre'], '$options': 'i'}
        
        # Frequency filter
        if search_params['frequency']:
            freq = search_params['frequency']
            query['extracted_frequency'] = {'$gte': freq - 0.5, '$lte': freq + 0.5}
        
        # Region filter (division)
        if search_params['region']:
            query['$or'] = [
                {'division_level1_name': {'$regex': search_params['region'], '$options': 'i'}},
                {'division_level2_name': {'$regex': search_params['region'], '$options': 'i'}}
            ]
        
        # Keywords (search in name and description)
        if search_params['keywords']:
            keyword_conditions = []
            for keyword in search_params['keywords']:
                keyword_conditions.extend([
                    {'name': {'$regex': keyword, '$options': 'i'}},
                    {'description': {'$regex': keyword, '$options': 'i'}},
                    {'call_sign': {'$regex': keyword, '$options': 'i'}}
                ])
            
            if keyword_conditions:
                if '$or' in query:
                    query['$and'] = [{'$or': query.pop('$or')}, {'$or': keyword_conditions}]
                else:
                    query['$or'] = keyword_conditions
        
        # Quality filter
        if search_params['quality_filter']:
            if not query:
                query = {}
            query['quality_score'] = {'$gte': 70}
        
        return query if query else {}
    
    async def _rank_results(self, stations: List[Dict], search_params: Dict, query: str) -> List[Dict]:
        """Rank search results by relevance"""
        ranked = []
        
        for station in stations:
            # Serialize the station first to handle ObjectId
            serialized_station = self._serialize_station(station)
            
            score = 0
            
            # Exact match bonus
            if query in serialized_station.get('name', '').lower():
                score += 50
            
            # Call sign match
            if query.upper() in serialized_station.get('call_sign', '').upper():
                score += 40
            
            # Quality score
            score += serialized_station.get('quality_score', 0) * 0.5
            
            # Country match
            if search_params['country'] and serialized_station.get('country') == search_params['country']:
                score += 30
            
            # Language match
            if search_params['language'] and search_params['language'] in serialized_station.get('language', '').lower():
                score += 20
            
            # Genre match
            if search_params['genre'] and search_params['genre'] in serialized_station.get('genre', '').lower():
                score += 25
            
            # Add relevance score
            serialized_station['relevance_score'] = score
            ranked.append(serialized_station)
        
        # Sort by relevance
        ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked
    
    async def search_by_location(self, lat: float, lon: float, radius_km: int = 100, limit: int = 50) -> List[Dict]:
        """Search stations by geographic location"""
        try:
            # Find stations within radius using Haversine formula
            # For now, simple implementation - can be optimized with geospatial indexes
            
            stations = await self.db.radio_stations.find({
                'lat': {'$exists': True},
                'lon': {'$exists': True}
            }).to_list(length=1000)
            
            nearby = []
            for station in stations:
                station_lat = station.get('lat')
                station_lon = station.get('lon')
                
                if station_lat and station_lon:
                    distance = self._calculate_distance(lat, lon, float(station_lat), float(station_lon))
                    if distance <= radius_km:
                        station['distance_km'] = round(distance, 2)
                        nearby.append(station)
            
            # Sort by distance
            nearby.sort(key=lambda x: x['distance_km'])
            
            return nearby[:limit]
        
        except Exception as e:
            logger.error(f"Location search error: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            suggestions = []
            
            # Suggest countries
            for name, code in self.country_mapping.items():
                if partial_query.lower() in name:
                    suggestions.append(f"Radio stations in {name.title()}")
            
            # Suggest from existing station names
            stations = await self.db.radio_stations.find({
                'name': {'$regex': partial_query, '$options': 'i'}
            }).limit(5).to_list(length=5)
            
            for station in stations:
                suggestions.append(station['name'])
            
            return suggestions[:limit]
        
        except Exception as e:
            logger.error(f"Suggestions error: {e}")
            return []


# Global instance
search_engine_instance = None


def get_search_engine() -> IntelligentSearchEngine:
    """Get or create search engine instance"""
    global search_engine_instance
    if search_engine_instance is None:
        search_engine_instance = IntelligentSearchEngine()
    return search_engine_instance
