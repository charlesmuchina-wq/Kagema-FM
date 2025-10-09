#!/usr/bin/env python3
"""
Kagema FM CarPlay/Android Auto Specific Backend Testing
Focus: Car mode functionality and automotive safety requirements
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os

# Get backend URL from frontend env
BACKEND_URL = "https://kagema-fm-audio.preview.emergentagent.com/api"

class CarModeBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.car_mode_tests = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: float = 5.0) -> Dict:
        """Make HTTP request with car mode timing requirements"""
        start_time = time.time()
        
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = (time.time() - start_time) * 1000
                    result = {
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
                    return result
                    
            elif method.upper() == "POST":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = (time.time() - start_time) * 1000
                    result = {
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
                    return result
                    
        except asyncio.TimeoutError:
            return {
                "status_code": 408,
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": "Request timeout",
                "data": None
            }
        except Exception as e:
            return {
                "status_code": 500,
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": str(e),
                "data": None
            }

    def log_test_result(self, test_name: str, success: bool, details: str, response_time: float = 0, priority: str = "medium"):
        """Log test result with car mode specific metrics"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time_ms": response_time,
            "priority": priority,
            "car_mode_compliant": response_time < 200 if response_time > 0 else True,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(result)
            
        # Mark as car mode test if it's safety critical
        if priority == "high" or "voice" in test_name.lower() or "streaming" in test_name.lower():
            self.car_mode_tests.append(result)
            
        status = "✅" if success else "❌"
        timing = f" ({response_time:.0f}ms)" if response_time > 0 else ""
        car_compliant = " 🚗" if response_time < 200 and response_time > 0 else " ⚠️" if response_time >= 200 else ""
        print(f"{status} {test_name}{timing}{car_compliant}: {details}")

    async def test_car_mode_voice_commands(self):
        """Test voice command processing for car mode - HIGH PRIORITY"""
        print("\n🎤 Testing Car Mode Voice Command Processing...")
        
        # Test critical car voice commands
        car_commands = [
            {"text": "play radio", "expected_intent": "play"},
            {"text": "pause music", "expected_intent": "pause"},
            {"text": "next station", "expected_intent": "next"},
            {"text": "tune to jazz station", "expected_intent": "station"},
            {"text": "search for classical music", "expected_intent": "search"},
            {"text": "volume up", "expected_intent": "volume_up"}
        ]
        
        for command in car_commands:
            result = await self.make_request("POST", "/voice/interpret", {
                "text": command["text"],
                "context": "car_mode"
            }, timeout=2.0)  # Car mode requires fast response
            
            if result["status_code"] == 200:
                data = result["data"]
                intent_correct = data.get("intent") == command["expected_intent"]
                confidence_good = data.get("confidence", 0) > 0.5
                
                if intent_correct and confidence_good:
                    self.log_test_result(
                        f"Voice Command: '{command['text']}'",
                        True,
                        f"Intent: {data.get('intent')}, Confidence: {data.get('confidence'):.2f}",
                        result["response_time_ms"],
                        "high"
                    )
                else:
                    self.log_test_result(
                        f"Voice Command: '{command['text']}'",
                        False,
                        f"Expected intent: {command['expected_intent']}, Got: {data.get('intent')}, Confidence: {data.get('confidence', 0):.2f}",
                        result["response_time_ms"],
                        "high"
                    )
            else:
                self.log_test_result(
                    f"Voice Command: '{command['text']}'",
                    False,
                    f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                    result["response_time_ms"],
                    "high"
                )

    async def test_car_mode_radio_streaming(self):
        """Test radio streaming APIs for car mode - HIGH PRIORITY"""
        print("\n📻 Testing Car Mode Radio Streaming...")
        
        # Test basic station info (must be fast for car safety)
        result = await self.make_request("GET", "/station-info", timeout=1.0)
        
        if result["status_code"] == 200:
            data = result["data"]
            has_stream_url = "streamUrl" in data and data["streamUrl"]
            has_station_name = "name" in data and data["name"]
            
            self.log_test_result(
                "Basic Station Info",
                has_stream_url and has_station_name,
                f"Station: {data.get('name', 'N/A')}, Stream: {data.get('streamUrl', 'N/A')[:50]}...",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Basic Station Info",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )
            
        # Test multilingual station info for car location services
        kenya_location = {"latitude": -1.286389, "longitude": 36.817223}  # Nairobi
        result = await self.make_request("POST", "/station-info/multilingual", kenya_location, timeout=1.5)
        
        if result["status_code"] == 200:
            data = result["data"]
            has_stream = "streamUrl" in data
            has_language = "detected_language" in data
            
            self.log_test_result(
                "Car Location-Based Station Info",
                has_stream and has_language,
                f"Language: {data.get('detected_language', 'N/A')}, Stream available: {has_stream}",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Car Location-Based Station Info",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )

    async def test_car_mode_background_audio_service(self):
        """Test background audio service compatibility - HIGH PRIORITY"""
        print("\n🔊 Testing Background Audio Service Compatibility...")
        
        # Test personalized content with radio streams (critical for car audio)
        test_location = {"latitude": -1.286389, "longitude": 36.817223}
        test_preferences = {
            "user_id": "car_mode_user",
            "preferred_language": "en",
            "audio": {
                "quality": "high",
                "volume": 0.8,
                "auto_play": True
            },
            "offline_mode": False,
            "theme": "dark"  # Car mode typically uses dark theme
        }
        
        request_data = {
            "location": test_location,
            "preferences": test_preferences
        }
        
        result = await self.make_request("POST", "/personalized-content/multilingual", request_data, timeout=2.0)
        
        if result["status_code"] == 200:
            data = result["data"]
            has_radio_streams = "radio_streams" in data
            has_main_station = has_radio_streams and "main_station" in data["radio_streams"]
            has_alternatives = has_radio_streams and "alternative_streams" in data["radio_streams"]
            
            stream_count = 0
            if has_alternatives:
                stream_count = len(data["radio_streams"]["alternative_streams"])
                
            self.log_test_result(
                "Background Audio Service Data",
                has_radio_streams and has_main_station,
                f"Main station: {has_main_station}, Alternative streams: {stream_count}",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Background Audio Service Data",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )

    async def test_car_mode_station_switching(self):
        """Test quick station switching for car interface - HIGH PRIORITY"""
        print("\n🔄 Testing Car Mode Station Switching...")
        
        # Test language detection (for regional station switching)
        locations = [
            {"latitude": -1.286389, "longitude": 36.817223, "name": "Nairobi"},
            {"latitude": -0.091702, "longitude": 34.767956, "name": "Kisumu"},
            {"latitude": -1.166667, "longitude": 36.666667, "name": "Kiambu"}
        ]
        
        for location in locations:
            result = await self.make_request("POST", "/language/detect", {
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            }, timeout=1.0)  # Must be fast for car safety
            
            if result["status_code"] == 200:
                data = result["data"]
                has_language = "detected_language" in data
                has_streams = "radio_streams" in data or "regional_stations" in data
                
                self.log_test_result(
                    f"Station Switching - {location['name']}",
                    has_language and has_streams,
                    f"Language: {data.get('detected_language', 'N/A')}, Streams available: {has_streams}",
                    result["response_time_ms"],
                    "high"
                )
            else:
                self.log_test_result(
                    f"Station Switching - {location['name']}",
                    False,
                    f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                    result["response_time_ms"],
                    "high"
                )

    async def test_car_mode_integration_apis(self):
        """Test integration APIs for CarPlay/Android Auto - MEDIUM PRIORITY"""
        print("\n🔗 Testing Car Mode Integration APIs...")
        
        # Test platform integrations
        integrations = ["general", "google_maps", "spotify", "voice_control"]
        
        for integration in integrations:
            result = await self.make_request("POST", "/integrations/initialize", {
                "type": integration,
                "config": {"car_mode": True}
            }, timeout=3.0)
            
            if result["status_code"] == 200:
                data = result["data"]
                initialized = data.get("status") == "initialized"
                
                self.log_test_result(
                    f"Integration: {integration}",
                    initialized,
                    f"Status: {data.get('status', 'N/A')}, Message: {data.get('message', 'N/A')[:50]}...",
                    result["response_time_ms"],
                    "medium"
                )
            else:
                self.log_test_result(
                    f"Integration: {integration}",
                    False,
                    f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                    result["response_time_ms"],
                    "medium"
                )

    async def test_car_mode_performance_safety(self):
        """Test performance and safety requirements for car mode - HIGH PRIORITY"""
        print("\n⚡ Testing Car Mode Performance & Safety...")
        
        # Test API root (basic connectivity)
        result = await self.make_request("GET", "/", timeout=1.0)
        
        if result["status_code"] == 200:
            self.log_test_result(
                "Basic Connectivity",
                True,
                f"API responsive in {result['response_time_ms']:.0f}ms",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Basic Connectivity",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )
            
        # Test voice intents (must be fast for safety)
        result = await self.make_request("GET", "/voice/intents", timeout=1.0)
        
        if result["status_code"] == 200:
            data = result["data"]
            has_intents = isinstance(data, dict) and len(data) > 0
            
            self.log_test_result(
                "Voice Intents Availability",
                has_intents,
                f"Available intents: {len(data) if has_intents else 0}",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Voice Intents Availability",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )
            
        # Test voice help (for car mode assistance)
        result = await self.make_request("GET", "/voice/help", timeout=1.5)
        
        if result["status_code"] == 200:
            data = result["data"]
            has_commands = "commands" in data
            has_tips = "usage_tips" in data
            
            self.log_test_result(
                "Voice Help System",
                has_commands and has_tips,
                f"Commands available: {has_commands}, Usage tips: {has_tips}",
                result["response_time_ms"],
                "high"
            )
        else:
            self.log_test_result(
                "Voice Help System",
                False,
                f"HTTP {result['status_code']}: {result.get('error', 'Unknown error')}",
                result["response_time_ms"],
                "high"
            )

    async def test_stream_accessibility(self):
        """Test radio stream accessibility for car audio - HIGH PRIORITY"""
        print("\n📡 Testing Radio Stream Accessibility...")
        
        # Get stream URLs from personalized content
        test_location = {"latitude": -1.286389, "longitude": 36.817223}
        test_preferences = {
            "user_id": "stream_test_user",
            "preferred_language": "en",
            "audio": {"quality": "high", "volume": 0.8, "auto_play": True},
            "offline_mode": False,
            "theme": "dark"
        }
        
        result = await self.make_request("POST", "/personalized-content/multilingual", {
            "location": test_location,
            "preferences": test_preferences
        }, timeout=3.0)
        
        if result["status_code"] == 200:
            data = result["data"]
            if "radio_streams" in data:
                streams_to_test = []
                
                # Add main station
                if "main_station" in data["radio_streams"]:
                    streams_to_test.append({
                        "name": data["radio_streams"]["main_station"].get("name", "Main Station"),
                        "url": data["radio_streams"]["main_station"].get("streamUrl")
                    })
                
                # Add alternative streams (limit to 3 for car mode testing)
                if "alternative_streams" in data["radio_streams"]:
                    for stream in data["radio_streams"]["alternative_streams"][:3]:
                        streams_to_test.append({
                            "name": stream.get("name", "Unknown"),
                            "url": stream.get("streamUrl")
                        })
                
                # Test stream accessibility
                for stream in streams_to_test:
                    if stream["url"]:
                        try:
                            start_time = time.time()
                            async with self.session.head(stream["url"], timeout=aiohttp.ClientTimeout(total=5.0)) as response:
                                response_time = (time.time() - start_time) * 1000
                                accessible = response.status == 200
                                content_type = response.headers.get('content-type', 'unknown')
                                
                                self.log_test_result(
                                    f"Stream: {stream['name']}",
                                    accessible,
                                    f"Status: {response.status}, Type: {content_type}",
                                    response_time,
                                    "high"
                                )
                        except Exception as e:
                            self.log_test_result(
                                f"Stream: {stream['name']}",
                                False,
                                f"Error: {str(e)}",
                                0,
                                "high"
                            )

    async def run_all_tests(self):
        """Run all car mode backend tests"""
        print("🚗 Starting Kagema FM CarPlay/Android Auto Backend Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # High Priority Tests (Car Safety Critical)
            await self.test_car_mode_performance_safety()
            await self.test_car_mode_voice_commands()
            await self.test_car_mode_radio_streaming()
            await self.test_car_mode_background_audio_service()
            await self.test_car_mode_station_switching()
            await self.test_stream_accessibility()
            
            # Medium Priority Tests (Enhanced Features)
            await self.test_car_mode_integration_apis()
            
        finally:
            await self.cleanup()
            
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary with car mode focus"""
        print("\n" + "=" * 80)
        print("🚗 CAR MODE BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        # Car mode specific metrics
        car_mode_tests = len(self.car_mode_tests)
        car_mode_passed = len([t for t in self.car_mode_tests if t["success"]])
        
        # Performance metrics (car safety critical)
        fast_responses = len([t for t in self.test_results if t["response_time_ms"] > 0 and t["response_time_ms"] < 200])
        slow_responses = len([t for t in self.test_results if t["response_time_ms"] >= 200])
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        print(f"\n🚗 CAR MODE CRITICAL TESTS:")
        print(f"   Car Mode Tests: {car_mode_tests}")
        print(f"   Car Mode Passed: {car_mode_passed} ({car_mode_passed/car_mode_tests*100:.1f}% if car_mode_tests > 0 else 0)")
        
        print(f"\n⚡ PERFORMANCE (Car Safety Critical):")
        print(f"   Fast Responses (<200ms): {fast_responses}")
        print(f"   Slow Responses (≥200ms): {slow_responses}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                priority_icon = "🔴" if test["priority"] == "high" else "🟡"
                timing = f" ({test['response_time_ms']:.0f}ms)" if test["response_time_ms"] > 0 else ""
                print(f"   {priority_icon} {test['test_name']}{timing}: {test['details']}")
        
        # Car mode readiness assessment
        high_priority_tests = [t for t in self.test_results if t["priority"] == "high"]
        high_priority_passed = [t for t in high_priority_tests if t["success"]]
        
        car_mode_ready = len(high_priority_passed) / len(high_priority_tests) >= 0.8 if high_priority_tests else False
        
        print(f"\n🎯 CAR MODE READINESS:")
        if car_mode_ready:
            print("   ✅ READY FOR CAR MODE DEPLOYMENT")
            print("   - High priority tests: 80%+ success rate")
            print("   - Voice commands functional")
            print("   - Radio streaming operational")
        else:
            print("   ❌ NOT READY FOR CAR MODE DEPLOYMENT")
            print("   - Critical issues found in high priority tests")
            print("   - Voice commands or streaming may be impaired")
            
        print("\n" + "=" * 80)

async def main():
    """Main test execution"""
    tester = CarModeBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())