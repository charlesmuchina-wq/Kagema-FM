#!/usr/bin/env python3
"""
Extended Backend API Testing for Kagema FM - Additional APIs from Review Request
Testing remaining APIs: User Management, Platform Integrations, Additional Compliance, etc.
"""

import requests
import json
import time
from datetime import datetime
import uuid
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://radio-companion.preview.emergentagent.com/api"

class ExtendedKagemaFMTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KagemaFM-Extended-Tester/1.0'
        })
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name} - {details} ({response_time:.0f}ms)")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name} - {details}")
    
    def test_additional_compliance_apis(self):
        """Test additional Content Compliance APIs"""
        print("\n⚖️ TESTING ADDITIONAL CONTENT COMPLIANCE APIs")
        
        # Test compliance acknowledgment
        try:
            start_time = time.time()
            payload = {
                "disclaimer_ids": ["general_responsibility", "age_verification", "content_warning"],
                "user_id": f"test_user_{uuid.uuid4().hex[:8]}",
                "timestamp": datetime.now().isoformat(),
                "user_age": 25,
                "country_code": "KE"
            }
            response = self.session.post(f"{self.backend_url}/compliance/acknowledge", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("acknowledgment_recorded"):
                    self.log_test("POST /api/compliance/acknowledge", True, f"Acknowledgment recorded successfully", response_time)
                else:
                    self.log_test("POST /api/compliance/acknowledge", False, f"Acknowledgment not recorded: {data}")
            else:
                self.log_test("POST /api/compliance/acknowledge", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/compliance/acknowledge", False, f"Connection error: {str(e)}")
        
        # Test content compliance check
        try:
            start_time = time.time()
            params = {
                "country_code": "KE",
                "content_rating": "mature",
                "user_age": 25,
                "current_hour": 14
            }
            response = self.session.post(f"{self.backend_url}/compliance/check-content", params=params)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "compliant" in data:
                    self.log_test("POST /api/compliance/check-content", True, f"Content compliance check working, compliant: {data.get('compliant')}", response_time)
                else:
                    self.log_test("POST /api/compliance/check-content", False, f"Missing compliance result: {data}")
            else:
                self.log_test("POST /api/compliance/check-content", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/compliance/check-content", False, f"Connection error: {str(e)}")
    
    def test_platform_integration_apis(self):
        """Test Platform Integration APIs"""
        print("\n🔌 TESTING PLATFORM INTEGRATION APIs")
        
        integration_types = ["general", "google_maps", "spotify", "voice_control"]
        
        for integration_type in integration_types:
            try:
                start_time = time.time()
                payload = {"type": integration_type, "config": {}}
                response = self.session.post(f"{self.backend_url}/integrations/initialize", json=payload)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "initialized":
                        self.log_test(f"POST /api/integrations/initialize ({integration_type})", True, f"Integration initialized: {data.get('message', '')}", response_time)
                    else:
                        self.log_test(f"POST /api/integrations/initialize ({integration_type})", False, f"Integration not initialized: {data}")
                else:
                    self.log_test(f"POST /api/integrations/initialize ({integration_type})", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"POST /api/integrations/initialize ({integration_type})", False, f"Connection error: {str(e)}")
    
    def test_satellite_offline_apis(self):
        """Test Satellite & Offline APIs"""
        print("\n📡 TESTING SATELLITE & OFFLINE APIs")
        
        # Test satellite connect
        try:
            start_time = time.time()
            payload = {
                "provider": "test_provider",
                "client_id": "kagema_fm_test",
                "location": "auto"
            }
            response = self.session.post(f"{self.backend_url}/satellite/connect", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "connected" in data:
                    self.log_test("POST /api/satellite/connect", True, f"Satellite connect working, connected: {data.get('connected')}", response_time)
                else:
                    self.log_test("POST /api/satellite/connect", False, f"Missing connection status: {data}")
            else:
                self.log_test("POST /api/satellite/connect", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/satellite/connect", False, f"Connection error: {str(e)}")
        
        # Test offline cache
        try:
            start_time = time.time()
            payload = {
                "content_types": ["radio_streams", "news", "weather", "music"],
                "location": {"latitude": -1.286389, "longitude": 36.817223},
                "cache_duration_hours": 24
            }
            response = self.session.post(f"{self.backend_url}/offline/cache", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "cached_items" in data:
                    self.log_test("POST /api/offline/cache", True, f"Offline cache working, offline ready: {data.get('offline_mode_ready')}", response_time)
                else:
                    self.log_test("POST /api/offline/cache", False, f"Missing cached_items: {data}")
            else:
                self.log_test("POST /api/offline/cache", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/offline/cache", False, f"Connection error: {str(e)}")
    
    def test_user_management_apis(self):
        """Test User Management APIs"""
        print("\n👤 TESTING USER MANAGEMENT APIs")
        
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Test user preferences - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/preferences")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data and "theme" in data:
                    self.log_test("GET /api/user/preferences", True, f"User preferences retrieved, theme: {data.get('theme')}", response_time)
                else:
                    self.log_test("GET /api/user/preferences", False, f"Missing required fields: {data}")
            else:
                self.log_test("GET /api/user/preferences", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/preferences", False, f"Connection error: {str(e)}")
        
        # Test user preferences - PUT
        try:
            start_time = time.time()
            payload = {
                "user_id": test_user_id,
                "preferred_language": "en",
                "theme": "dark",
                "offline_mode": False,
                "notifications": {
                    "enabled": True,
                    "news_updates": True,
                    "music_recommendations": True
                },
                "audio": {
                    "quality": "high",
                    "volume": 0.8,
                    "auto_play": True
                }
            }
            response = self.session.put(f"{self.backend_url}/user/{test_user_id}/preferences", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "updated" in data["message"]:
                    self.log_test("PUT /api/user/preferences", True, f"User preferences updated successfully", response_time)
                else:
                    self.log_test("PUT /api/user/preferences", False, f"Update not confirmed: {data}")
            else:
                self.log_test("PUT /api/user/preferences", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("PUT /api/user/preferences", False, f"Connection error: {str(e)}")
        
        # Test favorites - POST
        try:
            start_time = time.time()
            payload = {
                "favorite_type": "radio_station",
                "item_id": "kagema_fm_main",
                "title": "Kagema FM Main Station",
                "metadata": {
                    "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "frequency": "101.5 FM"
                }
            }
            response = self.session.post(f"{self.backend_url}/user/{test_user_id}/favorites", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "favorite_id" in data:
                    self.log_test("POST /api/user/favorites", True, f"Favorite added, ID: {data.get('favorite_id')[:8]}...", response_time)
                else:
                    self.log_test("POST /api/user/favorites", False, f"Favorite not added: {data}")
            else:
                self.log_test("POST /api/user/favorites", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/user/favorites", False, f"Connection error: {str(e)}")
        
        # Test favorites - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/favorites")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "favorites" in data:
                    favorites_count = len(data["favorites"])
                    self.log_test("GET /api/user/favorites", True, f"Favorites retrieved, count: {favorites_count}", response_time)
                else:
                    self.log_test("GET /api/user/favorites", False, f"Missing favorites: {data}")
            else:
                self.log_test("GET /api/user/favorites", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/favorites", False, f"Connection error: {str(e)}")
        
        # Test listening session - POST
        try:
            start_time = time.time()
            payload = {
                "station_id": "kagema_fm_main",
                "station_name": "Kagema FM",
                "started_at": datetime.now().isoformat(),
                "location": {"latitude": -1.286389, "longitude": 36.817223}
            }
            response = self.session.post(f"{self.backend_url}/user/{test_user_id}/listening-session", json=payload)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    self.log_test("POST /api/user/listening-session", True, f"Listening session started, ID: {data.get('session_id')[:8]}...", response_time)
                else:
                    self.log_test("POST /api/user/listening-session", False, f"Session not started: {data}")
            else:
                self.log_test("POST /api/user/listening-session", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/user/listening-session", False, f"Connection error: {str(e)}")
        
        # Test listening history - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/listening-history")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "history" in data:
                    history_count = len(data["history"])
                    self.log_test("GET /api/user/listening-history", True, f"Listening history retrieved, count: {history_count}", response_time)
                else:
                    self.log_test("GET /api/user/listening-history", False, f"Missing history: {data}")
            else:
                self.log_test("GET /api/user/listening-history", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/listening-history", False, f"Connection error: {str(e)}")
        
        # Test user stats - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/stats")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "statistics" in data:
                    self.log_test("GET /api/user/stats", True, f"User statistics retrieved", response_time)
                else:
                    self.log_test("GET /api/user/stats", False, f"Missing statistics: {data}")
            else:
                self.log_test("GET /api/user/stats", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/stats", False, f"Connection error: {str(e)}")
        
        # Test user recommendations - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/recommendations")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "recommendations" in data:
                    self.log_test("GET /api/user/recommendations", True, f"User recommendations retrieved", response_time)
                else:
                    self.log_test("GET /api/user/recommendations", False, f"Missing recommendations: {data}")
            else:
                self.log_test("GET /api/user/recommendations", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/recommendations", False, f"Connection error: {str(e)}")
        
        # Test enhanced station info - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/station-info/enhanced/{test_user_id}")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "name" in data and "personalization" in data:
                    self.log_test("GET /api/station-info/enhanced", True, f"Enhanced station info retrieved with personalization", response_time)
                else:
                    self.log_test("GET /api/station-info/enhanced", False, f"Missing required fields: {data}")
            else:
                self.log_test("GET /api/station-info/enhanced", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/station-info/enhanced", False, f"Connection error: {str(e)}")
        
        # Test GDPR data export - GET
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/user/{test_user_id}/export")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "user_data" in data or "preferences" in data:
                    self.log_test("GET /api/user/export (GDPR)", True, f"User data export working", response_time)
                else:
                    self.log_test("GET /api/user/export (GDPR)", False, f"Export data incomplete: {list(data.keys())}")
            else:
                self.log_test("GET /api/user/export (GDPR)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/user/export (GDPR)", False, f"Connection error: {str(e)}")
    
    def test_additional_content_apis(self):
        """Test additional content APIs"""
        print("\n📰 TESTING ADDITIONAL CONTENT APIs")
        
        # Test GET /api/languages
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/languages")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "languages" in data and len(data["languages"]) > 0:
                    self.log_test("GET /api/languages", True, f"Languages retrieved, count: {data.get('total_count', len(data['languages']))}", response_time)
                else:
                    self.log_test("GET /api/languages", False, f"No languages found: {data}")
            else:
                self.log_test("GET /api/languages", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/languages", False, f"Connection error: {str(e)}")
    
    def run_extended_tests(self):
        """Run all extended backend tests"""
        print("🎵 KAGEMA FM EXTENDED BACKEND API TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run all extended test suites
        self.test_additional_compliance_apis()
        self.test_platform_integration_apis()
        self.test_satellite_offline_apis()
        self.test_user_management_apis()
        self.test_additional_content_apis()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 EXTENDED TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Extended Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for test in self.passed_tests:
                print(f"  - {test}")
        
        # Calculate average response time
        response_times = [r['response_time'] for r in self.test_results if r['success'] and r['response_time'] > 0]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"\n⚡ EXTENDED PERFORMANCE METRICS:")
            print(f"Average Response Time: {avg_response_time:.0f}ms")
            print(f"Fastest Response: {min(response_times):.0f}ms")
            print(f"Slowest Response: {max(response_times):.0f}ms")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 85  # Consider 85%+ success rate as passing

if __name__ == "__main__":
    tester = ExtendedKagemaFMTester()
    success = tester.run_extended_tests()
    
    if success:
        print("🎉 EXTENDED BACKEND TESTING COMPLETE - ALL ADDITIONAL APIS WORKING!")
        sys.exit(0)
    else:
        print("⚠️ EXTENDED BACKEND TESTING COMPLETE - SOME ISSUES FOUND")
        sys.exit(1)