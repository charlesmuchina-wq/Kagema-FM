#!/usr/bin/env python3
"""
Kagema FM Radio Streaming Backend Test Suite
Testing radio streaming functionality as reported by user
"""

import requests
import json
import sys
from datetime import datetime
import subprocess
import time

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

class RadioStreamingTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success:
            self.failed_tests.append(test_name)
        print()

    def test_basic_station_info(self):
        """Test GET /api/station-info endpoint (mentioned in review request)"""
        try:
            response = requests.get(f"{API_BASE}/station-info", timeout=10)
            
            if response.status_code == 404:
                self.log_test(
                    "GET /api/station-info", 
                    False, 
                    "Endpoint not found (404) - This endpoint doesn't exist in current implementation",
                    {"status_code": 404, "error": "Endpoint missing"}
                )
            else:
                data = response.json()
                has_stream_url = 'streamUrl' in data or 'stream_url' in data
                self.log_test(
                    "GET /api/station-info", 
                    response.status_code == 200 and has_stream_url,
                    f"Status: {response.status_code}, Has stream URL: {has_stream_url}",
                    data
                )
        except Exception as e:
            self.log_test(
                "GET /api/station-info", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_multilingual_station_info_kenya(self):
        """Test POST /api/station-info/multilingual with Kenya coordinates"""
        try:
            kenya_coords = {
                "latitude": -1.286389,
                "longitude": 36.817223
            }
            
            response = requests.post(
                f"{API_BASE}/station-info/multilingual",
                json=kenya_coords,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                has_stream_url = 'streamUrl' in data
                stream_url = data.get('streamUrl', '')
                
                self.log_test(
                    "POST /api/station-info/multilingual (Kenya)", 
                    has_stream_url and stream_url,
                    f"Stream URL: {stream_url}, Language: {data.get('detected_language', 'N/A')}",
                    data
                )
                
                # Test if stream URL is accessible
                if stream_url:
                    self.test_stream_url_accessibility(stream_url, "Kenya Station")
                    
            else:
                self.log_test(
                    "POST /api/station-info/multilingual (Kenya)", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/station-info/multilingual (Kenya)", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_multilingual_station_info_brazil(self):
        """Test POST /api/station-info/multilingual with Brazil coordinates"""
        try:
            brazil_coords = {
                "latitude": -23.550520,
                "longitude": -46.633309
            }
            
            response = requests.post(
                f"{API_BASE}/station-info/multilingual",
                json=brazil_coords,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                has_stream_url = 'streamUrl' in data
                stream_url = data.get('streamUrl', '')
                
                self.log_test(
                    "POST /api/station-info/multilingual (Brazil)", 
                    has_stream_url and stream_url,
                    f"Stream URL: {stream_url}, Language: {data.get('detected_language', 'N/A')}",
                    data
                )
                
                # Test if stream URL is accessible
                if stream_url:
                    self.test_stream_url_accessibility(stream_url, "Brazil Station")
                    
            else:
                self.log_test(
                    "POST /api/station-info/multilingual (Brazil)", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/station-info/multilingual (Brazil)", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_personalized_content_with_radio(self):
        """Test POST /api/personalized-content/multilingual for radio streams"""
        try:
            payload = {
                "location": {
                    "latitude": -1.286389,
                    "longitude": 36.817223
                },
                "preferences": {
                    "interests": ["music", "news"],
                    "favorite_genres": ["afrobeat", "gospel"],
                    "location": "Nairobi",
                    "age_group": "adult",
                    "preferred_language": "en",
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
                has_radio_streams = 'radio_streams' in data
                
                self.log_test(
                    "POST /api/personalized-content/multilingual", 
                    has_radio_streams,
                    f"Has radio streams: {has_radio_streams}, Content source: {data.get('content_source', 'N/A')}",
                    {"has_radio_streams": has_radio_streams, "keys": list(data.keys())}
                )
                
            else:
                self.log_test(
                    "POST /api/personalized-content/multilingual", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "POST /api/personalized-content/multilingual", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_stream_url_accessibility(self, stream_url, station_name):
        """Test if a radio stream URL is accessible and returns audio data"""
        try:
            # Use curl to test stream accessibility with timeout
            curl_cmd = [
                'curl', '-s', '-I', '--max-time', '10', 
                '--user-agent', 'Kagema FM App/1.0',
                stream_url
            ]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                headers = result.stdout.lower()
                is_audio = any(audio_type in headers for audio_type in [
                    'audio/', 'application/ogg', 'video/mp2t', 'icy-'
                ])
                
                # Also check for streaming indicators
                is_streaming = any(indicator in headers for indicator in [
                    'icy-name', 'icy-genre', 'content-type: audio', 'shoutcast'
                ])
                
                success = is_audio or is_streaming
                
                self.log_test(
                    f"Stream URL Accessibility ({station_name})", 
                    success,
                    f"URL: {stream_url}, Audio headers: {is_audio}, Streaming headers: {is_streaming}",
                    {"headers_sample": headers[:200] if headers else "No headers"}
                )
                
            else:
                self.log_test(
                    f"Stream URL Accessibility ({station_name})", 
                    False,
                    f"Curl failed with return code {result.returncode}: {result.stderr}"
                )
                
        except Exception as e:
            self.log_test(
                f"Stream URL Accessibility ({station_name})", 
                False, 
                f"Stream test failed: {str(e)}"
            )

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                has_version = 'version' in data
                
                self.log_test(
                    "GET /api/ (API Root)", 
                    has_version,
                    f"Version: {data.get('version', 'N/A')}, Message: {data.get('message', 'N/A')}",
                    data
                )
            else:
                self.log_test(
                    "GET /api/ (API Root)", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "GET /api/ (API Root)", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_cors_headers(self):
        """Test CORS configuration for frontend integration"""
        try:
            # Test preflight request
            response = requests.options(
                f"{API_BASE}/station-info/multilingual",
                headers={
                    'Origin': 'https://kagema-fm-app.preview.emergentagent.com',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            has_cors = any(cors_headers.values())
            
            self.log_test(
                "CORS Configuration", 
                has_cors,
                f"CORS headers present: {has_cors}",
                cors_headers
            )
            
        except Exception as e:
            self.log_test(
                "CORS Configuration", 
                False, 
                f"CORS test failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run comprehensive radio streaming tests"""
        print("🎵 KAGEMA FM RADIO STREAMING BACKEND TESTS")
        print("=" * 50)
        print(f"Backend URL: {API_BASE}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Test API availability
        self.test_api_root()
        
        # Test radio streaming endpoints
        self.test_basic_station_info()
        self.test_multilingual_station_info_kenya()
        self.test_multilingual_station_info_brazil()
        self.test_personalized_content_with_radio()
        
        # Test infrastructure
        self.test_cors_headers()
        
        # Summary
        print("=" * 50)
        print("🎵 RADIO STREAMING TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "failed_test_names": self.failed_tests,
            "detailed_results": self.test_results
        }

if __name__ == "__main__":
    tester = RadioStreamingTester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)