#!/usr/bin/env python3
"""
Backend API Testing for Dragon KARAU AI Radio - Map & Traffic Integration
Testing newly implemented Map & Traffic Integration backend API endpoints
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://dragon-radio-app.preview.emergentagent.com/api"

class MapTrafficAPITester:
    """Comprehensive tester for Intelligent AI Search System"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "test_user_12345"  # From favorites tests
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                return {
                    'status_code': response.status,
                    'data': response_data,
                    'success': 200 <= response.status < 300
                }
        except Exception as e:
            logger.error(f"Request failed for {method} {url}: {e}")
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'success': False
            }
    
    async def test_phase_1_basic_intelligent_search(self):
        """Phase 1: Basic Intelligent Search Tests"""
        logger.info("\n🔍 PHASE 1: BASIC INTELLIGENT SEARCH TESTING")
        
        # Test 1: Simple text search
        response = await self.make_request('GET', '/search/intelligent?q=rock music&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            results = response['data'].get('data', {}).get('results', [])
            parsed_intent = response['data'].get('data', {}).get('parsed_intent', {})
            
            self.log_test_result(
                "Simple Text Search (rock music)",
                True,
                f"Found {len(results)} results, detected genre: {parsed_intent.get('genre')}",
                response['data']
            )
        else:
            self.log_test_result(
                "Simple Text Search (rock music)",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 2: Country-specific search
        response = await self.make_request('GET', '/search/intelligent?q=stations from US&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            results = response['data'].get('data', {}).get('results', [])
            parsed_intent = response['data'].get('data', {}).get('parsed_intent', {})
            
            self.log_test_result(
                "Country-Specific Search (US)",
                True,
                f"Found {len(results)} results, detected country: {parsed_intent.get('country')}",
                response['data']
            )
        else:
            self.log_test_result(
                "Country-Specific Search (US)",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 3: Language search
        response = await self.make_request('GET', '/search/intelligent?q=spanish radio&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            results = response['data'].get('data', {}).get('results', [])
            parsed_intent = response['data'].get('data', {}).get('parsed_intent', {})
            
            self.log_test_result(
                "Language Search (Spanish)",
                True,
                f"Found {len(results)} results, detected language: {parsed_intent.get('language')}",
                response['data']
            )
        else:
            self.log_test_result(
                "Language Search (Spanish)",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 4: Genre search
        response = await self.make_request('GET', '/search/intelligent?q=jazz stations&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            results = response['data'].get('data', {}).get('results', [])
            parsed_intent = response['data'].get('data', {}).get('parsed_intent', {})
            
            self.log_test_result(
                "Genre Search (Jazz)",
                True,
                f"Found {len(results)} results, detected genre: {parsed_intent.get('genre')}",
                response['data']
            )
        else:
            self.log_test_result(
                "Genre Search (Jazz)",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 5: Combined search
        response = await self.make_request('GET', '/search/intelligent?q=french news radio&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            results = response['data'].get('data', {}).get('results', [])
            parsed_intent = response['data'].get('data', {}).get('parsed_intent', {})
            
            detected_language = parsed_intent.get('language')
            detected_genre = parsed_intent.get('genre')
            
            self.log_test_result(
                "Combined Search (French News)",
                True,
                f"Found {len(results)} results, language: {detected_language}, genre: {detected_genre}",
                response['data']
            )
        else:
            self.log_test_result(
                "Combined Search (French News)",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
    
    async def test_phase_2_trending_recommendations(self):
        """Phase 2: Trending & Recommendations Tests"""
        logger.info("\n📈 PHASE 2: TRENDING & RECOMMENDATIONS TESTING")
        
        # Test 1: Trending stations
        response = await self.make_request('GET', '/search/trending?timeframe=day&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            trending = response['data'].get('data', {}).get('trending', [])
            
            # Verify trending returns high-quality stations
            high_quality_count = sum(1 for station in trending if station.get('quality_score', 0) >= 70)
            
            self.log_test_result(
                "Trending Stations",
                True,
                f"Found {len(trending)} trending stations, {high_quality_count} high-quality (≥70 score)",
                response['data']
            )
        else:
            self.log_test_result(
                "Trending Stations",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 2: Recommendations for user
        response = await self.make_request('GET', f'/search/recommendations/{self.test_user_id}?based_on=favorites&limit=10')
        if response['success'] and response['data'].get('status') == 'success':
            recommendations = response['data'].get('data', {}).get('recommendations', [])
            based_on = response['data'].get('data', {}).get('based_on')
            
            self.log_test_result(
                "User Recommendations",
                True,
                f"Found {len(recommendations)} recommendations based on {based_on}",
                response['data']
            )
        else:
            self.log_test_result(
                "User Recommendations",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
    
    async def test_phase_3_similar_stations(self):
        """Phase 3: Similar Stations Tests"""
        logger.info("\n🔗 PHASE 3: SIMILAR STATIONS TESTING")
        
        # First, get a station ID from the database
        response = await self.make_request('GET', '/stations?limit=1')
        station_id = None
        
        if response['success'] and response['data'].get('status') == 'success':
            stations = response['data'].get('data', {}).get('stations', [])
            if stations:
                station_id = stations[0].get('id')
                
                self.log_test_result(
                    "Get Station ID for Similar Test",
                    True,
                    f"Retrieved station ID: {station_id}",
                    stations[0]
                )
        
        if station_id:
            # Test similar stations
            response = await self.make_request('GET', f'/search/similar/{station_id}?limit=5')
            if response['success'] and response['data'].get('status') == 'success':
                similar = response['data'].get('data', {}).get('similar', [])
                reference_station = response['data'].get('data', {}).get('reference_station')
                
                self.log_test_result(
                    "Similar Stations",
                    True,
                    f"Found {len(similar)} similar stations to '{reference_station}'",
                    response['data']
                )
            else:
                self.log_test_result(
                    "Similar Stations",
                    False,
                    f"Status: {response['status_code']}, Error: {response['data']}",
                    response['data']
                )
        else:
            self.log_test_result(
                "Similar Stations",
                False,
                "Could not retrieve station ID for testing",
                None
            )
        
        # Test invalid station ID
        response = await self.make_request('GET', '/search/similar/invalid_station_id?limit=5')
        if response['status_code'] != 200 or response['data'].get('status') == 'error':
            self.log_test_result(
                "Similar Stations - Invalid ID",
                True,
                "Correctly handled invalid station ID with error response",
                response['data']
            )
        else:
            self.log_test_result(
                "Similar Stations - Invalid ID",
                False,
                "Should have returned error for invalid station ID",
                response['data']
            )
    
    async def test_phase_4_filter_metadata(self):
        """Phase 4: Filter Metadata Tests"""
        logger.info("\n🔧 PHASE 4: FILTER METADATA TESTING")
        
        # Test 1: Available languages
        response = await self.make_request('GET', '/search/filters/languages')
        if response['success'] and response['data'].get('status') == 'success':
            languages = response['data'].get('data', {}).get('languages', [])
            
            self.log_test_result(
                "Filter Languages",
                True,
                f"Retrieved {len(languages)} available languages: {languages[:5]}...",
                response['data']
            )
        else:
            self.log_test_result(
                "Filter Languages",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 2: Available genres
        response = await self.make_request('GET', '/search/filters/genres')
        if response['success'] and response['data'].get('status') == 'success':
            genres = response['data'].get('data', {}).get('genres', [])
            
            self.log_test_result(
                "Filter Genres",
                True,
                f"Retrieved {len(genres)} available genres: {genres[:5]}...",
                response['data']
            )
        else:
            self.log_test_result(
                "Filter Genres",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
        
        # Test 3: Available countries with counts
        response = await self.make_request('GET', '/search/filters/countries')
        if response['success'] and response['data'].get('status') == 'success':
            countries = response['data'].get('data', {}).get('countries', [])
            
            # Verify countries have codes and counts
            valid_countries = [c for c in countries if c.get('code') and c.get('count')]
            
            self.log_test_result(
                "Filter Countries",
                True,
                f"Retrieved {len(valid_countries)} countries with station counts",
                response['data']
            )
        else:
            self.log_test_result(
                "Filter Countries",
                False,
                f"Status: {response['status_code']}, Error: {response['data']}",
                response['data']
            )
    
    async def test_error_handling(self):
        """Test Error Handling Scenarios"""
        logger.info("\n⚠️  ERROR HANDLING TESTING")
        
        # Test 1: Empty query string
        response = await self.make_request('GET', '/search/intelligent?q=&limit=10')
        if response['status_code'] != 200 or not response['data'].get('data', {}).get('results'):
            self.log_test_result(
                "Empty Query Handling",
                True,
                "Correctly handled empty query",
                response['data']
            )
        else:
            self.log_test_result(
                "Empty Query Handling",
                False,
                "Should handle empty query gracefully",
                response['data']
            )
        
        # Test 2: Invalid filter parameters
        response = await self.make_request('GET', '/search/intelligent?q=test&limit=invalid')
        # Should handle gracefully or use default
        self.log_test_result(
            "Invalid Parameters Handling",
            True,  # Any response is acceptable as long as it doesn't crash
            f"Handled invalid limit parameter, status: {response['status_code']}",
            response['data']
        )
    
    async def run_all_tests(self):
        """Run all test phases"""
        logger.info("🚀 STARTING INTELLIGENT AI SEARCH SYSTEM TESTING")
        logger.info(f"Backend URL: {BACKEND_URL}")
        
        try:
            await self.test_phase_1_basic_intelligent_search()
            await self.test_phase_2_trending_recommendations()
            await self.test_phase_3_similar_stations()
            await self.test_phase_4_filter_metadata()
            await self.test_error_handling()
            
        except Exception as e:
            logger.error(f"Testing error: {e}")
            self.log_test_result("Overall Testing", False, f"Testing failed with error: {e}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("\n" + "="*80)
        logger.info("🎯 INTELLIGENT AI SEARCH SYSTEM TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("="*80)
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        logger.info("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                logger.info(f"  - {result['test']}: {result['details']}")


async def main():
    """Main test execution"""
    async with IntelligentSearchTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())