"""Dragon AI Search API
Advanced search and filtering for radio stations
"""
from fastapi import APIRouter, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
import logging

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/dragon-search', tags=['Dragon AI Search'])

# Database connection
mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
db = mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]

class StationSearchResult(BaseModel):
    id: str
    name: str
    country: str
    language: str
    genre: str
    stream_url: str
    quality_score: int
    validated: bool
    homepage: Optional[str] = None
    favicon: Optional[str] = None
    bitrate: Optional[int] = 0

class SearchFilters(BaseModel):
    language: Optional[str] = None
    genre: Optional[str] = None
    country: Optional[str] = None
    min_quality: Optional[int] = 0
    max_quality: Optional[int] = 100
    validated_only: bool = False

@router.get('/stations', response_model=List[StationSearchResult])
async def search_stations(
    query: Optional[str] = Query(None, description="Search by station name"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    min_quality: int = Query(0, ge=0, le=100, description="Minimum quality score"),
    max_quality: int = Query(100, ge=0, le=100, description="Maximum quality score"),
    validated_only: bool = Query(False, description="Only validated stations"),
    limit: int = Query(50, ge=1, le=500, description="Results limit"),
    skip: int = Query(0, ge=0, description="Results to skip")
):
    """Search and filter radio stations with advanced criteria"""
    try:
        # Build query
        filters = {}
        
        if query:
            filters['name'] = {'$regex': query, '$options': 'i'}
        
        if language:
            filters['language'] = language.lower()
        
        if genre:
            filters['genre'] = {'$regex': genre, '$options': 'i'}
        
        if country:
            filters['country'] = country.upper()
        
        if min_quality > 0 or max_quality < 100:
            filters['quality_score'] = {'$gte': min_quality, '$lte': max_quality}
        
        if validated_only:
            filters['validated'] = True
        
        # Execute query
        cursor = db.radio_stations.find(filters).sort('quality_score', -1).skip(skip).limit(limit)
        
        stations = []
        async for station in cursor:
            stations.append(StationSearchResult(
                id=station.get('id', str(station['_id'])),
                name=station.get('name', 'Unknown'),
                country=station.get('country', 'UNKNOWN'),
                language=station.get('language', 'en'),
                genre=station.get('genre', 'General'),
                stream_url=station.get('stream_url', ''),
                quality_score=station.get('quality_score', 50),
                validated=station.get('validated', False),
                homepage=station.get('homepage'),
                favicon=station.get('favicon'),
                bitrate=station.get('bitrate', 0)
            ))
        
        return stations
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/filters/languages')
async def get_available_languages():
    """Get list of available languages"""
    try:
        languages = await db.radio_stations.distinct('language')
        return {'languages': sorted(languages)}
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/filters/genres')
async def get_available_genres():
    """Get list of available genres"""
    try:
        genres = await db.radio_stations.distinct('genre')
        return {'genres': sorted(genres)}
    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/filters/countries')
async def get_available_countries():
    """Get list of available countries with station counts"""
    try:
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        countries = await db.radio_stations.aggregate(pipeline).to_list(length=None)
        
        return {
            'countries': [
                {'code': c['_id'], 'count': c['count']}
                for c in countries
            ]
        }
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/stats')
async def get_search_stats():
    """Get search and database statistics"""
    try:
        total = await db.radio_stations.count_documents({})
        validated = await db.radio_stations.count_documents({'validated': True})
        languages = len(await db.radio_stations.distinct('language'))
        countries = len(await db.radio_stations.distinct('country'))
        genres = len(await db.radio_stations.distinct('genre'))
        
        return {
            'total_stations': total,
            'validated_stations': validated,
            'validation_rate': f"{(validated/total*100):.1f}%" if total > 0 else "0%",
            'unique_languages': languages,
            'unique_countries': countries,
            'unique_genres': genres
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
