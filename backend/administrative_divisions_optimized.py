"""
Optimized Administrative Divisions Manager with Background Processing
Fixes timeout issues with pagination, caching, and async queue processing
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class OptimizedAdministrativeDivisionsManager:
    """Optimized manager with background processing and caching"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # API endpoint
        self.admin_divisions_api = 'https://rawcdn.githack.com/kamikazechaser/administrative-divisions-db/master/api'
        
        # Processing state
        self.is_processing = False
        self.current_progress = {
            'status': 'idle',
            'countries_processed': 0,
            'total_countries': 0,
            'current_country': None,
            'level1_divisions': 0,
            'level2_divisions': 0,
            'failed_countries': [],
            'started_at': None,
            'estimated_completion': None
        }
        
        # Country codes in batches for better performance
        self.country_batches = self._create_country_batches()
        
        # Cache settings
        self.cache_ttl = timedelta(days=30)  # Divisions don't change often
        
        logger.info("✅ Optimized Administrative Divisions Manager initialized")
    
    def _create_country_batches(self) -> List[List[str]]:
        """Create batches of countries for progressive processing"""
        all_countries = [
            'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
            'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BR', 'BN',
            'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CO', 'KM', 'CG',
            'CD', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ',
            'ER', 'EE', 'ET', 'FJ', 'FI', 'FR', 'GA', 'GM', 'GE', 'DE', 'GH', 'GR', 'GD', 'GT', 'GN',
            'GW', 'GY', 'HT', 'HN', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IL', 'IT', 'JM', 'JP',
            'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI',
            'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MR', 'MU', 'MX', 'FM', 'MD', 'MC',
            'MN', 'ME', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NZ', 'NI', 'NE', 'NG', 'NO', 'OM',
            'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PL', 'PT', 'QA', 'RO', 'RU', 'RW', 'KN',
            'LC', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO',
            'ZA', 'SS', 'ES', 'LK', 'SD', 'SR', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL',
            'TG', 'TO', 'TT', 'TN', 'TR', 'TM', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UY', 'UZ', 'VU',
            'VE', 'VN', 'YE', 'ZM', 'ZW',
        ]
        
        # Create batches of 20 countries each
        batch_size = 20
        return [all_countries[i:i + batch_size] for i in range(0, len(all_countries), batch_size)]
    
    async def check_cache(self, country_code: str) -> Optional[Dict]:
        """Check if country divisions are cached"""
        try:
            cached = await self.db.administrative_divisions_cache.find_one({
                'country_code': country_code,
                'cached_at': {'$gte': datetime.utcnow() - self.cache_ttl}
            })
            
            if cached:
                logger.info(f"✅ Cache hit for {country_code}")
                return cached.get('data')
            
            return None
        except Exception as e:
            logger.error(f"❌ Cache check error for {country_code}: {e}")
            return None
    
    async def save_to_cache(self, country_code: str, data: Dict):
        """Save country divisions to cache"""
        try:
            await self.db.administrative_divisions_cache.update_one(
                {'country_code': country_code},
                {
                    '$set': {
                        'country_code': country_code,
                        'data': data,
                        'cached_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            logger.info(f"💾 Cached divisions for {country_code}")
        except Exception as e:
            logger.error(f"❌ Cache save error for {country_code}: {e}")
    
    async def fetch_country_divisions_with_retry(self, country_code: str, max_retries: int = 2) -> Dict[str, Any]:
        """Fetch divisions with retry logic and caching"""
        # Check cache first
        cached_data = await self.check_cache(country_code)
        if cached_data:
            return cached_data
        
        # Fetch from API with retries
        for attempt in range(max_retries):
            try:
                url = f"{self.admin_divisions_api}/{country_code}.json"
                
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10),  # Reduced timeout
                    headers={'User-Agent': 'DragonKarauAI/1.0'}
                ) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Parse and structure data
                            result = {
                                'country_code': country_code,
                                'level1_divisions': [],
                                'level2_divisions': [],
                                'fetched_at': datetime.utcnow().isoformat()
                            }
                            
                            # Simple parsing - handle list of strings
                            if isinstance(data, list):
                                for idx, item in enumerate(data):
                                    if isinstance(item, str):
                                        result['level1_divisions'].append({
                                            'id': f"{country_code}-{idx}",
                                            'name': item,
                                            'country_code': country_code,
                                            'type': 'level1'
                                        })
                            
                            # Cache the result
                            await self.save_to_cache(country_code, result)
                            
                            return result
                        elif response.status == 404:
                            # Country has no divisions data
                            logger.info(f"ℹ️  No divisions data for {country_code}")
                            return {
                                'country_code': country_code,
                                'level1_divisions': [],
                                'level2_divisions': [],
                                'error': 'No data available'
                            }
                        else:
                            logger.warning(f"⚠️  HTTP {response.status} for {country_code}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏱️  Timeout for {country_code} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Brief delay before retry
            except Exception as e:
                logger.error(f"❌ Error fetching {country_code}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        # Return empty result after all retries failed
        return {
            'country_code': country_code,
            'level1_divisions': [],
            'level2_divisions': [],
            'error': 'Failed to fetch after retries'
        }
    
    async def populate_batch(self, country_batch: List[str]) -> Dict[str, Any]:
        """Populate divisions for a batch of countries"""
        batch_stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'level1_total': 0,
            'level2_total': 0
        }
        
        for country_code in country_batch:
            try:
                self.current_progress['current_country'] = country_code
                
                # Fetch divisions
                divisions_data = await self.fetch_country_divisions_with_retry(country_code)
                
                if 'error' not in divisions_data:
                    # Save to database
                    for div in divisions_data.get('level1_divisions', []):
                        await self.db.administrative_divisions.update_one(
                            {'id': div['id']},
                            {'$set': div},
                            upsert=True
                        )
                        batch_stats['level1_total'] += 1
                    
                    for div in divisions_data.get('level2_divisions', []):
                        await self.db.administrative_divisions.update_one(
                            {'id': div['id']},
                            {'$set': div},
                            upsert=True
                        )
                        batch_stats['level2_total'] += 1
                    
                    batch_stats['successful'] += 1
                    logger.info(f"✅ Populated {country_code}: {len(divisions_data.get('level1_divisions', []))} divisions")
                else:
                    batch_stats['failed'] += 1
                    self.current_progress['failed_countries'].append(country_code)
                
                batch_stats['processed'] += 1
                self.current_progress['countries_processed'] += 1
                
                # Small delay to be respectful to API
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error processing {country_code}: {e}")
                batch_stats['failed'] += 1
                self.current_progress['failed_countries'].append(country_code)
        
        return batch_stats
    
    async def populate_all_divisions_background(self) -> Dict[str, Any]:
        """Populate all divisions in background with progress tracking"""
        if self.is_processing:
            return {
                'status': 'already_running',
                'message': 'Population already in progress',
                'progress': self.current_progress
            }
        
        self.is_processing = True
        self.current_progress = {
            'status': 'running',
            'countries_processed': 0,
            'total_countries': sum(len(batch) for batch in self.country_batches),
            'current_country': None,
            'level1_divisions': 0,
            'level2_divisions': 0,
            'failed_countries': [],
            'started_at': datetime.utcnow().isoformat(),
            'estimated_completion': None
        }
        
        logger.info(f"🚀 Starting background population of {self.current_progress['total_countries']} countries")
        
        try:
            total_level1 = 0
            total_level2 = 0
            
            # Process batches sequentially to avoid overwhelming the API
            for batch_idx, batch in enumerate(self.country_batches):
                logger.info(f"📦 Processing batch {batch_idx + 1}/{len(self.country_batches)}")
                
                batch_stats = await self.populate_batch(batch)
                
                total_level1 += batch_stats['level1_total']
                total_level2 += batch_stats['level2_total']
                
                self.current_progress['level1_divisions'] = total_level1
                self.current_progress['level2_divisions'] = total_level2
                
                # Update progress in database for persistence
                await self.db.administrative_divisions_progress.update_one(
                    {'_id': 'current'},
                    {'$set': self.current_progress},
                    upsert=True
                )
                
                logger.info(f"✅ Batch {batch_idx + 1} complete: {batch_stats['processed']} processed, {batch_stats['successful']} successful")
            
            # Mark as complete
            self.current_progress['status'] = 'completed'
            self.current_progress['completed_at'] = datetime.utcnow().isoformat()
            
            await self.db.administrative_divisions_progress.update_one(
                {'_id': 'current'},
                {'$set': self.current_progress},
                upsert=True
            )
            
            logger.info(f"🎉 Population complete! {total_level1} Level 1, {total_level2} Level 2 divisions")
            
            return {
                'status': 'completed',
                'summary': self.current_progress
            }
            
        except Exception as e:
            logger.error(f"❌ Population error: {e}")
            self.current_progress['status'] = 'error'
            self.current_progress['error'] = str(e)
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            self.is_processing = False
    
    async def get_progress(self) -> Dict[str, Any]:
        """Get current population progress"""
        # Check database for persisted progress
        db_progress = await self.db.administrative_divisions_progress.find_one({'_id': 'current'})
        
        if db_progress:
            return db_progress
        
        return self.current_progress
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get division statistics"""
        try:
            total_divisions = await self.db.administrative_divisions.count_documents({})
            level1_count = await self.db.administrative_divisions.count_documents({'type': 'level1'})
            
            # Get unique countries
            countries = await self.db.administrative_divisions.distinct('country_code')
            
            return {
                'total_divisions': total_divisions,
                'level1_divisions': level1_count,
                'level2_divisions': total_divisions - level1_count,
                'countries_with_data': len(countries),
                'cache_entries': await self.db.administrative_divisions_cache.count_documents({})
            }
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return {'error': str(e)}


# Singleton instance
_optimized_divisions_manager = None

def get_optimized_divisions_manager():
    """Get singleton instance"""
    global _optimized_divisions_manager
    if _optimized_divisions_manager is None:
        _optimized_divisions_manager = OptimizedAdministrativeDivisionsManager()
    return _optimized_divisions_manager
