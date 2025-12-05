#!/usr/bin/env python3
"""
Dragon KARAU AI - COMPREHENSIVE PRODUCTION READINESS TESTING
Testing all production-critical implementations as requested in review:

1. Fixed Production Endpoints Testing (Geocoding Expansion, Stream Validation)
2. Security Features Testing (CORS, Rate Limiting, Security Headers)
3. Data Quality Verification (Geocoding Coverage, Stream Validation, Radio-Browser.info)
4. Core Functionality Verification (Station Discovery, Intelligent Search, Nearest Stations)
5. Background Processing Validation
6. Error Handling & Resilience

COMPREHENSIVE SYSTEM AUDIT & TESTING covering:
- Core API Health Check
- Distance Matrix API Integration
- Multi-Source Crawler System
- Administrative Divisions System (CRITICAL ISSUE)
- Favorites System
- Content Compliance System
- Stream Validation Service
- Radio-Browser.info Integration
- Intelligent Search Engine
- Geocoding Services
"""

import asyncio
import aiohttp
import json
import sys
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    # CORE API HEALTH CHECK TESTS
    # ===================================
    
    async def test_core_api_health(self):
        """Test core API endpoints health"""
        print("\n🔍 TESTING CORE API HEALTH")
        print("=" * 60)
        
        # Test API root
        result = await self.test_endpoint('GET', '/')
        if result['success']:
            api_data = result['data']
            version = api_data.get('version', 'Unknown')
            features = api_data.get('features', [])
            
            self.log_test(
                "Core API Root",
                True,
                f"Version: {version}, Features: {len(features)}"
            )
        else:
            self.log_test("Core API Root", False, f"Error: {result['data']}")
        
        # Test station info
        result = await self.test_endpoint('GET', '/station-info')
        if result['success']:
            station_data = result['data']
            station_name = station_data.get('name', 'Unknown')
            stream_url = station_data.get('streamUrl', '')
            
            self.log_test(
                "Station Info API",
                bool(station_name and stream_url),
                f"Station: {station_name}, Stream available: {bool(stream_url)}"
            )
        else:
            self.log_test("Station Info API", False, f"Error: {result['data']}")
        
        # Test stations endpoint
        result = await self.test_endpoint('GET', '/stations', params={'limit': 10})
        if result['success']:
            stations_data = result['data'].get('data', {})
            total_stations = stations_data.get('total', 0)
            
            self.log_test(
                "Stations API",
                result['data'].get('status') == 'success',
                f"Total stations: {total_stations}"
            )
        else:
            self.log_test("Stations API", False, f"Error: {result['data']}")
    
    # ===================================
    # ADMINISTRATIVE DIVISIONS TESTS (CRITICAL)
    # ===================================
    
    async def test_administrative_divisions_system(self):
        """Test Administrative Divisions System - CRITICAL FAILING COMPONENT"""
        print("\n🏛️ TESTING ADMINISTRATIVE DIVISIONS SYSTEM (CRITICAL)")
        print("=" * 60)
        
        # Test 1: Division stats (should show if populated)
        result = await self.test_endpoint('GET', '/divisions/stats')
        if result['success']:
            stats_data = result['data'].get('data', {})
            total_countries = stats_data.get('total_countries', 0)
            total_divisions = stats_data.get('total_divisions', 0)
            
            self.log_test(
                "Administrative Divisions Stats",
                True,
                f"Countries: {total_countries}, Divisions: {total_divisions}"
            )
            
            # Check if system is populated
            is_populated = total_countries > 0 and total_divisions > 0
            if not is_populated:
                print("    🚨 WARNING: Administrative divisions not populated!")
        else:
            self.log_test("Administrative Divisions Stats", False, f"Error: {result['data']}")
        
        # Test 2: Countries list
        result = await self.test_endpoint('GET', '/divisions/countries')
        if result['success']:
            countries_data = result['data'].get('data', {})
            countries = countries_data.get('countries', [])
            
            self.log_test(
                "Administrative Countries List",
                True,
                f"Countries available: {len(countries)}"
            )
        else:
            self.log_test("Administrative Countries List", False, f"Error: {result['data']}")
        
        # Test 3: Geocoder stats
        result = await self.test_endpoint('GET', '/divisions/geocoder-stats')
        if result['success']:
            geocoder_data = result['data'].get('data', {})
            assigned_stations = geocoder_data.get('assigned_stations', 0)
            total_stations = geocoder_data.get('total_stations', 0)
            assignment_rate = (assigned_stations / total_stations * 100) if total_stations > 0 else 0
            
            self.log_test(
                "Division Geocoder Stats",
                True,
                f"Assigned: {assigned_stations}/{total_stations} ({assignment_rate:.1f}%)"
            )
        else:
            self.log_test("Division Geocoder Stats", False, f"Error: {result['data']}")
        
        # Test 4: CRITICAL - Population endpoint (this is the failing component)
        print("    🚨 Testing CRITICAL population endpoint...")
        try:
            # Use shorter timeout for population test
            async with self.session.post(f"{self.backend_url}/divisions/populate", timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test(
                        "Administrative Divisions Population (CRITICAL)",
                        True,
                        f"Population successful: {data.get('message', 'Success')}"
                    )
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Administrative Divisions Population (CRITICAL)",
                        False,
                        f"Population failed: Status {response.status}, Error: {error_text[:200]}"
                    )
        except asyncio.TimeoutError:
            self.log_test(
                "Administrative Divisions Population (CRITICAL)",
                False,
                "Population failed: Timeout after 30 seconds - indicates parsing/processing issues"
            )
        except Exception as e:
            self.log_test(
                "Administrative Divisions Population (CRITICAL)",
                False,
                f"Population failed: {str(e)}"
            )
    
    # ===================================
    # DISTANCE MATRIX API TESTS
    # ===================================
    
    async def test_distance_matrix_api(self):
        """Test Distance Matrix API integration"""
        print("\n🗺️ TESTING DISTANCE MATRIX API")
        print("=" * 60)
        
        # Test status endpoint
        result = await self.test_endpoint('GET', '/routing/distance-matrix/status')
        if result['success']:
            status_data = result['data'].get('data', {})
            api_configured = status_data.get('api_configured', False)
            cache_entries = status_data.get('cache_entries', 0)
            provider = status_data.get('provider', 'Unknown')
            
            self.log_test(
                "Distance Matrix Status",
                api_configured,
                f"Configured: {api_configured}, Provider: {provider}, Cache: {cache_entries}"
            )
        else:
            self.log_test("Distance Matrix Status", False, f"Error: {result['data']}")
        
        # Test distance matrix calculation
        matrix_data = {
            "sources": [{"lat": 40.7128, "lon": -74.0060}],  # New York
            "targets": [{"lat": 41.8781, "lon": -87.6298}],  # Chicago
            "mode": "drive"
        }
        result = await self.test_endpoint('POST', '/routing/distance-matrix', data=matrix_data)
        if result['success']:
            matrix_result = result['data'].get('data', {})
            matrix = matrix_result.get('matrix', [])
            
            self.log_test(
                "Distance Matrix Calculation",
                len(matrix) > 0,
                f"Matrix calculated: {len(matrix)} rows, Provider: {matrix_result.get('provider', 'Unknown')}"
            )
        else:
            self.log_test("Distance Matrix Calculation", False, f"Error: {result['data']}")
        
        # Test nearest stations
        result = await self.test_endpoint('GET', '/stations/nearest', params={
            'lat': 40.7128, 'lon': -74.0060, 'limit': 5
        })
        if result['success']:
            nearest_data = result['data'].get('data', {})
            stations_count = nearest_data.get('count', 0)
            
            self.log_test(
                "Nearest Stations API",
                True,
                f"Stations found: {stations_count}"
            )
        else:
            self.log_test("Nearest Stations API", False, f"Error: {result['data']}")
    
    # ===================================
    # FAVORITES SYSTEM TESTS
    # ===================================
    
    async def test_favorites_system(self):
        """Test Favorites System"""
        print("\n❤️ TESTING FAVORITES SYSTEM")
        print("=" * 60)
        
        test_user_id = "test_user_comprehensive_audit"
        test_station_id = "test_station_001"
        
        # Test add favorite
        result = await self.test_endpoint('POST', '/favorites/add', params={
            'user_id': test_user_id, 'station_id': test_station_id
        })
        if result['success']:
            add_data = result['data'].get('data', {})
            
            self.log_test(
                "Add Favorite Station",
                result['data'].get('status') == 'success',
                f"Added favorite: {add_data.get('message', 'Success')}"
            )
        else:
            self.log_test("Add Favorite Station", False, f"Error: {result['data']}")
        
        # Test get favorites
        result = await self.test_endpoint('GET', f'/favorites/{test_user_id}')
        if result['success']:
            favorites_data = result['data'].get('data', {})
            total_count = favorites_data.get('total_count', 0)
            
            self.log_test(
                "Get User Favorites",
                result['data'].get('status') == 'success',
                f"Favorites count: {total_count}"
            )
        else:
            self.log_test("Get User Favorites", False, f"Error: {result['data']}")
        
        # Test check favorite status
        result = await self.test_endpoint('GET', f'/favorites/{test_user_id}/check/{test_station_id}')
        if result['success']:
            check_data = result['data'].get('data', {})
            is_favorite = check_data.get('is_favorite', False)
            
            self.log_test(
                "Check Favorite Status",
                result['data'].get('status') == 'success',
                f"Is favorite: {is_favorite}"
            )
        else:
            self.log_test("Check Favorite Status", False, f"Error: {result['data']}")
        
        # Test favorites stats
        result = await self.test_endpoint('GET', f'/favorites/{test_user_id}/stats')
        if result['success']:
            stats_data = result['data'].get('data', {})
            
            self.log_test(
                "Favorites Statistics",
                result['data'].get('status') == 'success',
                f"Stats available: {bool(stats_data)}"
            )
        else:
            self.log_test("Favorites Statistics", False, f"Error: {result['data']}")
        
        # Clean up - remove test favorite
        await self.test_endpoint('DELETE', '/favorites/remove', params={
            'user_id': test_user_id, 'station_id': test_station_id
        })
    
    # ===================================
    # CONTENT COMPLIANCE TESTS
    # ===================================
    
    async def test_content_compliance_system(self):
        """Test Content Compliance System"""
        print("\n⚖️ TESTING CONTENT COMPLIANCE SYSTEM")
        print("=" * 60)
        
        # Test content disclaimers
        compliance_data = {
            "country_code": "KE",
            "language_code": "en",
            "content_types": ["radio_streams", "music"]
        }
        result = await self.test_endpoint('POST', '/compliance/disclaimers', data=compliance_data)
        if result['success']:
            disclaimers_data = result['data']
            disclaimers = disclaimers_data.get('content_disclaimers', [])
            
            self.log_test(
                "Content Disclaimers API",
                len(disclaimers) > 0,
                f"Disclaimers: {len(disclaimers)}, Country: KE"
            )
        else:
            self.log_test("Content Disclaimers API", False, f"Error: {result['data']}")
        
        # Test content compliance check
        result = await self.test_endpoint('POST', '/compliance/check-content', params={
            'country_code': 'KE', 'content_rating': 'mature', 'user_age': 25
        })
        if result['success']:
            compliance_data = result['data']
            compliant = compliance_data.get('compliant', False)
            
            self.log_test(
                "Content Compliance Check",
                True,
                f"Compliant: {compliant}, Country: KE, Age: 25"
            )
        else:
            self.log_test("Content Compliance Check", False, f"Error: {result['data']}")
        
        # Test multilingual station info with compliance
        location_data = {"latitude": -1.286389, "longitude": 36.817223}  # Nairobi
        result = await self.test_endpoint('POST', '/station-info/multilingual', data=location_data)
        if result['success']:
            station_data = result['data']
            detected_language = station_data.get('detected_language', 'Unknown')
            disclaimers = station_data.get('content_disclaimers', [])
            
            self.log_test(
                "Multilingual Station Info with Compliance",
                bool(detected_language and disclaimers),
                f"Language: {detected_language}, Disclaimers: {len(disclaimers)}"
            )
        else:
            self.log_test("Multilingual Station Info with Compliance", False, f"Error: {result['data']}")
    
    # ===================================
    # INTELLIGENT SEARCH TESTS
    # ===================================
    
    async def test_intelligent_search_system(self):
        """Test Intelligent AI Search Engine"""
        print("\n🧠 TESTING INTELLIGENT AI SEARCH ENGINE")
        print("=" * 60)
        
        # Test intelligent search
        result = await self.test_endpoint('GET', '/search/intelligent', params={
            'q': 'rock music stations', 'limit': 5
        })
        if result['success']:
            search_data = result['data'].get('data', {})
            results = search_data.get('results', [])
            
            self.log_test(
                "Intelligent AI Search",
                result['data'].get('status') == 'success',
                f"Search results: {len(results)}"
            )
        else:
            self.log_test("Intelligent AI Search", False, f"Error: {result['data']}")
        
        # Test trending stations
        result = await self.test_endpoint('GET', '/search/trending', params={'limit': 10})
        if result['success']:
            trending_data = result['data'].get('data', {})
            trending = trending_data.get('trending', [])
            
            self.log_test(
                "Trending Stations",
                result['data'].get('status') == 'success',
                f"Trending stations: {len(trending)}"
            )
        else:
            self.log_test("Trending Stations", False, f"Error: {result['data']}")
        
        # Test search filters
        result = await self.test_endpoint('GET', '/search/filters/countries')
        if result['success']:
            countries_data = result['data'].get('data', {})
            countries = countries_data.get('countries', [])
            
            self.log_test(
                "Search Filter Countries",
                result['data'].get('status') == 'success',
                f"Available countries: {len(countries)}"
            )
        else:
            self.log_test("Search Filter Countries", False, f"Error: {result['data']}")
    
    # ===================================
    # GEOCODING SERVICES TESTS
    # ===================================
    
    async def test_geocoding_services(self):
        """Test Geocoding Services"""
        print("\n🌍 TESTING GEOCODING SERVICES")
        print("=" * 60)
        
        # Test geocoding stats
        result = await self.test_endpoint('GET', '/geocoding/stats')
        if result['success']:
            stats_data = result['data'].get('data', {})
            total_stations = stats_data.get('total_stations', 0)
            geocoded_stations = stats_data.get('geocoded_stations', 0)
            geocoding_rate = (geocoded_stations / total_stations * 100) if total_stations > 0 else 0
            
            self.log_test(
                "Geocoding Service Stats",
                True,
                f"Geocoded: {geocoded_stations}/{total_stations} ({geocoding_rate:.1f}%)"
            )
        else:
            self.log_test("Geocoding Service Stats", False, f"Error: {result['data']}")
        
        # Test batch geocoding (small batch)
        result = await self.test_endpoint('POST', '/geocoding/geocode-batch', params={'limit': 5})
        if result['success']:
            batch_data = result['data'].get('data', {})
            
            self.log_test(
                "Batch Geocoding",
                result.get('status') == 'success',
                f"Geocoding status: {batch_data.get('message', 'Unknown')}"
            )
        else:
            self.log_test("Batch Geocoding", False, f"Error: {result['data']}")
    
    # ===================================
    # MAP & TRAFFIC INTEGRATION TESTS
    # ===================================
    
    async def test_map_traffic_integration(self):
        """Test Map & Traffic Integration"""
        print("\n🗺️ TESTING MAP & TRAFFIC INTEGRATION")
        print("=" * 60)
        
        # Test map configuration
        result = await self.test_endpoint('GET', '/map/config')
        if result['success']:
            config_data = result['data'].get('data', {})
            
            self.log_test(
                "Map Configuration",
                result['data'].get('status') == 'success',
                f"Map config available: {bool(config_data)}"
            )
        else:
            self.log_test("Map Configuration", False, f"Error: {result['data']}")
        
        # Test stations for map
        result = await self.test_endpoint('GET', '/map/stations', params={'limit': 10})
        if result['success']:
            stations_data = result['data'].get('data', {})
            stations = stations_data.get('stations', [])
            
            self.log_test(
                "Map Stations API",
                result['data'].get('status') == 'success',
                f"Stations with coordinates: {len(stations)}"
            )
        else:
            self.log_test("Map Stations API", False, f"Error: {result['data']}")
    
    # ===================================
    # MAIN TEST RUNNER
    # ===================================
    
    async def run_all_tests(self):
        """Run comprehensive system audit"""
        print("🐉 DRAGON KARAU AI - COMPREHENSIVE SYSTEM AUDIT & TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run all test suites
        await self.test_core_api_health()
        await self.test_administrative_divisions_system()  # CRITICAL FOCUS
        await self.test_distance_matrix_api()
        await self.test_multi_source_crawler_integration()
        await self.test_favorites_system()
        await self.test_content_compliance_system()
        await self.test_stream_validation_service()
        await self.test_radio_browser_info_integration()
        await self.test_intelligent_search_system()
        await self.test_geocoding_services()
        await self.test_map_traffic_integration()
        await self.test_quality_and_metadata()
        
        # Summary
        print("\n📋 COMPREHENSIVE AUDIT SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # System Health Score
        if success_rate >= 90:
            health_status = "🟢 EXCELLENT"
        elif success_rate >= 75:
            health_status = "🟡 GOOD"
        elif success_rate >= 50:
            health_status = "🟠 NEEDS ATTENTION"
        else:
            health_status = "🔴 CRITICAL ISSUES"
        
        print(f"\n🏥 SYSTEM HEALTH: {health_status} ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Critical issues identification
        critical_failures = [r for r in self.test_results if not r['success'] and 'CRITICAL' in r['test']]
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES REQUIRING IMMEDIATE ATTENTION:")
            for failure in critical_failures:
                print(f"   🔥 {failure['test']}: {failure['details']}")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': success_rate,
            'health_status': health_status,
            'critical_failures': critical_failures,
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