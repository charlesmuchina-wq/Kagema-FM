#!/usr/bin/env python3
"""
Backend API Testing for Kagema FM Radio Streaming Functionality
Focus: Updated Personalized Content API with Radio Streams
Testing the specific issue: "none of the radio options are working"
"""

import requests
import json
import sys
from typing import Dict, Any, List
import subprocess
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "https://kagema-fm-app.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class RadioStreamingTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        result = {
            "test": test_name,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                features = data.get('features', [])
                self.log_test("API Root", True, f"Version: {version}, Features: {len(features)}")
                return True
            else:
                self.log_test("API Root", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root", False, f"Error: {str(e)}")
            return False
    
    def test_basic_station_info(self):
        """Test basic station info endpoint"""
        try:
            response = requests.get(f"{API_BASE}/station-info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                stream_url = data.get('streamUrl', '')
                name = data.get('name', '')
                self.log_test("Basic Station Info", True, f"Station: {name}, Stream: {stream_url}")
                return True, stream_url
            else:
                self.log_test("Basic Station Info", False, f"Status: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("Basic Station Info", False, f"Error: {str(e)}")
            return False, None
    
    def test_personalized_content_kenya(self):
        """Test personalized content API with Kenya coordinates - CRITICAL TEST"""
        try:
            payload = {
                "location": {
                    "latitude": -1.286389,
                    "longitude": 36.817223
                },
                "preferences": {
                    "interests": ["music", "news"],
                    "favorite_genres": ["afrobeat", "gospel"],
                    "offline_mode": False,
                    "user_age": 25,
                    "accept_adult_content": True
                }
            }
            
            response = requests.post(
                f"{API_BASE}/personalized-content/multilingual",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if radio_streams field exists - CRITICAL
                if "radio_streams" not in data:
                    self.log_test("Personalized Content Kenya - Radio Streams", False, 
                                "CRITICAL: radio_streams field missing from response")
                    return False, None
                
                radio_streams = data["radio_streams"]
                
                # Verify main_station exists and has required fields
                main_station = radio_streams.get("main_station", {})
                if not main_station:
                    self.log_test("Personalized Content Kenya - Main Station", False, 
                                "main_station missing from radio_streams")
                    return False, None
                
                required_fields = ["name", "streamUrl", "description", "frequency"]
                missing_fields = [field for field in required_fields if field not in main_station]
                if missing_fields:
                    self.log_test("Personalized Content Kenya - Main Station Fields", False, 
                                f"Missing fields: {missing_fields}")
                    return False, None
                
                # Verify regional_stations and alternative_streams exist
                regional_stations = radio_streams.get("regional_stations", [])
                alternative_streams = radio_streams.get("alternative_streams", [])
                
                self.log_test("Personalized Content Kenya - Radio Streams", True, 
                            f"Main station: {main_station['name']}, Regional: {len(regional_stations)}, Alt: {len(alternative_streams)}")
                
                return True, main_station.get("streamUrl")
            else:
                self.log_test("Personalized Content Kenya", False, f"Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Personalized Content Kenya", False, f"Error: {str(e)}")
            return False, None
    
    def test_personalized_content_brazil(self):
        """Test personalized content API with Brazil coordinates"""
        try:
            payload = {
                "location": {
                    "latitude": -23.550520,
                    "longitude": -46.633309
                },
                "preferences": {
                    "interests": ["music", "news"],
                    "favorite_genres": ["samba", "bossa nova"],
                    "offline_mode": False,
                    "user_age": 25,
                    "accept_adult_content": True
                }
            }
            
            response = requests.post(
                f"{API_BASE}/personalized-content/multilingual",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if radio_streams field exists
                if "radio_streams" not in data:
                    self.log_test("Personalized Content Brazil - Radio Streams", False, 
                                "radio_streams field missing from response")
                    return False, None
                
                radio_streams = data["radio_streams"]
                main_station = radio_streams.get("main_station", {})
                regional_stations = radio_streams.get("regional_stations", [])
                alternative_streams = radio_streams.get("alternative_streams", [])
                
                self.log_test("Personalized Content Brazil - Radio Streams", True, 
                            f"Main station: {main_station.get('name', 'N/A')}, Regional: {len(regional_stations)}, Alt: {len(alternative_streams)}")
                
                return True, main_station.get("streamUrl")
            else:
                self.log_test("Personalized Content Brazil", False, f"Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Personalized Content Brazil", False, f"Error: {str(e)}")
            return False, None
    
    def test_stream_url_accessibility(self, stream_url: str, location: str = ""):
        """Test if stream URL is accessible using curl"""
        if not stream_url:
            self.log_test(f"Stream URL Accessibility {location}", False, "No stream URL provided")
            return False
        
        try:
            # Use curl to test stream accessibility
            cmd = [
                "curl", "-I", "-L", "--max-time", "10", 
                "--user-agent", "KagemaFM/1.0", stream_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # Check for successful HTTP response
                if "200 OK" in result.stdout or "HTTP/1.1 200" in result.stdout or "HTTP/2 200" in result.stdout:
                    # Check for audio content type
                    if "audio/" in result.stdout.lower() or "icy-" in result.stdout.lower():
                        self.log_test(f"Stream URL Accessibility {location}", True, 
                                    f"Stream accessible: {stream_url}")
                        return True
                    else:
                        self.log_test(f"Stream URL Accessibility {location}", False, 
                                    f"Not audio content: {stream_url}")
                        return False
                else:
                    self.log_test(f"Stream URL Accessibility {location}", False, 
                                f"HTTP error for {stream_url}: {result.stdout[:200]}")
                    return False
            else:
                self.log_test(f"Stream URL Accessibility {location}", False, 
                            f"Curl failed for {stream_url}: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            self.log_test(f"Stream URL Accessibility {location}", False, f"Error testing {stream_url}: {str(e)}")
            return False
    
    def test_multilingual_station_info_kenya(self):
        """Test multilingual station info for backwards compatibility"""
        try:
            payload = {
                "latitude": -1.286389,
                "longitude": 36.817223
            }
            
            response = requests.post(
                f"{API_BASE}/station-info/multilingual",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                stream_url = data.get('streamUrl', '')
                name = data.get('name', '')
                detected_lang = data.get('detected_language', '')
                
                self.log_test("Multilingual Station Info Kenya", True, 
                            f"Station: {name}, Language: {detected_lang}, Stream: {stream_url}")
                return True, stream_url
            else:
                self.log_test("Multilingual Station Info Kenya", False, f"Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Multilingual Station Info Kenya", False, f"Error: {str(e)}")
            return False, None
    
    def test_multilingual_station_info_brazil(self):
        """Test multilingual station info for Brazil"""
        try:
            payload = {
                "latitude": -23.550520,
                "longitude": -46.633309
            }
            
            response = requests.post(
                f"{API_BASE}/station-info/multilingual",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                stream_url = data.get('streamUrl', '')
                name = data.get('name', '')
                detected_lang = data.get('detected_language', '')
                
                self.log_test("Multilingual Station Info Brazil", True, 
                            f"Station: {name}, Language: {detected_lang}, Stream: {stream_url}")
                return True, stream_url
            else:
                self.log_test("Multilingual Station Info Brazil", False, f"Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Multilingual Station Info Brazil", False, f"Error: {str(e)}")
            return False, None
    
    def compare_radio_data(self):
        """Compare radio stream data between personalized content and station info endpoints"""
        print("🔍 COMPARING RADIO DATA BETWEEN ENDPOINTS...")
        
        # Get data from both endpoints for Kenya
        try:
            # Personalized content
            pc_payload = {
                "location": {"latitude": -1.286389, "longitude": 36.817223},
                "preferences": {"offline_mode": False, "user_age": 25}
            }
            pc_response = requests.post(f"{API_BASE}/personalized-content/multilingual", json=pc_payload, timeout=10)
            
            # Station info
            si_payload = {"latitude": -1.286389, "longitude": 36.817223}
            si_response = requests.post(f"{API_BASE}/station-info/multilingual", json=si_payload, timeout=10)
            
            if pc_response.status_code == 200 and si_response.status_code == 200:
                pc_data = pc_response.json()
                si_data = si_response.json()
                
                # Compare stream URLs
                pc_main_stream = pc_data.get("radio_streams", {}).get("main_station", {}).get("streamUrl", "")
                si_stream = si_data.get("streamUrl", "")
                
                if pc_main_stream == si_stream:
                    self.log_test("Radio Data Comparison", True, 
                                f"Stream URLs match: {pc_main_stream}")
                else:
                    self.log_test("Radio Data Comparison", False, 
                                f"Stream URLs differ - PC: {pc_main_stream}, SI: {si_stream}")
            else:
                self.log_test("Radio Data Comparison", False, 
                            f"API errors - PC: {pc_response.status_code}, SI: {si_response.status_code}")
                
        except Exception as e:
            self.log_test("Radio Data Comparison", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all radio streaming tests"""
        print(f"🎵 KAGEMA FM RADIO STREAMING API TESTING")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Test 1: API Root
        self.test_api_root()
        
        # Test 2: Basic station info
        basic_success, basic_stream = self.test_basic_station_info()
        
        # Test 3: Personalized content Kenya (CRITICAL)
        kenya_success, kenya_stream = self.test_personalized_content_kenya()
        
        # Test 4: Personalized content Brazil
        brazil_success, brazil_stream = self.test_personalized_content_brazil()
        
        # Test 5: Stream URL accessibility
        if kenya_stream:
            self.test_stream_url_accessibility(kenya_stream, "(Kenya)")
        if brazil_stream:
            self.test_stream_url_accessibility(brazil_stream, "(Brazil)")
        if basic_stream:
            self.test_stream_url_accessibility(basic_stream, "(Basic)")
        
        # Test 6: Multilingual station info (backwards compatibility)
        kenya_si_success, kenya_si_stream = self.test_multilingual_station_info_kenya()
        brazil_si_success, brazil_si_stream = self.test_multilingual_station_info_brazil()
        
        # Test 7: Compare radio data between endpoints
        self.compare_radio_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎵 RADIO STREAMING TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in self.test_results:
            if test['success']:
                print(f"   • {test['test']}")
        
        return success_rate >= 80, self.failed_tests

if __name__ == "__main__":
    tester = RadioStreamingTester()
    success, failed_tests = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 RADIO STREAMING TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"\n🚨 RADIO STREAMING TESTS FAILED - {len(failed_tests)} issues found")
        sys.exit(1)