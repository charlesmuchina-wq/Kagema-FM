#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Kagema FM
Tests all major API endpoints and functionality per review request:
- Core API Endpoints
- Voice AI Service (/api/voice/interpret)
- Radio Streaming endpoints
- Error Handling
- Performance
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://fm-car-mode.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class KagemaFMBackendTester:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_time': response_time
        }
        self.results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
            
        print(f"{status} {test_name}: {details} ({response_time:.0f}ms)")
    
    def test_basic_connectivity(self) -> bool:
        """Test basic backend connectivity"""
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Basic Connectivity",
                        True,
                        f"Backend responsive: {data.get('message', 'Unknown')}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Basic Connectivity",
                        False,
                        f"Unexpected response: {data}",
                        response_time
                    )
                    return False
            else:
                self.log_result(
                    "Basic Connectivity",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result("Basic Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_core_radio_endpoints(self):
        """Test core radio streaming endpoints - Focus area from review request"""
        print("\n🎵 Testing Core Radio Endpoints...")
        
        # Test basic station info
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/station-info")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "streamUrl" in data and data["streamUrl"]:
                    self.log_result(
                        "GET /api/station-info", 
                        True, 
                        f"Station info with stream URL: {data['streamUrl'][:50]}...", 
                        response_time
                    )
                else:
                    self.log_result("GET /api/station-info", False, "Missing streamUrl in response", response_time)
            else:
                self.log_result("GET /api/station-info", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("GET /api/station-info", False, f"Request failed: {str(e)}")
        
        # Test multilingual station info
        try:
            start_time = time.time()
            payload = {"latitude": -1.286389, "longitude": 36.817223}  # Nairobi coordinates
            response = self.session.post(f"{API_BASE}/station-info/multilingual", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "streamUrl" in data and "detected_language" in data:
                    self.log_result(
                        "POST /api/station-info/multilingual", 
                        True, 
                        f"Language: {data['detected_language']}, Stream: {data['streamUrl'][:50]}...", 
                        response_time
                    )
                else:
                    self.log_result("POST /api/station-info/multilingual", False, "Missing required fields", response_time)
            else:
                self.log_result("POST /api/station-info/multilingual", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("POST /api/station-info/multilingual", False, f"Request failed: {str(e)}")
        
        # Test personalized content with radio streams - CRITICAL for frontend
        try:
            start_time = time.time()
            payload = {
                "latitude": -1.286389, 
                "longitude": 36.817223,
                "preferred_language": "en",
                "offline_mode": False,
                "theme": "dark",
                "notifications": {"enabled": True},
                "audio": {"quality": "high", "volume": 0.8}
            }
            response = self.session.post(f"{API_BASE}/personalized-content/multilingual", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "radio_streams" in data and "main_station" in data["radio_streams"]:
                    stream_count = len(data["radio_streams"].get("alternative_streams", []))
                    self.log_result(
                        "POST /api/personalized-content/multilingual", 
                        True, 
                        f"Radio streams data with {stream_count} alternatives - CRITICAL for frontend", 
                        response_time
                    )
                else:
                    self.log_result("POST /api/personalized-content/multilingual", False, "Missing radio_streams data", response_time)
            else:
                self.log_result("POST /api/personalized-content/multilingual", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("POST /api/personalized-content/multilingual", False, f"Request failed: {str(e)}")
    
    def test_radio_streaming_accessibility(self):
        """Test radio streaming URLs accessibility - Focus area from review request"""
        print("\n📡 Testing Radio Stream Accessibility...")
        
        # Get stream URLs from personalized content
        try:
            payload = {
                "latitude": -1.286389, 
                "longitude": 36.817223,
                "preferred_language": "en",
                "offline_mode": False,
                "theme": "dark",
                "notifications": {"enabled": True},
                "audio": {"quality": "high", "volume": 0.8}
            }
            response = self.session.post(f"{API_BASE}/personalized-content/multilingual", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                radio_streams = data.get("radio_streams", {})
                
                # Test main station stream
                main_station = radio_streams.get("main_station", {})
                if main_station.get("streamUrl"):
                    self.test_stream_url(main_station["streamUrl"], "Main Kagema FM Stream")
                
                # Test alternative streams
                alternative_streams = radio_streams.get("alternative_streams", [])
                for i, stream in enumerate(alternative_streams[:6]):  # Test first 6 alternatives
                    if stream.get("streamUrl"):
                        self.test_stream_url(stream["streamUrl"], f"Alternative Stream {i+1}: {stream.get('name', 'Unknown')}")
            
        except Exception as e:
            self.log_result("Radio Stream URL Retrieval", False, f"Failed to get stream URLs: {str(e)}")
    
    def test_stream_url(self, stream_url: str, stream_name: str):
        """Test individual stream URL accessibility"""
        try:
            start_time = time.time()
            response = requests.head(stream_url, timeout=10, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                icy_headers = [h for h in response.headers.keys() if h.lower().startswith('icy-')]
                self.log_result(
                    f"Stream: {stream_name}", 
                    True, 
                    f"Accessible ({content_type}, {len(icy_headers)} ICY headers)", 
                    response_time
                )
            else:
                self.log_result(f"Stream: {stream_name}", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result(f"Stream: {stream_name}", False, f"Stream test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling - Focus area from review request"""
        print("\n🚨 Testing Error Handling...")
        
        # Test invalid endpoints
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/nonexistent-endpoint")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 404:
                self.log_result("404 Error Handling", True, "Properly returns 404 for invalid endpoints", response_time)
            else:
                self.log_result("404 Error Handling", False, f"Expected 404, got {response.status_code}", response_time)
        except Exception as e:
            self.log_result("404 Error Handling", False, f"Request failed: {str(e)}")
        
        # Test invalid JSON payload
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/language/detect", json={"invalid": "data"})
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [400, 422]:
                self.log_result("Invalid JSON Handling", True, f"Properly returns {response.status_code} for invalid data", response_time)
            else:
                self.log_result("Invalid JSON Handling", False, f"Expected 400/422, got {response.status_code}", response_time)
        except Exception as e:
            self.log_result("Invalid JSON Handling", False, f"Request failed: {str(e)}")
    
    def test_performance_metrics(self):
        """Test performance - Focus area from review request"""
        print("\n⚡ Testing Performance...")
        
        # Calculate average response times
        if self.results:
            response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                # Performance thresholds
                if avg_time < 2000:  # Under 2 seconds average
                    self.log_result(
                        "Average Response Time", 
                        True, 
                        f"Excellent: {avg_time:.0f}ms avg (min: {min_time:.0f}ms, max: {max_time:.0f}ms)"
                    )
                elif avg_time < 5000:  # Under 5 seconds average
                    self.log_result(
                        "Average Response Time", 
                        True, 
                        f"Acceptable: {avg_time:.0f}ms avg (min: {min_time:.0f}ms, max: {max_time:.0f}ms)"
                    )
                else:
                    self.log_result(
                        "Average Response Time", 
                        False, 
                        f"Slow: {avg_time:.0f}ms avg (min: {min_time:.0f}ms, max: {max_time:.0f}ms)"
                    )

    def test_voice_ai_service(self):
        """Test Voice AI Service endpoints - Focus area from review request"""
        print("\n🎤 Testing Voice AI Service...")
        
        # Test voice command interpretation with various commands
        test_commands = [
            {"text": "play music", "expected_intent": "play"},
            {"text": "pause", "expected_intent": "pause"},
            {"text": "next station", "expected_intent": "next"},
            {"text": "search for jazz music", "expected_intent": "search"},
            {"text": "tune to classical station", "expected_intent": "station"},
            {"text": "I want to listen to relaxing ambient music", "expected_intent": "search"}
        ]
        
        for cmd in test_commands:
            try:
                start_time = time.time()
                payload = {"text": cmd["text"]}
                response = self.session.post(f"{API_BASE}/voice/interpret", json=payload)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if "intent" in data and "confidence" in data:
                        confidence = data["confidence"]
                        intent = data["intent"]
                        self.log_result(
                            f"Voice Command: '{cmd['text']}'", 
                            True, 
                            f"Intent: {intent}, Confidence: {confidence:.2f}", 
                            response_time
                        )
                    else:
                        self.log_result(f"Voice Command: '{cmd['text']}'", False, "Missing intent/confidence", response_time)
                else:
                    self.log_result(f"Voice Command: '{cmd['text']}'", False, f"HTTP {response.status_code}", response_time)
            except Exception as e:
                self.log_result(f"Voice Command: '{cmd['text']}'", False, f"Request failed: {str(e)}")
        
        # Test voice intents endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/intents")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                intent_count = len(data) if isinstance(data, dict) else 0
                self.log_result(
                    "GET /api/voice/intents", 
                    True, 
                    f"Retrieved {intent_count} available voice intents", 
                    response_time
                )
            else:
                self.log_result("GET /api/voice/intents", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("GET /api/voice/intents", False, f"Request failed: {str(e)}")
        
        # Test voice help endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/help")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "commands" in data and "usage_tips" in data:
                    tip_count = len(data.get("usage_tips", []))
                    self.log_result(
                        "GET /api/voice/help", 
                        True, 
                        f"Voice help with {tip_count} usage tips", 
                        response_time
                    )
                else:
                    self.log_result("GET /api/voice/help", False, "Missing commands/usage_tips", response_time)
            else:
                self.log_result("GET /api/voice/help", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("GET /api/voice/help", False, f"Request failed: {str(e)}")

    def test_additional_endpoints(self):
        """Test additional backend endpoints"""
        print("\n🔧 Testing Additional Endpoints...")
        
        # Test language detection
        try:
            start_time = time.time()
            payload = {"latitude": -1.286389, "longitude": 36.817223}  # Nairobi
            response = self.session.post(f"{API_BASE}/language/detect", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "detected_language" in data:
                    lang = data["detected_language"]
                    confidence = data.get("confidence", 0)
                    self.log_result(
                        "POST /api/language/detect", 
                        True, 
                        f"Detected: {lang} (confidence: {confidence})", 
                        response_time
                    )
                else:
                    self.log_result("POST /api/language/detect", False, "Missing detected_language", response_time)
            else:
                self.log_result("POST /api/language/detect", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("POST /api/language/detect", False, f"Request failed: {str(e)}")
        
        # Test supported languages
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/languages")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "languages" in data:
                    lang_count = len(data["languages"])
                    self.log_result(
                        "GET /api/languages", 
                        True, 
                        f"Retrieved {lang_count} supported languages", 
                        response_time
                    )
                else:
                    self.log_result("GET /api/languages", False, "Missing languages field", response_time)
            else:
                self.log_result("GET /api/languages", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("GET /api/languages", False, f"Request failed: {str(e)}")
        
        # Test satellite status
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/satellite/status")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "connection_type" in data:
                    conn_type = data["connection_type"]
                    signal = data.get("signal_strength", "unknown")
                    self.log_result(
                        "GET /api/satellite/status", 
                        True, 
                        f"Connection: {conn_type}, Signal: {signal}", 
                        response_time
                    )
                else:
                    self.log_result("GET /api/satellite/status", False, "Missing connection info", response_time)
            else:
                self.log_result("GET /api/satellite/status", False, f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("GET /api/satellite/status", False, f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all voice command processing tests"""
        print("🎤 VOICE COMMAND PROCESSING TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test basic connectivity first
        connectivity_ok = self.test_backend_connectivity()
        if not connectivity_ok:
            print("❌ Backend connectivity failed - aborting tests")
            return
        
        print("\n📋 TESTING VOICE AI ENDPOINTS")
        print("-" * 50)
        
        # Test voice endpoints
        interpret_ok = self.test_voice_interpret_endpoint()
        intents_ok = self.test_voice_intents_endpoint()
        help_ok = self.test_voice_help_endpoint()
        
        print("\n🎯 TESTING SIMPLE PATTERN MATCHING COMMANDS (Should get >0.9 confidence)")
        print("-" * 70)
        
        # Test simple commands that should use pattern matching
        simple_results = self.test_simple_pattern_matching_commands()
        
        print("\n🧠 TESTING COMPLEX AI PROCESSING COMMANDS")
        print("-" * 50)
        
        # Test complex commands that should use AI
        complex_results = self.test_complex_ai_commands()
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Specific statistics for voice command processing
        simple_commands_passed = sum(1 for cmd, success in simple_results.items() if success)
        simple_commands_total = len(simple_results)
        simple_success_rate = (simple_commands_passed / simple_commands_total * 100) if simple_commands_total > 0 else 0
        
        complex_commands_passed = sum(1 for cmd, success in complex_results.items() if success)
        complex_commands_total = len(complex_results)
        complex_success_rate = (complex_commands_passed / complex_commands_total * 100) if complex_commands_total > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎤 VOICE COMMAND PROCESSING TEST SUMMARY")
        print("=" * 80)
        print(f"Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Simple Pattern Matching Commands: {simple_commands_passed}/{simple_commands_total} ({simple_success_rate:.1f}%)")
        print(f"Complex AI Processing Commands: {complex_commands_passed}/{complex_commands_total} ({complex_success_rate:.1f}%)")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']} {result['test']}: {result['details']} ({result['response_time']})")
        
        # Critical findings
        print("\n🔍 CRITICAL FINDINGS:")
        
        if simple_success_rate < 100:
            failed_simple = [cmd for cmd, success in simple_results.items() if not success]
            print(f"❌ SIMPLE COMMANDS FAILING: {failed_simple}")
            print("   These should use pattern matching with >0.9 confidence for car mode safety")
        else:
            print("✅ ALL SIMPLE COMMANDS WORKING with high confidence pattern matching")
        
        if complex_success_rate < 100:
            failed_complex = [cmd for cmd, success in complex_results.items() if not success]
            print(f"❌ COMPLEX COMMANDS FAILING: {len(failed_complex)} commands")
            print("   These should use AI processing with good parameter extraction")
        else:
            print("✅ ALL COMPLEX COMMANDS WORKING with AI processing")
        
        # Voice AI endpoints status
        endpoints_working = interpret_ok and intents_ok and help_ok
        if endpoints_working:
            print("✅ ALL VOICE AI ENDPOINTS WORKING")
        else:
            failed_endpoints = []
            if not interpret_ok: failed_endpoints.append("interpret")
            if not intents_ok: failed_endpoints.append("intents") 
            if not help_ok: failed_endpoints.append("help")
            print(f"❌ VOICE AI ENDPOINTS FAILING: {failed_endpoints}")
        
        print("=" * 80)
        
        return {
            "overall_success_rate": success_rate,
            "simple_commands_success_rate": simple_success_rate,
            "complex_commands_success_rate": complex_success_rate,
            "endpoints_working": endpoints_working,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "simple_results": simple_results,
            "complex_results": complex_results
        }

def main():
    """Main test execution"""
    tester = VoiceCommandTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["overall_success_rate"] >= 80:  # 80% threshold for acceptable performance
        print(f"\n✅ VOICE COMMAND PROCESSING TESTS PASSED ({results['overall_success_rate']:.1f}% success rate)")
        return 0
    else:
        print(f"\n❌ VOICE COMMAND PROCESSING TESTS FAILED ({results['overall_success_rate']:.1f}% success rate)")
        return 1

if __name__ == "__main__":
    exit(main())