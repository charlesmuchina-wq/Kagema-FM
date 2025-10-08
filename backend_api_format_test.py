#!/usr/bin/env python3
"""
CRITICAL BACKEND API REQUEST FORMAT TESTING for Kagema FM Enhanced
Focus: Testing the specific API request format fixes mentioned in review request

SPECIFIC ISSUES FIXED TO TEST:
1. ✅ **Personalized Content API**: Fixed `/api/personalized-content/multilingual` to use single `PersonalizedContentRequest` model
2. ✅ **Request Format Consistency**: Updated endpoint to handle combined request body properly
3. ✅ **Voice AI Service**: Verified proper context parameter handling with default values

EXPECTED OUTCOME: Success rate should improve significantly from 67.5% to 85%+ if fixes are effective.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
import sys
import os

class BackendAPIFormatTester:
    def __init__(self):
        # Use the frontend env URL for testing as specified in instructions
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        
        if not hasattr(self, 'base_url'):
            self.base_url = "https://radioverse-18.preview.emergentagent.com"
        
        self.api_url = f"{self.base_url}/api"
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to API endpoint"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    content = await response.text()
                    
                    try:
                        json_data = json.loads(content)
                    except json.JSONDecodeError:
                        json_data = {"raw_content": content}
                    
                    return {
                        "status_code": response.status,
                        "data": json_data,
                        "response_time": response_time,
                        "headers": dict(response.headers)
                    }
            else:
                headers = {"Content-Type": "application/json"}
                async with self.session.request(method, url, json=data, params=params, headers=headers) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    content = await response.text()
                    
                    try:
                        json_data = json.loads(content)
                    except json.JSONDecodeError:
                        json_data = {"raw_content": content}
                    
                    return {
                        "status_code": response.status,
                        "data": json_data,
                        "response_time": response_time,
                        "headers": dict(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "response_time": 0,
                "headers": {}
            }
    
    def log_test_result(self, test_name: str, success: bool, details: str, response_time: int = 0):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} | {test_name} | {details}"
        if response_time > 0:
            result += f" | {response_time}ms"
            
        self.test_results.append(result)
        print(result)
    
    async def test_personalized_content_api_fixes(self):
        """Test the CRITICAL personalized content API fixes - HIGH PRIORITY"""
        print("\n🎯 TESTING PERSONALIZED CONTENT API FIXES (HIGH PRIORITY)")
        print("=" * 70)
        
        # Test with proper request format as specified in review request
        test_request = {
            "location": {
                "latitude": -1.286389,
                "longitude": 36.817223
            },
            "preferences": {
                "offline_mode": False,
                "preferred_language": "en"
            }
        }
        
        print(f"Testing with proper PersonalizedContentRequest format:")
        print(f"Request: {json.dumps(test_request, indent=2)}")
        
        response = await self.make_request('POST', '/personalized-content/multilingual', test_request)
        
        if response['status_code'] == 200:
            data = response['data']
            # Check for critical radio_streams data
            if 'radio_streams' in data:
                radio_streams = data['radio_streams']
                if 'main_station' in radio_streams and 'alternative_streams' in radio_streams:
                    alt_count = len(radio_streams.get('alternative_streams', []))
                    self.log_test_result("Personalized Content API - Request Format Fix", True, 
                                       f"API accepts combined request body, radio_streams present with {alt_count} alternatives", 
                                       response['response_time'])
                    
                    # Verify main station has required fields
                    main_station = radio_streams['main_station']
                    if 'streamUrl' in main_station and 'name' in main_station:
                        self.log_test_result("Personalized Content API - Main Station Structure", True, 
                                           f"Main station: {main_station['name']}, Stream URL present", 
                                           response['response_time'])
                    else:
                        self.log_test_result("Personalized Content API - Main Station Structure", False, 
                                           "Main station missing required fields (streamUrl or name)")
                else:
                    self.log_test_result("Personalized Content API - Radio Streams Structure", False, 
                                       "Missing main_station or alternative_streams in radio_streams")
            else:
                self.log_test_result("Personalized Content API - Request Format Fix", False, 
                                   "API accepts request but missing critical radio_streams data")
        elif response['status_code'] == 422:
            self.log_test_result("Personalized Content API - Request Format Fix", False, 
                               f"422 Validation Error - Request format still not accepted: {response['data']}")
        else:
            self.log_test_result("Personalized Content API - Request Format Fix", False, 
                               f"Status: {response['status_code']}, Error: {response['data']}")
        
        # Test with Brazil location for international support
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
        
        response = await self.make_request('POST', '/personalized-content/multilingual', brazil_request)
        if response['status_code'] == 200 and 'radio_streams' in response['data']:
            self.log_test_result("Personalized Content API - Brazil Location Support", True, 
                               "Brazil location processing with radio streams", 
                               response['response_time'])
        else:
            self.log_test_result("Personalized Content API - Brazil Location Support", False, 
                               f"Status: {response['status_code']}")
        
        # Test with offline mode preference
        offline_request = {
            "location": {
                "latitude": -1.286389,
                "longitude": 36.817223
            },
            "preferences": {
                "offline_mode": True,
                "preferred_language": "en"
            }
        }
        
        response = await self.make_request('POST', '/personalized-content/multilingual', offline_request)
        if response['status_code'] == 200:
            data = response['data']
            if data.get('offline_mode') == True and 'content_source' in data:
                self.log_test_result("Personalized Content API - Offline Mode Support", True, 
                                   f"Offline mode: {data['offline_mode']}, Source: {data['content_source']}", 
                                   response['response_time'])
            else:
                self.log_test_result("Personalized Content API - Offline Mode Support", False, 
                                   "Offline mode not properly handled")
        else:
            self.log_test_result("Personalized Content API - Offline Mode Support", False, 
                               f"Status: {response['status_code']}")
    
    async def test_voice_ai_service_fixes(self):
        """Test Voice AI service with proper context parameter handling - HIGH PRIORITY"""
        print("\n🎤 TESTING VOICE AI SERVICE FIXES (HIGH PRIORITY)")
        print("=" * 70)
        
        # Test voice command interpretation with proper context parameter
        voice_commands = [
            {"text": "play radio", "context": "radio_control"},
            {"text": "pause", "context": "playback_control"},
            {"text": "next station", "context": "station_control"},
            {"text": "volume up", "context": "audio_control"},
            {"text": "search for jazz music", "context": "content_search"},
            {"text": "tune to classical station", "context": "station_search"}
        ]
        
        for command in voice_commands:
            print(f"Testing voice command: {command}")
            response = await self.make_request('POST', '/voice/interpret', command)
            
            if response['status_code'] == 200:
                data = response['data']
                if 'intent' in data and 'confidence' in data:
                    confidence = data.get('confidence', 0)
                    intent = data.get('intent', 'unknown')
                    self.log_test_result(f"Voice AI - '{command['text']}'", True, 
                                       f"Intent: {intent}, Confidence: {confidence:.2f}", 
                                       response['response_time'])
                else:
                    self.log_test_result(f"Voice AI - '{command['text']}'", False, 
                                       "Missing intent or confidence in response")
            else:
                self.log_test_result(f"Voice AI - '{command['text']}'", False, 
                                   f"Status: {response['status_code']}, Error: {response['data']}")
        
        # Test voice command without context parameter (should use default)
        simple_command = {"text": "play radio"}
        response = await self.make_request('POST', '/voice/interpret', simple_command)
        
        if response['status_code'] == 200:
            data = response['data']
            if 'intent' in data and 'confidence' in data:
                self.log_test_result("Voice AI - Default Context Parameter", True, 
                                   f"Command without context handled: Intent: {data['intent']}", 
                                   response['response_time'])
            else:
                self.log_test_result("Voice AI - Default Context Parameter", False, 
                                   "Command without context not handled properly")
        else:
            self.log_test_result("Voice AI - Default Context Parameter", False, 
                               f"Status: {response['status_code']}")
    
    async def test_integration_support_endpoints(self):
        """Test iHeartRadio and Streema integration support endpoints - MEDIUM PRIORITY"""
        print("\n🌍 TESTING INTEGRATION SUPPORT ENDPOINTS (MEDIUM PRIORITY)")
        print("=" * 70)
        
        # Test language detection for US (iHeartRadio support)
        us_location = {"latitude": 40.7128, "longitude": -74.0060}  # New York
        response = await self.make_request('POST', '/language/detect', us_location)
        
        if response['status_code'] == 200:
            detected_lang = response['data'].get('detected_language', '')
            confidence = response['data'].get('confidence', 0)
            if detected_lang == 'en':
                self.log_test_result("iHeartRadio Support - US Language Detection", True, 
                                   f"US location detected as English: {detected_lang}, Confidence: {confidence:.2f}", 
                                   response['response_time'])
            else:
                self.log_test_result("iHeartRadio Support - US Language Detection", False, 
                                   f"Expected 'en', got: {detected_lang}")
        else:
            self.log_test_result("iHeartRadio Support - US Language Detection", False, 
                               f"Status: {response['status_code']}")
        
        # Test language detection for international locations (Streema support)
        international_locations = [
            {"latitude": 52.5200, "longitude": 13.4050, "location": "Berlin"},
            {"latitude": 48.8566, "longitude": 2.3522, "location": "Paris"}
        ]
        
        for loc_data in international_locations:
            location = {"latitude": loc_data["latitude"], "longitude": loc_data["longitude"]}
            response = await self.make_request('POST', '/language/detect', location)
            
            if response['status_code'] == 200:
                detected_lang = response['data'].get('detected_language', 'en')
                confidence = response['data'].get('confidence', 0)
                self.log_test_result(f"Streema Support - {loc_data['location']} Detection", True, 
                                   f"Location detected language: {detected_lang}, Confidence: {confidence:.2f}", 
                                   response['response_time'])
            else:
                self.log_test_result(f"Streema Support - {loc_data['location']} Detection", False, 
                                   f"Status: {response['status_code']}")
        
        # Test supported languages endpoint
        response = await self.make_request('GET', '/languages')
        if response['status_code'] == 200 and 'languages' in response['data']:
            lang_count = len(response['data']['languages'])
            supported_countries = response['data'].get('supported_countries', [])
            self.log_test_result("Integration Support - Supported Languages", True, 
                               f"{lang_count} languages, Countries: {supported_countries}", 
                               response['response_time'])
        else:
            self.log_test_result("Integration Support - Supported Languages", False, 
                               f"Status: {response['status_code']}")
    
    async def test_error_validation_and_fallbacks(self):
        """Test error validation and fallback handling - MEDIUM PRIORITY"""
        print("\n⚠️ TESTING ERROR VALIDATION & FALLBACK HANDLING (MEDIUM PRIORITY)")
        print("=" * 70)
        
        # Test invalid coordinates fallback
        invalid_location = {"latitude": 999, "longitude": 999}
        response = await self.make_request('POST', '/language/detect', invalid_location)
        
        if response['status_code'] == 200:
            detected_lang = response['data'].get('detected_language', '')
            if detected_lang == 'en':
                self.log_test_result("Error Handling - Invalid Coordinates Fallback", True, 
                                   f"Invalid coordinates fallback to English: {detected_lang}", 
                                   response['response_time'])
            else:
                self.log_test_result("Error Handling - Invalid Coordinates Fallback", False, 
                                   f"Expected 'en' fallback, got: {detected_lang}")
        else:
            self.log_test_result("Error Handling - Invalid Coordinates Fallback", False, 
                               f"Status: {response['status_code']}")
        
        # Test malformed request handling for personalized content
        malformed_request = {"invalid": "data"}
        response = await self.make_request('POST', '/personalized-content/multilingual', malformed_request)
        
        if response['status_code'] == 422:
            self.log_test_result("Error Handling - Malformed Request Validation", True, 
                               "422 validation error returned for malformed request", 
                               response['response_time'])
        else:
            self.log_test_result("Error Handling - Malformed Request Validation", False, 
                               f"Expected 422, got: {response['status_code']}")
        
        # Test missing location in personalized content request
        missing_location_request = {
            "preferences": {
                "offline_mode": False,
                "preferred_language": "en"
            }
        }
        response = await self.make_request('POST', '/personalized-content/multilingual', missing_location_request)
        
        if response['status_code'] == 422:
            self.log_test_result("Error Handling - Missing Location Validation", True, 
                               "422 validation error returned for missing location", 
                               response['response_time'])
        else:
            self.log_test_result("Error Handling - Missing Location Validation", False, 
                               f"Expected 422, got: {response['status_code']}")
        
        # Test non-existent endpoint
        response = await self.make_request('GET', '/non-existent-endpoint')
        if response['status_code'] == 404:
            self.log_test_result("Error Handling - Non-existent Endpoint", True, 
                               "404 error returned for non-existent endpoint", 
                               response['response_time'])
        else:
            self.log_test_result("Error Handling - Non-existent Endpoint", False, 
                               f"Expected 404, got: {response['status_code']}")
    
    async def test_radio_streaming_stability(self):
        """Test radio streaming functionality remains stable"""
        print("\n📻 TESTING RADIO STREAMING STABILITY")
        print("=" * 70)
        
        # Test basic endpoints
        endpoints = [
            ('GET', '/', 'API Root'),
            ('GET', '/station-info', 'Basic Station Info'),
            ('GET', '/radio/streams', 'Radio Streams'),
            ('GET', '/radio/stations', 'Radio Stations')
        ]
        
        for method, endpoint, name in endpoints:
            response = await self.make_request(method, endpoint)
            if response['status_code'] == 200:
                self.log_test_result(f"Radio Streaming - {name}", True, 
                                   f"Status: {response['status_code']}", 
                                   response['response_time'])
            else:
                self.log_test_result(f"Radio Streaming - {name}", False, 
                                   f"Status: {response['status_code']}")
        
        # Test stream URL accessibility
        response = await self.make_request('GET', '/radio/streams')
        if response['status_code'] == 200:
            data = response['data']
            main_stream_url = data.get('main_station', {}).get('streamUrl')
            if main_stream_url:
                # Test stream accessibility
                try:
                    async with self.session.head(main_stream_url) as stream_response:
                        if stream_response.status == 200:
                            content_type = stream_response.headers.get('content-type', '')
                            self.log_test_result("Radio Streaming - Main Stream Accessibility", True, 
                                               f"Stream accessible, Content-Type: {content_type}")
                        else:
                            self.log_test_result("Radio Streaming - Main Stream Accessibility", False, 
                                               f"Stream returned status: {stream_response.status}")
                except Exception as e:
                    self.log_test_result("Radio Streaming - Main Stream Accessibility", False, 
                                       f"Stream access error: {str(e)}")
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend API format tests"""
        print("🚀 STARTING CRITICAL BACKEND API REQUEST FORMAT TESTING")
        print(f"🔗 Testing Backend URL: {self.api_url}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all test suites in priority order
            await self.test_personalized_content_api_fixes()  # HIGH PRIORITY
            await self.test_voice_ai_service_fixes()  # HIGH PRIORITY
            await self.test_integration_support_endpoints()  # MEDIUM PRIORITY
            await self.test_error_validation_and_fallbacks()  # MEDIUM PRIORITY
            await self.test_radio_streaming_stability()  # Stability check
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 CRITICAL BACKEND API REQUEST FORMAT TESTING RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"✅ PASSED: {self.passed_tests}/{self.total_tests} tests")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        # Compare with previous results
        previous_rate = 67.5
        target_rate = 85.0
        
        if success_rate >= target_rate:
            print(f"🎉 EXCELLENT: Success rate {success_rate:.1f}% EXCEEDS target of {target_rate}%!")
            print(f"✅ IMPROVEMENT: +{success_rate - previous_rate:.1f}% from previous {previous_rate}%")
        elif success_rate > previous_rate:
            print(f"✅ GOOD: Success rate {success_rate:.1f}% improved from previous {previous_rate}%")
            print(f"📈 PROGRESS: +{success_rate - previous_rate:.1f}% improvement, target: {target_rate}%")
        else:
            print(f"⚠️ NEEDS ATTENTION: Success rate {success_rate:.1f}% not improved from {previous_rate}%")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(result)
        
        # Identify critical failures
        failed_tests = [result for result in self.test_results if "❌ FAIL" in result]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for failed_test in failed_tests:
                print(f"   {failed_test}")
        
        return success_rate

async def main():
    """Main test execution function"""
    tester = BackendAPIFormatTester()
    success_rate = await tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if success_rate >= 85:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs attention

if __name__ == "__main__":
    asyncio.run(main())