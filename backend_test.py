#!/usr/bin/env python3
"""
Backend API Testing Suite for Dragon KARAU AI - Intelligent Search System
Tests all AI Search endpoints with comprehensive scenarios
"""

import asyncio
import aiohttp
import json
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from frontend .env
BACKEND_URL = "https://dragon-radio-app.preview.emergentagent.com/api"

class IntelligentSearchTester:
    """Comprehensive tester for Intelligent AI Search System"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "test_user_12345"  # From favorites tests
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    async def get_sample_stations(self):
        """Get sample stations from database for testing"""
        try:
            # Get some stations from different countries for testing
            from motor.motor_asyncio import AsyncIOMotorClient
            load_dotenv(ROOT_DIR / 'backend' / '.env')
            
            client = AsyncIOMotorClient(os.environ['MONGO_URL'])
            db = client[os.environ['DB_NAME']]
            
            # Get stations from different countries
            stations = await db.radio_stations.find({}).limit(10).to_list(length=10)
            
            self.test_stations = []
            for station in stations:
                if station.get('id') and station.get('name'):
                    self.test_stations.append({
                        'id': station['id'],
                        'name': station['name'],
                        'country': station.get('country', 'Unknown')
                    })
            
            client.close()
            print(f"📡 Found {len(self.test_stations)} test stations")
            for i, station in enumerate(self.test_stations[:3]):
                print(f"   {i+1}. {station['name']} ({station['country']}) - ID: {station['id']}")
            
            return len(self.test_stations) > 0
            
        except Exception as e:
            print(f"❌ Failed to get sample stations: {e}")
            return False
    
    async def test_add_favorite(self):
        """Test POST /api/favorites/add"""
        if not self.test_stations:
            self.log_result("Add Favorite", False, "No test stations available")
            return
        
        station = self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/add"
            params = {
                'user_id': self.test_user_id,
                'station_id': station['id']
            }
            
            async with self.session.post(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    self.log_result("Add Favorite", True, f"Added {station['name']} to favorites")
                else:
                    self.log_result("Add Favorite", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Add Favorite", False, f"Exception: {e}")
    
    async def test_add_duplicate_favorite(self):
        """Test adding duplicate favorite (should handle gracefully)"""
        if not self.test_stations:
            self.log_result("Add Duplicate Favorite", False, "No test stations available")
            return
        
        station = self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/add"
            params = {
                'user_id': self.test_user_id,
                'station_id': station['id']
            }
            
            async with self.session.post(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    # Should indicate already exists
                    if data.get('data', {}).get('already_exists'):
                        self.log_result("Add Duplicate Favorite", True, "Correctly handled duplicate")
                    else:
                        self.log_result("Add Duplicate Favorite", True, "Added or already exists")
                else:
                    self.log_result("Add Duplicate Favorite", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Add Duplicate Favorite", False, f"Exception: {e}")
    
    async def test_get_favorites_list(self):
        """Test GET /api/favorites/{user_id}"""
        try:
            url = f"{API_BASE}/favorites/{self.test_user_id}"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    favorites = data.get('data', {}).get('favorites', [])
                    total_count = data.get('data', {}).get('total_count', 0)
                    
                    self.log_result("Get Favorites List", True, f"Retrieved {total_count} favorites")
                    
                    # Print some details
                    if favorites:
                        print(f"   First favorite: {favorites[0].get('name')} ({favorites[0].get('country')})")
                else:
                    self.log_result("Get Favorites List", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Get Favorites List", False, f"Exception: {e}")
    
    async def test_check_favorite_status_true(self):
        """Test GET /api/favorites/{user_id}/check/{station_id} - should return true"""
        if not self.test_stations:
            self.log_result("Check Favorite Status (True)", False, "No test stations available")
            return
        
        station = self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/{self.test_user_id}/check/{station['id']}"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    is_favorite = data.get('data', {}).get('is_favorite', False)
                    
                    if is_favorite:
                        self.log_result("Check Favorite Status (True)", True, f"{station['name']} is favorited")
                    else:
                        self.log_result("Check Favorite Status (True)", False, f"{station['name']} should be favorited but isn't")
                else:
                    self.log_result("Check Favorite Status (True)", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Check Favorite Status (True)", False, f"Exception: {e}")
    
    async def test_update_play_stats(self):
        """Test POST /api/favorites/play-stats"""
        if not self.test_stations:
            self.log_result("Update Play Stats", False, "No test stations available")
            return
        
        station = self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/play-stats"
            params = {
                'user_id': self.test_user_id,
                'station_id': station['id']
            }
            
            async with self.session.post(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    self.log_result("Update Play Stats", True, f"Updated play stats for {station['name']}")
                else:
                    self.log_result("Update Play Stats", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Update Play Stats", False, f"Exception: {e}")
    
    async def test_add_multiple_favorites(self):
        """Add multiple favorites from different countries"""
        if len(self.test_stations) < 3:
            self.log_result("Add Multiple Favorites", False, "Need at least 3 test stations")
            return
        
        success_count = 0
        
        for i in range(1, min(4, len(self.test_stations))):  # Add 3 more stations
            station = self.test_stations[i]
            
            try:
                url = f"{API_BASE}/favorites/add"
                params = {
                    'user_id': self.test_user_id,
                    'station_id': station['id']
                }
                
                async with self.session.post(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and data.get('status') == 'success':
                        success_count += 1
                        print(f"   Added: {station['name']} ({station['country']})")
                        
            except Exception as e:
                print(f"   Failed to add {station['name']}: {e}")
        
        if success_count >= 2:
            self.log_result("Add Multiple Favorites", True, f"Added {success_count} additional favorites")
        else:
            self.log_result("Add Multiple Favorites", False, f"Only added {success_count} favorites")
    
    async def test_get_user_statistics(self):
        """Test GET /api/favorites/{user_id}/stats"""
        try:
            url = f"{API_BASE}/favorites/{self.test_user_id}/stats"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    stats = data.get('data', {})
                    
                    total_favorites = stats.get('total_favorites', 0)
                    countries_represented = stats.get('countries_represented', 0)
                    country_breakdown = stats.get('country_breakdown', [])
                    
                    self.log_result("Get User Statistics", True, 
                                  f"Stats: {total_favorites} favorites, {countries_represented} countries")
                    
                    # Print country breakdown
                    if country_breakdown:
                        print("   Country breakdown:")
                        for country_stat in country_breakdown[:3]:
                            print(f"     {country_stat.get('country', 'Unknown')}: {country_stat.get('count', 0)} stations")
                else:
                    self.log_result("Get User Statistics", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Get User Statistics", False, f"Exception: {e}")
    
    async def test_remove_favorite(self):
        """Test DELETE /api/favorites/remove"""
        if not self.test_stations:
            self.log_result("Remove Favorite", False, "No test stations available")
            return
        
        # Remove the last added station
        station = self.test_stations[-1] if len(self.test_stations) > 1 else self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/remove"
            params = {
                'user_id': self.test_user_id,
                'station_id': station['id']
            }
            
            async with self.session.delete(url, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    self.log_result("Remove Favorite", True, f"Removed {station['name']} from favorites")
                else:
                    self.log_result("Remove Favorite", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Remove Favorite", False, f"Exception: {e}")
    
    async def test_check_favorite_status_false(self):
        """Test checking favorite status for removed station (should return false)"""
        if not self.test_stations:
            self.log_result("Check Favorite Status (False)", False, "No test stations available")
            return
        
        # Check the station we just removed
        station = self.test_stations[-1] if len(self.test_stations) > 1 else self.test_stations[0]
        
        try:
            url = f"{API_BASE}/favorites/{self.test_user_id}/check/{station['id']}"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    is_favorite = data.get('data', {}).get('is_favorite', False)
                    
                    if not is_favorite:
                        self.log_result("Check Favorite Status (False)", True, f"{station['name']} correctly not favorited")
                    else:
                        self.log_result("Check Favorite Status (False)", False, f"{station['name']} should not be favorited")
                else:
                    self.log_result("Check Favorite Status (False)", False, f"Status: {response.status}, Data: {data}")
                    
        except Exception as e:
            self.log_result("Check Favorite Status (False)", False, f"Exception: {e}")
    
    async def test_error_cases(self):
        """Test error handling for invalid inputs"""
        error_tests = [
            {
                'name': 'Invalid Station ID',
                'url': f"{API_BASE}/favorites/add",
                'params': {'user_id': self.test_user_id, 'station_id': 'invalid-station-id'},
                'method': 'POST'
            },
            {
                'name': 'Empty User ID',
                'url': f"{API_BASE}/favorites/add",
                'params': {'user_id': '', 'station_id': self.test_stations[0]['id'] if self.test_stations else 'test'},
                'method': 'POST'
            },
            {
                'name': 'Non-existent User Favorites',
                'url': f"{API_BASE}/favorites/non_existent_user_999",
                'params': {},
                'method': 'GET'
            }
        ]
        
        passed_error_tests = 0
        
        for test in error_tests:
            try:
                if test['method'] == 'POST':
                    async with self.session.post(test['url'], params=test['params']) as response:
                        data = await response.json()
                        
                        # Should handle error gracefully (either 200 with error status or 4xx)
                        if response.status in [200, 400, 404, 422]:
                            if response.status == 200:
                                # Check if error is properly indicated in response
                                if data.get('status') == 'error' or not data.get('data', {}).get('success', True):
                                    passed_error_tests += 1
                                    print(f"   ✅ {test['name']}: Properly handled error")
                                else:
                                    print(f"   ❌ {test['name']}: Should have returned error")
                            else:
                                passed_error_tests += 1
                                print(f"   ✅ {test['name']}: Returned appropriate HTTP error {response.status}")
                        else:
                            print(f"   ❌ {test['name']}: Unexpected status {response.status}")
                            
                elif test['method'] == 'GET':
                    async with self.session.get(test['url']) as response:
                        data = await response.json()
                        
                        # Should return empty list or handle gracefully
                        if response.status == 200:
                            if data.get('status') == 'success':
                                favorites = data.get('data', {}).get('favorites', [])
                                if len(favorites) == 0:
                                    passed_error_tests += 1
                                    print(f"   ✅ {test['name']}: Returned empty favorites list")
                                else:
                                    print(f"   ❌ {test['name']}: Should return empty list for non-existent user")
                            else:
                                passed_error_tests += 1
                                print(f"   ✅ {test['name']}: Properly indicated error")
                        else:
                            print(f"   ❌ {test['name']}: Unexpected status {response.status}")
                            
            except Exception as e:
                print(f"   ❌ {test['name']}: Exception {e}")
        
        if passed_error_tests >= 2:
            self.log_result("Error Handling", True, f"Passed {passed_error_tests}/3 error tests")
        else:
            self.log_result("Error Handling", False, f"Only passed {passed_error_tests}/3 error tests")
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🎵 STARTING FAVORITES SYSTEM BACKEND TESTING")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Setup
            print("\n📋 SETUP PHASE")
            if not await self.get_sample_stations():
                print("❌ Cannot proceed without test stations")
                return
            
            # Core functionality tests
            print("\n🔧 CORE FUNCTIONALITY TESTS")
            await self.test_add_favorite()
            await self.test_add_duplicate_favorite()
            await self.test_get_favorites_list()
            await self.test_check_favorite_status_true()
            await self.test_update_play_stats()
            
            # Extended functionality tests
            print("\n📊 EXTENDED FUNCTIONALITY TESTS")
            await self.test_add_multiple_favorites()
            await self.test_get_user_statistics()
            
            # Removal tests
            print("\n🗑️ REMOVAL TESTS")
            await self.test_remove_favorite()
            await self.test_check_favorite_status_false()
            
            # Error handling tests
            print("\n⚠️ ERROR HANDLING TESTS")
            await self.test_error_cases()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 FAVORITES SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 FAVORITES SYSTEM BACKEND: EXCELLENT PERFORMANCE!")
        elif success_rate >= 60:
            print("✅ FAVORITES SYSTEM BACKEND: GOOD PERFORMANCE")
        else:
            print("⚠️ FAVORITES SYSTEM BACKEND: NEEDS ATTENTION")
        
        return self.results


async def main():
    """Main test execution"""
    tester = FavoritesSystemTester()
    results = await tester.run_all_tests()
    
    # Return appropriate exit code
    if results['failed'] == 0:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())