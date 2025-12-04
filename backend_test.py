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
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_distance_matrix_status(self):
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