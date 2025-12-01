"""Dragon AI Crawler API
7 API automation features for discovering 12,500+ radio stations
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from dragon_ai_crawler_system import get_crawler
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/dragon-crawler', tags=['Dragon AI Crawler'])

class CrawlRequest(BaseModel):
    target_stations: int = 12500
    continent: str = None
    country: str = None

# =============================================================================
# API 1: START GLOBAL CRAWL
# =============================================================================

@router.post('/start')
async def start_global_crawl(
    background_tasks: BackgroundTasks,
    target_stations: int = Query(12500, ge=1000, le=50000, description="Target number of stations")
):
    """
    API 1: Start Global Crawl
    
    Initiates comprehensive crawl of all 195 countries to discover target number of stations.
    Runs in background and continues until target is reached or all countries are crawled.
    
    **Features:**
    - Crawls Radio Browser API (10M+ stations)
    - Intelligent quality scoring
    - Automatic deduplication
    - Geographic coverage tracking
    - Progress monitoring
    """
    try:
        crawler = get_crawler()
        result = await crawler.start_global_crawl(target_stations)
        return result
    except Exception as e:
        logger.error(f"Error starting crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 2: STOP CRAWL
# =============================================================================

@router.post('/stop')
async def stop_crawl():
    """
    API 2: Stop Current Crawl
    
    Gracefully stops the currently running crawl operation.
    Returns statistics of the crawl session up to the point of stopping.
    
    **Returns:**
    - Stations discovered
    - Stations saved
    - Countries crawled
    - Duplicate count
    """
    try:
        crawler = get_crawler()
        result = await crawler.stop_crawl()
        return result
    except Exception as e:
        logger.error(f"Error stopping crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 3: GET CRAWLER STATUS
# =============================================================================

@router.get('/status')
async def get_crawler_status():
    """
    API 3: Get Crawler Status
    
    Returns real-time status of the crawler including:
    - Running state
    - Current country being crawled
    - Statistics (discovered, saved, duplicates)
    - Database totals
    - Progress indicators
    
    **Use this to monitor long-running crawls**
    """
    try:
        crawler = get_crawler()
        status = await crawler.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 4: GET CRAWLER STATISTICS
# =============================================================================

@router.get('/statistics')
async def get_crawler_statistics():
    """
    API 4: Get Comprehensive Statistics
    
    Returns detailed statistics including:
    - Total stations in database
    - Validation rates
    - Geographic coverage
    - Top 10 countries by station count
    - Recent crawl history
    - Quality metrics
    
    **Perfect for analytics and reporting**
    """
    try:
        crawler = get_crawler()
        stats = await crawler.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 5: CRAWL SPECIFIC COUNTRY
# =============================================================================

@router.post('/crawl-country/{country_code}')
async def crawl_specific_country(country_code: str):
    """
    API 5: Crawl Specific Country
    
    Crawls all radio stations from a specific country.
    
    **Path Parameters:**
    - country_code: ISO 3166-1 alpha-2 code (e.g., US, GB, DE, BR, KE)
    
    **Example:**
    ```
    POST /api/dragon-crawler/crawl-country/US
    ```
    
    **Returns:**
    - Stations discovered in that country
    - Stations saved (new additions)
    - Duplicate count
    """
    try:
        crawler = get_crawler()
        result = await crawler.crawl_specific_country(country_code.upper())
        return result
    except Exception as e:
        logger.error(f"Error crawling country {country_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 6: CRAWL CONTINENT
# =============================================================================

@router.post('/crawl-continent/{continent}')
async def crawl_continent(continent: str):
    """
    API 6: Crawl Entire Continent
    
    Crawls all countries within a specific continent.
    
    **Available Continents:**
    - africa (54 countries)
    - asia (48 countries)
    - europe (44 countries)
    - north_america (23 countries)
    - south_america (12 countries)
    - oceania (14 countries)
    
    **Example:**
    ```
    POST /api/dragon-crawler/crawl-continent/europe
    ```
    
    **Returns:**
    - Countries crawled
    - Total stations discovered
    - Total stations saved
    """
    try:
        crawler = get_crawler()
        result = await crawler.crawl_continent(continent.lower())
        return result
    except Exception as e:
        logger.error(f"Error crawling continent {continent}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# API 7: GET DISCOVERED STATIONS
# =============================================================================

@router.get('/discovered-stations')
async def get_discovered_stations(
    limit: int = Query(100, ge=1, le=1000, description="Number of stations to return"),
    skip: int = Query(0, ge=0, description="Number of stations to skip"),
    country: str = Query(None, description="Filter by country code"),
    min_quality: int = Query(0, ge=0, le=100, description="Minimum quality score")
):
    """
    API 7: Get Discovered Stations
    
    Retrieves recently discovered stations from the database with filtering options.
    
    **Query Parameters:**
    - limit: Number of results (1-1000)
    - skip: Pagination offset
    - country: Filter by country code (optional)
    - min_quality: Minimum quality score (0-100, optional)
    
    **Example:**
    ```
    GET /api/dragon-crawler/discovered-stations?limit=50&country=US&min_quality=70
    ```
    
    **Returns:**
    - List of stations with metadata
    - Quality scores
    - Source information
    - Timestamps
    """
    try:
        from dragon_ai_crawler_system import get_crawler
        crawler = get_crawler()
        
        # Build query
        query = {}
        if country:
            query['country'] = country.upper()
        if min_quality > 0:
            query['quality_score'] = {'$gte': min_quality}
        
        # Query database
        cursor = crawler.db.radio_stations.find(query).sort('created_at', -1).skip(skip).limit(limit)
        stations = await cursor.to_list(length=limit)
        
        # Format response
        result = []
        for station in stations:
            result.append({
                'id': station.get('id'),
                'name': station.get('name'),
                'country': station.get('country'),
                'language': station.get('language'),
                'genre': station.get('genre'),
                'stream_url': station.get('stream_url'),
                'quality_score': station.get('quality_score'),
                'validated': station.get('validated'),
                'bitrate': station.get('bitrate'),
                'votes': station.get('votes'),
                'source': station.get('source'),
                'created_at': station.get('created_at').isoformat() if station.get('created_at') else None
            })
        
        return {
            'stations': result,
            'count': len(result),
            'limit': limit,
            'skip': skip
        }
    except Exception as e:
        logger.error(f"Error getting discovered stations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# BONUS: Quick Start Endpoint
# =============================================================================

@router.post('/quick-start')
async def quick_start_12500():
    """
    BONUS: Quick Start to 12,500 Stations
    
    One-click endpoint to start crawling toward 12,500 stations.
    This is the fastest way to populate your database.
    
    **What it does:**
    - Starts global crawl targeting 12,500 stations
    - Crawls all 195 countries
    - Runs in background
    - Auto-stops when target is reached
    
    **Estimated Time:** 30-60 minutes
    """
    try:
        crawler = get_crawler()
        result = await crawler.start_global_crawl(target_stations=12500)
        return {
            **result,
            'message': '🚀 Dragon AI Crawler launched! Targeting 12,500 stations across 195 countries.',
            'estimated_time': '30-60 minutes',
            'monitor_at': '/api/dragon-crawler/status'
        }
    except Exception as e:
        logger.error(f"Error in quick start: {e}")
        raise HTTPException(status_code=500, detail=str(e))
