"""
Analytics Dashboard Manager for Dragon KARAU AI
Task 21: Real-time analytics, user behavior tracking, trending analysis
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """Real-time analytics and reporting system"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        logger.info("Analytics Dashboard initialized")
    
    async def run_analytics_collection(self) -> Dict[str, Any]:
        """Run complete analytics collection and reporting"""
        start_time = datetime.utcnow()
        
        logger.info("📊 Starting Analytics Collection")
        
        results = {
            'timestamp': start_time.isoformat(),
            'analytics': {}
        }
        
        # Collect various analytics
        results['analytics']['user_behavior'] = await self.track_user_behavior()
        results['analytics']['station_popularity'] = await self.calculate_station_popularity()
        results['analytics']['geographic_distribution'] = await self.analyze_geographic_distribution()
        results['analytics']['listening_trends'] = await self.analyze_listening_trends()
        results['analytics']['api_usage'] = await self.track_api_usage()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['execution_time_seconds'] = duration
        results['status'] = 'completed'
        
        # Store analytics snapshot
        await self.db.analytics_snapshots.insert_one(results.copy())
        
        logger.info(f"✅ Analytics Collection Complete: {duration:.2f}s")
        
        return results
    
    async def track_user_behavior(self) -> Dict[str, Any]:
        """Track user interaction patterns"""
        try:
            # Analyze API request logs for user patterns
            recent_logs = await self.db.api_request_logs.find({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)}
            }).to_list(length=10000)
            
            if not recent_logs:
                return {'status': 'no_data', 'message': 'No recent user activity'}
            
            # Count unique users (by IP)
            unique_ips = set(log.get('client_ip') for log in recent_logs)
            
            # Most accessed endpoints
            endpoint_counts = {}
            for log in recent_logs:
                endpoint = log.get('path', 'unknown')
                endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
            
            top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'status': 'success',
                'unique_users_24h': len(unique_ips),
                'total_requests_24h': len(recent_logs),
                'avg_requests_per_user': len(recent_logs) / len(unique_ips) if unique_ips else 0,
                'top_endpoints': [{'path': ep, 'count': count} for ep, count in top_endpoints[:5]]
            }
            
        except Exception as e:
            logger.error(f"User behavior tracking error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def calculate_station_popularity(self) -> Dict[str, Any]:
        """Calculate station popularity metrics"""
        try:
            # Get top stations by quality score
            top_quality = await self.db.radio_stations.find({
                'quality_score': {'$exists': True}
            }).sort('quality_score', -1).limit(10).to_list(length=10)
            
            # Get most validated stations
            most_validated = await self.db.radio_stations.find({
                'stream_status': 'online'
            }).sort('stream_last_checked', -1).limit(10).to_list(length=10)
            
            return {
                'status': 'success',
                'top_quality_stations': len(top_quality),
                'online_stations': len(most_validated),
                'avg_quality_score': sum(s.get('quality_score', 0) for s in top_quality) / len(top_quality) if top_quality else 0
            }
            
        except Exception as e:
            logger.error(f"Station popularity error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Analyze geographic distribution of stations"""
        try:
            # Count stations by country
            pipeline = [
                {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 20}
            ]
            
            country_dist = await self.db.radio_stations.aggregate(pipeline).to_list(length=20)
            
            total_countries = await self.db.radio_stations.distinct('country')
            
            return {
                'status': 'success',
                'total_countries': len(total_countries),
                'top_countries': [{'country': c['_id'], 'stations': c['count']} for c in country_dist[:5]],
                'coverage': 'global'
            }
            
        except Exception as e:
            logger.error(f"Geographic analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_listening_trends(self) -> Dict[str, Any]:
        """Analyze listening trends over time"""
        try:
            # Analyze stream validation history to see trends
            recent_validations = await self.db.radio_stations.count_documents({
                'stream_last_checked': {'$gte': datetime.utcnow() - timedelta(days=7)}
            })
            
            online_ratio = await self.db.radio_stations.count_documents({
                'stream_status': 'online'
            })
            
            return {
                'status': 'success',
                'recent_validations_7d': recent_validations,
                'online_stations': online_ratio,
                'trend': 'stable'
            }
            
        except Exception as e:
            logger.error(f"Listening trends error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def track_api_usage(self) -> Dict[str, Any]:
        """Track API usage statistics"""
        try:
            # Get API request statistics for last 24 hours
            recent_logs = await self.db.api_request_logs.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)}
            })
            
            error_logs = await self.db.api_request_logs.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)},
                'response_status': {'$gte': 400}
            })
            
            error_rate = (error_logs / recent_logs * 100) if recent_logs > 0 else 0
            
            return {
                'status': 'success',
                'total_requests_24h': recent_logs,
                'error_requests_24h': error_logs,
                'error_rate_percent': round(error_rate, 2),
                'health': 'good' if error_rate < 5 else 'warning'
            }
            
        except Exception as e:
            logger.error(f"API usage tracking error: {e}")
            return {'status': 'error', 'error': str(e)}


def get_analytics_dashboard():
    """Get singleton analytics dashboard instance"""
    global _analytics_dashboard
    if '_analytics_dashboard' not in globals():
        globals()['_analytics_dashboard'] = AnalyticsDashboard()
    return globals()['_analytics_dashboard']
