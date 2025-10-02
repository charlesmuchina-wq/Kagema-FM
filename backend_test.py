#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Kagema FM Radio Station
Testing all critical radio streaming APIs and enhanced features per Phase 2 review request
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'frontend' / '.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class KagemaFMBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.start_time = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test result with timing information"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'response_time_ms': round(response_time * 1000, 2),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({response_time*1000:.0f}ms) - {details}")
        
    async def test_api_connectivity(self) -> bool:
        """Test basic API connectivity"""
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    expected_message = "Kagema FM Satellite & Offline Radio API"
                    if data.get("message") == expected_message:
                        self.log_test_result(
                            "API Root Connectivity", 
                            True, 
                            response_time,
                            f"API v{data.get('version', 'unknown')} responding correctly"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "API Root Connectivity", 
                            False, 
                            response_time,
                            f"Unexpected message: {data.get('message', 'none')}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "API Root Connectivity", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "API Root Connectivity", 
                False, 
                0,
                f"Connection error: {str(e)}"
            )
            return False
            
    async def test_station_info_basic(self) -> bool:
        """Test GET /api/station-info endpoint"""
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/station-info") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['name', 'description', 'streamUrl', 'frequency']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get('name') == 'Kagema FM':
                        self.log_test_result(
                            "Basic Station Info", 
                            True, 
                            response_time,
                            f"Complete station data with stream URL: {data.get('streamUrl', 'none')}"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Basic Station Info", 
                            False, 
                            response_time,
                            f"Missing fields: {missing_fields}" if missing_fields else "Invalid station name"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Basic Station Info", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Basic Station Info", 
                False, 
                0,
                f"Request error: {str(e)}"
            )
            return False
            
    async def test_multilingual_station_info(self) -> Dict[str, bool]:
        """Test POST /api/station-info/multilingual for different regions"""
        test_locations = {
            "Kenya": {"latitude": -1.2921, "longitude": 36.8219},  # Nairobi
            "Brazil": {"latitude": -23.5505, "longitude": -46.6333},  # São Paulo
            "Global": {"latitude": 40.7128, "longitude": -74.0060}  # New York
        }
        
        results = {}
        
        for region, location in test_locations.items():
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{API_BASE_URL}/station-info/multilingual",
                    json=location
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        required_fields = ['name', 'description', 'streamUrl', 'detected_language']
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            self.log_test_result(
                                f"Multilingual Station Info ({region})", 
                                True, 
                                response_time,
                                f"Language: {data.get('detected_language')}, Stream: {data.get('streamUrl')}"
                            )
                            results[region] = True
                        else:
                            self.log_test_result(
                                f"Multilingual Station Info ({region})", 
                                False, 
                                response_time,
                                f"Missing fields: {missing_fields}"
                            )
                            results[region] = False
                    else:
                        self.log_test_result(
                            f"Multilingual Station Info ({region})", 
                            False, 
                            response_time,
                            f"HTTP {response.status}"
                        )
                        results[region] = False
                        
            except Exception as e:
                self.log_test_result(
                    f"Multilingual Station Info ({region})", 
                    False, 
                    0,
                    f"Request error: {str(e)}"
                )
                results[region] = False
                
        return results
        
    async def test_personalized_content_multilingual(self) -> bool:
        """Test POST /api/personalized-content/multilingual - CRITICAL for frontend radio functionality"""
        try:
            # Test with Kenya location and basic preferences
            payload = {
                "location": {
                    "latitude": -1.2921, 
                    "longitude": 36.8219
                },
                "preferences": {
                    "user_id": "test_user_001",
                    "theme": "dark",
                    "language": "en",
                    "region": "auto",
                    "offline_mode": False,
                    "audio": {
                        "quality": "high",
                        "volume": 0.8,
                        "auto_play": True
                    },
                    "notifications": {
                        "enabled": True,
                        "news_updates": True,
                        "music_discovery": True
                    }
                }
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{API_BASE_URL}/personalized-content/multilingual",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for critical radio_streams data
                    has_radio_streams = 'radio_streams' in data
                    has_main_station = has_radio_streams and 'main_station' in data['radio_streams']
                    has_alternative_streams = has_radio_streams and 'alternative_streams' in data['radio_streams']
                    
                    # Check for other content sections
                    has_news = 'news' in data
                    has_music = 'music' in data
                    has_language_detection = 'language_detection' in data
                    
                    if has_radio_streams and has_main_station:
                        main_station = data['radio_streams']['main_station']
                        alt_streams_count = len(data['radio_streams'].get('alternative_streams', []))
                        
                        self.log_test_result(
                            "Personalized Content Multilingual", 
                            True, 
                            response_time,
                            f"Complete content with radio_streams: main + {alt_streams_count} alternatives, news: {has_news}, music: {has_music}"
                        )
                        return True
                    else:
                        missing_components = []
                        if not has_radio_streams:
                            missing_components.append("radio_streams")
                        if not has_main_station:
                            missing_components.append("main_station")
                            
                        self.log_test_result(
                            "Personalized Content Multilingual", 
                            False, 
                            response_time,
                            f"CRITICAL: Missing radio streaming data - {', '.join(missing_components)}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Personalized Content Multilingual", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Personalized Content Multilingual", 
                False, 
                0,
                f"Request error: {str(e)}"
            )
            return False
            
    async def test_stream_accessibility(self) -> Dict[str, bool]:
        """Test accessibility of main Kagema FM stream and alternatives"""
        # Get stream URLs from the personalized content API first
        try:
            payload = {
                "location": {
                    "latitude": -1.2921, 
                    "longitude": 36.8219
                },
                "preferences": {
                    "user_id": "test_user_stream",
                    "theme": "dark",
                    "language": "en",
                    "region": "auto",
                    "offline_mode": False,
                    "audio": {
                        "quality": "high", 
                        "volume": 0.8, 
                        "auto_play": True
                    },
                    "notifications": {
                        "enabled": True, 
                        "news_updates": True, 
                        "music_discovery": True
                    }
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/personalized-content/multilingual",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    radio_streams = data.get('radio_streams', {})
                    
                    # Test main station stream
                    main_station = radio_streams.get('main_station', {})
                    main_stream_url = main_station.get('streamUrl')
                    
                    # Test alternative streams
                    alternative_streams = radio_streams.get('alternative_streams', [])
                    
                    stream_results = {}
                    
                    # Test main stream
                    if main_stream_url:
                        stream_results['Main Kagema FM Stream'] = await self.test_single_stream(
                            main_stream_url, 
                            "Main Kagema FM Stream"
                        )
                    
                    # Test up to 5 alternative streams
                    for i, stream in enumerate(alternative_streams[:5]):
                        stream_name = stream.get('name', f'Alternative Stream {i+1}')
                        stream_url = stream.get('streamUrl')
                        if stream_url:
                            stream_results[stream_name] = await self.test_single_stream(
                                stream_url, 
                                stream_name
                            )
                    
                    return stream_results
                else:
                    self.log_test_result(
                        "Stream Accessibility Setup", 
                        False, 
                        0,
                        f"Failed to get stream URLs from API: HTTP {response.status}"
                    )
                    return {}
                    
        except Exception as e:
            self.log_test_result(
                "Stream Accessibility Setup", 
                False, 
                0,
                f"Error getting stream URLs: {str(e)}"
            )
            return {}
            
    async def test_single_stream(self, stream_url: str, stream_name: str) -> bool:
        """Test accessibility of a single audio stream"""
        try:
            start_time = time.time()
            async with self.session.head(stream_url, allow_redirects=True) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    icy_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('icy-')}
                    
                    is_audio = any(audio_type in content_type.lower() for audio_type in ['audio/', 'application/ogg'])
                    
                    if is_audio or icy_headers:
                        self.log_test_result(
                            f"Stream: {stream_name}", 
                            True, 
                            response_time,
                            f"Accessible - {content_type}, {len(icy_headers)} ICY headers"
                        )
                        return True
                    else:
                        self.log_test_result(
                            f"Stream: {stream_name}", 
                            False, 
                            response_time,
                            f"Not audio content: {content_type}"
                        )
                        return False
                else:
                    self.log_test_result(
                        f"Stream: {stream_name}", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                f"Stream: {stream_name}", 
                False, 
                0,
                f"Connection error: {str(e)}"
            )
            return False
            
    async def test_enhanced_features(self) -> Dict[str, bool]:
        """Test enhanced features from review request"""
        results = {}
        
        # Test language detection
        try:
            location = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
            start_time = time.time()
            async with self.session.post(f"{API_BASE_URL}/language/detect", json=location) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_detection = 'detected_language' in data and 'confidence' in data
                    
                    self.log_test_result(
                        "Language Detection", 
                        has_detection, 
                        response_time,
                        f"Language: {data.get('detected_language', 'none')}, Confidence: {data.get('confidence', 0)}"
                    )
                    results['language_detection'] = has_detection
                else:
                    self.log_test_result("Language Detection", False, response_time, f"HTTP {response.status}")
                    results['language_detection'] = False
        except Exception as e:
            self.log_test_result("Language Detection", False, 0, f"Error: {str(e)}")
            results['language_detection'] = False
            
        # Test content compliance
        try:
            compliance_request = {
                "country_code": "KE",
                "language_code": "en",
                "content_types": ["radio_streams", "music", "news"]
            }
            start_time = time.time()
            async with self.session.post(f"{API_BASE_URL}/compliance/disclaimers", json=compliance_request) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_disclaimers = 'content_disclaimers' in data and len(data['content_disclaimers']) > 0
                    
                    self.log_test_result(
                        "Content Compliance", 
                        has_disclaimers, 
                        response_time,
                        f"Disclaimers: {len(data.get('content_disclaimers', []))}"
                    )
                    results['content_compliance'] = has_disclaimers
                else:
                    self.log_test_result("Content Compliance", False, response_time, f"HTTP {response.status}")
                    results['content_compliance'] = False
        except Exception as e:
            self.log_test_result("Content Compliance", False, 0, f"Error: {str(e)}")
            results['content_compliance'] = False
            
        # Test satellite status
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/satellite/status") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_status = 'connection_type' in data and 'signal_strength' in data
                    
                    self.log_test_result(
                        "Satellite Status", 
                        has_status, 
                        response_time,
                        f"Connection: {data.get('connection_type', 'none')}, Signal: {data.get('signal_strength', 'none')}"
                    )
                    results['satellite_status'] = has_status
                else:
                    self.log_test_result("Satellite Status", False, response_time, f"HTTP {response.status}")
                    results['satellite_status'] = False
        except Exception as e:
            self.log_test_result("Satellite Status", False, 0, f"Error: {str(e)}")
            results['satellite_status'] = False
            
        return results

    async def test_voice_ai_endpoints(self) -> Dict[str, bool]:
        """Test Voice AI endpoints - NEW FEATURE TESTING"""
        results = {}
        
        # Test POST /api/voice/interpret endpoint
        print("\n🎤 Testing Voice AI Interpretation Endpoint")
        
        # Test cases for voice commands
        test_commands = [
            # Simple commands
            {
                "text": "play radio",
                "context": "radio_control",
                "expected_intent": "play",
                "description": "Simple play command"
            },
            {
                "text": "pause",
                "context": "radio_control", 
                "expected_intent": "pause",
                "description": "Simple pause command"
            },
            {
                "text": "next station",
                "context": "radio_control",
                "expected_intent": "next",
                "description": "Next station command"
            },
            # Complex commands
            {
                "text": "search for jazz music",
                "context": "radio_control",
                "expected_intent": "search",
                "description": "Complex search command"
            },
            {
                "text": "tune to classical station",
                "context": "radio_control",
                "expected_intent": "station",
                "description": "Complex station change command"
            },
            # Unknown commands for fallback testing
            {
                "text": "what is the weather today",
                "context": "radio_control",
                "expected_intent": "unknown",
                "description": "Unknown command fallback test"
            }
        ]
        
        voice_interpret_success = 0
        voice_interpret_total = len(test_commands)
        
        for i, test_case in enumerate(test_commands, 1):
            try:
                payload = {
                    "text": test_case["text"],
                    "context": test_case["context"]
                }
                
                start_time = time.time()
                async with self.session.post(
                    f"{API_BASE_URL}/voice/interpret",
                    json=payload
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = ["intent", "parameters", "confidence", "explanation"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            # Check if intent matches expected (for known commands)
                            intent_correct = (
                                test_case["expected_intent"] == "unknown" or 
                                data["intent"] == test_case["expected_intent"]
                            )
                            
                            # Validate confidence is between 0 and 1
                            confidence_valid = 0.0 <= data["confidence"] <= 1.0
                            
                            success = intent_correct and confidence_valid
                            if success:
                                voice_interpret_success += 1
                            
                            details = f"Intent: {data['intent']} (expected: {test_case['expected_intent']}), Confidence: {data['confidence']:.2f}"
                            if data["parameters"]:
                                details += f", Parameters: {data['parameters']}"
                            
                            self.log_test_result(
                                f"Voice Interpret: {test_case['description']}",
                                success,
                                response_time,
                                details
                            )
                        else:
                            self.log_test_result(
                                f"Voice Interpret: {test_case['description']}",
                                False,
                                response_time,
                                f"Missing fields: {missing_fields}"
                            )
                    else:
                        self.log_test_result(
                            f"Voice Interpret: {test_case['description']}",
                            False,
                            response_time,
                            f"HTTP {response.status}"
                        )
                        
            except Exception as e:
                self.log_test_result(
                    f"Voice Interpret: {test_case['description']}",
                    False,
                    0,
                    f"Exception: {str(e)}"
                )
        
        results['voice_interpret'] = voice_interpret_success == voice_interpret_total
        
        # Test GET /api/voice/intents endpoint
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/voice/intents") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Expected intents from voice_ai_service.py
                    expected_intents = [
                        "play", "pause", "next", "previous", "station", 
                        "volume_up", "volume_down", "search", "browse"
                    ]
                    
                    # Check if response contains intent data
                    if isinstance(data, dict):
                        found_intents = list(data.keys())
                        missing_intents = [intent for intent in expected_intents if intent not in found_intents]
                        
                        # Validate structure of each intent
                        structure_valid = True
                        for intent, intent_data in data.items():
                            if not isinstance(intent_data, dict):
                                structure_valid = False
                                break
                            if "description" not in intent_data or "keywords" not in intent_data:
                                structure_valid = False
                                break
                        
                        success = len(missing_intents) == 0 and structure_valid
                        details = f"Found {len(found_intents)} intents"
                        if missing_intents:
                            details += f", Missing: {missing_intents}"
                        
                        self.log_test_result(
                            "Voice Intents - Structure and Content",
                            success,
                            response_time,
                            details
                        )
                        results['voice_intents'] = success
                    else:
                        self.log_test_result(
                            "Voice Intents - Response Format",
                            False,
                            response_time,
                            "Response is not a dictionary"
                        )
                        results['voice_intents'] = False
                else:
                    self.log_test_result(
                        "Voice Intents - HTTP Response",
                        False,
                        response_time,
                        f"HTTP {response.status}"
                    )
                    results['voice_intents'] = False
                    
        except Exception as e:
            self.log_test_result(
                "Voice Intents - Request",
                False,
                0,
                f"Exception: {str(e)}"
            )
            results['voice_intents'] = False
        
        # Test GET /api/voice/help endpoint
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/voice/help") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Expected structure
                    expected_fields = ["commands", "available_intents", "usage_tips"]
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if not missing_fields:
                        # Validate content
                        commands_valid = isinstance(data["commands"], list) and len(data["commands"]) > 0
                        intents_valid = isinstance(data["available_intents"], list) and len(data["available_intents"]) > 0
                        tips_valid = isinstance(data["usage_tips"], list) and len(data["usage_tips"]) > 0
                        
                        success = commands_valid and intents_valid and tips_valid
                        details = f"Commands: {len(data['commands'])}, Intents: {len(data['available_intents'])}, Tips: {len(data['usage_tips'])}"
                        
                        self.log_test_result(
                            "Voice Help - Structure and Content",
                            success,
                            response_time,
                            details
                        )
                        results['voice_help'] = success
                    else:
                        self.log_test_result(
                            "Voice Help - Response Structure",
                            False,
                            response_time,
                            f"Missing fields: {missing_fields}"
                        )
                        results['voice_help'] = False
                else:
                    self.log_test_result(
                        "Voice Help - HTTP Response",
                        False,
                        response_time,
                        f"HTTP {response.status}"
                    )
                    results['voice_help'] = False
                    
        except Exception as e:
            self.log_test_result(
                "Voice Help - Request",
                False,
                0,
                f"Exception: {str(e)}"
            )
            results['voice_help'] = False
        
        # Test AI integration with complex commands
        print("\n🤖 Testing Emergent LLM Integration")
        complex_commands = [
            {
                "text": "I want to listen to some relaxing ambient music",
                "description": "Complex natural language request"
            },
            {
                "text": "Can you please change the station to something with jazz",
                "description": "Polite complex station request"
            }
        ]
        
        ai_integration_success = 0
        ai_integration_total = len(complex_commands)
        
        for i, test_case in enumerate(complex_commands, 1):
            try:
                payload = {
                    "text": test_case["text"],
                    "context": "radio_control"
                }
                
                start_time = time.time()
                async with self.session.post(
                    f"{API_BASE_URL}/voice/interpret",
                    json=payload
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if response makes sense for the complex command
                        reasonable_intent = data.get("intent") in ["search", "station", "play", "unknown"]
                        has_confidence = data.get("confidence", 0) > 0
                        has_explanation = bool(data.get("explanation", "").strip())
                        
                        success = reasonable_intent and has_confidence and has_explanation
                        if success:
                            ai_integration_success += 1
                        
                        details = f"Intent: {data.get('intent')}, Confidence: {data.get('confidence', 0):.2f}, Time: {response_time:.1f}s"
                        
                        self.log_test_result(
                            f"AI Integration: {test_case['description']}",
                            success,
                            response_time,
                            details
                        )
                    else:
                        self.log_test_result(
                            f"AI Integration: {test_case['description']}",
                            False,
                            response_time,
                            f"HTTP {response.status}"
                        )
                        
            except Exception as e:
                self.log_test_result(
                    f"AI Integration: {test_case['description']}",
                    False,
                    0,
                    f"Exception: {str(e)}"
                )
        
        results['ai_integration'] = ai_integration_success == ai_integration_total
        
        return results
        
    async def run_comprehensive_test(self):
        """Run all comprehensive backend tests"""
        print("🎵 STARTING COMPREHENSIVE KAGEMA FM BACKEND API VERIFICATION")
        print(f"Testing against: {API_BASE_URL}")
        print("=" * 80)
        
        # Phase 1: Critical Radio Streaming APIs
        print("\n📡 PHASE 1: CRITICAL RADIO STREAMING APIs")
        connectivity_ok = await self.test_api_connectivity()
        station_info_ok = await self.test_station_info_basic()
        multilingual_results = await self.test_multilingual_station_info()
        personalized_content_ok = await self.test_personalized_content_multilingual()
        
        # Phase 2: Stream Accessibility
        print("\n🎶 PHASE 2: STREAM ACCESSIBILITY VERIFICATION")
        stream_results = await self.test_stream_accessibility()
        
        # Phase 3: Enhanced Features
        print("\n⚡ PHASE 3: ENHANCED FEATURES")
        enhanced_results = await self.test_enhanced_features()
        
        # Phase 4: Voice AI Features (NEW)
        print("\n🎤 PHASE 4: VOICE AI FEATURES")
        voice_ai_results = await self.test_voice_ai_endpoints()
        
        # Calculate overall results
        total_time = time.time() - self.start_time
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance metrics
        response_times = [result['response_time_ms'] for result in self.test_results if result['response_time_ms'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE BACKEND TESTING COMPLETE")
        print("=" * 80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Total Time: {total_time:.1f}s")
        print(f"   • Avg Response Time: {avg_response_time:.0f}ms")
        print(f"   • Max Response Time: {max_response_time:.0f}ms")
        
        # Critical endpoints summary
        critical_endpoints = {
            'API Root': connectivity_ok,
            'Station Info': station_info_ok,
            'Multilingual Station (Kenya)': multilingual_results.get('Kenya', False),
            'Multilingual Station (Brazil)': multilingual_results.get('Brazil', False),
            'Multilingual Station (Global)': multilingual_results.get('Global', False),
            'Personalized Content': personalized_content_ok
        }
        
        critical_success = sum(critical_endpoints.values())
        critical_total = len(critical_endpoints)
        critical_rate = (critical_success / critical_total * 100) if critical_total > 0 else 0
        
        print(f"\n🎯 CRITICAL RADIO STREAMING APIs: {critical_success}/{critical_total} ({critical_rate:.1f}%)")
        for endpoint, status in critical_endpoints.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {endpoint}")
            
        # Stream accessibility summary
        if stream_results:
            working_streams = sum(stream_results.values())
            total_streams = len(stream_results)
            stream_rate = (working_streams / total_streams * 100) if total_streams > 0 else 0
            
            print(f"\n📡 STREAM ACCESSIBILITY: {working_streams}/{total_streams} ({stream_rate:.1f}%)")
            for stream_name, status in stream_results.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {stream_name}")
        
        # Enhanced features summary
        if enhanced_results:
            enhanced_success = sum(enhanced_results.values())
            enhanced_total = len(enhanced_results)
            enhanced_rate = (enhanced_success / enhanced_total * 100) if enhanced_total > 0 else 0
            
            print(f"\n⚡ ENHANCED FEATURES: {enhanced_success}/{enhanced_total} ({enhanced_rate:.1f}%)")
            for feature, status in enhanced_results.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        # Voice AI features summary (NEW)
        if voice_ai_results:
            voice_ai_success = sum(voice_ai_results.values())
            voice_ai_total = len(voice_ai_results)
            voice_ai_rate = (voice_ai_success / voice_ai_total * 100) if voice_ai_total > 0 else 0
            
            print(f"\n🎤 VOICE AI FEATURES: {voice_ai_success}/{voice_ai_total} ({voice_ai_rate:.1f}%)")
            for feature, status in voice_ai_results.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        # Performance assessment
        print(f"\n⚡ PERFORMANCE ASSESSMENT:")
        if avg_response_time < 2000:
            print(f"   ✅ Response Time: EXCELLENT ({avg_response_time:.0f}ms avg)")
        elif avg_response_time < 5000:
            print(f"   ⚠️  Response Time: ACCEPTABLE ({avg_response_time:.0f}ms avg)")
        else:
            print(f"   ❌ Response Time: SLOW ({avg_response_time:.0f}ms avg)")
            
        # Final assessment
        if success_rate >= 95 and critical_rate >= 90:
            print(f"\n🎉 DEPLOYMENT STATUS: ✅ PRODUCTION READY")
            print(f"   Backend API endpoints are fully operational and meet all requirements")
        elif success_rate >= 85 and critical_rate >= 80:
            print(f"\n⚠️  DEPLOYMENT STATUS: 🔶 MOSTLY READY")
            print(f"   Minor issues detected but core functionality working")
        else:
            print(f"\n❌ DEPLOYMENT STATUS: 🔴 NEEDS ATTENTION")
            print(f"   Critical issues found that require resolution")
            
        return {
            'success_rate': success_rate,
            'critical_rate': critical_rate,
            'stream_accessibility': stream_results,
            'enhanced_features': enhanced_results,
            'performance': {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time
            },
            'test_results': self.test_results
        }

async def main():
    """Main test execution function"""
    async with KagemaFMBackendTester() as tester:
        results = await tester.run_comprehensive_test()
        return results

if __name__ == "__main__":
    asyncio.run(main())