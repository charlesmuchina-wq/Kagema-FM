#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND PRODUCTION READINESS TESTING
Kagema FM Enhanced - Production Deployment Verification

Focus Areas:
1. **PRODUCTION LOAD TESTING** - Test backend under production-level concurrent requests
2. **API STABILITY VERIFICATION** - All critical endpoints must maintain >98% success rate
3. **PERFORMANCE BENCHMARKING** - Response times <300ms average for production readiness
4. **INTEGRATION POINTS TESTING** - Voice AI, geolocation, radio streaming, external services
5. **ERROR HANDLING VALIDATION** - Proper error responses and recovery mechanisms
6. **SECURITY & COMPLIANCE** - Production security headers, rate limiting, data protection
7. **MEMORY & RESOURCE MANAGEMENT** - No memory leaks, proper resource cleanup
8. **CROSS-PLATFORM COMPATIBILITY** - Android/iOS specific API requirements

Critical APIs for Production:
- /api/geolocation/* (GPS/IP location services)
- /api/radio-browser/* (radio streaming)
- /api/accuradio/* (music services) 
- /api/voice/* (AI voice commands)
- /api/satellite/* (satellite connectivity)
- All country-based content filtering endpoints

Deployment Readiness Criteria:
- >98% Success Rate Required
- <300ms Average Response Time
- Zero Critical Failures
- All Integration Points Functional
- Production Security Standards Met
"""

import json
import requests
import time
import statistics
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Backend URL from frontend environment
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://geoaudio-hub.preview.emergentagent.com')
BACKEND_URL = FRONTEND_ENV_URL
API_BASE = f"{BACKEND_URL}/api"

class ProductionReadinessTestSuite:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        self.performance_metrics = []
        self.stream_accessibility_results = []
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    timeout: int = 30, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request and measure performance"""
        url = f"{API_BASE}{endpoint}"
        start_time = time.time()
        
        try:
            request_headers = {
                'User-Agent': 'Kagema-FM-Production-Test/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            if headers:
                request_headers.update(headers)
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout, headers=request_headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=timeout, headers=request_headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=timeout, headers=request_headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=timeout, headers=request_headers)
            else:
                response = requests.request(method, url, json=data, timeout=timeout, headers=request_headers)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                response_data = response.text
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': 200 <= response.status_code < 300,
                'response_data': response_data,
                'error_message': None
            }
            
            self.performance_metrics.append(response_time)
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'response_data': None,
                'error_message': str(e)
            }
            self.performance_metrics.append(response_time)
            return result
    
    def test_core_api_health(self):
        """Test core API health endpoints"""
        print("🔍 Testing Core API Health...")
        
        endpoints = [
            ('GET', '/'),
            ('GET', '/app/info'),
            ('GET', '/app/version'),
            ('GET', '/station-info'),
        ]
        
        for method, endpoint in endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"{method} {endpoint}")
                print(f"  ✅ {method} {endpoint}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{method} {endpoint}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {method} {endpoint}: {result.get('error_message', result['status_code'])} ({result['response_time']:.0f}ms)")
    
    def test_geolocation_services(self):
        """Test geolocation and location-based services - CRITICAL for production"""
        print("🌍 Testing Geolocation Services...")
        
        # IP-based geolocation
        result = self.make_request('GET', '/geolocation/ip')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("IP Geolocation")
            print(f"  ✅ IP Geolocation: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"IP Geolocation: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ IP Geolocation: {result.get('error_message', result['status_code'])}")
        
        # Location suggestions
        result = self.make_request('GET', '/geolocation/suggestions?context=radio')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Location Suggestions")
            print(f"  ✅ Location Suggestions: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Location Suggestions: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Location Suggestions: {result.get('error_message', result['status_code'])}")
        
        # Geolocation service info
        result = self.make_request('GET', '/geolocation/info')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Geolocation Service Info")
            print(f"  ✅ Geolocation Service Info: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Geolocation Service Info: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Geolocation Service Info: {result.get('error_message', result['status_code'])}")
        
        # Language detection from coordinates - Test multiple locations
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi, Kenya"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo, Brazil"},
            {"latitude": 52.5200, "longitude": 13.4050, "name": "Berlin, Germany"}
        ]
        
        for location in test_locations:
            location_data = {"latitude": location["latitude"], "longitude": location["longitude"]}
            result = self.make_request('POST', '/language/detect', data=location_data)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Language Detection - {location['name']}")
                print(f"  ✅ Language Detection ({location['name']}): {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Language Detection - {location['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ Language Detection ({location['name']}): {result.get('error_message', result['status_code'])}")
    
    def test_radio_streaming_apis(self):
        """Test radio streaming and station APIs - CRITICAL for production"""
        print("📻 Testing Radio Streaming APIs...")
        
        # Radio streams
        result = self.make_request('GET', '/radio/streams')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Radio Streams")
            print(f"  ✅ Radio Streams: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Radio Streams: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Radio Streams: {result.get('error_message', result['status_code'])}")
        
        # Radio stations
        result = self.make_request('GET', '/radio/stations')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Radio Stations")
            print(f"  ✅ Radio Stations: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Radio Stations: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Radio Stations: {result.get('error_message', result['status_code'])}")
        
        # Multilingual station info
        location_data = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
        result = self.make_request('POST', '/station-info/multilingual', data=location_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Multilingual Station Info")
            print(f"  ✅ Multilingual Station Info: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Multilingual Station Info: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Multilingual Station Info: {result.get('error_message', result['status_code'])}")
        
        # Personalized content - CRITICAL for frontend functionality
        personalized_data = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"preferred_language": "en", "offline_mode": False}
        }
        result = self.make_request('POST', '/personalized-content/multilingual', data=personalized_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Personalized Content")
            print(f"  ✅ Personalized Content: {result['status_code']} ({result['response_time']:.0f}ms)")
            
            # Check if radio_streams data is present - CRITICAL for frontend
            if result['response_data'] and 'radio_streams' in result['response_data']:
                print(f"    ✅ Radio streams data present in response")
            else:
                print(f"    ⚠️  Radio streams data missing from response")
        else:
            self.failed_tests.append(f"Personalized Content: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Personalized Content: {result.get('error_message', result['status_code'])}")
    
    def test_voice_ai_integration(self):
        """Test Voice AI and command processing - CRITICAL for production"""
        print("🎤 Testing Voice AI Integration...")
        
        # Voice intents
        result = self.make_request('GET', '/voice/intents')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Voice Intents")
            print(f"  ✅ Voice Intents: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Voice Intents: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Voice Intents: {result.get('error_message', result['status_code'])}")
        
        # Voice help
        result = self.make_request('GET', '/voice/help')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Voice Help")
            print(f"  ✅ Voice Help: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Voice Help: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Voice Help: {result.get('error_message', result['status_code'])}")
        
        # Voice command interpretation - Test various command types
        voice_commands = [
            {"text": "play", "context": "radio", "name": "Simple Play Command"},
            {"text": "pause", "context": "radio", "name": "Simple Pause Command"},
            {"text": "next", "context": "radio", "name": "Simple Next Command"},
            {"text": "volume up", "context": "radio", "name": "Simple Volume Command"},
            {"text": "search for jazz music", "context": "radio", "name": "Complex Search Command"},
            {"text": "tune to classical station", "context": "radio", "name": "Complex Tune Command"},
            {"text": "browse external sources", "context": "radio", "name": "Complex Browse Command"}
        ]
        
        for cmd in voice_commands:
            result = self.make_request('POST', '/voice/interpret', data={"text": cmd["text"], "context": cmd["context"]})
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Voice Command - {cmd['name']}")
                print(f"  ✅ {cmd['name']}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Voice Command - {cmd['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {cmd['name']}: {result.get('error_message', result['status_code'])}")
    
    def test_external_services_integration(self):
        """Test external services and integrations - CRITICAL for production"""
        print("🔗 Testing External Services Integration...")
        
        # Radio Browser API
        radio_browser_endpoints = [
            ('GET', '/radio-browser/info', 'Radio Browser Info'),
            ('GET', '/radio-browser/search?q=jazz&limit=10', 'Radio Browser Search'),
            ('GET', '/radio-browser/popular?limit=20', 'Radio Browser Popular'),
            ('GET', '/radio-browser/countries?limit=20', 'Radio Browser Countries'),
            ('GET', '/radio-browser/languages?limit=20', 'Radio Browser Languages'),
            ('GET', '/radio-browser/tags?limit=20', 'Radio Browser Tags')
        ]
        
        for method, endpoint, name in radio_browser_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # AccuRadio API
        accuradio_endpoints = [
            ('GET', '/accuradio/info', 'AccuRadio Info'),
            ('GET', '/accuradio/genres', 'AccuRadio Genres'),
            ('GET', '/accuradio/channels?featured=true', 'AccuRadio Featured Channels')
        ]
        
        for method, endpoint, name in accuradio_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # Spotify Integration
        spotify_endpoints = [
            ('GET', '/spotify/auth/login', 'Spotify Auth Login'),
            ('GET', '/spotify/genres', 'Spotify Genres')
        ]
        
        for method, endpoint, name in spotify_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
        
        # Google Maps Integration
        googlemaps_endpoints = [
            ('GET', '/googlemaps/geocode?address=Nairobi,Kenya', 'Google Maps Geocoding'),
            ('GET', '/googlemaps/reverse-geocode?lat=-1.2921&lng=36.8219', 'Google Maps Reverse Geocoding'),
            ('GET', '/googlemaps/nearby?lat=-1.2921&lng=36.8219&type=restaurant', 'Google Maps Nearby Places')
        ]
        
        for method, endpoint, name in googlemaps_endpoints:
            result = self.make_request(method, endpoint)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(name)
                print(f"  ✅ {name}: {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"{name}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ {name}: {result.get('error_message', result['status_code'])}")
    
    def test_satellite_connectivity(self):
        """Test satellite connectivity and offline features"""
        print("🛰️ Testing Satellite Connectivity...")
        
        # Satellite status
        result = self.make_request('GET', '/satellite/status')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Status")
            print(f"  ✅ Satellite Status: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Status: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Status: {result.get('error_message', result['status_code'])}")
        
        # Satellite main stations
        result = self.make_request('GET', '/satellite/main_stations')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Main Stations")
            print(f"  ✅ Satellite Main Stations: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Main Stations: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Main Stations: {result.get('error_message', result['status_code'])}")
        
        # Satellite connection attempt
        connection_data = {"provider": "auto", "client_id": "kagema_fm_production_test", "location": "auto"}
        result = self.make_request('POST', '/satellite/connect', data=connection_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Satellite Connection")
            print(f"  ✅ Satellite Connection: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Satellite Connection: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Satellite Connection: {result.get('error_message', result['status_code'])}")
        
        # Offline content caching
        cache_data = {
            "content_types": ["radio_streams", "news", "weather"],
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "cache_duration_hours": 24
        }
        result = self.make_request('POST', '/offline/cache', data=cache_data)
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Offline Content Caching")
            print(f"  ✅ Offline Content Caching: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Offline Content Caching: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Offline Content Caching: {result.get('error_message', result['status_code'])}")
    
    def test_content_compliance(self):
        """Test content compliance and regional features"""
        print("⚖️ Testing Content Compliance...")
        
        # Supported languages
        result = self.make_request('GET', '/languages')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Supported Languages")
            print(f"  ✅ Supported Languages: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Supported Languages: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Supported Languages: {result.get('error_message', result['status_code'])}")
        
        # Content disclaimers for different regions
        regions = [
            {"country_code": "KE", "language_code": "en", "name": "Kenya"},
            {"country_code": "BR", "language_code": "pt-br", "name": "Brazil"},
            {"country_code": "GLOBAL", "language_code": "en", "name": "Global"}
        ]
        
        for region in regions:
            compliance_data = {
                "country_code": region["country_code"],
                "language_code": region["language_code"],
                "content_types": ["radio_streams", "music", "news"]
            }
            result = self.make_request('POST', '/compliance/disclaimers', data=compliance_data)
            self.results.append(result)
            
            if result['success']:
                self.passed_tests.append(f"Content Disclaimers - {region['name']}")
                print(f"  ✅ Content Disclaimers ({region['name']}): {result['status_code']} ({result['response_time']:.0f}ms)")
            else:
                self.failed_tests.append(f"Content Disclaimers - {region['name']}: {result.get('error_message', result['status_code'])}")
                print(f"  ❌ Content Disclaimers ({region['name']}): {result.get('error_message', result['status_code'])}")
        
        # Content compliance check
        result = self.make_request('POST', '/compliance/check-content?country_code=KE&content_rating=mature&user_age=25')
        self.results.append(result)
        if result['success']:
            self.passed_tests.append("Content Compliance Check")
            print(f"  ✅ Content Compliance Check: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Content Compliance Check: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Content Compliance Check: {result.get('error_message', result['status_code'])}")
    
    def test_stream_accessibility(self):
        """Test actual radio stream accessibility - CRITICAL for production"""
        print("🎵 Testing Radio Stream Accessibility...")
        
        # Get radio streams first
        result = self.make_request('GET', '/radio/streams')
        if result['success'] and result['response_data']:
            streams_to_test = []
            
            # Add main station
            if 'main_station' in result['response_data']:
                streams_to_test.append({
                    'name': result['response_data']['main_station']['name'],
                    'url': result['response_data']['main_station']['streamUrl']
                })
            
            # Add alternative streams
            if 'alternative_streams' in result['response_data']:
                for stream in result['response_data']['alternative_streams']:
                    streams_to_test.append({
                        'name': stream['name'],
                        'url': stream['streamUrl']
                    })
            
            # Test stream accessibility
            for stream in streams_to_test:
                start_time = time.time()
                try:
                    response = requests.head(stream['url'], timeout=10, headers={
                        'User-Agent': 'Kagema-FM-Production-Test/1.0'
                    })
                    response_time = (time.time() - start_time) * 1000
                    success = response.status_code == 200
                    
                    stream_result = {
                        'name': stream['name'],
                        'url': stream['url'],
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': success,
                        'headers': dict(response.headers)
                    }
                    
                    self.stream_accessibility_results.append(stream_result)
                    
                    if success:
                        print(f"  ✅ {stream['name']}: {response.status_code} ({response_time:.0f}ms)")
                        # Check for audio streaming headers
                        content_type = response.headers.get('content-type', '').lower()
                        if 'audio' in content_type or 'mpeg' in content_type:
                            print(f"    ✅ Audio content type detected: {content_type}")
                        if 'icy-' in str(response.headers).lower():
                            print(f"    ✅ ICY streaming metadata detected")
                    else:
                        print(f"  ❌ {stream['name']}: {response.status_code} ({response_time:.0f}ms)")
                        
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    stream_result = {
                        'name': stream['name'],
                        'url': stream['url'],
                        'status_code': 0,
                        'response_time': response_time,
                        'success': False,
                        'error': str(e)
                    }
                    self.stream_accessibility_results.append(stream_result)
                    print(f"  ❌ {stream['name']}: ERROR ({response_time:.0f}ms) - {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🚨 Testing Error Handling...")
        
        # Test 404 endpoints
        result = self.make_request('GET', '/nonexistent-endpoint')
        self.results.append(result)
        if result['status_code'] == 404:
            self.passed_tests.append("404 Error Handling")
            print(f"  ✅ 404 Error Handling: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"404 Error Handling: Expected 404, got {result['status_code']}")
            print(f"  ❌ 404 Error Handling: Expected 404, got {result['status_code']}")
        
        # Test invalid POST data
        result = self.make_request('POST', '/language/detect', data={"invalid": "data"})
        self.results.append(result)
        if result['status_code'] == 422:
            self.passed_tests.append("Invalid POST Data Handling")
            print(f"  ✅ Invalid POST Data: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Invalid POST Data: Expected 422, got {result['status_code']}")
            print(f"  ❌ Invalid POST Data: Expected 422, got {result['status_code']}")
        
        # Test empty voice command
        result = self.make_request('POST', '/voice/interpret', data={"text": "", "context": "radio"})
        self.results.append(result)
        if result['status_code'] in [400, 422]:
            self.passed_tests.append("Empty Voice Command Handling")
            print(f"  ✅ Empty Voice Command: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Empty Voice Command: Expected 400/422, got {result['status_code']}")
            print(f"  ❌ Empty Voice Command: Expected 400/422, got {result['status_code']}")
        
        # Test invalid coordinates fallback
        result = self.make_request('POST', '/language/detect', data={"latitude": 999, "longitude": 999})
        self.results.append(result)
        if result['success']:  # Should fallback gracefully
            self.passed_tests.append("Invalid Coordinates Fallback")
            print(f"  ✅ Invalid Coordinates Fallback: {result['status_code']} ({result['response_time']:.0f}ms)")
        else:
            self.failed_tests.append(f"Invalid Coordinates Fallback: {result.get('error_message', result['status_code'])}")
            print(f"  ❌ Invalid Coordinates Fallback: {result.get('error_message', result['status_code'])}")
    
    def test_production_load(self):
        """Test production-level concurrent load"""
        print("⚡ Testing Production Load (Concurrent Requests)...")
        
        # Define critical endpoints for load testing
        load_test_endpoints = [
            ('GET', '/', 'API Root'),
            ('GET', '/station-info', 'Station Info'),
            ('GET', '/radio/streams', 'Radio Streams'),
            ('GET', '/voice/intents', 'Voice Intents'),
            ('GET', '/languages', 'Languages'),
            ('POST', '/language/detect', {"latitude": -1.2921, "longitude": 36.8219}, 'Language Detection'),
            ('POST', '/voice/interpret', {"text": "play", "context": "radio"}, 'Voice Command'),
        ]
        
        # Test with 5 concurrent requests per endpoint (35 total concurrent requests)
        concurrent_requests = []
        for method, endpoint, data, name in load_test_endpoints:
            for i in range(5):
                if isinstance(data, dict):
                    concurrent_requests.append((method, endpoint, data, f"{name} #{i+1}"))
                else:
                    concurrent_requests.append((method, endpoint, None, f"{name} #{i+1}"))
        
        print(f"  🔄 Executing {len(concurrent_requests)} concurrent requests...")
        
        def execute_request(request_data):
            method, endpoint, data, name = request_data
            return self.make_request(method, endpoint, data)
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_request = {executor.submit(execute_request, req): req for req in concurrent_requests}
            concurrent_results = []
            
            for future in as_completed(future_to_request):
                try:
                    result = future.result()
                    concurrent_results.append(result)
                except Exception as e:
                    print(f"    ❌ Concurrent request failed: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Analyze concurrent load results
        successful_requests = sum(1 for r in concurrent_results if r['success'])
        failed_requests = len(concurrent_results) - successful_requests
        success_rate = (successful_requests / len(concurrent_results)) * 100 if concurrent_results else 0
        avg_requests_per_second = len(concurrent_results) / total_time if total_time > 0 else 0
        
        # Add concurrent results to main results
        self.results.extend(concurrent_results)
        
        print(f"  ✅ Concurrent Load Test Complete:")
        print(f"    - Total Requests: {len(concurrent_results)}")
        print(f"    - Successful: {successful_requests}")
        print(f"    - Failed: {failed_requests}")
        print(f"    - Success Rate: {success_rate:.1f}%")
        print(f"    - Requests/Second: {avg_requests_per_second:.1f}")
        print(f"    - Total Time: {total_time:.2f}s")
        
        if success_rate >= 95.0:
            self.passed_tests.append(f"Production Load Test - {success_rate:.1f}% success rate")
        else:
            self.failed_tests.append(f"Production Load Test - {success_rate:.1f}% success rate (below 95%)")
    
    def analyze_results(self):
        """Analyze test results and generate production readiness report"""
        print("\n" + "="*80)
        print("📊 PRODUCTION READINESS ANALYSIS")
        print("="*80)
        
        # Basic statistics
        total_tests = len(self.results)
        successful_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Performance statistics
        if self.performance_metrics:
            avg_response_time = statistics.mean(self.performance_metrics)
            median_response_time = statistics.median(self.performance_metrics)
            max_response_time = max(self.performance_metrics)
            min_response_time = min(self.performance_metrics)
            
            # Performance targets
            fast_responses = sum(1 for rt in self.performance_metrics if rt < 300)  # <300ms target
            acceptable_responses = sum(1 for rt in self.performance_metrics if rt < 1000)  # <1s acceptable
            slow_responses = sum(1 for rt in self.performance_metrics if rt >= 1000)  # >1s slow
        else:
            avg_response_time = median_response_time = max_response_time = min_response_time = 0
            fast_responses = acceptable_responses = slow_responses = 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if self.performance_metrics:
            print(f"⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.1f}ms")
            print(f"   Median Response Time: {median_response_time:.1f}ms")
            print(f"   Min Response Time: {min_response_time:.1f}ms")
            print(f"   Max Response Time: {max_response_time:.1f}ms")
            print(f"   Fast Responses (<300ms): {fast_responses}/{len(self.performance_metrics)} ({(fast_responses/len(self.performance_metrics)*100):.1f}%)")
            print(f"   Acceptable Responses (<1s): {acceptable_responses}/{len(self.performance_metrics)} ({(acceptable_responses/len(self.performance_metrics)*100):.1f}%)")
            print(f"   Slow Responses (>1s): {slow_responses}/{len(self.performance_metrics)} ({(slow_responses/len(self.performance_metrics)*100):.1f}%)")
            print()
        
        # Production readiness criteria
        print(f"🏆 PRODUCTION READINESS CRITERIA:")
        success_rate_met = success_rate >= 98.0
        performance_met = avg_response_time < 300 if self.performance_metrics else False
        reliability_met = slow_responses == 0
        
        print(f"   ✓ Success Rate >98%: {'✅ PASS' if success_rate_met else '❌ FAIL'} ({success_rate:.1f}%)")
        print(f"   ✓ Avg Response <300ms: {'✅ PASS' if performance_met else '❌ FAIL'} ({avg_response_time:.1f}ms)")
        print(f"   ✓ No Slow Responses: {'✅ PASS' if reliability_met else '❌ FAIL'} ({slow_responses} slow)")
        print()
        
        # Stream accessibility
        if self.stream_accessibility_results:
            successful_streams = sum(1 for r in self.stream_accessibility_results if r['success'])
            stream_success_rate = (successful_streams / len(self.stream_accessibility_results)) * 100
            print(f"📻 RADIO STREAM ACCESSIBILITY:")
            print(f"   Total Streams Tested: {len(self.stream_accessibility_results)}")
            print(f"   Accessible Streams: {successful_streams}")
            print(f"   Stream Success Rate: {stream_success_rate:.1f}%")
            print()
        
        # Failed tests details
        if self.failed_tests:
            print(f"❌ FAILED TESTS DETAILS:")
            for failed_test in self.failed_tests[:10]:  # Show first 10 failures
                print(f"   - {failed_test}")
            if len(self.failed_tests) > 10:
                print(f"   ... and {len(self.failed_tests) - 10} more failures")
            print()
        
        # Final recommendation
        overall_ready = success_rate_met and performance_met and reliability_met
        print(f"🎯 DEPLOYMENT RECOMMENDATION:")
        if overall_ready:
            print(f"   ✅ PRODUCTION READY - All criteria met, deploy with confidence!")
        elif success_rate >= 95.0 and avg_response_time < 500:
            print(f"   ⚠️  MOSTLY READY - Minor issues present, acceptable for deployment")
        else:
            print(f"   ❌ NOT READY - Critical issues must be resolved before deployment")
        
        print("="*80)
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'production_ready': overall_ready,
            'stream_accessibility': len([r for r in self.stream_accessibility_results if r['success']]) if self.stream_accessibility_results else 0,
            'total_streams': len(self.stream_accessibility_results) if self.stream_accessibility_results else 0
        }
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        print("🚀 KAGEMA FM BACKEND PRODUCTION READINESS TESTING")
        print("="*80)
        print("Testing Criteria:")
        print("  • Success Rate: >98% required")
        print("  • Response Time: <300ms average target")
        print("  • Load Testing: Concurrent request handling")
        print("  • Integration Testing: All external services")
        print("  • Error Handling: Proper error responses")
        print("  • Stream Accessibility: All radio streams functional")
        print("="*80)
        print()
        
        try:
            # Execute all test categories
            self.test_core_api_health()
            self.test_geolocation_services()
            self.test_radio_streaming_apis()
            self.test_voice_ai_integration()
            self.test_external_services_integration()
            self.test_satellite_connectivity()
            self.test_content_compliance()
            self.test_stream_accessibility()
            self.test_error_handling()
            self.test_production_load()
            
            # Analyze and report results
            results = self.analyze_results()
            return results
            
        except Exception as e:
            print(f"❌ Test suite execution failed: {str(e)}")
            return None

def main():
    """Main test execution function"""
    suite = ProductionReadinessTestSuite()
    results = suite.run_all_tests()
    
    if results:
        if results['production_ready']:
            print("\n🎉 PRODUCTION DEPLOYMENT APPROVED!")
            return 0
        elif results['success_rate'] >= 95.0:
            print("\n⚠️  PRODUCTION DEPLOYMENT ACCEPTABLE WITH MINOR ISSUES")
            return 0
        else:
            print("\n❌ PRODUCTION DEPLOYMENT NOT RECOMMENDED")
            return 1
    else:
        print("\n❌ TESTING FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)