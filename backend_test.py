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

    def test_voice_interpret_endpoint(self) -> bool:
        """Test POST /api/voice/interpret endpoint"""
        try:
            start_time = time.time()
            
            # Test simple command that should use pattern matching
            test_data = {
                "text": "pause",
                "context": "radio_control"
            }
            
            response = self.session.post(f"{API_BASE}/voice/interpret", json=test_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['intent', 'parameters', 'confidence', 'explanation']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Voice Interpret Endpoint",
                        True,
                        f"Endpoint working, returned intent: {data['intent']}, confidence: {data['confidence']:.2f}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Voice Interpret Endpoint",
                        False,
                        f"Missing required fields in response: {data}",
                        response_time
                    )
                    return False
            else:
                self.log_result(
                    "Voice Interpret Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result("Voice Interpret Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_simple_pattern_matching_commands(self) -> Dict[str, bool]:
        """Test simple commands that should use pattern matching with high confidence (>0.9)"""
        simple_commands = [
            {"text": "pause", "expected_intent": "pause"},
            {"text": "next", "expected_intent": "next"},
            {"text": "volume up", "expected_intent": "volume_up"},
            {"text": "play", "expected_intent": "play"}
        ]
        
        results = {}
        
        for cmd in simple_commands:
            try:
                start_time = time.time()
                
                test_data = {
                    "text": cmd["text"],
                    "context": "radio_control"
                }
                
                response = self.session.post(f"{API_BASE}/voice/interpret", json=test_data)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    intent = data.get('intent')
                    confidence = data.get('confidence', 0)
                    explanation = data.get('explanation', '')
                    
                    # Check if intent matches expected
                    intent_correct = intent == cmd["expected_intent"]
                    
                    # Check if confidence is high (>0.9) for pattern matching
                    high_confidence = confidence > 0.9
                    
                    # Check if it used pattern matching (not AI)
                    used_pattern_matching = "pattern" in explanation.lower() or "matched" in explanation.lower()
                    
                    success = intent_correct and high_confidence
                    
                    details = f"Command '{cmd['text']}' -> Intent: {intent} (expected: {cmd['expected_intent']}), Confidence: {confidence:.2f}, Method: {'Pattern' if used_pattern_matching else 'AI'}"
                    
                    if success:
                        details += " - HIGH CONFIDENCE PATTERN MATCHING ✅"
                    elif intent_correct and not high_confidence:
                        details += f" - CORRECT INTENT BUT LOW CONFIDENCE ({confidence:.2f}) ⚠️"
                    elif not intent_correct:
                        details += " - WRONG INTENT ❌"
                    
                    self.log_result(
                        f"Simple Command: {cmd['text']}",
                        success,
                        details,
                        response_time
                    )
                    
                    results[cmd["text"]] = success
                else:
                    self.log_result(
                        f"Simple Command: {cmd['text']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}",
                        response_time
                    )
                    results[cmd["text"]] = False
                    
            except Exception as e:
                self.log_result(f"Simple Command: {cmd['text']}", False, f"Exception: {str(e)}")
                results[cmd["text"]] = False
        
        return results

    def test_complex_ai_commands(self) -> Dict[str, bool]:
        """Test complex commands that should use AI processing"""
        complex_commands = [
            {
                "text": "search for jazz music",
                "expected_intent": "search",
                "expected_params": {"query": "jazz"}
            },
            {
                "text": "I want to listen to classical music",
                "expected_intent": "search",
                "expected_params": {"query": "classical music"}
            }
        ]
        
        results = {}
        
        for cmd in complex_commands:
            try:
                start_time = time.time()
                
                test_data = {
                    "text": cmd["text"],
                    "context": "radio_control"
                }
                
                response = self.session.post(f"{API_BASE}/voice/interpret", json=test_data)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    intent = data.get('intent')
                    parameters = data.get('parameters', {})
                    confidence = data.get('confidence', 0)
                    explanation = data.get('explanation', '')
                    
                    # Check if intent matches expected
                    intent_correct = intent == cmd["expected_intent"]
                    
                    # Check if parameters are extracted correctly
                    params_correct = True
                    for key, expected_value in cmd["expected_params"].items():
                        if key not in parameters:
                            params_correct = False
                            break
                        # For search queries, check if expected value is contained in actual value
                        if key == "query":
                            if expected_value.lower() not in parameters[key].lower():
                                params_correct = False
                                break
                        elif parameters[key] != expected_value:
                            params_correct = False
                            break
                    
                    # Check if confidence is reasonable for AI processing (>0.7)
                    good_confidence = confidence > 0.7
                    
                    # Check if it used AI processing
                    used_ai = "ai" in explanation.lower() or confidence < 0.9
                    
                    success = intent_correct and params_correct and good_confidence
                    
                    details = f"Command '{cmd['text']}' -> Intent: {intent}, Params: {parameters}, Confidence: {confidence:.2f}, Method: {'AI' if used_ai else 'Pattern'}"
                    
                    if success:
                        details += " - GOOD AI PROCESSING ✅"
                    elif not intent_correct:
                        details += " - WRONG INTENT ❌"
                    elif not params_correct:
                        details += " - WRONG PARAMETERS ❌"
                    elif not good_confidence:
                        details += f" - LOW CONFIDENCE ({confidence:.2f}) ⚠️"
                    
                    self.log_result(
                        f"Complex Command: {cmd['text'][:30]}...",
                        success,
                        details,
                        response_time
                    )
                    
                    results[cmd["text"]] = success
                else:
                    self.log_result(
                        f"Complex Command: {cmd['text'][:30]}...",
                        False,
                        f"HTTP {response.status_code}: {response.text}",
                        response_time
                    )
                    results[cmd["text"]] = False
                    
            except Exception as e:
                self.log_result(f"Complex Command: {cmd['text'][:30]}...", False, f"Exception: {str(e)}")
                results[cmd["text"]] = False
        
        return results

    def test_voice_intents_endpoint(self) -> bool:
        """Test GET /api/voice/intents endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/intents")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it returns intent information
                expected_intents = ["play", "pause", "next", "previous", "station", "volume_up", "volume_down", "search", "browse"]
                
                if isinstance(data, dict) and len(data) > 0:
                    found_intents = list(data.keys())
                    missing_intents = [intent for intent in expected_intents if intent not in found_intents]
                    
                    if len(missing_intents) == 0:
                        self.log_result(
                            "Voice Intents Endpoint",
                            True,
                            f"All {len(expected_intents)} expected intents found: {', '.join(found_intents)}",
                            response_time
                        )
                        return True
                    else:
                        self.log_result(
                            "Voice Intents Endpoint",
                            False,
                            f"Missing intents: {missing_intents}, Found: {found_intents}",
                            response_time
                        )
                        return False
                else:
                    self.log_result(
                        "Voice Intents Endpoint",
                        False,
                        f"Invalid response format: {data}",
                        response_time
                    )
                    return False
            else:
                self.log_result(
                    "Voice Intents Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result("Voice Intents Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_voice_help_endpoint(self) -> bool:
        """Test GET /api/voice/help endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/help")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it returns help information
                required_fields = ["commands", "available_intents", "usage_tips"]
                
                if all(field in data for field in required_fields):
                    commands_count = len(data.get("commands", []))
                    intents_count = len(data.get("available_intents", []))
                    tips_count = len(data.get("usage_tips", []))
                    
                    self.log_result(
                        "Voice Help Endpoint",
                        True,
                        f"Help data complete: {commands_count} commands, {intents_count} intents, {tips_count} tips",
                        response_time
                    )
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result(
                        "Voice Help Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        response_time
                    )
                    return False
            else:
                self.log_result(
                    "Voice Help Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result("Voice Help Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_backend_connectivity(self) -> bool:
        """Test basic backend connectivity"""
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Backend Connectivity",
                        True,
                        f"Backend responsive: {data.get('message', 'Unknown')}",
                        response_time
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Connectivity",
                        False,
                        f"Unexpected response: {data}",
                        response_time
                    )
                    return False
            else:
                self.log_result(
                    "Backend Connectivity",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_result("Backend Connectivity", False, f"Exception: {str(e)}")
            return False

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