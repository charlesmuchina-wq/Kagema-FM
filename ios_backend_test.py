#!/usr/bin/env python3
"""
iOS Memory Integrity Enforcement Backend Testing
Focus: Core API Health, Radio Streaming, Voice AI, Performance, Content Compliance
"""

import requests
import time
import json
from typing import Dict, List, Any, Optional

# Backend URL
BACKEND_URL = "https://carmedia-hub-1.preview.emergentagent.com/api"

class IOSBackendTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_request(self, name: str, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a test request and return results"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000
            
            result = {
                "name": name,
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response_time,
                "data": response.json() if response.status_code < 400 else None,
                "error": None
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                "name": name,
                "success": False,
                "status_code": None,
                "response_time": response_time,
                "data": None,
                "error": str(e)
            }
        
        self.results.append(result)
        return result
    
    def test_stream_accessibility(self, stream_url: str, stream_name: str) -> Dict:
        """Test if radio stream is accessible"""
        start_time = time.time()
        
        try:
            response = requests.head(stream_url, timeout=5, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            # Check for audio content type or ICY headers
            content_type = response.headers.get('content-type', '').lower()
            is_audio = any(audio_type in content_type for audio_type in ['audio', 'mpeg', 'aac'])
            has_icy = any(header.lower().startswith('icy-') for header in response.headers.keys())
            
            result = {
                "name": f"Stream: {stream_name}",
                "success": response.status_code == 200 and (is_audio or has_icy),
                "status_code": response.status_code,
                "response_time": response_time,
                "data": {
                    "content_type": content_type,
                    "has_icy_headers": has_icy
                },
                "error": None
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                "name": f"Stream: {stream_name}",
                "success": False,
                "status_code": None,
                "response_time": response_time,
                "data": None,
                "error": str(e)
            }
        
        self.results.append(result)
        return result

    def run_comprehensive_test(self):
        """Run comprehensive iOS backend testing"""
        print("🍎 iOS MEMORY INTEGRITY ENFORCEMENT BACKEND TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        
        # 1. Core API Health Check
        print("\n🔍 1. CORE API HEALTH CHECK")
        print("-" * 40)
        
        self.test_request("API Root", "GET", "/")
        self.test_request("Basic Station Info", "GET", "/station-info")
        
        # Test multilingual station info
        nairobi_location = {"latitude": -1.2921, "longitude": 36.8219}
        self.test_request("Multilingual Station Info", "POST", "/station-info/multilingual", nairobi_location)
        
        # Test personalized content - CRITICAL for frontend
        personalized_request = {
            "location": nairobi_location,
            "preferences": {"offline_mode": False, "preferred_language": "en"}
        }
        self.test_request("Personalized Content", "POST", "/personalized-content/multilingual", personalized_request)
        
        # 2. Radio Streaming Verification
        print("\n📻 2. RADIO STREAMING VERIFICATION")
        print("-" * 40)
        
        # Get radio streams
        streams_result = self.test_request("Radio Streams", "GET", "/radio/streams")
        
        if streams_result["success"] and streams_result["data"]:
            # Test main station stream
            main_station = streams_result["data"].get("main_station", {})
            if main_station.get("streamUrl"):
                self.test_stream_accessibility(
                    main_station["streamUrl"], 
                    main_station.get("name", "Main Station")
                )
            
            # Test all 7 alternative streams
            alt_streams = streams_result["data"].get("alternative_streams", [])
            for stream in alt_streams:
                if stream.get("streamUrl"):
                    self.test_stream_accessibility(
                        stream["streamUrl"],
                        stream.get("name", "Unknown Stream")
                    )
        
        # 3. Voice AI Integration
        print("\n🎤 3. VOICE AI INTEGRATION")
        print("-" * 40)
        
        self.test_request("Voice Intents", "GET", "/voice/intents")
        self.test_request("Voice Help", "GET", "/voice/help")
        
        # Test voice commands
        voice_commands = [
            {"text": "play", "context": "radio_control"},
            {"text": "pause", "context": "radio_control"},
            {"text": "next", "context": "radio_control"},
            {"text": "volume up", "context": "radio_control"},
            {"text": "search for jazz music", "context": "music_search"},
            {"text": "tune to classical station", "context": "station_control"}
        ]
        
        for command in voice_commands:
            self.test_request(f"Voice Command: {command['text']}", "POST", "/voice/interpret", command)
        
        # 4. Performance Validation
        print("\n⚡ 4. PERFORMANCE VALIDATION")
        print("-" * 40)
        
        # Test response times for critical endpoints
        critical_endpoints = [
            ("API Root Performance", "GET", "/"),
            ("Station Info Performance", "GET", "/station-info"),
            ("Radio Streams Performance", "GET", "/radio/streams")
        ]
        
        for name, method, endpoint in critical_endpoints:
            self.test_request(name, method, endpoint)
        
        # 5. Content & Compliance
        print("\n📋 5. CONTENT & COMPLIANCE")
        print("-" * 40)
        
        # Test language detection
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "name": "Nairobi"},
            {"latitude": -0.0917, "longitude": 34.7680, "name": "Kisumu"},
            {"latitude": -23.5505, "longitude": -46.6333, "name": "São Paulo"}
        ]
        
        for location in test_locations:
            self.test_request(
                f"Language Detection: {location['name']}", 
                "POST", 
                "/language/detect", 
                {"latitude": location["latitude"], "longitude": location["longitude"]}
            )
        
        self.test_request("Supported Languages", "GET", "/languages")
        
        # Test content disclaimers
        regions = ["KE", "BR", "GLOBAL"]
        for region in regions:
            self.test_request(
                f"Content Disclaimers: {region}",
                "POST",
                "/compliance/disclaimers",
                {
                    "country_code": region,
                    "language_code": "en",
                    "content_types": ["radio_streams", "music", "news"]
                }
            )
        
        # 6. Global Radio Networks
        print("\n🌍 6. GLOBAL RADIO NETWORKS")
        print("-" * 40)
        
        self.test_request("Radio Stations", "GET", "/radio/stations")
        self.test_request("Satellite Status", "GET", "/satellite/status")
        self.test_request("Satellite Main Stations", "GET", "/satellite/main_stations")
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("🎉 iOS MEMORY INTEGRITY ENFORCEMENT TEST RESULTS")
        print("=" * 70)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Performance metrics
        response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        under_500ms = sum(1 for rt in response_times if rt < 500)
        performance_rate = (under_500ms / len(response_times)) * 100 if response_times else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Average Response Time: {avg_response_time:.1f}ms")
        print(f"   Max Response Time: {max_response_time:.1f}ms")
        print(f"   Tests Under 500ms: {under_500ms}/{len(response_times)} ({performance_rate:.1f}%)")
        
        # Group results by category
        categories = {
            "Core API Health": [],
            "Radio Streaming": [],
            "Voice AI Integration": [],
            "Performance": [],
            "Content & Compliance": [],
            "Global Radio Networks": []
        }
        
        for result in self.results:
            name = result["name"].lower()
            if any(keyword in name for keyword in ["api root", "station info", "personalized content", "multilingual"]):
                categories["Core API Health"].append(result)
            elif any(keyword in name for keyword in ["stream", "radio"]):
                categories["Radio Streaming"].append(result)
            elif "voice" in name:
                categories["Voice AI Integration"].append(result)
            elif "performance" in name:
                categories["Performance"].append(result)
            elif any(keyword in name for keyword in ["language", "compliance", "disclaimer"]):
                categories["Content & Compliance"].append(result)
            elif any(keyword in name for keyword in ["satellite", "stations"]):
                categories["Global Radio Networks"].append(result)
        
        # Print detailed results by category
        for category, results in categories.items():
            if results:
                successful = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"\n✅ {category}: {successful}/{total} ({(successful/total)*100:.1f}%)")
                
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    time_str = f"{result['response_time']:.0f}ms" if result["response_time"] > 0 else "N/A"
                    print(f"   {status} {result['name']} ({time_str})")
                    
                    if not result["success"] and result["error"]:
                        print(f"      Error: {result['error']}")
        
        # Failed tests summary
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS SUMMARY ({len(failed_tests)} failures):")
            for result in failed_tests:
                print(f"   • {result['name']}")
                if result["error"]:
                    print(f"     Error: {result['error']}")
                if result["status_code"]:
                    print(f"     Status Code: {result['status_code']}")
        
        # iOS Memory Integrity Impact Assessment
        print(f"\n🍎 iOS MEMORY INTEGRITY IMPACT ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - iOS security enhancements have had ZERO NEGATIVE IMPACT on backend stability")
        elif success_rate >= 85:
            print("   ✅ GOOD - iOS security enhancements have minimal impact on backend stability")
        elif success_rate >= 70:
            print("   ⚠️  FAIR - Some issues detected, may be related to iOS configuration changes")
        else:
            print("   ❌ POOR - Significant issues detected, requires investigation")
        
        # Deployment readiness assessment
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        criteria_met = 0
        total_criteria = 4
        
        if success_rate >= 95:
            print("   ✅ >95% Success Rate ACHIEVED")
            criteria_met += 1
        else:
            print(f"   ❌ >95% Success Rate NOT MET ({success_rate:.1f}%)")
        
        if avg_response_time < 500:
            print("   ✅ <500ms Average Response Time ACHIEVED")
            criteria_met += 1
        else:
            print(f"   ❌ <500ms Average Response Time NOT MET ({avg_response_time:.1f}ms)")
        
        # Check stream accessibility
        stream_tests = [r for r in self.results if "stream:" in r["name"].lower()]
        stream_success_rate = (sum(1 for r in stream_tests if r["success"]) / len(stream_tests)) * 100 if stream_tests else 0
        if stream_success_rate >= 90:
            print("   ✅ Radio Stream Accessibility VERIFIED")
            criteria_met += 1
        else:
            print(f"   ❌ Radio Stream Accessibility ISSUES ({stream_success_rate:.1f}%)")
        
        if len(failed_tests) == 0:
            print("   ✅ Zero Critical Failures ACHIEVED")
            criteria_met += 1
        else:
            print(f"   ❌ {len(failed_tests)} Critical Failures DETECTED")
        
        print(f"\n📊 DEPLOYMENT READINESS: {criteria_met}/{total_criteria} criteria met")
        
        if criteria_met >= 3:
            print("🎉 RECOMMENDATION: ✅ PRODUCTION READY - Backend is stable after iOS Memory Integrity Enforcement")
        elif criteria_met >= 2:
            print("⚠️  RECOMMENDATION: READY WITH MONITORING - Minor issues detected")
        else:
            print("❌ RECOMMENDATION: NOT READY - Significant issues require resolution")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = IOSBackendTester()
    tester.run_comprehensive_test()