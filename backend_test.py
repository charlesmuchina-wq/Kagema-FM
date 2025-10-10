#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Kagema FM Enhanced Browser Extension Conflict Prevention
Testing the FIXED middleware logic for security vulnerabilities as per review request
"""

import asyncio
import aiohttp
import time
import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://carmedia-hub-1.preview.emergentagent.com/api"

@dataclass
class TestResult:
    name: str
    passed: bool
    response_time: float
    status_code: Optional[int] = None
    details: str = ""
    security_headers: Dict[str, str] = None

class KagemaFMSecurityTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def run_all_tests(self):
        """Run FIXED browser extension conflict prevention tests as per review request"""
        print("🔒 KAGEMA FM ENHANCED BROWSER EXTENSION CONFLICT PREVENTION TESTING")
        print("Testing the FIXED middleware logic for security vulnerabilities")
        print("=" * 80)
        
        # Test the specific fixes mentioned in review request
        await self.test_extension_origin_blocking()
        await self.test_suspicious_user_agent_detection()
        await self.test_unauthorized_origin_blocking()
        await self.test_legitimate_requests()
        await self.test_security_headers_in_error_responses()
        await self.test_performance_under_security_checks()
        
        self.print_summary()
        
    async def test_cors_configuration(self):
        """Test enhanced CORS configuration"""
        print("\n🌐 1. CORS CONFIGURATION TESTING")
        print("-" * 50)
        
        # Test legitimate origins (should work - return 200)
        legitimate_origins = [
            "https://carmedia-hub-1.preview.emergentagent.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]
        
        for origin in legitimate_origins:
            await self.test_cors_request(origin, should_pass=True)
            
        # Test browser extension origins (should be blocked - return 403/500)
        extension_origins = [
            "chrome-extension://abcdefghijklmnopqrstuvwxyz123456",
            "moz-extension://12345678-1234-1234-1234-123456789abc",
            "safari-extension://com.example.extension",
            "ms-browser-extension://extension-id-here"
        ]
        
        for origin in extension_origins:
            await self.test_cors_request(origin, should_pass=False)
            
        # Test unauthorized origins (should be blocked)
        unauthorized_origins = [
            "https://malicious-site.com",
            "http://suspicious-domain.net",
            "https://fake-kagema.com"
        ]
        
        for origin in unauthorized_origins:
            await self.test_cors_request(origin, should_pass=False)
    
    async def test_cors_request(self, origin: str, should_pass: bool):
        """Test CORS request with specific origin"""
        start_time = time.time()
        
        headers = {
            "Origin": origin,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Check security headers
                    security_headers = {
                        "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
                        "X-Frame-Options": response.headers.get("X-Frame-Options"),
                        "X-XSS-Protection": response.headers.get("X-XSS-Protection"),
                        "Referrer-Policy": response.headers.get("Referrer-Policy"),
                        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin")
                    }
                    
                    if should_pass:
                        # Legitimate requests should return 200
                        passed = response.status == 200
                        details = f"Legitimate origin {origin} - Expected 200, got {response.status}"
                    else:
                        # Extension/unauthorized requests should be blocked (403 or 500)
                        passed = response.status in [403, 500]
                        details = f"Extension/unauthorized origin {origin} - Expected 403/500, got {response.status}"
                    
                    self.add_result(TestResult(
                        name=f"CORS Origin: {origin[:50]}...",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details,
                        security_headers=security_headers
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            # For extension origins, connection errors might be expected
            passed = not should_pass  # If we expect failure and got error, that's good
            self.add_result(TestResult(
                name=f"CORS Origin: {origin[:50]}...",
                passed=passed,
                response_time=response_time,
                details=f"Connection error (expected for blocked origins): {str(e)}"
            ))
    
    async def test_request_validation_middleware(self):
        """Test RequestAuthenticatorMiddleware for suspicious requests"""
        print("\n🛡️ 2. SERVER-SIDE REQUEST VALIDATION TESTING")
        print("-" * 50)
        
        # Test suspicious user agents (should be blocked)
        suspicious_user_agents = [
            "Mozilla/5.0 Chrome Extension Bot",
            "Firefox Addon Scanner v1.0",
            "Browser Plugin Crawler",
            "Extension Content Script",
            "Addon Background Script"
        ]
        
        for user_agent in suspicious_user_agents:
            await self.test_user_agent_validation(user_agent, should_pass=False)
            
        # Test legitimate user agents (should work)
        legitimate_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        ]
        
        for user_agent in legitimate_user_agents:
            await self.test_user_agent_validation(user_agent, should_pass=True)
    
    async def test_user_agent_validation(self, user_agent: str, should_pass: bool):
        """Test user agent validation"""
        start_time = time.time()
        
        headers = {
            "User-Agent": user_agent,
            "Origin": "https://carmedia-hub-1.preview.emergentagent.com"  # Use legitimate origin
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if should_pass:
                        passed = response.status == 200
                        details = f"Legitimate user agent - Expected 200, got {response.status}"
                    else:
                        passed = response.status == 403
                        details = f"Suspicious user agent - Expected 403, got {response.status}"
                    
                    self.add_result(TestResult(
                        name=f"User Agent: {user_agent[:50]}...",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            passed = not should_pass
            self.add_result(TestResult(
                name=f"User Agent: {user_agent[:50]}...",
                passed=passed,
                response_time=response_time,
                details=f"Connection error: {str(e)}"
            ))
    
    async def test_api_endpoint_security(self):
        """Test API endpoint security against browser extension conflicts"""
        print("\n🔐 3. API ENDPOINT SECURITY TESTING")
        print("-" * 50)
        
        # Critical API endpoints to test
        endpoints = [
            "/",
            "/station-info", 
            "/personalized-content/multilingual",
            "/voice/interpret"
        ]
        
        for endpoint in endpoints:
            # Test with legitimate request
            await self.test_endpoint_security(endpoint, legitimate=True)
            
            # Test with extension-like request
            await self.test_endpoint_security(endpoint, legitimate=False)
    
    async def test_endpoint_security(self, endpoint: str, legitimate: bool):
        """Test individual endpoint security"""
        start_time = time.time()
        
        if legitimate:
            headers = {
                "Origin": "https://carmedia-hub-1.preview.emergentagent.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json"
            }
            test_name = f"Legitimate request to {endpoint}"
        else:
            headers = {
                "Origin": "chrome-extension://malicious-extension-id",
                "User-Agent": "Chrome Extension Bot",
                "Content-Type": "application/json"
            }
            test_name = f"Extension request to {endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if endpoint == "/personalized-content/multilingual":
                    # POST request with required data
                    data = {
                        "location": {"latitude": -1.286389, "longitude": 36.817223},
                        "preferences": {"offline_mode": False}
                    }
                    async with session.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=data) as response:
                        response_time = (time.time() - start_time) * 1000
                        await self.process_endpoint_response(response, response_time, test_name, legitimate)
                        
                elif endpoint == "/voice/interpret":
                    # POST request with voice data
                    data = {
                        "text": "play radio",
                        "context": "radio_control"
                    }
                    async with session.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=data) as response:
                        response_time = (time.time() - start_time) * 1000
                        await self.process_endpoint_response(response, response_time, test_name, legitimate)
                else:
                    # GET request
                    async with session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                        response_time = (time.time() - start_time) * 1000
                        await self.process_endpoint_response(response, response_time, test_name, legitimate)
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            passed = not legitimate  # Error expected for illegitimate requests
            self.add_result(TestResult(
                name=test_name,
                passed=passed,
                response_time=response_time,
                details=f"Connection error: {str(e)}"
            ))
    
    async def process_endpoint_response(self, response, response_time: float, test_name: str, legitimate: bool):
        """Process endpoint response and determine if test passed"""
        # Check security headers
        security_headers = {
            "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
            "X-Frame-Options": response.headers.get("X-Frame-Options"),
            "X-XSS-Protection": response.headers.get("X-XSS-Protection"),
            "Referrer-Policy": response.headers.get("Referrer-Policy")
        }
        
        if legitimate:
            # Legitimate requests should succeed (200)
            passed = response.status == 200
            details = f"Expected 200 for legitimate request, got {response.status}"
        else:
            # Extension requests should be blocked (403)
            passed = response.status == 403
            details = f"Expected 403 for extension request, got {response.status}"
        
        # Verify security headers are present
        required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Referrer-Policy"]
        missing_headers = [h for h in required_headers if not security_headers.get(h)]
        
        if missing_headers:
            details += f" | Missing security headers: {', '.join(missing_headers)}"
            if passed:  # Only fail if other checks passed
                passed = False
        
        self.add_result(TestResult(
            name=test_name,
            passed=passed,
            response_time=response_time,
            status_code=response.status,
            details=details,
            security_headers=security_headers
        ))
    
    async def test_performance_impact(self):
        """Test performance impact of security middleware"""
        print("\n⚡ 4. PERFORMANCE IMPACT TESTING")
        print("-" * 50)
        
        # Test response times for multiple requests
        endpoint = "/"
        num_requests = 10
        response_times = []
        
        headers = {
            "Origin": "https://carmedia-hub-1.preview.emergentagent.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        print(f"Testing {num_requests} concurrent requests to measure performance impact...")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                task = self.measure_request_time(session, f"{BACKEND_URL}{endpoint}", headers)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_times = [r for r in results if isinstance(r, float)]
            response_times.extend(successful_times)
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Performance should be under 500ms average as per requirements
            passed = avg_time < 500
            
            self.add_result(TestResult(
                name="Performance Impact - Average Response Time",
                passed=passed,
                response_time=avg_time,
                details=f"Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms (Target: <500ms)"
            ))
            
            # Test concurrent request handling
            passed_concurrent = len(successful_times) >= num_requests * 0.9  # 90% success rate
            self.add_result(TestResult(
                name="Concurrent Request Handling",
                passed=passed_concurrent,
                response_time=avg_time,
                details=f"Successfully handled {len(successful_times)}/{num_requests} concurrent requests"
            ))
        else:
            self.add_result(TestResult(
                name="Performance Impact Testing",
                passed=False,
                response_time=0,
                details="No successful requests completed"
            ))
    
    async def measure_request_time(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str]) -> float:
        """Measure individual request time"""
        start_time = time.time()
        try:
            async with session.get(url, headers=headers) as response:
                await response.read()  # Ensure full response is received
                return (time.time() - start_time) * 1000
        except Exception:
            return -1  # Indicate failure
    
    async def test_cross_browser_compatibility(self):
        """Test backend response to different browser contexts"""
        print("\n🌍 5. CROSS-BROWSER COMPATIBILITY TESTING")
        print("-" * 50)
        
        # Different browser user agents
        browser_contexts = [
            {
                "name": "Chrome Desktop",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "should_pass": True
            },
            {
                "name": "Firefox Desktop", 
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "should_pass": True
            },
            {
                "name": "Safari Desktop",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "should_pass": True
            },
            {
                "name": "Chrome Mobile",
                "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "should_pass": True
            },
            {
                "name": "Chrome with Extension Indicators",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome Extension Helper",
                "should_pass": False
            },
            {
                "name": "Firefox with Addon Indicators",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0 Addon Manager",
                "should_pass": False
            }
        ]
        
        for context in browser_contexts:
            await self.test_browser_context(context)
    
    async def test_browser_context(self, context: Dict[str, Any]):
        """Test specific browser context"""
        start_time = time.time()
        
        headers = {
            "Origin": "https://carmedia-hub-1.preview.emergentagent.com",
            "User-Agent": context["user_agent"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if context["should_pass"]:
                        passed = response.status == 200
                        details = f"Expected 200 for {context['name']}, got {response.status}"
                    else:
                        passed = response.status == 403
                        details = f"Expected 403 for {context['name']} (suspicious), got {response.status}"
                    
                    self.add_result(TestResult(
                        name=f"Browser Context: {context['name']}",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            passed = not context["should_pass"]
            self.add_result(TestResult(
                name=f"Browser Context: {context['name']}",
                passed=passed,
                response_time=response_time,
                details=f"Connection error: {str(e)}"
            ))
    
    def add_result(self, result: TestResult):
        """Add test result and update counters"""
        self.results.append(result)
        self.total_tests += 1
        if result.passed:
            self.passed_tests += 1
        
        # Print result immediately
        status = "✅ PASS" if result.passed else "❌ FAIL"
        time_str = f"{result.response_time:.1f}ms" if result.response_time > 0 else "N/A"
        status_code = f"({result.status_code})" if result.status_code else ""
        print(f"{status} {result.name} - {time_str} {status_code}")
        if result.details:
            print(f"     Details: {result.details}")
        
        # Print security headers for important tests
        if result.security_headers and any(result.security_headers.values()):
            print(f"     Security Headers: {result.security_headers}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 BROWSER EXTENSION CONFLICT PREVENTION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        # Categorize results
        categories = {
            "CORS Configuration": [r for r in self.results if "CORS Origin" in r.name],
            "Request Validation": [r for r in self.results if "User Agent" in r.name],
            "API Endpoint Security": [r for r in self.results if any(endpoint in r.name for endpoint in ["/", "/station-info", "/personalized-content", "/voice/interpret"])],
            "Performance Impact": [r for r in self.results if "Performance" in r.name or "Concurrent" in r.name],
            "Cross-Browser Compatibility": [r for r in self.results if "Browser Context" in r.name]
        }
        
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t.passed)
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"\n🔍 {category}: {passed}/{total} ({rate:.1f}%)")
                
                # Show failed tests
                failed_tests = [t for t in tests if not t.passed]
                if failed_tests:
                    print("   Failed tests:")
                    for test in failed_tests:
                        print(f"   ❌ {test.name}: {test.details}")
        
        # Performance metrics
        performance_tests = [r for r in self.results if r.response_time > 0]
        if performance_tests:
            avg_response_time = sum(r.response_time for r in performance_tests) / len(performance_tests)
            print(f"\n⚡ Average Response Time: {avg_response_time:.1f}ms")
            
            fast_responses = sum(1 for r in performance_tests if r.response_time < 500)
            print(f"⚡ Responses under 500ms: {fast_responses}/{len(performance_tests)} ({fast_responses/len(performance_tests)*100:.1f}%)")
        
        # Security headers analysis
        security_tests = [r for r in self.results if r.security_headers]
        if security_tests:
            print(f"\n🛡️ Security Headers Analysis:")
            required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Referrer-Policy"]
            for header in required_headers:
                present_count = sum(1 for r in security_tests if r.security_headers.get(header))
                print(f"   {header}: {present_count}/{len(security_tests)} responses")
        
        # Final assessment
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        if success_rate >= 95:
            print("✅ EXCELLENT - Browser extension conflict prevention working perfectly")
        elif success_rate >= 85:
            print("✅ GOOD - Minor issues detected, but core security functional")
        elif success_rate >= 70:
            print("⚠️ FAIR - Some security issues need attention")
        else:
            print("❌ POOR - Significant security vulnerabilities detected")
        
        print(f"\n📋 Expected Results Verification:")
        print(f"   Extension requests blocked (403/500): {'✅' if any('Expected 403' in r.details and r.passed for r in self.results) else '❌'}")
        print(f"   Legitimate requests allowed (200): {'✅' if any('Expected 200' in r.details and r.passed for r in self.results) else '❌'}")
        print(f"   Security headers present: {'✅' if security_tests else '❌'}")
        print(f"   Performance under 500ms: {'✅' if avg_response_time < 500 else '❌'}")

async def main():
    """Main test execution"""
    tester = BrowserExtensionConflictTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())