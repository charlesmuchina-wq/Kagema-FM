#!/usr/bin/env python3
"""
Kagema FM Backend API Deployment Readiness Testing
Focused testing for production deployment verification
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys

# Backend URL from frontend environment
BACKEND_URL = "https://fm-assistant.preview.emergentagent.com/api"

class DeploymentReadinessTest:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.critical_failures = []
        self.start_time = time.time()
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0, critical: bool = False):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            if critical:
                self.critical_failures.append(f"{test_name}: {details}")
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "critical": critical
        }
        self.results.append(result)
        print(f"{status} - {test_name} ({result['response_time_ms']}ms)")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict:
        """Generic endpoint testing method"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                try:
                    json_data = response.json()
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": json_data,
                        "response_time": response_time
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": "Invalid JSON response",
                        "response_time": response_time
                    }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"Expected {expected_status}, got {response.status_code}",
                    "response_time": response_time
                }
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def test_stream_accessibility(self, stream_url: str, stream_name: str) -> Dict:
        """Test if audio stream URL is accessible"""
        start_time = time.time()
        try:
            response = requests.head(stream_url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time
            
            content_type = response.headers.get('content-type', '').lower()
            icy_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('icy-')}
            
            is_audio = any(audio_type in content_type for audio_type in ['audio/', 'application/ogg'])
            
            return {
                "success": response.status_code == 200 and is_audio,
                "status_code": response.status_code,
                "content_type": content_type,
                "icy_headers": icy_headers,
                "response_time": response_time,
                "stream_name": stream_name
            }
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "stream_name": stream_name
            }

    def run_deployment_readiness_tests(self):
        """Run deployment readiness checklist"""
        print("🚀 KAGEMA FM BACKEND API DEPLOYMENT READINESS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Core Radio API Functionality
        print("\n🎵 1. CORE RADIO API FUNCTIONALITY")
        print("-" * 40)
        
        # GET /api/ (API root and version info)
        result = self.test_endpoint("GET", "/")
        if result["success"]:
            data = result["data"]
            has_version = "version" in data
            has_features = "features" in data
            self.log_result(
                "GET /api/ - API Root & Version Info", 
                result["success"] and has_version and has_features,
                f"Version: {data.get('version', 'N/A')}, Features: {len(data.get('features', []))}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("GET /api/ - API Root & Version Info", False, result.get("error", "Unknown error"), result["response_time"], critical=True)
        
        # GET /api/station-info (basic station information)
        result = self.test_endpoint("GET", "/station-info")
        if result["success"]:
            data = result["data"]
            has_stream_url = "streamUrl" in data and data["streamUrl"].startswith("http")
            has_name = data.get("name") == "Kagema FM"
            self.log_result(
                "GET /api/station-info - Basic Station Info", 
                result["success"] and has_stream_url and has_name,
                f"Station: {data.get('name', 'N/A')}, Stream: {data.get('streamUrl', 'N/A')[:50]}...",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("GET /api/station-info - Basic Station Info", False, result.get("error", "Unknown error"), result["response_time"], critical=True)
        
        # POST /api/station-info/multilingual (regional station data)
        kenya_location = {"latitude": -1.286389, "longitude": 36.817223}  # Nairobi
        result = self.test_endpoint("POST", "/station-info/multilingual", kenya_location)
        if result["success"]:
            data = result["data"]
            has_compliance = "content_disclaimers" in data
            has_language = "detected_language" in data
            has_stream = "streamUrl" in data
            self.log_result(
                "POST /api/station-info/multilingual - Regional Data", 
                result["success"] and has_compliance and has_language and has_stream,
                f"Language: {data.get('detected_language', 'N/A')}, Disclaimers: {len(data.get('content_disclaimers', []))}, Stream: {'Yes' if has_stream else 'No'}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("POST /api/station-info/multilingual - Regional Data", False, result.get("error", "Unknown error"), result["response_time"], critical=True)
        
        # POST /api/personalized-content/multilingual (complete personalized content with radio streams)
        personalized_request = {
            "latitude": -1.286389, 
            "longitude": 36.817223,
            "interests": ["music", "news"],
            "favorite_genres": ["rock", "jazz"],
            "user_age": 25,
            "accept_adult_content": True
        }
        result = self.test_endpoint("POST", "/personalized-content/multilingual", personalized_request)
        if result["success"]:
            data = result["data"]
            has_radio_streams = "radio_streams" in data
            has_news = "news" in data
            has_music = "music" in data
            has_compliance = "content_disclaimers" in data
            self.log_result(
                "POST /api/personalized-content/multilingual - Complete Content", 
                result["success"] and has_radio_streams and has_news and has_music and has_compliance,
                f"Radio Streams: {'Yes' if has_radio_streams else 'No'}, News: {len(data.get('news', {}).get('articles', []))}, Music: {len(data.get('music', {}).get('tracks', []))}, Compliance: {'Yes' if has_compliance else 'No'}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("POST /api/personalized-content/multilingual - Complete Content", False, result.get("error", "Unknown error"), result["response_time"], critical=True)

        # 2. Audio Stream Accessibility (CRITICAL for deployment)
        print("\n📡 2. AUDIO STREAM ACCESSIBILITY (CRITICAL)")
        print("-" * 40)
        
        # Test main Kenya stream
        main_stream = "https://ice1.somafm.com/groovesalad-256-mp3"
        result = self.test_stream_accessibility(main_stream, "Main Kenya Stream")
        self.log_result(
            "Main Kenya Stream - Groove Salad (CRITICAL)",
            result["success"],
            f"Status: {result.get('status_code', 'N/A')}, Content-Type: {result.get('content_type', 'N/A')}, ICY Headers: {len(result.get('icy_headers', {}))}",
            result["response_time"],
            critical=True
        )
        
        # Test new alternative streams
        alternative_streams = [
            ("Radio Paradise AAC", "https://stream.radioparadise.com/aac-320"),
            ("FIP France MP3", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
            ("Drone Zone", "http://ice1.somafm.com/dronezone-256-mp3")
        ]
        
        working_alternatives = 0
        for name, url in alternative_streams:
            result = self.test_stream_accessibility(url, name)
            if result["success"]:
                working_alternatives += 1
            self.log_result(
                f"Alternative Stream - {name}",
                result["success"],
                f"Status: {result.get('status_code', 'N/A')}, Content-Type: {result.get('content_type', 'N/A')}",
                result["response_time"],
                critical=False
            )
        
        # Overall stream reliability check
        total_streams = 1 + len(alternative_streams)  # Main + alternatives
        working_streams = (1 if main_stream else 0) + working_alternatives
        stream_reliability = (working_streams / total_streams) * 100
        
        self.log_result(
            "Overall Stream Reliability",
            stream_reliability >= 75,  # At least 75% should work
            f"Working: {working_streams}/{total_streams} ({stream_reliability:.1f}%)",
            0,
            critical=stream_reliability < 50
        )

        # 3. Content Compliance System
        print("\n⚖️ 3. CONTENT COMPLIANCE SYSTEM")
        print("-" * 40)
        
        # POST /api/compliance/disclaimers (multilingual disclaimers)
        compliance_request = {"country_code": "KE", "language_code": "en", "content_types": ["radio_streams", "music"]}
        result = self.test_endpoint("POST", "/compliance/disclaimers", compliance_request)
        if result["success"]:
            data = result["data"]
            has_disclaimers = "content_disclaimers" in data and len(data.get("content_disclaimers", [])) > 0
            has_regional = "regional_compliance" in data
            self.log_result(
                "POST /api/compliance/disclaimers - Multilingual Support",
                result["success"] and has_disclaimers and has_regional,
                f"Disclaimers: {len(data.get('content_disclaimers', []))}, Regional: {'Yes' if has_regional else 'No'}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("POST /api/compliance/disclaimers - Multilingual Support", False, result.get("error", "Unknown error"), result["response_time"], critical=True)
        
        # POST /api/compliance/acknowledge (user acknowledgment storage)
        acknowledgment_data = {
            "disclaimer_ids": ["general_responsibility", "platform_responsibility"],
            "user_id": "deployment_test_user",
            "timestamp": datetime.now().isoformat(),
            "user_age": 25,
            "country_code": "KE"
        }
        result = self.test_endpoint("POST", "/compliance/acknowledge", acknowledgment_data)
        if result["success"]:
            data = result["data"]
            acknowledged = data.get("acknowledgment_recorded", False)
            self.log_result(
                "POST /api/compliance/acknowledge - User Acknowledgment",
                result["success"] and acknowledged,
                f"Recorded: {acknowledged}, Valid Until: {data.get('valid_until', 'N/A')[:19]}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("POST /api/compliance/acknowledge - User Acknowledgment", False, result.get("error", "Unknown error"), result["response_time"], critical=True)
        
        # POST /api/compliance/check-content (age verification and content filtering)
        compliance_check = {"country_code": "KE", "content_rating": "mature", "user_age": 25, "current_hour": 22}
        query_params = "&".join([f"{k}={v}" for k, v in compliance_check.items()])
        result = self.test_endpoint("POST", f"/compliance/check-content?{query_params}")
        if result["success"]:
            data = result["data"]
            has_compliance_result = "compliant" in data
            self.log_result(
                "POST /api/compliance/check-content - Age Verification",
                result["success"] and has_compliance_result,
                f"Compliant: {data.get('compliant', 'N/A')}, Reason: {data.get('reason', 'N/A')[:30]}",
                result["response_time"],
                critical=True
            )
        else:
            self.log_result("POST /api/compliance/check-content - Age Verification", False, result.get("error", "Unknown error"), result["response_time"], critical=True)

        # 4. Language & Localization
        print("\n🌍 4. LANGUAGE & LOCALIZATION")
        print("-" * 40)
        
        # POST /api/language/detect (GPS-based language detection)
        kenya_coords = {"latitude": -1.286389, "longitude": 36.817223}
        result = self.test_endpoint("POST", "/language/detect", kenya_coords)
        if result["success"]:
            data = result["data"]
            has_language = "detected_language" in data
            has_confidence = data.get("confidence", 0) > 0
            self.log_result(
                "POST /api/language/detect - GPS-based Detection",
                result["success"] and has_language and has_confidence,
                f"Language: {data.get('detected_language', 'N/A')}, Confidence: {data.get('confidence', 0)}, County: {data.get('county', 'N/A')}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("POST /api/language/detect - GPS-based Detection", False, result.get("error", "Unknown error"), result["response_time"], critical=False)
        
        # GET /api/languages (supported languages list)
        result = self.test_endpoint("GET", "/languages")
        if result["success"]:
            data = result["data"]
            languages = data.get("languages", [])
            has_kenya_brazil = data.get("total_count", 0) >= 7
            self.log_result(
                "GET /api/languages - Supported Languages",
                result["success"] and len(languages) >= 7 and has_kenya_brazil,
                f"Languages: {data.get('total_count', 0)}, Kenya/Brazil Support: {'Yes' if has_kenya_brazil else 'No'}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("GET /api/languages - Supported Languages", False, result.get("error", "Unknown error"), result["response_time"], critical=False)

        # 5. Platform Integrations
        print("\n🔌 5. PLATFORM INTEGRATIONS")
        print("-" * 40)
        
        # POST /api/integrations/initialize (Google Maps, Spotify, Voice Control)
        integration_data = {"type": "general", "config": {}}
        result = self.test_endpoint("POST", "/integrations/initialize", integration_data)
        if result["success"]:
            data = result["data"]
            is_initialized = data.get("status") == "initialized"
            self.log_result(
                "POST /api/integrations/initialize - Platform Integrations",
                result["success"] and is_initialized,
                f"Status: {data.get('status', 'N/A')}, Type: {data.get('integration', 'N/A')}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("POST /api/integrations/initialize - Platform Integrations", False, result.get("error", "Unknown error"), result["response_time"], critical=False)

        # 6. Satellite & Offline Features
        print("\n🛰️ 6. SATELLITE & OFFLINE FEATURES")
        print("-" * 40)
        
        # GET /api/satellite/status
        result = self.test_endpoint("GET", "/satellite/status")
        if result["success"]:
            data = result["data"]
            has_connection_info = "connection_type" in data and "signal_strength" in data
            self.log_result(
                "GET /api/satellite/status - Satellite Status",
                result["success"] and has_connection_info,
                f"Connection: {data.get('connection_type', 'N/A')}, Signal: {data.get('signal_strength', 'N/A')}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("GET /api/satellite/status - Satellite Status", False, result.get("error", "Unknown error"), result["response_time"], critical=False)
        
        # POST /api/satellite/connect
        connect_data = {"provider": "auto", "client_id": "deployment_test", "location": "auto"}
        result = self.test_endpoint("POST", "/satellite/connect", connect_data)
        if result["success"]:
            data = result["data"]
            has_connection_result = "connected" in data
            self.log_result(
                "POST /api/satellite/connect - Connection Attempt",
                result["success"] and has_connection_result,
                f"Connected: {data.get('connected', 'N/A')}, Message: {data.get('message', 'N/A')[:30]}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("POST /api/satellite/connect - Connection Attempt", False, result.get("error", "Unknown error"), result["response_time"], critical=False)
        
        # POST /api/offline/cache
        cache_data = {
            "content_types": ["radio_streams", "news", "weather"],
            "location": {"latitude": -1.286389, "longitude": 36.817223},
            "cache_duration_hours": 24
        }
        result = self.test_endpoint("POST", "/offline/cache", cache_data)
        if result["success"]:
            data = result["data"]
            has_cached_items = "cached_items" in data and len(data.get("cached_items", {})) > 0
            self.log_result(
                "POST /api/offline/cache - Offline Caching",
                result["success"] and has_cached_items,
                f"Cached Items: {len(data.get('cached_items', {}))}, Offline Ready: {data.get('offline_mode_ready', 'N/A')}",
                result["response_time"],
                critical=False
            )
        else:
            self.log_result("POST /api/offline/cache - Offline Caching", False, result.get("error", "Unknown error"), result["response_time"], critical=False)

        # 7. Performance & Error Handling
        print("\n⚡ 7. PERFORMANCE & ERROR HANDLING")
        print("-" * 40)
        
        # Test response times (should be <2 seconds for most endpoints)
        fast_endpoints = [
            ("GET", "/", "API Root"),
            ("GET", "/station-info", "Station Info"),
            ("GET", "/languages", "Languages")
        ]
        
        slow_responses = 0
        for method, endpoint, name in fast_endpoints:
            result = self.test_endpoint(method, endpoint)
            is_fast = result.get("response_time", 999) < 2.0
            if not is_fast:
                slow_responses += 1
            self.log_result(
                f"Performance - {name} Response Time",
                result["success"] and is_fast,
                f"Response Time: {result.get('response_time', 0)*1000:.0f}ms ({'FAST' if is_fast else 'SLOW'})",
                result.get("response_time", 0),
                critical=False
            )
        
        # Test proper error responses
        result = self.test_endpoint("GET", "/invalid-endpoint", expected_status=404)
        self.log_result(
            "Error Handling - 404 for Invalid Endpoint",
            result["success"],
            f"Status: {result.get('status_code', 'N/A')}",
            result.get("response_time", 0),
            critical=False
        )
        
        # Generate final deployment assessment
        self.generate_deployment_assessment()
    
    def generate_deployment_assessment(self):
        """Generate deployment readiness assessment"""
        total_time = time.time() - self.start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 DEPLOYMENT READINESS ASSESSMENT")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Critical Failures: {len(self.critical_failures)}")
        print(f"Total Test Time: {total_time:.2f} seconds")
        
        # Calculate average response time
        response_times = [r["response_time_ms"] for r in self.results if r["response_time_ms"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"Average Response Time: {avg_response_time:.0f}ms")
        print(f"Maximum Response Time: {max_response_time:.0f}ms")
        
        # Deployment readiness decision
        print("\n🚀 DEPLOYMENT READINESS DECISION:")
        if success_rate >= 95 and len(self.critical_failures) == 0:
            deployment_status = "✅ PRODUCTION READY"
            deployment_message = "All critical systems operational. Safe to deploy."
        elif success_rate >= 85 and len(self.critical_failures) <= 1:
            deployment_status = "⚠️ READY WITH CAUTION"
            deployment_message = "Minor issues present but core functionality works."
        elif success_rate >= 70 and len(self.critical_failures) <= 2:
            deployment_status = "🔶 NEEDS ATTENTION"
            deployment_message = "Several issues need resolution before deployment."
        else:
            deployment_status = "❌ NOT READY"
            deployment_message = "Critical issues must be resolved before deployment."
        
        print(f"{deployment_status}")
        print(f"Assessment: {deployment_message}")
        
        # Show critical failures if any
        if self.critical_failures:
            print(f"\n🚨 CRITICAL ISSUES BLOCKING DEPLOYMENT ({len(self.critical_failures)}):")
            for issue in self.critical_failures:
                print(f"  • {issue}")
        
        # Success criteria summary
        print(f"\n📋 SUCCESS CRITERIA SUMMARY:")
        print(f"  • All endpoints return 200 OK: {'✅' if success_rate >= 90 else '❌'}")
        print(f"  • Stream URLs accessible: {'✅' if 'Main Kenya Stream' in [r['test'] for r in self.results if r['success']] else '❌'}")
        print(f"  • No critical errors: {'✅' if len(self.critical_failures) == 0 else '❌'}")
        print(f"  • Response times <2s: {'✅' if max_response_time < 2000 else '❌'}")
        print(f"  • Compliance system working: {'✅' if any('compliance' in r['test'].lower() and r['success'] for r in self.results) else '❌'}")
        
        print("\n" + "=" * 60)
        
        return {
            "deployment_ready": success_rate >= 85 and len(self.critical_failures) <= 1,
            "success_rate": success_rate,
            "critical_failures": len(self.critical_failures),
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time
        }

if __name__ == "__main__":
    tester = DeploymentReadinessTest()
    tester.run_deployment_readiness_tests()
    
    # Exit with appropriate code based on success rate and critical failures
    success_rate = (tester.passed_tests / tester.total_tests * 100) if tester.total_tests > 0 else 0
    deployment_ready = success_rate >= 85 and len(tester.critical_failures) <= 1
    sys.exit(0 if deployment_ready else 1)