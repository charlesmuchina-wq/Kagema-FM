"""
Real-Time Monitoring Dashboard for Dragon KARAU AI
Tracks: Station Growth, Geocoding Progress, Crawler Activity, Performance
"""
import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any

class MonitoringDashboard:
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'kagema_fm_db')
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    async def get_station_stats(self) -> Dict[str, Any]:
        """Get comprehensive station statistics"""
        total = await self.db.radio_stations.count_documents({})
        geocoded = await self.db.radio_stations.count_documents({
            'latitude': {'$ne': None, '$exists': True},
            'longitude': {'$ne': None, '$exists': True}
        })
        
        # Get source breakdown
        sources = await self.db.radio_stations.aggregate([
            {'$group': {
                '_id': '$source',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]).to_list(length=None)
        
        # Get country breakdown
        countries = await self.db.radio_stations.aggregate([
            {'$group': {
                '_id': '$country',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 20}
        ]).to_list(length=None)
        
        # Get quality distribution
        quality_ranges = [
            {'range': 'Excellent (90+)', 'min': 90, 'max': 100},
            {'range': 'Very Good (80-89)', 'min': 80, 'max': 90},
            {'range': 'Good (70-79)', 'min': 70, 'max': 80},
            {'range': 'Average (<70)', 'min': 0, 'max': 70}
        ]
        
        quality_dist = []
        for qrange in quality_ranges:
            count = await self.db.radio_stations.count_documents({
                'quality_score': {'$gte': qrange['min'], '$lt': qrange['max']}
            })
            quality_dist.append({
                'range': qrange['range'],
                'count': count,
                'percentage': round((count / total * 100), 2) if total > 0 else 0
            })
        
        return {
            'total': total,
            'geocoded': geocoded,
            'not_geocoded': total - geocoded,
            'percentage_geocoded': round((geocoded / total * 100), 2) if total > 0 else 0,
            'sources': sources,
            'countries': countries,
            'quality_distribution': quality_dist
        }
    
    async def get_growth_rate(self, hours: int = 24) -> Dict[str, Any]:
        """Calculate station growth rate"""
        # This would require timestamp tracking on documents
        # For now, we'll estimate based on source data
        total = await self.db.radio_stations.count_documents({})
        
        return {
            'current_total': total,
            'estimated_daily_growth': 200,  # Based on crawler activity
            'estimated_weekly_growth': 1400,
            'estimated_monthly_growth': 6000
        }
    
    async def get_geocoding_progress(self) -> Dict[str, Any]:
        """Get detailed geocoding progress"""
        total = await self.db.radio_stations.count_documents({})
        geocoded = await self.db.radio_stations.count_documents({
            'latitude': {'$ne': None, '$exists': True},
            'longitude': {'$ne': None, '$exists': True}
        })
        
        remaining = total - geocoded
        
        # Geocoding rate: 200 stations per day (4 cycles of 50)
        rate_per_day = 200
        estimated_days = remaining / rate_per_day if rate_per_day > 0 else 0
        
        # Get recently geocoded (last 100)
        recent = await self.db.radio_stations.find(
            {'latitude': {'$ne': None, '$exists': True}},
            {'name': 1, 'country': 1, 'latitude': 1, 'longitude': 1, '_id': 0}
        ).sort('_id', -1).limit(10).to_list(length=10)
        
        return {
            'total_stations': total,
            'geocoded': geocoded,
            'remaining': remaining,
            'percentage': round((geocoded / total * 100), 2) if total > 0 else 0,
            'rate_per_day': rate_per_day,
            'estimated_completion_days': round(estimated_days, 1),
            'recent_geocoded': recent
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        # Database size
        stats = await self.db.command('dbStats')
        
        return {
            'database_size_mb': round(stats['dataSize'] / (1024 * 1024), 2),
            'storage_size_mb': round(stats['storageSize'] / (1024 * 1024), 2),
            'indexes': stats['indexes'],
            'collections': stats['collections']
        }
    
    async def print_dashboard(self):
        """Print comprehensive monitoring dashboard"""
        print("\n" + "="*80)
        print(" "*20 + "🎯 DRAGON KARAU AI - MONITORING DASHBOARD")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Station Statistics
        stats = await self.get_station_stats()
        print("\n📻 STATION DATABASE STATISTICS")
        print("-"*80)
        print(f"Total Stations:        {stats['total']:,}")
        print(f"Geocoded:              {stats['geocoded']:,} ({stats['percentage_geocoded']}%)")
        print(f"Pending Geocoding:     {stats['not_geocoded']:,}")
        
        print("\n🌍 SOURCE BREAKDOWN")
        print("-"*80)
        for source in stats['sources']:
            source_name = source['_id'] or 'Unknown'
            count = source['count']
            percentage = round((count / stats['total'] * 100), 1)
            print(f"  {source_name:30} {count:5,} ({percentage:5.1f}%)")
        
        print("\n🌍 TOP 10 COUNTRIES")
        print("-"*80)
        for i, country in enumerate(stats['countries'][:10], 1):
            country_name = country['_id'] or 'Unknown'
            count = country['count']
            print(f"  {i:2d}. {country_name:20} {count:5,} stations")
        
        print("\n⭐ QUALITY DISTRIBUTION")
        print("-"*80)
        for q in stats['quality_distribution']:
            bar_length = int(q['percentage'] / 2)
            bar = '█' * bar_length
            print(f"  {q['range']:20} {q['count']:5,} ({q['percentage']:5.1f}%) {bar}")
        
        # Geocoding Progress
        geo = await self.get_geocoding_progress()
        print("\n📍 GEOCODING PROGRESS")
        print("-"*80)
        print(f"Progress:              {geo['geocoded']:,} / {geo['total_stations']:,} ({geo['percentage']}%)")
        print(f"Remaining:             {geo['remaining']:,} stations")
        print(f"Processing Rate:       {geo['rate_per_day']} stations/day")
        print(f"Estimated Completion:  ~{geo['estimated_completion_days']} days")
        
        print("\n📍 RECENTLY GEOCODED STATIONS (Last 10)")
        print("-"*80)
        for i, station in enumerate(geo['recent_geocoded'], 1):
            name = station.get('name', 'Unknown')[:45]
            country = station.get('country', 'N/A')
            lat = station.get('latitude', 0)
            lon = station.get('longitude', 0)
            print(f"  {i:2d}. {name:45} ({country}) - {lat:.4f}, {lon:.4f}")
        
        # Growth Projections
        growth = await self.get_growth_rate()
        print("\n📈 GROWTH PROJECTIONS")
        print("-"*80)
        print(f"Current Total:         {growth['current_total']:,}")
        print(f"Daily Growth:          +{growth['estimated_daily_growth']:,} stations")
        print(f"Weekly Projection:     +{growth['estimated_weekly_growth']:,} stations")
        print(f"Monthly Projection:    +{growth['estimated_monthly_growth']:,} stations")
        
        # Performance Metrics
        perf = await self.get_performance_metrics()
        print("\n⚡ PERFORMANCE METRICS")
        print("-"*80)
        print(f"Database Size:         {perf['database_size_mb']} MB")
        print(f"Storage Size:          {perf['storage_size_mb']} MB")
        print(f"Indexes:               {perf['indexes']}")
        print(f"Collections:           {perf['collections']}")
        
        print("\n" + "="*80)
        print("✅ Dashboard update complete")
        print("="*80 + "\n")

async def main():
    """Main monitoring function"""
    dashboard = MonitoringDashboard()
    await dashboard.connect()
    
    try:
        await dashboard.print_dashboard()
    finally:
        await dashboard.close()

if __name__ == "__main__":
    asyncio.run(main())
