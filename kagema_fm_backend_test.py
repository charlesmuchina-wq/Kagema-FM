#!/usr/bin/env python3
"""
Kagema FM Backend API Testing Suite
Tests core radio streaming endpoints after frontend React Hook error fix
Focus on: Core radio streaming endpoints, Personalized content API, Basic connectivity
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend .env
BACKEND_URL = "https://autotunes.preview.emergentagent.com/api"

class KagemaFMBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 10
        
    def log_test(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details} ({result['response_time_ms']}ms)")
        
    def test_api_root(self):
        """Test GET /api/ endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Kagema FM" in data["message"]:
                    self.log_test("API Root", True, f"API Root working - {data['message']}", response_time)
                    return True
                else:
                    self.log_test("API Root", False, f"Unexpected response format: {data}", response_time)
                    return False
            else:
                self.log_test("API Root", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("API Root", False, f"Connection error: {str(e)}")
            return False
    
    def test_station_info(self):
        """Test GET /api/station-info endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/station-info")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "currentShow"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    stream_url = data.get("streamUrl", "")
                    if stream_url and "http" in stream_url:
                        self.log_test("Station Info", True, f"Station info complete with stream URL: {stream_url}", response_time)
                        return True
                    else:
                        self.log_test("Station Info", False, f"Invalid or missing stream URL: {stream_url}", response_time)
                        return False
                else:
                    self.log_test("Station Info", False, f"Missing required fields: {missing_fields}", response_time)
                    return False
            else:
                self.log_test("Station Info", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Station Info", False, f"Connection error: {str(e)}")
            return False
    
    def test_personalized_content_multilingual(self):
        """Test POST /api/personalized-content/multilingual endpoint"""
        try:
            # Test with Kenya coordinates (Nairobi) and proper payload structure
            test_payload = {
                "location": {
                    "latitude": -1.2921,
                    "longitude": 36.8219
                },
                "preferences": {
                    "user_id": "test_user_123",
                    "theme": "dark",
                    "language": "en",
                    "region": "KE",
                    "offline_mode": False,
                    "notifications": {
                        "enabled": True,
                        "news_updates": True,
                        "music_discovery": True
                    },
                    "audio": {
                        "quality": "high",
                        "volume": 0.8
                    }
                }
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/personalized-content/multilingual",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for critical radio_streams data
                if "radio_streams" in data:
                    radio_streams = data["radio_streams"]
                    if "main_station" in radio_streams and "alternative_streams" in radio_streams:
                        main_station = radio_streams["main_station"]
                        alt_streams = radio_streams["alternative_streams"]
                        
                        if main_station.get("streamUrl") and len(alt_streams) > 0:
                            self.log_test("Personalized Content API", True, 
                                        f"Complete with radio_streams: main + {len(alt_streams)} alternatives", response_time)
                            return True
                        else:
                            self.log_test("Personalized Content API", False, 
                                        "radio_streams missing stream URLs", response_time)
                            return False
                    else:
                        self.log_test("Personalized Content API", False, 
                                    "radio_streams missing main_station or alternative_streams", response_time)
                        return False
                else:
                    self.log_test("Personalized Content API", False, 
                                "Missing critical radio_streams data", response_time)
                    return False
            else:
                self.log_test("Personalized Content API", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Personalized Content API", False, f"Connection error: {str(e)}")
            return False
    
    def test_stream_accessibility(self):
        """Test accessibility of main radio stream"""
        try:
            # First get the stream URL from station-info
            response = self.session.get(f"{self.backend_url}/station-info")
            if response.status_code != 200:
                self.log_test("Stream Accessibility", False, "Could not get station info for stream URL")
                return False
                
            data = response.json()
            stream_url = data.get("streamUrl")
            
            if not stream_url:
                self.log_test("Stream Accessibility", False, "No stream URL found in station info")
                return False
            
            # Test stream accessibility
            start_time = time.time()
            stream_response = self.session.head(stream_url, timeout=5)
            response_time = time.time() - start_time
            
            if stream_response.status_code == 200:
                content_type = stream_response.headers.get("Content-Type", "")
                if "audio" in content_type.lower():
                    self.log_test("Stream Accessibility", True, 
                                f"Stream accessible: {stream_url} ({content_type})", response_time)
                    return True
                else:
                    self.log_test("Stream Accessibility", False, 
                                f"Stream URL not audio content: {content_type}", response_time)
                    return False
            else:
                self.log_test("Stream Accessibility", False, 
                            f"Stream not accessible: HTTP {stream_response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Stream Accessibility", False, f"Stream test error: {str(e)}")
            return False
    
    def test_basic_connectivity(self):
        """Test basic backend connectivity and response times"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                if response_time < 2.0:  # Under 2 seconds is good
                    self.log_test("Basic Connectivity", True, 
                                f"Backend responsive in {response_time:.2f}s", response_time)
                    return True
                else:
                    self.log_test("Basic Connectivity", False, 
                                f"Backend slow response: {response_time:.2f}s", response_time)
                    return False
            else:
                self.log_test("Basic Connectivity", False, 
                            f"Backend not accessible: HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_multilingual_station_info(self):
        """Test POST /api/station-info/multilingual endpoint"""
        try:
            # Test with Kenya coordinates
            test_payload = {
                "latitude": -1.2921,
                "longitude": 36.8219
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/station-info/multilingual",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "detected_language"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    detected_lang = data.get("detected_language", "")
                    stream_url = data.get("streamUrl", "")
                    
                    if detected_lang and stream_url:
                        self.log_test("Multilingual Station Info", True, 
                                    f"Language detected: {detected_lang}, Stream: {stream_url}", response_time)
                        return True
                    else:
                        self.log_test("Multilingual Station Info", False, 
                                    "Missing language detection or stream URL", response_time)
                        return False
                else:
                    self.log_test("Multilingual Station Info", False, 
                                f"Missing required fields: {missing_fields}", response_time)
                    return False
            else:
                self.log_test("Multilingual Station Info", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Multilingual Station Info", False, f"Connection error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🎵 KAGEMA FM BACKEND API TESTING STARTED")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Core tests as requested in review
        tests = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("API Root", self.test_api_root),
            ("Station Info", self.test_station_info),
            ("Personalized Content API", self.test_personalized_content_multilingual),
            ("Multilingual Station Info", self.test_multilingual_station_info),
            ("Stream Accessibility", self.test_stream_accessibility),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        print("=" * 60)
        success_rate = (passed_tests / total_tests) * 100
        print(f"🎯 TEST SUMMARY: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 90:
            print("✅ BACKEND STATUS: EXCELLENT - Production ready")
        elif success_rate >= 75:
            print("⚠️  BACKEND STATUS: GOOD - Minor issues detected")
        else:
            print("❌ BACKEND STATUS: NEEDS ATTENTION - Critical issues found")
        
        return self.test_results, success_rate

def main():
    """Main test execution"""
    tester = KagemaFMBackendTester()
    results, success_rate = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/kagema_fm_test_results.json", "w") as f:
        json.dump({
            "test_results": results,
            "success_rate": success_rate,
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["success"]),
            "test_timestamp": datetime.now().isoformat(),
            "backend_url": BACKEND_URL
        }, f, indent=2)
    
    return success_rate >= 75  # Return True if tests are mostly successful

if __name__ == "__main__":
    main()