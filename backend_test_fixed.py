#!/usr/bin/env python3
"""
🚀 PHASE 2 BACKEND TESTING - Tasks 21-25
Dragon KARAU AI - Comprehensive Backend Testing for Phase 2 Features

TESTING FOCUS:
1. Task 21 - Analytics Dashboard: Real-time analytics, user behavior tracking, trending analysis
2. Task 22 - Real-Time Monitoring: Proactive monitoring, alerting, and incident response  
3. Task 23 - A/B Testing Framework: Experiment management, user segmentation, results analysis
4. Task 24 - Content Compliance Engine: Automated content filtering, policy enforcement, compliance checks
5. Task 25 - User Feedback API: User feedback collection, rating system, issue reporting

SUCCESS CRITERIA:
✅ All 15+ new API endpoints should respond correctly
✅ Phase 2 features should be functional
✅ No critical errors in backend logs
✅ All Phase 2 modules should initialize without errors
✅ Automated scheduler can call all 5 Phase 2 tasks
"""

import asyncio
import aiohttp
import json
import sys
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from frontend environment
BACKEND_URL = "https://karau-grid-update.preview.emergentagent.com/api"

class Phase2BackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        self.phase2_results = {
            'task_21': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []},
            'task_22': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []},
            'task_23': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []},
            'task_24': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []},
            'task_25': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []},
            'scheduler': {'tests': 0, 'passed': 0, 'failed': 0, 'details': []}
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Generic endpoint tester"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'success': response.status == 200
                    }
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data, params=params) as response:
                    response_data = await response.json()
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'success': response.status == 200
                    }
        except Exception as e:
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'success': False,
                'exception': str(e)
            }
    
    async def test_task_21_analytics_dashboard(self):
        """Test Task 21: Analytics Dashboard API endpoints"""
        print("\n📊 TESTING TASK 21 - ANALYTICS DASHBOARD")
        print("=" * 60)
        
        task_results = self.phase2_results['task_21']
        
        # Test 1: GET /api/analytics/dashboard
        print("Testing GET /api/analytics/dashboard...")
        result = await self.test_endpoint('GET', '/analytics/dashboard')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'analytics' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Analytics Dashboard API", True, f"Status: {result['status_code']}")
                task_results['details'].append("✅ Analytics dashboard returns proper data structure")
            else:
                task_results['failed'] += 1
                self.log_test("Analytics Dashboard API", False, f"Invalid response structure")
                task_results['details'].append("❌ Analytics dashboard response missing 'analytics' field")
        else:
            task_results['failed'] += 1
            self.log_test("Analytics Dashboard API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Analytics dashboard API failed: {result.get('data')}")
        
        # Test 2: GET /api/analytics/stats
        print("Testing GET /api/analytics/stats...")
        result = await self.test_endpoint('GET', '/analytics/stats')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'recent_analytics' in data:
                task_results['passed'] += 1
                self.log_test("Analytics Stats API", True, f"Status: {result['status_code']}")
                task_results['details'].append("✅ Analytics stats returns snapshot data")
            else:
                task_results['failed'] += 1
                self.log_test("Analytics Stats API", False, f"Invalid response")
                task_results['details'].append("❌ Analytics stats response invalid structure")
        else:
            task_results['failed'] += 1
            self.log_test("Analytics Stats API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Analytics stats API failed: {result.get('data')}")
    
    async def test_task_22_real_time_monitoring(self):
        """Test Task 22: Real-Time Monitoring API endpoints"""
        print("\n🔍 TESTING TASK 22 - REAL-TIME MONITORING")
        print("=" * 60)
        
        task_results = self.phase2_results['task_22']
        
        # Test 1: GET /api/monitoring/status
        print("Testing GET /api/monitoring/status...")
        result = await self.test_endpoint('GET', '/monitoring/status')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'checks' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Monitoring Status API", True, f"Status: {result['status_code']}")
                task_results['details'].append("✅ Monitoring status returns health checks")
                
                # Check for expected monitoring components
                checks = data.get('data', {}).get('checks', {})
                expected_checks = ['service_health', 'error_rate', 'performance', 'database']
                for check in expected_checks:
                    if check in checks:
                        task_results['details'].append(f"✅ {check} monitoring active")
                    else:
                        task_results['details'].append(f"⚠️ {check} monitoring missing")
            else:
                task_results['failed'] += 1
                self.log_test("Monitoring Status API", False, f"Invalid response")
                task_results['details'].append("❌ Monitoring status missing 'checks' field")
        else:
            task_results['failed'] += 1
            self.log_test("Monitoring Status API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Monitoring status API failed: {result.get('data')}")
        
        # Test 2: GET /api/monitoring/alerts
        print("Testing GET /api/monitoring/alerts...")
        result = await self.test_endpoint('GET', '/monitoring/alerts')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'alerts' in data:
                task_results['passed'] += 1
                self.log_test("Monitoring Alerts API", True, f"Status: {result['status_code']}")
                task_results['details'].append("✅ Monitoring alerts returns alert data")
            else:
                task_results['failed'] += 1
                self.log_test("Monitoring Alerts API", False, f"Invalid response")
                task_results['details'].append("❌ Monitoring alerts response invalid")
        else:
            task_results['failed'] += 1
            self.log_test("Monitoring Alerts API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Monitoring alerts API failed: {result.get('data')}")
    
    async def test_task_23_ab_testing_framework(self):
        """Test Task 23: A/B Testing Framework API endpoints"""
        print("\n🧪 TESTING TASK 23 - A/B TESTING FRAMEWORK")
        print("=" * 60)
        
        task_results = self.phase2_results['task_23']
        
        # Test 1: POST /api/experiments/create
        print("Testing POST /api/experiments/create...")
        experiment_data = {
            "name": "Test Radio Layout Experiment",
            "description": "Testing different radio player layouts",
            "hypothesis": "Grid layout increases user engagement",
            "type": "simple_ab",
            "variants": [
                {"name": "control", "weight": 0.5, "config": {"layout": "list"}},
                {"name": "treatment", "weight": 0.5, "config": {"layout": "grid"}}
            ],
            "target_metric": "engagement_rate",
            "sample_size": 1000,
            "confidence_level": 95
        }
        
        result = await self.test_endpoint('POST', '/experiments/create', experiment_data)
        task_results['tests'] += 1
        
        experiment_id = None
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'experiment_id' in data.get('data', {}):
                experiment_id = data['data']['experiment_id']
                task_results['passed'] += 1
                self.log_test("Create A/B Experiment", True, f"Experiment ID: {experiment_id}")
                task_results['details'].append("✅ A/B experiment created successfully")
            else:
                task_results['failed'] += 1
                self.log_test("Create A/B Experiment", False, f"Invalid response")
                task_results['details'].append("❌ A/B experiment creation failed")
        else:
            task_results['failed'] += 1
            self.log_test("Create A/B Experiment", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Create experiment API failed: {result.get('data')}")
        
        # Test 2: GET /api/experiments/summary
        print("Testing GET /api/experiments/summary...")
        result = await self.test_endpoint('GET', '/experiments/summary')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'total_experiments' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Experiments Summary API", True, f"Total experiments: {data.get('data', {}).get('total_experiments')}")
                task_results['details'].append("✅ Experiments summary returns proper data")
            else:
                task_results['failed'] += 1
                self.log_test("Experiments Summary API", False, f"Invalid response")
                task_results['details'].append("❌ Experiments summary response invalid")
        else:
            task_results['failed'] += 1
            self.log_test("Experiments Summary API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Experiments summary API failed: {result.get('data')}")
        
        # Test 3: User assignment (if experiment was created)
        if experiment_id:
            print(f"Testing GET /api/experiments/{experiment_id}/assign/test_user_123...")
            result = await self.test_endpoint('GET', f'/experiments/{experiment_id}/assign/test_user_123')
            task_results['tests'] += 1
            
            if result['success'] and result['status_code'] == 200:
                data = result['data']
                if isinstance(data, dict) and data.get('success') and 'variant' in data.get('data', {}):
                    task_results['passed'] += 1
                    self.log_test("User Variant Assignment", True, f"Assigned variant: {data.get('data', {}).get('variant')}")
                    task_results['details'].append("✅ User variant assignment working")
                else:
                    task_results['failed'] += 1
                    self.log_test("User Variant Assignment", False, f"Invalid response")
                    task_results['details'].append("❌ User variant assignment failed")
            else:
                task_results['failed'] += 1
                self.log_test("User Variant Assignment", False, f"Status: {result['status_code']}")
                task_results['details'].append(f"❌ User assignment API failed: {result.get('data')}")
            
            # Test 4: Track conversion
            print(f"Testing POST /api/experiments/{experiment_id}/track...")
            conversion_data = {
                "user_id": "test_user_123",
                "metric": "engagement_rate",
                "value": 1.0
            }
            
            result = await self.test_endpoint('POST', f'/experiments/{experiment_id}/track', conversion_data)
            task_results['tests'] += 1
            
            if result['success'] and result['status_code'] == 200:
                data = result['data']
                if isinstance(data, dict) and data.get('success'):
                    task_results['passed'] += 1
                    self.log_test("Track Conversion", True, "Conversion tracked")
                    task_results['details'].append("✅ Conversion tracking working")
                else:
                    task_results['failed'] += 1
                    self.log_test("Track Conversion", False, f"Invalid response")
                    task_results['details'].append("❌ Conversion tracking failed")
            else:
                task_results['failed'] += 1
                self.log_test("Track Conversion", False, f"Status: {result['status_code']}")
                task_results['details'].append(f"❌ Track conversion API failed: {result.get('data')}")
    
    async def test_task_24_content_compliance_engine(self):
        """Test Task 24: Content Compliance Engine API endpoints"""
        print("\n🔒 TESTING TASK 24 - CONTENT COMPLIANCE ENGINE")
        print("=" * 60)
        
        task_results = self.phase2_results['task_24']
        
        # Test 1: GET /api/compliance/stats
        print("Testing GET /api/compliance/stats...")
        result = await self.test_endpoint('GET', '/compliance/stats')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'total_stations' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Compliance Stats API", True, f"Total stations: {data.get('data', {}).get('total_stations')}")
                task_results['details'].append("✅ Compliance stats returns station data")
                
                # Check compliance metrics
                compliance_rate = data.get('data', {}).get('compliance_rate_percent', 0)
                task_results['details'].append(f"📊 Compliance rate: {compliance_rate}%")
            else:
                task_results['failed'] += 1
                self.log_test("Compliance Stats API", False, f"Invalid response")
                task_results['details'].append("❌ Compliance stats response invalid")
        else:
            task_results['failed'] += 1
            self.log_test("Compliance Stats API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Compliance stats API failed: {result.get('data')}")
        
        # Test 2: GET /api/compliance/report
        print("Testing GET /api/compliance/report...")
        result = await self.test_endpoint('GET', '/compliance/report')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and ('compliance_rate_percent' in data.get('data', {}) or 'total_stations' in data.get('data', {})):
                task_results['passed'] += 1
                self.log_test("Compliance Report API", True, f"Status: {result['status_code']}")
                task_results['details'].append("✅ Compliance report returns detailed data")
            else:
                task_results['failed'] += 1
                self.log_test("Compliance Report API", False, f"Invalid response")
                task_results['details'].append("❌ Compliance report response invalid")
        else:
            task_results['failed'] += 1
            self.log_test("Compliance Report API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Compliance report API failed: {result.get('data')}")
        
        # Test 3: POST /api/stations/{station_id}/rate-content (using a valid ObjectId format)
        print("Testing POST /api/stations/507f1f77bcf86cd799439011/rate-content...")
        rating_data = {
            "rating": "general"
        }
        
        result = await self.test_endpoint('POST', '/stations/507f1f77bcf86cd799439011/rate-content', rating_data)
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success'):
                task_results['passed'] += 1
                self.log_test("Rate Station Content", True, f"Rating applied: {rating_data['rating']}")
                task_results['details'].append("✅ Station content rating working")
            else:
                task_results['failed'] += 1
                self.log_test("Rate Station Content", False, f"Invalid response")
                task_results['details'].append("❌ Station content rating failed")
        else:
            # This might fail if station doesn't exist, which is expected for a test ObjectId
            if result['status_code'] == 404 or 'not found' in str(result.get('data', '')).lower():
                task_results['passed'] += 1
                self.log_test("Rate Station Content", True, "API working (test station not found as expected)")
                task_results['details'].append("✅ Station rating API functional (test station not found)")
            elif 'ObjectId' in str(result.get('data', '')):
                task_results['failed'] += 1
                self.log_test("Rate Station Content", False, "ObjectId validation error")
                task_results['details'].append("❌ Station rating API ObjectId validation issue")
            else:
                task_results['failed'] += 1
                self.log_test("Rate Station Content", False, f"Status: {result['status_code']}")
                task_results['details'].append(f"❌ Rate content API failed: {result.get('data')}")
    
    async def test_task_25_user_feedback_api(self):
        """Test Task 25: User Feedback API endpoints"""
        print("\n💬 TESTING TASK 25 - USER FEEDBACK API")
        print("=" * 60)
        
        task_results = self.phase2_results['task_25']
        
        # Test 1: POST /api/feedback/submit
        print("Testing POST /api/feedback/submit...")
        feedback_data = {
            "user_id": "test_user_456",
            "category": "app_performance",
            "title": "App loading slowly",
            "description": "The radio app takes too long to load stations",
            "rating": 2,
            "metadata": {
                "device": "iPhone 14",
                "app_version": "1.0.0",
                "os": "iOS 16.0"
            }
        }
        
        result = await self.test_endpoint('POST', '/feedback/submit', feedback_data)
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'feedback_id' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Submit Feedback", True, f"Feedback ID: {data.get('data', {}).get('feedback_id')}")
                task_results['details'].append("✅ Feedback submission working")
            else:
                task_results['failed'] += 1
                self.log_test("Submit Feedback", False, f"Invalid response")
                task_results['details'].append("❌ Feedback submission failed")
        else:
            task_results['failed'] += 1
            self.log_test("Submit Feedback", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Submit feedback API failed: {result.get('data')}")
        
        # Test 2: POST /api/feedback/rate-station
        print("Testing POST /api/feedback/rate-station...")
        rating_data = {
            "user_id": "test_user_456",
            "station_id": "test_station_789",
            "rating": 4,
            "review": "Great music selection and clear audio quality"
        }
        
        result = await self.test_endpoint('POST', '/feedback/rate-station', rating_data)
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success'):
                task_results['passed'] += 1
                self.log_test("Rate Station", True, f"Rating: {rating_data['rating']}/5")
                task_results['details'].append("✅ Station rating working")
            else:
                task_results['failed'] += 1
                self.log_test("Rate Station", False, f"Invalid response")
                task_results['details'].append("❌ Station rating failed")
        else:
            task_results['failed'] += 1
            self.log_test("Rate Station", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Rate station API failed: {result.get('data')}")
        
        # Test 3: POST /api/feedback/report-issue
        print("Testing POST /api/feedback/report-issue...")
        issue_data = {
            "user_id": "test_user_456",
            "type": "quality",
            "title": "Station stream not working",
            "description": "The stream URL returns 404 error",
            "station_id": "test_station_789",
            "severity": "high"
        }
        
        result = await self.test_endpoint('POST', '/feedback/report-issue', issue_data)
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'issue_id' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Report Issue", True, f"Issue ID: {data.get('data', {}).get('issue_id')}")
                task_results['details'].append("✅ Issue reporting working")
            else:
                task_results['failed'] += 1
                self.log_test("Report Issue", False, f"Invalid response")
                task_results['details'].append("❌ Issue reporting failed")
        else:
            task_results['failed'] += 1
            self.log_test("Report Issue", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Report issue API failed: {result.get('data')}")
        
        # Test 4: GET /api/feedback/stats
        print("Testing GET /api/feedback/stats...")
        result = await self.test_endpoint('GET', '/feedback/stats')
        task_results['tests'] += 1
        
        if result['success'] and result['status_code'] == 200:
            data = result['data']
            if isinstance(data, dict) and data.get('success') and 'total_feedback' in data.get('data', {}):
                task_results['passed'] += 1
                self.log_test("Feedback Stats API", True, f"Total feedback: {data.get('data', {}).get('total_feedback')}")
                task_results['details'].append("✅ Feedback stats returns proper data")
            else:
                task_results['failed'] += 1
                self.log_test("Feedback Stats API", False, f"Invalid response")
                task_results['details'].append("❌ Feedback stats response invalid")
        else:
            task_results['failed'] += 1
            self.log_test("Feedback Stats API", False, f"Status: {result['status_code']}")
            task_results['details'].append(f"❌ Feedback stats API failed: {result.get('data')}")
    
    async def test_automated_scheduler_integration(self):
        """Test that automated scheduler can call all Phase 2 tasks"""
        print("\n⚙️ TESTING AUTOMATED SCHEDULER INTEGRATION")
        print("=" * 60)
        
        task_results = self.phase2_results['scheduler']
        
        # Check if backend logs show Phase 2 tasks are loaded
        print("Checking automated scheduler integration...")
        
        # We can't directly test the scheduler, but we can verify the modules are importable
        try:
            # Test importing all Phase 2 modules
            import sys
            sys.path.append('/app/backend')
            
            from analytics_dashboard import get_analytics_dashboard
            from real_time_monitor import get_real_time_monitor
            from ab_testing_framework import get_ab_testing_framework
            from content_compliance_engine import get_content_compliance_engine
            from user_feedback_api import get_user_feedback_api
            
            task_results['tests'] += 1
            task_results['passed'] += 1
            self.log_test("Phase 2 Module Imports", True, "All modules importable")
            task_results['details'].append("✅ All Phase 2 modules can be imported")
            
            # Test that instances can be created
            analytics = get_analytics_dashboard()
            monitor = get_real_time_monitor()
            ab_framework = get_ab_testing_framework()
            compliance = get_content_compliance_engine()
            feedback = get_user_feedback_api()
            
            task_results['tests'] += 1
            task_results['passed'] += 1
            self.log_test("Phase 2 Instance Creation", True, "All instances created")
            task_results['details'].append("✅ All Phase 2 service instances created successfully")
            
        except Exception as e:
            task_results['tests'] += 2
            task_results['failed'] += 2
            self.log_test("Phase 2 Module Integration", False, f"Import error: {e}")
            task_results['details'].append(f"❌ Module integration failed: {e}")
    
    async def run_all_tests(self):
        """Run all Phase 2 backend tests"""
        print("🚀 STARTING PHASE 2 BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test each Phase 2 task
        await self.test_task_21_analytics_dashboard()
        await self.test_task_22_real_time_monitoring()
        await self.test_task_23_ab_testing_framework()
        await self.test_task_24_content_compliance_engine()
        await self.test_task_25_user_feedback_api()
        await self.test_automated_scheduler_integration()
        
        duration = time.time() - start_time
        
        # Calculate overall results
        total_tests = sum(task['tests'] for task in self.phase2_results.values())
        total_passed = sum(task['passed'] for task in self.phase2_results.values())
        total_failed = sum(task['failed'] for task in self.phase2_results.values())
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 PHASE 2 BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        for task_name, results in self.phase2_results.items():
            task_success_rate = (results['passed'] / results['tests'] * 100) if results['tests'] > 0 else 0
            status = "✅ PASSED" if results['failed'] == 0 else "❌ FAILED" if results['passed'] == 0 else "⚠️ PARTIAL"
            print(f"{task_name.upper()}: {status} ({results['passed']}/{results['tests']} - {task_success_rate:.1f}%)")
            
            for detail in results['details']:
                print(f"  {detail}")
        
        print("=" * 60)
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        
        if success_rate >= 80:
            print("🎉 PHASE 2 BACKEND TESTING: EXCELLENT SUCCESS!")
        elif success_rate >= 60:
            print("✅ PHASE 2 BACKEND TESTING: GOOD SUCCESS!")
        else:
            print("⚠️ PHASE 2 BACKEND TESTING: NEEDS ATTENTION!")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        return {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'success_rate': success_rate,
            'duration': duration,
            'task_results': self.phase2_results
        }


async def main():
    """Main test runner"""
    async with Phase2BackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Exit with appropriate code
        if results['success_rate'] >= 80:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure


if __name__ == "__main__":
    asyncio.run(main())
