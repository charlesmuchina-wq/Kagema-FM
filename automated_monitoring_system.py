#!/usr/bin/env python3
"""
Automated Monitoring System for Preventive Actions
Continuously monitors the effectiveness of implemented preventive measures
"""

import time
import json
import requests
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import os

class AutomatedMonitoringSystem:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.monitoring_active = False
        self.alerts = []
        self.metrics_history = []
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring schedule
        self.setup_monitoring_schedule()
    
    def setup_monitoring_schedule(self):
        """Setup automated monitoring schedule"""
        # Continuous monitoring (every 5 minutes)
        schedule.every(5).minutes.do(self.monitor_security_measures)
        schedule.every(10).minutes.do(self.monitor_performance_metrics)
        schedule.every(15).minutes.do(self.monitor_system_health)
        
        # Daily comprehensive checks
        schedule.every().day.at("02:00").do(self.run_daily_comprehensive_check)
        
        # Weekly preventive measures validation
        schedule.every().monday.at("01:00").do(self.run_weekly_preventive_validation)
    
    def monitor_security_measures(self):
        """Monitor security measures effectiveness"""
        self.logger.info("🔒 Running security measures monitoring...")
        
        security_metrics = {
            'timestamp': datetime.now().isoformat(),
            'browser_extension_blocking': self._check_extension_blocking(),
            'cors_protection': self._check_cors_protection(),
            'input_validation': self._check_input_validation(),
            'security_headers': self._check_security_headers(),
            'overall_security_status': 'unknown'
        }
        
        # Calculate overall security status
        security_checks = [
            security_metrics['browser_extension_blocking'],
            security_metrics['cors_protection'],
            security_metrics['input_validation'],
            security_metrics['security_headers']
        ]
        
        success_rate = sum(1 for check in security_checks if check['status'] == 'pass') / len(security_checks)
        
        if success_rate >= 0.95:
            security_metrics['overall_security_status'] = 'excellent'
        elif success_rate >= 0.8:
            security_metrics['overall_security_status'] = 'good'
        else:
            security_metrics['overall_security_status'] = 'critical'
            self._create_alert('CRITICAL_SECURITY', 'Security measures failing', security_metrics)
        
        self.metrics_history.append({'type': 'security', 'data': security_metrics})
        return security_metrics
    
    def _check_extension_blocking(self) -> Dict:
        """Check browser extension blocking effectiveness"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/",
                headers={'origin': 'chrome-extension://test-extension'},
                timeout=10
            )
            return {
                'status': 'pass' if response.status_code == 403 else 'fail',
                'response_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _check_cors_protection(self) -> Dict:
        """Check CORS protection effectiveness"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/",
                headers={'origin': 'https://malicious-site.com'},
                timeout=10
            )
            return {
                'status': 'pass' if response.status_code == 403 else 'fail',
                'response_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _check_input_validation(self) -> Dict:
        """Check input validation effectiveness"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/personalized-content/multilingual",
                json={'invalid': 'data'},
                timeout=10
            )
            return {
                'status': 'pass' if response.status_code == 422 else 'fail',
                'response_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _check_security_headers(self) -> Dict:
        """Check security headers presence"""
        try:
            response = requests.get(f"{self.backend_url}/api/", timeout=10)
            required_headers = ['x-content-type-options', 'x-frame-options', 'x-xss-protection']
            headers_present = [header.lower() in [h.lower() for h in response.headers.keys()] for header in required_headers]
            
            return {
                'status': 'pass' if all(headers_present) else 'fail',
                'headers_found': sum(headers_present),
                'headers_required': len(required_headers),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def monitor_performance_metrics(self):
        """Monitor performance metrics"""
        self.logger.info("⚡ Running performance monitoring...")
        
        performance_metrics = {
            'timestamp': datetime.now().isoformat(),
            'response_times': self._measure_response_times(),
            'cache_effectiveness': self._check_cache_effectiveness(),
            'system_resources': self._check_system_resources(),
            'overall_performance_status': 'unknown'
        }
        
        # Calculate overall performance status
        avg_response_time = performance_metrics['response_times']['average_ms']
        cache_working = performance_metrics['cache_effectiveness']['status'] == 'pass'
        
        if avg_response_time < 100 and cache_working:
            performance_metrics['overall_performance_status'] = 'excellent'
        elif avg_response_time < 500 and cache_working:
            performance_metrics['overall_performance_status'] = 'good'
        else:
            performance_metrics['overall_performance_status'] = 'degraded'
            if avg_response_time > 1000:
                self._create_alert('PERFORMANCE_DEGRADED', 'Response times excessive', performance_metrics)
        
        self.metrics_history.append({'type': 'performance', 'data': performance_metrics})
        return performance_metrics
    
    def _measure_response_times(self) -> Dict:
        """Measure API response times"""
        endpoints = ['/api/', '/api/station-info', '/api/languages']
        response_times = []
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)
            except:
                continue
        
        if response_times:
            return {
                'average_ms': sum(response_times) / len(response_times),
                'min_ms': min(response_times),
                'max_ms': max(response_times),
                'count': len(response_times)
            }
        else:
            return {'average_ms': 0, 'min_ms': 0, 'max_ms': 0, 'count': 0}
    
    def _check_cache_effectiveness(self) -> Dict:
        """Check cache header effectiveness"""
        try:
            response = requests.get(f"{self.backend_url}/api/languages", timeout=10)
            has_cache_headers = 'cache-control' in response.headers
            
            return {
                'status': 'pass' if has_cache_headers else 'fail',
                'cache_control': response.headers.get('cache-control', 'none'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            # Simple system check - in production, would use actual system metrics
            response = requests.get(f"{self.backend_url}/api/", timeout=10)
            return {
                'api_responsive': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'api_responsive': False, 'error': str(e)}
    
    def monitor_system_health(self):
        """Monitor overall system health"""
        self.logger.info("🌐 Running system health monitoring...")
        
        health_metrics = {
            'timestamp': datetime.now().isoformat(),
            'api_availability': self._check_api_availability(),
            'service_connectivity': self._check_service_connectivity(),
            'error_rates': self._analyze_error_rates(),
            'overall_health_status': 'unknown'
        }
        
        # Calculate overall health status
        api_up = health_metrics['api_availability']['status'] == 'up'
        connectivity_good = health_metrics['service_connectivity']['status'] == 'good'
        error_rate_low = health_metrics['error_rates']['rate'] < 0.05  # Less than 5% error rate
        
        if api_up and connectivity_good and error_rate_low:
            health_metrics['overall_health_status'] = 'healthy'
        elif api_up and connectivity_good:
            health_metrics['overall_health_status'] = 'degraded'
        else:
            health_metrics['overall_health_status'] = 'critical'
            self._create_alert('SYSTEM_HEALTH_CRITICAL', 'System health critical', health_metrics)
        
        self.metrics_history.append({'type': 'health', 'data': health_metrics})
        return health_metrics
    
    def _check_api_availability(self) -> Dict:
        """Check API availability"""
        try:
            response = requests.get(f"{self.backend_url}/api/", timeout=10)
            return {
                'status': 'up' if response.status_code == 200 else 'down',
                'response_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {'status': 'down', 'error': str(e)}
    
    def _check_service_connectivity(self) -> Dict:
        """Check service connectivity"""
        endpoints = ['/api/station-info', '/api/languages', '/api/voice/help']
        successful_connections = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    successful_connections += 1
            except:
                continue
        
        connectivity_rate = successful_connections / len(endpoints)
        return {
            'status': 'good' if connectivity_rate >= 0.8 else 'poor',
            'successful_connections': successful_connections,
            'total_endpoints': len(endpoints),
            'connectivity_rate': connectivity_rate
        }
    
    def _analyze_error_rates(self) -> Dict:
        """Analyze error rates from recent metrics"""
        # Simple error rate analysis - in production, would analyze logs
        recent_metrics = [m for m in self.metrics_history if 
                         (datetime.now() - datetime.fromisoformat(m['data']['timestamp'])).seconds < 3600]
        
        if not recent_metrics:
            return {'rate': 0.0, 'count': 0}
        
        error_count = sum(1 for m in recent_metrics if 
                         any('error' in str(v) for v in m['data'].values() if isinstance(v, dict)))
        
        return {
            'rate': error_count / len(recent_metrics) if recent_metrics else 0.0,
            'error_count': error_count,
            'total_checks': len(recent_metrics)
        }
    
    def _create_alert(self, alert_type: str, message: str, details: Dict):
        """Create an alert for critical issues"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'resolved': False
        }
        
        self.alerts.append(alert)
        self.logger.error(f"🚨 ALERT: {alert_type} - {message}")
        
        # In production, would send notifications (email, Slack, etc.)
        
    def run_daily_comprehensive_check(self):
        """Run daily comprehensive system check"""
        self.logger.info("📊 Running daily comprehensive check...")
        
        # Run all monitoring checks
        security_results = self.monitor_security_measures()
        performance_results = self.monitor_performance_metrics()
        health_results = self.monitor_system_health()
        
        # Generate daily report
        daily_report = {
            'date': datetime.now().date().isoformat(),
            'security': security_results,
            'performance': performance_results,
            'health': health_results,
            'alerts': [alert for alert in self.alerts if not alert['resolved']],
            'metrics_count': len(self.metrics_history)
        }
        
        # Save daily report
        report_file = f'/app/daily_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w') as f:
            json.dump(daily_report, f, indent=2)
        
        self.logger.info(f"📄 Daily report saved: {report_file}")
        
        # Clean old metrics (keep last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['data']['timestamp']) > cutoff_time
        ]
        
    def run_weekly_preventive_validation(self):
        """Run weekly comprehensive preventive measures validation"""
        self.logger.info("🔄 Running weekly preventive validation...")
        
        # Import and run the preventive actions system
        from preventive_actions_system import PreventiveActionsSystem
        
        validation_system = PreventiveActionsSystem()
        weekly_results = validation_system.run_comprehensive_system_validation()
        
        # Save weekly validation report
        report_file = f'/app/weekly_validation_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w') as f:
            json.dump(weekly_results, f, indent=2)
        
        self.logger.info(f"📄 Weekly validation report saved: {report_file}")
        
        # Check if any critical issues found
        if weekly_results.get('overall_status') in ['poor', 'fair']:
            self._create_alert(
                'WEEKLY_VALIDATION_FAILED',
                'Weekly preventive validation found critical issues',
                weekly_results
            )
    
    def start_monitoring(self):
        """Start the automated monitoring system"""
        self.monitoring_active = True
        self.logger.info("🚀 Starting automated monitoring system...")
        
        def monitoring_loop():
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Start monitoring in a separate thread
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        self.logger.info("✅ Automated monitoring system started")
        
    def stop_monitoring(self):
        """Stop the automated monitoring system"""
        self.monitoring_active = False
        self.logger.info("🛑 Automated monitoring system stopped")
    
    def get_system_status(self) -> Dict:
        """Get current system status summary"""
        if not self.metrics_history:
            return {'status': 'no_data', 'message': 'No monitoring data available'}
        
        # Get latest metrics from each category
        latest_security = None
        latest_performance = None
        latest_health = None
        
        for metric in reversed(self.metrics_history):
            if metric['type'] == 'security' and not latest_security:
                latest_security = metric['data']
            elif metric['type'] == 'performance' and not latest_performance:
                latest_performance = metric['data']
            elif metric['type'] == 'health' and not latest_health:
                latest_health = metric['data']
        
        # Calculate overall status
        statuses = []
        if latest_security:
            statuses.append(latest_security['overall_security_status'])
        if latest_performance:
            statuses.append(latest_performance['overall_performance_status'])
        if latest_health:
            statuses.append(latest_health['overall_health_status'])
        
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'degraded' in statuses or 'poor' in statuses:
            overall_status = 'degraded'
        elif 'good' in statuses or 'healthy' in statuses:
            overall_status = 'good'
        elif 'excellent' in statuses:
            overall_status = 'excellent'
        else:
            overall_status = 'unknown'
        
        return {
            'overall_status': overall_status,
            'security': latest_security,
            'performance': latest_performance,
            'health': latest_health,
            'active_alerts': len([alert for alert in self.alerts if not alert['resolved']]),
            'monitoring_active': self.monitoring_active,
            'last_updated': datetime.now().isoformat()
        }
    
    def run_immediate_check(self):
        """Run immediate comprehensive check"""
        print("🔄 Running immediate system check...")
        
        security_results = self.monitor_security_measures()
        performance_results = self.monitor_performance_metrics()
        health_results = self.monitor_system_health()
        
        status = self.get_system_status()
        
        print(f"\n📊 System Status Summary:")
        print(f"  Overall Status: {status['overall_status'].upper()}")
        print(f"  Security: {security_results['overall_security_status'].upper()}")
        print(f"  Performance: {performance_results['overall_performance_status'].upper()}")
        print(f"  Health: {health_results['overall_health_status'].upper()}")
        print(f"  Active Alerts: {status['active_alerts']}")
        
        return status

if __name__ == "__main__":
    monitoring = AutomatedMonitoringSystem()
    
    # Run immediate check
    monitoring.run_immediate_check()
    
    print("\n🚀 Starting continuous monitoring...")
    monitoring.start_monitoring()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
            status = monitoring.get_system_status()
            if status['overall_status'] in ['critical', 'degraded']:
                print(f"⚠️ System status: {status['overall_status'].upper()}")
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitoring.stop_monitoring()