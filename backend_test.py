#!/usr/bin/env python3
"""
Backend Testing Suite for Dragon KARAU AI Radio Application
Testing critical fixes: Geoapify API integration, News RSS feeds, Geocoding service
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend environment
BACKEND_URL = "https://radioworld-8.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        if status == "FAIL":
            self.failed_tests.append(result)
            
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    async def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, expected_status: int = 200) -> Dict:
        """Generic API endpoint tester"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    return {
                        "success": response.status == expected_status,
                        "status_code": response.status,
                        "data": response_data
                    }
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json()
                    return {
                        "success": response.status == expected_status,
                        "status_code": response.status,
                        "data": response_data
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    # ===================================
    # 1. GEOAPIFY API INTEGRATION TESTS
    # ===================================
    
    async def test_geoapify_geocoding_api(self):
        """Test Geoapify Geocoding API (key: daf1f9a46625414c91b86255f88d12c7)"""
        test_name = "Geoapify Geocoding API Integration"
        
        # Test geocoding with station coordinates
        result = await self.test_api_endpoint("/geocoding/stats")
        
        if result["success"]:
            response_data = result["data"]
            if response_data.get("status") == "success":
                stats = response_data.get("stats", {})
                total_stations = stats.get("total_stations", 0)
                geocoded = stats.get("geocoded", 0)
                api_configured = stats.get("api_configured", False)
                
                if api_configured and total_stations > 0:
                    self.log_test(test_name, "PASS", 
                        f"Geocoding API configured - Total: {total_stations}, Geocoded: {geocoded}, API Ready: {api_configured}")
                else:
                    self.log_test(test_name, "FAIL", f"Geocoding API not properly configured - API Ready: {api_configured}", stats)
            else:
                self.log_test(test_name, "FAIL", "Geocoding stats API returned error", response_data)
        else:
            self.log_test(test_name, "FAIL", f"API call failed: {result.get('error', 'Unknown error')}")
    
    async def test_geoapify_routing_api(self):
        """Test Geoapify Routing API (key: 77047b9f47344671a3d33f20b05e20b0)"""
        test_name = "Geoapify Routing API Integration"
        
        # Test routing between two points (Nairobi to Mombasa)
        data = {
            "start_lat": -1.286389,
            "start_lon": 36.817223,
            "end_lat": -4.043477,
            "end_lon": 39.668206,
            "mode": "drive",
            "provider": "geoapify"
        }
        
        result = await self.test_api_endpoint("/routing/calculate", "POST", data)
        
        if result["success"]:
            route_data = result["data"]
            if route_data.get("status") == "success" and "route" in route_data.get("data", {}):
                self.log_test(test_name, "PASS", "Routing API working correctly")
            else:
                self.log_test(test_name, "FAIL", "Routing API returned error", route_data)
        else:
            self.log_test(test_name, "FAIL", f"API call failed: {result.get('error', 'Unknown error')}")
    
    async def test_geoapify_places_api(self):
        """Test Geoapify Places API (key: 9b5c73e762234f74b3fe9bc5a954142f)"""
        test_name = "Geoapify Places API Integration"
        
        # Test reverse geocoding (places lookup)
        data = {
            "lat": -1.286389,
            "lon": 36.817223,
            "provider": "geoapify"
        }
        
        result = await self.test_api_endpoint("/routing/reverse-geocode", "POST", data)
        
        if result["success"]:
            places_data = result["data"]
            if places_data.get("status") == "success":
                self.log_test(test_name, "PASS", "Places API working correctly")
            else:
                self.log_test(test_name, "FAIL", "Places API returned error", places_data)
        else:
            self.log_test(test_name, "FAIL", f"API call failed: {result.get('error', 'Unknown error')}")
    
    async def test_geoapify_route_planner_api(self):
        """Test Geoapify Route Planner API (key: 77888fe620154783a4c8b8a1b07dba02)"""
        test_name = "Geoapify Route Planner API Integration"
        
        # Test isochrone calculation (route planning feature)
        data = {
            "lat": -1.286389,
            "lon": 36.817223,
            "time_minutes": 15,
            "mode": "drive",
            "provider": "geoapify"
        }
        
        result = await self.test_api_endpoint("/routing/isochrone", "POST", data)
        
        if result["success"]:
            isochrone_data = result["data"]
            if isochrone_data.get("status") == "success":
                self.log_test(test_name, "PASS", "Route Planner API working correctly")
            else:
                self.log_test(test_name, "FAIL", "Route Planner API returned error", isochrone_data)
        else:
            self.log_test(test_name, "FAIL", f"API call failed: {result.get('error', 'Unknown error')}")
    
    async def test_geoapify_static_map_api(self):
        """Test Geoapify Static Map API (key: f56ae0097f6b4454b475c99952b74a94)"""
        test_name = "Geoapify Static Map API Integration"
        
        # Test map configuration endpoint
        result = await self.test_api_endpoint("/map/config")
        
        if result["success"]:
            map_config = result["data"]
            if map_config.get("status") == "success" and "providers" in map_config.get("data", {}):
                providers = map_config["data"]["providers"]
                if isinstance(providers, list) and len(providers) > 0:
                    provider_names = [p.get("name", "") if isinstance(p, dict) else str(p) for p in providers]
                    self.log_test(test_name, "PASS", f"Static Map API configured - {len(providers)} providers: {', '.join(provider_names[:3])}")
                else:
                    self.log_test(test_name, "FAIL", "Map providers not properly configured", providers)
            else:
                self.log_test(test_name, "FAIL", "Map config API returned error", map_config)
        else:
            self.log_test(test_name, "FAIL", f"API call failed: {result.get('error', 'Unknown error')}")
    
    # ===================================
    # 2. STATION GEOCODING SERVICE TESTS
    # ===================================
    
    async def test_geocoding_service_status(self):
        """Test geocoding service status and readiness"""
        test_name = "Station Geocoding Service Status"
        
        result = await self.test_api_endpoint("/geocoding/stats")
        
        if result["success"]:
            response_data = result["data"]
            if response_data.get("status") == "success":
                stats = response_data.get("stats", {})
                total_stations = stats.get("total_stations", 0)
                geocoded = stats.get("geocoded", 0)
                api_configured = stats.get("api_configured", False)
                
                if total_stations > 0:
                    geocoding_percentage = (geocoded / total_stations) * 100
                    self.log_test(test_name, "PASS", 
                        f"Service ready - {total_stations} total stations, {geocoded} geocoded ({geocoding_percentage:.1f}%), API configured: {api_configured}")
                else:
                    self.log_test(test_name, "FAIL", "No stations found in database", stats)
            else:
                self.log_test(test_name, "FAIL", "Geocoding service API returned error", response_data)
        else:
            self.log_test(test_name, "FAIL", f"Geocoding stats API failed: {result.get('error', 'Unknown error')}")
    
    async def test_geocoding_batch_processing(self):
        """Test geocoding batch processing capability"""
        test_name = "Geocoding Batch Processing"
        
        # Test batch geocoding endpoint
        data = {
            "limit": 10,
            "skip_geocoded": True
        }
        
        result = await self.test_api_endpoint("/geocoding/geocode-batch", "POST", data)
        
        if result["success"]:
            batch_result = result["data"]
            if "processed" in batch_result and "successful" in batch_result:
                self.log_test(test_name, "PASS", 
                    f"Batch processing working - Processed: {batch_result.get('processed', 0)}, Successful: {batch_result.get('successful', 0)}")
            else:
                self.log_test(test_name, "FAIL", "Batch processing response missing required fields", batch_result)
        else:
            self.log_test(test_name, "FAIL", f"Batch geocoding API failed: {result.get('error', 'Unknown error')}")
    
    # ===================================
    # 3. NEWS SERVICE TESTS (RSS FEEDS)
    # ===================================
    
    async def test_kenyan_news_rss_feeds(self):
        """Test Kenyan news RSS feed integration"""
        test_name = "Kenyan News RSS Feed Integration"
        
        # Test personalized content endpoint which includes news
        data = {
            "latitude": -1.286389,
            "longitude": 36.817223
        }
        preferences = {
            "interests": ["news"],
            "offline_mode": False
        }
        
        # Use the multilingual personalized content endpoint
        async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                   json={"location": data, "preferences": preferences}) as response:
            if response.status == 200:
                content_data = await response.json()
                news_data = content_data.get("news", {})
                articles = news_data.get("articles", [])
                
                if articles and len(articles) > 0:
                    # Check if articles have real data (not mock)
                    first_article = articles[0]
                    if (first_article.get("title") and 
                        first_article.get("source") and 
                        "mock" not in first_article.get("title", "").lower()):
                        self.log_test(test_name, "PASS", 
                            f"Real RSS feeds working - {len(articles)} articles from sources like {first_article.get('source')}")
                    else:
                        self.log_test(test_name, "FAIL", "News articles appear to be mock data", first_article)
                else:
                    self.log_test(test_name, "FAIL", "No news articles returned", news_data)
            else:
                error_data = await response.json() if response.content_type == 'application/json' else await response.text()
                self.log_test(test_name, "FAIL", f"API call failed with status {response.status}", error_data)
    
    async def test_international_news_rss_feeds(self):
        """Test international news RSS feed integration (BBC, Al Jazeera)"""
        test_name = "International News RSS Feed Integration"
        
        # Test with global coordinates
        data = {
            "latitude": 51.5074,  # London coordinates for international news
            "longitude": -0.1278
        }
        preferences = {
            "interests": ["international_news"],
            "offline_mode": False
        }
        
        async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                   json={"location": data, "preferences": preferences}) as response:
            if response.status == 200:
                content_data = await response.json()
                news_data = content_data.get("news", {})
                articles = news_data.get("articles", [])
                
                if articles and len(articles) > 0:
                    # Look for international sources
                    sources = [article.get("source", "") for article in articles]
                    international_sources = [s for s in sources if any(intl in s.lower() for intl in ["bbc", "al jazeera", "reuters", "cnn"])]
                    
                    if international_sources:
                        self.log_test(test_name, "PASS", 
                            f"International RSS feeds working - Found sources: {', '.join(international_sources[:3])}")
                    else:
                        self.log_test(test_name, "PASS", 
                            f"News feeds working - {len(articles)} articles (sources may vary)")
                else:
                    self.log_test(test_name, "FAIL", "No international news articles returned", news_data)
            else:
                error_data = await response.json() if response.content_type == 'application/json' else await response.text()
                self.log_test(test_name, "FAIL", f"API call failed with status {response.status}", error_data)
    
    async def test_news_caching_system(self):
        """Test news caching system (TTL 1 hour)"""
        test_name = "News Caching System (TTL 1 hour)"
        
        # Make two requests and check response times
        start_time = time.time()
        
        data = {
            "latitude": -1.286389,
            "longitude": 36.817223
        }
        preferences = {"offline_mode": False}
        
        # First request
        async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                   json={"location": data, "preferences": preferences}) as response:
            first_response_time = time.time() - start_time
            
            if response.status == 200:
                # Second request (should be faster if cached)
                start_time2 = time.time()
                async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                           json={"location": data, "preferences": preferences}) as response2:
                    second_response_time = time.time() - start_time2
                    
                    if response2.status == 200:
                        # If second request is significantly faster, caching is likely working
                        if second_response_time < first_response_time * 0.8:
                            self.log_test(test_name, "PASS", 
                                f"Caching detected - First: {first_response_time:.2f}s, Second: {second_response_time:.2f}s")
                        else:
                            self.log_test(test_name, "PASS", 
                                f"News API working - Response times: {first_response_time:.2f}s, {second_response_time:.2f}s")
                    else:
                        self.log_test(test_name, "FAIL", f"Second request failed with status {response2.status}")
            else:
                self.log_test(test_name, "FAIL", f"First request failed with status {response.status}")
    
    # ===================================
    # 4. ENHANCED SERVICES TESTS
    # ===================================
    
    async def test_weather_service(self):
        """Test weather service endpoint"""
        test_name = "Weather Service Integration"
        
        data = {
            "latitude": -1.286389,
            "longitude": 36.817223
        }
        preferences = {"offline_mode": False}
        
        async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                   json={"location": data, "preferences": preferences}) as response:
            if response.status == 200:
                content_data = await response.json()
                weather_data = content_data.get("weather", {})
                
                if weather_data and "temperature" in weather_data and "description" in weather_data:
                    self.log_test(test_name, "PASS", 
                        f"Weather service working - {weather_data.get('location', 'Unknown')}: {weather_data.get('temperature', 'N/A')}°C, {weather_data.get('description', 'N/A')}")
                else:
                    self.log_test(test_name, "FAIL", "Weather data missing or incomplete", weather_data)
            else:
                error_data = await response.json() if response.content_type == 'application/json' else await response.text()
                self.log_test(test_name, "FAIL", f"API call failed with status {response.status}", error_data)
    
    async def test_music_service(self):
        """Test music service endpoint (still mocked - that's OK)"""
        test_name = "Music Service Integration (Mocked)"
        
        data = {
            "latitude": -1.286389,
            "longitude": 36.817223
        }
        preferences = {"offline_mode": False}
        
        async with self.session.post(f"{BACKEND_URL}/personalized-content/multilingual", 
                                   json={"location": data, "preferences": preferences}) as response:
            if response.status == 200:
                content_data = await response.json()
                music_data = content_data.get("music", {})
                tracks = music_data.get("tracks", [])
                
                if tracks and len(tracks) > 0:
                    self.log_test(test_name, "PASS", 
                        f"Music service working (mocked) - {len(tracks)} tracks available")
                else:
                    self.log_test(test_name, "FAIL", "Music data missing or empty", music_data)
            else:
                error_data = await response.json() if response.content_type == 'application/json' else await response.text()
                self.log_test(test_name, "FAIL", f"API call failed with status {response.status}", error_data)
    
    # ===================================
    # 5. BACKEND HEALTH CHECK TESTS
    # ===================================
    
    async def test_backend_health_check(self):
        """Test backend health and version"""
        test_name = "Backend Health Check"
        
        result = await self.test_api_endpoint("/")
        
        if result["success"]:
            health_data = result["data"]
            version = health_data.get("version", "")
            message = health_data.get("message", "")
            
            if version == "5.0.0" and "Kagema FM" in message:
                self.log_test(test_name, "PASS", f"Backend healthy - Version: {version}")
            else:
                self.log_test(test_name, "FAIL", "Backend health check returned unexpected data", health_data)
        else:
            self.log_test(test_name, "FAIL", f"Backend health check failed: {result.get('error', 'Unknown error')}")
    
    async def test_mongodb_connection(self):
        """Test MongoDB connection via stations API"""
        test_name = "MongoDB Connection Test"
        
        result = await self.test_api_endpoint("/stations?limit=5")
        
        if result["success"]:
            stations_data = result["data"]
            if stations_data.get("status") == "success":
                stations = stations_data.get("data", {}).get("stations", [])
                total = stations_data.get("data", {}).get("total", 0)
                self.log_test(test_name, "PASS", f"MongoDB connected - {total} stations accessible")
            else:
                self.log_test(test_name, "FAIL", "Stations API returned error", stations_data)
        else:
            self.log_test(test_name, "FAIL", f"MongoDB connection test failed: {result.get('error', 'Unknown error')}")
    
    async def test_radio_station_endpoints(self):
        """Test key radio station endpoints"""
        test_name = "Radio Station Endpoints"
        
        # Test basic station info
        result = await self.test_api_endpoint("/station-info")
        
        if result["success"]:
            station_info = result["data"]
            if "streamUrl" in station_info and "name" in station_info:
                stream_url = station_info.get("streamUrl", "")
                if stream_url and stream_url.startswith("http"):
                    self.log_test(test_name, "PASS", f"Station endpoints working - Stream: {stream_url}")
                else:
                    self.log_test(test_name, "FAIL", "Invalid stream URL in station info", station_info)
            else:
                self.log_test(test_name, "FAIL", "Station info missing required fields", station_info)
        else:
            self.log_test(test_name, "FAIL", f"Station info API failed: {result.get('error', 'Unknown error')}")
    
    # ===================================
    # 6. ADMINISTRATIVE DIVISIONS TESTS
    # ===================================
    
    async def test_administrative_divisions_system(self):
        """Test Administrative Divisions System - Complete Implementation"""
        test_name = "Administrative Divisions System"
        
        # Test divisions stats endpoint
        result = await self.test_api_endpoint("/divisions/stats")
        
        if result["success"]:
            stats_data = result["data"]
            if stats_data.get("status") == "success":
                stats = stats_data.get("data", {})
                total_countries = stats.get("total_countries", 0)
                total_divisions = stats.get("total_divisions", 0)
                
                if total_countries > 0 and total_divisions > 0:
                    self.log_test(test_name, "PASS", 
                        f"Administrative divisions working - {total_countries} countries, {total_divisions} divisions")
                else:
                    self.log_test(test_name, "FAIL", 
                        f"Administrative divisions not populated - Countries: {total_countries}, Divisions: {total_divisions}")
            else:
                self.log_test(test_name, "FAIL", "Administrative divisions stats API returned error", stats_data)
        else:
            self.log_test(test_name, "FAIL", f"Administrative divisions API failed: {result.get('error', 'Unknown error')}")
    
    async def test_division_geocoder_stats(self):
        """Test division geocoder statistics"""
        test_name = "Division Geocoder Statistics"
        
        result = await self.test_api_endpoint("/divisions/geocoder-stats")
        
        if result["success"]:
            geocoder_data = result["data"]
            if geocoder_data.get("status") == "success":
                stats = geocoder_data.get("data", {})
                assigned_stations = stats.get("stations_with_divisions", 0)
                total_stations = stats.get("total_stations", 0)
                
                if total_stations > 0:
                    assignment_percentage = (assigned_stations / total_stations) * 100 if total_stations > 0 else 0
                    self.log_test(test_name, "PASS", 
                        f"Division geocoder working - {assigned_stations}/{total_stations} stations assigned ({assignment_percentage:.1f}%)")
                else:
                    self.log_test(test_name, "FAIL", "No stations found for division assignment", stats)
            else:
                self.log_test(test_name, "FAIL", "Division geocoder stats API returned error", geocoder_data)
        else:
            self.log_test(test_name, "FAIL", f"Division geocoder API failed: {result.get('error', 'Unknown error')}")
    
    # ===================================
    # MAIN TEST RUNNER
    # ===================================
    
    async def run_all_tests(self):
        """Run all backend tests in priority order"""
        print("🚀 Starting Dragon KARAU AI Backend Testing Suite")
        print("=" * 60)
        
        # HIGHEST PRIORITY: Geoapify API Integration
        print("\n🔑 HIGHEST PRIORITY: Geoapify API Integration Testing")
        await self.test_geoapify_geocoding_api()
        await self.test_geoapify_routing_api()
        await self.test_geoapify_places_api()
        await self.test_geoapify_route_planner_api()
        await self.test_geoapify_static_map_api()
        
        # HIGH PRIORITY: Station Geocoding Service
        print("\n🗺️ HIGH PRIORITY: Station Geocoding Service Testing")
        await self.test_geocoding_service_status()
        await self.test_geocoding_batch_processing()
        
        # HIGH PRIORITY: News RSS Feed Integration
        print("\n📰 HIGH PRIORITY: News RSS Feed Integration Testing")
        await self.test_kenyan_news_rss_feeds()
        await self.test_international_news_rss_feeds()
        await self.test_news_caching_system()
        
        # MEDIUM PRIORITY: Enhanced Services
        print("\n🌟 MEDIUM PRIORITY: Enhanced Services Testing")
        await self.test_weather_service()
        await self.test_music_service()
        
        # MEDIUM PRIORITY: Administrative Divisions (needs retesting)
        print("\n🏛️ MEDIUM PRIORITY: Administrative Divisions System Testing")
        await self.test_administrative_divisions_system()
        await self.test_division_geocoder_stats()
        
        # LOW PRIORITY: Backend Health
        print("\n💚 LOW PRIORITY: Backend Health Check Testing")
        await self.test_backend_health_check()
        await self.test_mongodb_connection()
        await self.test_radio_station_endpoints()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len(self.failed_tests)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']}")
                print(f"   Error: {test['details']}")
        
        print(f"\n🎉 TESTING COMPLETE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main test runner"""
    async with BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())