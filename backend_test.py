#!/usr/bin/env python3
"""
AI-Powered Anomaly Detection System Testing - Phase 4
Comprehensive backend testing for anomaly detection capabilities, performance baselines, and monitoring
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    endpoint: str
    response_time: float
    status_code: int
    timestamp: datetime
    payload_size: int
    error_message: Optional[str] = None

@dataclass
class AnomalyDetectionResult:
    metric_type: str
    baseline_value: float
    current_value: float
    deviation_score: float
    is_anomaly: bool
    severity: str
    recommendation: str

class AIAnomalyDetectionTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.performance_metrics: List[PerformanceMetric] = []
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.anomalies_detected: List[AnomalyDetectionResult] = []
    
    def log_test_result(self, test_name: str, passed: bool, details: Dict[str, Any], response_time: float = 0):
        """Log individual test results"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
            if details.get("critical", False):
                self.results["critical_issues"].append(f"{test_name}: {details.get('error', 'Unknown error')}")
        
        self.results["test_details"].append({
            "test_name": test_name,
            "status": status,
            "response_time_ms": round(response_time * 1000, 2),
            "details": details
        })
        
        print(f"{status} {test_name} ({response_time*1000:.0f}ms)")
        if not passed and details.get("error"):
            print(f"    Error: {details['error']}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request and measure response time"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            return response, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return None, response_time, str(e)
    
    def test_core_radio_apis(self):
        """Test Core Radio APIs"""
        print("\n🎵 TESTING CORE RADIO APIs...")
        
        # 1. Test API Root
        response, response_time = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            passed = "Kagema FM" in data.get("message", "") and "version" in data
            self.log_test_result(
                "GET /api/ - API Root",
                passed,
                {"status_code": response.status_code, "data": data, "critical": not passed},
                response_time
            )
        else:
            self.log_test_result(
                "GET /api/ - API Root",
                False,
                {"error": "Failed to connect or invalid response", "critical": True},
                response_time
            )
        
        # 2. Test Basic Station Info
        response, response_time = self.make_request("GET", "/station-info")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["name", "description", "streamUrl", "currentShow"]
            has_required = all(field in data for field in required_fields)
            stream_url_valid = data.get("streamUrl", "").startswith("http")
            
            passed = has_required and stream_url_valid and data.get("name") == "Kagema FM"
            self.log_test_result(
                "GET /api/station-info - Basic Station Info",
                passed,
                {
                    "status_code": response.status_code,
                    "has_required_fields": has_required,
                    "stream_url_valid": stream_url_valid,
                    "station_name": data.get("name"),
                    "stream_url": data.get("streamUrl"),
                    "critical": not passed
                },
                response_time
            )
        else:
            self.log_test_result(
                "GET /api/station-info - Basic Station Info",
                False,
                {"error": "Failed to get station info", "critical": True},
                response_time
            )
        
        # 3. Test Multilingual Station Info for each location
        for location_name, coords in self.test_coordinates.items():
            response, response_time = self.make_request(
                "POST", 
                "/station-info/multilingual",
                coords
            )
            
            if response and response.status_code == 200:
                data = response.json()
                required_fields = ["name", "description", "streamUrl", "detected_language", "location"]
                has_required = all(field in data for field in required_fields)
                has_compliance = "content_disclaimers" in data and "compliance_info" in data
                
                passed = has_required and has_compliance and data.get("name") == "Kagema FM"
                self.log_test_result(
                    f"POST /api/station-info/multilingual - {location_name.title()} Location",
                    passed,
                    {
                        "status_code": response.status_code,
                        "detected_language": data.get("detected_language"),
                        "location": data.get("location"),
                        "stream_url": data.get("streamUrl"),
                        "has_compliance": has_compliance,
                        "critical": not passed
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/station-info/multilingual - {location_name.title()} Location",
                    False,
                    {"error": f"Failed to get multilingual station info for {location_name}", "critical": True},
                    response_time
                )
    
    def test_content_personalization_apis(self):
        """Test Content & Personalization APIs"""
        print("\n🌍 TESTING CONTENT & PERSONALIZATION APIs...")
        
        # 1. Test Language Detection for each location
        for location_name, coords in self.test_coordinates.items():
            response, response_time = self.make_request(
                "POST",
                "/language/detect",
                coords
            )
            
            if response and response.status_code == 200:
                data = response.json()
                required_fields = ["detected_language", "county", "region", "confidence"]
                has_required = all(field in data for field in required_fields)
                has_radio_streams = "radio_streams" in data or "regional_stations" in data
                
                passed = has_required and has_radio_streams and data.get("confidence", 0) > 0
                self.log_test_result(
                    f"POST /api/language/detect - {location_name.title()} Location",
                    passed,
                    {
                        "status_code": response.status_code,
                        "detected_language": data.get("detected_language"),
                        "county": data.get("county"),
                        "confidence": data.get("confidence"),
                        "has_radio_streams": has_radio_streams,
                        "critical": not passed
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/language/detect - {location_name.title()} Location",
                    False,
                    {"error": f"Failed language detection for {location_name}", "critical": True},
                    response_time
                )
        
        # 2. Test Supported Languages
        response, response_time = self.make_request("GET", "/languages")
        if response and response.status_code == 200:
            data = response.json()
            has_languages = "languages" in data and len(data["languages"]) > 0
            has_kenyan_languages = any(
                lang.get("code") in ["en", "sw", "ki", "luo"] 
                for lang in data.get("languages", [])
            )
            
            passed = has_languages and has_kenyan_languages and data.get("total_count", 0) >= 7
            self.log_test_result(
                "GET /api/languages - Supported Languages",
                passed,
                {
                    "status_code": response.status_code,
                    "total_languages": data.get("total_count", 0),
                    "has_kenyan_languages": has_kenyan_languages,
                    "supported_countries": data.get("supported_countries", []),
                    "critical": not passed
                },
                response_time
            )
        else:
            self.log_test_result(
                "GET /api/languages - Supported Languages",
                False,
                {"error": "Failed to get supported languages", "critical": True},
                response_time
            )
        
        # 3. Test Personalized Content for each location
        for location_name, coords in self.test_coordinates.items():
            user_preferences = {
                "user_id": "test-user-personalized",
                "theme": "auto",
                "language": "en",
                "region": location_name.upper(),
                "notifications": {
                    "enabled": True,
                    "show_reminders": True,
                    "news_updates": True,
                    "music_discovery": True,
                    "app_updates": True,
                    "quiet_hours_enabled": False,
                    "quiet_start_time": "22:00",
                    "quiet_end_time": "08:00",
                    "sound_enabled": True,
                    "vibration_enabled": True
                },
                "audio": {
                    "quality": "medium",
                    "volume": 0.8,
                    "auto_play": False,
                    "background_play": True,
                    "equalizer_preset": "default"
                },
                "offline_mode": False,
                "data_saver": False,
                "analytics_enabled": True
            }
            
            response, response_time = self.make_request(
                "POST",
                "/personalized-content/multilingual",
                {
                    "location": coords,
                    "preferences": user_preferences
                }
            )
            
            if response and response.status_code == 200:
                data = response.json()
                has_content = all(key in data for key in ["news", "music", "language_detection"])
                has_compliance = "content_disclaimers" in data and "compliance_info" in data
                has_radio_streams = "radio_streams" in data  # CRITICAL for frontend
                
                passed = has_content and has_compliance and has_radio_streams
                self.log_test_result(
                    f"POST /api/personalized-content/multilingual - {location_name.title()}",
                    passed,
                    {
                        "status_code": response.status_code,
                        "has_content": has_content,
                        "has_compliance": has_compliance,
                        "has_radio_streams": has_radio_streams,
                        "detected_language": data.get("language_detection", {}).get("detected_language"),
                        "news_count": len(data.get("news", {}).get("articles", [])),
                        "music_count": len(data.get("music", {}).get("tracks", [])),
                        "critical": not has_radio_streams  # Critical if radio streams missing
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/personalized-content/multilingual - {location_name.title()}",
                    False,
                    {"error": f"Failed to get personalized content for {location_name}", "critical": True},
                    response_time
                )
    
    def test_content_compliance_apis(self):
        """Test Content Compliance APIs"""
        print("\n⚖️ TESTING CONTENT COMPLIANCE APIs...")
        
        # 1. Test Content Disclaimers for different countries
        countries = [
            {"code": "KE", "language": "en", "name": "Kenya English"},
            {"code": "KE", "language": "sw", "name": "Kenya Swahili"},
            {"code": "BR", "language": "pt-br", "name": "Brazil Portuguese"},
            {"code": "GLOBAL", "language": "en", "name": "Global English"}
        ]
        
        for country in countries:
            response, response_time = self.make_request(
                "POST",
                "/compliance/disclaimers",
                {
                    "country_code": country["code"],
                    "language_code": country["language"],
                    "content_types": ["radio_streams", "music", "news"],
                    "user_age": 25
                }
            )
            
            if response and response.status_code == 200:
                data = response.json()
                has_disclaimers = "content_disclaimers" in data and len(data["content_disclaimers"]) > 0
                has_compliance = "regional_compliance" in data
                has_platform_responsibility = any(
                    "Platform" in disclaimer.get("title", "") or "Responsibility" in disclaimer.get("title", "") or
                    "Jukwaa" in disclaimer.get("title", "") or "Plataforma" in disclaimer.get("title", "")
                    for disclaimer in data.get("content_disclaimers", [])
                )
                
                passed = has_disclaimers and has_compliance and has_platform_responsibility
                self.log_test_result(
                    f"POST /api/compliance/disclaimers - {country['name']}",
                    passed,
                    {
                        "status_code": response.status_code,
                        "disclaimer_count": len(data.get("content_disclaimers", [])),
                        "has_platform_responsibility": has_platform_responsibility,
                        "regional_compliance": data.get("regional_compliance", {}),
                        "critical": not passed
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/compliance/disclaimers - {country['name']}",
                    False,
                    {"error": f"Failed to get disclaimers for {country['name']}", "critical": True},
                    response_time
                )
        
        # 2. Test User Acknowledgment
        acknowledgment_data = {
            "disclaimer_ids": ["general_responsibility", "platform_responsibility"],
            "user_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_age": 25,
            "country_code": "KE"
        }
        
        response, response_time = self.make_request(
            "POST",
            "/compliance/acknowledge",
            acknowledgment_data
        )
        
        if response and response.status_code == 200:
            data = response.json()
            passed = data.get("acknowledgment_recorded") == True and "valid_until" in data
            self.log_test_result(
                "POST /api/compliance/acknowledge - User Acknowledgment",
                passed,
                {
                    "status_code": response.status_code,
                    "acknowledgment_recorded": data.get("acknowledgment_recorded"),
                    "valid_until": data.get("valid_until"),
                    "critical": not passed
                },
                response_time
            )
        else:
            self.log_test_result(
                "POST /api/compliance/acknowledge - User Acknowledgment",
                False,
                {"error": "Failed to record user acknowledgment", "critical": True},
                response_time
            )
        
        # 3. Test Content Compliance Check
        compliance_scenarios = [
            {"country": "KE", "rating": "general", "age": 25, "hour": 14, "name": "Kenya General Daytime"},
            {"country": "KE", "rating": "mature", "age": 25, "hour": 22, "name": "Kenya Mature Evening"},
            {"country": "BR", "rating": "explicit", "age": 25, "hour": 18, "name": "Brazil Explicit Evening"},
            {"country": "BR", "rating": "explicit", "age": 25, "hour": 21, "name": "Brazil Explicit Night"},
            {"country": "GLOBAL", "rating": "adult", "age": 17, "hour": 20, "name": "Global Adult Minor"}
        ]
        
        for scenario in compliance_scenarios:
            response, response_time = self.make_request(
                "POST",
                "/compliance/check-content",
                params={
                    "country_code": scenario["country"],
                    "content_rating": scenario["rating"],
                    "user_age": scenario["age"],
                    "current_hour": scenario["hour"]
                }
            )
            
            if response and response.status_code == 200:
                data = response.json()
                has_compliance_result = "compliant" in data and ("warnings" in data or "blocking_reasons" in data)
                
                passed = has_compliance_result
                self.log_test_result(
                    f"POST /api/compliance/check-content - {scenario['name']}",
                    passed,
                    {
                        "status_code": response.status_code,
                        "compliant": data.get("compliant"),
                        "reason": data.get("reason"),
                        "age_appropriate": data.get("age_appropriate"),
                        "critical": not passed
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/compliance/check-content - {scenario['name']}",
                    False,
                    {"error": f"Failed compliance check for {scenario['name']}", "critical": True},
                    response_time
                )
    
    def test_platform_integration_apis(self):
        """Test Platform Integration APIs"""
        print("\n🔌 TESTING PLATFORM INTEGRATION APIs...")
        
        integration_types = [
            {"type": "general", "name": "General Platform"},
            {"type": "google_maps", "name": "Google Maps"},
            {"type": "spotify", "name": "Spotify"},
            {"type": "voice_control", "name": "Voice Control"}
        ]
        
        for integration in integration_types:
            response, response_time = self.make_request(
                "POST",
                "/integrations/initialize",
                {
                    "type": integration["type"],
                    "config": {"client_id": "test_client", "environment": "web_preview"}
                }
            )
            
            if response and response.status_code == 200:
                data = response.json()
                has_status = "status" in data and "integration" in data
                is_initialized = data.get("status") == "initialized"
                
                passed = has_status and is_initialized
                self.log_test_result(
                    f"POST /api/integrations/initialize - {integration['name']}",
                    passed,
                    {
                        "status_code": response.status_code,
                        "integration_type": data.get("integration"),
                        "status": data.get("status"),
                        "config": data.get("config", {}),
                        "critical": False  # Integrations are not critical for core functionality
                    },
                    response_time
                )
            else:
                self.log_test_result(
                    f"POST /api/integrations/initialize - {integration['name']}",
                    False,
                    {"error": f"Failed to initialize {integration['name']}", "critical": False},
                    response_time
                )
    
    def test_satellite_offline_apis(self):
        """Test Satellite & Offline APIs"""
        print("\n🛰️ TESTING SATELLITE & OFFLINE APIs...")
        
        # 1. Test Satellite Status
        response, response_time = self.make_request("GET", "/satellite/status")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["connection_type", "signal_strength", "download_speed", "upload_speed"]
            has_required = all(field in data for field in required_fields)
            
            passed = has_required and data.get("download_speed", 0) >= 0  # Allow 0 speed for no connection
            self.log_test_result(
                "GET /api/satellite/status - Satellite Status",
                passed,
                {
                    "status_code": response.status_code,
                    "connection_type": data.get("connection_type"),
                    "signal_strength": data.get("signal_strength"),
                    "download_speed": data.get("download_speed"),
                    "provider": data.get("provider"),
                    "critical": False  # Satellite is optional feature
                },
                response_time
            )
        else:
            self.log_test_result(
                "GET /api/satellite/status - Satellite Status",
                False,
                {"error": "Failed to get satellite status", "critical": False},
                response_time
            )
        
        # 2. Test Satellite Connection
        response, response_time = self.make_request(
            "POST",
            "/satellite/connect",
            {
                "provider": "auto",
                "client_id": "kagema_fm_test",
                "location": "auto"
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            has_connection_info = "connected" in data and "message" in data
            
            passed = has_connection_info
            self.log_test_result(
                "POST /api/satellite/connect - Satellite Connection",
                passed,
                {
                    "status_code": response.status_code,
                    "connected": data.get("connected"),
                    "provider": data.get("provider"),
                    "message": data.get("message"),
                    "critical": False  # Satellite is optional feature
                },
                response_time
            )
        else:
            self.log_test_result(
                "POST /api/satellite/connect - Satellite Connection",
                False,
                {"error": "Failed to connect to satellite", "critical": False},
                response_time
            )
        
        # 3. Test Offline Cache
        cache_request = {
            "content_types": ["radio_streams", "news", "weather", "music"],
            "location": self.test_coordinates["kenya"],
            "cache_duration_hours": 24
        }
        
        response, response_time = self.make_request(
            "POST",
            "/offline/cache",
            cache_request
        )
        
        if response and response.status_code == 200:
            data = response.json()
            has_cached_items = "cached_items" in data and len(data["cached_items"]) > 0
            has_compliance_warning = "compliance_warning" in data
            
            passed = has_cached_items and has_compliance_warning
            self.log_test_result(
                "POST /api/offline/cache - Offline Content Caching",
                passed,
                {
                    "status_code": response.status_code,
                    "cached_items": list(data.get("cached_items", {}).keys()),
                    "offline_mode_ready": data.get("offline_mode_ready"),
                    "has_compliance_warning": has_compliance_warning,
                    "critical": False  # Offline is optional feature
                },
                response_time
            )
        else:
            self.log_test_result(
                "POST /api/offline/cache - Offline Content Caching",
                False,
                {"error": "Failed to cache content for offline use", "critical": False},
                response_time
            )
    
    def test_stream_accessibility(self):
        """Test actual radio stream accessibility - AUDIO STREAM VERIFICATION FOCUS"""
        print("\n📻 TESTING RADIO STREAM ACCESSIBILITY - COMPREHENSIVE AUDIO STREAM VERIFICATION...")
        
        # Specific streams from review request
        test_streams = [
            {
                "name": "Brazil Bahia (102.3 FM)",
                "url": "http://ice2.somafm.com/bagel-256-mp3",
                "region": "Brazil",
                "critical": True
            },
            {
                "name": "Kenya Nairobi (101.5 FM)", 
                "url": "http://ice1.somafm.com/groovesalad-256-mp3",
                "region": "Kenya",
                "critical": True
            },
            {
                "name": "Satellite Stream",
                "url": "http://ice1.somafm.com/spacestation-256-mp3",
                "region": "Satellite",
                "critical": True
            },
            {
                "name": "International Stream",
                "url": "http://ice3.somafm.com/beatblender-256-mp3", 
                "region": "International",
                "critical": True
            },
            {
                "name": "Secret Agent Stream",
                "url": "http://ice1.somafm.com/secretagent-256-mp3",
                "region": "Fallback",
                "critical": False
            },
            {
                "name": "DEF CON Stream",
                "url": "http://ice1.somafm.com/defcon-256-mp3",
                "region": "Fallback",
                "critical": False
            },
            {
                "name": "Lush Stream",
                "url": "http://ice1.somafm.com/lush-256-mp3",
                "region": "Fallback",
                "critical": False
            }
        ]
        
        accessible_streams = 0
        total_critical_streams = sum(1 for stream in test_streams if stream["critical"])
        
        for stream in test_streams:
            try:
                start_time = time.time()
                
                # Test with HEAD request first
                stream_response = requests.head(stream["url"], timeout=10, allow_redirects=True)
                response_time = time.time() - start_time
                
                is_accessible = stream_response.status_code == 200
                content_type = stream_response.headers.get("content-type", "")
                is_audio = "audio" in content_type.lower() or "mpeg" in content_type.lower()
                
                # Check for ICY streaming headers
                icy_headers = {}
                for header, value in stream_response.headers.items():
                    if header.lower().startswith('icy-'):
                        icy_headers[header] = value
                
                has_icy_headers = len(icy_headers) > 0
                
                # If HEAD fails, try GET with limited data
                if not is_accessible:
                    try:
                        get_response = requests.get(stream["url"], timeout=10, stream=True)
                        is_accessible = get_response.status_code == 200
                        content_type = get_response.headers.get("content-type", "")
                        is_audio = "audio" in content_type.lower() or "mpeg" in content_type.lower()
                        get_response.close()
                    except:
                        pass
                
                if is_accessible:
                    accessible_streams += 1
                
                passed = is_accessible and (is_audio or has_icy_headers)
                
                self.log_test_result(
                    f"Stream Accessibility - {stream['name']} ({stream['region']})",
                    passed,
                    {
                        "stream_url": stream["url"],
                        "status_code": stream_response.status_code,
                        "content_type": content_type,
                        "is_audio": is_audio,
                        "has_icy_headers": has_icy_headers,
                        "icy_header_count": len(icy_headers),
                        "region": stream["region"],
                        "critical": stream["critical"] and not passed
                    },
                    response_time
                )
                
            except Exception as e:
                self.log_test_result(
                    f"Stream Accessibility - {stream['name']} ({stream['region']})",
                    False,
                    {
                        "error": f"Stream accessibility test failed: {str(e)}", 
                        "stream_url": stream["url"],
                        "critical": stream["critical"]
                    },
                    0
                )
        
        # Summary of stream accessibility
        accessibility_rate = (accessible_streams / len(test_streams)) * 100
        print(f"\n📊 STREAM ACCESSIBILITY SUMMARY:")
        print(f"   • Total Streams Tested: {len(test_streams)}")
        print(f"   • Accessible Streams: {accessible_streams}")
        print(f"   • Accessibility Rate: {accessibility_rate:.1f}%")
        print(f"   • Critical Streams: {total_critical_streams}")
        
        # Log overall stream accessibility result
        overall_passed = accessibility_rate >= 70  # At least 70% should be accessible
        self.log_test_result(
            "Overall Stream Accessibility Rate",
            overall_passed,
            {
                "total_streams": len(test_streams),
                "accessible_streams": accessible_streams,
                "accessibility_rate": accessibility_rate,
                "critical": not overall_passed
            },
            0
        )
    
    def calculate_overall_health(self):
        """Calculate overall system health"""
        if self.results["total_tests"] == 0:
            self.results["overall_health"] = "NO_TESTS"
            return
        
        success_rate = (self.results["passed_tests"] / self.results["total_tests"]) * 100
        critical_issues_count = len(self.results["critical_issues"])
        
        if success_rate >= 95 and critical_issues_count == 0:
            self.results["overall_health"] = "EXCELLENT"
        elif success_rate >= 85 and critical_issues_count <= 1:
            self.results["overall_health"] = "GOOD"
        elif success_rate >= 70 and critical_issues_count <= 3:
            self.results["overall_health"] = "FAIR"
        elif success_rate >= 50:
            self.results["overall_health"] = "POOR"
        else:
            self.results["overall_health"] = "CRITICAL"
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        self.calculate_overall_health()
        
        print("\n" + "="*80)
        print("🎵 KAGEMA FM BACKEND API COMPREHENSIVE HEALTH REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL HEALTH: {self.results['overall_health']}")
        print(f"✅ Tests Passed: {self.results['passed_tests']}/{self.results['total_tests']}")
        print(f"❌ Tests Failed: {self.results['failed_tests']}/{self.results['total_tests']}")
        print(f"📈 Success Rate: {(self.results['passed_tests']/self.results['total_tests']*100):.1f}%")
        
        if self.results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   • {issue}")
        
        # Performance metrics
        response_times = [test["response_time_ms"] for test in self.results["test_details"]]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   • Average Response Time: {avg_response_time:.0f}ms")
            print(f"   • Maximum Response Time: {max_response_time:.0f}ms")
            print(f"   • Performance Target (<2000ms): {'✅ MET' if max_response_time < 2000 else '❌ EXCEEDED'}")
        
        # Detailed test results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test in self.results["test_details"]:
            print(f"   {test['status']} {test['test_name']} ({test['response_time_ms']}ms)")
        
        print("\n" + "="*80)
        
        return self.results
    
    def test_enhanced_user_features(self):
        """Test Enhanced User Features - NEW FEATURES FROM REVIEW REQUEST"""
        print("\n👤 TESTING ENHANCED USER FEATURES (NEW)...")
        
        test_user_id = "test-user-123"  # As specified in review request
        
        # 1. Test User Preferences Management
        print("\n🔧 Testing User Preferences Management...")
        
        # Get initial preferences (might not exist)
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/preferences")
        if response and response.status_code in [200, 404]:
            # 404 is acceptable for new user
            passed = True
            details = {"status_code": response.status_code, "message": "User preferences endpoint accessible"}
        else:
            passed = False
            details = {"error": "Failed to access user preferences", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/preferences", passed, details, response_time)
        
        # Update user preferences with correct model structure
        preferences_data = {
            "user_id": test_user_id,
            "theme": "dark",
            "language": "en",
            "region": "KE",
            "notifications": {
                "enabled": True,
                "show_reminders": True,
                "news_updates": True,
                "music_discovery": True,
                "app_updates": True,
                "quiet_hours_enabled": False,
                "quiet_start_time": "22:00",
                "quiet_end_time": "08:00",
                "sound_enabled": True,
                "vibration_enabled": True
            },
            "audio": {
                "quality": "high",
                "volume": 0.8,
                "auto_play": False,
                "background_play": True,
                "equalizer_preset": "default"
            },
            "offline_mode": False,
            "data_saver": False,
            "analytics_enabled": True
        }
        
        response, response_time = self.make_request("PUT", f"/user/{test_user_id}/preferences", preferences_data)
        if response and response.status_code == 200:
            data = response.json()
            passed = "message" in data
            details = {"status_code": response.status_code, "response": data}
        else:
            passed = False
            details = {"error": "Failed to update user preferences", "critical": True}
        
        self.log_test_result("PUT /api/user/{user_id}/preferences", passed, details, response_time)
        
        # 2. Test Favorites System
        print("\n⭐ Testing Favorites System...")
        
        # Add different types of favorites - CORRECTED FORMAT
        favorites_to_test = [
            {
                "favorite_type": "radio_station",
                "item_id": "kagema_fm_nairobi",
                "title": "Kagema FM Nairobi",
                "metadata": {
                    "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
                    "frequency": "101.5 FM",
                    "location": "Nairobi, Kenya"
                }
            },
            {
                "favorite_type": "news_article", 
                "item_id": "kenya_news_001",
                "title": "Latest Kenya News Update",
                "metadata": {
                    "source": "Kenya Broadcasting Corporation",
                    "category": "local_news",
                    "published_at": datetime.now().isoformat()
                }
            },
            {
                "favorite_type": "music_track",
                "item_id": "sauti_sol_midnight_train",
                "title": "Midnight Train - Sauti Sol",
                "metadata": {
                    "artist": "Sauti Sol",
                    "album": "Midnight Train",
                    "genre": "Afro-pop",
                    "duration": 240
                }
            }
        ]
        
        favorite_ids = []
        
        # Add favorites
        for favorite in favorites_to_test:
            response, response_time = self.make_request("POST", f"/user/{test_user_id}/favorites", favorite)
            if response and response.status_code == 200:
                data = response.json()
                favorite_id = data.get("favorite_id")
                if favorite_id:
                    favorite_ids.append(favorite_id)
                    passed = True
                    details = {"status_code": response.status_code, "favorite_id": favorite_id, "type": favorite["favorite_type"]}
                else:
                    passed = False
                    details = {"error": "No favorite_id returned", "critical": True}
            else:
                passed = False
                details = {"error": f"Failed to add {favorite['favorite_type']} favorite", "critical": True}
            
            self.log_test_result(f"POST /api/user/{{user_id}}/favorites - {favorite['favorite_type']}", passed, details, response_time)
        
        # Get all favorites
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/favorites")
        if response and response.status_code == 200:
            data = response.json()
            favorites_list = data.get("favorites", [])
            passed = len(favorites_list) > 0
            details = {"status_code": response.status_code, "favorites_count": len(favorites_list)}
        else:
            passed = False
            details = {"error": "Failed to get user favorites", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/favorites", passed, details, response_time)
        
        # Test filtering by type
        for item_type in ["radio_station", "news_article", "music_track"]:
            response, response_time = self.make_request("GET", f"/user/{test_user_id}/favorites", params={"favorite_type": item_type})
            if response and response.status_code == 200:
                data = response.json()
                type_favorites = data.get("favorites", [])
                passed = True  # Any result is acceptable
                details = {"status_code": response.status_code, "type_favorites_count": len(type_favorites)}
            else:
                passed = False
                details = {"error": f"Failed to get {item_type} favorites", "critical": False}
            
            self.log_test_result(f"GET /api/user/{{user_id}}/favorites?favorite_type={item_type}", passed, details, response_time)
        
        # Remove a favorite
        if favorite_ids:
            favorite_to_remove = favorite_ids[0]
            response, response_time = self.make_request("DELETE", f"/user/{test_user_id}/favorites/{favorite_to_remove}")
            if response and response.status_code == 200:
                passed = True
                details = {"status_code": response.status_code, "removed_favorite_id": favorite_to_remove}
            else:
                passed = False
                details = {"error": "Failed to remove favorite", "critical": True}
            
            self.log_test_result("DELETE /api/user/{user_id}/favorites/{favorite_id}", passed, details, response_time)
        
        # 3. Test Listening History & Analytics
        print("\n📊 Testing Listening History & Analytics...")
        
        # Start listening sessions
        sessions_to_start = [
            {
                "user_id": test_user_id,
                "station_name": "Kagema FM Nairobi", 
                "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
                "started_at": datetime.now().isoformat(),
                "quality": "high",
                "device_info": {
                    "type": "web",
                    "browser": "Chrome",
                    "os": "Linux"
                }
            },
            {
                "user_id": test_user_id,
                "station_name": "Radio Paradise",
                "stream_url": "https://stream.radioparadise.com/aac-320", 
                "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "quality": "medium",
                "device_info": {
                    "type": "mobile",
                    "browser": "Safari",
                    "os": "iOS"
                }
            }
        ]
        
        session_ids = []
        
        for session in sessions_to_start:
            response, response_time = self.make_request("POST", f"/user/{test_user_id}/listening-session", session)
            if response and response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                if session_id:
                    session_ids.append(session_id)
                    passed = True
                    details = {"status_code": response.status_code, "session_id": session_id, "station": session["station_name"]}
                else:
                    passed = False
                    details = {"error": "No session_id returned", "critical": True}
            else:
                passed = False
                details = {"error": "Failed to start listening session", "critical": True}
            
            self.log_test_result(f"POST /api/user/{{user_id}}/listening-session - {session['station_name']}", passed, details, response_time)
        
        # End a listening session
        if session_ids:
            session_to_end = session_ids[0]
            end_time = datetime.now()
            duration_seconds = 1800  # 30 minutes
            
            response, response_time = self.make_request(
                "PUT", 
                f"/user/{test_user_id}/listening-session/{session_to_end}",
                params={"ended_at": end_time.isoformat(), "duration_seconds": duration_seconds}
            )
            
            if response and response.status_code == 200:
                passed = True
                details = {"status_code": response.status_code, "ended_session_id": session_to_end}
            else:
                passed = False
                details = {"error": "Failed to end listening session", "critical": True}
            
            self.log_test_result("PUT /api/user/{user_id}/listening-session/{session_id}", passed, details, response_time)
        
        # Get listening history
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/listening-history", params={"limit": 50})
        if response and response.status_code == 200:
            data = response.json()
            history = data.get("history", [])
            passed = True  # Any result is acceptable
            details = {"status_code": response.status_code, "history_count": len(history)}
        else:
            passed = False
            details = {"error": "Failed to get listening history", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/listening-history", passed, details, response_time)
        
        # Get listening statistics
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/stats")
        if response and response.status_code == 200:
            data = response.json()
            stats = data.get("statistics", {})
            passed = True  # Any result is acceptable
            details = {"status_code": response.status_code, "stats_categories": len(stats)}
        else:
            passed = False
            details = {"error": "Failed to get listening statistics", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/stats", passed, details, response_time)
        
        # 4. Test Personalization & Recommendations
        print("\n🎯 Testing Personalization & Recommendations...")
        
        # Get personalized recommendations
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/recommendations")
        if response and response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", {})
            passed = True  # Any result is acceptable
            details = {"status_code": response.status_code, "recommendation_categories": len(recommendations)}
        else:
            passed = False
            details = {"error": "Failed to get personalized recommendations", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/recommendations", passed, details, response_time)
        
        # Get enhanced station info with personalization
        response, response_time = self.make_request("GET", f"/station-info/enhanced/{test_user_id}")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["name", "description", "streamUrl", "personalization"]
            has_required = all(field in data for field in required_fields)
            personalization = data.get("personalization", {})
            has_personalization = personalization.get("enabled", False)
            
            passed = has_required and has_personalization
            details = {
                "status_code": response.status_code,
                "has_required_fields": has_required,
                "personalization_enabled": has_personalization,
                "personalization_score": personalization.get("score", 0.0)
            }
        else:
            passed = False
            details = {"error": "Failed to get enhanced station info", "critical": True}
        
        self.log_test_result("GET /api/station-info/enhanced/{user_id}", passed, details, response_time)
        
        # 5. Test Data Management (GDPR Compliance)
        print("\n🔒 Testing Data Management (GDPR Compliance)...")
        
        # Export user data
        response, response_time = self.make_request("GET", f"/user/{test_user_id}/export")
        if response and response.status_code in [200, 404]:
            # 404 is acceptable if no data exists
            if response.status_code == 200:
                data = response.json()
                passed = True
                details = {"status_code": response.status_code, "exported_data_sections": len(data)}
            else:
                passed = True
                details = {"status_code": response.status_code, "message": "No user data found (acceptable)"}
        else:
            passed = False
            details = {"error": "Failed to export user data", "critical": True}
        
        self.log_test_result("GET /api/user/{user_id}/export", passed, details, response_time)
        
        # Delete user data (GDPR compliance)
        response, response_time = self.make_request("DELETE", f"/user/{test_user_id}/data")
        if response and response.status_code == 200:
            data = response.json()
            passed = "message" in data
            details = {"status_code": response.status_code, "deletion_message": data.get("message", "")}
        else:
            passed = False
            details = {"error": "Failed to delete user data", "critical": True}
        
        self.log_test_result("DELETE /api/user/{user_id}/data (GDPR)", passed, details, response_time)

    def run_comprehensive_health_check(self):
        """Run all health check tests"""
        print("🎵 STARTING ENHANCED KAGEMA FM BACKEND API COMPREHENSIVE HEALTH CHECK...")
        print(f"🌐 Testing API Base URL: {self.base_url}")
        print(f"⏰ Test Started: {datetime.now().isoformat()}")
        print("📋 Testing ALL Enhanced Features from Review Request")
        
        # Run all test suites
        self.test_core_radio_apis()
        self.test_content_personalization_apis()
        self.test_content_compliance_apis()
        self.test_platform_integration_apis()
        self.test_satellite_offline_apis()
        self.test_stream_accessibility()
        
        # NEW: Test enhanced user features from review request
        self.test_enhanced_user_features()
        
        # Generate final report
        return self.generate_health_report()

def main():
    """Main test execution"""
    tester = KagemaFMAPITester()
    results = tester.run_comprehensive_health_check()
    
    # Return exit code based on health
    if results["overall_health"] in ["EXCELLENT", "GOOD"]:
        exit(0)
    elif results["overall_health"] in ["FAIR"]:
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    main()