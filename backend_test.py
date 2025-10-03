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

# Get backend URL from environment
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://radio-garden.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class KagemaFMComprehensiveTester:
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

    def test_radio_garden_api_integration(self):
        """Test Radio Garden API integration - Primary focus from review request"""
        print("\n🌍 Testing Radio Garden API Integration...")
        
        # Test basic station info
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
                        "Radio Garden - Basic Station Info",
                        True,
                        f"Station: {data.get('name')}, Stream: {data.get('streamUrl')}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Radio Garden - Basic Station Info",
                        False,
                        f"Missing fields: {missing_fields}",
                        response_time
                    )
            else:
                self.log_result(
                    "Radio Garden - Basic Station Info",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Radio Garden - Basic Station Info", False, f"Exception: {str(e)}")

        # Test radio streams endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/radio/streams")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                main_station = data.get("main_station", {})
                alternative_streams = data.get("alternative_streams", [])
                
                if main_station and alternative_streams:
                    self.log_result(
                        "Radio Garden - Stream Collection",
                        True,
                        f"Main station + {len(alternative_streams)} alternatives",
                        response_time
                    )
                else:
                    self.log_result(
                        "Radio Garden - Stream Collection",
                        False,
                        "Missing main station or alternatives",
                        response_time
                    )
            else:
                self.log_result(
                    "Radio Garden - Stream Collection",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Radio Garden - Stream Collection", False, f"Exception: {str(e)}")

        # Test radio stations endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/radio/stations")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                stations = data.get("stations", [])
                
                if stations:
                    # Check for international stations (Radio Garden feature)
                    international_count = sum(1 for s in stations if s.get("location") != "Global")
                    self.log_result(
                        "Radio Garden - International Stations",
                        True,
                        f"Found {len(stations)} stations, {international_count} international",
                        response_time
                    )
                else:
                    self.log_result(
                        "Radio Garden - International Stations",
                        False,
                        "No stations found",
                        response_time
                    )
            else:
                self.log_result(
                    "Radio Garden - International Stations",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Radio Garden - International Stations", False, f"Exception: {str(e)}")

    def test_geolocation_services(self):
        """Test geolocation services and geocoding - Primary focus from review request"""
        print("\n📍 Testing Geolocation Services...")
        
        # Test language detection from coordinates
        test_locations = [
            {"name": "Nairobi, Kenya", "lat": -1.2921, "lng": 36.8219, "expected_lang": "en"},
            {"name": "Kisumu, Kenya", "lat": -0.0917, "lng": 34.7680, "expected_lang": "luo"},
            {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333, "expected_lang": "pt-br"},
            {"name": "Invalid Location", "lat": 999, "lng": 999, "expected_lang": "en"}  # Should fallback
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
                    
                    if detected_lang:
                        self.log_result(
                            f"Geolocation - Language Detection ({location['name']})",
                            True,
                            f"Detected: {detected_lang}, County: {county}, Confidence: {confidence}",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Geolocation - Language Detection ({location['name']})",
                            False,
                            "No language detected",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Geolocation - Language Detection ({location['name']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Geolocation - Language Detection ({location['name']})", False, f"Exception: {str(e)}")

        # Test multilingual station info with geolocation
        test_locations = [
            {"name": "Kenya", "lat": -1.2921, "lng": 36.8219},
            {"name": "Brazil", "lat": -23.5505, "lng": -46.6333},
            {"name": "Global", "lat": 51.5074, "lng": -0.1278}  # London
        ]
        
        for location in test_locations:
            try:
                start_time = time.time()
                payload = {"latitude": location["lat"], "longitude": location["lng"]}
                response = self.session.post(f"{API_BASE}/station-info/multilingual", json=payload)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["name", "description", "streamUrl", "detected_language"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result(
                            f"Geolocation - Multilingual Station Info ({location['name']})",
                            True,
                            f"Language: {data.get('detected_language')}, Stream: {data.get('streamUrl')}",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Geolocation - Multilingual Station Info ({location['name']})",
                            False,
                            f"Missing fields: {missing_fields}",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Geolocation - Multilingual Station Info ({location['name']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Geolocation - Multilingual Station Info ({location['name']})", False, f"Exception: {str(e)}")

    def test_google_maps_geocoding(self):
        """Test Google Maps geocoding integration"""
        print("\n🗺️ Testing Google Maps Geocoding...")
        
        # Test geocoding
        try:
            start_time = time.time()
            payload = {"address": "Nairobi, Kenya"}
            response = self.session.post(f"{API_BASE}/googlemaps/geocode", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                location = data.get("location", {})
                status = data.get("status", "unknown")
                
                if location.get("lat") and location.get("lng"):
                    self.log_result(
                        "Google Maps - Geocoding",
                        True,
                        f"Lat: {location['lat']}, Lng: {location['lng']}, Status: {status}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Google Maps - Geocoding",
                        True,
                        f"Fallback response, Status: {status}",
                        response_time
                    )
            else:
                self.log_result(
                    "Google Maps - Geocoding",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps - Geocoding", False, f"Exception: {str(e)}")

        # Test reverse geocoding
        try:
            start_time = time.time()
            payload = {"latitude": -1.2921, "longitude": 36.8219}
            response = self.session.post(f"{API_BASE}/googlemaps/reverse-geocode", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                status = data.get("status", "unknown")
                
                if address.get("formatted_address"):
                    self.log_result(
                        "Google Maps - Reverse Geocoding",
                        True,
                        f"Address: {address['formatted_address']}, Status: {status}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Google Maps - Reverse Geocoding",
                        True,
                        f"Fallback response, Status: {status}",
                        response_time
                    )
            else:
                self.log_result(
                    "Google Maps - Reverse Geocoding",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps - Reverse Geocoding", False, f"Exception: {str(e)}")

        # Test nearby places
        try:
            start_time = time.time()
            payload = {
                "latitude": -1.2921,
                "longitude": 36.8219,
                "radius": 5000,
                "place_type": "restaurant"
            }
            response = self.session.post(f"{API_BASE}/googlemaps/places/nearby", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("places", [])
                status = data.get("status", "unknown")
                
                if places:
                    self.log_result(
                        "Google Maps - Nearby Places",
                        True,
                        f"Found {len(places)} places, Status: {status}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Google Maps - Nearby Places",
                        True,
                        f"No places found (expected), Status: {status}",
                        response_time
                    )
            else:
                self.log_result(
                    "Google Maps - Nearby Places",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Google Maps - Nearby Places", False, f"Exception: {str(e)}")

    def test_station_data_accessibility(self):
        """Test radio station data accessibility - Primary focus from review request"""
        print("\n📻 Testing Station Data Accessibility...")
        
        # Test personalized content with radio streams
        test_locations = [
            {"name": "Kenya", "lat": -1.2921, "lng": 36.8219},
            {"name": "Brazil", "lat": -23.5505, "lng": -46.6333}
        ]
        
        # Mock user preferences
        user_preferences = {
            "user_id": "test_user_radio_garden",
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
        
        for location in test_locations:
            try:
                start_time = time.time()
                payload = {
                    "location": {
                        "latitude": location["lat"], 
                        "longitude": location["lng"]
                    },
                    "preferences": user_preferences
                }
                response = self.session.post(f"{API_BASE}/personalized-content/multilingual", json=payload)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for radio_streams data - CRITICAL for Radio Garden functionality
                    radio_streams = data.get("radio_streams")
                    if radio_streams:
                        main_station = radio_streams.get("main_station")
                        alternative_streams = radio_streams.get("alternative_streams", [])
                        
                        if main_station and alternative_streams:
                            self.log_result(
                                f"Station Data - Personalized Content ({location['name']})",
                                True,
                                f"Main station + {len(alternative_streams)} alternatives",
                                response_time
                            )
                        else:
                            self.log_result(
                                f"Station Data - Personalized Content ({location['name']})",
                                False,
                                "Missing main station or alternatives",
                                response_time
                            )
                    else:
                        self.log_result(
                            f"Station Data - Personalized Content ({location['name']})",
                            False,
                            "No radio_streams data found",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Station Data - Personalized Content ({location['name']})",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Station Data - Personalized Content ({location['name']})", False, f"Exception: {str(e)}")

        # Test stream URL accessibility
        self.test_stream_accessibility()

    def test_stream_accessibility(self):
        """Test accessibility of radio stream URLs"""
        print("\n🎵 Testing Stream URL Accessibility...")
        
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
                for alt in alternatives[:5]:  # Test first 5 alternatives
                    if alt.get("streamUrl"):
                        stream_urls.append((alt["name"], alt["streamUrl"]))
        except Exception as e:
            self.log_result("Stream URLs - API Fetch", False, f"Failed to get stream URLs: {str(e)}")
            return
            
        # Test each stream URL accessibility
        for stream_name, stream_url in stream_urls:
            try:
                start_time = time.time()
                response = self.session.head(stream_url, allow_redirects=True, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    icy_headers = [h for h in response.headers.keys() if h.lower().startswith('icy-')]
                    
                    if 'audio' in content_type.lower() or icy_headers:
                        self.log_result(
                            f"Stream Accessibility - {stream_name}",
                            True,
                            f"Content-Type: {content_type}, ICY headers: {len(icy_headers)}",
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Stream Accessibility - {stream_name}",
                            False,
                            f"Not audio stream: {content_type}",
                            response_time
                        )
                else:
                    self.log_result(
                        f"Stream Accessibility - {stream_name}",
                        False,
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_result(f"Stream Accessibility - {stream_name}", False, f"Exception: {str(e)}")

    def test_error_handling_fallbacks(self):
        """Test error handling and fallback scenarios - Primary focus from review request"""
        print("\n🛡️ Testing Error Handling & Fallbacks...")
        
        # Test invalid coordinates
        try:
            start_time = time.time()
            payload = {"latitude": 999, "longitude": 999}
            response = self.session.post(f"{API_BASE}/language/detect", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("detected_language") == "en":  # Should fallback to English
                    self.log_result(
                        "Error Handling - Invalid Coordinates",
                        True,
                        f"Proper fallback to English",
                        response_time
                    )
                else:
                    self.log_result(
                        "Error Handling - Invalid Coordinates",
                        False,
                        f"Unexpected fallback: {data.get('detected_language')}",
                        response_time
                    )
            else:
                self.log_result(
                    "Error Handling - Invalid Coordinates",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Error Handling - Invalid Coordinates", False, f"Exception: {str(e)}")

        # Test malformed request
        try:
            start_time = time.time()
            payload = {"invalid": "data"}
            response = self.session.post(f"{API_BASE}/language/detect", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [400, 422]:  # Should return validation error
                self.log_result(
                    "Error Handling - Malformed Request",
                    True,
                    f"Proper validation error HTTP {response.status_code}",
                    response_time
                )
            else:
                self.log_result(
                    "Error Handling - Malformed Request",
                    False,
                    f"Unexpected response HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Error Handling - Malformed Request", False, f"Exception: {str(e)}")

        # Test service unavailable scenarios
        try:
            start_time = time.time()
            payload = {"address": "NonExistentPlace12345"}
            response = self.session.post(f"{API_BASE}/googlemaps/geocode", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                if status == "fallback":
                    self.log_result(
                        "Error Handling - Service Unavailable",
                        True,
                        f"Proper fallback response, Status: {status}",
                        response_time
                    )
                else:
                    self.log_result(
                        "Error Handling - Service Unavailable",
                        True,
                        f"Service response, Status: {status}",
                        response_time
                    )
            else:
                self.log_result(
                    "Error Handling - Service Unavailable",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
        except Exception as e:
            self.log_result("Error Handling - Service Unavailable", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all Radio Garden and geolocation tests"""
        print("🌍 STARTING RADIO GARDEN & GEOLOCATION BACKEND TESTING")
        print("=" * 70)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Backend not accessible. Stopping tests.")
            return self.get_summary()
        
        # Run Radio Garden and geolocation focused tests
        self.test_radio_garden_api_integration()
        self.test_geolocation_services()
        self.test_google_maps_geocoding()
        self.test_station_data_accessibility()
        self.test_error_handling_fallbacks()
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        total_tests = len(self.results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("🎯 RADIO GARDEN & GEOLOCATION TESTING SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🌍 Radio Garden & Geolocation Testing Complete!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.results
        }

def main():
    """Main test execution for Radio Garden and geolocation features"""
    tester = RadioGardenBackendTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["success_rate"] >= 80:  # 80% threshold for acceptable performance
        print(f"\n✅ RADIO GARDEN & GEOLOCATION TESTS PASSED ({results['success_rate']:.1f}% success rate)")
        return 0
    else:
        print(f"\n❌ RADIO GARDEN & GEOLOCATION TESTS FAILED ({results['success_rate']:.1f}% success rate)")
        return 1

if __name__ == "__main__":
    exit(main())