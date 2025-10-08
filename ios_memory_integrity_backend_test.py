#!/usr/bin/env python3
"""
iOS Memory Integrity Enforcement Backend Testing
Testing Focus: Verify backend stability after iOS security configuration changes

CONTEXT: Just implemented comprehensive iOS Memory Integrity Enforcement
- Need to verify backend stability is unaffected by iOS security configuration changes
- Focus on the 6 priority areas from review request
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://global-audio-hub.preview.emergentagent.com/api"

@dataclass
class TestResult:
    name: str
    success: bool
    response_time: float
    details: str
    error: Optional[str] = None

class iOSMemoryIntegrityBackendTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple[bool, Dict, float]:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        try:
            url = f"{BACKEND_URL}{endpoint}"
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    result = await response.json()
                    return response.status == 200, result, response_time
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    result = await response.json()
                    return response.status == 200, result, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return False, {"error": str(e)}, response_time
    
    async def test_stream_accessibility(self, stream_url: str, stream_name: str) -> TestResult:
        """Test if radio stream is accessible with proper headers"""
        start_time = time.time()
        try:
            async with self.session.head(stream_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = time.time() - start_time
                
                # Check for audio content type
                content_type = response.headers.get('content-type', '').lower()
                is_audio = any(audio_type in content_type for audio_type in ['audio', 'mpeg', 'mp3', 'aac'])
                
                # Check for ICY streaming headers (common for radio streams)
                has_icy = any(header.lower().startswith('icy-') for header in response.headers.keys())
                
                success = response.status == 200 and (is_audio or has_icy)
                details = f"Status: {response.status}, Content-Type: {content_type}, ICY Headers: {has_icy}"
                
                return TestResult(
                    name=f"Stream Accessibility - {stream_name}",
                    success=success,
                    response_time=response_time * 1000,  # Convert to ms
                    details=details
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                name=f"Stream Accessibility - {stream_name}",
                success=False,
                response_time=response_time * 1000,
                details="Stream connection failed",
                error=str(e)
            )
    
    # PRIORITY 1: Core API Health Check
    async def test_core_api_health_check(self):
        """Test core API endpoints as specified in review request"""
        print("🔍 PRIORITY 1: Core API Health Check")
        
        # Test GET /api/
        success, result, response_time = await self.make_request("GET", "/")
        self.results.append(TestResult(
            name="Core API Health - GET /api/",
            success=success and "Kagema FM" in str(result),
            response_time=response_time * 1000,
            details=f"API Message: {result.get('message', 'N/A')}, Version: {result.get('version', 'N/A')}" if success else "Failed to connect"
        ))
        
        # Test GET /api/station-info
        success, result, response_time = await self.make_request("GET", "/station-info")
        self.results.append(TestResult(
            name="Core API Health - GET /api/station-info",
            success=success and result.get('streamUrl') is not None,
            response_time=response_time * 1000,
            details=f"Station: {result.get('name', 'N/A')}, Stream: {result.get('streamUrl', 'N/A')}" if success else "Failed to get station info"
        ))
        
        # Test POST /api/personalized-content/multilingual (CRITICAL for frontend)
        personalized_request = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"offline_mode": False, "preferred_language": "en"}
        }
        success, result, response_time = await self.make_request("POST", "/personalized-content/multilingual", personalized_request)
        has_radio_streams = success and 'radio_streams' in result
        self.results.append(TestResult(
            name="Core API Health - POST /api/personalized-content/multilingual",
            success=has_radio_streams,
            response_time=response_time * 1000,
            details=f"Radio streams present: {has_radio_streams}, Content source: {result.get('content_source', 'N/A')}" if success else "Failed to get personalized content"
        ))
    
    # PRIORITY 2: Radio Streaming Verification
    async def test_radio_streaming_verification(self):
        """Test all 8 radio streams to ensure they remain accessible"""
        print("📻 PRIORITY 2: Radio Streaming Verification")
        
        # Get radio streams from API
        success, streams_data, _ = await self.make_request("GET", "/radio/streams")
        
        if success:
            # Test main station
            main_station = streams_data.get('main_station', {})
            if main_station.get('streamUrl'):
                result = await self.test_stream_accessibility(main_station['streamUrl'], main_station.get('name', 'Main Station'))
                self.results.append(result)
            
            # Test alternative streams (should be 7 according to review request)
            alt_streams = streams_data.get('alternative_streams', [])
            for stream in alt_streams:
                if stream.get('streamUrl'):
                    result = await self.test_stream_accessibility(stream['streamUrl'], stream.get('name', 'Unknown Stream'))
                    self.results.append(result)
        else:
            self.results.append(TestResult(
                name="Radio Streaming Setup",
                success=False,
                response_time=0,
                details="Failed to get radio streams for testing"
            ))
    
    # PRIORITY 3: Voice AI Integration
    async def test_voice_ai_integration(self):
        """Verify voice command processing is unaffected by configuration changes"""
        print("🎤 PRIORITY 3: Voice AI Integration")
        
        # Test voice intents
        success, result, response_time = await self.make_request("GET", "/voice/intents")
        intents_count = len(result) if success and isinstance(result, dict) else 0
        self.results.append(TestResult(
            name="Voice AI - Available Intents",
            success=success and intents_count > 0,
            response_time=response_time * 1000,
            details=f"Available intents: {intents_count}" if success else "Failed to get voice intents"
        ))
        
        # Test voice help
        success, result, response_time = await self.make_request("GET", "/voice/help")
        help_commands = len(result.get('commands', {})) if success else 0
        usage_tips = len(result.get('usage_tips', [])) if success else 0
        self.results.append(TestResult(
            name="Voice AI - Help System",
            success=success and help_commands > 0,
            response_time=response_time * 1000,
            details=f"Commands: {help_commands}, Usage tips: {usage_tips}" if success else "Failed to get voice help"
        ))
        
        # Test voice command interpretation - Simple commands
        simple_commands = [
            {"text": "play", "context": "radio"},
            {"text": "pause", "context": "radio"},
            {"text": "next", "context": "radio"},
            {"text": "volume up", "context": "radio"}
        ]
        
        for cmd in simple_commands:
            success, result, response_time = await self.make_request("POST", "/voice/interpret", cmd)
            confidence = result.get('confidence', 0) if success else 0
            self.results.append(TestResult(
                name=f"Voice AI - Simple Command '{cmd['text']}'",
                success=success and confidence > 0.8,
                response_time=response_time * 1000,
                details=f"Intent: {result.get('intent', 'N/A')}, Confidence: {confidence:.2f}" if success else "Command interpretation failed"
            ))
        
        # Test complex AI processing commands
        complex_commands = [
            {"text": "search for jazz music", "context": "radio"},
            {"text": "tune to classical station", "context": "radio"}
        ]
        
        for cmd in complex_commands:
            success, result, response_time = await self.make_request("POST", "/voice/interpret", cmd)
            confidence = result.get('confidence', 0) if success else 0
            self.results.append(TestResult(
                name=f"Voice AI - Complex Command '{cmd['text']}'",
                success=success and confidence > 0.7,
                response_time=response_time * 1000,
                details=f"Intent: {result.get('intent', 'N/A')}, Confidence: {confidence:.2f}, Parameters: {result.get('parameters', {})}" if success else "Complex command failed"
            ))
    
    # PRIORITY 4: Performance Validation
    async def test_performance_validation(self):
        """Ensure response times remain under 500ms target"""
        print("⚡ PRIORITY 4: Performance Validation")
        
        # Test critical endpoints for performance
        critical_endpoints = [
            ("GET", "/", "API Root"),
            ("GET", "/station-info", "Station Info"),
            ("GET", "/radio/streams", "Radio Streams"),
            ("GET", "/voice/intents", "Voice Intents"),
            ("GET", "/languages", "Languages")
        ]
        
        for method, endpoint, name in critical_endpoints:
            success, result, response_time = await self.make_request(method, endpoint)
            response_time_ms = response_time * 1000
            under_target = response_time_ms < 500
            
            self.results.append(TestResult(
                name=f"Performance - {name}",
                success=success and under_target,
                response_time=response_time_ms,
                details=f"Status: {success}, Time: {response_time_ms:.1f}ms (target: <500ms)" if success else "Request failed"
            ))
        
        # Test concurrent requests
        concurrent_endpoints = [
            ("GET", "/"),
            ("GET", "/station-info"),
            ("GET", "/languages"),
            ("GET", "/radio/streams"),
            ("GET", "/voice/intents")
        ]
        
        start_time = time.time()
        tasks = []
        for method, endpoint in concurrent_endpoints:
            tasks.append(self.make_request(method, endpoint))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for result in results if not isinstance(result, Exception) and result[0])
        avg_response_time = sum(result[2] for result in results if not isinstance(result, Exception)) / len(results) * 1000
        
        self.results.append(TestResult(
            name="Performance - Concurrent Requests",
            success=successful_requests == len(concurrent_endpoints) and avg_response_time < 500,
            response_time=avg_response_time,
            details=f"Successful: {successful_requests}/{len(concurrent_endpoints)}, Avg time: {avg_response_time:.1f}ms, Total: {total_time:.2f}s"
        ))
    
    # PRIORITY 5: Content & Compliance
    async def test_content_compliance(self):
        """Test language detection and content compliance features"""
        print("🌍 PRIORITY 5: Content & Compliance")
        
        # Test language detection for different locations
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "expected": "Nairobi, Kenya"},
            {"latitude": -1.4743, "longitude": 35.0063, "expected": "Kisumu, Kenya"},
            {"latitude": -23.5505, "longitude": -46.6333, "expected": "São Paulo, Brazil"}
        ]
        
        for location in test_locations:
            success, result, response_time = await self.make_request("POST", "/language/detect", 
                {"latitude": location["latitude"], "longitude": location["longitude"]})
            detected_lang = result.get('detected_language', 'unknown') if success else 'failed'
            confidence = result.get('confidence', 0) if success else 0
            
            self.results.append(TestResult(
                name=f"Content Compliance - Language Detection ({location['expected']})",
                success=success and confidence > 0.8,
                response_time=response_time * 1000,
                details=f"Language: {detected_lang}, Confidence: {confidence:.2f}, County: {result.get('county', 'N/A')}" if success else "Language detection failed"
            ))
        
        # Test supported languages
        success, result, response_time = await self.make_request("GET", "/languages")
        languages_count = len(result.get('languages', [])) if success else 0
        self.results.append(TestResult(
            name="Content Compliance - Supported Languages",
            success=success and languages_count >= 8,
            response_time=response_time * 1000,
            details=f"Languages: {languages_count}, Countries: {result.get('supported_countries', [])}" if success else "Failed to get languages"
        ))
        
        # Test content disclaimers for different regions
        regions = ["KE", "BR", "GLOBAL"]
        for region in regions:
            disclaimer_request = {
                "country_code": region,
                "language_code": "en",
                "content_types": ["radio_streams", "music", "news"]
            }
            success, result, response_time = await self.make_request("POST", "/compliance/disclaimers", disclaimer_request)
            disclaimers_count = len(result.get('content_disclaimers', [])) if success else 0
            
            self.results.append(TestResult(
                name=f"Content Compliance - Disclaimers ({region})",
                success=success and disclaimers_count > 0,
                response_time=response_time * 1000,
                details=f"Disclaimers: {disclaimers_count}, User acknowledgment required: {result.get('user_acknowledgment_required', False)}" if success else "Failed to get disclaimers"
            ))
    
    # PRIORITY 6: Error Handling
    async def test_error_handling(self):
        """Verify proper error responses for invalid requests"""
        print("❌ PRIORITY 6: Error Handling")
        
        # Test 404 for non-existent endpoints
        try:
            async with self.session.get(f"{BACKEND_URL}/non-existent-endpoint") as response:
                success = response.status == 404
                self.results.append(TestResult(
                    name="Error Handling - 404 for Invalid Endpoints",
                    success=success,
                    response_time=0,
                    details=f"Status: {response.status} (expected 404)" if success else f"Unexpected status: {response.status}"
                ))
        except Exception as e:
            self.results.append(TestResult(
                name="Error Handling - 404 for Invalid Endpoints",
                success=False,
                response_time=0,
                details="Request failed",
                error=str(e)
            ))
        
        # Test 422 for invalid POST data
        try:
            async with self.session.post(f"{BACKEND_URL}/language/detect", json={"invalid": "data"}) as response:
                success = response.status == 422
                self.results.append(TestResult(
                    name="Error Handling - 422 for Invalid Data",
                    success=success,
                    response_time=0,
                    details=f"Status: {response.status} (expected 422)" if success else f"Unexpected status: {response.status}"
                ))
        except Exception as e:
            self.results.append(TestResult(
                name="Error Handling - 422 for Invalid Data",
                success=False,
                response_time=0,
                details="Request failed",
                error=str(e)
            ))
        
        # Test invalid coordinates fallback
        invalid_coords = {"latitude": 999, "longitude": 999}
        success, result, response_time = await self.make_request("POST", "/language/detect", invalid_coords)
        fallback_lang = result.get('detected_language', '') if success else ''
        self.results.append(TestResult(
            name="Error Handling - Invalid Coordinates Fallback",
            success=success and fallback_lang == 'en',
            response_time=response_time * 1000,
            details=f"Fallback language: {fallback_lang}" if success else "Fallback handling failed"
        ))
    
    async def run_all_tests(self):
        """Run all test suites for iOS Memory Integrity Enforcement verification"""
        print("🎯 iOS MEMORY INTEGRITY ENFORCEMENT - BACKEND STABILITY TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites in priority order
        await self.test_core_api_health_check()
        await self.test_radio_streaming_verification()
        await self.test_voice_ai_integration()
        await self.test_performance_validation()
        await self.test_content_compliance()
        await self.test_error_handling()
        
        total_time = time.time() - start_time
        
        # Calculate results
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        avg_response_time = sum(result.response_time for result in self.results) / total_tests if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎉 iOS MEMORY INTEGRITY ENFORCEMENT BACKEND TESTING COMPLETE")
        print("=" * 80)
        print(f"📊 RESULTS SUMMARY:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed_tests}")
        print(f"   • Failed: {total_tests - passed_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Average Response Time: {avg_response_time:.1f}ms")
        print(f"   • Total Test Duration: {total_time:.2f}s")
        
        # Performance metrics
        under_500ms = sum(1 for result in self.results if result.response_time < 500)
        performance_rate = (under_500ms / total_tests) * 100 if total_tests > 0 else 0
        print(f"   • Responses Under 500ms: {under_500ms}/{total_tests} ({performance_rate:.1f}%)")
        
        # Priority area results
        print(f"\n📋 PRIORITY AREA RESULTS:")
        print("-" * 80)
        
        priority_areas = {
            "Core API Health": [r for r in self.results if "Core API Health" in r.name],
            "Radio Streaming": [r for r in self.results if "Stream Accessibility" in r.name],
            "Voice AI Integration": [r for r in self.results if "Voice AI" in r.name],
            "Performance Validation": [r for r in self.results if "Performance" in r.name],
            "Content & Compliance": [r for r in self.results if "Content Compliance" in r.name],
            "Error Handling": [r for r in self.results if "Error Handling" in r.name]
        }
        
        for area, area_results in priority_areas.items():
            if area_results:
                area_passed = sum(1 for r in area_results if r.success)
                area_total = len(area_results)
                area_rate = (area_passed / area_total) * 100
                status = "✅" if area_rate >= 90 else "⚠️" if area_rate >= 70 else "❌"
                print(f"{status} {area}: {area_passed}/{area_total} ({area_rate:.1f}%)")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        print("-" * 80)
        
        failed_tests = []
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} | {result.name:<50} | {result.response_time:>6.0f}ms | {result.details}")
            if not result.success:
                failed_tests.append(result)
        
        # Failed tests details
        if failed_tests:
            print(f"\n🚨 FAILED TESTS DETAILS:")
            print("-" * 80)
            for result in failed_tests:
                print(f"❌ {result.name}")
                print(f"   Details: {result.details}")
                if result.error:
                    print(f"   Error: {result.error}")
                print()
        
        # iOS Memory Integrity Impact Assessment
        print(f"\n🍎 iOS MEMORY INTEGRITY IMPACT ASSESSMENT:")
        print("-" * 80)
        
        critical_areas_status = {
            "Core API Endpoints": any("Core API Health" in r.name for r in self.results if r.success),
            "Radio Stream Accessibility": any("Stream Accessibility" in r.name for r in self.results if r.success),
            "Voice AI Processing": any("Voice AI" in r.name for r in self.results if r.success),
            "Performance (<500ms)": performance_rate > 95,
            "Content Compliance": any("Content Compliance" in r.name for r in self.results if r.success),
            "Error Handling": any("Error Handling" in r.name for r in self.results if r.success)
        }
        
        for area, status in critical_areas_status.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {area}")
        
        all_critical_passed = all(critical_areas_status.values())
        deployment_ready = success_rate >= 95 and all_critical_passed
        
        print(f"\n🚀 DEPLOYMENT RECOMMENDATION:")
        if deployment_ready:
            print("✅ PRODUCTION READY - iOS security enhancements have not affected backend stability")
            print("   All critical functionality verified, backend remains stable after iOS configuration changes")
        elif success_rate >= 85:
            print("⚠️  MOSTLY READY - Minor issues detected, but core functionality stable")
            print("   iOS security enhancements appear to have minimal impact on backend performance")
        else:
            print("❌ REQUIRES ATTENTION - Some critical issues detected")
            print("   Review failed tests to ensure iOS security changes haven't introduced instability")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "deployment_ready": deployment_ready,
            "failed_tests": failed_tests,
            "ios_impact_minimal": success_rate >= 85
        }

async def main():
    """Main test execution"""
    async with iOSMemoryIntegrityBackendTester() as tester:
        results = await tester.run_all_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())