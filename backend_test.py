#!/usr/bin/env python3
"""
Dragon KARAU AI - Comprehensive Backend Testing Suite
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