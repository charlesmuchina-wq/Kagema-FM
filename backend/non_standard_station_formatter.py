"""Non-Standard Station Formatter
Creates standardized identifiers for radio stations without ITU call signs
Uses frequency, numeric identifiers, and geographic data
"""
import re
import logging
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class NonStandardStationFormatter:
    """Formats stations without call signs into standardized identifiers"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Stats
        self.stats = {
            'stations_processed': 0,
            'formatted': 0,
            'failed': 0
        }
        
        logger.info("Non-Standard Station Formatter initialized")
    
    def extract_frequency(self, name: str, metadata: Dict = None) -> Optional[float]:
        """Extract frequency from station name or metadata"""
        try:
            # Try metadata first
            if metadata:
                if 'frequency' in metadata:
                    return float(metadata['frequency'])
            
            # Common frequency patterns in names
            patterns = [
                r'(\d+\.?\d*)\s*(?:FM|MHz)',  # 95.5 FM, 98 FM, 100.7MHz
                r'FM\s*(\d+\.?\d*)',  # FM 95.5
                r'(\d+\.?\d*)\s*KHz',  # 1530 KHz
                r'AM\s*(\d+)',  # AM 1530
            ]
            
            name_upper = name.upper()
            
            for pattern in patterns:
                match = re.search(pattern, name_upper)
                if match:
                    freq = float(match.group(1))
                    
                    # Validate frequency ranges
                    # FM: 87.5 - 108 MHz
                    if 87.5 <= freq <= 108:
                        return freq
                    
                    # AM: 530 - 1700 KHz (convert to MHz for consistency)
                    if 530 <= freq <= 1700:
                        return freq / 1000  # Convert KHz to MHz
                    
                    # If already in MHz
                    if 0.530 <= freq <= 1.700:
                        return freq
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting frequency: {e}")
            return None
    
    def extract_numeric_identifier(self, name: str) -> Optional[int]:
        """Extract numeric identifier from station name"""
        try:
            # Look for numeric patterns
            patterns = [
                r'(\d+)',  # Any number
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, name)
                if matches:
                    # Return first meaningful number (prefer larger numbers)
                    numbers = [int(m) for m in matches if int(m) > 0]
                    if numbers:
                        # Prefer numbers in typical range (1-999)
                        for num in numbers:
                            if 1 <= num <= 999:
                                return num
                        return numbers[0]
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting numeric ID: {e}")
            return None
    
    def clean_station_name(self, name: str) -> str:
        """Clean station name by removing frequency and technical info"""
        # Remove frequency markers
        cleaned = re.sub(r'\d+\.?\d*\s*(?:FM|MHz|KHz|AM)', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Remove leading/trailing special characters
        cleaned = cleaned.strip('- .')
        
        return cleaned or name
    
    def generate_standard_id(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Generate standardized identifier for non-call-sign station"""
        try:
            name = station.get('name', '')
            country = station.get('country', 'XX')
            
            # Get division info if available
            division_l1 = station.get('division_level1_name', '')
            division_l2 = station.get('division_level2_name', '')
            
            # Extract frequency
            frequency = self.extract_frequency(name, station.get('metadata', {}))
            
            # Extract numeric identifier
            numeric_id = self.extract_numeric_identifier(name)
            
            # Clean station name
            clean_name = self.clean_station_name(name)
            
            # Generate standard ID components
            components = []
            
            # Format 1: Country-Frequency-Name
            if frequency:
                freq_str = f"{frequency:.1f}".replace('.', '')
                components.append(f"{country}-FM{freq_str}")
                standard_id = f"{country}-FM{freq_str}"
                display_name = f"{clean_name} ({frequency:.1f} FM)"
                format_type = 'frequency_based'
            
            # Format 2: Country-Number-Name
            elif numeric_id:
                components.append(f"{country}-R{numeric_id}")
                standard_id = f"{country}-R{numeric_id}"
                display_name = f"{clean_name} (R{numeric_id})"
                format_type = 'numeric_based'
            
            # Format 3: Country-Region-Sequential
            else:
                # Use first letters of name as identifier
                name_code = ''.join([c for c in clean_name[:6] if c.isalnum()]).upper()
                if not name_code:
                    name_code = 'RADIO'
                
                standard_id = f"{country}-{name_code}"
                display_name = clean_name
                format_type = 'name_based'
            
            # Add region if available
            region_code = None
            if division_l1:
                # Take first 3 letters of division
                region_code = ''.join([c for c in division_l1[:3] if c.isalnum()]).upper()
            
            return {
                'standard_id': standard_id,
                'display_name': display_name,
                'clean_name': clean_name,
                'frequency': frequency,
                'numeric_id': numeric_id,
                'format_type': format_type,
                'region_code': region_code,
                'components': {
                    'country': country,
                    'frequency': frequency,
                    'numeric_id': numeric_id,
                    'name_code': clean_name[:10],
                    'region': division_l1 or division_l2
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating standard ID: {e}")
            return None
    
    async def format_station(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single non-standard station"""
        try:
            # Skip if already has call sign
            if station.get('call_sign'):
                return {
                    'status': 'skipped',
                    'reason': 'has_call_sign',
                    'station_id': station.get('id')
                }
            
            # Generate standard ID
            standard_info = self.generate_standard_id(station)
            
            if standard_info:
                # Update station with standardized info
                update_data = {
                    'standard_id': standard_info['standard_id'],
                    'standard_display_name': standard_info['display_name'],
                    'clean_name': standard_info['clean_name'],
                    'extracted_frequency': standard_info['frequency'],
                    'numeric_identifier': standard_info['numeric_id'],
                    'standardization_format': standard_info['format_type'],
                    'region_code': standard_info['region_code'],
                    'standardization_components': standard_info['components'],
                    'is_standardized': True
                }
                
                # Update in database
                await self.db.radio_stations.update_one(
                    {'_id': station['_id']},
                    {'$set': update_data}
                )
                
                self.stats['formatted'] += 1
                
                return {
                    'status': 'success',
                    'station_id': station.get('id'),
                    'standard_id': standard_info['standard_id']
                }
            else:
                self.stats['failed'] += 1
                return {
                    'status': 'failed',
                    'station_id': station.get('id'),
                    'reason': 'unable_to_generate_id'
                }
                
        except Exception as e:
            logger.error(f"Error formatting station: {e}")
            self.stats['failed'] += 1
            return {
                'status': 'error',
                'station_id': station.get('id'),
                'error': str(e)
            }
        finally:
            self.stats['stations_processed'] += 1
    
    async def format_all_non_standard_stations(self, batch_size: int = 100) -> Dict[str, Any]:
        """Format all stations without call signs"""
        logger.info("Starting non-standard station formatting")
        
        # Get all stations without call signs
        stations = await self.db.radio_stations.find({
            '$or': [
                {'call_sign': {'$exists': False}},
                {'call_sign': None}
            ]
        }).to_list(length=None)
        
        total_stations = len(stations)
        logger.info(f"Found {total_stations} stations without call signs")
        
        # Process in batches
        for i in range(0, total_stations, batch_size):
            batch = stations[i:i + batch_size]
            
            for station in batch:
                await self.format_station(station)
            
            if (i + batch_size) % 1000 == 0:
                logger.info(f"Processed {i + batch_size}/{total_stations} stations")
        
        logger.info(f"Non-standard formatting complete: {self.stats}")
        
        return {
            'status': 'success',
            'stats': self.stats,
            'total_processed': self.stats['stations_processed']
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get formatting statistics"""
        # Count stations with standard IDs
        with_standard_ids = await self.db.radio_stations.count_documents({
            'standard_id': {'$exists': True, '$ne': None}
        })
        
        # Count by format type
        format_breakdown = await self.db.radio_stations.aggregate([
            {'$match': {'standardization_format': {'$exists': True}}},
            {'$group': {
                '_id': '$standardization_format',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]).to_list(length=100)
        
        total = await self.db.radio_stations.count_documents({})
        
        return {
            'total_stations': total,
            'with_standard_ids': with_standard_ids,
            'format_breakdown': {
                item['_id']: item['count'] 
                for item in format_breakdown
            },
            'coverage_percentage': round((with_standard_ids / total * 100), 2) if total > 0 else 0,
            'processing_stats': self.stats
        }
    
    async def get_examples_by_format(self, format_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get example stations for a specific format type"""
        stations = await self.db.radio_stations.find({
            'standardization_format': format_type
        }).limit(limit).to_list(length=limit)
        
        return [{
            'name': s.get('name'),
            'standard_id': s.get('standard_id'),
            'display_name': s.get('standard_display_name'),
            'country': s.get('country'),
            'frequency': s.get('extracted_frequency'),
            'numeric_id': s.get('numeric_identifier')
        } for s in stations]


# Global instance
non_standard_formatter_instance = None


def get_non_standard_formatter() -> NonStandardStationFormatter:
    """Get or create non-standard formatter instance"""
    global non_standard_formatter_instance
    if non_standard_formatter_instance is None:
        non_standard_formatter_instance = NonStandardStationFormatter()
    return non_standard_formatter_instance
