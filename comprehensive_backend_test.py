#!/usr/bin/env python3
"""
COMPREHENSIVE DEPLOYMENT READINESS TESTING
Testing all areas specified in the review request:
1. Radio Streaming APIs
2. Voice AI Integration  
3. Content & Personalization
4. Content Compliance
5. Platform Integrations
6. Satellite & Offline APIs
7. User Management
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://kagema-player.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.response_times = []
        self.critical_failures = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, response_time: float, details: str = "", critical: bool = False):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            if critical:
                self.critical_failures.append(test_name)
                
        self.response_times.append(response_time)
        result = f"{status} | {test_name} | {response_time:.0f}ms | {details}"
        self.test_results.append(result)
        print(result)
        
    async def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          expected_status: int = 200, test_name: str = "", critical: bool = False) -> Dict[str, Any]:
        """Generic endpoint testing method"""
        start_time = time.time()
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    success = response.status == expected_status
                    
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    success = response.status == expected_status
                    
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    success = response.status == expected_status
                    
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    success = response.status == expected_status
                    
            details = f"Status: {response.status}"
            if not success:
                details += f" | Expected: {expected_status}"
                
            self.log_test(test_name or f"{method} {endpoint}", success, response_time, details, critical)
            
            return {
                "success": success,
                "status": response.status,
                "data": response_data,
                "response_time": response_time
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_test(test_name or f"{method} {endpoint}", False, response_time, f"Error: {str(e)}", critical)
            return {
                "success": False,
                "status": 0,
                "data": {},
                "response_time": response_time,
                "error": str(e)
            }

    async def test_stream_accessibility(self, stream_url: str, stream_name: str, critical: bool = False) -> bool:
        """Test if a radio stream is accessible"""
        start_time = time.time()
        try:
            async with self.session.head(stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = (time.time() - start_time) * 1000
                success = response.status == 200
                content_type = response.headers.get('content-type', '')
                icy_headers = [h for h in response.headers.keys() if h.lower().startswith('icy-')]
                
                details = f"Status: {response.status} | Content-Type: {content_type}"
                if icy_headers:
                    details += f" | ICY Headers: {len(icy_headers)}"
                    
                self.log_test(f"Stream Access: {stream_name}", success, response_time, details, critical)
                return success
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_test(f"Stream Access: {stream_name}", False, response_time, f"Error: {str(e)}", critical)
            return False

    # ==================== 1. RADIO STREAMING APIs ====================
    
    async def test_radio_streaming_apis(self):
        """Test all radio endpoints and stream accessibility"""
        print("\n🎵 TESTING RADIO STREAMING APIs")
        print("=" * 60)
        
        # Test API root
        await self.test_endpoint("GET", "/", test_name="API Root", critical=True)
        
        # Test basic station info
        result = await self.test_endpoint("GET", "/station-info", test_name="Basic Station Info", critical=True)
        if result["success"] and "streamUrl" in result["data"]:
            stream_url = result["data"]["streamUrl"]
            await self.test_stream_accessibility(stream_url, "Main Kagema FM Stream", critical=True)
        
        # Test multilingual station info for different regions
        test_locations = [
            ({"latitude": -1.2921, "longitude": 36.8219}, "Kenya"),
            ({"latitude": -23.5505, "longitude": -46.6333}, "Brazil"),
            ({"latitude": 40.7128, "longitude": -74.0060}, "Global")
        ]
        
        for location, name in test_locations:
            await self.test_endpoint("POST", "/station-info/multilingual", 
                                   data=location, test_name=f"Multilingual Station Info - {name}", critical=True)
            
        # Test personalized content with radio streams - CRITICAL
        user_preferences = {
            "user_id": str(uuid.uuid4()),
            "preferred_language": "en",
            "theme": "dark",
            "offline_mode": False,
            "audio": {"quality": "high", "volume": 0.8},
            "notifications": {"enabled": True, "sound": True}
        }
        
        result = await self.test_endpoint("POST", "/personalized-content/multilingual",
                                        data={
                                            "location": {"latitude": -1.2921, "longitude": 36.8219},
                                            "preferences": user_preferences
                                        },
                                        test_name="Personalized Content with Radio Streams", critical=True)
        
        # Test all alternative streams
        if result["success"] and "radio_streams" in result["data"]:
            radio_streams = result["data"]["radio_streams"]
            if "alternative_streams" in radio_streams:
                print(f"   📡 Testing {len(radio_streams['alternative_streams'])} alternative streams")
                
                for i, stream in enumerate(radio_streams["alternative_streams"]):
                    if "streamUrl" in stream:
                        await self.test_stream_accessibility(
                            stream["streamUrl"], 
                            stream.get("name", f"Stream {i+1}"),
                            critical=(i < 3)  # First 3 streams are critical
                        )

    # ==================== 2. VOICE AI INTEGRATION ====================
    
    async def test_voice_ai_integration(self):
        """Test voice command processing and interpretation"""
        print("\n🎤 TESTING VOICE AI INTEGRATION")
        print("=" * 60)
        
        # Test voice intents endpoint
        await self.test_endpoint("GET", "/voice/intents", test_name="Voice Intents List", critical=True)
        
        # Test voice help endpoint
        await self.test_endpoint("GET", "/voice/help", test_name="Voice Help System", critical=True)
        
        # Test comprehensive voice command interpretation
        voice_commands = [
            {"text": "play music", "expected": "play", "critical": True},
            {"text": "pause", "expected": "pause", "critical": True},
            {"text": "next station", "expected": "next", "critical": True},
            {"text": "volume up", "expected": "volume_up", "critical": False},
            {"text": "search for jazz music", "expected": "search", "critical": True},
            {"text": "tune to classical station", "expected": "station", "critical": True},
            {"text": "I want to listen to relaxing ambient music", "expected": "search", "critical": False},
            {"text": "browse external sources", "expected": "browse", "critical": False},
            {"text": "find rock music", "expected": "search", "critical": False}
        ]
        
        for cmd in voice_commands:
            result = await self.test_endpoint("POST", "/voice/interpret",
                                            data={"text": cmd["text"]},
                                            test_name=f"Voice Command: '{cmd['text']}'",
                                            critical=cmd["critical"])
            
            if result["success"] and "intent" in result["data"]:
                intent = result["data"]["intent"]
                confidence = result["data"].get("confidence", 0)
                parameters = result["data"].get("parameters", {})
                print(f"   🎯 Intent: {intent} | Confidence: {confidence:.2f} | Params: {parameters}")

    # ==================== 3. CONTENT & PERSONALIZATION ====================
    
    async def test_content_personalization(self):
        """Test multilingual content and language detection"""
        print("\n🌍 TESTING CONTENT & PERSONALIZATION")
        print("=" * 60)
        
        # Test supported languages
        await self.test_endpoint("GET", "/languages", test_name="Supported Languages", critical=True)
        
        # Test language detection for different Kenyan regions
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "expected": "Nairobi, Kenya"},
            {"latitude": -0.0917, "longitude": 34.7680, "expected": "Kisumu, Kenya"},
            {"latitude": -1.1010, "longitude": 37.0140, "expected": "Kiambu, Kenya"},
            {"latitude": 0.5143, "longitude": 35.2698, "expected": "Kakamega, Kenya"},
            {"latitude": -0.3031, "longitude": 36.0800, "expected": "Nakuru, Kenya"}
        ]
        
        for location in test_locations:
            result = await self.test_endpoint("POST", "/language/detect",
                                            data={"latitude": location["latitude"], "longitude": location["longitude"]},
                                            test_name=f"Language Detection - {location['expected']}", critical=True)
            
            if result["success"]:
                detected_lang = result["data"].get("detected_language", "unknown")
                confidence = result["data"].get("confidence", 0)
                county = result["data"].get("county", "unknown")
                print(f"   🗣️ Language: {detected_lang} | County: {county} | Confidence: {confidence:.3f}")

    # ==================== 4. CONTENT COMPLIANCE ====================
    
    async def test_content_compliance(self):
        """Test disclaimer and compliance systems"""
        print("\n⚖️ TESTING CONTENT COMPLIANCE")
        print("=" * 60)
        
        # Test content disclaimers for different regions and languages
        compliance_requests = [
            {"country_code": "KE", "language_code": "en", "content_types": ["radio_streams", "music", "news"]},
            {"country_code": "KE", "language_code": "sw", "content_types": ["radio_streams"]},
            {"country_code": "BR", "language_code": "pt-br", "content_types": ["radio_streams", "news"]},
            {"country_code": "GLOBAL", "language_code": "en", "content_types": ["radio_streams", "music"]}
        ]
        
        for req in compliance_requests:
            await self.test_endpoint("POST", "/compliance/disclaimers",
                                   data=req, 
                                   test_name=f"Content Disclaimers - {req['country_code']} ({req['language_code']})",
                                   critical=True)
        
        # Test user acknowledgment system
        acknowledgment_data = {
            "disclaimer_ids": ["general_responsibility", "mature_content", "platform_responsibility"],
            "user_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_age": 25,
            "country_code": "KE"
        }
        
        await self.test_endpoint("POST", "/compliance/acknowledge",
                               data=acknowledgment_data, 
                               test_name="User Acknowledgment Recording", critical=True)
        
        # Test content compliance checks for different scenarios
        compliance_scenarios = [
            {"country_code": "KE", "content_rating": "general", "user_age": 18, "current_hour": 14},
            {"country_code": "KE", "content_rating": "mature", "user_age": 25, "current_hour": 22},
            {"country_code": "BR", "content_rating": "adult", "user_age": 30, "current_hour": 20},
            {"country_code": "GLOBAL", "content_rating": "explicit", "user_age": 21, "current_hour": 2}
        ]
        
        for scenario in compliance_scenarios:
            params = "&".join([f"{k}={v}" for k, v in scenario.items()])
            await self.test_endpoint("POST", f"/compliance/check-content?{params}",
                                   test_name=f"Content Compliance - {scenario['country_code']} {scenario['content_rating']}", 
                                   critical=True)

    # ==================== 5. PLATFORM INTEGRATIONS ====================
    
    async def test_platform_integrations(self):
        """Test Spotify, Google Maps, external audio sources"""
        print("\n🔗 TESTING PLATFORM INTEGRATIONS")
        print("=" * 60)
        
        # Test platform initialization
        integration_types = ["general", "google_maps", "spotify", "voice_control"]
        
        for integration_type in integration_types:
            await self.test_endpoint("POST", "/integrations/initialize",
                                   data={"type": integration_type},
                                   test_name=f"Initialize {integration_type.title()} Integration",
                                   critical=True)
        
        # Test Spotify integration endpoints
        await self.test_endpoint("GET", "/spotify/auth/login", test_name="Spotify Auth URL", critical=False)
        await self.test_endpoint("GET", "/spotify/genres", test_name="Spotify Available Genres", critical=False)
        
        # Test Spotify search functionality
        search_data = {"query": "jazz music", "limit": 10}
        await self.test_endpoint("POST", "/spotify/search", 
                               data=search_data, test_name="Spotify Track Search", critical=False)
        
        # Test Google Maps integration
        nearby_places_data = {
            "latitude": -1.2921,
            "longitude": 36.8219,
            "radius": 5000,
            "place_type": "restaurant"
        }
        await self.test_endpoint("POST", "/googlemaps/places/nearby",
                               data=nearby_places_data, test_name="Google Maps Nearby Places", critical=False)
        
        # Test geocoding services
        geocode_data = {"address": "Nairobi, Kenya"}
        await self.test_endpoint("POST", "/googlemaps/geocode",
                               data=geocode_data, test_name="Google Maps Geocoding", critical=False)
        
        reverse_geocode_data = {"latitude": -1.2921, "longitude": 36.8219}
        await self.test_endpoint("POST", "/googlemaps/reverse-geocode",
                               data=reverse_geocode_data, test_name="Google Maps Reverse Geocoding", critical=False)
        
        # Test directions and traffic
        directions_data = {
            "origin": "Nairobi, Kenya",
            "destination": "Mombasa, Kenya",
            "mode": "driving"
        }
        await self.test_endpoint("POST", "/googlemaps/directions",
                               data=directions_data, test_name="Google Maps Directions", critical=False)
        
        traffic_params = "?latitude=-1.2921&longitude=36.8219&radius=2000"
        await self.test_endpoint("POST", f"/googlemaps/traffic{traffic_params}",
                               test_name="Google Maps Traffic Conditions", critical=False)

    # ==================== 6. SATELLITE & OFFLINE APIs ====================
    
    async def test_satellite_offline_apis(self):
        """Test offline caching and satellite connectivity"""
        print("\n📡 TESTING SATELLITE & OFFLINE APIs")
        print("=" * 60)
        
        # Test satellite status
        await self.test_endpoint("GET", "/satellite/status", test_name="Satellite Status", critical=True)
        
        # Test satellite connection
        satellite_data = {
            "provider": "starlink",
            "client_id": "kagema_fm_test",
            "location": "auto"
        }
        await self.test_endpoint("POST", "/satellite/connect",
                               data=satellite_data, test_name="Satellite Connection", critical=True)
        
        # Test offline caching with comprehensive content types
        cache_data = {
            "content_types": ["radio_streams", "news", "weather", "music", "language_data"],
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "cache_duration_hours": 24
        }
        await self.test_endpoint("POST", "/offline/cache",
                               data=cache_data, test_name="Offline Content Caching", critical=True)

    # ==================== 7. USER MANAGEMENT ====================
    
    async def test_user_management(self):
        """Test user preferences, favorites, listening history"""
        print("\n👤 TESTING USER MANAGEMENT")
        print("=" * 60)
        
        test_user_id = str(uuid.uuid4())
        
        # Test user preferences management
        preferences_data = {
            "user_id": test_user_id,
            "preferred_language": "en",
            "theme": "dark",
            "offline_mode": False,
            "audio": {"quality": "high", "volume": 0.8},
            "notifications": {"enabled": True, "sound": True}
        }
        
        await self.test_endpoint("PUT", f"/user/{test_user_id}/preferences",
                               data=preferences_data, test_name="Update User Preferences", critical=True)
        
        await self.test_endpoint("GET", f"/user/{test_user_id}/preferences",
                               test_name="Get User Preferences", critical=True)
        
        # Test favorites system
        favorite_items = [
            {"favorite_type": "radio_station", "item_id": "kagema_fm_main", "title": "Kagema FM", 
             "metadata": {"frequency": "101.5 FM", "location": "Nairobi"}},
            {"favorite_type": "news_article", "item_id": "news_123", "title": "Breaking News", 
             "metadata": {"source": "BBC", "category": "world"}},
            {"favorite_type": "music_track", "item_id": "track_456", "title": "Jazz Classic", 
             "metadata": {"artist": "Miles Davis", "album": "Kind of Blue"}}
        ]
        
        for favorite in favorite_items:
            await self.test_endpoint("POST", f"/user/{test_user_id}/favorites",
                                   data=favorite, 
                                   test_name=f"Add Favorite - {favorite['favorite_type']}", critical=True)
        
        await self.test_endpoint("GET", f"/user/{test_user_id}/favorites",
                               test_name="Get All User Favorites", critical=True)
        
        # Test filtered favorites
        await self.test_endpoint("GET", f"/user/{test_user_id}/favorites?favorite_type=radio_station",
                               test_name="Get Filtered Favorites", critical=False)
        
        # Test listening history and analytics
        session_data = {
            "user_id": test_user_id,
            "station_id": "kagema_fm_main",
            "station_name": "Kagema FM",
            "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
            "started_at": datetime.now().isoformat(),
            "content_type": "radio_stream"
        }
        
        result = await self.test_endpoint("POST", f"/user/{test_user_id}/listening-session",
                                        data=session_data, test_name="Start Listening Session", critical=True)
        
        await self.test_endpoint("GET", f"/user/{test_user_id}/listening-history",
                               test_name="Get Listening History", critical=True)
        
        await self.test_endpoint("GET", f"/user/{test_user_id}/stats",
                               test_name="Get Listening Statistics", critical=True)
        
        await self.test_endpoint("GET", f"/user/{test_user_id}/recommendations",
                               test_name="Get Personalized Recommendations", critical=True)
        
        # Test enhanced station info with personalization
        await self.test_endpoint("GET", f"/station-info/enhanced/{test_user_id}",
                               test_name="Enhanced Station Info with Personalization", critical=False)
        
        # Test GDPR compliance features
        await self.test_endpoint("GET", f"/user/{test_user_id}/export",
                               test_name="Export User Data (GDPR)", critical=True)

    # ==================== PERFORMANCE & RELIABILITY TESTS ====================
    
    async def test_performance_reliability(self):
        """Test response times and concurrent connections"""
        print("\n⚡ TESTING PERFORMANCE & RELIABILITY")
        print("=" * 60)
        
        # Test concurrent connections
        print("   🔄 Testing concurrent connections...")
        concurrent_tasks = []
        for i in range(10):
            task = self.test_endpoint("GET", "/station-info", test_name=f"Concurrent Request {i+1}")
            concurrent_tasks.append(task)
        
        results = await asyncio.gather(*concurrent_tasks)
        successful_concurrent = sum(1 for r in results if r["success"])
        print(f"   📊 Concurrent Success Rate: {successful_concurrent}/10 ({successful_concurrent*10}%)")
        
        # Test error handling
        await self.test_endpoint("GET", "/nonexistent-endpoint", 
                               expected_status=404, test_name="404 Error Handling", critical=False)
        
        await self.test_endpoint("POST", "/station-info/multilingual",
                               data={"invalid": "data"},
                               expected_status=422, test_name="422 Validation Error", critical=False)

    # ==================== MAIN TEST RUNNER ====================
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend tests per review request"""
        print("🎉 KAGEMA FM COMPREHENSIVE DEPLOYMENT READINESS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites per review request
            await self.test_radio_streaming_apis()           # 1. Radio Streaming APIs
            await self.test_voice_ai_integration()           # 2. Voice AI Integration
            await self.test_content_personalization()        # 3. Content & Personalization
            await self.test_content_compliance()             # 4. Content Compliance
            await self.test_platform_integrations()          # 5. Platform Integrations
            await self.test_satellite_offline_apis()         # 6. Satellite & Offline APIs
            await self.test_user_management()                # 7. User Management
            await self.test_performance_reliability()        # Performance & Reliability
            
        finally:
            await self.cleanup()
        
        # Generate final deployment readiness report
        return self.generate_deployment_readiness_report()
    
    def generate_deployment_readiness_report(self):
        """Generate comprehensive deployment readiness report"""
        print("\n" + "=" * 80)
        print("🎯 DEPLOYMENT READINESS ASSESSMENT")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        max_response_time = max(self.response_times) if self.response_times else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Critical Failures: {len(self.critical_failures)}")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Average Response Time: {avg_response_time:.0f}ms")
        print(f"   Maximum Response Time: {max_response_time:.0f}ms")
        print(f"   Target <500ms: {'✅ MET' if avg_response_time < 500 else '⚠️ EXCEEDED'}")
        print(f"   Target <2000ms: {'✅ MET' if max_response_time < 2000 else '⚠️ EXCEEDED'}")
        
        print(f"\n🎯 DEPLOYMENT READINESS CRITERIA:")
        
        # Critical endpoints success rate
        critical_success = success_rate >= 95
        print(f"   >95% Success Rate: {'✅ ACHIEVED' if critical_success else '❌ NOT MET'} ({success_rate:.1f}%)")
        
        # Performance criteria
        performance_met = avg_response_time < 500
        print(f"   <500ms Average Response: {'✅ ACHIEVED' if performance_met else '❌ NOT MET'} ({avg_response_time:.0f}ms)")
        
        # No critical failures
        no_critical_failures = len(self.critical_failures) == 0
        print(f"   No Critical Failures: {'✅ ACHIEVED' if no_critical_failures else '❌ CRITICAL ISSUES'}")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        print(f"\n🎉 DEPLOYMENT RECOMMENDATION:")
        if critical_success and performance_met and no_critical_failures:
            print("   ✅ PRODUCTION READY - All criteria met, deploy with confidence!")
            deployment_status = "READY"
        elif success_rate >= 90 and len(self.critical_failures) == 0:
            print("   ⚠️ MOSTLY READY - Minor issues present, acceptable for deployment")
            deployment_status = "ACCEPTABLE"
        elif success_rate >= 80:
            print("   ⚠️ NEEDS ATTENTION - Several issues found, address before deployment")
            deployment_status = "NEEDS_WORK"
        else:
            print("   ❌ NOT READY - Critical issues found, do not deploy")
            deployment_status = "NOT_READY"
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results[-10:]:  # Show last 10 results
            print(f"   {result}")
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE DEPLOYMENT READINESS TESTING COMPLETE")
        print("=" * 80)
        
        return {
            "deployment_status": deployment_status,
            "success_rate": success_rate,
            "critical_failures": len(self.critical_failures),
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time
        }

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    results = await tester.run_comprehensive_tests()
    
    # Return appropriate exit code based on deployment readiness
    if results["deployment_status"] in ["READY", "ACCEPTABLE"]:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))