#!/usr/bin/env python3
"""
FOCUSED BACKEND TESTING - External Audio Source Error Fixes Verification
Testing the recently fixed PersonalizedContentRequest model and Voice AI Service
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Backend URL from frontend environment
BACKEND_URL = "https://radio-anywhere-6.preview.emergentagent.com/api"

@dataclass
class TestResult:
    name: str
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class FocusedBackendTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> TestResult:
        """Make HTTP request and return test result"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    return TestResult(
                        name=f"{method} {endpoint}",
                        success=response.status < 400,
                        response_time=response_time,
                        status_code=response.status,
                        response_data=response_data
                    )
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    return TestResult(
                        name=f"{method} {endpoint}",
                        success=response.status < 400,
                        response_time=response_time,
                        status_code=response.status,
                        response_data=response_data
                    )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                name=f"{method} {endpoint}",
                success=False,
                response_time=response_time,
                error_message=str(e)
            )
    
    async def test_personalized_content_fix(self):
        """Test the recently fixed PersonalizedContentRequest endpoint with correct format"""
        print("🔧 Testing PersonalizedContentRequest Fix - CRITICAL")
        print("-" * 60)
        
        # Test with Kenya location using CORRECT request format
        kenya_request = {
            "location": {
                "latitude": -1.2921,
                "longitude": 36.8219
            },
            "preferences": {
                "offline_mode": False,
                "preferred_language": "en",
                "user_age": 25
            }
        }
        
        result = await self.make_request("POST", "/personalized-content/multilingual", kenya_request)
        self.results.append(result)
        
        if result.success and result.response_data:
            radio_streams = result.response_data.get('radio_streams', {})
            main_station = radio_streams.get('main_station', {})
            alternatives = radio_streams.get('alternative_streams', [])
            
            print(f"  ✅ Kenya Personalized Content: {result.response_time:.0f}ms")
            print(f"    📻 Main Station: {main_station.get('name', 'N/A')}")
            print(f"    📻 Alternative Streams: {len(alternatives)} available")
            print(f"    🌍 Location Info: {'location_info' in result.response_data}")
            print(f"    🔒 Content Disclaimers: {len(result.response_data.get('content_disclaimers', []))}")
            
            # Verify critical data structure
            has_radio_streams = 'radio_streams' in result.response_data
            has_main_station = main_station.get('streamUrl') is not None
            has_alternatives = len(alternatives) >= 7
            
            if has_radio_streams and has_main_station and has_alternatives:
                print(f"    ✅ Data Structure: Complete radio_streams data present")
            else:
                print(f"    ❌ Data Structure: Missing critical radio data")
                
        else:
            print(f"  ❌ Kenya Personalized Content: {result.error_message or f'Status {result.status_code}'}")
        
        # Test with Brazil location
        brazil_request = {
            "location": {
                "latitude": -23.5505,
                "longitude": -46.6333
            },
            "preferences": {
                "offline_mode": False,
                "preferred_language": "pt-br"
            }
        }
        
        result = await self.make_request("POST", "/personalized-content/multilingual", brazil_request)
        self.results.append(result)
        
        if result.success:
            print(f"  ✅ Brazil Personalized Content: {result.response_time:.0f}ms")
            if result.response_data:
                radio_streams = result.response_data.get('radio_streams', {})
                print(f"    📻 Radio Streams Available: {'radio_streams' in result.response_data}")
        else:
            print(f"  ❌ Brazil Personalized Content: {result.error_message or f'Status {result.status_code}'}")
        
        # Test offline mode
        offline_request = {
            "location": {
                "latitude": -1.2921,
                "longitude": 36.8219
            },
            "preferences": {
                "offline_mode": True,
                "preferred_language": "en"
            }
        }
        
        result = await self.make_request("POST", "/personalized-content/multilingual", offline_request)
        self.results.append(result)
        
        if result.success:
            print(f"  ✅ Offline Mode Content: {result.response_time:.0f}ms")
            if result.response_data:
                offline_mode = result.response_data.get('offline_mode', False)
                print(f"    💾 Offline Mode Active: {offline_mode}")
        else:
            print(f"  ❌ Offline Mode Content: {result.error_message or f'Status {result.status_code}'}")
    
    async def test_voice_ai_service_fix(self):
        """Test Voice AI Service with proper context parameter handling"""
        print("\n🎤 Testing Voice AI Service - Context Parameter Fix")
        print("-" * 60)
        
        # Test simple commands with proper context
        simple_commands = [
            {"text": "play", "context": "radio_control"},
            {"text": "pause", "context": "radio_control"},
            {"text": "next", "context": "radio_control"},
            {"text": "volume up", "context": "audio_control"}
        ]
        
        for cmd in simple_commands:
            result = await self.make_request("POST", "/voice/interpret", cmd)
            self.results.append(result)
            
            if result.success and result.response_data:
                confidence = result.response_data.get('confidence', 0)
                intent = result.response_data.get('intent', 'unknown')
                print(f"  ✅ '{cmd['text']}': {intent} ({confidence:.2f} confidence) - {result.response_time:.0f}ms")
            else:
                print(f"  ❌ '{cmd['text']}': {result.error_message or f'Status {result.status_code}'}")
        
        # Test complex commands
        complex_commands = [
            {"text": "search for jazz music", "context": "music_discovery"},
            {"text": "tune to classical station", "context": "station_control"}
        ]
        
        for cmd in complex_commands:
            result = await self.make_request("POST", "/voice/interpret", cmd)
            self.results.append(result)
            
            if result.success and result.response_data:
                confidence = result.response_data.get('confidence', 0)
                intent = result.response_data.get('intent', 'unknown')
                parameters = result.response_data.get('parameters', {})
                print(f"  ✅ '{cmd['text']}': {intent} ({confidence:.2f} confidence)")
                if parameters:
                    print(f"    📋 Parameters: {parameters}")
            else:
                print(f"  ❌ '{cmd['text']}': {result.error_message or f'Status {result.status_code}'}")
    
    async def test_external_audio_sources(self):
        """Test external audio source integrations"""
        print("\n🌐 Testing External Audio Sources - Error Fixes")
        print("-" * 60)
        
        # Test app version endpoint for external sources configuration
        result = await self.make_request("GET", "/app/version")
        self.results.append(result)
        
        if result.success and result.response_data:
            external_sources = result.response_data.get('external_sources', {})
            print(f"  ✅ External Sources Config: {result.response_time:.0f}ms")
            print(f"    📡 Sources Configured: {len(external_sources)}")
            for source, url in external_sources.items():
                if source != 'last_updated':
                    print(f"    🎵 {source}: {url}")
        else:
            print(f"  ❌ External Sources Config: {result.error_message or f'Status {result.status_code}'}")
        
        # Test language detection (foundation for external sources)
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi, Kenya"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo, Brazil"},
            {"latitude": 40.7128, "longitude": -74.0060, "name": "New York, USA"}
        ]
        
        for location in test_locations:
            result = await self.make_request("POST", "/language/detect", {
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            })
            self.results.append(result)
            
            if result.success and result.response_data:
                detected_lang = result.response_data.get('detected_language', 'unknown')
                confidence = result.response_data.get('confidence', 0)
                radio_streams = result.response_data.get('radio_streams', [])
                print(f"  ✅ {location['name']}: {detected_lang} ({confidence:.2f} confidence)")
                print(f"    📻 Radio Streams: {len(radio_streams)} available")
            else:
                print(f"  ❌ {location['name']}: {result.error_message or f'Status {result.status_code}'}")
    
    async def test_radio_streaming_stability(self):
        """Test all 8 radio streams for accessibility with proper audio headers"""
        print("\n📻 Testing Radio Streaming Stability - All 8 Streams")
        print("-" * 60)
        
        # Get radio streams
        result = await self.make_request("GET", "/radio/streams")
        self.results.append(result)
        
        if not result.success:
            print(f"  ❌ Radio Streams API: {result.error_message or f'Status {result.status_code}'}")
            return
        
        print(f"  ✅ Radio Streams API: {result.response_time:.0f}ms")
        
        # Test stream URL accessibility
        stream_urls = [
            ("Main Station", "https://ice1.somafm.com/groovesalad-256-mp3"),
            ("SomaFM Groove Salad", "https://ice1.somafm.com/groovesalad-256-mp3"),
            ("Radio Paradise AAC", "https://stream.radioparadise.com/aac-320"),
            ("Radio Paradise MP3", "https://stream.radioparadise.com/mp3-192"),
            ("FIP Radio France AAC", "https://icecast.radiofrance.fr/fip-hifi.aac"),
            ("FIP Radio France MP3", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
            ("SomaFM Drone Zone", "http://ice1.somafm.com/dronezone-256-mp3"),
            ("SomaFM DEF CON Radio", "http://ice1.somafm.com/defcon-256-mp3")
        ]
        
        accessible_streams = 0
        for name, url in stream_urls:
            try:
                start_time = time.time()
                async with self.session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status < 400:
                        accessible_streams += 1
                        content_type = response.headers.get('content-type', '')
                        icy_headers = any('icy' in str(k).lower() for k in response.headers.keys())
                        print(f"  ✅ {name}: {response_time:.0f}ms")
                        print(f"    📡 Content-Type: {content_type}")
                        if icy_headers:
                            print(f"    🎵 ICY Streaming: Detected")
                    else:
                        print(f"  ❌ {name}: Status {response.status}")
            except Exception as e:
                print(f"  ❌ {name}: {str(e)}")
        
        print(f"\n  📊 Stream Accessibility: {accessible_streams}/{len(stream_urls)} ({accessible_streams/len(stream_urls)*100:.1f}%)")
    
    async def test_error_handling_fixes(self):
        """Test error handling scenarios"""
        print("\n⚠️ Testing Error Handling - 404/422 Response Fixes")
        print("-" * 60)
        
        # Test 404 errors
        result = await self.make_request("GET", "/nonexistent-endpoint")
        self.results.append(result)
        
        if result.status_code == 404:
            print(f"  ✅ 404 Error Handling: {result.response_time:.0f}ms")
        else:
            print(f"  ❌ 404 Error Handling: Expected 404, got {result.status_code}")
        
        # Test 422 validation errors with invalid PersonalizedContentRequest
        invalid_data = {"invalid": "data"}
        result = await self.make_request("POST", "/personalized-content/multilingual", invalid_data)
        self.results.append(result)
        
        if result.status_code == 422:
            print(f"  ✅ 422 Validation Error: {result.response_time:.0f}ms")
        else:
            print(f"  ❌ 422 Validation Error: Expected 422, got {result.status_code}")
        
        # Test missing location field
        missing_location = {"preferences": {"offline_mode": False}}
        result = await self.make_request("POST", "/personalized-content/multilingual", missing_location)
        self.results.append(result)
        
        if result.status_code == 422:
            print(f"  ✅ Missing Location Validation: {result.response_time:.0f}ms")
        else:
            print(f"  ❌ Missing Location Validation: Expected 422, got {result.status_code}")
    
    async def test_performance_verification(self):
        """Test performance requirements - average response times under 500ms"""
        print("\n⚡ Testing Performance Verification - <500ms Target")
        print("-" * 60)
        
        # Test critical endpoints for performance
        critical_endpoints = [
            ("GET", "/", "API Root"),
            ("GET", "/station-info", "Station Info"),
            ("GET", "/radio/streams", "Radio Streams"),
            ("GET", "/voice/intents", "Voice Intents"),
            ("GET", "/languages", "Supported Languages")
        ]
        
        total_response_time = 0
        successful_requests = 0
        
        for method, endpoint, name in critical_endpoints:
            result = await self.make_request(method, endpoint)
            self.results.append(result)
            
            if result.success:
                successful_requests += 1
                total_response_time += result.response_time
                
                if result.response_time < 500:
                    print(f"  ✅ {name}: {result.response_time:.0f}ms (under 500ms target)")
                else:
                    print(f"  ⚠️ {name}: {result.response_time:.0f}ms (over 500ms target)")
            else:
                print(f"  ❌ {name}: {result.error_message or f'Status {result.status_code}'}")
        
        if successful_requests > 0:
            avg_response_time = total_response_time / successful_requests
            print(f"\n  📊 Average Response Time: {avg_response_time:.0f}ms")
            
            if avg_response_time < 500:
                print(f"  ✅ Performance Target: ACHIEVED (under 500ms)")
            else:
                print(f"  ❌ Performance Target: MISSED (over 500ms)")
    
    async def run_focused_tests(self):
        """Run focused tests for external audio source error fixes"""
        print("🎉 FOCUSED BACKEND TESTING - EXTERNAL AUDIO SOURCE ERROR FIXES VERIFICATION")
        print("=" * 90)
        print(f"🎯 Backend URL: {BACKEND_URL}")
        print("🔧 Focus: PersonalizedContentRequest Fix & Voice AI Context Parameters")
        print("=" * 90)
        
        await self.test_personalized_content_fix()
        await self.test_voice_ai_service_fix()
        await self.test_external_audio_sources()
        await self.test_radio_streaming_stability()
        await self.test_error_handling_fixes()
        await self.test_performance_verification()
        
        # Summary
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        response_times = [r.response_time for r in self.results if r.response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print("\n" + "=" * 90)
        print("📊 FOCUSED TEST RESULTS SUMMARY")
        print("=" * 90)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time:.0f}ms")
        
        # Critical findings
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test.name}: {test.error_message or f'Status {test.status_code}'}")
        
        # Performance analysis
        if avg_response_time < 500:
            print(f"\n✅ PERFORMANCE: Excellent ({avg_response_time:.0f}ms average)")
        else:
            print(f"\n⚠️ PERFORMANCE: Needs improvement ({avg_response_time:.0f}ms average)")
        
        # Deployment readiness
        print(f"\n🎯 EXTERNAL AUDIO SOURCE FIXES ASSESSMENT:")
        if success_rate >= 95:
            print("✅ EXCELLENT - All fixes working correctly")
        elif success_rate >= 85:
            print("✅ GOOD - Minor issues detected")
        elif success_rate >= 75:
            print("⚠️ FAIR - Some fixes need attention")
        else:
            print("❌ POOR - Critical fixes not working")
        
        return success_rate, avg_response_time, failed_tests

async def main():
    """Main test execution"""
    async with FocusedBackendTester() as tester:
        success_rate, avg_response_time, failed_tests = await tester.run_focused_tests()
        
        # Return results for further analysis
        return success_rate, avg_response_time, failed_tests

if __name__ == "__main__":
    asyncio.run(main())