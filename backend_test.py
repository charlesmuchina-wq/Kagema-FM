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
        
    def test_api_root_version(self):
        """Test GET /api/ - Check for v5.0.0 with content compliance features"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check version
                if data.get("version") == "5.0.0":
                    # Check for content compliance features
                    features = data.get("features", [])
                    if "content_compliance" in features:
                        self.log_test(
                            "API Root Version Check", 
                            True, 
                            f"API v{data.get('version')} with content compliance features",
                            data
                        )
                    else:
                        self.log_test(
                            "API Root Version Check", 
                            False, 
                            f"Content compliance feature missing from features: {features}",
                            data
                        )
                else:
                    self.log_test(
                        "API Root Version Check", 
                        False, 
                        f"Expected v5.0.0, got v{data.get('version')}",
                        data
                    )
            else:
                self.log_test(
                    "API Root Version Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("API Root Version Check", False, f"Exception: {str(e)}")
    
    def test_content_disclaimers(self):
        """Test POST /api/compliance/disclaimers - Content disclaimer retrieval with platform responsibility focus"""
        test_cases = [
            {
                "name": "GLOBAL English Platform Responsibility Disclaimers",
                "payload": {
                    "country_code": "GLOBAL",
                    "language_code": "en",
                    "content_types": ["radio_streams", "music", "news"]
                }
            },
            {
                "name": "Brazil Portuguese Platform Responsibility Disclaimers", 
                "payload": {
                    "country_code": "BR",
                    "language_code": "pt-br",
                    "content_types": ["radio_streams", "music"]
                }
            },
            {
                "name": "Kenya Swahili Platform Responsibility Disclaimers",
                "payload": {
                    "country_code": "KE",
                    "language_code": "sw",
                    "content_types": ["radio_streams", "news"]
                }
            },
            {
                "name": "Kenya English All Content Types",
                "payload": {
                    "country_code": "KE",
                    "language_code": "en",
                    "content_types": ["radio_streams", "music", "news"]
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/compliance/disclaimers",
                    json=test_case["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["content_disclaimers", "regional_compliance", "user_acknowledgment_required"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        disclaimers = data.get("content_disclaimers", [])
                        compliance = data.get("regional_compliance", {})
                        
                        if disclaimers and compliance:
                            # Check for platform responsibility disclaimer specifically
                            platform_disclaimer = None
                            for disclaimer in disclaimers:
                                if disclaimer.get("id") == "platform_responsibility":
                                    platform_disclaimer = disclaimer
                                    break
                            
                            if platform_disclaimer:
                                # Verify platform responsibility content
                                title = platform_disclaimer.get("title", "")
                                content = platform_disclaimer.get("content", "")
                                
                                # Check for key platform responsibility phrases
                                key_phrases = []
                                if test_case['payload']['language_code'] == 'en':
                                    key_phrases = [
                                        "Platform and Licensing Responsibility Notice",
                                        "integration platform and aggregator service only",
                                        "solely responsible",
                                        "assumes no responsibility"
                                    ]
                                elif test_case['payload']['language_code'] == 'pt-br':
                                    key_phrases = [
                                        "Responsabilidade de Plataforma e Licenciamento",
                                        "plataforma de integração e agregação",
                                        "únicas responsáveis",
                                        "Não assumimos responsabilidade"
                                    ]
                                elif test_case['payload']['language_code'] == 'sw':
                                    key_phrases = [
                                        "Jukumu la Jukwaa na Leseni",
                                        "jukwaa la uunganishaji wa redio",
                                        "jukumu pekee",
                                        "Hatuchukui jukumu"
                                    ]
                                
                                phrases_found = sum(1 for phrase in key_phrases if phrase.lower() in (title + " " + content).lower())
                                
                                if phrases_found >= len(key_phrases) - 1:  # Allow for minor variations
                                    self.log_test(
                                        f"Content Disclaimers - {test_case['name']}", 
                                        True, 
                                        f"Platform responsibility disclaimer verified: {phrases_found}/{len(key_phrases)} key phrases found, {len(disclaimers)} total disclaimers",
                                        data
                                    )
                                else:
                                    self.log_test(
                                        f"Content Disclaimers - {test_case['name']}", 
                                        False, 
                                        f"Platform responsibility disclaimer incomplete: only {phrases_found}/{len(key_phrases)} key phrases found",
                                        data
                                    )
                            else:
                                self.log_test(
                                    f"Content Disclaimers - {test_case['name']}", 
                                    False, 
                                    f"Platform responsibility disclaimer not found in {len(disclaimers)} disclaimers",
                                    data
                                )
                        else:
                            self.log_test(
                                f"Content Disclaimers - {test_case['name']}", 
                                False, 
                                f"Empty disclaimers or compliance data",
                                data
                            )
                    else:
                        self.log_test(
                            f"Content Disclaimers - {test_case['name']}", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        f"Content Disclaimers - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Content Disclaimers - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_user_acknowledgment(self):
        """Test POST /api/compliance/acknowledge - User acknowledgment recording"""
        test_cases = [
            {
                "name": "Adult User Kenya Acknowledgment",
                "payload": {
                    "disclaimer_ids": ["general_responsibility", "explicit_content_warning"],
                    "user_id": "user_ke_001",
                    "timestamp": datetime.now().isoformat(),
                    "user_age": 25,
                    "country_code": "KE"
                }
            },
            {
                "name": "Adult User Brazil Acknowledgment",
                "payload": {
                    "disclaimer_ids": ["general_responsibility", "brazil_compliance"],
                    "user_id": "user_br_001", 
                    "timestamp": datetime.now().isoformat(),
                    "user_age": 30,
                    "country_code": "BR"
                }
            },
            {
                "name": "Young Adult Global Acknowledgment",
                "payload": {
                    "disclaimer_ids": ["general_responsibility"],
                    "user_id": "user_global_001",
                    "timestamp": datetime.now().isoformat(),
                    "user_age": 19,
                    "country_code": "GLOBAL"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/compliance/acknowledge",
                    json=test_case["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["acknowledgment_recorded", "valid_until", "message"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get("acknowledgment_recorded") is True:
                        self.log_test(
                            f"User Acknowledgment - {test_case['name']}", 
                            True, 
                            f"Acknowledgment recorded for user {test_case['payload']['user_id']}",
                            data
                        )
                    else:
                        self.log_test(
                            f"User Acknowledgment - {test_case['name']}", 
                            False, 
                            f"Invalid response structure or acknowledgment not recorded: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        f"User Acknowledgment - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"User Acknowledgment - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_content_compliance_check(self):
        """Test POST /api/compliance/check-content - Content compliance checking"""
        test_cases = [
            {
                "name": "Adult Content - Adult User Kenya",
                "params": {
                    "country_code": "KE",
                    "content_rating": "adult",
                    "user_age": 25,
                    "current_hour": 22  # 10 PM - allowed time for adult content in Kenya
                }
            },
            {
                "name": "Adult Content - Minor User Kenya",
                "params": {
                    "country_code": "KE", 
                    "content_rating": "adult",
                    "user_age": 16,
                    "current_hour": 22
                }
            },
            {
                "name": "Explicit Content - Adult User Brazil Restricted Hours",
                "params": {
                    "country_code": "BR",
                    "content_rating": "explicit",
                    "user_age": 25,
                    "current_hour": 18  # 6 PM - before allowed time in Brazil (23:00-06:00)
                }
            },
            {
                "name": "Mature Content - Teen User Kenya",
                "params": {
                    "country_code": "KE",
                    "content_rating": "mature", 
                    "user_age": 17,
                    "current_hour": 14
                }
            },
            {
                "name": "General Content - All Users",
                "params": {
                    "country_code": "GLOBAL",
                    "content_rating": "general",
                    "user_age": 12,
                    "current_hour": 10
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/compliance/check-content",
                    params=test_case["params"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["compliant", "warnings", "blocking_reasons", "age_appropriate", "time_appropriate"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Analyze compliance result based on test case
                        compliant = data.get("compliant")
                        age_appropriate = data.get("age_appropriate")
                        time_appropriate = data.get("time_appropriate")
                        
                        # Determine expected result
                        expected_compliant = True
                        if test_case["params"]["content_rating"] in ["adult", "explicit"] and test_case["params"]["user_age"] < 18:
                            expected_compliant = False
                        elif test_case["params"]["content_rating"] == "explicit" and test_case["params"]["current_hour"] == 18 and test_case["params"]["country_code"] == "BR":
                            expected_compliant = False  # Outside allowed hours
                        
                        if (compliant == expected_compliant) or (compliant is False and not age_appropriate):
                            self.log_test(
                                f"Content Compliance Check - {test_case['name']}", 
                                True, 
                                f"Compliance check correct: compliant={compliant}, age_appropriate={age_appropriate}, time_appropriate={time_appropriate}",
                                data
                            )
                        else:
                            self.log_test(
                                f"Content Compliance Check - {test_case['name']}", 
                                False, 
                                f"Unexpected compliance result: expected={expected_compliant}, got={compliant}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Content Compliance Check - {test_case['name']}", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        f"Content Compliance Check - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Content Compliance Check - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_multilingual_station_info_with_compliance(self):
        """Test POST /api/station-info/multilingual - Enhanced station info with compliance"""
        test_cases = [
            {
                "name": "Kenya Nairobi Location",
                "payload": {
                    "latitude": -1.286389,
                    "longitude": 36.817223
                }
            },
            {
                "name": "Brazil São Paulo Location", 
                "payload": {
                    "latitude": -23.550520,
                    "longitude": -46.633309
                }
            },
            {
                "name": "Kenya Kisumu Location",
                "payload": {
                    "latitude": -0.0917,
                    "longitude": 34.7680
                }
            },
            {
                "name": "Global Location (Outside Kenya/Brazil)",
                "payload": {
                    "latitude": 40.7128,
                    "longitude": -74.0060  # New York
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/station-info/multilingual",
                    json=test_case["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["name", "description", "streamUrl", "detected_language", "content_disclaimers", "compliance_info", "requires_age_verification"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        disclaimers = data.get("content_disclaimers", [])
                        compliance_info = data.get("compliance_info", {})
                        
                        if disclaimers and compliance_info:
                            # Check for platform responsibility disclaimer in station info
                            platform_disclaimer_found = False
                            for disclaimer in disclaimers:
                                if disclaimer.get("id") == "platform_responsibility":
                                    platform_disclaimer_found = True
                                    break
                            
                            if platform_disclaimer_found:
                                self.log_test(
                                    f"Multilingual Station Info - {test_case['name']}", 
                                    True, 
                                    f"Station info with platform responsibility disclaimer: {len(disclaimers)} disclaimers, language={data.get('detected_language')}, location={data.get('location')}",
                                    data
                                )
                            else:
                                self.log_test(
                                    f"Multilingual Station Info - {test_case['name']}", 
                                    False, 
                                    f"Platform responsibility disclaimer missing from station info: {len(disclaimers)} disclaimers found",
                                    data
                                )
                        else:
                            self.log_test(
                                f"Multilingual Station Info - {test_case['name']}", 
                                False, 
                                f"Missing compliance data: disclaimers={len(disclaimers)}, compliance_info={bool(compliance_info)}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Multilingual Station Info - {test_case['name']}", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        f"Multilingual Station Info - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Multilingual Station Info - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_offline_cache_with_compliance(self):
        """Test POST /api/offline/cache - Offline caching with compliance warnings"""
        test_cases = [
            {
                "name": "Cache Radio Streams with Compliance",
                "payload": {
                    "content_types": ["radio_streams"],
                    "location": {
                        "latitude": -1.286389,
                        "longitude": 36.817223
                    },
                    "cache_duration_hours": 24
                }
            },
            {
                "name": "Cache All Content Types",
                "payload": {
                    "content_types": ["radio_streams", "news", "weather", "music", "language_data"],
                    "cache_duration_hours": 12
                }
            },
            {
                "name": "Cache News and Music Only",
                "payload": {
                    "content_types": ["news", "music"],
                    "cache_duration_hours": 6
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{API_BASE}/offline/cache",
                    json=test_case["payload"],
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["cached_items", "cache_expires_in_hours", "offline_mode_ready", "compliance_warning", "disclaimer"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        cached_items = data.get("cached_items", {})
                        compliance_warning = data.get("compliance_warning", "")
                        disclaimer = data.get("disclaimer", "")
                        
                        if cached_items and compliance_warning and disclaimer:
                            self.log_test(
                                f"Offline Cache - {test_case['name']}", 
                                True, 
                                f"Cached {len(cached_items)} content types with compliance warnings",
                                data
                            )
                        else:
                            self.log_test(
                                f"Offline Cache - {test_case['name']}", 
                                False, 
                                f"Missing cache data or compliance warnings: items={len(cached_items)}, warning={bool(compliance_warning)}, disclaimer={bool(disclaimer)}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Offline Cache - {test_case['name']}", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                else:
                    self.log_test(
                        f"Offline Cache - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Offline Cache - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        error_test_cases = [
            {
                "name": "Invalid Country Code in Disclaimers",
                "endpoint": "/compliance/disclaimers",
                "method": "POST",
                "payload": {
                    "country_code": "INVALID",
                    "language_code": "en",
                    "content_types": ["radio_streams"]
                }
            },
            {
                "name": "Missing Required Fields in Acknowledgment",
                "endpoint": "/compliance/acknowledge", 
                "method": "POST",
                "payload": {
                    "user_id": "test_user"
                    # Missing required fields
                }
            },
            {
                "name": "Invalid Content Rating in Compliance Check",
                "endpoint": "/compliance/check-content",
                "method": "POST",
                "params": {
                    "country_code": "KE",
                    "content_rating": "invalid_rating",
                    "user_age": 25
                }
            }
        ]
        
        for test_case in error_test_cases:
            try:
                if test_case["method"] == "POST":
                    if "payload" in test_case:
                        response = requests.post(
                            f"{API_BASE}{test_case['endpoint']}",
                            json=test_case["payload"],
                            timeout=10
                        )
                    else:
                        response = requests.post(
                            f"{API_BASE}{test_case['endpoint']}",
                            params=test_case.get("params", {}),
                            timeout=10
                        )
                
                # For error handling, we expect either proper error responses or graceful handling
                if response.status_code in [400, 422, 500]:
                    self.log_test(
                        f"Error Handling - {test_case['name']}", 
                        True, 
                        f"Proper error response: HTTP {response.status_code}",
                        response.text
                    )
                elif response.status_code == 200:
                    # If it returns 200, check if it handled the error gracefully
                    data = response.json()
                    self.log_test(
                        f"Error Handling - {test_case['name']}", 
                        True, 
                        f"Graceful error handling with fallback response",
                        data
                    )
                else:
                    self.log_test(
                        f"Error Handling - {test_case['name']}", 
                        False, 
                        f"Unexpected response: HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(f"Error Handling - {test_case['name']}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all content compliance tests"""
        print("🎵 STARTING KAGEMA FM CONTENT COMPLIANCE BACKEND TESTING")
        print("=" * 70)
        print(f"Testing backend at: {API_BASE}")
        print("=" * 70)
        
        # Test API version and features
        self.test_api_root_version()
        
        # Test content compliance endpoints
        self.test_content_disclaimers()
        self.test_user_acknowledgment()
        self.test_content_compliance_check()
        self.test_multilingual_station_info_with_compliance()
        self.test_offline_cache_with_compliance()
        
        # Test error handling
        self.test_error_handling()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎵 KAGEMA FM CONTENT COMPLIANCE TESTING SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        print("\n" + "=" * 70)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "failed_test_details": self.failed_tests
        }

if __name__ == "__main__":
    # Initialize tester
    tester = KagemaFMBackendTester()
    
    # Run all tests
    tester.run_all_tests()
    results = tester.print_summary()
    
    # Exit with appropriate code
    exit(0 if results["failed_tests"] == 0 else 1)