#!/usr/bin/env python3
"""
Comprehensive Backend Stability Testing for Kagema FM Application
Testing all priority areas as specified in the review request:
- Core Radio Streaming APIs
- Voice AI Integration  
- External Audio Sources (Radio.net, TuneIn, Radio Garden)
- Content Compliance & Multilingual Support
- Stream Accessibility (7+ radio streams)
- Performance & Reliability
- Error Handling & Edge Cases
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any, List
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Tunnel URLs from tunnel-manager implementation
TUNNEL_BACKEND_URL = "https://fashion-tree-wellness-simulations.trycloudflare.com"
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://carplay-hub-1.preview.emergentagent.com')

# Test both URLs - tunnel first, then fallback
BACKEND_URL = TUNNEL_BACKEND_URL
API_BASE = f"{BACKEND_URL}/api"

class KagemaFMComprehensiveTester:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        self.performance_metrics = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.total_tests = 0
        self.critical_failures = []

    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0, critical: bool = False):
        """Log test result with performance tracking"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_time': response_time,
            'critical': critical
        }
        self.results.append(result)
        self.total_tests += 1
        
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
            if critical:
                self.critical_failures.append(test_name)
        
        # Track performance metrics
        if response_time > 0:
            self.performance_metrics.append({
                'endpoint': test_name,
                'response_time_ms': response_time
            })
            
        print(f"{status} {test_name}: {details} ({response_time:.0f}ms)")
    
    def test_tunnel_accessibility(self) -> bool:
        """Test tunnel manager implementation - Priority Focus"""
        print("\n🌐 Testing Tunnel Manager Implementation...")
        
        # Test 1: Tunnel URL Accessibility
        tunnel_working = False
        try:
            start_time = time.time()
            response = self.session.get(f"{TUNNEL_BACKEND_URL}/api/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Tunnel URL Accessibility",
                        True,
                        f"Tunnel backend accessible: {data.get('message', 'Unknown')}",
                        response_time,
                        critical=True
                    )
                    tunnel_working = True
                else:
                    self.log_result(
                        "Tunnel URL Accessibility",
                        False,
                        f"Tunnel responding but unexpected data: {data}",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "Tunnel URL Accessibility",
                    False,
                    f"Tunnel HTTP {response.status_code}: {response.text[:100]}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Tunnel URL Accessibility", False, f"Tunnel Exception: {str(e)}", critical=True)
        
        # Test 2: Frontend Env URL Accessibility (fallback)
        frontend_env_working = False
        try:
            start_time = time.time()
            response = self.session.get(f"{FRONTEND_ENV_URL}/api/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Frontend Env URL Accessibility",
                        True,
                        f"Frontend env backend accessible: {data.get('message', 'Unknown')}",
                        response_time,
                        critical=True
                    )
                    frontend_env_working = True
                else:
                    self.log_result(
                        "Frontend Env URL Accessibility",
                        False,
                        f"Frontend env responding but unexpected data: {data}",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "Frontend Env URL Accessibility",
                    False,
                    f"Frontend env HTTP {response.status_code}: {response.text[:100]}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Frontend Env URL Accessibility", False, f"Frontend env Exception: {str(e)}", critical=True)
        
        # Determine which URL to use for remaining tests
        global API_BASE
        if tunnel_working:
            API_BASE = f"{TUNNEL_BACKEND_URL}/api"
            self.log_result(
                "Tunnel Manager Status",
                True,
                "Using tunnel URL for remaining tests - Tunnel manager working correctly",
                0,
                critical=True
            )
            return True
        elif frontend_env_working:
            API_BASE = f"{FRONTEND_ENV_URL}/api"
            self.log_result(
                "Tunnel Manager Status",
                False,
                "Tunnel failed, using frontend env URL - Tunnel manager needs attention",
                0,
                critical=True
            )
            return True
        else:
            self.log_result(
                "Tunnel Manager Status",
                False,
                "Both tunnel and frontend env URLs failed - Critical connectivity issue",
                0,
                critical=True
            )
            return False

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
                        response_time,
                        critical=True
                    )
                    return True
                else:
                    self.log_result(
                        "Basic Connectivity",
                        False,
                        f"Unexpected response: {data}",
                        response_time,
                        critical=True
                    )
                    return False
            else:
                self.log_result(
                    "Basic Connectivity",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response_time,
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result("Basic Connectivity", False, f"Exception: {str(e)}", critical=True)
            return False

    def test_core_radio_streaming_apis(self):
        """Test Core Radio Streaming APIs - Priority Area 1"""
        print("\n🎵 Testing Core Radio Streaming APIs...")
        
        # Test 1: Basic Station Info
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/station-info")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "frequency"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields and data.get("streamUrl"):
                    self.log_result(
                        "Core Radio - Basic Station Info",
                        True,
                        f"Station: {data.get('name')}, Stream: {data.get('streamUrl')}",
                        response_time,
                        critical=True
                    )
                else:
                    self.log_result(
                        "Core Radio - Basic Station Info",
                        False,
                        f"Missing fields: {missing_fields}",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "Core Radio - Basic Station Info",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Core Radio - Basic Station Info", False, f"Exception: {str(e)}", critical=True)

        # Test 2: Multilingual Station Info - Kenya
        try:
            start_time = time.time()
            payload = {"latitude": -1.2921, "longitude": 36.8219}
            response = self.session.post(f"{API_BASE}/station-info/multilingual", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "detected_language"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result(
                        "Core Radio - Multilingual Station Info (Kenya)",
                        True,
                        f"Language: {data.get('detected_language')}, Stream: {data.get('streamUrl')}",
                        response_time,
                        critical=True
                    )
                else:
                    self.log_result(
                        "Core Radio - Multilingual Station Info (Kenya)",
                        False,
                        f"Missing fields: {missing_fields}",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "Core Radio - Multilingual Station Info (Kenya)",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Core Radio - Multilingual Station Info (Kenya)", False, f"Exception: {str(e)}", critical=True)

        # Test 3: Personalized Content with Radio Streams - CRITICAL
        try:
            start_time = time.time()
            user_preferences = {
                "user_id": str(uuid.uuid4()),
                "preferred_language": "en",
                "theme": "dark",
                "offline_mode": False,
                "audio": {
                    "quality": "high",
                    "volume": 0.8,
                    "auto_play": True
                },
                "notifications": {
                    "enabled": True,
                    "news_updates": True,
                    "weather_alerts": True
                }
            }
            
            payload = {
                "location": {
                    "latitude": -1.2921,
                    "longitude": 36.8219
                },
                "preferences": user_preferences
            }
            response = self.session.post(f"{API_BASE}/personalized-content/multilingual", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for radio_streams data - CRITICAL for frontend radio functionality
                radio_streams = data.get("radio_streams")
                if radio_streams:
                    main_station = radio_streams.get("main_station")
                    alternative_streams = radio_streams.get("alternative_streams", [])
                    
                    if main_station and alternative_streams:
                        self.log_result(
                            "Core Radio - Personalized Content with Radio Streams",
                            True,
                            f"Main station + {len(alternative_streams)} alternatives - CRITICAL for frontend",
                            response_time,
                            critical=True
                        )
                    else:
                        self.log_result(
                            "Core Radio - Personalized Content with Radio Streams",
                            False,
                            "Missing main station or alternatives - CRITICAL FAILURE",
                            response_time,
                            critical=True
                        )
                else:
                    self.log_result(
                        "Core Radio - Personalized Content with Radio Streams",
                        False,
                        "No radio_streams data found - CRITICAL FAILURE",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "Core Radio - Personalized Content with Radio Streams",
                    False,
                    f"HTTP {response.status_code} - CRITICAL FAILURE",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Core Radio - Personalized Content with Radio Streams", False, f"Exception: {str(e)}", critical=True)

    def test_voice_ai_integration(self):
        """Test Voice AI Integration - Priority Area 2"""
        print("\n🎤 Testing Voice AI Integration...")
        
        # Test 1: Voice Command Interpretation - Simple Commands
        simple_commands = [
            {"text": "play music", "expected_intent": "play"},
            {"text": "pause", "expected_intent": "pause"},
            {"text": "next station", "expected_intent": "next"},
            {"text": "volume up", "expected_intent": "volume_up"}
        ]
        
        for command in simple_commands:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/voice/interpret", json=command)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    detected_intent = data.get("intent")
                    confidence = data.get("confidence", 0)
                    
                    if detected_intent and confidence > 0.5:
                        self.log_result(
                            f"Voice AI - Simple Command ({command['text']})",
                            True,
                            f"Intent: {detected_intent}, Confidence: {confidence:.2f}",
                            response_time,
                            critical=True
                        )
                    else:
                        self.log_result(
                            f"Voice AI - Simple Command ({command['text']})",
                            False,
                            f"Low confidence or no intent: {detected_intent}, {confidence}",
                            response_time,
                            critical=True
                        )
                else:
                    self.log_result(
                        f"Voice AI - Simple Command ({command['text']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time,
                        critical=True
                    )
            except Exception as e:
                self.log_result(f"Voice AI - Simple Command ({command['text']})", False, f"Exception: {str(e)}", critical=True)

        # Test 2: Voice Command Interpretation - Complex Commands
        complex_commands = [
            {"text": "search for jazz music", "expected_intent": "search"},
            {"text": "tune to classical station", "expected_intent": "station"}
        ]
        
        for command in complex_commands:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/voice/interpret", json=command)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    detected_intent = data.get("intent")
                    confidence = data.get("confidence", 0)
                    parameters = data.get("parameters", {})
                    
                    if detected_intent and confidence > 0.5:
                        self.log_result(
                            f"Voice AI - Complex Command ({command['text']})",
                            True,
                            f"Intent: {detected_intent}, Confidence: {confidence:.2f}, Params: {parameters}",
                            response_time,
                            critical=True
                        )
                    else:
                        self.log_result(
                            f"Voice AI - Complex Command ({command['text']})",
                            False,
                            f"Low confidence or no intent: {detected_intent}, {confidence}",
                            response_time,
                            critical=True
                        )
                else:
                    self.log_result(
                        f"Voice AI - Complex Command ({command['text']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time,
                        critical=True
                    )
            except Exception as e:
                self.log_result(f"Voice AI - Complex Command ({command['text']})", False, f"Exception: {str(e)}", critical=True)

        # Test 3: Voice Intents List
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/intents")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) >= 5:  # Should have at least 5 intents
                    self.log_result(
                        "Voice AI - Intents List",
                        True,
                        f"Found {len(data)} voice intents",
                        response_time
                    )
                else:
                    self.log_result(
                        "Voice AI - Intents List",
                        False,
                        f"Insufficient intents: {len(data) if isinstance(data, dict) else 'Invalid format'}",
                        response_time
                    )
            else:
                self.log_result(
                    "Voice AI - Intents List",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Voice AI - Intents List", False, f"Exception: {str(e)}")

        # Test 4: Voice Help System
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/voice/help")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "commands" in data and "usage_tips" in data:
                    self.log_result(
                        "Voice AI - Help System",
                        True,
                        f"Commands: {len(data.get('commands', []))}, Tips: {len(data.get('usage_tips', []))}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Voice AI - Help System",
                        False,
                        "Missing commands or usage_tips",
                        response_time
                    )
            else:
                self.log_result(
                    "Voice AI - Help System",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Voice AI - Help System", False, f"Exception: {str(e)}")

    def test_external_audio_sources(self):
        """Test External Audio Sources - Priority Area 3"""
        print("\n📻 Testing External Audio Sources...")
        
        # Test 1: Radio Streams Endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/radio/streams")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                main_station = data.get("main_station", {})
                alternative_streams = data.get("alternative_streams", [])
                
                if main_station and alternative_streams and len(alternative_streams) >= 5:
                    self.log_result(
                        "External Audio - Radio Streams",
                        True,
                        f"Main station + {len(alternative_streams)} alternatives",
                        response_time,
                        critical=True
                    )
                else:
                    self.log_result(
                        "External Audio - Radio Streams",
                        False,
                        f"Insufficient streams: main={bool(main_station)}, alt={len(alternative_streams)}",
                        response_time,
                        critical=True
                    )
            else:
                self.log_result(
                    "External Audio - Radio Streams",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("External Audio - Radio Streams", False, f"Exception: {str(e)}", critical=True)

        # Test 2: Radio Stations Endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/radio/stations")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                stations = data.get("stations", [])
                
                if stations and len(stations) >= 5:
                    # Check for international stations (Radio Garden feature)
                    international_count = sum(1 for s in stations if s.get("location") != "Global")
                    self.log_result(
                        "External Audio - Radio Stations",
                        True,
                        f"Found {len(stations)} stations, {international_count} international",
                        response_time
                    )
                else:
                    self.log_result(
                        "External Audio - Radio Stations",
                        False,
                        f"Insufficient stations: {len(stations)}",
                        response_time
                    )
            else:
                self.log_result(
                    "External Audio - Radio Stations",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("External Audio - Radio Stations", False, f"Exception: {str(e)}")

        # Test 3: External Sources Configuration
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/app/version")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                external_sources = data.get("external_sources", {})
                
                expected_sources = ["soma_fm", "bbc_world", "radio_garden"]
                found_sources = [src for src in expected_sources if src in external_sources]
                
                if len(found_sources) >= 2:
                    self.log_result(
                        "External Audio - Sources Configuration",
                        True,
                        f"Found {len(found_sources)} external sources: {found_sources}",
                        response_time
                    )
                else:
                    self.log_result(
                        "External Audio - Sources Configuration",
                        False,
                        f"Missing external sources: found {found_sources}",
                        response_time
                    )
            else:
                self.log_result(
                    "External Audio - Sources Configuration",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("External Audio - Sources Configuration", False, f"Exception: {str(e)}")

    def test_content_compliance(self):
        """Test Content Compliance - Priority Area 4"""
        print("\n🌍 Testing Content Compliance...")
        
        # Test 1: Language Detection
        test_locations = [
            {"name": "Nairobi, Kenya", "lat": -1.2921, "lng": 36.8219, "expected": "en"},
            {"name": "Kisumu, Kenya", "lat": -0.0917, "lng": 34.7680, "expected": "luo"},
            {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333, "expected": "pt-br"}
        ]
        
        for location in test_locations:
            try:
                start_time = time.time()
                payload = {"latitude": location["lat"], "longitude": location["lng"]}
                response = self.session.post(f"{API_BASE}/language/detect", json=payload)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    detected_lang = data.get("detected_language")
                    confidence = data.get("confidence", 0)
                    county = data.get("county", "Unknown")
                    
                    if detected_lang and confidence > 0.8:
                        self.log_result(
                            f"Content Compliance - Language Detection ({location['name']})",
                            True,
                            f"Detected: {detected_lang}, County: {county}, Confidence: {confidence:.2f}",
                            response_time,
                            critical=True
                        )
                    else:
                        self.log_result(
                            f"Content Compliance - Language Detection ({location['name']})",
                            False,
                            f"Low confidence or no language: {detected_lang}, {confidence}",
                            response_time,
                            critical=True
                        )
                else:
                    self.log_result(
                        f"Content Compliance - Language Detection ({location['name']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time,
                        critical=True
                    )
            except Exception as e:
                self.log_result(f"Content Compliance - Language Detection ({location['name']})", False, f"Exception: {str(e)}", critical=True)

        # Test 2: Supported Languages
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/languages")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                languages = data.get("languages", [])
                total_count = data.get("total_count", 0)
                
                if total_count >= 8 and len(languages) >= 8:
                    self.log_result(
                        "Content Compliance - Supported Languages",
                        True,
                        f"Found {total_count} supported languages",
                        response_time
                    )
                else:
                    self.log_result(
                        "Content Compliance - Supported Languages",
                        False,
                        f"Insufficient languages: {total_count}",
                        response_time
                    )
            else:
                self.log_result(
                    "Content Compliance - Supported Languages",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Content Compliance - Supported Languages", False, f"Exception: {str(e)}")

        # Test 3: Content Disclaimers
        compliance_requests = [
            {"country_code": "KE", "language_code": "en"},
            {"country_code": "BR", "language_code": "pt-br"},
            {"country_code": "GLOBAL", "language_code": "en"}
        ]
        
        for req in compliance_requests:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/compliance/disclaimers", json=req)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    disclaimers = data.get("content_disclaimers", [])
                    
                    if disclaimers and len(disclaimers) > 0:
                        self.log_result(
                            f"Content Compliance - Disclaimers ({req['country_code']})",
                            True,
                            f"Found {len(disclaimers)} disclaimers",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Content Compliance - Disclaimers ({req['country_code']})",
                            False,
                            "No disclaimers found",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Content Compliance - Disclaimers ({req['country_code']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Content Compliance - Disclaimers ({req['country_code']})", False, f"Exception: {str(e)}")

    def test_stream_accessibility(self):
        """Test Stream Accessibility - Priority Area 5"""
        print("\n📡 Testing Stream Accessibility...")
        
        # Get stream URLs from the API first
        stream_urls = []
        
        try:
            response = self.session.get(f"{API_BASE}/radio/streams")
            if response.status_code == 200:
                data = response.json()
                main_station = data.get("main_station", {})
                if main_station.get("streamUrl"):
                    stream_urls.append(("Main Station", main_station["streamUrl"]))
                
                alternatives = data.get("alternative_streams", [])
                for alt in alternatives:
                    if alt.get("streamUrl"):
                        stream_urls.append((alt["name"], alt["streamUrl"]))
        except Exception as e:
            self.log_result("Stream Accessibility - API Fetch", False, f"Failed to get stream URLs: {str(e)}", critical=True)
            return
            
        # Test each stream URL accessibility
        accessible_streams = 0
        total_streams = len(stream_urls)
        
        for stream_name, stream_url in stream_urls:
            try:
                start_time = time.time()
                response = self.session.head(stream_url, allow_redirects=True, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    icy_headers = [h for h in response.headers.keys() if h.lower().startswith('icy-')]
                    
                    if 'audio' in content_type.lower() or icy_headers:
                        accessible_streams += 1
                        self.log_result(
                            f"Stream Accessibility - {stream_name}",
                            True,
                            f"Content-Type: {content_type}, ICY headers: {len(icy_headers)}",
                            response_time,
                            critical=True
                        )
                    else:
                        self.log_result(
                            f"Stream Accessibility - {stream_name}",
                            False,
                            f"Not audio stream: {content_type}",
                            response_time,
                            critical=True
                        )
                else:
                    self.log_result(
                        f"Stream Accessibility - {stream_name}",
                        False,
                        f"HTTP {response.status_code}",
                        response_time,
                        critical=True
                    )
            except Exception as e:
                self.log_result(f"Stream Accessibility - {stream_name}", False, f"Exception: {str(e)}", critical=True)
        
        # Summary of stream accessibility
        accessibility_rate = (accessible_streams / total_streams * 100) if total_streams > 0 else 0
        self.log_result(
            "Stream Accessibility - Overall",
            accessibility_rate >= 70,  # 70% threshold
            f"{accessible_streams}/{total_streams} streams accessible ({accessibility_rate:.1f}%)",
            critical=True
        )

    def test_performance_and_reliability(self):
        """Test Performance & Reliability - Priority Area 6"""
        print("\n⚡ Testing Performance & Reliability...")
        
        # Test 1: Response Time Check - Critical Endpoints
        critical_endpoints = [
            ("GET", "/", None),
            ("GET", "/station-info", None),
            ("POST", "/language/detect", {"latitude": -1.2921, "longitude": 36.8219}),
            ("GET", "/languages", None),
            ("POST", "/voice/interpret", {"text": "play music"})
        ]
        
        response_times = []
        
        for method, endpoint, payload in critical_endpoints:
            try:
                start_time = time.time()
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                else:
                    response = self.session.post(f"{API_BASE}{endpoint}", json=payload)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                # Check if response time is under 500ms target
                fast_response = response_time < 500
                success = response.status_code == 200 and fast_response
                
                self.log_result(
                    f"Performance - {endpoint}",
                    success,
                    f"HTTP {response.status_code}, Target <500ms: {fast_response}",
                    response_time,
                    critical=True
                )
                
            except Exception as e:
                self.log_result(f"Performance - {endpoint}", False, f"Exception: {str(e)}", critical=True)
        
        # Calculate average response time
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            self.log_result(
                "Performance - Average Response Time",
                avg_response_time < 500,
                f"Average: {avg_response_time:.0f}ms (Target: <500ms)",
                avg_response_time,
                critical=True
            )
        
        # Test 2: Concurrent Connections (simplified)
        print("Testing concurrent connections...")
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def make_concurrent_request():
                try:
                    start_time = time.time()
                    response = self.session.get(f"{API_BASE}/station-info")
                    response_time = (time.time() - start_time) * 1000
                    results_queue.put((response.status_code == 200, response_time))
                except Exception as e:
                    results_queue.put((False, 0))
            
            # Create 5 concurrent threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_concurrent_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            concurrent_results = []
            while not results_queue.empty():
                concurrent_results.append(results_queue.get())
            
            successful_concurrent = sum(1 for success, _ in concurrent_results if success)
            
            self.log_result(
                "Performance - Concurrent Connections",
                successful_concurrent >= 4,  # 4/5 success threshold
                f"{successful_concurrent}/5 concurrent requests successful",
                critical=True
            )
            
        except Exception as e:
            self.log_result("Performance - Concurrent Connections", False, f"Exception: {str(e)}", critical=True)

    def test_error_handling(self):
        """Test Error Handling - Priority Area 7"""
        print("\n🚨 Testing Error Handling...")
        
        # Test 1: Invalid Endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/invalid-endpoint-12345")
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code == 404
            self.log_result(
                "Error Handling - Invalid Endpoint",
                success,
                f"HTTP {response.status_code} (Expected: 404)",
                response_time
            )
        except Exception as e:
            self.log_result("Error Handling - Invalid Endpoint", False, f"Exception: {str(e)}")

        # Test 2: Invalid POST Data
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/language/detect", json={"invalid": "data"})
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code in [400, 422]
            self.log_result(
                "Error Handling - Invalid POST Data",
                success,
                f"HTTP {response.status_code} (Expected: 400/422)",
                response_time
            )
        except Exception as e:
            self.log_result("Error Handling - Invalid POST Data", False, f"Exception: {str(e)}")

        # Test 3: Missing Required Fields
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/compliance/acknowledge", json={})
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code in [400, 422]
            self.log_result(
                "Error Handling - Missing Required Fields",
                success,
                f"HTTP {response.status_code} (Expected: 400/422)",
                response_time
            )
        except Exception as e:
            self.log_result("Error Handling - Missing Required Fields", False, f"Exception: {str(e)}")

        # Test 4: Invalid Coordinates Fallback
        try:
            start_time = time.time()
            payload = {"latitude": 999, "longitude": 999}
            response = self.session.post(f"{API_BASE}/language/detect", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                # Should fallback to English
                success = data.get("detected_language") == "en"
                self.log_result(
                    "Error Handling - Invalid Coordinates Fallback",
                    success,
                    f"Fallback language: {data.get('detected_language')} (Expected: en)",
                    response_time
                )
            else:
                self.log_result(
                    "Error Handling - Invalid Coordinates Fallback",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Error Handling - Invalid Coordinates Fallback", False, f"Exception: {str(e)}")

    def calculate_metrics(self):
        """Calculate comprehensive performance and quality metrics"""
        if not self.performance_metrics:
            return {}
        
        response_times = [m["response_time_ms"] for m in self.performance_metrics]
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": len(self.passed_tests),
            "failed_tests": len(self.failed_tests),
            "critical_failures": len(self.critical_failures),
            "success_rate_percent": (len(self.passed_tests) / self.total_tests * 100) if self.total_tests > 0 else 0,
            "average_response_time_ms": sum(response_times) / len(response_times),
            "max_response_time_ms": max(response_times),
            "min_response_time_ms": min(response_times),
            "under_500ms_count": sum(1 for rt in response_times if rt < 500),
            "under_500ms_percent": sum(1 for rt in response_times if rt < 500) / len(response_times) * 100
        }

    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🔍 STARTING COMPREHENSIVE KAGEMA FM BACKEND TUNNEL TESTING")
        print("Focus: Tunnel Manager Implementation and Core API Functionality")
        print("Testing all priority areas as specified in review request...")
        print("-" * 80)
        
        # Test tunnel accessibility first - PRIORITY
        if not self.test_tunnel_accessibility():
            print("❌ Backend not accessible via tunnel or fallback. Stopping tests.")
            return self.get_summary()
        
        # Test basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Backend not responding properly. Stopping tests.")
            return self.get_summary()
        
        # Run all test suites
        self.test_core_radio_streaming_apis()
        self.test_voice_ai_integration()
        self.test_external_audio_sources()
        self.test_content_compliance()
        self.test_stream_accessibility()
        self.test_performance_and_reliability()
        self.test_error_handling()
        
        return self.get_summary()

    def get_summary(self):
        """Get comprehensive test summary"""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE KAGEMA FM BACKEND TESTING COMPLETE")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {metrics.get('total_tests', 0)}")
        print(f"   Passed: {metrics.get('passed_tests', 0)}")
        print(f"   Failed: {metrics.get('failed_tests', 0)}")
        print(f"   Critical Failures: {metrics.get('critical_failures', 0)}")
        print(f"   Success Rate: {metrics.get('success_rate_percent', 0):.1f}%")
        
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {metrics.get('average_response_time_ms', 0):.0f}ms")
            print(f"   Max Response Time: {metrics.get('max_response_time_ms', 0):.0f}ms")
            print(f"   Min Response Time: {metrics.get('min_response_time_ms', 0):.0f}ms")
            print(f"   Under 500ms Target: {metrics.get('under_500ms_percent', 0):.1f}%")
        
        # Quality Assessment
        success_rate = metrics.get('success_rate_percent', 0)
        avg_response = metrics.get('average_response_time_ms', 0)
        critical_failures = metrics.get('critical_failures', 0)
        
        print(f"\n🎯 QUALITY ASSESSMENT:")
        if success_rate >= 95:
            print(f"   ✅ Endpoint Success Rate: {success_rate:.1f}% (Target: >95%) - EXCELLENT")
        else:
            print(f"   ❌ Endpoint Success Rate: {success_rate:.1f}% (Target: >95%) - NEEDS IMPROVEMENT")
            
        if avg_response < 500:
            print(f"   ✅ Average Response Time: {avg_response:.0f}ms (Target: <500ms) - EXCELLENT")
        else:
            print(f"   ⚠️ Average Response Time: {avg_response:.0f}ms (Target: <500ms) - ACCEPTABLE")
        
        if critical_failures == 0:
            print(f"   ✅ Critical Failures: 0 - PERFECT")
        else:
            print(f"   ❌ Critical Failures: {critical_failures} - NEEDS ATTENTION")
        
        # Failed Tests Details
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for i, result in enumerate([r for r in self.results if not r['success']][:10], 1):  # Show first 10 failures
                print(f"   {i}. {result['test']}: {result['details']}")
                if result.get('critical'):
                    print(f"      ⚠️ CRITICAL FAILURE")
        
        # Critical Failures Summary
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES SUMMARY:")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        # Deployment Recommendation
        print(f"\n🚀 DEPLOYMENT RECOMMENDATION:")
        if success_rate >= 95 and avg_response < 500 and critical_failures == 0:
            print("   ✅ PRODUCTION READY - All criteria met, deploy with confidence!")
        elif success_rate >= 90 and critical_failures <= 2:
            print("   ⚠️ MOSTLY READY - Minor issues detected, review failed tests")
        else:
            print("   ❌ NOT READY - Significant issues detected, requires fixes")
        
        print("="*80)
        
        return {
            "total_tests": metrics.get('total_tests', 0),
            "passed_tests": metrics.get('passed_tests', 0),
            "failed_tests": metrics.get('failed_tests', 0),
            "critical_failures": critical_failures,
            "success_rate": success_rate,
            "test_results": self.results,
            "performance_metrics": metrics
        }

def main():
    """Main test execution for comprehensive backend testing"""
    tester = KagemaFMComprehensiveTester()
    results = tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["success_rate"] >= 90 and results["critical_failures"] == 0:
        print(f"\n✅ COMPREHENSIVE BACKEND TESTS PASSED ({results['success_rate']:.1f}% success rate)")
        return 0
    else:
        print(f"\n❌ COMPREHENSIVE BACKEND TESTS FAILED ({results['success_rate']:.1f}% success rate, {results['critical_failures']} critical failures)")
        return 1

if __name__ == "__main__":
    exit(main())