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

    async def test_extension_origin_blocking(self):
        """Test 1: Extension Origin Blocking - chrome-extension://, moz-extension:// should return 403"""
        print("\n🔒 1. EXTENSION ORIGIN BLOCKING TESTING")
        print("-" * 50)
        
        extension_origins = [
            "chrome-extension://abcdefghijklmnopqrstuvwxyz123456",
            "moz-extension://12345678-1234-1234-1234-123456789abc",
            "safari-extension://com.example.extension",
            "ms-browser-extension://extension-id-here"
        ]
        
        for origin in extension_origins:
            await self.test_extension_origin_request(origin)

    async def test_extension_origin_request(self, origin: str):
        """Test extension origin request - should return 403 with security headers"""
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
                        "Referrer-Policy": response.headers.get("Referrer-Policy")
                    }
                    
                    # Should return 403
                    passed = response.status == 403
                    
                    # Check if all required security headers are present
                    required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Referrer-Policy"]
                    missing_headers = [h for h in required_headers if not security_headers.get(h)]
                    
                    if passed and not missing_headers:
                        details = f"✅ Correctly blocked with 403 and all security headers"
                    elif passed:
                        details = f"⚠️ Blocked with 403 but missing headers: {missing_headers}"
                        passed = False
                    else:
                        details = f"❌ Expected 403, got {response.status}"
                    
                    self.add_result(TestResult(
                        name=f"Extension Origin Block: {origin.split('://')[0]}://",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details,
                        security_headers=security_headers
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.add_result(TestResult(
                name=f"Extension Origin Block: {origin.split('://')[0]}://",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_suspicious_user_agent_detection(self):
        """Test 2: Suspicious User Agent Detection - should block regardless of origin"""
        print("\n🕵️ 2. SUSPICIOUS USER AGENT DETECTION TESTING")
        print("-" * 50)
        
        # Test with legitimate origin but suspicious user agent
        legitimate_origin = "https://carmedia-hub-1.preview.emergentagent.com"
        suspicious_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome Extension Helper",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36 addon-manager",
            "Mozilla/5.0 (X11; Linux x86_64) Firefox/91.0 plugin-container",
            "CustomBot extension/1.0",
            "BrowserAddon/2.1",
            "PluginHelper/1.5"
        ]
        
        for user_agent in suspicious_agents:
            await self.test_suspicious_user_agent_request(legitimate_origin, user_agent)

    async def test_suspicious_user_agent_request(self, origin: str, user_agent: str):
        """Test suspicious user agent request - should return 403 even with legitimate origin"""
        start_time = time.time()
        
        headers = {
            "Origin": origin,
            "User-Agent": user_agent
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
                        "Referrer-Policy": response.headers.get("Referrer-Policy")
                    }
                    
                    # Should return 403 even with legitimate origin
                    passed = response.status == 403
                    
                    # Check if all required security headers are present
                    required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Referrer-Policy"]
                    missing_headers = [h for h in required_headers if not security_headers.get(h)]
                    
                    if passed and not missing_headers:
                        details = f"✅ Correctly blocked with 403 and all security headers"
                    elif passed:
                        details = f"⚠️ Blocked with 403 but missing headers: {missing_headers}"
                        passed = False
                    else:
                        details = f"❌ Expected 403, got {response.status}"
                    
                    # Extract key part of user agent for display
                    agent_key = "extension" if "extension" in user_agent.lower() else "addon" if "addon" in user_agent.lower() else "plugin" if "plugin" in user_agent.lower() else user_agent.split()[-1]
                    
                    self.add_result(TestResult(
                        name=f"Suspicious User Agent: {agent_key}",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details,
                        security_headers=security_headers
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            agent_key = user_agent.split()[-1] if user_agent else "unknown"
            self.add_result(TestResult(
                name=f"Suspicious User Agent: {agent_key}",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_unauthorized_origin_blocking(self):
        """Test 3: Unauthorized Origin Blocking - malicious origins should return 403"""
        print("\n🚫 3. UNAUTHORIZED ORIGIN BLOCKING TESTING")
        print("-" * 50)
        
        malicious_origins = [
            "https://malicious-site.com",
            "https://fake-kagema.com",
            "https://evil-radio.net",
            "https://phishing-kagema.org",
            "http://localhost:8080",  # Not in whitelist
            "https://unauthorized-domain.com"
        ]
        
        for origin in malicious_origins:
            await self.test_unauthorized_origin_request(origin)

    async def test_unauthorized_origin_request(self, origin: str):
        """Test unauthorized origin request - should return 403"""
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
                        "Referrer-Policy": response.headers.get("Referrer-Policy")
                    }
                    
                    # Should return 403
                    passed = response.status == 403
                    
                    # Check if all required security headers are present
                    required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Referrer-Policy"]
                    missing_headers = [h for h in required_headers if not security_headers.get(h)]
                    
                    if passed and not missing_headers:
                        details = f"✅ Correctly blocked with 403 and all security headers"
                    elif passed:
                        details = f"⚠️ Blocked with 403 but missing headers: {missing_headers}"
                        passed = False
                    else:
                        details = f"❌ Expected 403, got {response.status}"
                    
                    self.add_result(TestResult(
                        name=f"Unauthorized Origin: {origin}",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details,
                        security_headers=security_headers
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.add_result(TestResult(
                name=f"Unauthorized Origin: {origin}",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_legitimate_requests(self):
        """Test 4: Legitimate Requests - whitelisted origins should work normally (200)"""
        print("\n✅ 4. LEGITIMATE REQUESTS TESTING")
        print("-" * 50)
        
        legitimate_origins = [
            "https://carmedia-hub-1.preview.emergentagent.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:19006"  # Expo dev
        ]
        
        # Test basic endpoints
        test_endpoints = [
            "/",
            "/station-info",
            "/languages"
        ]
        
        for origin in legitimate_origins:
            for endpoint in test_endpoints:
                await self.test_legitimate_request(origin, endpoint)

    async def test_legitimate_request(self, origin: str, endpoint: str):
        """Test legitimate request - should return 200"""
        start_time = time.time()
        
        headers = {
            "Origin": origin,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Check that security headers are still present
                    security_headers = {
                        "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
                        "X-Frame-Options": response.headers.get("X-Frame-Options"),
                        "X-XSS-Protection": response.headers.get("X-XSS-Protection"),
                        "Referrer-Policy": response.headers.get("Referrer-Policy")
                    }
                    
                    # Should return 200
                    passed = response.status == 200
                    
                    present_headers = [h for h in security_headers.keys() if security_headers.get(h)]
                    
                    if passed:
                        details = f"✅ Success with {len(present_headers)}/4 security headers"
                    else:
                        details = f"❌ Expected 200, got {response.status}"
                    
                    # Extract domain for display
                    domain = origin.split('//')[1].split('.')[0] if '//' in origin else origin
                    
                    self.add_result(TestResult(
                        name=f"Legitimate Request: {domain} {endpoint}",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details,
                        security_headers=security_headers
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            domain = origin.split('//')[1].split('.')[0] if '//' in origin else origin
            self.add_result(TestResult(
                name=f"Legitimate Request: {domain} {endpoint}",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_security_headers_in_error_responses(self):
        """Test 5: Security Headers - All error responses should include security headers"""
        print("\n🛡️ 5. SECURITY HEADERS IN ERROR RESPONSES TESTING")
        print("-" * 50)
        
        # Test various error scenarios
        test_cases = [
            {
                "name": "Extension Origin",
                "headers": {
                    "Origin": "chrome-extension://test",
                    "User-Agent": "Mozilla/5.0"
                }
            },
            {
                "name": "Suspicious User Agent",
                "headers": {
                    "Origin": "https://carmedia-hub-1.preview.emergentagent.com",
                    "User-Agent": "BrowserExtension/1.0"
                }
            },
            {
                "name": "Malicious Origin",
                "headers": {
                    "Origin": "https://evil-site.com",
                    "User-Agent": "Mozilla/5.0"
                }
            }
        ]
        
        required_security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        for test_case in test_cases:
            await self.test_security_headers_case(test_case, required_security_headers)

    async def test_security_headers_case(self, test_case: dict, required_security_headers: dict):
        """Test security headers for specific case"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=test_case["headers"]) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 403:
                        # Check all required security headers
                        missing_headers = []
                        incorrect_values = []
                        
                        for header, expected_value in required_security_headers.items():
                            if header not in response.headers:
                                missing_headers.append(header)
                            elif response.headers[header] != expected_value:
                                incorrect_values.append(f"{header}: got '{response.headers[header]}', expected '{expected_value}'")
                        
                        if not missing_headers and not incorrect_values:
                            passed = True
                            details = f"✅ All security headers present with correct values"
                        else:
                            passed = False
                            issues = []
                            if missing_headers:
                                issues.append(f"Missing: {missing_headers}")
                            if incorrect_values:
                                issues.append(f"Incorrect: {incorrect_values}")
                            details = f"❌ Header issues: {'; '.join(issues)}"
                        
                        self.add_result(TestResult(
                            name=f"Security Headers: {test_case['name']}",
                            passed=passed,
                            response_time=response_time,
                            status_code=response.status,
                            details=details
                        ))
                    else:
                        self.add_result(TestResult(
                            name=f"Security Headers: {test_case['name']}",
                            passed=False,
                            response_time=response_time,
                            status_code=response.status,
                            details=f"❌ Expected 403 for security header test, got {response.status}"
                        ))
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.add_result(TestResult(
                name=f"Security Headers: {test_case['name']}",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_performance_under_security_checks(self):
        """Test 6: Performance - Security checks should not significantly impact performance"""
        print("\n⚡ 6. PERFORMANCE UNDER SECURITY CHECKS TESTING")
        print("-" * 50)
        
        # Test legitimate request performance
        await self.test_legitimate_request_performance()
        
        # Test blocked request performance (should also be fast)
        await self.test_blocked_request_performance()

    async def test_legitimate_request_performance(self):
        """Test legitimate request performance"""
        start_time = time.time()
        
        headers = {
            "Origin": "https://carmedia-hub-1.preview.emergentagent.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Performance should be under 500ms as specified
                    if response.status == 200 and response_time < 500:
                        passed = True
                        details = f"✅ Response time within target (<500ms)"
                    elif response.status == 200:
                        passed = False
                        details = f"⚠️ Response time exceeded 500ms target"
                    else:
                        passed = False
                        details = f"❌ Unexpected status code: {response.status}"
                    
                    self.add_result(TestResult(
                        name="Performance: Legitimate Request",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.add_result(TestResult(
                name="Performance: Legitimate Request",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    async def test_blocked_request_performance(self):
        """Test blocked request performance"""
        start_time = time.time()
        
        headers = {
            "Origin": "chrome-extension://test",
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Blocked requests should also be fast
                    if response.status == 403 and response_time < 500:
                        passed = True
                        details = f"✅ Block response time within target (<500ms)"
                    elif response.status == 403:
                        passed = False
                        details = f"⚠️ Block response time exceeded 500ms target"
                    else:
                        passed = False
                        details = f"❌ Expected 403, got {response.status}"
                    
                    self.add_result(TestResult(
                        name="Performance: Blocked Request",
                        passed=passed,
                        response_time=response_time,
                        status_code=response.status,
                        details=details
                    ))
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.add_result(TestResult(
                name="Performance: Blocked Request",
                passed=False,
                response_time=response_time,
                details=f"Request failed: {str(e)}"
            ))

    def add_result(self, result: TestResult):
        """Add test result and update counters"""
        self.results.append(result)
        self.total_tests += 1
        if result.passed:
            self.passed_tests += 1
        
        # Print result immediately
        status = "✅ PASS" if result.passed else "❌ FAIL"
        time_str = f"{result.response_time:.0f}ms" if result.response_time > 0 else "N/A"
        status_code = f"({result.status_code})" if result.status_code else ""
        print(f"{status} {result.name} - {time_str} {status_code}")
        if result.details:
            print(f"     {result.details}")

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 BROWSER EXTENSION CONFLICT PREVENTION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test.name}: {test.details}")
        
        # Performance metrics
        performance_tests = [r for r in self.results if r.response_time > 0]
        if performance_tests:
            avg_response_time = sum(r.response_time for r in performance_tests) / len(performance_tests)
            print(f"\n⚡ Average Response Time: {avg_response_time:.1f}ms")
            
            fast_responses = sum(1 for r in performance_tests if r.response_time < 500)
            print(f"⚡ Responses under 500ms: {fast_responses}/{len(performance_tests)} ({fast_responses/len(performance_tests)*100:.1f}%)")
        
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
        extension_blocked = any('Extension Origin Block' in r.name and r.passed for r in self.results)
        suspicious_blocked = any('Suspicious User Agent' in r.name and r.passed for r in self.results)
        unauthorized_blocked = any('Unauthorized Origin' in r.name and r.passed for r in self.results)
        legitimate_allowed = any('Legitimate Request' in r.name and r.passed for r in self.results)
        security_headers = any('Security Headers' in r.name and r.passed for r in self.results)
        performance_good = avg_response_time < 500 if performance_tests else False
        
        print(f"   Extension requests blocked (403): {'✅' if extension_blocked else '❌'}")
        print(f"   Suspicious user agents blocked (403): {'✅' if suspicious_blocked else '❌'}")
        print(f"   Unauthorized origins blocked (403): {'✅' if unauthorized_blocked else '❌'}")
        print(f"   Legitimate requests allowed (200): {'✅' if legitimate_allowed else '❌'}")
        print(f"   Security headers in error responses: {'✅' if security_headers else '❌'}")
        print(f"   Performance under 500ms: {'✅' if performance_good else '❌'}")

async def main():
    """Main test execution"""
    tester = KagemaFMSecurityTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())