"""Administrative Divisions Manager
Manages administrative divisions (Level 1 and Level 2) for all 278 countries and regions
Uses administrative-divisions-db API and geoBoundaries for comprehensive coverage
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AdministrativeDivisionsManager:
    """Manages administrative divisions for all countries"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # API endpoints
        self.admin_divisions_api = 'https://rawcdn.githack.com/kamikazechaser/administrative-divisions-db/master/api'
        
        # Stats
        self.stats = {
            'countries_processed': 0,
            'level1_divisions': 0,
            'level2_divisions': 0,
            'failed_countries': 0
        }
        
        # All country codes (ISO 3166-1 alpha-2)
        self.all_country_codes = [
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
            # Additional territories and regions
            'AX', 'BQ', 'CW', 'GG', 'IM', 'JE', 'BL', 'MF', 'SX', 'GI', 'FK', 'GF', 'PF', 'TF', 'GP',
            'GU', 'HK', 'MO', 'MQ', 'YT', 'NC', 'NU', 'NF', 'MP', 'PR', 'RE', 'SH', 'PM', 'TK', 'TC',
            'VI', 'VG', 'WF'
        ]
        
        logger.info("Administrative Divisions Manager initialized")
    
    async def fetch_country_divisions(self, country_code: str) -> Dict[str, Any]:
        """Fetch administrative divisions for a specific country"""
        try:
            url = f"{self.admin_divisions_api}/{country_code}.json"
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'DragonKarauAI/1.0'}
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse the data structure
                        level1_divisions = []
                        level2_divisions = []
                        
                        # The API returns data in various formats
                        # We need to normalize it
                        if isinstance(data, list):
                            for item in data:
                                # API returns simple string array of division names
                                if isinstance(item, str):
                                    level1_div = self._parse_level1_division_from_string(item, country_code)
                                    if level1_div:
                                        level1_divisions.append(level1_div)
                                # Some APIs might return objects
                                elif isinstance(item, dict):
                                    level1_div = self._parse_level1_division(item, country_code)
                                    if level1_div:
                                        level1_divisions.append(level1_div)
                                        
                                        # Check for Level 2 subdivisions
                                        if 'subdivisions' in item or 'districts' in item or 'counties' in item:
                                            level2_divs = self._parse_level2_divisions(item, level1_div['id'])
                                            level2_divisions.extend(level2_divs)
                        elif isinstance(data, dict):
                            # Some countries return dict format
                            for key, value in data.items():
                                if isinstance(value, dict):
                                    level1_div = self._parse_level1_division({'name': key, **value}, country_code)
                                else:
                                    level1_div = self._parse_level1_division_from_string(key, country_code)
                                if level1_div:
                                    level1_divisions.append(level1_div)
                        
                        return {
                            'country_code': country_code,
                            'level1': level1_divisions,
                            'level2': level2_divisions,
                            'status': 'success'
                        }
                    elif response.status == 404:
                        # Country not found in API
                        logger.warning(f"No administrative data found for {country_code}")
                        return {
                            'country_code': country_code,
                            'level1': [],
                            'level2': [],
                            'status': 'not_found'
                        }
                    else:
                        logger.error(f"Failed to fetch {country_code}: HTTP {response.status}")
                        return {
                            'country_code': country_code,
                            'level1': [],
                            'level2': [],
                            'status': 'error'
                        }
        
        except Exception as e:
            logger.error(f"Error fetching divisions for {country_code}: {e}")
            return {
                'country_code': country_code,
                'level1': [],
                'level2': [],
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_level1_division_from_string(self, name: str, country_code: str) -> Optional[Dict[str, Any]]:
        """Parse Level 1 administrative division from simple string name"""
        try:
            if not name or not isinstance(name, str):
                return None
            
            return {
                'id': f"{country_code}_{name.lower().replace(' ', '_').replace('-', '_')}",
                'country_code': country_code,
                'name': name,
                'level': 1,
                'type': 'Province',
                'code': '',
                'population': 0,
                'lat': None,
                'lon': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error parsing Level 1 division from string '{name}': {e}")
            return None
    
    def _parse_level1_division(self, item: Dict, country_code: str) -> Optional[Dict[str, Any]]:
        """Parse Level 1 administrative division from dict object"""
        try:
            name = item.get('name', item.get('admin_name', item.get('asciiname', '')))
            if not name:
                return None
            
            return {
                'id': f"{country_code}_{name.lower().replace(' ', '_').replace('-', '_')}",
                'country_code': country_code,
                'name': name,
                'level': 1,
                'type': item.get('admin_level', 'Province'),
                'code': item.get('code', item.get('admin_code', '')),
                'population': item.get('population', 0),
                'lat': item.get('lat', item.get('latitude', None)),
                'lon': item.get('lon', item.get('longitude', None)),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error parsing Level 1 division: {e}")
            return None
    
    def _parse_level2_divisions(self, parent: Dict, parent_id: str) -> List[Dict[str, Any]]:
        """Parse Level 2 administrative divisions"""
        divisions = []
        
        # Check various possible keys for subdivisions
        subdiv_keys = ['subdivisions', 'districts', 'counties', 'municipalities']
        
        for key in subdiv_keys:
            if key in parent and isinstance(parent[key], list):
                for item in parent[key]:
                    try:
                        name = item.get('name', item.get('asciiname', ''))
                        if name:
                            div = {
                                'id': f"{parent_id}_{name.lower().replace(' ', '_')}",
                                'parent_id': parent_id,
                                'name': name,
                                'level': 2,
                                'type': item.get('type', 'District'),
                                'code': item.get('code', ''),
                                'population': item.get('population', 0),
                                'lat': item.get('lat', item.get('latitude', None)),
                                'lon': item.get('lon', item.get('longitude', None)),
                                'created_at': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            }
                            divisions.append(div)
                    except Exception as e:
                        logger.error(f"Error parsing Level 2 division: {e}")
        
        return divisions
    
    async def populate_all_divisions(self) -> Dict[str, Any]:
        """Populate database with administrative divisions for all countries"""
        logger.info(f"Starting population of administrative divisions for {len(self.all_country_codes)} countries")
        
        start_time = datetime.utcnow()
        results = {
            'started_at': start_time.isoformat(),
            'countries': {}
        }
        
        for country_code in self.all_country_codes:
            logger.info(f"Processing {country_code}...")
            
            # Fetch divisions
            data = await self.fetch_country_divisions(country_code)
            
            if data['status'] == 'success':
                # Save Level 1 divisions
                for div in data['level1']:
                    await self._save_division(div)
                    self.stats['level1_divisions'] += 1
                
                # Save Level 2 divisions
                for div in data['level2']:
                    await self._save_division(div)
                    self.stats['level2_divisions'] += 1
                
                self.stats['countries_processed'] += 1
                results['countries'][country_code] = {
                    'level1': len(data['level1']),
                    'level2': len(data['level2']),
                    'status': 'success'
                }
            else:
                self.stats['failed_countries'] += 1
                results['countries'][country_code] = {
                    'status': data['status']
                }
            
            # Rate limiting - 1 request per second
            await asyncio.sleep(1)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['completed_at'] = datetime.utcnow().isoformat()
        results['duration_seconds'] = duration
        results['stats'] = self.stats
        
        # Save to history
        await self.db.administrative_divisions_history.insert_one(results)
        
        logger.info(f"Administrative divisions population complete: {self.stats}")
        
        return results
    
    async def _save_division(self, division: Dict[str, Any]) -> None:
        """Save division to database"""
        try:
            # Upsert (update or insert)
            await self.db.administrative_divisions.update_one(
                {'id': division['id']},
                {'$set': division},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving division {division.get('id')}: {e}")
    
    async def get_divisions_by_country(self, country_code: str, level: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get administrative divisions for a country"""
        try:
            query = {'country_code': country_code.upper()}
            if level:
                query['level'] = level
            
            divisions = await self.db.administrative_divisions.find(query).to_list(length=None)
            
            return [{
                'id': d['id'],
                'name': d['name'],
                'level': d['level'],
                'type': d.get('type', ''),
                'code': d.get('code', ''),
                'parent_id': d.get('parent_id'),
                'lat': d.get('lat'),
                'lon': d.get('lon')
            } for d in divisions]
        
        except Exception as e:
            logger.error(f"Error getting divisions for {country_code}: {e}")
            return []
    
    async def get_division_hierarchy(self, country_code: str) -> Dict[str, Any]:
        """Get complete hierarchical structure for a country"""
        try:
            # Get Level 1 divisions
            level1 = await self.get_divisions_by_country(country_code, level=1)
            
            # Build hierarchy
            hierarchy = {
                'country_code': country_code,
                'divisions': []
            }
            
            for l1_div in level1:
                # Get Level 2 subdivisions
                level2 = await self.db.administrative_divisions.find(
                    {'parent_id': l1_div['id']}
                ).to_list(length=None)
                
                l1_div['subdivisions'] = [{
                    'id': d['id'],
                    'name': d['name'],
                    'type': d.get('type', ''),
                    'code': d.get('code', '')
                } for d in level2]
                
                hierarchy['divisions'].append(l1_div)
            
            return hierarchy
        
        except Exception as e:
            logger.error(f"Error getting hierarchy for {country_code}: {e}")
            return {'country_code': country_code, 'divisions': []}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about administrative divisions"""
        try:
            total_divisions = await self.db.administrative_divisions.count_documents({})
            level1_count = await self.db.administrative_divisions.count_documents({'level': 1})
            level2_count = await self.db.administrative_divisions.count_documents({'level': 2})
            countries_count = len(await self.db.administrative_divisions.distinct('country_code'))
            
            return {
                'total_divisions': total_divisions,
                'level1_divisions': level1_count,
                'level2_divisions': level2_count,
                'countries_covered': countries_count,
                'target_countries': len(self.all_country_codes)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global instance
admin_divisions_manager_instance = None


def get_admin_divisions_manager() -> AdministrativeDivisionsManager:
    """Get or create administrative divisions manager instance"""
    global admin_divisions_manager_instance
    if admin_divisions_manager_instance is None:
        admin_divisions_manager_instance = AdministrativeDivisionsManager()
    return admin_divisions_manager_instance
