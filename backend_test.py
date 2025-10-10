#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Kagema FM Preventive Actions
Testing all implemented preventive measures as per review request
"""

import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, List, Any
from datetime import datetime

# Test configuration
BACKEND_URL = "https://carmedia-hub-1.preview.emergentagent.com/api"
TEST_RESULTS = []

class PreventiveActionTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, category: str, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "category": category,
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} [{category}] {test_name}: {details}")
    
    async def test_browser_extension_blocking(self):
        """Test Category 1: Browser Extension Conflict Prevention"""
        print("\n🔒 TESTING BROWSER EXTENSION CONFLICT PREVENTION")
        
        # Test 1: Block chrome-extension origins
        extension_origins = [
            "chrome-extension://abcdefghijklmnop",
            "moz-extension://12345678-1234-1234-1234-123456789abc",
            "safari-extension://com.example.extension",
            "ms-browser-extension://extension-id"
        ]
        
        for origin in extension_origins:
            start_time = time.time()
            try:
                headers = {"Origin": origin}
                async with self.session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = time.time() - start_time
                    if response.status == 403:
                        data = await response.json()
                        if "Browser extension requests are not allowed" in data.get("error", ""):
                            self.log_test("Extension Blocking", f"Block {origin.split('://')[0]}", True, 
                                        f"Correctly blocked with 403, response time: {response_time:.3f}s", response_time)
                        else:
                            self.log_test("Extension Blocking", f"Block {origin.split('://')[0]}", False, 
                                        f"Wrong error message: {data.get('error', '')}", response_time)
                    else:
                        self.log_test("Extension Blocking", f"Block {origin.split('://')[0]}", False, 
                                    f"Expected 403, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Extension Blocking", f"Block {origin.split('://')[0]}", False, f"Exception: {str(e)}")
        
        # Test 2: Block suspicious user agents
        suspicious_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome Extension Helper",
            "Firefox Addon Manager/1.0",
            "Safari Plugin Loader/1.0",
            "Chrome Extension Bot/2.0"
        ]
        
        for agent in suspicious_agents:
            start_time = time.time()
            try:
                headers = {"User-Agent": agent}
                async with self.session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = time.time() - start_time
                    if response.status == 403:
                        data = await response.json()
                        if "Suspicious request detected" in data.get("error", ""):
                            self.log_test("Suspicious User Agents", f"Block suspicious agent", True, 
                                        f"Correctly blocked suspicious user agent, response time: {response_time:.3f}s", response_time)
                        else:
                            self.log_test("Suspicious User Agents", f"Block suspicious agent", False, 
                                        f"Wrong error message: {data.get('error', '')}", response_time)
                    else:
                        self.log_test("Suspicious User Agents", f"Block suspicious agent", False, 
                                    f"Expected 403, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Suspicious User Agents", f"Block suspicious agent", False, f"Exception: {str(e)}")
        
        # Test 3: Block unauthorized origins
        malicious_origins = [
            "https://fake-kagema.com",
            "https://malicious-site.com",
            "https://phishing-kagema.net",
            "https://evil-radio.com"
        ]
        
        for origin in malicious_origins:
            start_time = time.time()
            try:
                headers = {"Origin": origin}
                async with self.session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = time.time() - start_time
                    if response.status == 403:
                        data = await response.json()
                        if "Unauthorized origin" in data.get("error", ""):
                            self.log_test("Unauthorized Origins", f"Block {origin}", True, 
                                        f"Correctly blocked unauthorized origin, response time: {response_time:.3f}s", response_time)
                        else:
                            self.log_test("Unauthorized Origins", f"Block {origin}", False, 
                                        f"Wrong error message: {data.get('error', '')}", response_time)
                    else:
                        self.log_test("Unauthorized Origins", f"Block {origin}", False, 
                                    f"Expected 403, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Unauthorized Origins", f"Block {origin}", False, f"Exception: {str(e)}")
        
        # Test 4: Verify security headers on blocked requests
        start_time = time.time()
        try:
            headers = {"Origin": "chrome-extension://test"}
            async with self.session.get(f"{BACKEND_URL}/", headers=headers) as response:
                response_time = time.time() - start_time
                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options", 
                    "X-XSS-Protection",
                    "Referrer-Policy"
                ]
                missing_headers = []
                for header in security_headers:
                    if header not in response.headers:
                        missing_headers.append(header)
                
                if not missing_headers:
                    self.log_test("Security Headers", "Security headers on blocked requests", True, 
                                f"All security headers present, response time: {response_time:.3f}s", response_time)
                else:
                    self.log_test("Security Headers", "Security headers on blocked requests", False, 
                                f"Missing headers: {missing_headers}", response_time)
        except Exception as e:
            self.log_test("Security Headers", "Security headers on blocked requests", False, f"Exception: {str(e)}")
        
        # Test 5: Verify legitimate access works
        legitimate_origins = [
            "https://carmedia-hub-1.preview.emergentagent.com",
            "http://localhost:3000"
        ]
        
        for origin in legitimate_origins:
            start_time = time.time()
            try:
                headers = {"Origin": origin}
                async with self.session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        self.log_test("Legitimate Access", f"Allow {origin}", True, 
                                    f"Legitimate origin allowed, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Legitimate Access", f"Allow {origin}", False, 
                                    f"Expected 200, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Legitimate Access", f"Allow {origin}", False, f"Exception: {str(e)}")
    
    async def test_security_vulnerability_prevention(self):
        """Test Category 2: Security Vulnerability Prevention"""
        print("\n🛡️ TESTING SECURITY VULNERABILITY PREVENTION")
        
        # Test 1: CORS hardening
        start_time = time.time()
        try:
            headers = {"Origin": "https://evil-site.com"}
            async with self.session.options(f"{BACKEND_URL}/", headers=headers) as response:
                response_time = time.time() - start_time
                if response.status == 403:
                    self.log_test("CORS Hardening", "Block unauthorized CORS", True, 
                                f"CORS properly blocked unauthorized origin, response time: {response_time:.3f}s", response_time)
                else:
                    self.log_test("CORS Hardening", "Block unauthorized CORS", False, 
                                f"Expected 403, got {response.status}", response_time)
        except Exception as e:
            self.log_test("CORS Hardening", "Block unauthorized CORS", False, f"Exception: {str(e)}")
        
        # Test 2: Input validation - malformed requests
        malformed_requests = [
            {"endpoint": "/language/detect", "data": {"invalid": "data"}},
            {"endpoint": "/personalized-content/multilingual", "data": {"malformed": True}},
            {"endpoint": "/compliance/disclaimers", "data": {"country_code": "INVALID_CODE"}}
        ]
        
        for req in malformed_requests:
            start_time = time.time()
            try:
                async with self.session.post(f"{BACKEND_URL}{req['endpoint']}", 
                                           json=req['data']) as response:
                    response_time = time.time() - start_time
                    if response.status == 422:
                        self.log_test("Input Validation", f"Reject malformed {req['endpoint']}", True, 
                                    f"Correctly returned 422 validation error, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Input Validation", f"Reject malformed {req['endpoint']}", False, 
                                    f"Expected 422, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Input Validation", f"Reject malformed {req['endpoint']}", False, f"Exception: {str(e)}")
        
        # Test 3: Security headers on all responses
        test_endpoints = ["/", "/station-info", "/languages"]
        
        for endpoint in test_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    security_headers = [
                        "X-Content-Type-Options",
                        "X-Frame-Options",
                        "X-XSS-Protection", 
                        "Referrer-Policy"
                    ]
                    missing_headers = []
                    for header in security_headers:
                        if header not in response.headers:
                            missing_headers.append(header)
                    
                    if not missing_headers:
                        self.log_test("Security Headers", f"Headers on {endpoint}", True, 
                                    f"All security headers present, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Security Headers", f"Headers on {endpoint}", False, 
                                    f"Missing headers: {missing_headers}", response_time)
            except Exception as e:
                self.log_test("Security Headers", f"Headers on {endpoint}", False, f"Exception: {str(e)}")
        
        # Test 4: Request authentication middleware
        start_time = time.time()
        try:
            # Test with no origin header (should still work for API calls)
            async with self.session.get(f"{BACKEND_URL}/") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    self.log_test("Request Authentication", "No origin header", True, 
                                f"API accessible without origin header, response time: {response_time:.3f}s", response_time)
                else:
                    self.log_test("Request Authentication", "No origin header", False, 
                                f"Expected 200, got {response.status}", response_time)
        except Exception as e:
            self.log_test("Request Authentication", "No origin header", False, f"Exception: {str(e)}")
    
    async def test_performance_issue_prevention(self):
        """Test Category 3: Performance Issue Prevention"""
        print("\n⚡ TESTING PERFORMANCE ISSUE PREVENTION")
        
        # Test 1: Response time optimization - all endpoints under 500ms
        critical_endpoints = [
            "/",
            "/station-info", 
            "/languages",
            "/radio/streams",
            "/radio/stations"
        ]
        
        for endpoint in critical_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    if response_time < 0.5:  # Under 500ms
                        self.log_test("Response Time", f"{endpoint} performance", True, 
                                    f"Response time {response_time:.3f}s (under 500ms target)", response_time)
                    else:
                        self.log_test("Response Time", f"{endpoint} performance", False, 
                                    f"Response time {response_time:.3f}s (over 500ms target)", response_time)
            except Exception as e:
                self.log_test("Response Time", f"{endpoint} performance", False, f"Exception: {str(e)}")
        
        # Test 2: Cache effectiveness - check cache headers
        cacheable_endpoints = ["/languages", "/radio/streams", "/radio/stations", "/app/info", "/app/version"]
        
        for endpoint in cacheable_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    cache_headers = ["Cache-Control", "ETag", "Last-Modified"]
                    present_headers = [h for h in cache_headers if h in response.headers]
                    
                    if len(present_headers) >= 1:  # At least one cache header
                        self.log_test("Cache Headers", f"{endpoint} caching", True, 
                                    f"Cache headers present: {present_headers}, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Cache Headers", f"{endpoint} caching", False, 
                                    f"No cache headers found", response_time)
            except Exception as e:
                self.log_test("Cache Headers", f"{endpoint} caching", False, f"Exception: {str(e)}")
        
        # Test 3: Resource efficiency - concurrent requests
        start_time = time.time()
        try:
            tasks = []
            for i in range(10):  # 10 concurrent requests
                task = self.session.get(f"{BACKEND_URL}/")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            response_time = time.time() - start_time
            
            success_count = sum(1 for r in responses if r.status == 200)
            if success_count == 10:
                self.log_test("Resource Efficiency", "Concurrent requests", True, 
                            f"All 10 concurrent requests successful, total time: {response_time:.3f}s", response_time)
            else:
                self.log_test("Resource Efficiency", "Concurrent requests", False, 
                            f"Only {success_count}/10 requests successful", response_time)
            
            # Close all responses
            for r in responses:
                r.close()
                
        except Exception as e:
            self.log_test("Resource Efficiency", "Concurrent requests", False, f"Exception: {str(e)}")
        
        # Test 4: Error recovery - graceful error handling
        error_endpoints = [
            "/nonexistent-endpoint",
            "/station-info/invalid",
            "/user/invalid-id/preferences"
        ]
        
        for endpoint in error_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    if response.status in [404, 422, 500]:  # Expected error codes
                        try:
                            error_data = await response.json()
                            if "error" in error_data or "detail" in error_data:
                                self.log_test("Error Recovery", f"Graceful error {endpoint}", True, 
                                            f"Proper error response with status {response.status}, response time: {response_time:.3f}s", response_time)
                            else:
                                self.log_test("Error Recovery", f"Graceful error {endpoint}", False, 
                                            f"Error response missing error details", response_time)
                        except:
                            self.log_test("Error Recovery", f"Graceful error {endpoint}", False, 
                                        f"Error response not JSON", response_time)
                    else:
                        self.log_test("Error Recovery", f"Graceful error {endpoint}", False, 
                                    f"Unexpected status code: {response.status}", response_time)
            except Exception as e:
                self.log_test("Error Recovery", f"Graceful error {endpoint}", False, f"Exception: {str(e)}")
    
    async def test_network_resilience_prevention(self):
        """Test Category 4: Network Resilience Prevention"""
        print("\n🌐 TESTING NETWORK RESILIENCE PREVENTION")
        
        # Test 1: Endpoint health - all critical endpoints responsive
        critical_endpoints = [
            "/",
            "/station-info",
            "/languages", 
            "/radio/streams",
            "/radio/stations",
            "/app/info",
            "/app/version"
        ]
        
        for endpoint in critical_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        self.log_test("Endpoint Health", f"{endpoint} availability", True, 
                                    f"Endpoint responsive, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Endpoint Health", f"{endpoint} availability", False, 
                                    f"Expected 200, got {response.status}", response_time)
            except Exception as e:
                self.log_test("Endpoint Health", f"{endpoint} availability", False, f"Exception: {str(e)}")
        
        # Test 2: Connection stability - multiple requests to same endpoint
        start_time = time.time()
        try:
            response_times = []
            for i in range(5):
                req_start = time.time()
                async with self.session.get(f"{BACKEND_URL}/") as response:
                    req_time = time.time() - req_start
                    response_times.append(req_time)
                    if response.status != 200:
                        raise Exception(f"Request {i+1} failed with status {response.status}")
            
            total_time = time.time() - start_time
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Check for consistency (max time shouldn't be more than 3x min time)
            if max_time <= min_time * 3:
                self.log_test("Connection Stability", "Response time consistency", True, 
                            f"Consistent response times: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s", avg_time)
            else:
                self.log_test("Connection Stability", "Response time consistency", False, 
                            f"Inconsistent response times: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s", avg_time)
                
        except Exception as e:
            self.log_test("Connection Stability", "Response time consistency", False, f"Exception: {str(e)}")
        
        # Test 3: Fallback mechanisms - test with various request scenarios
        fallback_tests = [
            {"name": "Invalid location fallback", "endpoint": "/language/detect", 
             "data": {"latitude": 999, "longitude": 999}},
            {"name": "Missing data fallback", "endpoint": "/personalized-content/multilingual", 
             "data": {"location": {"latitude": 0, "longitude": 0}}}
        ]
        
        for test in fallback_tests:
            start_time = time.time()
            try:
                async with self.session.post(f"{BACKEND_URL}{test['endpoint']}", 
                                           json=test['data']) as response:
                    response_time = time.time() - start_time
                    if response.status in [200, 422]:  # Either success with fallback or validation error
                        if response.status == 200:
                            data = await response.json()
                            if "detected_language" in data:  # Has fallback data
                                self.log_test("Fallback Mechanisms", test['name'], True, 
                                            f"Fallback data provided, response time: {response_time:.3f}s", response_time)
                            else:
                                self.log_test("Fallback Mechanisms", test['name'], False, 
                                            f"No fallback data in response", response_time)
                        else:  # 422 - proper validation
                            self.log_test("Fallback Mechanisms", test['name'], True, 
                                        f"Proper validation error, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Fallback Mechanisms", test['name'], False, 
                                    f"Unexpected status: {response.status}", response_time)
            except Exception as e:
                self.log_test("Fallback Mechanisms", test['name'], False, f"Exception: {str(e)}")
        
        # Test 4: Service availability - high availability metrics
        start_time = time.time()
        try:
            # Test multiple endpoints rapidly
            endpoints = ["/", "/station-info", "/languages", "/radio/streams"]
            total_requests = 0
            successful_requests = 0
            
            for endpoint in endpoints:
                for i in range(3):  # 3 requests per endpoint
                    total_requests += 1
                    try:
                        async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                            if response.status == 200:
                                successful_requests += 1
                    except:
                        pass  # Count as failure
            
            availability = (successful_requests / total_requests) * 100
            response_time = time.time() - start_time
            
            if availability >= 95:  # 95% availability target
                self.log_test("Service Availability", "High availability", True, 
                            f"Availability: {availability:.1f}% ({successful_requests}/{total_requests}), response time: {response_time:.3f}s", response_time)
            else:
                self.log_test("Service Availability", "High availability", False, 
                            f"Availability: {availability:.1f}% (below 95% target)", response_time)
                
        except Exception as e:
            self.log_test("Service Availability", "High availability", False, f"Exception: {str(e)}")
    
    async def test_automated_monitoring_validation(self):
        """Test Category 5: Automated Monitoring Validation"""
        print("\n📊 TESTING AUTOMATED MONITORING VALIDATION")
        
        # Test 1: Real-time detection - API health monitoring
        start_time = time.time()
        try:
            # Test app info endpoint for monitoring data
            async with self.session.get(f"{BACKEND_URL}/app/info") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if "status" in data and data["status"] == "active":
                        self.log_test("Real-time Detection", "API health monitoring", True, 
                                    f"API health status active, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Real-time Detection", "API health monitoring", False, 
                                    f"API status not active: {data.get('status', 'unknown')}", response_time)
                else:
                    self.log_test("Real-time Detection", "API health monitoring", False, 
                                f"Expected 200, got {response.status}", response_time)
        except Exception as e:
            self.log_test("Real-time Detection", "API health monitoring", False, f"Exception: {str(e)}")
        
        # Test 2: Alert system - version monitoring
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/app/version") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["version", "build", "update_available"]
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if not missing_fields:
                        self.log_test("Alert System", "Version monitoring", True, 
                                    f"Version monitoring data complete, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Alert System", "Version monitoring", False, 
                                    f"Missing monitoring fields: {missing_fields}", response_time)
                else:
                    self.log_test("Alert System", "Version monitoring", False, 
                                f"Expected 200, got {response.status}", response_time)
        except Exception as e:
            self.log_test("Alert System", "Version monitoring", False, f"Exception: {str(e)}")
        
        # Test 3: Metrics collection - external sources monitoring
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/app/version") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if "external_sources" in data:
                        sources = data["external_sources"]
                        if len(sources) >= 3:  # Should have multiple external sources
                            self.log_test("Metrics Collection", "External sources monitoring", True, 
                                        f"External sources tracked: {len(sources)} sources, response time: {response_time:.3f}s", response_time)
                        else:
                            self.log_test("Metrics Collection", "External sources monitoring", False, 
                                        f"Insufficient external sources: {len(sources)}", response_time)
                    else:
                        self.log_test("Metrics Collection", "External sources monitoring", False, 
                                    f"No external sources data", response_time)
                else:
                    self.log_test("Metrics Collection", "External sources monitoring", False, 
                                f"Expected 200, got {response.status}", response_time)
        except Exception as e:
            self.log_test("Metrics Collection", "External sources monitoring", False, f"Exception: {str(e)}")
        
        # Test 4: Preventive actions - satellite connectivity monitoring
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/satellite/status") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["connection_type", "signal_strength", "timestamp"]
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if not missing_fields:
                        self.log_test("Preventive Actions", "Satellite monitoring", True, 
                                    f"Satellite monitoring active, response time: {response_time:.3f}s", response_time)
                    else:
                        self.log_test("Preventive Actions", "Satellite monitoring", False, 
                                    f"Missing satellite fields: {missing_fields}", response_time)
                else:
                    self.log_test("Preventive Actions", "Satellite monitoring", False, 
                                f"Expected 200, got {response.status}", response_time)
        except Exception as e:
            self.log_test("Preventive Actions", "Satellite monitoring", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all preventive action tests"""
        print("🎯 STARTING COMPREHENSIVE KAGEMA FM PREVENTIVE ACTIONS TESTING")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test categories
            await self.test_browser_extension_blocking()
            await self.test_security_vulnerability_prevention()
            await self.test_performance_issue_prevention()
            await self.test_network_resilience_prevention()
            await self.test_automated_monitoring_validation()
            
            # Generate summary
            self.generate_summary()
            
        finally:
            await self.cleanup()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PREVENTIVE ACTIONS TEST SUMMARY")
        print("=" * 80)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0, "avg_response_time": 0}
            
            categories[category]["total"] += 1
            if result["passed"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            if result["response_time"] > 0:
                categories[category]["avg_response_time"] += result["response_time"]
        
        # Calculate averages and print category summaries
        total_passed = 0
        total_tests = 0
        
        for category, stats in categories.items():
            if stats["total"] > 0:
                success_rate = (stats["passed"] / stats["total"]) * 100
                avg_time = stats["avg_response_time"] / stats["total"] if stats["avg_response_time"] > 0 else 0
                
                status = "✅ EXCELLENT" if success_rate >= 95 else "⚠️ NEEDS ATTENTION" if success_rate >= 80 else "❌ CRITICAL"
                
                print(f"\n{status} [{category}]")
                print(f"  Success Rate: {success_rate:.1f}% ({stats['passed']}/{stats['total']} tests passed)")
                if avg_time > 0:
                    print(f"  Average Response Time: {avg_time:.3f}s")
                
                total_passed += stats["passed"]
                total_tests += stats["total"]
        
        # Overall summary
        overall_success = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL PREVENTIVE ACTIONS EFFECTIVENESS")
        print(f"Success Rate: {overall_success:.1f}% ({total_passed}/{total_tests} tests passed)")
        
        if overall_success >= 95:
            print("✅ EXCELLENT: All preventive actions working effectively!")
        elif overall_success >= 80:
            print("⚠️ GOOD: Most preventive actions working, minor issues detected")
        else:
            print("❌ CRITICAL: Significant preventive action failures detected")
        
        # List any failed tests
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • [{test['category']}] {test['test_name']}: {test['details']}")
        
        print("\n" + "=" * 80)
        return overall_success

async def main():
    """Main test execution"""
    tester = PreventiveActionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())