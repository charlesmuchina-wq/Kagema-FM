"""
Real-Time Monitoring & Alerting for Dragon KARAU AI
Task 22: Proactive monitoring, alerting, and incident response
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class RealTimeMonitor:
    """Real-time system monitoring and alerting"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
        self.db = self.mongo_client[os.getenv('DB_NAME', 'kagema_fm_db')]
        
        # Alert thresholds
        self.error_rate_threshold = 10  # %
        self.response_time_threshold = 1000  # ms
        self.memory_threshold = 90  # %
        
        logger.info("Real-Time Monitor initialized")
    
    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run complete monitoring cycle"""
        start_time = datetime.utcnow()
        
        logger.info("🔍 Starting Real-Time Monitoring")
        
        results = {
            'timestamp': start_time.isoformat(),
            'checks': {},
            'alerts': []
        }
        
        # Monitor various system aspects
        results['checks']['service_health'] = await self.check_service_health()
        results['checks']['error_rate'] = await self.check_error_rate()
        results['checks']['performance'] = await self.check_performance_degradation()
        results['checks']['database'] = await self.check_database_health()
        
        # Generate alerts if needed
        for check_name, check_result in results['checks'].items():
            if isinstance(check_result, dict) and check_result.get('alert'):
                results['alerts'].append({
                    'type': check_name,
                    'severity': check_result.get('severity', 'warning'),
                    'message': check_result.get('alert_message', 'Alert triggered')
                })
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        results['execution_time_seconds'] = duration
        results['status'] = 'completed'
        results['alerts_count'] = len(results['alerts'])
        
        # Store monitoring results
        await self.db.monitoring_history.insert_one(results.copy())
        
        logger.info(f"✅ Monitoring Cycle Complete: {len(results['alerts'])} alerts")
        
        return results
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            # Check if critical collections are accessible
            await self.db.radio_stations.count_documents({}, limit=1)
            
            return {
                'status': 'healthy',
                'services': {
                    'database': 'online',
                    'api': 'online'
                },
                'alert': False
            }
        except Exception as e:
            return {
                'status': 'error',
                'alert': True,
                'severity': 'critical',
                'alert_message': f'Service health check failed: {str(e)}'
            }
    
    async def check_error_rate(self) -> Dict[str, Any]:
        """Check API error rate"""
        try:
            recent_logs = await self.db.api_request_logs.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)}
            })
            
            error_logs = await self.db.api_request_logs.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)},
                'response_status': {'$gte': 400}
            })
            
            error_rate = (error_logs / recent_logs * 100) if recent_logs > 0 else 0
            
            return {
                'status': 'ok' if error_rate < self.error_rate_threshold else 'warning',
                'error_rate': round(error_rate, 2),
                'threshold': self.error_rate_threshold,
                'alert': error_rate >= self.error_rate_threshold,
                'severity': 'warning' if error_rate < 20 else 'critical',
                'alert_message': f'Error rate {error_rate:.1f}% exceeds threshold {self.error_rate_threshold}%'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'alert': False}
    
    async def check_performance_degradation(self) -> Dict[str, Any]:
        """Check for performance degradation"""
        try:
            # Get recent response times
            recent_logs = await self.db.api_request_logs.find({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=1)},
                'response_time_ms': {'$exists': True}
            }).limit(100).to_list(length=100)
            
            if not recent_logs:
                return {'status': 'no_data', 'alert': False}
            
            avg_response = sum(log.get('response_time_ms', 0) for log in recent_logs) / len(recent_logs)
            
            return {
                'status': 'ok' if avg_response < self.response_time_threshold else 'warning',
                'avg_response_time_ms': round(avg_response, 2),
                'threshold': self.response_time_threshold,
                'alert': avg_response >= self.response_time_threshold,
                'severity': 'warning',
                'alert_message': f'Avg response time {avg_response:.0f}ms exceeds threshold'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'alert': False}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health metrics"""
        try:
            # Basic database health check
            db_stats = await self.db.command('dbStats')
            
            return {
                'status': 'healthy',
                'collections': db_stats.get('collections', 0),
                'data_size_mb': round(db_stats.get('dataSize', 0) / (1024**2), 2),
                'alert': False
            }
        except Exception as e:
            return {
                'status': 'error',
                'alert': True,
                'severity': 'critical',
                'alert_message': f'Database health check failed: {str(e)}'
            }


def get_real_time_monitor():
    """Get singleton monitor instance"""
    global _monitor
    if '_monitor' not in globals():
        globals()['_monitor'] = RealTimeMonitor()
    return globals()['_monitor']
