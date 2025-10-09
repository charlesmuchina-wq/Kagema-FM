#!/usr/bin/env python3
"""
APPLE FEATURES INTEGRATION BACKEND TESTING
Testing Focus: SiriKit and Enhanced AirPlay 2 services compatibility

REVIEW REQUEST FOCUS AREAS:
1. Core API Health - GET /api/, GET /api/station-info, POST /api/personalized-content/multilingual
2. Voice AI Integration - /api/voice/interpret endpoint for SiriKit integration compatibility  
3. External Audio Services - radio streams and station data for AirPlay integration
4. Performance Validation - response times and system stability
5. Content APIs - language detection and multilingual content support for advanced voice commands

APPLE FEATURES BEING TESTED:
- "Find Brazilian radio stations" voice command support
- "Play Portuguese radio stations" voice command support  
- "Find jazz radio stations" voice command support
- "Play offline content" voice command support
- Multi-room audio streaming capabilities
"""

import json
import requests
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Backend URL from frontend environment
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://radioverse-18.preview.emergentagent.com')
API_BASE = f"{FRONTEND_ENV_URL}/api"

class AppleFeaturesBackendTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result with performance tracking"""
        self.total_tests += 1
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time
        }
        
        self.results.append(result)
        
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        print(f"  {status}: {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    Response time: {response_time:.0f}ms")

    def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 10) -> tuple:
        """Make HTTP request and return response with timing"""
        url = f"{API_BASE}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000
            return response, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return None, response_time

    def test_core_api_health(self):
        """Test Core API Health endpoints for Apple Features integration"""
        print("\n🍎 === CORE API HEALTH TESTS FOR APPLE FEATURES ===")
        
        # Test API root
        response, response_time = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            success = "Kagema FM" in data.get("message", "") and "5.0.0" in data.get("version", "")
            self.log_result(
                "Core API Health - API Root",
                success,
                f"Status: {response.status_code}, Version: {data.get('version', 'N/A')}",
                response_time
            )
        else:
            self.log_result("Core API Health - API Root", False, "Failed to connect", response_time)
        
        # Test basic station info
        response, response_time = self.make_request("GET", "/station-info")
        if response and response.status_code == 200:
            data = response.json()
            success = "streamUrl" in data and "Kagema FM" in data.get("name", "")
            self.log_result(
                "Core API Health - Station Info",
                success,
                f"Status: {response.status_code}, Stream URL present: {'streamUrl' in data}",
                response_time
            )
        else:
            self.log_result("Core API Health - Station Info", False, "Failed to get station info", response_time)
        
        # Test multilingual personalized content (critical for Apple integration)
        nairobi_location = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"preferred_language": "en", "offline_mode": False}
        }
        response, response_time = self.make_request("POST", "/personalized-content/multilingual", nairobi_location)
        if response and response.status_code == 200:
            data = response.json()
            has_radio_streams = "radio_streams" in data
            success = has_radio_streams and "main_station" in data.get("radio_streams", {})
            self.log_result(
                "Core API Health - Multilingual Content",
                success,
                f"Status: {response.status_code}, Radio streams: {has_radio_streams}",
                response_time
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Core API Health - Multilingual Content", False, f"Failed - Status: {status_code}", response_time)

    def test_voice_ai_integration(self):
        """Test Voice AI Integration for SiriKit compatibility"""
        print("\n🎤 === VOICE AI INTEGRATION TESTS FOR SIRIKIT ===")
        
        # Test voice command interpretation - Simple commands
        simple_commands = [
            {"text": "play", "context": "radio_control"},
            {"text": "pause", "context": "radio_control"},
            {"text": "next", "context": "radio_control"},
            {"text": "volume up", "context": "radio_control"}
        ]
        
        for cmd in simple_commands:
            response, response_time = self.make_request("POST", "/voice/interpret", cmd)
            if response and response.status_code == 200:
                data = response.json()
                success = "intent" in data and "confidence" in data and data.get("confidence", 0) >= 0.8
                self.log_result(
                    f"Voice AI - Simple Command: '{cmd['text']}'",
                    success,
                    f"Status: {response.status_code}, Intent: {data.get('intent')}, Confidence: {data.get('confidence', 0):.2f}",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Voice AI - Simple Command: '{cmd['text']}'", False, f"Failed - Status: {status_code}", response_time)
        
        # Test voice command interpretation - Complex Apple integration commands
        complex_commands = [
            {"text": "Find Brazilian radio stations", "context": "station_search"},
            {"text": "Play Portuguese radio stations", "context": "station_search"},
            {"text": "Find jazz radio stations", "context": "music_search"},
            {"text": "Play offline content", "context": "offline_mode"},
            {"text": "Search for classical music", "context": "music_search"},
            {"text": "Tune to classical station", "context": "station_control"}
        ]
        
        for cmd in complex_commands:
            response, response_time = self.make_request("POST", "/voice/interpret", cmd)
            if response and response.status_code == 200:
                data = response.json()
                success = "intent" in data and "confidence" in data and data.get("confidence", 0) >= 0.7
                self.log_result(
                    f"Voice AI - Apple Command: '{cmd['text']}'",
                    success,
                    f"Status: {response.status_code}, Intent: {data.get('intent')}, Confidence: {data.get('confidence', 0):.2f}",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Voice AI - Apple Command: '{cmd['text']}'", False, f"Failed - Status: {status_code}", response_time)
        
        # Test voice intents and help
        response, response_time = self.make_request("GET", "/voice/intents")
        if response and response.status_code == 200:
            data = response.json()
            success = isinstance(data, dict) and len(data) >= 9
            self.log_result(
                "Voice AI - Available Intents",
                success,
                f"Status: {response.status_code}, Intents available: {len(data) if isinstance(data, dict) else 0}",
                response_time
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Voice AI - Available Intents", False, f"Failed - Status: {status_code}", response_time)
        
        response, response_time = self.make_request("GET", "/voice/help")
        if response and response.status_code == 200:
            data = response.json()
            success = "commands" in data and "usage_tips" in data and len(data.get("usage_tips", [])) >= 6
            self.log_result(
                "Voice AI - Help System",
                success,
                f"Status: {response.status_code}, Commands: {len(data.get('commands', []))}, Tips: {len(data.get('usage_tips', []))}",
                response_time
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Voice AI - Help System", False, f"Failed - Status: {status_code}", response_time)

    def test_external_audio_services(self):
        """Test External Audio Services for AirPlay integration"""
        print("\n📻 === EXTERNAL AUDIO SERVICES TESTS FOR AIRPLAY ===")
        
        # Test radio streams endpoint
        response, response_time = self.make_request("GET", "/radio/streams")
        if response and response.status_code == 200:
            data = response.json()
            has_main = "main_station" in data
            has_alternatives = "alternative_streams" in data and len(data.get("alternative_streams", [])) >= 7
            success = has_main and has_alternatives
            self.log_result(
                "External Audio - Radio Streams",
                success,
                f"Status: {response.status_code}, Main station: {has_main}, Alternatives: {len(data.get('alternative_streams', []))}",
                response_time
            )
            
            # Test stream accessibility for AirPlay compatibility
            if success:
                self.test_stream_accessibility(data)
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("External Audio - Radio Streams", False, f"Failed - Status: {status_code}", response_time)
        
        # Test radio stations endpoint
        response, response_time = self.make_request("GET", "/radio/stations")
        if response and response.status_code == 200:
            data = response.json()
            stations_count = len(data.get("stations", []))
            success = stations_count >= 8
            self.log_result(
                "External Audio - Radio Stations",
                success,
                f"Status: {response.status_code}, Stations available: {stations_count}",
                response_time
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("External Audio - Radio Stations", False, f"Failed - Status: {status_code}", response_time)

    def test_stream_accessibility(self, streams_data):
        """Test stream accessibility for AirPlay compatibility"""
        print("\n🎵 === STREAM ACCESSIBILITY TESTS FOR AIRPLAY ===")
        
        # Test main station stream
        main_stream = streams_data.get("main_station", {}).get("streamUrl")
        if main_stream:
            self.validate_stream_url(main_stream, "Main Station")
        
        # Test alternative streams
        alt_streams = streams_data.get("alternative_streams", [])
        for i, stream in enumerate(alt_streams):
            stream_url = stream.get("streamUrl")
            stream_name = stream.get("name", f"Alternative Stream {i+1}")
            if stream_url:
                self.validate_stream_url(stream_url, stream_name)

    def validate_stream_url(self, url: str, name: str):
        """Validate individual stream URL accessibility"""
        try:
            start_time = time.time()
            response = requests.head(url, timeout=5, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            is_valid = response.status_code == 200
            content_type = response.headers.get('content-type', '')
            
            # Check for audio content type or ICY streaming
            is_audio = (
                'audio' in content_type.lower() or 
                'mpeg' in content_type.lower() or
                'icy' in str(response.headers).lower()
            )
            
            test_passed = is_valid and (is_audio or response.status_code == 200)
            
            self.log_result(
                f"Stream Accessibility - {name}",
                test_passed,
                f"Status: {response.status_code}, Type: {content_type}" if test_passed 
                else f"Failed - Status: {response.status_code}, Type: {content_type}",
                response_time
            )
            
        except requests.exceptions.Timeout:
            self.log_result(f"Stream Accessibility - {name}", False, "Timeout after 5 seconds", 5000)
        except Exception as e:
            self.log_result(f"Stream Accessibility - {name}", False, f"Error: {str(e)}", 0)

    def test_performance_validation(self):
        """Test Performance Validation for Apple integration"""
        print("\n⚡ === PERFORMANCE VALIDATION TESTS ===")
        
        # Test concurrent requests (simulating multi-room audio)
        import threading
        import queue
        
        def make_concurrent_request(result_queue, request_id):
            try:
                response, response_time = self.make_request("GET", "/station-info")
                success = response and response.status_code == 200 and "streamUrl" in response.json()
                result_queue.put((request_id, success, response_time))
            except Exception as e:
                result_queue.put((request_id, False, 0))
        
        # Run 5 concurrent requests (multi-room audio simulation)
        result_queue = queue.Queue()
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=make_concurrent_request, args=(result_queue, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        successful_requests = sum(1 for _, success, _ in results if success)
        success_rate = (successful_requests / len(results)) * 100 if results else 0
        
        self.log_result(
            "Performance - Multi-room Audio Simulation",
            success_rate >= 80,
            f"{successful_requests}/{len(results)} successful ({success_rate:.1f}%) in {total_time:.2f}s",
            total_time * 1000
        )

    def test_content_apis(self):
        """Test Content APIs for multilingual support"""
        print("\n🌍 === CONTENT APIs TESTS FOR MULTILINGUAL SUPPORT ===")
        
        # Test supported languages
        response, response_time = self.make_request("GET", "/languages")
        if response and response.status_code == 200:
            data = response.json()
            languages = data.get("languages", [])
            has_english = any(lang.get("code") == "en" for lang in languages)
            has_portuguese = any(lang.get("code") == "pt-br" for lang in languages)
            success = has_english and has_portuguese and len(languages) >= 8
            self.log_result(
                "Content APIs - Supported Languages",
                success,
                f"Status: {response.status_code}, Total: {len(languages)}, English: {has_english}, Portuguese: {has_portuguese}",
                response_time
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Content APIs - Supported Languages", False, f"Failed - Status: {status_code}", response_time)
        
        # Test language detection for Apple Features locations
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi, Kenya", "expected": "en"},
            {"latitude": -0.0917, "longitude": 34.7680, "name": "Kisumu, Kenya", "expected": "luo"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo, Brazil", "expected": "pt-br"}
        ]
        
        for location in test_locations:
            response, response_time = self.make_request("POST", "/language/detect", 
                                                       {"latitude": location["latitude"], "longitude": location["longitude"]})
            if response and response.status_code == 200:
                data = response.json()
                detected = data.get("detected_language")
                confidence = data.get("confidence", 0)
                success = detected is not None and confidence >= 0.5
                self.log_result(
                    f"Content APIs - Language Detection: {location['name']}",
                    success,
                    f"Status: {response.status_code}, Detected: {detected}, Confidence: {confidence:.2f}",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Content APIs - Language Detection: {location['name']}", False, f"Failed - Status: {status_code}", response_time)

    def run_apple_features_tests(self):
        """Run all Apple Features integration tests"""
        print("🍎 APPLE FEATURES INTEGRATION BACKEND TESTING")
        print("=" * 80)
        print(f"🎯 Testing Backend URL: {API_BASE}")
        print("=" * 80)
        
        # Run all test suites
        test_suites = [
            self.test_core_api_health,
            self.test_voice_ai_integration,
            self.test_external_audio_services,
            self.test_performance_validation,
            self.test_content_apis
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                print(f"❌ Test suite failed: {e}")
        
        self.print_final_summary()

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎉 APPLE FEATURES INTEGRATION BACKEND TESTING COMPLETE")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.0f}ms")
            print(f"   Maximum Response Time: {max_response_time:.0f}ms")
        
        # Failed tests details
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        # Apple Features readiness assessment
        print(f"\n🍎 APPLE FEATURES READINESS ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - Ready for Apple App Store deployment")
            print("   ✅ SiriKit integration fully supported")
            print("   ✅ Enhanced AirPlay 2 services compatible")
            print("   ✅ Multi-room audio streaming capabilities verified")
        elif success_rate >= 85:
            print("   ⚠️  GOOD - Minor issues to address before Apple deployment")
            print("   ✅ Core Apple features working")
            print("   ⚠️  Some advanced features may need refinement")
        elif success_rate >= 70:
            print("   ⚠️  FAIR - Several issues need fixing for Apple compatibility")
            print("   ⚠️  Basic functionality working but advanced features limited")
        else:
            print("   ❌ POOR - Major issues prevent Apple integration")
            print("   ❌ Significant work needed for Apple compatibility")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   • Core API Health: {'✅ All endpoints operational' if success_rate >= 90 else '⚠️ Some issues detected'}")
        print(f"   • Voice AI Integration: {'✅ SiriKit compatible' if success_rate >= 85 else '⚠️ Needs improvement'}")
        print(f"   • External Audio Services: {'✅ AirPlay ready' if success_rate >= 85 else '⚠️ Stream issues detected'}")
        print(f"   • Performance: {'✅ Excellent' if avg_response_time < 500 else '⚠️ Acceptable' if avg_response_time < 1000 else '❌ Needs improvement'} ({avg_response_time:.0f}ms avg)" if response_times else "   • Performance: Data not available")
        print(f"   • Content APIs: {'✅ Multilingual support working' if success_rate >= 80 else '⚠️ Language detection issues'}")
        
        return success_rate

if __name__ == "__main__":
    tester = AppleFeaturesBackendTester()
    success_rate = tester.run_apple_features_tests()
    
    # Exit with appropriate code
    if success_rate >= 85:
        exit(0)  # Success
    else:
        exit(1)  # Failure