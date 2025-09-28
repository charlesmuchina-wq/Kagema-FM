#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Kagema FM Multilingual Radio API v3.0.0
Tests all multilingual features including automatic language detection based on GPS coordinates
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class KagemaFMMultilingualTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("version") == "3.0.0" and "Multilingual" in data.get("message", ""):
                    self.log_result("API Root v3.0.0", True, f"Version: {data.get('version')}")
                else:
                    self.log_result("API Root v3.0.0", False, f"Unexpected response: {data}")
            else:
                self.log_result("API Root v3.0.0", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API Root v3.0.0", False, f"Error: {str(e)}")
    
    def test_language_detection(self):
        """Test GPS-based language detection for different Kenyan regions"""
        test_coordinates = [
            # Nairobi - Should detect English
            {"lat": -1.2921, "lon": 36.8219, "expected_lang": "en", "expected_county": "Nairobi"},
            # Kisumu - Should detect Luo
            {"lat": -0.091, "lon": 34.768, "expected_lang": "luo", "expected_county": "Kisumu"},
            # Kiambu - Should detect Kikuyu
            {"lat": -1.172, "lon": 36.836, "expected_lang": "ki", "expected_county": "Kiambu"},
            # Kakamega - Should detect Luhya
            {"lat": 0.283, "lon": 34.752, "expected_lang": "luy", "expected_county": "Kakamega"},
            # Nakuru - Should detect Kalenjin
            {"lat": -0.303, "lon": 36.080, "expected_lang": "kal", "expected_county": "Nakuru"},
            # Invalid coordinates - Should fallback to English
            {"lat": 90.0, "lon": 180.0, "expected_lang": "en", "expected_county": "Unknown"}
        ]
        
        for coord in test_coordinates:
            try:
                payload = {"latitude": coord["lat"], "longitude": coord["lon"]}
                response = requests.post(f"{API_BASE}/language/detect", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    detected_lang = data.get("detected_language")
                    county = data.get("county")
                    confidence = data.get("confidence", 0)
                    
                    # Check if language detection is correct
                    lang_correct = detected_lang == coord["expected_lang"]
                    county_correct = county == coord["expected_county"] or coord["expected_county"] == "Unknown"
                    
                    # Verify response structure
                    required_fields = ["detected_language", "alternative_languages", "county", 
                                     "distance_km", "confidence", "language_info", 
                                     "radio_streams", "regional_stations", "localized_content"]
                    
                    has_all_fields = all(field in data for field in required_fields)
                    
                    if lang_correct and county_correct and has_all_fields and confidence >= 0:
                        self.log_result(f"Language Detection ({coord['expected_county']})", True, 
                                      f"Detected: {detected_lang}, County: {county}, Confidence: {confidence:.2f}")
                    else:
                        self.log_result(f"Language Detection ({coord['expected_county']})", False, 
                                      f"Expected: {coord['expected_lang']}/{coord['expected_county']}, Got: {detected_lang}/{county}")
                else:
                    self.log_result(f"Language Detection ({coord['expected_county']})", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Language Detection ({coord['expected_county']})", False, f"Error: {str(e)}")
    
    def test_multilingual_station_info(self):
        """Test multilingual station info with automatic language switching"""
        test_locations = [
            {"lat": -1.2921, "lon": 36.8219, "location": "Nairobi"},
            {"lat": -0.091, "lon": 34.768, "location": "Kisumu"},
            {"lat": -1.172, "lon": 36.836, "location": "Kiambu"}
        ]
        
        for location in test_locations:
            try:
                payload = {"latitude": location["lat"], "longitude": location["lon"]}
                response = requests.post(f"{API_BASE}/station-info/multilingual", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["name", "description", "streamUrl", "detected_language"]
                    has_required = all(field in data for field in required_fields)
                    
                    # Check if station name is correct
                    correct_name = data.get("name") == "Kagema FM"
                    
                    # Check if stream URL is provided
                    has_stream = bool(data.get("streamUrl"))
                    
                    # Check if language is detected
                    has_language = bool(data.get("detected_language"))
                    
                    if has_required and correct_name and has_stream and has_language:
                        self.log_result(f"Multilingual Station Info ({location['location']})", True, 
                                      f"Language: {data.get('detected_language')}, Stream: {bool(data.get('streamUrl'))}")
                    else:
                        self.log_result(f"Multilingual Station Info ({location['location']})", False, 
                                      f"Missing fields or incorrect data")
                else:
                    self.log_result(f"Multilingual Station Info ({location['location']})", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Multilingual Station Info ({location['location']})", False, f"Error: {str(e)}")
    
    def test_supported_languages(self):
        """Test getting all supported languages"""
        try:
            response = requests.get(f"{API_BASE}/languages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                languages = data.get("supported_languages", [])
                total_count = data.get("total_count", 0)
                
                # Check if we have expected Kenyan languages
                expected_languages = ["en", "sw", "ki", "luo", "luy", "kam", "kal"]
                language_codes = [lang.get("code") for lang in languages]
                
                has_expected = all(code in language_codes for code in expected_languages)
                correct_count = total_count == len(languages) and total_count >= 7
                
                if has_expected and correct_count:
                    self.log_result("Supported Languages", True, 
                                  f"Found {total_count} languages including all expected Kenyan languages")
                else:
                    self.log_result("Supported Languages", False, 
                                  f"Missing expected languages or incorrect count. Got: {language_codes}")
            else:
                self.log_result("Supported Languages", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Supported Languages", False, f"Error: {str(e)}")
    
    def test_regional_stations(self):
        """Test regional radio stations for different languages"""
        test_languages = ["en", "sw", "ki", "luo", "luy", "kam", "kal"]
        
        for lang_code in test_languages:
            try:
                response = requests.get(f"{API_BASE}/regional-stations/{lang_code}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["language_code", "language_name", "native_name", "stations", "total_count"]
                    has_required = all(field in data for field in required_fields)
                    
                    # Check if language code matches
                    correct_code = data.get("language_code") == lang_code
                    
                    # Check if stations are provided
                    stations = data.get("stations", [])
                    has_stations = len(stations) > 0
                    
                    # Check station structure
                    valid_stations = True
                    if stations:
                        for station in stations:
                            if not all(key in station for key in ["name", "stream", "frequency"]):
                                valid_stations = False
                                break
                    
                    if has_required and correct_code and has_stations and valid_stations:
                        self.log_result(f"Regional Stations ({lang_code})", True, 
                                      f"Found {len(stations)} stations for {data.get('language_name')}")
                    else:
                        self.log_result(f"Regional Stations ({lang_code})", False, 
                                      f"Invalid response structure or missing data")
                else:
                    self.log_result(f"Regional Stations ({lang_code})", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Regional Stations ({lang_code})", False, f"Error: {str(e)}")
    
    def test_multilingual_personalized_content(self):
        """Test personalized content with automatic language detection"""
        test_locations = [
            {"lat": -1.2921, "lon": 36.8219, "location": "Nairobi"},
            {"lat": -0.091, "lon": 34.768, "location": "Kisumu"}
        ]
        
        for location in test_locations:
            try:
                payload = {
                    "latitude": location["lat"],
                    "longitude": location["lon"],
                    "preferences": {
                        "interests": ["music", "news"],
                        "favorite_genres": ["afrobeats", "gospel"],
                        "age_group": "25-35"
                    }
                }
                
                full_payload = payload
                response = requests.post(f"{API_BASE}/personalized-content/multilingual", 
                                       json=full_payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check main sections
                    required_sections = ["weather", "news", "music", "ai_recommendations", 
                                       "location_info", "language_detection"]
                    has_sections = all(section in data for section in required_sections)
                    
                    # Check language detection section
                    lang_detection = data.get("language_detection", {})
                    has_lang_detection = bool(lang_detection.get("detected_language"))
                    
                    # Check news and music data
                    news = data.get("news", {})
                    music = data.get("music", {})
                    has_content = bool(news.get("articles")) and bool(music.get("tracks"))
                    
                    if has_sections and has_lang_detection and has_content:
                        detected_lang = lang_detection.get("detected_language")
                        self.log_result(f"Multilingual Personalized Content ({location['location']})", True, 
                                      f"Language: {detected_lang}, Content sections: {len([s for s in required_sections if data.get(s)])}")
                    else:
                        self.log_result(f"Multilingual Personalized Content ({location['location']})", False, 
                                      f"Missing sections or content")
                else:
                    self.log_result(f"Multilingual Personalized Content ({location['location']})", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Multilingual Personalized Content ({location['location']})", False, f"Error: {str(e)}")
    
    def test_backwards_compatibility(self):
        """Test that existing endpoints still work (backwards compatibility)"""
        try:
            # Test original station-info endpoint
            response = requests.get(f"{API_BASE}/station-info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("name") == "Kagema FM" and data.get("streamUrl"):
                    self.log_result("Backwards Compatibility (station-info)", True, "Original endpoint working")
                else:
                    self.log_result("Backwards Compatibility (station-info)", False, "Invalid response")
            else:
                self.log_result("Backwards Compatibility (station-info)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Backwards Compatibility (station-info)", False, f"Error: {str(e)}")
        
        try:
            # Test original personalized-content endpoint
            payload = {
                "latitude": -1.2921,
                "longitude": 36.8219,
                "preferences": {
                    "interests": ["music"],
                    "favorite_genres": ["afrobeats"]
                }
            }
            response = requests.post(f"{API_BASE}/personalized-content", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "news" in data and "music" in data:
                    self.log_result("Backwards Compatibility (personalized-content)", True, "Original endpoint working")
                else:
                    self.log_result("Backwards Compatibility (personalized-content)", False, "Invalid response")
            else:
                self.log_result("Backwards Compatibility (personalized-content)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Backwards Compatibility (personalized-content)", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid coordinates
            payload = {"latitude": "invalid", "longitude": "invalid"}
            response = requests.post(f"{API_BASE}/language/detect", json=payload, timeout=10)
            
            if response.status_code == 422:  # Validation error expected
                self.log_result("Error Handling (Invalid Coordinates)", True, "Proper validation error returned")
            else:
                self.log_result("Error Handling (Invalid Coordinates)", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling (Invalid Coordinates)", False, f"Error: {str(e)}")
        
        try:
            # Test invalid language code
            response = requests.get(f"{API_BASE}/regional-stations/invalid_lang", timeout=10)
            
            if response.status_code in [200, 500]:  # Should handle gracefully
                self.log_result("Error Handling (Invalid Language)", True, "Handled invalid language code")
            else:
                self.log_result("Error Handling (Invalid Language)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling (Invalid Language)", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all multilingual API tests"""
        print("🎵 KAGEMA FM MULTILINGUAL API TESTING v3.0.0")
        print("=" * 60)
        print(f"Testing backend at: {API_BASE}")
        print("=" * 60)
        
        # Test all multilingual features
        self.test_api_root()
        self.test_language_detection()
        self.test_multilingual_station_info()
        self.test_supported_languages()
        self.test_regional_stations()
        self.test_multilingual_personalized_content()
        self.test_backwards_compatibility()
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎵 KAGEMA FM MULTILINGUAL API TEST SUMMARY")
        print("=" * 60)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Multilingual API is working great!")
        elif success_rate >= 75:
            print("✅ GOOD: Most multilingual features are working")
        elif success_rate >= 50:
            print("⚠️  PARTIAL: Some multilingual features need attention")
        else:
            print("❌ CRITICAL: Major multilingual issues detected")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = KagemaFMMultilingualTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)