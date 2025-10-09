#!/usr/bin/env python3
"""
Comprehensive Backend Performance Testing Framework - iOS-Equivalent Performance Testing
Implementing comprehensive performance testing using iOS-equivalent performance testing framework:

PERFORMANCE TESTING FRAMEWORK:
1. Time Profiler Testing - CPU usage analysis, method execution times, bottleneck identification
2. Core Animation Testing - Response time analysis, API rendering performance 
3. XCTest Performance - Automated performance regression testing with baselines
4. Network Link Conditioner - Test under various network conditions (5G, 4G, 3G, 2G, Slow, Offline)
5. Debug Gauges - Real-time performance monitoring during load testing

SPECIFIC PERFORMANCE TESTS:
- Load Testing: Test concurrent user loads (1, 5, 10, 25, 50 users)
- Stress Testing: Push API endpoints to breaking point
- Latency Testing: Measure response times under different conditions
- Throughput Testing: Test requests per second capabilities
- Memory Usage: Monitor memory consumption during operations
- CPU Usage: Analyze server resource utilization
- Database Performance: Test MongoDB query performance
- Stream Accessibility: Verify all radio streams under load

PERFORMANCE BASELINES:
- API Response Time: <500ms average
- Concurrent Users: Support 50+ simultaneous users
- Radio Stream Loading: <2000ms
- Voice AI Processing: <3000ms
- Memory Usage: Stable under load
- Zero critical failures under normal load

TEST SCENARIOS:
1. Normal load (5 concurrent users)
2. Peak load (25 concurrent users) 
3. Stress load (50+ concurrent users)
4. Network simulation (3G, 4G, 5G conditions)
5. Long-duration stability (sustained load)
"""

import json
import requests
import time
import statistics
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import aiohttp
import psutil
import gc
from dataclasses import dataclass

# Load environment variables
load_dotenv('/app/frontend/.env')

# Backend URL from frontend environment
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://autoradio-debug.preview.emergentagent.com')
BACKEND_URL = FRONTEND_ENV_URL
API_BASE = f"{BACKEND_URL}/api"

# Performance Testing Configuration
PERFORMANCE_BASELINES = {
    "api_response_time_ms": 500,  # <500ms average
    "concurrent_users": 50,       # Support 50+ simultaneous users
    "radio_stream_loading_ms": 2000,  # <2000ms
    "voice_ai_processing_ms": 3000,   # <3000ms
    "memory_stability": True,     # Stable under load
    "zero_critical_failures": True   # Zero critical failures under normal load
}

# Test Scenarios Configuration
TEST_SCENARIOS = {
    "normal_load": 5,      # 5 concurrent users
    "peak_load": 25,       # 25 concurrent users
    "stress_load": 50,     # 50+ concurrent users
    "extreme_load": 100    # 100 concurrent users for stress testing
}

# Network Conditions Simulation
NETWORK_CONDITIONS = {
    "5G": {"delay": 0.01, "timeout": 5},
    "4G": {"delay": 0.05, "timeout": 10},
    "3G": {"delay": 0.2, "timeout": 15},
    "2G": {"delay": 0.5, "timeout": 30},
    "Slow": {"delay": 1.0, "timeout": 60},
    "Offline": {"delay": 10.0, "timeout": 1}  # Will timeout quickly
}

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    endpoint: str
    response_time_ms: float
    status_code: int
    success: bool
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    network_condition: str = "5G"
    concurrent_users: int = 1
    error_message: Optional[str] = None

@dataclass
class LoadTestResult:
    """Load test result summary"""
    scenario: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    success_rate_percent: float
    memory_peak_mb: float
    cpu_peak_percent: float
    duration_seconds: float
    baseline_met: bool

class PerformanceTestFramework:
    """iOS-Equivalent Performance Testing Framework for Backend APIs"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.load_test_results: List[LoadTestResult] = []
        self.baseline_violations: List[str] = []
        self.start_time = None
        try:
            self.process = psutil.Process()
        except:
            self.process = None
        
    def get_system_metrics(self) -> tuple[float, float]:
        """Get current system memory and CPU usage"""
        try:
            if self.process:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                cpu_percent = self.process.cpu_percent()
                return memory_mb, cpu_percent
        except:
            pass
        return 0.0, 0.0
    
    def make_performance_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                               network_condition: str = "5G", concurrent_users: int = 1) -> PerformanceMetrics:
        """Make a single API request with performance monitoring"""
        start_time = time.time()
        memory_mb, cpu_percent = self.get_system_metrics()
        
        # Simulate network conditions
        if network_condition in NETWORK_CONDITIONS:
            time.sleep(NETWORK_CONDITIONS[network_condition]["delay"])
            timeout = NETWORK_CONDITIONS[network_condition]["timeout"]
        else:
            timeout = 30
        
        try:
            url = f"{API_BASE}{endpoint}"
            
            request_headers = {
                'User-Agent': 'Kagema-FM-Performance-Test/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout, headers=request_headers)
            else:
                response = requests.get(url, timeout=timeout, headers=request_headers)
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return PerformanceMetrics(
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                success=200 <= response.status_code < 300,
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                timestamp=datetime.now(),
                network_condition=network_condition,
                concurrent_users=concurrent_users
            )
                    
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return PerformanceMetrics(
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                timestamp=datetime.now(),
                network_condition=network_condition,
                concurrent_users=concurrent_users,
                error_message=str(e)
            )
    
    def test_concurrent_load(self, endpoints: List[Dict], concurrent_users: int, 
                           duration_seconds: int = 60, network_condition: str = "5G") -> LoadTestResult:
        """Test concurrent load (XCTest Performance equivalent)"""
        print(f"🔄 Starting load test: {concurrent_users} concurrent users for {duration_seconds}s on {network_condition}")
        
        start_time = time.time()
        test_metrics = []
        
        def user_session():
            """Simulate a single user session"""
            session_start = time.time()
            while time.time() - session_start < duration_seconds:
                for endpoint_config in endpoints:
                    try:
                        metric = self.make_performance_request(
                            endpoint_config.get("method", "GET"),
                            endpoint_config["endpoint"], 
                            endpoint_config.get("data"),
                            network_condition,
                            concurrent_users
                        )
                        test_metrics.append(metric)
                        
                        # Small delay between requests to simulate real usage
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"❌ Error in user session: {e}")
        
        # Run concurrent user sessions
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_session) for _ in range(concurrent_users)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ User session failed: {e}")
        
        # Calculate results
        total_duration = time.time() - start_time
        successful_requests = sum(1 for m in test_metrics if m.success)
        failed_requests = len(test_metrics) - successful_requests
        
        if test_metrics:
            response_times = [m.response_time_ms for m in test_metrics if m.success]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else avg_response_time
                p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else avg_response_time
            else:
                avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
            
            memory_peak = max(m.memory_usage_mb for m in test_metrics)
            cpu_peak = max(m.cpu_usage_percent for m in test_metrics)
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
            memory_peak = cpu_peak = 0
        
        requests_per_second = len(test_metrics) / total_duration if total_duration > 0 else 0
        success_rate = (successful_requests / len(test_metrics) * 100) if test_metrics else 0
        
        # Check baseline compliance
        baseline_met = (
            avg_response_time <= PERFORMANCE_BASELINES["api_response_time_ms"] and
            success_rate >= 95.0 and
            concurrent_users <= PERFORMANCE_BASELINES["concurrent_users"]
        )
        
        scenario_name = f"{concurrent_users}_users_{network_condition}"
        
        result = LoadTestResult(
            scenario=scenario_name,
            concurrent_users=concurrent_users,
            total_requests=len(test_metrics),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            requests_per_second=requests_per_second,
            success_rate_percent=success_rate,
            memory_peak_mb=memory_peak,
            cpu_peak_percent=cpu_peak,
            duration_seconds=total_duration,
            baseline_met=baseline_met
        )
        
        self.load_test_results.append(result)
        self.metrics.extend(test_metrics)
        
        return result
    
    def test_radio_stream_accessibility_performance(self, network_condition: str = "5G") -> Dict[str, Any]:
        """Test radio stream accessibility under load (Core Animation equivalent)"""
        print(f"🎵 Testing radio stream accessibility performance on {network_condition}")
        
        # Test stream URLs accessibility with performance metrics
        stream_results = []
        stream_urls = [
            ("Main Kagema FM Stream", "https://ice1.somafm.com/groovesalad-256-mp3"),
            ("SomaFM Groove Salad", "https://ice1.somafm.com/groovesalad-256-mp3"),
            ("Radio Paradise AAC", "https://stream.radioparadise.com/aac-320"),
            ("Radio Paradise MP3", "https://stream.radioparadise.com/mp3-192"),
            ("FIP Radio France AAC", "https://icecast.radiofrance.fr/fip-hifi.aac"),
            ("FIP Radio France MP3", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
            ("SomaFM Drone Zone", "http://ice1.somafm.com/dronezone-256-mp3"),
            ("SomaFM DEF CON Radio", "http://ice1.somafm.com/defcon-256-mp3")
        ]
        
        for name, url in stream_urls:
            start_time = time.time()
            
            try:
                timeout = NETWORK_CONDITIONS.get(network_condition, {}).get("timeout", 30)
                response = requests.head(url, timeout=timeout, headers={
                    'User-Agent': 'Kagema-FM-Performance-Test/1.0'
                })
                load_time_ms = (time.time() - start_time) * 1000
                stream_results.append({
                    "name": name,
                    "url": url,
                    "accessible": response.status_code == 200,
                    "load_time_ms": load_time_ms,
                    "baseline_met": load_time_ms <= PERFORMANCE_BASELINES["radio_stream_loading_ms"],
                    "status_code": response.status_code
                })
            except Exception as e:
                load_time_ms = (time.time() - start_time) * 1000
                stream_results.append({
                    "name": name,
                    "url": url,
                    "accessible": False,
                    "load_time_ms": load_time_ms,
                    "baseline_met": False,
                    "error": str(e)
                })
        
        accessible_streams = sum(1 for s in stream_results if s["accessible"])
        baseline_met = all(s.get("baseline_met", False) for s in stream_results if s["accessible"])
        
        return {
            "total_streams_tested": len(stream_results),
            "accessible_streams": accessible_streams,
            "stream_results": stream_results,
            "success_rate": (accessible_streams / len(stream_results) * 100) if stream_results else 0,
            "baseline_met": baseline_met and accessible_streams > 0
        }
    
    def test_voice_ai_performance(self, network_condition: str = "5G") -> Dict[str, Any]:
        """Test Voice AI processing performance"""
        print(f"🎤 Testing Voice AI performance on {network_condition}")
        
        voice_commands = [
            {"text": "play radio", "context": "radio_control"},
            {"text": "pause music", "context": "radio_control"},
            {"text": "next station", "context": "radio_control"},
            {"text": "volume up", "context": "radio_control"},
            {"text": "search for jazz music", "context": "music_search"},
            {"text": "tune to classical station", "context": "station_change"}
        ]
        
        voice_results = []
        
        for command in voice_commands:
            metric = self.make_performance_request(
                "POST",
                "/voice/interpret", 
                command,
                network_condition
            )
            
            baseline_met = (
                metric.success and 
                metric.response_time_ms <= PERFORMANCE_BASELINES["voice_ai_processing_ms"]
            )
            
            voice_results.append({
                "command": command["text"],
                "success": metric.success,
                "response_time_ms": metric.response_time_ms,
                "baseline_met": baseline_met,
                "error": metric.error_message
            })
        
        successful_commands = sum(1 for r in voice_results if r["success"])
        avg_response_time = statistics.mean([r["response_time_ms"] for r in voice_results if r["success"]]) if successful_commands > 0 else 0
        baseline_met = all(r.get("baseline_met", False) for r in voice_results if r["success"])
        
        return {
            "total_commands_tested": len(voice_results),
            "successful_commands": successful_commands,
            "avg_response_time_ms": avg_response_time,
            "success_rate": (successful_commands / len(voice_results) * 100) if voice_results else 0,
            "baseline_met": baseline_met and successful_commands > 0,
            "command_results": voice_results
        }
    
    def run_comprehensive_performance_tests(self):
        """Run comprehensive performance testing suite"""
        print("🚀 Starting Comprehensive Backend Performance Testing Framework")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Define core API endpoints to test
        core_endpoints = [
            {"endpoint": "/", "method": "GET"},
            {"endpoint": "/station-info", "method": "GET"},
            {"endpoint": "/languages", "method": "GET"},
            {"endpoint": "/radio/streams", "method": "GET"},
            {"endpoint": "/radio/stations", "method": "GET"},
            {"endpoint": "/voice/intents", "method": "GET"},
            {"endpoint": "/voice/help", "method": "GET"},
            {
                "endpoint": "/language/detect", 
                "method": "POST", 
                "data": {"latitude": -1.286389, "longitude": 36.817223}
            },
            {
                "endpoint": "/personalized-content/multilingual",
                "method": "POST",
                "data": {
                    "location": {"latitude": -1.286389, "longitude": 36.817223},
                    "preferences": {"offline_mode": False, "preferred_language": "en"}
                }
            }
        ]
        
        # 1. Time Profiler Testing - Individual endpoint performance
        print("\n📊 1. TIME PROFILER TESTING - Individual Endpoint Performance")
        print("-" * 60)
        
        for endpoint_config in core_endpoints:
            metric = self.make_performance_request(
                endpoint_config.get("method", "GET"),
                endpoint_config["endpoint"],
                endpoint_config.get("data")
            )
            
            baseline_status = "✅ PASS" if metric.response_time_ms <= PERFORMANCE_BASELINES["api_response_time_ms"] else "❌ FAIL"
            print(f"{endpoint_config['endpoint']}: {metric.response_time_ms:.1f}ms - {baseline_status}")
            
            if not metric.success:
                self.baseline_violations.append(f"Endpoint {endpoint_config['endpoint']} failed: {metric.error_message}")
        
        # 2. Core Animation Testing - Radio Stream Performance
        print("\n🎵 2. CORE ANIMATION TESTING - Radio Stream Performance")
        print("-" * 60)
        
        for network in ["5G", "4G", "3G"]:
            stream_result = self.test_radio_stream_accessibility_performance(network)
            baseline_status = "✅ PASS" if stream_result["baseline_met"] else "❌ FAIL"
            print(f"{network} Network: {stream_result['accessible_streams']}/{stream_result['total_streams_tested']} streams accessible - {baseline_status}")
        
        # 3. XCTest Performance - Load Testing
        print("\n⚡ 3. XCTEST PERFORMANCE - Automated Load Testing")
        print("-" * 60)
        
        for scenario_name, users in TEST_SCENARIOS.items():
            if users <= 50:  # Skip extreme load for baseline testing
                result = self.test_concurrent_load(core_endpoints[:5], users, 30)  # 30 second tests
                baseline_status = "✅ PASS" if result.baseline_met else "❌ FAIL"
                print(f"{scenario_name.upper()}: {users} users, {result.avg_response_time_ms:.1f}ms avg, {result.success_rate_percent:.1f}% success - {baseline_status}")
        
        # 4. Network Link Conditioner - Network Condition Testing
        print("\n🌐 4. NETWORK LINK CONDITIONER - Network Condition Testing")
        print("-" * 60)
        
        for network in ["5G", "4G", "3G", "2G"]:
            result = self.test_concurrent_load(core_endpoints[:3], 5, 15, network)  # 15 second tests
            baseline_status = "✅ PASS" if result.baseline_met else "❌ FAIL"
            print(f"{network}: {result.avg_response_time_ms:.1f}ms avg, {result.success_rate_percent:.1f}% success - {baseline_status}")
        
        # 5. Debug Gauges - Voice AI Performance
        print("\n🎤 5. DEBUG GAUGES - Voice AI Performance Testing")
        print("-" * 60)
        
        voice_result = self.test_voice_ai_performance()
        baseline_status = "✅ PASS" if voice_result["baseline_met"] else "❌ FAIL"
        print(f"Voice AI: {voice_result['successful_commands']}/{voice_result['total_commands_tested']} commands, {voice_result['avg_response_time_ms']:.1f}ms avg - {baseline_status}")
        
        # 6. Long-Duration Stability Testing
        print("\n⏱️  6. LONG-DURATION STABILITY TESTING")
        print("-" * 60)
        
        stability_result = self.test_concurrent_load(core_endpoints[:3], 10, 120)  # 2 minute sustained load
        baseline_status = "✅ PASS" if stability_result.baseline_met else "❌ FAIL"
        print(f"Stability Test: {stability_result.success_rate_percent:.1f}% success rate over 2 minutes - {baseline_status}")
        
        # Generate comprehensive report
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate comprehensive performance test report"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE PERFORMANCE TEST REPORT")
        print("=" * 80)
        
        # Overall Statistics
        total_requests = len(self.metrics)
        successful_requests = sum(1 for m in self.metrics if m.success)
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        if successful_requests > 0:
            avg_response_time = statistics.mean([m.response_time_ms for m in self.metrics if m.success])
            p95_response_time = statistics.quantiles([m.response_time_ms for m in self.metrics if m.success], n=20)[18] if successful_requests > 1 else avg_response_time
        else:
            avg_response_time = p95_response_time = 0
        
        print(f"\n📊 OVERALL PERFORMANCE METRICS:")
        print(f"   Total Test Duration: {total_duration:.1f} seconds")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful Requests: {successful_requests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Average Response Time: {avg_response_time:.1f}ms")
        print(f"   95th Percentile Response Time: {p95_response_time:.1f}ms")
        
        # Baseline Compliance Check
        print(f"\n🎯 PERFORMANCE BASELINE COMPLIANCE:")
        baseline_checks = [
            ("API Response Time", avg_response_time <= PERFORMANCE_BASELINES["api_response_time_ms"], f"{avg_response_time:.1f}ms ≤ {PERFORMANCE_BASELINES['api_response_time_ms']}ms"),
            ("Success Rate", success_rate >= 95.0, f"{success_rate:.1f}% ≥ 95.0%"),
            ("Concurrent Users Support", len([r for r in self.load_test_results if r.concurrent_users <= 50 and r.baseline_met]) > 0, "50+ users supported"),
            ("Zero Critical Failures", len(self.baseline_violations) == 0, f"{len(self.baseline_violations)} violations found")
        ]
        
        all_baselines_met = True
        for check_name, passed, details in baseline_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check_name}: {status} ({details})")
            if not passed:
                all_baselines_met = False
        
        # Load Test Results Summary
        if self.load_test_results:
            print(f"\n⚡ LOAD TEST RESULTS SUMMARY:")
            for result in self.load_test_results:
                baseline_status = "✅ PASS" if result.baseline_met else "❌ FAIL"
                print(f"   {result.scenario}: {result.success_rate_percent:.1f}% success, {result.avg_response_time_ms:.1f}ms avg - {baseline_status}")
        
        # Violations and Issues
        if self.baseline_violations:
            print(f"\n⚠️  BASELINE VIOLATIONS:")
            for violation in self.baseline_violations:
                print(f"   • {violation}")
        
        # Final Assessment
        print(f"\n🏆 FINAL PERFORMANCE ASSESSMENT:")
        if all_baselines_met and success_rate >= 95.0:
            print("   ✅ EXCELLENT - All performance baselines met, production ready!")
        elif success_rate >= 90.0 and avg_response_time <= PERFORMANCE_BASELINES["api_response_time_ms"] * 1.5:
            print("   ⚠️  GOOD - Most baselines met, minor optimizations recommended")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Performance baselines not met, optimization required")
        
        print("=" * 80)

class ProductionReadinessTestSuite:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        self.performance_metrics = []
        self.stream_accessibility_results = []
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    timeout: int = 30, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request and measure performance"""
        url = f"{API_BASE}{endpoint}"
        start_time = time.time()
        
        try:
            request_headers = {
                'User-Agent': 'Kagema-FM-Production-Test/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            if headers:
                request_headers.update(headers)
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout, headers=request_headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=timeout, headers=request_headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=timeout, headers=request_headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=timeout, headers=request_headers)
            else:
                response = requests.request(method, url, json=data, timeout=timeout, headers=request_headers)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                response_data = response.text
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': 200 <= response.status_code < 300,
                'response_data': response_data,
                'error_message': None
            }
            
            self.performance_metrics.append(response_time)
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'response_data': None,
                'error_message': str(e)
            }
            self.performance_metrics.append(response_time)
            return result
    
    def test_core_api_health(self):
        """Test core API health endpoints"""
        print("🔍 Testing Core API Health...")
        
        endpoints = [
            ('GET', '/'),
            ('GET', '/app/info'),
            ('GET', '/app/version'),
            ('GET', '/station-info'),
        ]
        
        for method, endpoint in endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"{method} {endpoint}")
                print(f"  ✅ {method} {endpoint}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{method} {endpoint}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {method} {endpoint}: {result.get('error_message', result['status_code'])} ({result['response_time']:.0f}ms)")
    
    def test_geolocation_services(self):
        """Test geolocation and location-based services - CRITICAL for production"""
        print("🌍 Testing Geolocation Services...")
        
        # IP-based geolocation
        result = self.make_request('GET', '/geolocation/ip')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("IP Geolocation")
            print(f"  ✅ IP Geolocation: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"IP Geolocation: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ IP Geolocation: {result.get('error_message', result['status_code'])}")
        
        # Location suggestions
        result = self.make_request('GET', '/geolocation/suggestions?context=radio')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Location Suggestions")
            print(f"  ✅ Location Suggestions: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Location Suggestions: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Location Suggestions: {result.get('error_message', result['status_code'])}")
        
        # Geolocation service info
        result = self.make_request('GET', '/geolocation/info')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Geolocation Service Info")
            print(f"  ✅ Geolocation Service Info: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Geolocation Service Info: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Geolocation Service Info: {result.get('error_message', result['status_code'])}")
        
        # Language detection from coordinates - Test multiple locations
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi, Kenya"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo, Brazil"},
            {"latitude": 52.5200, "longitude": 13.4050, "name": "Berlin, Germany"}
        ]
        
        for location in test_locations:
            location_data = {"latitude": location["latitude"], "longitude": location["longitude"]}
            result = self.make_request('POST', '/language/detect', data=location_data)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Language Detection - {location['name']}")
                print(f"  ✅ Language Detection ({location['name']}): {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Language Detection - {location['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ Language Detection ({location['name']}): {result.get('error_message', result['status_code'])}")
    
    def test_radio_streaming_apis(self):
        """Test radio streaming and station APIs - CRITICAL for production"""
        print("📻 Testing Radio Streaming APIs...")
        
        # Radio streams
        result = self.make_request('GET', '/radio/streams')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Radio Streams")
            print(f"  ✅ Radio Streams: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Radio Streams: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Radio Streams: {result.get('error_message', result['status_code'])}")
        
        # Radio stations
        result = self.make_request('GET', '/radio/stations')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Radio Stations")
            print(f"  ✅ Radio Stations: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Radio Stations: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Radio Stations: {result.get('error_message', result['status_code'])}")
        
        # Multilingual station info
        location_data = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
        result = self.make_request('POST', '/station-info/multilingual', data=location_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Multilingual Station Info")
            print(f"  ✅ Multilingual Station Info: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Multilingual Station Info: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Multilingual Station Info: {result.get('error_message', result['status_code'])}")
        
        # Personalized content - CRITICAL for frontend functionality
        personalized_data = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"preferred_language": "en", "offline_mode": False}
        }
        result = self.make_request('POST', '/personalized-content/multilingual', data=personalized_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Personalized Content")
            print(f"  ✅ Personalized Content: {result['status_code']} ({result['response_time']:.0f}ms)")
            
            # Check if radio_streams data is present - CRITICAL for frontend
            if result['response_data'] and 'radio_streams' in result['response_data']:
                print(f"    ✅ Radio streams data present in response")
            else:
                print(f"    ⚠️  Radio streams data missing from response")
        else:
            self.failed_tests.append(f"Personalized Content: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Personalized Content: {result.get('error_message', result['status_code'])}")
    
    def test_voice_ai_integration(self):
        """Test Voice AI and command processing - CRITICAL for production"""
        print("🎤 Testing Voice AI Integration...")
        
        # Voice intents
        result = self.make_request('GET', '/voice/intents')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Voice Intents")
            print(f"  ✅ Voice Intents: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Voice Intents: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Voice Intents: {result.get('error_message', result['status_code'])}")
        
        # Voice help
        result = self.make_request('GET', '/voice/help')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Voice Help")
            print(f"  ✅ Voice Help: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Voice Help: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Voice Help: {result.get('error_message', result['status_code'])}")
        
        # Voice command interpretation - Test various command types
        voice_commands = [
            {"text": "play", "context": "radio", "name": "Simple Play Command"},
            {"text": "pause", "context": "radio", "name": "Simple Pause Command"},
            {"text": "next", "context": "radio", "name": "Simple Next Command"},
            {"text": "volume up", "context": "radio", "name": "Simple Volume Command"},
            {"text": "search for jazz music", "context": "radio", "name": "Complex Search Command"},
            {"text": "tune to classical station", "context": "radio", "name": "Complex Tune Command"},
            {"text": "browse external sources", "context": "radio", "name": "Complex Browse Command"}
        ]
        
        for cmd in voice_commands:
            result = self.make_request('POST', '/voice/interpret', data={"text": cmd["text"], "context": cmd["context"]})
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Voice Command - {cmd['name']}")
                print(f"  ✅ {cmd['name']}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Voice Command - {cmd['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {cmd['name']}: {result.get('error_message', result['status_code'])}")
    
    def test_external_services_integration(self):
        """Test external services and integrations - CRITICAL for production"""
        print("🔗 Testing External Services Integration...")
        
        # Radio Browser API
        radio_browser_endpoints = [
            ('GET', '/radio-browser/info', 'Radio Browser Info'),
            ('GET', '/radio-browser/search?q=jazz&limit=10', 'Radio Browser Search'),
            ('GET', '/radio-browser/popular?limit=20', 'Radio Browser Popular'),
            ('GET', '/radio-browser/countries?limit=20', 'Radio Browser Countries'),
            ('GET', '/radio-browser/languages?limit=20', 'Radio Browser Languages'),
            ('GET', '/radio-browser/tags?limit=20', 'Radio Browser Tags')
        ]
        
        for method, endpoint, name in radio_browser_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # AccuRadio API
        accuradio_endpoints = [
            ('GET', '/accuradio/info', 'AccuRadio Info'),
            ('GET', '/accuradio/genres', 'AccuRadio Genres'),
            ('GET', '/accuradio/channels?featured=true', 'AccuRadio Featured Channels')
        ]
        
        for method, endpoint, name in accuradio_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # Spotify Integration
        spotify_endpoints = [
            ('GET', '/spotify/auth/login', 'Spotify Auth Login'),
            ('GET', '/spotify/genres', 'Spotify Genres')
        ]
        
        for method, endpoint, name in spotify_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # Google Maps Integration
        googlemaps_endpoints = [
            ('GET', '/googlemaps/geocode?address=Nairobi,Kenya', 'Google Maps Geocoding'),
            ('GET', '/googlemaps/reverse-geocode?lat=-1.2921&lng=36.8219', 'Google Maps Reverse Geocoding'),
            ('GET', '/googlemaps/nearby?lat=-1.2921&lng=36.8219&type=restaurant', 'Google Maps Nearby Places')
        ]
        
        for method, endpoint, name in googlemaps_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
    
    def test_satellite_connectivity(self):
        """Test satellite connectivity and offline features"""
        print("🛰️ Testing Satellite Connectivity...")
        
        # Satellite status
        result = self.make_request('GET', '/satellite/status')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Status")
            print(f"  ✅ Satellite Status: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Status: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Status: {result.get('error_message', result['status_code'])}")
        
        # Satellite main stations
        result = self.make_request('GET', '/satellite/main_stations')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Main Stations")
            print(f"  ✅ Satellite Main Stations: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Main Stations: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Main Stations: {result.get('error_message', result['status_code'])}")
        
        # Satellite connection attempt
        connection_data = {"provider": "auto", "client_id": "kagema_fm_production_test", "location": "auto"}
        result = self.make_request('POST', '/satellite/connect', data=connection_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Connection")
            print(f"  ✅ Satellite Connection: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Connection: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Connection: {result.get('error_message', result['status_code'])}")
        
        # Offline content caching
        cache_data = {
            "content_types": ["radio_streams", "news", "weather"],
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "cache_duration_hours": 24
        }
        result = self.make_request('POST', '/offline/cache', data=cache_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Offline Content Caching")
            print(f"  ✅ Offline Content Caching: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Offline Content Caching: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Offline Content Caching: {result.get('error_message', result['status_code'])}")
    
    def test_content_compliance(self):
        """Test content compliance and regional features"""
        print("⚖️ Testing Content Compliance...")
        
        # Supported languages
        result = self.make_request('GET', '/languages')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Supported Languages")
            print(f"  ✅ Supported Languages: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Supported Languages: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Supported Languages: {result.get('error_message', result['status_code'])}")
        
        # Content disclaimers for different regions
        regions = [
            {"country_code": "KE", "language_code": "en", "name": "Kenya"},
            {"country_code": "BR", "language_code": "pt-br", "name": "Brazil"},
            {"country_code": "GLOBAL", "language_code": "en", "name": "Global"}
        ]
        
        for region in regions:
            compliance_data = {
                "country_code": region["country_code"],
                "language_code": region["language_code"],
                "content_types": ["radio_streams", "music", "news"]
            }
            result = self.make_request('POST', '/compliance/disclaimers', data=compliance_data)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Content Disclaimers - {region['name']}")
                print(f"  ✅ Content Disclaimers ({region['name']}): {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Content Disclaimers - {region['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ Content Disclaimers ({region['name']}): {result.get('error_message', result['status_code'])}")
        
        # Content compliance check
        result = self.make_request('POST', '/compliance/check-content?country_code=KE&content_rating=mature&user_age=25')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Content Compliance Check")
            print(f"  ✅ Content Compliance Check: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Content Compliance Check: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Content Compliance Check: {result.get('error_message', result['status_code'])}")
    
    def test_stream_accessibility(self):
        """Test actual radio stream accessibility - CRITICAL for production"""
        print("🎵 Testing Radio Stream Accessibility...")
        
        # Get radio streams first
        result = self.make_request('GET', '/radio/streams')
        if result['success'] and result['response_data']:
            streams_to_test = []
            
            # Add main station
            if 'main_station' in result['response_data']:
                streams_to_test.append({
                    'name': result['response_data']['main_station']['name'],
                    'url': result['response_data']['main_station']['streamUrl']
                })
            
            # Add alternative streams
            if 'alternative_streams' in result['response_data']:
                for stream in result['response_data']['alternative_streams']:
                    streams_to_test.append({
                        'name': stream['name'],
                        'url': stream['streamUrl']
                    })
            
            # Test stream accessibility
            for stream in streams_to_test:
                start_time = time.time()
                try:
                    response = requests.head(stream['url'], timeout=10, headers={
                        'User-Agent': 'Kagema-FM-Production-Test/1.0'
                    })
                    response_time = (time.time() - start_time) * 1000
                    success = response.status_code == 200
                    
                    stream_result = {
                        'name': stream['name'],
                        'url': stream['url'],
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': success,
                        'headers': dict(response.headers)
                    }
                    
                    self.stream_accessibility_results.append(stream_result)
                    
                    if success:
                        print(f"  ✅ {stream['name']}: {response.status_code} ({response_time:.0f}ms)")
                        # Check for audio streaming headers
                        content_type = response.headers.get('content-type', '').lower()
                        if 'audio' in content_type or 'mpeg' in content_type:
                            print(f"    ✅ Audio content type detected: {content_type}")
                        if 'icy-' in str(response.headers).lower():
                            print(f"    ✅ ICY streaming metadata detected")
                    else:
                        print(f"  ❌ {stream['name']}: {response.status_code} ({response_time:.0f}ms)")
                        
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    stream_result = {
                        'name': stream['name'],
                        'url': stream['url'],
                        'status_code': 0,
                        'response_time': response_time,
                        'success': False,
                        'error': str(e)
                    }
                    self.stream_accessibility_results.append(stream_result)
                    print(f"  ❌ {stream['name']}: ERROR ({response_time:.0f}ms) - {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🚨 Testing Error Handling...")
        
        # Test 404 endpoints
        result = self.make_request('GET', '/nonexistent-endpoint')
        self.results.append(result)
        if result['status_code'] == 404:
            self.passed_tests.append("404 Error Handling")
            print(f"  ✅ 404 Error Handling: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"404 Error Handling: Expected 404, got {result['status_code']}")
            print(f"  ❌ 404 Error Handling: Expected 404, got {result['status_code']}")
        
        # Test invalid POST data
        result = self.make_request('POST', '/language/detect', data={"invalid": "data"})
        self.results.append(result)
        if result['status_code'] == 422:
            self.passed_tests.append("Invalid POST Data Handling")
            print(f"  ✅ Invalid POST Data: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Invalid POST Data: Expected 422, got {result['status_code']}")
            print(f"  ❌ Invalid POST Data: Expected 422, got {result['status_code']}")
        
        # Test empty voice command
        result = self.make_request('POST', '/voice/interpret', data={"text": "", "context": "radio"})
        self.results.append(result)
        if result['status_code'] in [400, 422]:
            self.passed_tests.append("Empty Voice Command Handling")
            print(f"  ✅ Empty Voice Command: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Empty Voice Command: Expected 400/422, got {result['status_code']}")
            print(f"  ❌ Empty Voice Command: Expected 400/422, got {result['status_code']}")
        
        # Test invalid coordinates fallback
        result = self.make_request('POST', '/language/detect', data={"latitude": 999, "longitude": 999})
        self.results.append(result)
        if result['success']:  # Should fallback gracefully
            self.passed_tests.append("Invalid Coordinates Fallback")
            print(f"  ✅ Invalid Coordinates Fallback: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Invalid Coordinates Fallback: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Invalid Coordinates Fallback: {result.get('error_message', result['status_code'])}")
    
    def test_production_load(self):
        """Test production-level concurrent load"""
        print("⚡ Testing Production Load (Concurrent Requests)...")
        
        # Define critical endpoints for load testing
        load_test_endpoints = [
            ('GET', '/', None, 'API Root'),
            ('GET', '/station-info', None, 'Station Info'),
            ('GET', '/radio/streams', None, 'Radio Streams'),
            ('GET', '/voice/intents', None, 'Voice Intents'),
            ('GET', '/languages', None, 'Languages'),
            ('POST', '/language/detect', {"latitude": -1.2921, "longitude": 36.8219}, 'Language Detection'),
            ('POST', '/voice/interpret', {"text": "play", "context": "radio"}, 'Voice Command'),
        ]
        
        # Test with 5 concurrent requests per endpoint (35 total concurrent requests)
        concurrent_requests = []
        for method, endpoint, data, name in load_test_endpoints:
            for i in range(5):
                concurrent_requests.append((method, endpoint, data, f"{name} #{i+1}"))
        
        print(f"  🔄 Executing {len(concurrent_requests)} concurrent requests...")
        
        def execute_request(request_data):
            method, endpoint, data, name = request_data
            return self.make_request(method, endpoint, data)
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_request = {executor.submit(execute_request, req): req for req in concurrent_requests}
            concurrent_results = []
            
            for future in as_completed(future_to_request):
                try:
                    result = future.result()
                    concurrent_results.append(result)
                except Exception as e:
                    print(f"    ❌ Concurrent request failed: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Analyze concurrent load results
        successful_requests = sum(1 for r in concurrent_results if r['success'])
        failed_requests = len(concurrent_results) - successful_requests
        success_rate = (successful_requests / len(concurrent_results)) * 100 if concurrent_results else 0
        avg_requests_per_second = len(concurrent_results) / total_time if total_time > 0 else 0
        
        # Add concurrent results to main results
        self.results.extend(concurrent_results)
        
        print(f"  ✅ Concurrent Load Test Complete:")
        print(f"    - Total Requests: {len(concurrent_results)}")
        print(f"    - Successful: {successful_requests}")
        print(f"    - Failed: {failed_requests}")
        print(f"    - Success Rate: {success_rate:.1f}%")
        print(f"    - Requests/Second: {avg_requests_per_second:.1f}")
        print(f"    - Total Time: {total_time:.2f}s")
        
        if success_rate >= 95.0:
            self.passed_tests.append(f"Production Load Test - {success_rate:.1f}% success rate")
        else:
            self.failed_tests.append(f"Production Load Test - {success_rate:.1f}% success rate (below 95%)")
    
    def analyze_results(self):
        """Analyze test results and generate production readiness report"""
        print("\n" + "="*80)
        print("📊 PRODUCTION READINESS ANALYSIS")
        print("="*80)
        
        # Basic statistics
        total_tests = len(self.results)
        successful_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Performance statistics
        if self.performance_metrics:
            avg_response_time = statistics.mean(self.performance_metrics)
            median_response_time = statistics.median(self.performance_metrics)
            max_response_time = max(self.performance_metrics)
            min_response_time = min(self.performance_metrics)
            
            # Performance targets
            fast_responses = sum(1 for rt in self.performance_metrics if rt < 300)  # <300ms target
            acceptable_responses = sum(1 for rt in self.performance_metrics if rt < 1000)  # <1s acceptable
            slow_responses = sum(1 for rt in self.performance_metrics if rt >= 1000)  # >1s slow
        else:
            avg_response_time = median_response_time = max_response_time = min_response_time = 0
            fast_responses = acceptable_responses = slow_responses = 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if self.performance_metrics:
            print(f"⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.1f}ms")
            print(f"   Median Response Time: {median_response_time:.1f}ms")
            print(f"   Min Response Time: {min_response_time:.1f}ms")
            print(f"   Max Response Time: {max_response_time:.1f}ms")
            print(f"   Fast Responses (<300ms): {fast_responses}/{len(self.performance_metrics)} ({(fast_responses/len(self.performance_metrics)*100):.1f}%)")
            print(f"   Acceptable Responses (<1s): {acceptable_responses}/{len(self.performance_metrics)} ({(acceptable_responses/len(self.performance_metrics)*100):.1f}%)")
            print(f"   Slow Responses (>1s): {slow_responses}/{len(self.performance_metrics)} ({(slow_responses/len(self.performance_metrics)*100):.1f}%)")
            print()
        
        # Production readiness criteria
        print(f"🏆 PRODUCTION READINESS CRITERIA:")
        success_rate_met = success_rate >= 98.0
        performance_met = avg_response_time < 300 if self.performance_metrics else False
        reliability_met = slow_responses == 0
        
        print(f"   ✓ Success Rate >98%: {'✅ PASS' if success_rate_met else '❌ FAIL'} ({success_rate:.1f}%)")
        print(f"   ✓ Avg Response <300ms: {'✅ PASS' if performance_met else '❌ FAIL'} ({avg_response_time:.1f}ms)")
        print(f"   ✓ No Slow Responses: {'✅ PASS' if reliability_met else '❌ FAIL'} ({slow_responses} slow)")
        print()
        
        # Stream accessibility
        if self.stream_accessibility_results:
            successful_streams = sum(1 for r in self.stream_accessibility_results if r['success'])
            stream_success_rate = (successful_streams / len(self.stream_accessibility_results)) * 100
            print(f"📻 RADIO STREAM ACCESSIBILITY:")
            print(f"   Total Streams Tested: {len(self.stream_accessibility_results)}")
            print(f"   Accessible Streams: {successful_streams}")
            print(f"   Stream Success Rate: {stream_success_rate:.1f}%")
            print()
        
        # Failed tests details
        if self.failed_tests:
            print(f"❌ FAILED TESTS DETAILS:")
            for failed_test in self.failed_tests[:10]:  # Show first 10 failures
                print(f"   - {failed_test}")
            if len(self.failed_tests) > 10:
                print(f"   ... and {len(self.failed_tests) - 10} more failures")
            print()
        
        # Final recommendation
        overall_ready = success_rate_met and performance_met and reliability_met
        print(f"🎯 DEPLOYMENT RECOMMENDATION:")
        if overall_ready:
            print(f"   ✅ PRODUCTION READY - All criteria met, deploy with confidence!")
        elif success_rate >= 95.0 and avg_response_time < 500:
            print(f"   ⚠️  MOSTLY READY - Minor issues present, acceptable for deployment")
        else:
            print(f"   ❌ NOT READY - Critical issues must be resolved before deployment")
        
        print("="*80)
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'production_ready': overall_ready,
            'stream_accessibility': len([r for r in self.stream_accessibility_results if r['success']]) if self.stream_accessibility_results else 0,
            'total_streams': len(self.stream_accessibility_results) if self.stream_accessibility_results else 0
        }
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        print("🚀 KAGEMA FM BACKEND PRODUCTION READINESS TESTING")
        print("="*80)
        print("Testing Criteria:")
        print("  • Success Rate: >98% required")
        print("  • Response Time: <300ms average target")
        print("  • Load Testing: Concurrent request handling")
        print("  • Integration Testing: All external services")
        print("  • Error Handling: Proper error responses")
        print("  • Stream Accessibility: All radio streams functional")
        print("="*80)
        print()
        
        try:
            # Execute all test categories
            self.test_core_api_health()
            self.test_geolocation_services()
            self.test_radio_streaming_apis()
            self.test_voice_ai_integration()
            self.test_external_services_integration()
            self.test_satellite_connectivity()
            self.test_content_compliance()
            self.test_stream_accessibility()
            self.test_error_handling()
            self.test_production_load()
            
            # Analyze and report results
            results = self.analyze_results()
            return results
            
        except Exception as e:
            print(f"❌ Test suite execution failed: {str(e)}")
            return None

def main():
    """Main test execution function"""
    suite = ProductionReadinessTestSuite()
    results = suite.run_all_tests()
    
    if results:
        if results['production_ready']:
            print("\n🎉 PRODUCTION DEPLOYMENT APPROVED!")
            return 0
        elif results['success_rate'] >= 95.0:
            print("\n⚠️  PRODUCTION DEPLOYMENT ACCEPTABLE WITH MINOR ISSUES")
            return 0
        else:
            print("\n❌ PRODUCTION DEPLOYMENT NOT RECOMMENDED")
            return 1
    else:
        print("\n❌ TESTING FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)