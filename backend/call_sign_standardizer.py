"""Call Sign Standardizer
Standardizes radio station names and call signs according to international broadcast standards
Based on ITU (International Telecommunication Union) call sign conventions
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CallSignStandardizer:
    """Standardizes broadcast call signs according to international conventions"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Call sign patterns by country (ITU prefixes)
        self.call_sign_patterns = {
            # North America
            'US': {
                'patterns': [
                    r'^[KW][A-Z]{2,3}(-FM|-TV|-AM)?$',  # K/W + 3-4 letters
                ],
                'prefixes': ['K', 'W'],
                'format': 'K/W + 3-4 letters + suffix'
            },
            'CA': {
                'patterns': [
                    r'^C[BF-K][A-Z]{1,2}(-FM|-TV)?$',  # CB, CF-CK + letters
                    r'^VO[A-Z]{2}(-FM)?$',  # Newfoundland VO prefix
                ],
                'prefixes': ['CB', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'VO'],
                'format': 'C + letter + 1-2 letters + suffix'
            },
            'MX': {
                'patterns': [
                    r'^X[EH][A-Z]{1,4}(-FM|-TV|-TDT)?$',  # XE/XH + letters
                ],
                'prefixes': ['XE', 'XH'],
                'format': 'XE/XH + 1-4 letters + suffix'
            },
            
            # Central America
            'CR': {'patterns': [r'^TI-[A-Z]{2,4}$'], 'prefixes': ['TI'], 'format': 'TI-XXX'},
            'SV': {'patterns': [r'^YS[A-Z]{1,3}(-TV)?$'], 'prefixes': ['YS', 'YX', 'HU'], 'format': 'YS + letters'},
            'GT': {'patterns': [r'^TG[A-Z]{1,4}(-TV)?$'], 'prefixes': ['TG'], 'format': 'TG + letters'},
            'HN': {'patterns': [r'^HR[A-Z]{2,4}(-TV)?$'], 'prefixes': ['HR'], 'format': 'HR + letters'},
            'NI': {'patterns': [r'^YN[A-Z]{2,4}$'], 'prefixes': ['YN'], 'format': 'YN + letters'},
            
            # Caribbean
            'DO': {'patterns': [r'^HI[A-Z]{1,4}$'], 'prefixes': ['HI'], 'format': 'HI + letters'},
            
            # South America
            'AR': {'patterns': [r'^L[RST-W]\d{1,3}(-TV)?$'], 'prefixes': ['LR', 'LS', 'LT', 'LU', 'LV', 'LW'], 'format': 'L + letter + number'},
            'BO': {'patterns': [r'^CP\s?\d{1,3}\s?TV$'], 'prefixes': ['CP'], 'format': 'CP + number + TV'},
            'BR': {'patterns': [r'^ZY[A-Z]\d{3}$'], 'prefixes': ['ZYA', 'ZYB', 'ZYC', 'ZYD', 'ZYG', 'ZYI', 'ZYJ', 'ZYK', 'ZYL', 'ZYM', 'ZYR', 'ZYT', 'ZYU'], 'format': 'ZY + letter + 3 numbers'},
            'CL': {'patterns': [r'^X[QR][A-E]\d{1,3}$'], 'prefixes': ['XQ', 'XR'], 'format': 'XQ/XR + letter + number'},
            'CO': {'patterns': [r'^H[JK][A-Z]{2,4}$'], 'prefixes': ['HJ', 'HK'], 'format': 'HJ/HK + letters'},
            'PY': {'patterns': [r'^ZPV\s?\d{3}\s?TV$'], 'prefixes': ['ZPV'], 'format': 'ZPV + 3 numbers + TV'},
            'PE': {'patterns': [r'^O[A-C][A-Z]-\d[A-Z]$'], 'prefixes': ['OA', 'OB', 'OC'], 'format': 'OA-OC + letter-number-letter'},
            'UY': {'patterns': [r'^CXB\d{1,3}$'], 'prefixes': ['CXB'], 'format': 'CXB + number'},
            'VE': {'patterns': [r'^YV[A-Z]{2,4}$'], 'prefixes': ['YV'], 'format': 'YV + letters'},
            
            # Asia
            'ID': {'patterns': [r'^PM\d[BCDF][A-Z]{2}$'], 'prefixes': ['PM'], 'format': 'PM + number + letter + 2 letters'},
            'JP': {'patterns': [r'^JO[A-Z]{2,4}$'], 'prefixes': ['JO'], 'format': 'JO + letters'},
            'PH': {'patterns': [r'^D[WYX][A-Z]{1,4}(-FM|-TV)?$'], 'prefixes': ['DW', 'DY', 'DX', 'DZ'], 'format': 'DW/DY/DX + letters'},
            'TW': {'patterns': [r'^BET\d{2}$'], 'prefixes': ['BET'], 'format': 'BET + 2 numbers'},
            
            # Oceania
            'AU': {
                'patterns': [
                    r'^\d[A-Z]{2,3}(-FM)?$',  # Number + letters
                    r'^VL\d[A-Z]{2,3}$',  # VL prefix (legacy)
                ],
                'prefixes': ['2', '3', '4', '5', '6', '7', '8', 'VL'],
                'format': 'Number + 2-3 letters'
            },
        }
        
        # Stats
        self.stats = {
            'stations_processed': 0,
            'call_signs_extracted': 0,
            'standardized': 0,
            'failed': 0
        }
        
        logger.info("Call Sign Standardizer initialized")
    
    def extract_call_sign(self, station_name: str, country: str) -> Optional[Dict[str, Any]]:
        """Extract and validate call sign from station name"""
        try:
            # Clean up the name
            name_upper = station_name.upper().strip()
            
            # Get country-specific patterns
            if country not in self.call_sign_patterns:
                # Try to extract generic format
                return self._extract_generic_call_sign(name_upper)
            
            country_config = self.call_sign_patterns[country]
            
            # Try each pattern for this country
            for pattern in country_config['patterns']:
                match = re.search(pattern, name_upper)
                if match:
                    call_sign = match.group(0)
                    return {
                        'call_sign': call_sign,
                        'prefix': call_sign[:2] if len(call_sign) >= 2 else call_sign[0],
                        'country': country,
                        'valid': True,
                        'format': country_config['format'],
                        'standardized_name': self._format_standardized_name(call_sign, station_name)
                    }
            
            # Try to find prefix match in name
            for prefix in country_config['prefixes']:
                if name_upper.startswith(prefix):
                    # Extract potential call sign
                    potential = name_upper.split()[0] if ' ' in name_upper else name_upper[:8]
                    return {
                        'call_sign': potential,
                        'prefix': prefix,
                        'country': country,
                        'valid': False,  # Doesn't match exact pattern
                        'format': country_config['format'],
                        'standardized_name': self._format_standardized_name(potential, station_name)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting call sign: {e}")
            return None
    
    def _extract_generic_call_sign(self, name: str) -> Optional[Dict[str, Any]]:
        """Extract call sign using generic patterns"""
        # Look for patterns like: 2-4 letters followed by optional numbers
        generic_patterns = [
            r'^[A-Z]{2,4}\d{0,3}(-FM|-TV|-AM)?',  # Letters + optional numbers + suffix
            r'^\d[A-Z]{2,3}(-FM)?',  # Number + letters (Australian style)
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, name)
            if match:
                call_sign = match.group(0)
                return {
                    'call_sign': call_sign,
                    'prefix': call_sign[:2],
                    'country': 'UNKNOWN',
                    'valid': False,
                    'format': 'Generic',
                    'standardized_name': call_sign
                }
        
        return None
    
    def _format_standardized_name(self, call_sign: str, original_name: str) -> str:
        """Format standardized station name"""
        # Remove extra whitespace and standardize
        call_sign_clean = call_sign.replace(' ', '').upper()
        
        # If original name has additional info, preserve it
        if len(original_name) > len(call_sign):
            # Extract brand name if present
            parts = original_name.split('-')
            if len(parts) > 1:
                brand = parts[-1].strip()
                return f"{call_sign_clean} - {brand}"
        
        return call_sign_clean
    
    async def standardize_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize a single station's call sign"""
        try:
            station_name = station.get('name', '')
            country = station.get('country', '')
            
            if not station_name or not country:
                return {
                    'status': 'skipped',
                    'reason': 'missing_data',
                    'station_id': station.get('id')
                }
            
            # Extract call sign
            call_sign_info = self.extract_call_sign(station_name, country)
            
            if call_sign_info:
                # Update station with standardized info
                update_data = {
                    'call_sign': call_sign_info['call_sign'],
                    'call_sign_prefix': call_sign_info['prefix'],
                    'call_sign_valid': call_sign_info['valid'],
                    'call_sign_format': call_sign_info['format'],
                    'standardized_name': call_sign_info['standardized_name'],
                    'original_name': station_name  # Preserve original
                }
                
                # Update in database
                await self.db.radio_stations.update_one(
                    {'_id': station['_id']},
                    {'$set': update_data}
                )
                
                self.stats['call_signs_extracted'] += 1
                self.stats['standardized'] += 1
                
                return {
                    'status': 'success',
                    'station_id': station.get('id'),
                    'call_sign': call_sign_info['call_sign']
                }
            else:
                self.stats['failed'] += 1
                return {
                    'status': 'no_call_sign',
                    'station_id': station.get('id'),
                    'reason': 'pattern_not_matched'
                }
                
        except Exception as e:
            logger.error(f"Error standardizing station: {e}")
            self.stats['failed'] += 1
            return {
                'status': 'error',
                'station_id': station.get('id'),
                'error': str(e)
            }
        finally:
            self.stats['stations_processed'] += 1
    
    async def standardize_all_stations(self, batch_size: int = 100) -> Dict[str, Any]:
        """Standardize call signs for all stations"""
        logger.info("Starting call sign standardization for all stations")
        
        # Get all stations
        stations = await self.db.radio_stations.find({}).to_list(length=None)
        total_stations = len(stations)
        
        logger.info(f"Processing {total_stations} stations for call sign standardization")
        
        # Process in batches
        for i in range(0, total_stations, batch_size):
            batch = stations[i:i + batch_size]
            
            for station in batch:
                await self.standardize_station(station)
            
            if (i + batch_size) % 1000 == 0:
                logger.info(f"Processed {i + batch_size}/{total_stations} stations")
        
        logger.info(f"Call sign standardization complete: {self.stats}")
        
        return {
            'status': 'success',
            'stats': self.stats,
            'total_processed': self.stats['stations_processed']
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get standardization statistics"""
        # Count stations with call signs
        with_call_signs = await self.db.radio_stations.count_documents({
            'call_sign': {'$exists': True, '$ne': None}
        })
        
        valid_call_signs = await self.db.radio_stations.count_documents({
            'call_sign_valid': True
        })
        
        total = await self.db.radio_stations.count_documents({})
        
        return {
            'total_stations': total,
            'with_call_signs': with_call_signs,
            'valid_call_signs': valid_call_signs,
            'without_call_signs': total - with_call_signs,
            'coverage_percentage': round((with_call_signs / total * 100), 2) if total > 0 else 0,
            'valid_percentage': round((valid_call_signs / with_call_signs * 100), 2) if with_call_signs > 0 else 0,
            'processing_stats': self.stats
        }
    
    async def get_call_sign_by_country(self, country: str) -> Dict[str, Any]:
        """Get call sign statistics for a specific country"""
        pipeline = [
            {'$match': {'country': country}},
            {'$group': {
                '_id': '$call_sign_prefix',
                'count': {'$sum': 1},
                'valid': {'$sum': {'$cond': [{'$eq': ['$call_sign_valid', True]}, 1, 0]}}
            }},
            {'$sort': {'count': -1}}
        ]
        
        prefix_breakdown = await self.db.radio_stations.aggregate(pipeline).to_list(length=100)
        
        total = await self.db.radio_stations.count_documents({'country': country})
        with_call_signs = await self.db.radio_stations.count_documents({
            'country': country,
            'call_sign': {'$exists': True, '$ne': None}
        })
        
        return {
            'country': country,
            'total_stations': total,
            'with_call_signs': with_call_signs,
            'prefix_breakdown': prefix_breakdown,
            'expected_format': self.call_sign_patterns.get(country, {}).get('format', 'Not defined')
        }


# Global instance
call_sign_standardizer_instance = None


def get_call_sign_standardizer() -> CallSignStandardizer:
    """Get or create call sign standardizer instance"""
    global call_sign_standardizer_instance
    if call_sign_standardizer_instance is None:
        call_sign_standardizer_instance = CallSignStandardizer()
    return call_sign_standardizer_instance
