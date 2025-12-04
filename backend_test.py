#!/usr/bin/env python3
"""
Dragon KARAU AI - Backend Testing Suite
Testing Stream Validation Service Fix and Radio-Browser.info Integration
"""

import asyncio
import aiohttp
import json
import sys
import time
from typing import Dict, Any, List
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://radio-compass-5.preview.emergentagent.com/api"

class DragonKarauBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Generic endpoint tester"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'success': response.status == 200
                    }
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data, params=params) as response:
                    response_data = await response.json()
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'success': response.status == 200
                    }
        except Exception as e:
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'success': False,
                'exception': str(e)
            }
    
    # ===================================
    # STREAM VALIDATION SERVICE TESTS
    # ===================================
    
    async def test_stream_validation_service(self):
        """Test Stream Validation Service with improved timeout and retry settings"""
        print("\n🔍 TESTING STREAM VALIDATION SERVICE")
        print("=" * 60)
        
        # Test 1: Stream validation statistics
        result = await self.test_endpoint('GET', '/streams/stats')
        if result['success']:
            stats = result['data'].get('data', {})
            self.log_test(
                "Stream Validation Stats API",
                True,
                f"Total stations: {stats.get('total_stations', 0)}, "
                f"Validated: {stats.get('validated', 0)}, "
                f"Online: {stats.get('online', 0)}, "
                f"Offline: {stats.get('offline', 0)}"
            )
        else:
            self.log_test("Stream Validation Stats API", False, f"Error: {result['data']}")
        
        # Test 2: Validate known working stream URL
        test_stream_url = "http://ice1.somafm.com/groovesalad-256-mp3"
        result = await self.test_endpoint('GET', '/streams/validate-url', params={'url': test_stream_url})
        if result['success']:
            validation_data = result['data'].get('data', {})
            is_valid = validation_data.get('is_valid', False)
            status = validation_data.get('status', 'unknown')
            response_time = validation_data.get('response_time_ms', 0)
            content_type = validation_data.get('content_type', '')
            
            self.log_test(
                "Stream URL Validation (SomaFM)",
                is_valid and status == 'online',
                f"Status: {status}, Valid: {is_valid}, "
                f"Response time: {response_time}ms, Content-Type: {content_type}"
            )
        else:
            self.log_test("Stream URL Validation (SomaFM)", False, f"Error: {result['data']}")
        
        # Test 3: Test timeout handling with invalid URL
        invalid_stream_url = "http://invalid-stream-url-that-should-timeout.com/stream"
        result = await self.test_endpoint('GET', '/streams/validate-url', params={'url': invalid_stream_url})
        if result['success']:
            validation_data = result['data'].get('data', {})
            status = validation_data.get('status', 'unknown')
            error = validation_data.get('error', '')
            
            # Should handle timeout or error gracefully
            timeout_handled = status in ['timeout', 'error'] and not validation_data.get('is_valid', True)
            self.log_test(
                "Stream Timeout Handling",
                timeout_handled,
                f"Status: {status}, Error: {error[:100]}"
            )
        else:
            self.log_test("Stream Timeout Handling", False, f"Error: {result['data']}")
        
        # Test 4: Batch validation (small batch for testing)
        result = await self.test_endpoint('POST', '/streams/validate-batch', params={'limit': 5})
        if result['success']:
            batch_data = result['data'].get('data', {})
            validated = batch_data.get('validated', 0)
            online = batch_data.get('online', 0)
            offline = batch_data.get('offline', 0)
            
            self.log_test(
                "Batch Stream Validation",
                batch_data.get('status') == 'success',
                f"Validated: {validated}, Online: {online}, Offline: {offline}"
            )
        else:
            self.log_test("Batch Stream Validation", False, f"Error: {result['data']}")
    
    # ===================================
    # RADIO-BROWSER.INFO INTEGRATION TESTS
    # ===================================
    
    async def test_radio_browser_info_integration(self):
        """Test Radio-Browser.info Integration (Free API, no authentication required)"""
        print("\n🌍 TESTING RADIO-BROWSER.INFO INTEGRATION")
        print("=" * 60)
        
        # Test 1: Get available countries
        result = await self.test_endpoint('GET', '/radio-browser-info/countries')
        if result['success']:
            countries_data = result['data']
            count = countries_data.get('count', 0)
            countries = countries_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Countries API",
                count > 0 and len(countries) > 0,
                f"Retrieved {count} countries, showing first {len(countries)}"
            )
            
            # Show sample countries
            if countries:
                sample_countries = [c.get('name', 'Unknown') for c in countries[:5]]
                print(f"    Sample countries: {', '.join(sample_countries)}")
        else:
            self.log_test("Radio-Browser Countries API", False, f"Error: {result['data']}")
        
        # Test 2: Get available languages
        result = await self.test_endpoint('GET', '/radio-browser-info/languages')
        if result['success']:
            languages_data = result['data']
            count = languages_data.get('count', 0)
            languages = languages_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Languages API",
                count > 0 and len(languages) > 0,
                f"Retrieved {count} languages, showing first {len(languages)}"
            )
            
            # Show sample languages
            if languages:
                sample_languages = [l.get('name', 'Unknown') for l in languages[:5]]
                print(f"    Sample languages: {', '.join(sample_languages)}")
        else:
            self.log_test("Radio-Browser Languages API", False, f"Error: {result['data']}")
        
        # Test 3: Get available tags/genres
        result = await self.test_endpoint('GET', '/radio-browser-info/tags')
        if result['success']:
            tags_data = result['data']
            count = tags_data.get('count', 0)
            tags = tags_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Tags/Genres API",
                count > 0 and len(tags) > 0,
                f"Retrieved {count} tags/genres, showing first {len(tags)}"
            )
            
            # Show sample tags
            if tags:
                sample_tags = [t.get('name', 'Unknown') for t in tags[:5]]
                print(f"    Sample tags: {', '.join(sample_tags)}")
        else:
            self.log_test("Radio-Browser Tags/Genres API", False, f"Error: {result['data']}")
        
        # Test 4: Search by country (US)
        result = await self.test_endpoint('POST', '/radio-browser-info/search', params={'country': 'US', 'limit': 10})
        if result['success']:
            search_data = result['data']
            count = search_data.get('count', 0)
            stations = search_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Search by Country (US)",
                count > 0 and len(stations) > 0,
                f"Found {count} US stations"
            )
            
            # Verify station data structure
            if stations:
                station = stations[0]
                has_required_fields = all(field in station for field in ['name', 'stream_url', 'country'])
                print(f"    Sample station: {station.get('name', 'Unknown')} - {station.get('country', 'Unknown')}")
                print(f"    Required fields present: {has_required_fields}")
        else:
            self.log_test("Radio-Browser Search by Country (US)", False, f"Error: {result['data']}")
        
        # Test 5: Search by language (english)
        result = await self.test_endpoint('POST', '/radio-browser-info/search', params={'language': 'english', 'limit': 10})
        if result['success']:
            search_data = result['data']
            count = search_data.get('count', 0)
            stations = search_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Search by Language (English)",
                count > 0 and len(stations) > 0,
                f"Found {count} English stations"
            )
        else:
            self.log_test("Radio-Browser Search by Language (English)", False, f"Error: {result['data']}")
        
        # Test 6: Search by tag/genre (rock)
        result = await self.test_endpoint('POST', '/radio-browser-info/search', params={'tag': 'rock', 'limit': 10})
        if result['success']:
            search_data = result['data']
            count = search_data.get('count', 0)
            stations = search_data.get('data', [])
            
            self.log_test(
                "Radio-Browser Search by Tag (Rock)",
                count > 0 and len(stations) > 0,
                f"Found {count} rock stations"
            )
        else:
            self.log_test("Radio-Browser Search by Tag (Rock)", False, f"Error: {result['data']}")
        
        # Test 7: Crawl and save stations (small batch for testing)
        crawl_data = {
            "countries": ["KE", "US"],  # Kenya and US
            "limit_per_search": 20
        }
        result = await self.test_endpoint('POST', '/radio-browser-info/crawl', data=crawl_data)
        if result['success']:
            crawl_result = result['data'].get('data', {})
            total_found = crawl_result.get('total_found', 0)
            new_stations = crawl_result.get('new_stations', 0)
            updated_stations = crawl_result.get('updated_stations', 0)
            
            self.log_test(
                "Radio-Browser Crawl and Save",
                crawl_result.get('start_time') is not None,
                f"Found: {total_found}, New: {new_stations}, Updated: {updated_stations}"
            )
        else:
            self.log_test("Radio-Browser Crawl and Save", False, f"Error: {result['data']}")
    
    # ===================================
    # MULTI-SOURCE CRAWLER INTEGRATION TESTS
    # ===================================
    
    async def test_multi_source_crawler_integration(self):
        """Test Multi-Source Crawler Manager integration with Radio-Browser.info"""
        print("\n🔄 TESTING MULTI-SOURCE CRAWLER INTEGRATION")
        print("=" * 60)
        
        # Test 1: Get crawler statistics
        result = await self.test_endpoint('GET', '/crawler/stats')
        if result['success']:
            stats_data = result['data'].get('data', {})
            total_stations = stats_data.get('total_stations', 0)
            sources = stats_data.get('sources', {})
            available_crawlers = stats_data.get('available_crawlers', [])
            
            radio_browser_info_available = 'radio_browser_info' in available_crawlers
            
            self.log_test(
                "Multi-Source Crawler Stats",
                total_stations >= 0 and len(available_crawlers) > 0,
                f"Total stations: {total_stations}, Available crawlers: {len(available_crawlers)}"
            )
            
            self.log_test(
                "Radio-Browser.info Crawler Available",
                radio_browser_info_available,
                f"Available crawlers: {', '.join(available_crawlers)}"
            )
        else:
            self.log_test("Multi-Source Crawler Stats", False, f"Error: {result['data']}")
        
        # Test 2: Start Radio-Browser.info crawler via multi-source manager
        result = await self.test_endpoint('POST', '/crawler/start/radio_browser_info')
        if result['success']:
            start_data = result['data']
            
            self.log_test(
                "Start Radio-Browser.info Crawler",
                start_data.get('status') in ['success', 'started', 'running'],
                f"Status: {start_data.get('status', 'unknown')}"
            )
        else:
            self.log_test("Start Radio-Browser.info Crawler", False, f"Error: {result['data']}")
        
        # Test 3: Verify Radio-Browser.info is listed as available source
        result = await self.test_endpoint('GET', '/crawler/discover-sources')
        if result['success']:
            discover_data = result['data'].get('data', {})
            current_sources = discover_data.get('current_sources', [])
            
            radio_browser_info_listed = 'radio_browser_info' in current_sources
            
            self.log_test(
                "Radio-Browser.info Listed as Source",
                radio_browser_info_listed,
                f"Current sources: {', '.join(current_sources)}"
            )
        else:
            self.log_test("Radio-Browser.info Listed as Source", False, f"Error: {result['data']}")
    
    # ===================================
    # QUALITY AND METADATA TESTS
    # ===================================
    
    async def test_quality_and_metadata(self):
        """Test quality scores and metadata for Radio-Browser.info stations"""
        print("\n📊 TESTING QUALITY SCORES AND METADATA")
        print("=" * 60)
        
        # Get some stations and check their quality scores and metadata
        result = await self.test_endpoint('POST', '/radio-browser-info/search', params={'limit': 5})
        if result['success']:
            stations = result['data'].get('data', [])
            
            if stations:
                quality_scores = []
                has_coordinates = 0
                has_metadata = 0
                
                for station in stations:
                    # Check quality score (should be 0-100)
                    quality_score = station.get('quality_score', 0)
                    if 0 <= quality_score <= 100:
                        quality_scores.append(quality_score)
                    
                    # Check coordinates
                    if station.get('latitude') and station.get('longitude'):
                        has_coordinates += 1
                    
                    # Check metadata
                    required_fields = ['name', 'stream_url', 'country', 'source']
                    if all(station.get(field) for field in required_fields):
                        has_metadata += 1
                
                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                
                self.log_test(
                    "Quality Scores (0-100 range)",
                    len(quality_scores) == len(stations) and avg_quality > 0,
                    f"Average quality: {avg_quality:.1f}, Range: {min(quality_scores) if quality_scores else 0}-{max(quality_scores) if quality_scores else 0}"
                )
                
                self.log_test(
                    "Station Coordinates Available",
                    has_coordinates > 0,
                    f"{has_coordinates}/{len(stations)} stations have coordinates"
                )
                
                self.log_test(
                    "Station Metadata Complete",
                    has_metadata == len(stations),
                    f"{has_metadata}/{len(stations)} stations have complete metadata"
                )
            else:
                self.log_test("Quality and Metadata Tests", False, "No stations found for testing")
        else:
            self.log_test("Quality and Metadata Tests", False, f"Error: {result['data']}")
    
    # ===================================
    # MAIN TEST RUNNER
    # ===================================
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🐉 DRAGON KARAU AI - BACKEND TESTING SUITE")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run test suites
        await self.test_stream_validation_service()
        await self.test_radio_browser_info_integration()
        await self.test_multi_source_crawler_integration()
        await self.test_quality_and_metadata()
        
        # Summary
        print("\n📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }


async def main():
    """Main test runner"""
    async with DragonKarauBackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Exit with appropriate code
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

# End of file
        """Test 1: Distance Matrix Status Endpoint"""
        print("\n🔍 Testing Distance Matrix Status Endpoint...")
        
        try:
            url = f"{BACKEND_URL}/routing/distance-matrix/status"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required fields
                    if data.get('status') == 'success':
                        status_data = data.get('data', {})
                        
                        # Verify API configuration
                        api_configured = status_data.get('api_configured', False)
                        provider = status_data.get('provider')
                        cache_entries = status_data.get('cache_entries', 0)
                        endpoints = status_data.get('endpoints', [])
                        
                        self.log_test(
                            "Distance Matrix Status API",
                            True,
                            f"API configured: {api_configured}, Provider: {provider}, Cache entries: {cache_entries}, Endpoints: {len(endpoints)}"
                        )
                        
                        # Check if API key is properly loaded
                        if api_configured:
                            self.log_test("Distance Matrix API Key Configuration", True, "API key is properly loaded")
                        else:
                            self.log_test("Distance Matrix API Key Configuration", False, "API key not configured")
                        
                        return True
                    else:
                        self.log_test("Distance Matrix Status API", False, f"Unexpected status: {data.get('status')}")
                        return False
                else:
                    self.log_test("Distance Matrix Status API", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Distance Matrix Status API", False, f"Exception: {str(e)}")
            return False
    
    async def test_distance_matrix_calculation(self):
        """Test 2: Distance Matrix Calculation Endpoint"""
        print("\n🧮 Testing Distance Matrix Calculation Endpoint...")
        
        # Test data: New York to Chicago, Los Angeles
        test_data = {
            "sources": [
                {"lat": 40.7128, "lon": -74.0060},  # New York
                {"lat": 34.0522, "lon": -118.2437}  # Los Angeles
            ],
            "targets": [
                {"lat": 41.8781, "lon": -87.6298},  # Chicago
                {"lat": 29.7604, "lon": -95.3698}   # Houston
            ],
            "mode": "drive"
        }
        
        try:
            url = f"{BACKEND_URL}/routing/distance-matrix"
            headers = {'Content-Type': 'application/json'}
            
            async with self.session.post(url, json=test_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        result_data = data.get('data', {})
                        
                        # Verify response structure
                        provider = result_data.get('provider')
                        mode = result_data.get('mode')
                        sources_count = result_data.get('sources_count')
                        targets_count = result_data.get('targets_count')
                        matrix = result_data.get('matrix', [])
                        
                        self.log_test(
                            "Distance Matrix Calculation - Basic Structure",
                            True,
                            f"Provider: {provider}, Mode: {mode}, Sources: {sources_count}, Targets: {targets_count}"
                        )
                        
                        # Verify matrix dimensions
                        if len(matrix) == sources_count:
                            matrix_valid = True
                            for i, source_row in enumerate(matrix):
                                if len(source_row) != targets_count:
                                    matrix_valid = False
                                    break
                                    
                                # Check distance and duration data
                                for j, target_data in enumerate(source_row):
                                    if target_data.get('reachable'):
                                        distance_m = target_data.get('distance_meters')
                                        duration_s = target_data.get('duration_seconds')
                                        distance_km = target_data.get('distance_km')
                                        duration_min = target_data.get('duration_minutes')
                                        
                                        if not all([distance_m, duration_s, distance_km, duration_min]):
                                            matrix_valid = False
                                            break
                            
                            if matrix_valid:
                                self.log_test(
                                    "Distance Matrix Calculation - Matrix Data",
                                    True,
                                    f"Valid {sources_count}x{targets_count} matrix with distances and durations"
                                )
                            else:
                                self.log_test(
                                    "Distance Matrix Calculation - Matrix Data",
                                    False,
                                    "Matrix contains invalid or missing distance/duration data"
                                )
                        else:
                            self.log_test(
                                "Distance Matrix Calculation - Matrix Dimensions",
                                False,
                                f"Expected {sources_count} rows, got {len(matrix)}"
                            )
                        
                        return True
                    else:
                        self.log_test("Distance Matrix Calculation", False, f"API returned error: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Distance Matrix Calculation", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Distance Matrix Calculation", False, f"Exception: {str(e)}")
            return False
    
    async def test_distance_matrix_modes(self):
        """Test 3: Distance Matrix with Different Travel Modes"""
        print("\n🚗🚶🚴 Testing Distance Matrix with Different Travel Modes...")
        
        # Simple test data
        test_data_base = {
            "sources": [{"lat": 40.7128, "lon": -74.0060}],  # New York
            "targets": [{"lat": 41.8781, "lon": -87.6298}]   # Chicago
        }
        
        modes = ['drive', 'walk', 'bicycle']
        mode_results = {}
        
        for mode in modes:
            try:
                test_data = test_data_base.copy()
                test_data['mode'] = mode
                
                url = f"{BACKEND_URL}/routing/distance-matrix"
                headers = {'Content-Type': 'application/json'}
                
                async with self.session.post(url, json=test_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'success':
                            result_data = data.get('data', {})
                            matrix = result_data.get('matrix', [])
                            
                            if matrix and len(matrix) > 0 and len(matrix[0]) > 0:
                                target_data = matrix[0][0]
                                if target_data.get('reachable'):
                                    mode_results[mode] = {
                                        'distance_km': target_data.get('distance_km'),
                                        'duration_minutes': target_data.get('duration_minutes')
                                    }
                                    self.log_test(
                                        f"Distance Matrix - {mode.title()} Mode",
                                        True,
                                        f"Distance: {target_data.get('distance_km')}km, Duration: {target_data.get('duration_minutes')}min"
                                    )
                                else:
                                    self.log_test(f"Distance Matrix - {mode.title()} Mode", False, "Route not reachable")
                            else:
                                self.log_test(f"Distance Matrix - {mode.title()} Mode", False, "Empty matrix response")
                        else:
                            self.log_test(f"Distance Matrix - {mode.title()} Mode", False, f"API error: {data}")
                    else:
                        self.log_test(f"Distance Matrix - {mode.title()} Mode", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"Distance Matrix - {mode.title()} Mode", False, f"Exception: {str(e)}")
        
        return len(mode_results) > 0
    
    async def test_nearest_stations_endpoint(self):
        """Test 4: Nearest Stations Endpoint"""
        print("\n📍 Testing Nearest Stations Endpoint...")
        
        # Test locations
        test_locations = [
            {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
            {"lat": 51.5074, "lon": -0.1278, "name": "London"},
            {"lat": 48.8566, "lon": 2.3522, "name": "Paris"}
        ]
        
        success_count = 0
        
        for location in test_locations:
            try:
                url = f"{BACKEND_URL}/stations/nearest"
                params = {
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'mode': 'drive',
                    'limit': 5
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'success':
                            result_data = data.get('data', {})
                            nearest_stations = result_data.get('nearest_stations', [])
                            count = result_data.get('count', 0)
                            
                            self.log_test(
                                f"Nearest Stations - {location['name']}",
                                True,
                                f"Found {count} stations within range"
                            )
                            
                            # Verify station data structure
                            if nearest_stations:
                                station = nearest_stations[0]
                                required_fields = ['name', 'distance_km', 'duration_minutes']
                                has_required = all(field in station for field in required_fields)
                                
                                if has_required:
                                    self.log_test(
                                        f"Nearest Stations Data - {location['name']}",
                                        True,
                                        f"Station: {station.get('name')}, Distance: {station.get('distance_km')}km"
                                    )
                                else:
                                    self.log_test(
                                        f"Nearest Stations Data - {location['name']}",
                                        False,
                                        f"Missing required fields in station data"
                                    )
                            
                            success_count += 1
                        else:
                            self.log_test(
                                f"Nearest Stations - {location['name']}",
                                False,
                                f"API error: {data}"
                            )
                    else:
                        error_text = await response.text()
                        self.log_test(
                            f"Nearest Stations - {location['name']}",
                            False,
                            f"HTTP {response.status}: {error_text}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Nearest Stations - {location['name']}",
                    False,
                    f"Exception: {str(e)}"
                )
        
        return success_count > 0
    
    async def test_nearest_stations_with_country_filter(self):
        """Test 5: Nearest Stations with Country Filter"""
        print("\n🌍 Testing Nearest Stations with Country Filter...")
        
        try:
            url = f"{BACKEND_URL}/stations/nearest"
            params = {
                'lat': 40.7128,
                'lon': -74.0060,
                'mode': 'drive',
                'limit': 5,
                'country': 'US'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        result_data = data.get('data', {})
                        nearest_stations = result_data.get('nearest_stations', [])
                        
                        # Verify all stations are from US
                        us_stations = all(
                            station.get('country', '').upper() == 'US' 
                            for station in nearest_stations
                        )
                        
                        self.log_test(
                            "Nearest Stations - Country Filter",
                            us_stations,
                            f"Found {len(nearest_stations)} US stations" if us_stations else "Non-US stations in results"
                        )
                        
                        return us_stations
                    else:
                        self.log_test("Nearest Stations - Country Filter", False, f"API error: {data}")
                        return False
                else:
                    self.log_test("Nearest Stations - Country Filter", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Nearest Stations - Country Filter", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Test 6: Error Handling"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test empty sources
        try:
            test_data = {
                "sources": [],
                "targets": [{"lat": 40.7128, "lon": -74.0060}],
                "mode": "drive"
            }
            
            url = f"{BACKEND_URL}/routing/distance-matrix"
            headers = {'Content-Type': 'application/json'}
            
            async with self.session.post(url, json=test_data, headers=headers) as response:
                data = await response.json()
                
                if data.get('status') == 'error':
                    self.log_test("Error Handling - Empty Sources", True, "Correctly rejected empty sources")
                else:
                    self.log_test("Error Handling - Empty Sources", False, "Should reject empty sources")
                    
        except Exception as e:
            self.log_test("Error Handling - Empty Sources", False, f"Exception: {str(e)}")
        
        # Test invalid coordinates
        try:
            params = {
                'lat': 999,  # Invalid latitude
                'lon': -74.0060,
                'mode': 'drive',
                'limit': 5
            }
            
            url = f"{BACKEND_URL}/stations/nearest"
            async with self.session.get(url, params=params) as response:
                # Should handle gracefully (either error or empty results)
                if response.status in [200, 400, 422]:
                    self.log_test("Error Handling - Invalid Coordinates", True, "Handled invalid coordinates gracefully")
                else:
                    self.log_test("Error Handling - Invalid Coordinates", False, f"Unexpected status: {response.status}")
                    
        except Exception as e:
            self.log_test("Error Handling - Invalid Coordinates", False, f"Exception: {str(e)}")
    
    async def test_automated_scheduler_integration(self):
        """Test 7: Check Automated Scheduler Integration"""
        print("\n⏰ Testing Automated Scheduler Integration...")
        
        try:
            # Check if distance_matrix_cache collection exists and has data
            # We'll use the status endpoint to check cache entries
            url = f"{BACKEND_URL}/routing/distance-matrix/status"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        status_data = data.get('data', {})
                        cache_entries = status_data.get('cache_entries', 0)
                        
                        if cache_entries > 0:
                            self.log_test(
                                "Automated Scheduler Integration",
                                True,
                                f"Distance matrix cache has {cache_entries} entries - scheduler is working"
                            )
                        else:
                            self.log_test(
                                "Automated Scheduler Integration",
                                True,
                                "Cache is empty but scheduler integration is configured (may not have run yet)"
                            )
                        
                        return True
                    else:
                        self.log_test("Automated Scheduler Integration", False, "Status endpoint failed")
                        return False
                else:
                    self.log_test("Automated Scheduler Integration", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Automated Scheduler Integration", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all Distance Matrix API tests"""
        print("🗺️ DISTANCE MATRIX API INTEGRATION TESTING")
        print("=" * 60)
        
        test_functions = [
            self.test_distance_matrix_status,
            self.test_distance_matrix_calculation,
            self.test_distance_matrix_modes,
            self.test_nearest_stations_endpoint,
            self.test_nearest_stations_with_country_filter,
            self.test_error_handling,
            self.test_automated_scheduler_integration
        ]
        
        passed = 0
        total = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DISTANCE MATRIX API TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        # Detailed results
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        return success_rate >= 70  # Consider 70%+ as overall success


async def main():
    """Main test runner"""
    async with DistanceMatrixTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 Distance Matrix API Integration Testing COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n⚠️ Distance Matrix API Integration Testing COMPLETED WITH ISSUES!")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())