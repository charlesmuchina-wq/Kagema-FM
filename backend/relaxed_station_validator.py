"""Relaxed Station Validator
Fast validation system that checks basic fields instead of stream accessibility
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)

class RelaxedStationValidator:
    """Validates stations based on required fields without testing stream"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        self.stations = self.db.radio_stations
        
        self.required_fields = ['name', 'stream_url', 'country']
        self.stats = {
            'processed': 0,
            'validated': 0,
            'failed': 0
        }
    
    def validate_station(self, station: Dict[str, Any]) -> bool:
        """Quick validation - check if required fields exist and are valid"""
        try:
            # Check required fields exist
            for field in self.required_fields:
                if not station.get(field):
                    return False
            
            # Validate stream URL format
            stream_url = station.get('stream_url', '')
            if not stream_url.startswith(('http://', 'https://')):
                return False
            
            # Validate name is not empty or generic
            name = station.get('name', '').strip()
            if len(name) < 2 or name.lower() in ['unknown', 'untitled', 'n/a']:
                return False
            
            # Validate country code format (2-3 letters)
            country = station.get('country', '').strip()
            if not (2 <= len(country) <= 3) or not country.isalpha():
                return False
            
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    async def validate_all_stations(self) -> Dict[str, Any]:
        """Bulk validate all stations in database"""
        logger.info("Starting bulk validation...")
        
        cursor = self.stations.find({})
        async for station in cursor:
            self.stats['processed'] += 1
            
            if self.validate_station(station):
                # Mark as validated
                await self.stations.update_one(
                    {'_id': station['_id']},
                    {
                        '$set': {
                            'validated': True,
                            'validation_method': 'relaxed',
                            'validated_at': datetime.utcnow()
                        }
                    }
                )
                self.stats['validated'] += 1
            else:
                self.stats['failed'] += 1
            
            # Log progress every 100 stations
            if self.stats['processed'] % 100 == 0:
                logger.info(f"Processed {self.stats['processed']} stations...")
        
        validation_rate = (self.stats['validated'] / self.stats['processed'] * 100) if self.stats['processed'] > 0 else 0
        
        logger.info(f"Validation complete: {self.stats['validated']}/{self.stats['processed']} ({validation_rate:.1f}%)")
        
        return {
            'total_processed': self.stats['processed'],
            'validated': self.stats['validated'],
            'failed': self.stats['failed'],
            'validation_rate': f"{validation_rate:.1f}%"
        }
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get current validation statistics"""
        total = await self.stations.count_documents({})
        validated = await self.stations.count_documents({'validated': True})
        
        return {
            'total_stations': total,
            'validated': validated,
            'unvalidated': total - validated,
            'validation_rate': f"{(validated/total*100):.1f}%" if total > 0 else "0%"
        }


async def main():
    """Run bulk validation"""
    validator = RelaxedStationValidator()
    result = await validator.validate_all_stations()
    print("\n✅ Validation Complete!")
    print(f"  Processed: {result['total_processed']}")
    print(f"  Validated: {result['validated']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Rate: {result['validation_rate']}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
