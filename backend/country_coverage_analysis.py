"""Country Coverage Analysis
Analyzes radio station coverage across countries and continents
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

logger = logging.getLogger(__name__)

class CountryCoverageAnalyzer:
    """Analyzes geographic coverage of radio stations"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.db = self.mongo_client[db_name]
        self.stations = self.db.radio_stations
        
        # Continent mapping
        self.continent_map = {
            'AF': ['DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'YT', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RE', 'RW', 'SH', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW'],
            'AS': ['AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'GE', 'HK', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KP', 'KR', 'KW', 'KG', 'LA', 'LB', 'MO', 'MY', 'MV', 'MN', 'MM', 'NP', 'OM', 'PK', 'PS', 'PH', 'QA', 'SA', 'SG', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TL', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE'],
            'EU': ['AX', 'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FO', 'FI', 'FR', 'DE', 'GI', 'GR', 'GG', 'HU', 'IS', 'IE', 'IM', 'IT', 'JE', 'XK', 'LV', 'LI', 'LT', 'LU', 'MK', 'MT', 'MD', 'MC', 'ME', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SJ', 'SE', 'CH', 'UA', 'GB', 'VA'],
            'NA': ['AI', 'AG', 'AW', 'BS', 'BB', 'BZ', 'BM', 'BQ', 'CA', 'KY', 'CR', 'CU', 'CW', 'DM', 'DO', 'SV', 'GL', 'GD', 'GP', 'GT', 'HT', 'HN', 'JM', 'MQ', 'MX', 'MS', 'NI', 'PA', 'PR', 'BL', 'KN', 'LC', 'MF', 'PM', 'VC', 'SX', 'TT', 'TC', 'US', 'VG', 'VI'],
            'SA': ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'FK', 'GF', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE'],
            'OC': ['AS', 'AU', 'CK', 'FJ', 'PF', 'GU', 'KI', 'MH', 'FM', 'NR', 'NC', 'NZ', 'NU', 'NF', 'MP', 'PW', 'PG', 'PN', 'WS', 'SB', 'TK', 'TO', 'TV', 'UM', 'VU', 'WF']
        }
    
    def get_continent(self, country_code: str) -> str:
        """Get continent code for a country"""
        for continent, countries in self.continent_map.items():
            if country_code.upper() in countries:
                return continent
        return 'UNKNOWN'
    
    async def analyze_coverage(self) -> Dict[str, Any]:
        """Comprehensive coverage analysis"""
        # Get country distribution
        country_pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        country_stats = await self.stations.aggregate(country_pipeline).to_list(length=None)
        
        # Calculate continent distribution
        continent_counts = {cont: 0 for cont in ['AF', 'AS', 'EU', 'NA', 'SA', 'OC', 'UNKNOWN']}
        for stat in country_stats:
            continent = self.get_continent(stat['_id'])
            continent_counts[continent] += stat['count']
        
        # Get top 10 countries
        top_countries = country_stats[:10]
        
        # Get total stats
        total_stations = await self.stations.count_documents({})
        validated_stations = await self.stations.count_documents({'validated': True})
        unique_countries = len(country_stats)
        
        return {
            'total_stations': total_stations,
            'validated_stations': validated_stations,
            'unique_countries': unique_countries,
            'top_countries': top_countries,
            'continent_distribution': continent_counts,
            'coverage_percentage': f"{(unique_countries / 195 * 100):.1f}%"
        }
    
    async def get_countries_needing_stations(self, min_stations: int = 5) -> List[str]:
        """Get countries with fewer than min_stations"""
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$match': {'count': {'$lt': min_stations}}},
            {'$sort': {'count': 1}}
        ]
        
        results = await self.stations.aggregate(pipeline).to_list(length=None)
        return [r['_id'] for r in results]


async def main():
    """Run coverage analysis"""
    analyzer = CountryCoverageAnalyzer()
    coverage = await analyzer.analyze_coverage()
    
    print("\n📊 Coverage Analysis:")
    print(f"  Total Stations: {coverage['total_stations']}")
    print(f"  Validated: {coverage['validated_stations']}")
    print(f"  Countries: {coverage['unique_countries']}")
    print(f"  Coverage: {coverage['coverage_percentage']}")
    print("\n🌍 Top 10 Countries:")
    for i, country in enumerate(coverage['top_countries'], 1):
        print(f"  {i}. {country['_id']}: {country['count']} stations")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
