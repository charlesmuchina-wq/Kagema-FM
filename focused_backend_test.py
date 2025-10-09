#!/usr/bin/env python3
"""
Focused Enhanced Backend Performance Testing for Kagema FM
Mobile Production Requirements Testing Suite - Optimized Version

This test suite covers the essential performance testing requirements:
1. Core API Performance Testing
2. Radio Stream Accessibility Testing  
3. Voice AI Integration Testing
4. Multilingual Support Testing
5. Security & Error Handling Testing
6. Concurrent Load Testing (optimized)
7. Performance Baseline Validation
"""

import requests
import time
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures
import threading

# Test Configuration
BASE_URL = "https://autoradio-debug.preview.emergentagent.com/api"
TIMEOUT = 15  # Reduced timeout for efficiency
MAX_WORKERS = 10  # Reduced for resource management

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    data: Optional[Dict] = None

class FocusedBackendTester:
    """Focused comprehensive backend testing suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> TestResult:
        """Make HTTP request and measure performance"""
        start_time = time.time()
        test_name = f"{method} {endpoint}"
        
        try:
            url = f"{BASE_URL}{endpoint}"
            headers = {
                'User-Agent': 'Kagema-FM-Enhanced-Test/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT, headers=headers)
            else:
                response = requests.get(url, timeout=TIMEOUT, headers=headers)
            
            response_time = time.time() - start_time
            
            # Try to get response data
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                response_data = response.text
            
            return TestResult(
                test_name=test_name,
                success=response.status_code < 400,
                response_time=response_time,
                status_code=response.status_code,
                data=response_data
            )
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                response_time=response_time,
                error_message=str(e)
            )

    def test_core_api_performance(self) -> List[TestResult]:
        """Test core API endpoints performance"""
        print("🔍 Testing Core API Performance...")
        tests = []
        
        # Core API endpoints
        endpoints = [
            ("GET", "/"),
            ("GET", "/app/info"),
            ("GET", "/app/version"),
            ("GET", "/station-info"),
            ("GET", "/languages"),
            ("GET", "/radio/streams"),
            ("GET", "/radio/stations"),
        ]
        
        for method, endpoint in endpoints:
            result = self.make_request(method, endpoint)
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  {method} {endpoint}: {status} ({result.response_time:.3f}s)")
            
        return tests

    def test_radio_streaming_functionality(self) -> List[TestResult]:
        """Test radio streaming and personalized content"""
        print("📻 Testing Radio Streaming Functionality...")
        tests = []
        
        # Test personalized content - CRITICAL for frontend
        test_scenarios = [
            {
                "location": {"latitude": -1.2921, "longitude": 36.8219},  # Nairobi, Kenya
                "preferences": {"preferred_language": "en", "offline_mode": False},
                "name": "Kenya Online"
            },
            {
                "location": {"latitude": -23.5505, "longitude": -46.6333},  # São Paulo, Brazil
                "preferences": {"preferred_language": "pt-br", "offline_mode": False},
                "name": "Brazil Online"
            },
            {
                "location": {"latitude": -1.2921, "longitude": 36.8219},  # Kenya offline
                "preferences": {"preferred_language": "en", "offline_mode": True},
                "name": "Kenya Offline"
            }
        ]
        
        for scenario in test_scenarios:
            result = self.make_request("POST", "/personalized-content/multilingual", scenario)
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  Personalized Content ({scenario['name']}): {status} ({result.response_time:.3f}s)")
            
            # Check for radio_streams data - CRITICAL
            if result.success and result.data and isinstance(result.data, dict):
                if 'radio_streams' in result.data:
                    print(f"    ✅ Radio streams data present")
                else:
                    print(f"    ⚠️  Radio streams data missing")
        
        # Test multilingual station info
        locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo"},
        ]
        
        for location in locations:
            result = self.make_request("POST", "/station-info/multilingual", location)
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  Multilingual Station Info ({location['name']}): {status} ({result.response_time:.3f}s)")
            
        return tests

    def test_voice_ai_integration(self) -> List[TestResult]:
        """Test Voice AI functionality"""
        print("🎤 Testing Voice AI Integration...")
        tests = []
        
        # Voice AI endpoints
        voice_endpoints = [
            ("GET", "/voice/intents"),
            ("GET", "/voice/help"),
        ]
        
        for method, endpoint in voice_endpoints:
            result = self.make_request(method, endpoint)
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  {method} {endpoint}: {status} ({result.response_time:.3f}s)")
        
        # Test voice command interpretation
        voice_commands = [
            {"text": "play radio", "context": "radio_control", "name": "Simple Play"},
            {"text": "pause music", "context": "radio_control", "name": "Simple Pause"},
            {"text": "next station", "context": "radio_control", "name": "Simple Next"},
            {"text": "volume up", "context": "radio_control", "name": "Simple Volume"},
            {"text": "search for jazz music", "context": "music_search", "name": "Complex Search"},
            {"text": "tune to classical station", "context": "station_search", "name": "Complex Tune"},
        ]
        
        for command in voice_commands:
            result = self.make_request("POST", "/voice/interpret", {
                "text": command["text"], 
                "context": command["context"]
            })
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  Voice Command '{command['name']}': {status} ({result.response_time:.3f}s)")
            
        return tests

    def test_multilingual_localization(self) -> List[TestResult]:
        """Test multilingual and localization features"""
        print("🌍 Testing Multilingual & Localization...")
        tests = []
        
        # Test language detection for different regions
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi, Kenya"},
            {"latitude": -0.0917, "longitude": 34.7680, "name": "Kisumu, Kenya (Luo)"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo, Brazil"},
            {"latitude": 40.7128, "longitude": -74.0060, "name": "New York, USA"},
        ]
        
        for location in test_locations:
            result = self.make_request("POST", "/language/detect", {
                "latitude": location["latitude"], 
                "longitude": location["longitude"]
            })
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  Language Detection ({location['name']}): {status} ({result.response_time:.3f}s)")
            
        return tests

    def test_content_compliance_security(self) -> List[TestResult]:
        """Test content compliance and security features"""
        print("🛡️ Testing Content Compliance & Security...")
        tests = []
        
        # Test content disclaimers for different regions
        compliance_tests = [
            {"country_code": "KE", "language_code": "en", "content_types": ["radio_streams"], "name": "Kenya"},
            {"country_code": "BR", "language_code": "pt-br", "content_types": ["radio_streams"], "name": "Brazil"},
            {"country_code": "GLOBAL", "language_code": "en", "content_types": ["radio_streams"], "name": "Global"},
        ]
        
        for test_data in compliance_tests:
            result = self.make_request("POST", "/compliance/disclaimers", test_data)
            tests.append(result)
            status = "✅" if result.success else "❌"
            print(f"  Content Disclaimers ({test_data['name']}): {status} ({result.response_time:.3f}s)")
        
        # Test security - invalid endpoints (should return 404)
        invalid_endpoints = ["/nonexistent", "/admin/secret"]
        for endpoint in invalid_endpoints:
            result = self.make_request("GET", endpoint)
            tests.append(result)
            expected_failure = result.status_code == 404
            status = "✅" if expected_failure else "❌"
            print(f"  Security Test {endpoint}: {status} (Status: {result.status_code})")
        
        # Test malformed requests (should return 422)
        result = self.make_request("POST", "/language/detect", {"invalid": "data"})
        tests.append(result)
        expected_error = result.status_code in [400, 422]
        status = "✅" if expected_error else "❌"
        print(f"  Malformed Request Handling: {status} (Status: {result.status_code})")
        
        return tests

    def test_stream_accessibility(self) -> List[TestResult]:
        """Test radio stream URLs accessibility"""
        print("🎵 Testing Stream Accessibility...")
        tests = []
        
        # Get radio streams first
        streams_result = self.make_request("GET", "/radio/streams")
        if not streams_result.success:
            print("  ❌ Could not get radio streams list")
            return [streams_result]
            
        # Extract and test stream URLs
        stream_urls = []
        try:
            data = streams_result.data
            if isinstance(data, dict):
                # Main station
                if "main_station" in data and "streamUrl" in data["main_station"]:
                    stream_urls.append(("Main Station", data["main_station"]["streamUrl"]))
                
                # Alternative streams (test first 5 for efficiency)
                if "alternative_streams" in data:
                    for i, stream in enumerate(data["alternative_streams"][:5]):
                        if "streamUrl" in stream and "name" in stream:
                            stream_urls.append((stream["name"], stream["streamUrl"]))
        except Exception as e:
            print(f"  ❌ Error parsing streams data: {e}")
            return tests
        
        # Test each stream URL accessibility
        for name, url in stream_urls:
            start_time = time.time()
            try:
                response = requests.head(url, timeout=10, headers={
                    'User-Agent': 'Kagema-FM-Enhanced-Test/1.0'
                })
                response_time = time.time() - start_time
                success = response.status_code < 400
                
                result = TestResult(
                    test_name=f"Stream: {name}",
                    success=success,
                    response_time=response_time,
                    status_code=response.status_code
                )
                tests.append(result)
                status = "✅" if success else "❌"
                print(f"  {name}: {status} ({response_time:.3f}s)")
                
            except Exception as e:
                response_time = time.time() - start_time
                result = TestResult(
                    test_name=f"Stream: {name}",
                    success=False,
                    response_time=response_time,
                    error_message=str(e)
                )
                tests.append(result)
                print(f"  {name}: ❌ ({response_time:.3f}s) - {str(e)}")
                
        return tests

    def test_concurrent_load_optimized(self) -> List[TestResult]:
        """Test concurrent load with optimized approach"""
        print("⚡ Testing Concurrent Load (Optimized)...")
        tests = []
        
        # Test with smaller concurrent loads for efficiency
        test_loads = [5, 10, 15]  # Reduced from original high loads
        
        # Define lightweight endpoints for load testing
        test_endpoints = [
            ("GET", "/"),
            ("GET", "/station-info"),
            ("GET", "/radio/streams"),
        ]
        
        for concurrent_users in test_loads:
            print(f"  Testing {concurrent_users} concurrent users...")
            
            def make_concurrent_request(endpoint_data):
                method, endpoint = endpoint_data
                return self.make_request(method, endpoint)
            
            # Create tasks for concurrent execution
            tasks = []
            for _ in range(concurrent_users):
                for endpoint_data in test_endpoints:
                    tasks.append(endpoint_data)
            
            # Execute concurrent requests
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                results = list(executor.map(make_concurrent_request, tasks))
            
            total_time = time.time() - start_time
            
            # Analyze results
            successful_requests = sum(1 for r in results if r.success)
            total_requests = len(results)
            success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
            
            if successful_requests > 0:
                avg_response_time = statistics.mean([r.response_time for r in results if r.success])
            else:
                avg_response_time = 0
            
            tests.extend(results)
            
            status = "✅" if success_rate >= 90 and avg_response_time <= 2.0 else "❌"
            print(f"    {concurrent_users} users: {status} {success_rate:.1f}% success, {avg_response_time:.3f}s avg")
        
        return tests

    def test_performance_baselines(self) -> List[TestResult]:
        """Test performance against mobile production baselines"""
        print("📊 Testing Performance Baselines...")
        tests = []
        
        # Performance baseline requirements
        BASELINE_WIFI = 0.5  # 500ms for WiFi
        BASELINE_3G = 2.0    # 2000ms for 3G
        
        # Test critical endpoints multiple times for accuracy
        critical_endpoints = [
            ("GET", "/"),
            ("GET", "/station-info"),
            ("POST", "/language/detect", {"latitude": -1.2921, "longitude": 36.8219}),
        ]
        
        for method, endpoint, *args in critical_endpoints:
            data = args[0] if args else None
            
            # Run 3 tests for each endpoint
            response_times = []
            for _ in range(3):
                result = self.make_request(method, endpoint, data)
                tests.append(result)
                if result.success:
                    response_times.append(result.response_time)
            
            if response_times:
                avg_time = statistics.mean(response_times)
                meets_wifi = avg_time <= BASELINE_WIFI
                meets_3g = avg_time <= BASELINE_3G
                
                if meets_wifi:
                    baseline_status = "✅ WiFi Ready"
                elif meets_3g:
                    baseline_status = "✅ 3G Ready"
                else:
                    baseline_status = "❌ Too Slow"
                
                print(f"  {method} {endpoint}: {baseline_status} (Avg: {avg_time:.3f}s)")
        
        return tests

    def calculate_final_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if not self.results:
            return {}
        
        successful_tests = [t for t in self.results if t.success]
        response_times = [t.response_time for t in self.results if t.response_time > 0]
        
        total_tests = len(self.results)
        successful_count = len(successful_tests)
        success_rate = (successful_count / total_tests) * 100 if total_tests > 0 else 0
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_count,
            'failed_tests': total_tests - successful_count,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'wifi_ready': avg_response_time <= 0.5,
            'mobile_3g_ready': avg_response_time <= 2.0,
            'production_ready': success_rate >= 90 and avg_response_time <= 2.0
        }

    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Enhanced Comprehensive Backend Performance Testing")
        print("=" * 70)
        print("Mobile Production Requirements Testing Suite")
        print("=" * 70)
        
        # Execute all test categories
        self.results.extend(self.test_core_api_performance())
        self.results.extend(self.test_radio_streaming_functionality())
        self.results.extend(self.test_voice_ai_integration())
        self.results.extend(self.test_multilingual_localization())
        self.results.extend(self.test_content_compliance_security())
        self.results.extend(self.test_stream_accessibility())
        self.results.extend(self.test_concurrent_load_optimized())
        self.results.extend(self.test_performance_baselines())
        
        # Calculate final metrics
        metrics = self.calculate_final_metrics()
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("📊 ENHANCED PERFORMANCE TESTING RESULTS")
        print("=" * 70)
        print(f"Total Test Duration: {total_time:.1f} seconds")
        print(f"Total Tests Executed: {metrics.get('total_tests', 0)}")
        print(f"Successful Tests: {metrics.get('successful_tests', 0)}")
        print(f"Failed Tests: {metrics.get('failed_tests', 0)}")
        print(f"Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"Average Response Time: {metrics.get('avg_response_time', 0):.3f}s")
        print(f"Min Response Time: {metrics.get('min_response_time', 0):.3f}s")
        print(f"Max Response Time: {metrics.get('max_response_time', 0):.3f}s")
        
        print("\n🎯 MOBILE PRODUCTION READINESS ASSESSMENT:")
        
        # Performance baseline assessment
        if metrics.get('wifi_ready', False):
            print("✅ WiFi Performance: EXCELLENT (< 500ms)")
        elif metrics.get('mobile_3g_ready', False):
            print("✅ 3G Performance: GOOD (< 2000ms)")
        else:
            print("❌ Performance: NEEDS IMPROVEMENT (> 2000ms)")
        
        # Success rate assessment
        success_rate = metrics.get('success_rate', 0)
        if success_rate >= 95:
            print("✅ Reliability: EXCELLENT (≥ 95%)")
        elif success_rate >= 90:
            print("✅ Reliability: GOOD (≥ 90%)")
        else:
            print("❌ Reliability: NEEDS IMPROVEMENT (< 90%)")
        
        # Overall production readiness
        if metrics.get('production_ready', False):
            print("✅ PRODUCTION READY: All mobile performance criteria met!")
        else:
            print("❌ NOT PRODUCTION READY: Performance optimization required")
        
        print("\n" + "=" * 70)
        print("🎉 ENHANCED COMPREHENSIVE BACKEND TESTING COMPLETE!")
        print("=" * 70)
        
        return metrics

def main():
    """Main test execution function"""
    try:
        tester = FocusedBackendTester()
        metrics = tester.run_comprehensive_tests()
        
        # Return success based on production readiness
        if metrics.get('production_ready', False):
            print("\n🎉 ALL MOBILE PRODUCTION CRITERIA MET!")
            return 0
        else:
            print("\n⚠️ MOBILE PRODUCTION CRITERIA NOT FULLY MET")
            return 1
            
    except Exception as e:
        print(f"\n❌ TESTING FAILED: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)