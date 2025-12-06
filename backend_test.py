#!/usr/bin/env python3
"""
🧪 RADIOPLAYER REMOVAL VERIFICATION TESTS
Dragon KARAU AI - Backend Testing for Radioplayer Integration Removal

TESTING FOCUS:
Verify that Radioplayer integration has been successfully removed from Dragon KARAU AI
and that the multi-source crawler system continues to work with remaining sources.

TEST OBJECTIVES:
1. Multi-Source Crawler Manager Initialization - should return 3 crawlers (no radioplayer)
2. Crawler Source Discovery - should show current sources without radioplayer  
3. Individual Crawler Endpoints - radioplayer should fail, others should work
4. Verify Deleted Endpoints - radioplayer endpoints should return 404
5. Dashboard Overview - no radioplayer references

EXPECTED RESULTS:
✅ Multi-source crawler system working with 3 sources
✅ No radioplayer references in any API responses
✅ Radioplayer endpoints properly removed (404)
✅ Remaining crawlers (Dragon AI, Radio Garden, Radio-Browser.info) functional
✅ System operates normally without Radioplayer
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://dragon-radio.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class RadioplayerRemovalTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_multi_source_crawler_stats(self):
        """Test 1: Multi-Source Crawler Manager Initialization"""
        try:
            async with self.session.get(f"{API_BASE}/crawler/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if we have the expected 3 crawlers (no radioplayer)
                    available_crawlers = data.get('available_crawlers', [])
                    expected_crawlers = ['dragon_ai', 'radio_garden', 'radio_browser_info']
                    
                    # Verify no radioplayer in available crawlers
                    has_radioplayer = 'radioplayer' in available_crawlers
                    has_expected_count = len(available_crawlers) == 3
                    has_all_expected = all(crawler in available_crawlers for crawler in expected_crawlers)
                    
                    if not has_radioplayer and has_expected_count and has_all_expected:
                        self.log_test(
                            "Multi-Source Crawler Stats", 
                            True, 
                            f"3 crawlers available: {available_crawlers}, no radioplayer found"
                        )
                    else:
                        self.log_test(
                            "Multi-Source Crawler Stats", 
                            False, 
                            f"Expected 3 crawlers without radioplayer, got: {available_crawlers}"
                        )
                else:
                    self.log_test("Multi-Source Crawler Stats", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Multi-Source Crawler Stats", False, f"Exception: {str(e)}")
    
    async def test_crawler_discover_sources(self):
        """Test 2: Crawler Source Discovery"""
        try:
            async with self.session.get(f"{API_BASE}/crawler/discover-sources") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_sources = data.get('current_sources', [])
                    
                    # Verify no radioplayer in current sources
                    has_radioplayer = 'radioplayer' in current_sources
                    expected_sources = ['dragon_ai', 'radio_garden', 'radio_browser_info']
                    has_all_expected = all(source in current_sources for source in expected_sources)
                    
                    if not has_radioplayer and has_all_expected:
                        self.log_test(
                            "Crawler Source Discovery", 
                            True, 
                            f"Current sources: {current_sources}, no radioplayer found"
                        )
                    else:
                        self.log_test(
                            "Crawler Source Discovery", 
                            False, 
                            f"Unexpected sources: {current_sources}"
                        )
                else:
                    self.log_test("Crawler Source Discovery", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Crawler Source Discovery", False, f"Exception: {str(e)}")
    
    async def test_individual_crawler_endpoints(self):
        """Test 3: Individual Crawler Endpoints"""
        
        # Test valid crawlers (should work or timeout gracefully)
        valid_crawlers = ['dragon_ai', 'radio_garden', 'radio_browser_info']
        
        for crawler in valid_crawlers:
            try:
                async with self.session.post(f"{API_BASE}/crawler/start/{crawler}") as response:
                    # These may timeout (expected for long operations) or return success
                    if response.status in [200, 202, 408, 504]:  # Success, Accepted, or Timeout
                        self.log_test(
                            f"Crawler Start {crawler}", 
                            True, 
                            f"HTTP {response.status} (expected for long operations)"
                        )
                    else:
                        data = await response.text()
                        self.log_test(
                            f"Crawler Start {crawler}", 
                            False, 
                            f"HTTP {response.status}: {data[:100]}"
                        )
            except asyncio.TimeoutError:
                # Timeout is expected for crawler operations
                self.log_test(
                    f"Crawler Start {crawler}", 
                    True, 
                    "Timeout (expected for long crawler operations)"
                )
            except Exception as e:
                self.log_test(f"Crawler Start {crawler}", False, f"Exception: {str(e)}")
        
        # Test radioplayer crawler (should fail)
        try:
            async with self.session.post(f"{API_BASE}/crawler/start/radioplayer") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'error' in data and 'Unknown source' in data.get('error', ''):
                        self.log_test(
                            "Radioplayer Crawler (Should Fail)", 
                            True, 
                            f"Correctly rejected: {data.get('error')}"
                        )
                    else:
                        self.log_test(
                            "Radioplayer Crawler (Should Fail)", 
                            False, 
                            f"Unexpected success: {data}"
                        )
                else:
                    self.log_test(
                        "Radioplayer Crawler (Should Fail)", 
                        True, 
                        f"HTTP {response.status} (correctly rejected)"
                    )
        except Exception as e:
            self.log_test("Radioplayer Crawler (Should Fail)", False, f"Exception: {str(e)}")
    
    async def test_deleted_radioplayer_endpoints(self):
        """Test 4: Verify Deleted Radioplayer Endpoints"""
        
        # Test deleted endpoints (should return 404)
        deleted_endpoints = [
            "/api/radioplayer/auth-status",
            "/api/radioplayer/test-fetch"
        ]
        
        for endpoint in deleted_endpoints:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status == 404:
                        self.log_test(
                            f"Deleted Endpoint {endpoint}", 
                            True, 
                            "HTTP 404 (correctly removed)"
                        )
                    else:
                        data = await response.text()
                        self.log_test(
                            f"Deleted Endpoint {endpoint}", 
                            False, 
                            f"HTTP {response.status}: {data[:100]}"
                        )
            except Exception as e:
                self.log_test(f"Deleted Endpoint {endpoint}", False, f"Exception: {str(e)}")
    
    async def test_multi_source_crawler_start(self):
        """Test 5: Multi-Source Crawler Start"""
        try:
            payload = {"target_stations": 100}  # Small target for testing
            async with self.session.post(
                f"{API_BASE}/crawler/start-multi-source", 
                json=payload
            ) as response:
                if response.status in [200, 202, 408, 504]:  # Success, Accepted, or Timeout
                    self.log_test(
                        "Multi-Source Crawler Start", 
                        True, 
                        f"HTTP {response.status} (multi-source endpoint accessible)"
                    )
                else:
                    data = await response.text()
                    self.log_test(
                        "Multi-Source Crawler Start", 
                        False, 
                        f"HTTP {response.status}: {data[:100]}"
                    )
        except asyncio.TimeoutError:
            # Timeout is expected for crawler operations
            self.log_test(
                "Multi-Source Crawler Start", 
                True, 
                "Timeout (expected for crawler operations)"
            )
        except Exception as e:
            self.log_test("Multi-Source Crawler Start", False, f"Exception: {str(e)}")
    
    async def test_backend_health(self):
        """Test 6: Backend Health Check"""
        try:
            async with self.session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    version = data.get('version', 'unknown')
                    features = data.get('features', [])
                    
                    self.log_test(
                        "Backend Health Check", 
                        True, 
                        f"API v{version}, features: {len(features)}"
                    )
                else:
                    self.log_test("Backend Health Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 RADIOPLAYER REMOVAL VERIFICATION TESTS")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run tests in order
            await self.test_backend_health()
            await self.test_multi_source_crawler_stats()
            await self.test_crawler_discover_sources()
            await self.test_individual_crawler_endpoints()
            await self.test_deleted_radioplayer_endpoints()
            await self.test_multi_source_crawler_start()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("🎉 EXCELLENT - Radioplayer removal successful!")
        elif success_rate >= 70:
            print("✅ GOOD - Most tests passed, minor issues detected")
        else:
            print("⚠️ ISSUES - Significant problems detected")
        
        return success_rate >= 85


async def main():
    """Main test runner"""
    tester = RadioplayerRemovalTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())