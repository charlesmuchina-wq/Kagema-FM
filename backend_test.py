#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Kagema FM Enhanced Geographic Coverage
Testing Focus: Enhanced SoundCast Service, Satellite Radio Integration, 
Advanced Geolocation Features, and External Source Error Fixes

Priority Testing Areas:
1. Enhanced SoundCast Service with comprehensive North/South American coverage
2. New Satellite Radio Integration (SiriusXM, Global Satellite Network, Emergency Broadcast)
3. Advanced Geolocation Features (GPS-based station discovery, offline caching, regional mapping)
4. Fixed External Source Errors with proper fallback mechanisms
5. Performance and stability under geographic coverage enhancements
"""

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

# Backend URL from frontend environment
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://kagema-player.preview.emergentagent.com')
LOCAL_BACKEND_URL = "http://localhost:8001"

# Use frontend env URL as primary
BACKEND_URL = FRONTEND_ENV_URL
API_BASE = f"{BACKEND_URL}/api"

class KagemaFMGeographicCoverageTester:
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

    def test_backend_accessibility(self) -> bool:
        """Test backend accessibility"""
        print("\n🌐 Testing Backend Accessibility...")
        
        # Test frontend env URL first
        try:
            start_time = time.time()
            response = self.session.get(f"{FRONTEND_ENV_URL}/api/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Backend Accessibility",
                        True,
                        f"Frontend env backend accessible: {data.get('message', 'Unknown')}",
                        response_time,
                        critical=True
                    )
                    return True
        except Exception as e:
            pass
        
        # Fallback to local backend
        try:
            global API_BASE
            API_BASE = f"{LOCAL_BACKEND_URL}/api"
            start_time = time.time()
            response = self.session.get(f"{LOCAL_BACKEND_URL}/api/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_result(
                        "Backend Accessibility",
                        True,
                        f"Local backend accessible: {data.get('message', 'Unknown')}",
                        response_time,
                        critical=True
                    )
                    return True
        except Exception as e:
            self.log_result("Backend Accessibility", False, f"All backends failed: {str(e)}", critical=True)
            return False
        
        return False

    def test_enhanced_soundcast_service(self):
        """Test Enhanced SoundCast Service with North/South American coverage"""
        print("\n🌎 Testing Enhanced SoundCast Service - North/South American Coverage...")
        
        # Test locations across North and South America
        test_locations = [
            # United States regions
            {"lat": 40.7128, "lng": -74.0060, "name": "New York, NY (East Coast)", "region": "US_EAST"},
            {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles, CA (West Coast)", "region": "US_WEST"},
            {"lat": 41.8781, "lng": -87.6298, "name": "Chicago, IL (Central)", "region": "US_CENTRAL"},
            {"lat": 29.7604, "lng": -95.3698, "name": "Houston, TX (Southern)", "region": "US_SOUTH"},
            
            # Canada provinces
            {"lat": 43.6532, "lng": -79.3832, "name": "Toronto, ON, Canada", "region": "CA_ON"},
            {"lat": 45.5017, "lng": -73.5673, "name": "Montreal, QC, Canada", "region": "CA_QC"},
            
            # Mexico major cities
            {"lat": 19.4326, "lng": -99.1332, "name": "Mexico City, Mexico", "region": "MX_CENTRAL"},
            
            # Brazil major cities
            {"lat": -23.5505, "lng": -46.6333, "name": "São Paulo, Brazil", "region": "BR_SP"},
            {"lat": -22.9068, "lng": -43.1729, "name": "Rio de Janeiro, Brazil", "region": "BR_RJ"},
            {"lat": -15.8267, "lng": -47.9218, "name": "Brasília, Brazil", "region": "BR_DF"},
            
            # Other South American cities
            {"lat": -34.6118, "lng": -58.3960, "name": "Buenos Aires, Argentina", "region": "AR_BA"},
            {"lat": -33.4489, "lng": -70.6693, "name": "Santiago, Chile", "region": "CL_RM"},
            {"lat": 4.7110, "lng": -74.0721, "name": "Bogotá, Colombia", "region": "CO_BOG"},
            {"lat": -12.0464, "lng": -77.0428, "name": "Lima, Peru", "region": "PE_LIM"},
            
            # Caribbean Islands
            {"lat": 18.1096, "lng": -77.2975, "name": "Kingston, Jamaica", "region": "JM_KIN"},
            {"lat": 23.1136, "lng": -82.3666, "name": "Havana, Cuba", "region": "CU_HAV"},
            {"lat": 13.1939, "lng": -59.5432, "name": "Bridgetown, Barbados", "region": "BB_BRI"}
        ]
        
        successful_locations = 0
        
        for location in test_locations:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/station-info/multilingual", json={
                    "latitude": location["lat"],
                    "longitude": location["lng"]
                })
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    detected_lang = data.get("detected_language", "unknown")
                    location_info = data.get("location", "unknown")
                    stream_url = data.get("streamUrl", "")
                    
                    if stream_url and detected_lang:
                        successful_locations += 1
                        self.log_result(
                            f"SoundCast Coverage - {location['name']}",
                            True,
                            f"Language: {detected_lang}, Location: {location_info}, Stream: ✓",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"SoundCast Coverage - {location['name']}",
                            False,
                            f"Missing stream or language detection",
                            response_time
                        )
                else:
                    self.log_result(
                        f"SoundCast Coverage - {location['name']}",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"SoundCast Coverage - {location['name']}", False, f"Exception: {str(e)}")
        
        # Overall coverage assessment
        coverage_rate = (successful_locations / len(test_locations)) * 100
        self.log_result(
            "Enhanced SoundCast Service - Overall Coverage",
            coverage_rate >= 80,  # 80% threshold for geographic coverage
            f"{successful_locations}/{len(test_locations)} locations covered ({coverage_rate:.1f}%)",
            critical=True
        )

    def test_satellite_radio_integration(self):
        """Test New Satellite Radio Integration"""
        print("\n📡 Testing Satellite Radio Integration...")
        
        # Test 1: Satellite Status Check
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/satellite/status")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                connection_type = data.get("connection_type", "unknown")
                signal_strength = data.get("signal_strength", "unknown")
                provider = data.get("provider", "unknown")
                
                self.log_result(
                    "Satellite Integration - Status Check",
                    True,
                    f"Connection: {connection_type}, Signal: {signal_strength}, Provider: {provider}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "Satellite Integration - Status Check",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Satellite Integration - Status Check", False, f"Exception: {str(e)}", critical=True)
        
        # Test 2: Satellite Connection Test
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/satellite/connect", json={
                "provider": "Global Satellite Network",
                "client_id": "kagema_fm_test",
                "location": "auto"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                connected = data.get("connected", False)
                provider = data.get("provider", "unknown")
                
                self.log_result(
                    "Satellite Integration - Connection Test",
                    True,
                    f"Connected: {connected}, Provider: {provider}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "Satellite Integration - Connection Test",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Satellite Integration - Connection Test", False, f"Exception: {str(e)}", critical=True)
        
        # Test 3: Satellite Main Stations
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/satellite/main_stations")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                stations = data.get("main_stations", [])
                satellite_status = data.get("satellite_status", {})
                
                self.log_result(
                    "Satellite Integration - Main Stations",
                    len(stations) >= 2,
                    f"Found {len(stations)} satellite stations, Status: {satellite_status.get('connection_type', 'unknown')}",
                    response_time
                )
            else:
                self.log_result(
                    "Satellite Integration - Main Stations",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Satellite Integration - Main Stations", False, f"Exception: {str(e)}")

    def test_advanced_geolocation_features(self):
        """Test Advanced Geolocation Features"""
        print("\n🗺️ Testing Advanced Geolocation Features...")
        
        # Test 1: GPS-based Station Discovery
        test_coordinates = [
            {"lat": -1.2921, "lng": 36.8219, "name": "Nairobi, Kenya"},
            {"lat": -0.0917, "lng": 34.7680, "name": "Kisumu, Kenya"},
            {"lat": -23.5505, "lng": -46.6333, "name": "São Paulo, Brazil"},
            {"lat": 40.7128, "lng": -74.0060, "name": "New York, USA"},
            {"lat": 19.4326, "lng": -99.1332, "name": "Mexico City, Mexico"}
        ]
        
        for coord in test_coordinates:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/language/detect", json={
                    "latitude": coord["lat"],
                    "longitude": coord["lng"]
                })
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    detected_lang = data.get("detected_language", "unknown")
                    confidence = data.get("confidence", 0)
                    county = data.get("county", "unknown")
                    regional_stations = data.get("regional_stations", [])
                    
                    self.log_result(
                        f"GPS Station Discovery - {coord['name']}",
                        confidence > 0.8,
                        f"Language: {detected_lang}, Confidence: {confidence:.2f}, County: {county}, Stations: {len(regional_stations)}",
                        response_time,
                        critical=True
                    )
                else:
                    self.log_result(
                        f"GPS Station Discovery - {coord['name']}",
                        False,
                        f"HTTP {response.status_code}",
                        response_time,
                        critical=True
                    )
            except Exception as e:
                self.log_result(f"GPS Station Discovery - {coord['name']}", False, f"Exception: {str(e)}", critical=True)
        
        # Test 2: Google Maps Geocoding Integration
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/googlemaps/geocode", json={
                "address": "Nairobi, Kenya"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                location = data.get("location", {})
                
                self.log_result(
                    "Google Maps Geocoding",
                    "lat" in location and "lng" in location,
                    f"Geocoded address to coordinates: {location}",
                    response_time
                )
            else:
                self.log_result(
                    "Google Maps Geocoding",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps Geocoding", False, f"Exception: {str(e)}")
        
        # Test 3: Reverse Geocoding
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/googlemaps/reverse-geocode", json={
                "latitude": -1.2921,
                "longitude": 36.8219
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                formatted_address = address.get("formatted_address", "unknown")
                
                self.log_result(
                    "Google Maps Reverse Geocoding",
                    len(formatted_address) > 10,
                    f"Address: {formatted_address}",
                    response_time
                )
            else:
                self.log_result(
                    "Google Maps Reverse Geocoding",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps Reverse Geocoding", False, f"Exception: {str(e)}")
        
        # Test 4: Nearby Places Search
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/googlemaps/places/nearby", json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "radius": 5000,
                "place_type": "establishment"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("places", [])
                
                self.log_result(
                    "Google Maps Nearby Places",
                    len(places) > 0,
                    f"Found {len(places)} nearby places",
                    response_time
                )
            else:
                self.log_result(
                    "Google Maps Nearby Places",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps Nearby Places", False, f"Exception: {str(e)}")

    def test_offline_caching_features(self):
        """Test Offline Station Caching for Remote Areas"""
        print("\n💾 Testing Offline Caching Features...")
        
        # Test 1: Offline Content Caching
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/offline/cache", json={
                "content_types": ["radio_streams", "news", "weather", "music", "language_data"],
                "location": {"latitude": -1.2921, "longitude": 36.8219},
                "cache_duration_hours": 24
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                cached_items = data.get("cached_items", {})
                offline_ready = data.get("offline_mode_ready", False)
                
                self.log_result(
                    "Offline Caching - Content Cache",
                    len(cached_items) >= 3,
                    f"Cached {len(cached_items)} content types, Offline ready: {offline_ready}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "Offline Caching - Content Cache",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Offline Caching - Content Cache", False, f"Exception: {str(e)}", critical=True)
        
        # Test 2: Offline Mode Content Access
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/personalized-content/multilingual", json={
                "latitude": -1.2921,
                "longitude": 36.8219,
                "preferred_language": "en",
                "offline_mode": True,
                "user_age": 25,
                "audio": {"quality": "high", "volume": 0.8},
                "theme": "dark"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                offline_mode = data.get("offline_mode", False)
                content_source = data.get("content_source", "unknown")
                radio_streams = data.get("radio_streams", {})
                
                self.log_result(
                    "Offline Caching - Offline Mode Access",
                    offline_mode and radio_streams,
                    f"Offline: {offline_mode}, Source: {content_source}, Streams: {'✓' if radio_streams else '✗'}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "Offline Caching - Offline Mode Access",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("Offline Caching - Offline Mode Access", False, f"Exception: {str(e)}", critical=True)

    def test_external_source_error_fixes(self):
        """Test Fixed External Source Errors with Fallback Mechanisms"""
        print("\n🔧 Testing External Source Error Fixes...")
        
        # Test 1: Radio Streams with Fallback
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/radio/streams")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                main_station = data.get("main_station", {})
                alternative_streams = data.get("alternative_streams", [])
                
                self.log_result(
                    "External Sources - Radio Streams",
                    main_station and len(alternative_streams) >= 5,
                    f"Main station: {main_station.get('name', 'Unknown')}, Alternatives: {len(alternative_streams)}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "External Sources - Radio Streams",
                    False,
                    f"HTTP {response.status_code}",
                    response_time,
                    critical=True
                )
        except Exception as e:
            self.log_result("External Sources - Radio Streams", False, f"Exception: {str(e)}", critical=True)
        
        # Test 2: Stream Accessibility Check
        try:
            # Get stream URLs first
            response = self.session.get(f"{API_BASE}/radio/streams")
            if response.status_code == 200:
                data = response.json()
                all_streams = [data.get("main_station", {})] + data.get("alternative_streams", [])
                accessible_streams = 0
                
                for stream in all_streams[:8]:  # Test first 8 streams
                    stream_url = stream.get("streamUrl", "")
                    stream_name = stream.get("name", "Unknown")
                    
                    if stream_url:
                        try:
                            start_time = time.time()
                            stream_response = self.session.head(stream_url, allow_redirects=True, timeout=10)
                            stream_response_time = (time.time() - start_time) * 1000
                            
                            if stream_response.status_code == 200:
                                content_type = stream_response.headers.get('content-type', '')
                                icy_headers = [h for h in stream_response.headers.keys() if h.lower().startswith('icy-')]
                                
                                if 'audio' in content_type.lower() or icy_headers:
                                    accessible_streams += 1
                                    self.log_result(
                                        f"Stream Accessibility - {stream_name}",
                                        True,
                                        f"Accessible with {len(icy_headers)} ICY headers",
                                        stream_response_time
                                    )
                                else:
                                    self.log_result(
                                        f"Stream Accessibility - {stream_name}",
                                        False,
                                        f"Not audio stream: {content_type}",
                                        stream_response_time
                                    )
                            else:
                                self.log_result(
                                    f"Stream Accessibility - {stream_name}",
                                    False,
                                    f"HTTP {stream_response.status_code}",
                                    stream_response_time
                                )
                        except Exception as e:
                            self.log_result(f"Stream Accessibility - {stream_name}", False, f"Exception: {str(e)}")
                
                # Overall accessibility assessment
                accessibility_rate = (accessible_streams / len(all_streams[:8])) * 100 if all_streams else 0
                self.log_result(
                    "External Sources - Stream Accessibility",
                    accessibility_rate >= 50,  # 50% threshold
                    f"{accessible_streams}/{len(all_streams[:8])} streams accessible ({accessibility_rate:.1f}%)",
                    critical=True
                )
        except Exception as e:
            self.log_result("External Sources - Stream Accessibility", False, f"Exception: {str(e)}", critical=True)
        
        # Test 3: Spotify Integration with Fallback
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/spotify/search", json={
                "query": "jazz music",
                "limit": 10
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", [])
                status = data.get("status", "unknown")
                
                self.log_result(
                    "External Sources - Spotify Fallback",
                    len(tracks) > 0,
                    f"Status: {status}, Tracks: {len(tracks)}",
                    response_time
                )
            else:
                self.log_result(
                    "External Sources - Spotify Fallback",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("External Sources - Spotify Fallback", False, f"Exception: {str(e)}")

    def test_voice_ai_integration(self):
        """Test Voice AI Integration"""
        print("\n🎤 Testing Voice AI Integration...")
        
        # Test voice commands
        voice_commands = [
            {"text": "play radio", "expected_intent": "play"},
            {"text": "pause music", "expected_intent": "pause"},
            {"text": "next station", "expected_intent": "next"},
            {"text": "volume up", "expected_intent": "volume_control"},
            {"text": "search for jazz music", "expected_intent": "search"},
            {"text": "tune to classical station", "expected_intent": "tune_station"}
        ]
        
        successful_commands = 0
        
        for command in voice_commands:
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/voice/interpret", json={
                    "text": command["text"],
                    "language": "en",
                    "context": "radio_control"
                })
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    intent = data.get("intent", "unknown")
                    confidence = data.get("confidence", 0)
                    
                    if confidence > 0.5:
                        successful_commands += 1
                        self.log_result(
                            f"Voice AI - '{command['text']}'",
                            True,
                            f"Intent: {intent}, Confidence: {confidence:.2f}",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Voice AI - '{command['text']}'",
                            False,
                            f"Low confidence: {confidence:.2f}",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Voice AI - '{command['text']}'",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Voice AI - '{command['text']}'", False, f"Exception: {str(e)}")
        
        # Overall voice AI assessment
        voice_success_rate = (successful_commands / len(voice_commands)) * 100
        self.log_result(
            "Voice AI Integration - Overall",
            voice_success_rate >= 70,
            f"{successful_commands}/{len(voice_commands)} commands successful ({voice_success_rate:.1f}%)",
            critical=True
        )

    def test_performance_and_stability(self):
        """Test Performance and Stability"""
        print("\n⚡ Testing Performance and Stability...")
        
        # Test critical endpoints performance
        critical_endpoints = [
            ("GET", "/", None),
            ("GET", "/station-info", None),
            ("POST", "/language/detect", {"latitude": -1.2921, "longitude": 36.8219}),
            ("GET", "/satellite/status", None),
            ("POST", "/voice/interpret", {"text": "play music"})
        ]
        
        response_times = []
        successful_endpoints = 0
        
        for method, endpoint, payload in critical_endpoints:
            try:
                start_time = time.time()
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                else:
                    response = self.session.post(f"{API_BASE}{endpoint}", json=payload)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_endpoints += 1
                    
                fast_response = response_time < 2000  # 2 second threshold
                self.log_result(
                    f"Performance - {endpoint}",
                    response.status_code == 200 and fast_response,
                    f"HTTP {response.status_code}, Response time: {response_time:.0f}ms",
                    response_time
                )
                
            except Exception as e:
                self.log_result(f"Performance - {endpoint}", False, f"Exception: {str(e)}")
        
        # Calculate average response time
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            self.log_result(
                "Performance - Average Response Time",
                avg_response_time < 1000,  # 1 second average threshold
                f"Average: {avg_response_time:.0f}ms, All endpoints: {successful_endpoints}/{len(critical_endpoints)}",
                avg_response_time,
                critical=True
            )

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
            "average_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0
        }

    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests for geographic coverage enhancements"""
        print("🌍 STARTING COMPREHENSIVE KAGEMA FM GEOGRAPHIC COVERAGE BACKEND TESTING")
        print("="*80)
        print("Testing Focus Areas:")
        print("• Enhanced SoundCast Service with North/South American coverage")
        print("• New Satellite Radio Integration (SiriusXM, Global Satellite Network)")
        print("• Advanced Geolocation Features (GPS-based discovery, offline caching)")
        print("• Fixed External Source Errors with proper fallback mechanisms")
        print("="*80)
        
        # Test backend accessibility first
        if not self.test_backend_accessibility():
            print("❌ Backend not accessible. Stopping tests.")
            return self.get_summary()
        
        # Run all test suites
        self.test_enhanced_soundcast_service()
        self.test_satellite_radio_integration()
        self.test_advanced_geolocation_features()
        self.test_offline_caching_features()
        self.test_external_source_error_fixes()
        self.test_voice_ai_integration()
        self.test_performance_and_stability()
        
        return self.get_summary()

    def get_summary(self):
        """Get comprehensive test summary"""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE KAGEMA FM GEOGRAPHIC COVERAGE TESTING COMPLETE")
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
        
        # Geographic Coverage Assessment
        soundcast_tests = [r for r in self.results if "SoundCast Coverage" in r["test"]]
        if soundcast_tests:
            soundcast_success_rate = (sum(1 for t in soundcast_tests if t["success"]) / len(soundcast_tests)) * 100
            print(f"\n🌎 GEOGRAPHIC COVERAGE ASSESSMENT:")
            print(f"   SoundCast Coverage Success Rate: {soundcast_success_rate:.1f}%")
            
        satellite_tests = [r for r in self.results if "Satellite Integration" in r["test"]]
        if satellite_tests:
            satellite_success_rate = (sum(1 for t in satellite_tests if t["success"]) / len(satellite_tests)) * 100
            print(f"   Satellite Integration Success Rate: {satellite_success_rate:.1f}%")
        
        # Quality Assessment
        success_rate = metrics.get('success_rate_percent', 0)
        critical_failures = metrics.get('critical_failures', 0)
        
        print(f"\n🎯 DEPLOYMENT READINESS:")
        if success_rate >= 95 and critical_failures == 0:
            print("   ✅ EXCELLENT - Production ready with outstanding geographic coverage")
        elif success_rate >= 85 and critical_failures <= 2:
            print("   ✅ GOOD - Production ready with minor geographic coverage issues")
        elif success_rate >= 75:
            print("   ⚠️ FAIR - Geographic coverage needs attention before production")
        else:
            print("   ❌ POOR - Significant geographic coverage issues require immediate attention")
        
        # Failed Tests Details
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for i, result in enumerate([r for r in self.results if not r['success']][:10], 1):
                print(f"   {i}. {result['test']}: {result['details']}")
                if result.get('critical'):
                    print(f"      ⚠️ CRITICAL FAILURE")
        
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
    """Main test execution for comprehensive geographic coverage testing"""
    tester = KagemaFMGeographicCoverageTester()
    results = tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["success_rate"] >= 85 and results["critical_failures"] <= 2:
        print(f"\n✅ GEOGRAPHIC COVERAGE TESTS PASSED ({results['success_rate']:.1f}% success rate)")
        return 0
    else:
        print(f"\n❌ GEOGRAPHIC COVERAGE TESTS FAILED ({results['success_rate']:.1f}% success rate, {results['critical_failures']} critical failures)")
        return 1

if __name__ == "__main__":
    exit(main())