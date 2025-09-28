#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Enhanced Kagema FM Radio Station
Tests all enhanced features including geolocation, weather, news, music, and AI services
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys
import os

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class KagemaFMAPITester:
    def __init__(self):
        self.base_url = API_BASE
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(f"{test_name}: {details}")
        print(result)
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "Kagema FM" in data.get("message", "") and data.get("version") == "2.0.0":
                    self.log_test("API Root Endpoint", True, "Enhanced API version 2.0.0 detected")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_station_info(self):
        """Test enhanced station info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/station-info")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "currentShow", "genre", "location", "frequency"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Enhanced Station Info", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check for enhanced features
                enhanced_features = ["personalized content", "weather updates", "trending music"]
                description = data.get("description", "").lower()
                has_enhanced = any(feature in description for feature in enhanced_features)
                
                if has_enhanced:
                    self.log_test("Enhanced Station Info", True, "Enhanced features detected in description")
                    return True
                else:
                    self.log_test("Enhanced Station Info", True, "Basic station info working, enhanced features not mentioned")
                    return True
            else:
                self.log_test("Enhanced Station Info", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Enhanced Station Info", False, f"Exception: {str(e)}")
            return False
    
    def test_weather_endpoint(self):
        """Test weather data endpoint with various coordinates"""
        test_locations = [
            {"name": "Nairobi", "lat": -1.2921, "lon": 36.8219},
            {"name": "Mombasa", "lat": -4.0435, "lon": 39.6682},
            {"name": "Kisumu", "lat": -0.1022, "lon": 34.7617}
        ]
        
        success_count = 0
        for location in test_locations:
            try:
                payload = {"latitude": location["lat"], "longitude": location["lon"]}
                response = self.session.post(f"{self.base_url}/location/weather", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["location", "temperature", "feels_like", "humidity", "description", "icon", "timestamp"]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test(f"Weather API - {location['name']}", False, f"Missing fields: {missing_fields}")
                    else:
                        # Validate data types
                        if (isinstance(data["temperature"], (int, float)) and 
                            isinstance(data["humidity"], int) and
                            isinstance(data["location"], str)):
                            success_count += 1
                            self.log_test(f"Weather API - {location['name']}", True, f"Temp: {data['temperature']}°C, {data['description']}")
                        else:
                            self.log_test(f"Weather API - {location['name']}", False, "Invalid data types")
                else:
                    self.log_test(f"Weather API - {location['name']}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Weather API - {location['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(test_locations)
    
    def test_geocoding_endpoint(self):
        """Test reverse geocoding endpoint"""
        test_coordinates = [
            {"name": "Nairobi Center", "lat": -1.2921, "lon": 36.8219},
            {"name": "Outside Nairobi", "lat": -2.0, "lon": 37.0}
        ]
        
        success_count = 0
        for coord in test_coordinates:
            try:
                payload = {"latitude": coord["lat"], "longitude": coord["lon"]}
                response = self.session.post(f"{self.base_url}/location/geocode", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["city", "region", "country", "formatted_address"]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test(f"Geocoding - {coord['name']}", False, f"Missing fields: {missing_fields}")
                    else:
                        success_count += 1
                        self.log_test(f"Geocoding - {coord['name']}", True, f"Location: {data['formatted_address']}")
                else:
                    self.log_test(f"Geocoding - {coord['name']}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Geocoding - {coord['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(test_coordinates)
    
    def test_local_news_endpoint(self):
        """Test local Kenyan news endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/news/local?limit=10")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "articles" not in data or "total_count" not in data:
                    self.log_test("Local News API", False, "Missing articles or total_count fields")
                    return False
                
                articles = data["articles"]
                if not isinstance(articles, list) or len(articles) == 0:
                    self.log_test("Local News API", False, "No articles returned")
                    return False
                
                # Check article structure
                first_article = articles[0]
                required_fields = ["title", "description", "url", "source", "published_at"]
                missing_fields = [field for field in required_fields if field not in first_article]
                
                if missing_fields:
                    self.log_test("Local News API", False, f"Article missing fields: {missing_fields}")
                    return False
                
                # Check for AI summary
                has_summary = "summary" in data and data["summary"]
                summary_note = " with AI summary" if has_summary else " (no AI summary)"
                
                self.log_test("Local News API", True, f"{len(articles)} articles returned{summary_note}")
                return True
            else:
                self.log_test("Local News API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Local News API", False, f"Exception: {str(e)}")
            return False
    
    def test_international_news_endpoint(self):
        """Test international news endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/news/international?limit=5")
            if response.status_code == 200:
                data = response.json()
                
                if "articles" not in data or "total_count" not in data:
                    self.log_test("International News API", False, "Missing articles or total_count fields")
                    return False
                
                articles = data["articles"]
                if not isinstance(articles, list) or len(articles) == 0:
                    self.log_test("International News API", False, "No articles returned")
                    return False
                
                # Check for AI summary
                has_summary = "summary" in data and data["summary"]
                summary_note = " with AI summary" if has_summary else " (no AI summary)"
                
                self.log_test("International News API", True, f"{len(articles)} articles returned{summary_note}")
                return True
            else:
                self.log_test("International News API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("International News API", False, f"Exception: {str(e)}")
            return False
    
    def test_trending_music_endpoint(self):
        """Test trending music endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/music/trending?country=KE&limit=10")
            if response.status_code == 200:
                data = response.json()
                
                if "tracks" not in data:
                    self.log_test("Trending Music API", False, "Missing tracks field")
                    return False
                
                tracks = data["tracks"]
                if not isinstance(tracks, list) or len(tracks) == 0:
                    self.log_test("Trending Music API", False, "No tracks returned")
                    return False
                
                # Check track structure
                first_track = tracks[0]
                required_fields = ["id", "name", "artists", "album", "popularity"]
                missing_fields = [field for field in required_fields if field not in first_track]
                
                if missing_fields:
                    self.log_test("Trending Music API", False, f"Track missing fields: {missing_fields}")
                    return False
                
                # Check data types
                if (isinstance(first_track["artists"], list) and 
                    isinstance(first_track["popularity"], int)):
                    self.log_test("Trending Music API", True, f"{len(tracks)} tracks returned")
                    return True
                else:
                    self.log_test("Trending Music API", False, "Invalid data types in track data")
                    return False
            else:
                self.log_test("Trending Music API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Trending Music API", False, f"Exception: {str(e)}")
            return False
    
    def test_kenyan_music_endpoint(self):
        """Test Kenyan music endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/music/kenyan?limit=5")
            if response.status_code == 200:
                data = response.json()
                
                if "tracks" not in data:
                    self.log_test("Kenyan Music API", False, "Missing tracks field")
                    return False
                
                tracks = data["tracks"]
                if not isinstance(tracks, list) or len(tracks) == 0:
                    self.log_test("Kenyan Music API", False, "No tracks returned")
                    return False
                
                self.log_test("Kenyan Music API", True, f"{len(tracks)} Kenyan tracks returned")
                return True
            else:
                self.log_test("Kenyan Music API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Kenyan Music API", False, f"Exception: {str(e)}")
            return False
    
    def test_personalized_content_endpoint(self):
        """Test the main personalized content endpoint"""
        try:
            payload = {
                "location": {
                    "latitude": -1.2921,
                    "longitude": 36.8219
                },
                "preferences": {
                    "interests": ["music", "news", "weather"],
                    "favorite_genres": ["Afrobeats", "Hip Hop"],
                    "location": "Nairobi",
                    "age_group": "25-35"
                }
            }
            
            response = self.session.post(f"{self.base_url}/personalized-content", json=payload)
            if response.status_code == 200:
                data = response.json()
                
                # Check main sections
                required_sections = ["weather", "news", "music", "ai_recommendations", "location_info"]
                missing_sections = [section for section in required_sections if section not in data]
                
                if missing_sections:
                    self.log_test("Personalized Content API", False, f"Missing sections: {missing_sections}")
                    return False
                
                # Validate each section
                weather_valid = data["weather"] and "temperature" in data["weather"]
                news_valid = data["news"] and "articles" in data["news"] and len(data["news"]["articles"]) > 0
                music_valid = data["music"] and "tracks" in data["music"] and len(data["music"]["tracks"]) > 0
                ai_valid = data["ai_recommendations"] and isinstance(data["ai_recommendations"], dict)
                location_valid = data["location_info"] and "city" in data["location_info"]
                
                if all([weather_valid, news_valid, music_valid, ai_valid, location_valid]):
                    self.log_test("Personalized Content API", True, "All sections populated with valid data")
                    return True
                else:
                    invalid_sections = []
                    if not weather_valid: invalid_sections.append("weather")
                    if not news_valid: invalid_sections.append("news")
                    if not music_valid: invalid_sections.append("music")
                    if not ai_valid: invalid_sections.append("ai_recommendations")
                    if not location_valid: invalid_sections.append("location_info")
                    
                    self.log_test("Personalized Content API", False, f"Invalid sections: {invalid_sections}")
                    return False
            else:
                self.log_test("Personalized Content API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Personalized Content API", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        error_tests = [
            {
                "name": "Invalid Weather Coordinates",
                "endpoint": "/location/weather",
                "method": "POST",
                "payload": {"latitude": "invalid", "longitude": 36.8219}
            },
            {
                "name": "Missing Weather Data",
                "endpoint": "/location/weather", 
                "method": "POST",
                "payload": {}
            },
            {
                "name": "Invalid Geocoding Coordinates",
                "endpoint": "/location/geocode",
                "method": "POST", 
                "payload": {"latitude": 999, "longitude": 999}
            }
        ]
        
        success_count = 0
        for test in error_tests:
            try:
                if test["method"] == "POST":
                    response = self.session.post(f"{self.base_url}{test['endpoint']}", json=test["payload"])
                else:
                    response = self.session.get(f"{self.base_url}{test['endpoint']}")
                
                # Expect 4xx or 5xx status codes for error cases
                if 400 <= response.status_code < 600:
                    success_count += 1
                    self.log_test(f"Error Handling - {test['name']}", True, f"Properly returned {response.status_code}")
                else:
                    self.log_test(f"Error Handling - {test['name']}", False, f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Error Handling - {test['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(error_tests)
    
    def test_performance_and_caching(self):
        """Test response times and caching functionality"""
        try:
            # Test response time for weather endpoint
            start_time = time.time()
            payload = {"latitude": -1.2921, "longitude": 36.8219}
            response1 = self.session.post(f"{self.base_url}/location/weather", json=payload)
            first_request_time = time.time() - start_time
            
            if response1.status_code != 200:
                self.log_test("Performance Test", False, "Weather endpoint not responding")
                return False
            
            # Test caching with second request
            start_time = time.time()
            response2 = self.session.post(f"{self.base_url}/location/weather", json=payload)
            second_request_time = time.time() - start_time
            
            if response2.status_code != 200:
                self.log_test("Performance Test", False, "Second weather request failed")
                return False
            
            # Check if responses are identical (indicating caching)
            if response1.json() == response2.json():
                cache_note = " (caching detected)" if second_request_time < first_request_time else " (no caching detected)"
                self.log_test("Performance Test", True, f"Response time: {first_request_time:.2f}s{cache_note}")
                return True
            else:
                self.log_test("Performance Test", False, "Inconsistent responses between requests")
                return False
        except Exception as e:
            self.log_test("Performance Test", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"🎵 KAGEMA FM ENHANCED RADIO API TESTING")
        print(f"Testing backend at: {self.base_url}")
        print("=" * 60)
        
        test_methods = [
            self.test_api_root,
            self.test_enhanced_station_info,
            self.test_weather_endpoint,
            self.test_geocoding_endpoint,
            self.test_local_news_endpoint,
            self.test_international_news_endpoint,
            self.test_trending_music_endpoint,
            self.test_kenyan_music_endpoint,
            self.test_personalized_content_endpoint,
            self.test_error_handling,
            self.test_performance_and_caching
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL: {test_method.__name__} - Unexpected error: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"🎵 KAGEMA FM ENHANCED API TEST SUMMARY")
        print(f"Passed: {passed_tests}/{total_tests} test suites")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for failure in self.failed_tests:
                print(f"  - {failure}")
        
        if passed_tests == total_tests:
            print("🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test suite(s) failed")
            return False

def main():
    """Main test execution"""
    tester = KagemaFMAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()