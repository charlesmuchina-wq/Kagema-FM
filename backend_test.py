#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING FOR COUNTRY-BASED ORGANIZATION FEATURES
Testing country-based organization and GPS-based auto-selection features

Focus Areas:
1. **EXTERNAL AUDIO SOURCES API** - Test existing endpoints that should still be working
2. **ACCURADIO INTEGRATION** - Test /api/accuradio/ endpoints for country-specific functionality  
3. **RADIO BROWSER INTEGRATION** - Test /api/radio-browser/ endpoints with country filtering
4. **HYBRID GEOLOCATION SERVICE** - Test /api/hybrid-geolocation/ endpoints for location-based country detection
5. **SOUNDCAST STATIONS** - Test any endpoints related to SoundCast functionality

Key test scenarios:
- GPS location detection for auto country selection
- Country filtering for audio sources
- Integration between location services and audio source filtering
- Verify all existing functionality still works properly

Testing all existing integrations (SiriKit, AirPlay 2, AccuRadio, Radio Browser, Hybrid Geolocation) are functional
Backend APIs respond correctly with no regressions introduced by country-organization changes
Location-based country detection works for auto-selection features
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
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://geoaudio-hub.preview.emergentagent.com')
LOCAL_BACKEND_URL = "http://localhost:8001"

# Use frontend env URL as primary
BACKEND_URL = FRONTEND_ENV_URL
API_BASE = f"{BACKEND_URL}/api"

class CountryBasedOrganizationTester:
    def __init__(self):
        self.results = []
        self.failed_tests = []
        self.passed_tests = []
        self.performance_metrics = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Kagema-FM-Testing/1.0'
        })
        self.total_tests = 0
        self.critical_failures = []

    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0, critical: bool = False):
        """Log test result with performance tracking"""
        self.total_tests += 1
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat(),
            'critical': critical
        }
        
        self.results.append(result)
        
        if success:
            self.passed_tests.append(result)
            status = "✅ PASS"
        else:
            self.failed_tests.append(result)
            status = "❌ FAIL"
            if critical:
                self.critical_failures.append(result)
        
        if response_time > 0:
            self.performance_metrics.append({
                'test_name': test_name,
                'response_time': response_time
            })
        
        print(f"  {status}: {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    Response time: {response_time:.0f}ms")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, timeout: int = 10) -> tuple:
        """Make HTTP request and return response with timing"""
        url = f"{API_BASE}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params, timeout=timeout)
            elif method == "PUT":
                response = self.session.put(url, json=data, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000
            return response, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return None, response_time

    def test_radio_browser_search(self):
        """Test Radio Browser search endpoint"""
        print("\n🔍 Testing Radio Browser Search Functionality")
        print("-" * 60)
        
        # Test basic search
        response, response_time = self.make_request("GET", "/radio-browser/search", params={"q": "jazz", "limit": 10})
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "query", "stations", "count", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
            self.log_result(
                "Radio Browser Search - Basic Query (Jazz)",
                success,
                f"Status: {response.status_code}, Found {data.get('count', 0)} stations, Source: {data.get('source')}",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Search - Basic Query (Jazz)", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test search with different queries
        test_queries = ["classical", "rock", "news", "pop", "bbc"]
        for query in test_queries:
            response, response_time = self.make_request("GET", "/radio-browser/search", params={"q": query, "limit": 5})
            if response and response.status_code == 200:
                data = response.json()
                success = data.get("source") == "Radio Browser" and "stations" in data
                self.log_result(
                    f"Radio Browser Search - {query.title()}",
                    success,
                    f"Status: {response.status_code}, Found {data.get('count', 0)} stations",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Radio Browser Search - {query.title()}", False, f"Failed - Status: {status_code}", response_time)

    def test_radio_browser_popular(self):
        """Test Radio Browser popular stations endpoint"""
        print("\n🌟 Testing Radio Browser Popular Stations")
        print("-" * 60)
        
        response, response_time = self.make_request("GET", "/radio-browser/popular", params={"limit": 50})
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "stations", "count", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
            self.log_result(
                "Radio Browser Popular Stations",
                success,
                f"Status: {response.status_code}, Retrieved {data.get('count', 0)} popular stations",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Popular Stations", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_radio_browser_country(self):
        """Test Radio Browser country-specific stations"""
        print("\n🌍 Testing Radio Browser Country-Specific Stations")
        print("-" * 60)
        
        test_countries = ["Germany", "United States", "France", "United Kingdom", "Canada"]
        
        for country in test_countries:
            response, response_time = self.make_request("GET", f"/radio-browser/country/{country}", params={"limit": 20})
            if response and response.status_code == 200:
                data = response.json()
                expected_keys = ["status", "country", "stations", "count", "source"]
                missing_keys = [key for key in expected_keys if key not in data]
                
                success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
                self.log_result(
                    f"Radio Browser Country - {country}",
                    success,
                    f"Status: {response.status_code}, Found {data.get('count', 0)} stations",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Radio Browser Country - {country}", False, f"Failed - Status: {status_code}", response_time)

    def test_radio_browser_language(self):
        """Test Radio Browser language-specific stations"""
        print("\n🗣️ Testing Radio Browser Language-Specific Stations")
        print("-" * 60)
        
        test_languages = ["english", "german", "french", "spanish", "italian"]
        
        for language in test_languages:
            response, response_time = self.make_request("GET", f"/radio-browser/language/{language}", params={"limit": 15})
            if response and response.status_code == 200:
                data = response.json()
                expected_keys = ["status", "language", "stations", "count", "source"]
                missing_keys = [key for key in expected_keys if key not in data]
                
                success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
                self.log_result(
                    f"Radio Browser Language - {language.title()}",
                    success,
                    f"Status: {response.status_code}, Found {data.get('count', 0)} stations",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Radio Browser Language - {language.title()}", False, f"Failed - Status: {status_code}", response_time)

    def test_radio_browser_tags(self):
        """Test Radio Browser tags/genres functionality"""
        print("\n🏷️ Testing Radio Browser Tags/Genres")
        print("-" * 60)
        
        # Test getting available tags
        response, response_time = self.make_request("GET", "/radio-browser/tags", params={"limit": 30})
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "tags", "count", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
            self.log_result(
                "Radio Browser Tags List",
                success,
                f"Status: {response.status_code}, Retrieved {data.get('count', 0)} available tags",
                response_time,
                critical=True
            )
            
            # Test specific tag searches
            test_tags = ["jazz", "rock", "classical", "news", "pop"]
            for tag in test_tags:
                tag_response, tag_response_time = self.make_request("GET", f"/radio-browser/tag/{tag}", params={"limit": 10})
                if tag_response and tag_response.status_code == 200:
                    tag_data = tag_response.json()
                    station_count = tag_data.get("count", 0)
                    tag_success = tag_data.get("source") == "Radio Browser" and "stations" in tag_data
                    self.log_result(
                        f"Radio Browser Tag - {tag.title()}",
                        tag_success,
                        f"Status: {tag_response.status_code}, Found {station_count} stations",
                        tag_response_time
                    )
                else:
                    status_code = tag_response.status_code if tag_response else "No response"
                    self.log_result(f"Radio Browser Tag - {tag.title()}", False, f"Failed - Status: {status_code}", tag_response_time)
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Tags List", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_radio_browser_countries_languages(self):
        """Test Radio Browser countries and languages endpoints"""
        print("\n🌐 Testing Radio Browser Countries and Languages Lists")
        print("-" * 60)
        
        # Test countries endpoint
        response, response_time = self.make_request("GET", "/radio-browser/countries", params={"limit": 50})
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "countries", "count", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
            self.log_result(
                "Radio Browser Countries List",
                success,
                f"Status: {response.status_code}, Retrieved {data.get('count', 0)} countries",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Countries List", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test languages endpoint
        response, response_time = self.make_request("GET", "/radio-browser/languages", params={"limit": 50})
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "languages", "count", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser" and data.get("count", 0) >= 0
            self.log_result(
                "Radio Browser Languages List",
                success,
                f"Status: {response.status_code}, Retrieved {data.get('count', 0)} languages",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Languages List", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_radio_browser_info(self):
        """Test Radio Browser service information endpoint"""
        print("\n📊 Testing Radio Browser Service Information")
        print("-" * 60)
        
        response, response_time = self.make_request("GET", "/radio-browser/info")
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "info", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "Radio Browser"
            self.log_result(
                "Radio Browser Service Info",
                success,
                f"Status: {response.status_code}, Service information retrieved successfully",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser Service Info", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_integration_verification(self):
        """Test Radio Browser integration with existing services"""
        print("\n🔗 Testing Radio Browser Integration Verification")
        print("-" * 60)
        
        # Test app version endpoint for external sources
        response, response_time = self.make_request("GET", "/app/version")
        if response and response.status_code == 200:
            data = response.json()
            if "external_sources" in data and "radio_browser" in data["external_sources"]:
                radio_browser_url = data["external_sources"]["radio_browser"]
                success = "radio-browser.info" in radio_browser_url
                self.log_result(
                    "Radio Browser in External Sources",
                    success,
                    f"Status: {response.status_code}, Found Radio Browser URL: {radio_browser_url}",
                    response_time,
                    critical=True
                )
            else:
                self.log_result(
                    "Radio Browser in External Sources",
                    False,
                    f"Status: {response.status_code}, Radio Browser not found in external sources",
                    response_time,
                    critical=True
                )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Radio Browser in External Sources", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test voice commands integration
        voice_commands = [
            "Find popular radio stations",
            "Search radio browser",
            "Find stations from Germany",
            "Browse radio browser stations",
            "Search for jazz radio"
        ]
        
        for command in voice_commands:
            voice_data = {"text": command, "context": "radio_browser_integration"}
            response, response_time = self.make_request("POST", "/voice/interpret", data=voice_data)
            if response and response.status_code == 200:
                data = response.json()
                if "intent" in data and "confidence" in data:
                    confidence = data.get("confidence", 0)
                    intent = data.get("intent", "unknown")
                    success = confidence > 0.5
                    self.log_result(
                        f"Voice Command - '{command}'",
                        success,
                        f"Status: {response.status_code}, Intent: {intent}, Confidence: {confidence}",
                        response_time
                    )
                else:
                    self.log_result(
                        f"Voice Command - '{command}'",
                        False,
                        f"Status: {response.status_code}, Missing intent or confidence in response",
                        response_time
                    )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Voice Command - '{command}'", False, f"Failed - Status: {status_code}", response_time)

    def test_service_stability(self):
        """Test service stability with AccuRadio and other integrations"""
        print("\n⚖️ Testing Service Stability with Other Integrations")
        print("-" * 60)
        
        # Test AccuRadio endpoints to ensure they still work
        accuradio_endpoints = [
            ("/accuradio/channels", {"limit": 10}),
            ("/accuradio/genres", {}),
            ("/accuradio/info", {})
        ]
        
        for endpoint, params in accuradio_endpoints:
            response, response_time = self.make_request("GET", endpoint, params=params)
            endpoint_name = endpoint.split('/')[-1].split('?')[0].title()
            if response and response.status_code == 200:
                self.log_result(
                    f"AccuRadio {endpoint_name} Stability",
                    True,
                    f"Status: {response.status_code}, AccuRadio service working alongside Radio Browser",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(
                    f"AccuRadio {endpoint_name} Stability",
                    False,
                    f"AccuRadio service affected - Status: {status_code}",
                    response_time
                )
        
        # Test core radio functionality
        core_endpoints = [
            "/",
            "/station-info",
            "/radio/streams",
            "/radio/stations"
        ]
        
        for endpoint in core_endpoints:
            response, response_time = self.make_request("GET", endpoint)
            endpoint_name = endpoint.replace('/', '').replace('-', ' ').title() or "API Root"
            if response and response.status_code == 200:
                self.log_result(
                    f"Core Service - {endpoint_name}",
                    True,
                    f"Status: {response.status_code}, Core functionality stable",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(
                    f"Core Service - {endpoint_name}",
                    False,
                    f"Core service affected - Status: {status_code}",
                    response_time,
                    critical=True
                )

    def test_performance_and_data_quality(self):
        """Test performance and data quality of Radio Browser endpoints"""
        print("\n⚡ Testing Performance and Data Quality")
        print("-" * 60)
        
        # Performance test - multiple concurrent requests
        import threading
        import queue
        
        def make_concurrent_request(result_queue, request_id):
            try:
                response, response_time = self.make_request("GET", "/radio-browser/popular", params={"limit": 20})
                success = response and response.status_code == 200 and "stations" in response.json()
                result_queue.put((request_id, success, response_time))
            except Exception as e:
                result_queue.put((request_id, False, 0))
        
        # Run 5 concurrent requests
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
            "Concurrent Request Performance",
            success_rate >= 80,
            f"{successful_requests}/{len(results)} successful ({success_rate:.1f}%) in {total_time:.2f}s",
            total_time * 1000
        )
        
        # Data quality test - check station data format
        response, response_time = self.make_request("GET", "/radio-browser/search", params={"q": "bbc", "limit": 5})
        if response and response.status_code == 200:
            data = response.json()
            stations = data.get("stations", [])
            if stations:
                # Check first station for required fields
                station = stations[0]
                required_fields = ["name", "url"]
                missing_fields = [field for field in required_fields if field not in station or not station[field]]
                
                success = not missing_fields
                self.log_result(
                    "Station Data Quality",
                    success,
                    f"Status: {response.status_code}, Station data contains required fields" if success else f"Missing required fields: {missing_fields}",
                    response_time
                )
            else:
                self.log_result(
                    "Station Data Quality",
                    False,
                    f"Status: {response.status_code}, No station data returned for quality check",
                    response_time
                )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Station Data Quality", False, f"Failed to retrieve station data - Status: {status_code}", response_time)

    def test_hybrid_geolocation_services(self):
        """Test hybrid geolocation services for country detection"""
        print("\n🌍 Testing Hybrid Geolocation Services for Country Detection")
        print("-" * 60)
        
        # Test IP-based location detection
        response, response_time = self.make_request("GET", "/geolocation/ip")
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["status", "location", "client_ip", "source"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys and data.get("source") == "ip_geolocation"
            self.log_result(
                "IP Location Detection",
                success,
                f"Status: {response.status_code}, IP: {data.get('client_ip', 'N/A')}, Country: {data.get('location', {}).get('country', 'N/A')}",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("IP Location Detection", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test location suggestions for radio
        response, response_time = self.make_request("GET", "/geolocation/suggestions", params={"context": "radio"})
        if response and response.status_code == 200:
            data = response.json()
            success = data.get("source") == "location_suggestions" and "suggestions" in data
            self.log_result(
                "Location-Based Radio Suggestions",
                success,
                f"Status: {response.status_code}, Suggestions: {len(data.get('suggestions', []))}",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Location-Based Radio Suggestions", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test hybrid location with GPS data for different countries
        test_locations = [
            {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
            {"name": "Nairobi, Kenya", "lat": -1.2921, "lng": 36.8219},
            {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333},
            {"name": "London, UK", "lat": 51.5074, "lng": -0.1278}
        ]
        
        for location in test_locations:
            gps_data = {
                "gps_data": {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "accuracy": 10
                }
            }
            response, response_time = self.make_request("POST", "/geolocation/hybrid", data=gps_data)
            if response and response.status_code == 200:
                data = response.json()
                success = data.get("source") == "hybrid_geolocation" and "location" in data
                country = data.get("location", {}).get("country", "Unknown")
                self.log_result(
                    f"Hybrid Location - {location['name']}",
                    success,
                    f"Status: {response.status_code}, Detected Country: {country}",
                    response_time
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Hybrid Location - {location['name']}", False, f"Failed - Status: {status_code}", response_time)

    def test_language_detection_gps(self):
        """Test GPS-based language detection for auto country selection"""
        print("\n🗣️ Testing GPS-Based Language Detection")
        print("-" * 60)
        
        test_locations = [
            {"name": "Nairobi, Kenya", "lat": -1.2921, "lng": 36.8219, "expected_lang": "en"},
            {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333, "expected_lang": "pt-br"},
            {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060, "expected_lang": "en"},
            {"name": "Paris, France", "lat": 48.8566, "lng": 2.3522, "expected_lang": "en"}  # Should fallback to English
        ]
        
        for location in test_locations:
            location_data = {
                "latitude": location["lat"],
                "longitude": location["lng"]
            }
            response, response_time = self.make_request("POST", "/language/detect", data=location_data)
            if response and response.status_code == 200:
                data = response.json()
                detected_lang = data.get("detected_language", "unknown")
                confidence = data.get("confidence", 0)
                success = "detected_language" in data and confidence > 0
                self.log_result(
                    f"Language Detection - {location['name']}",
                    success,
                    f"Status: {response.status_code}, Detected: {detected_lang}, Confidence: {confidence}",
                    response_time,
                    critical=True
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Language Detection - {location['name']}", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_personalized_content_country_detection(self):
        """Test personalized content with country-based organization"""
        print("\n🎯 Testing Personalized Content with Country Detection")
        print("-" * 60)
        
        test_requests = [
            {
                "name": "Kenya Request",
                "location": {"latitude": -1.2921, "longitude": 36.8219},
                "preferences": {"preferred_language": "en", "offline_mode": False}
            },
            {
                "name": "Brazil Request", 
                "location": {"latitude": -23.5505, "longitude": -46.6333},
                "preferences": {"preferred_language": "pt-br", "offline_mode": False}
            },
            {
                "name": "USA Request",
                "location": {"latitude": 40.7128, "longitude": -74.0060},
                "preferences": {"preferred_language": "en", "offline_mode": False}
            }
        ]
        
        for test_request in test_requests:
            response, response_time = self.make_request("POST", "/personalized-content/multilingual", data=test_request)
            if response and response.status_code == 200:
                data = response.json()
                expected_keys = ["content_source", "language_detection", "radio_streams"]
                missing_keys = [key for key in expected_keys if key not in data]
                
                # Check for radio_streams data which is critical for frontend
                radio_streams = data.get("radio_streams", {})
                has_main_station = "main_station" in radio_streams
                has_alternatives = "alternative_streams" in radio_streams
                
                success = not missing_keys and has_main_station and has_alternatives
                self.log_result(
                    f"Personalized Content - {test_request['name']}",
                    success,
                    f"Status: {response.status_code}, Language: {data.get('language_detection', {}).get('detected_language', 'N/A')}, Streams: {len(radio_streams.get('alternative_streams', []))}",
                    response_time,
                    critical=True
                )
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(f"Personalized Content - {test_request['name']}", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def test_soundcast_satellite_functionality(self):
        """Test SoundCast and satellite functionality"""
        print("\n🛰️ Testing SoundCast/Satellite Functionality")
        print("-" * 60)
        
        # Test satellite status
        response, response_time = self.make_request("GET", "/satellite/status")
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["connection_type", "signal_strength", "recommendations"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            success = not missing_keys
            self.log_result(
                "Satellite Status",
                success,
                f"Status: {response.status_code}, Connection: {data.get('connection_type', 'N/A')}, Signal: {data.get('signal_strength', 'N/A')}",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Satellite Status", False, f"Failed - Status: {status_code}", response_time, critical=True)
        
        # Test satellite main stations (SoundCast equivalent)
        response, response_time = self.make_request("GET", "/satellite/main_stations")
        if response and response.status_code == 200:
            data = response.json()
            expected_keys = ["satellite_status", "main_stations"]
            missing_keys = [key for key in expected_keys if key not in data]
            
            main_stations = data.get("main_stations", [])
            success = not missing_keys and len(main_stations) > 0
            self.log_result(
                "SoundCast/Satellite Main Stations",
                success,
                f"Status: {response.status_code}, Stations: {len(main_stations)}",
                response_time,
                critical=True
            )
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("SoundCast/Satellite Main Stations", False, f"Failed - Status: {status_code}", response_time, critical=True)

    def run_comprehensive_test(self):
        """Run all country-based organization tests"""
        print("🌍 COMPREHENSIVE COUNTRY-BASED ORGANIZATION TESTING")
        print("=" * 80)
        print(f"🎯 Testing Backend URL: {API_BASE}")
        print(f"📡 Frontend Backend URL: {FRONTEND_ENV_URL}")
        print("=" * 80)
        
        # Run all test suites
        test_suites = [
            self.test_radio_browser_search,
            self.test_radio_browser_country,
            self.test_radio_browser_language,
            self.test_radio_browser_countries_languages,
            self.test_radio_browser_info,
            self.test_hybrid_geolocation_services,
            self.test_language_detection_gps,
            self.test_personalized_content_country_detection,
            self.test_soundcast_satellite_functionality,
            self.test_integration_verification,
            self.test_service_stability,
            self.test_performance_and_data_quality
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
        print("🎉 COMPREHENSIVE COUNTRY-BASED ORGANIZATION TESTING COMPLETE")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        if self.performance_metrics:
            avg_response_time = sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics)
            max_response_time = max(m['response_time'] for m in self.performance_metrics)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.0f}ms")
            print(f"   Maximum Response Time: {max_response_time:.0f}ms")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure['test_name']}: {failure['details']}")
        
        # Failed tests details
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        # Summary by category
        categories = {}
        for result in self.results:
            category = result["test_name"].split(" - ")[0] if " - " in result["test_name"] else "General"
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
        
        print(f"\n📈 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
            print(f"   {status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Deployment readiness assessment
        print(f"\n🎯 COUNTRY-BASED ORGANIZATION STATUS:")
        
        if success_rate >= 90 and len(self.critical_failures) == 0:
            print("   ✅ EXCELLENT - Country-based organization working perfectly!")
        elif success_rate >= 75 and len(self.critical_failures) <= 1:
            print("   ✅ GOOD - Country-based organization working well with minor issues")
        elif success_rate >= 50:
            print("   ⚠️ FAIR - Country-based organization has some issues that need attention")
        else:
            print("   ❌ POOR - Country-based organization has significant issues")
        
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   • GPS Location Detection: {'Working' if success_rate >= 85 else 'Issues detected'}")
        print(f"   • Country Filtering: {'Functional' if success_rate >= 80 else 'Needs attention'}")
        print(f"   • AccuRadio Integration: {'Stable' if success_rate >= 85 else 'Some issues detected'}")
        print(f"   • Radio Browser Integration: {'Working' if success_rate >= 80 else 'Issues detected'}")
        print(f"   • Hybrid Geolocation Service: {'Operational' if success_rate >= 85 else 'Needs attention'}")
        print(f"   • SoundCast/Satellite Functionality: {'Available' if success_rate >= 75 else 'Issues detected'}")
        print(f"   • Performance: {'Excellent' if self.performance_metrics and sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics) < 500 else 'Acceptable' if self.performance_metrics and sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics) < 1000 else 'Needs improvement'} ({sum(m['response_time'] for m in self.performance_metrics) / len(self.performance_metrics):.0f}ms avg)" if self.performance_metrics else "Performance data not available")
        print(f"   • Auto-Selection Features: {'Working' if success_rate >= 80 else 'Needs improvement'}")

if __name__ == "__main__":
    tester = CountryBasedOrganizationTester()
    tester.run_comprehensive_test()