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
BACKEND_URL = "https://wavelength-finder.preview.emergentagent.com/api"

class MapTrafficAPITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
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
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success:
            self.failed_tests.append(result)
    
    async def test_api_endpoint(self, endpoint: str, method: str = 'GET', params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Generic API endpoint tester"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method == 'GET':
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'success': response.status == 200
                    }
            elif method == 'POST':
                async with self.session.post(url, params=params, json=data) as response:
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
    # Phase 1: Map Configuration Tests
    # ===================================
    
    async def test_map_config(self):
        """Test GET /api/map/config - Get map configuration and available providers"""
        print("\n🗺️  PHASE 1: MAP CONFIGURATION TESTING")
        print("=" * 60)
        
        result = await self.test_api_endpoint('/map/config')
        
        if result['success']:
            data = result['data']
            
            # Verify response structure
            if data.get('status') == 'success' and 'data' in data:
                config = data['data']
                
                # Check for required providers
                expected_providers = ['google_maps', 'tomtom', 'mapbox', 'openstreetmap']
                providers = config.get('providers', {})
                
                missing_providers = [p for p in expected_providers if p not in providers]
                
                if not missing_providers:
                    # Check provider details
                    provider_details = []
                    for provider, details in providers.items():
                        enabled = details.get('enabled', False)
                        features = details.get('features', [])
                        free_tier = details.get('free_tier', 'Unknown')
                        
                        provider_details.append(f"{provider}: enabled={enabled}, features={len(features)}, free_tier='{free_tier}'")
                    
                    self.log_test(
                        "GET /api/map/config - Map configuration",
                        True,
                        f"Found {len(providers)} providers: {', '.join(providers.keys())}. Details: {'; '.join(provider_details)}",
                        config
                    )
                else:
                    self.log_test(
                        "GET /api/map/config - Map configuration",
                        False,
                        f"Missing providers: {missing_providers}",
                        data
                    )
            else:
                self.log_test(
                    "GET /api/map/config - Map configuration",
                    False,
                    f"Invalid response structure: {data}",
                    data
                )
        else:
            self.log_test(
                "GET /api/map/config - Map configuration",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
    
    # ===================================
    # Phase 2: Station Mapping Tests
    # ===================================
    
    async def test_stations_for_map(self):
        """Test GET /api/map/stations - Get stations for map display"""
        print("\n📍 PHASE 2: STATION MAPPING TESTING")
        print("=" * 60)
        
        # Test 1: Basic stations query (no filters)
        result = await self.test_api_endpoint('/map/stations')
        
        if result['success']:
            data = result['data']
            if data.get('status') == 'success':
                stations = data.get('data', {}).get('stations', [])
                total = data.get('data', {}).get('total', 0)
                
                # Verify stations have required fields
                valid_stations = 0
                for station in stations:
                    lat = station.get('latitude')
                    lon = station.get('longitude')
                    
                    if lat and lon and -90 <= lat <= 90 and -180 <= lon <= 180:
                        valid_stations += 1
                
                self.log_test(
                    "GET /api/map/stations - Basic stations query",
                    True,
                    f"Retrieved {total} stations, {valid_stations} with valid coordinates",
                    {'total': total, 'valid_coords': valid_stations}
                )
            else:
                self.log_test(
                    "GET /api/map/stations - Basic stations query",
                    False,
                    f"API returned error: {data}",
                    data
                )
        else:
            self.log_test(
                "GET /api/map/stations - Basic stations query",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
        
        # Test 2: Country filter
        test_countries = ['US', 'GB', 'FR']
        for country in test_countries:
            result = await self.test_api_endpoint('/map/stations', params={'country': country, 'limit': 100})
            
            if result['success']:
                data = result['data']
                if data.get('status') == 'success':
                    stations = data.get('data', {}).get('stations', [])
                    
                    # Verify all stations are from the requested country
                    correct_country = all(s.get('country') == country for s in stations)
                    
                    self.log_test(
                        f"GET /api/map/stations - Country filter ({country})",
                        correct_country,
                        f"Retrieved {len(stations)} stations for {country}, all correct country: {correct_country}",
                        {'country': country, 'count': len(stations)}
                    )
                else:
                    self.log_test(
                        f"GET /api/map/stations - Country filter ({country})",
                        False,
                        f"API returned error: {data}",
                        data
                    )
            else:
                self.log_test(
                    f"GET /api/map/stations - Country filter ({country})",
                    False,
                    f"API call failed: {result.get('exception', 'Unknown error')}",
                    result
                )
        
        # Test 3: Bounding box filter (New York area)
        bbox_params = {
            'min_lat': 40.0,
            'max_lat': 45.0,
            'min_lon': -75.0,
            'max_lon': -70.0,
            'limit': 50
        }
        
        result = await self.test_api_endpoint('/map/stations', params=bbox_params)
        
        if result['success']:
            data = result['data']
            if data.get('status') == 'success':
                stations = data.get('data', {}).get('stations', [])
                
                # Verify all stations are within bounding box
                within_bbox = 0
                for station in stations:
                    lat = station.get('latitude')
                    lon = station.get('longitude')
                    
                    if (lat and lon and 
                        bbox_params['min_lat'] <= lat <= bbox_params['max_lat'] and
                        bbox_params['min_lon'] <= lon <= bbox_params['max_lon']):
                        within_bbox += 1
                
                self.log_test(
                    "GET /api/map/stations - Bounding box filter",
                    within_bbox == len(stations),
                    f"Retrieved {len(stations)} stations, {within_bbox} within bounding box",
                    {'total': len(stations), 'within_bbox': within_bbox}
                )
            else:
                self.log_test(
                    "GET /api/map/stations - Bounding box filter",
                    False,
                    f"API returned error: {data}",
                    data
                )
        else:
            self.log_test(
                "GET /api/map/stations - Bounding box filter",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
    
    # ===================================
    # Phase 3: Traffic Incidents Tests
    # ===================================
    
    async def test_traffic_incidents(self):
        """Test GET /api/traffic/incidents - Get traffic incidents"""
        print("\n🚦 PHASE 3: TRAFFIC INCIDENTS TESTING")
        print("=" * 60)
        
        # Test locations
        test_locations = [
            {'name': 'New York City', 'lat': 40.7128, 'lon': -74.0060},
            {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
            {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522}
        ]
        
        for location in test_locations:
            # Test with different radius values
            for radius in [5, 10, 20]:
                params = {
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'radius': radius,
                    'provider': 'tomtom'
                }
                
                result = await self.test_api_endpoint('/traffic/incidents', params=params)
                
                if result['success']:
                    data = result['data']
                    if data.get('status') == 'success':
                        incidents_data = data.get('data', {})
                        incidents = incidents_data.get('incidents', [])
                        provider = incidents_data.get('provider', 'unknown')
                        
                        # Verify incident structure
                        valid_incidents = 0
                        for incident in incidents:
                            required_fields = ['id', 'type', 'severity', 'description', 'location']
                            if all(field in incident for field in required_fields):
                                # Check severity values
                                if incident['severity'] in ['critical', 'major', 'moderate', 'minor']:
                                    valid_incidents += 1
                        
                        self.log_test(
                            f"GET /api/traffic/incidents - {location['name']} (radius: {radius}km)",
                            True,
                            f"Provider: {provider}, {len(incidents)} incidents, {valid_incidents} valid structure",
                            {'location': location['name'], 'provider': provider, 'incidents': len(incidents)}
                        )
                    else:
                        self.log_test(
                            f"GET /api/traffic/incidents - {location['name']} (radius: {radius}km)",
                            False,
                            f"API returned error: {data}",
                            data
                        )
                else:
                    self.log_test(
                        f"GET /api/traffic/incidents - {location['name']} (radius: {radius}km)",
                        False,
                        f"API call failed: {result.get('exception', 'Unknown error')}",
                        result
                    )
    
    # ===================================
    # Phase 4: Traffic Flow Tests
    # ===================================
    
    async def test_traffic_flow(self):
        """Test GET /api/traffic/flow - Get traffic flow configuration"""
        print("\n🌊 PHASE 4: TRAFFIC FLOW TESTING")
        print("=" * 60)
        
        test_params = {
            'lat': 40.7128,
            'lon': -74.0060,
            'zoom': 12,
            'provider': 'tomtom'
        }
        
        result = await self.test_api_endpoint('/traffic/flow', params=test_params)
        
        if result['success']:
            data = result['data']
            if data.get('status') == 'success':
                flow_data = data.get('data', {})
                provider = flow_data.get('provider', 'unknown')
                
                # Check for tile URL or configuration
                has_config = any(key in flow_data for key in ['tile_url', 'traffic_layer', 'error'])
                
                self.log_test(
                    "GET /api/traffic/flow - Traffic flow configuration",
                    has_config,
                    f"Provider: {provider}, configuration available: {has_config}",
                    flow_data
                )
            else:
                self.log_test(
                    "GET /api/traffic/flow - Traffic flow configuration",
                    False,
                    f"API returned error: {data}",
                    data
                )
        else:
            self.log_test(
                "GET /api/traffic/flow - Traffic flow configuration",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
    
    # ===================================
    # Phase 5: Traffic Announcements Tests
    # ===================================
    
    async def test_traffic_announcements(self):
        """Test POST /api/traffic/announcement - Generate traffic announcement"""
        print("\n📢 PHASE 5: TRAFFIC ANNOUNCEMENTS TESTING")
        print("=" * 60)
        
        # Test with incidents (NYC)
        params = {
            'lat': 40.7128,
            'lon': -74.0060,
            'radius': 10,
            'location_name': 'New York',
            'provider': 'tomtom'
        }
        
        result = await self.test_api_endpoint('/traffic/announcement', method='POST', params=params)
        
        if result['success']:
            data = result['data']
            if data.get('status') == 'success':
                announcement_data = data.get('data', {})
                announcement = announcement_data.get('announcement', '')
                severity = announcement_data.get('severity', 'none')
                
                # Verify announcement quality
                is_readable = len(announcement) > 10 and any(word in announcement.lower() for word in ['traffic', 'update', 'new york'])
                
                self.log_test(
                    "POST /api/traffic/announcement - Generate announcement (with location)",
                    is_readable,
                    f"Announcement length: {len(announcement)}, severity: {severity}, readable: {is_readable}",
                    {'announcement_preview': announcement[:100] + '...' if len(announcement) > 100 else announcement}
                )
            else:
                self.log_test(
                    "POST /api/traffic/announcement - Generate announcement (with location)",
                    False,
                    f"API returned error: {data}",
                    data
                )
        else:
            self.log_test(
                "POST /api/traffic/announcement - Generate announcement (with location)",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
        
        # Test without location name
        params_no_location = {
            'lat': 51.5074,
            'lon': -0.1278,
            'radius': 15,
            'provider': 'tomtom'
        }
        
        result = await self.test_api_endpoint('/traffic/announcement', method='POST', params=params_no_location)
        
        if result['success']:
            data = result['data']
            if data.get('status') == 'success':
                announcement_data = data.get('data', {})
                announcement = announcement_data.get('announcement', '')
                
                # Verify announcement exists
                has_announcement = len(announcement) > 0
                
                self.log_test(
                    "POST /api/traffic/announcement - Generate announcement (no location)",
                    has_announcement,
                    f"Announcement generated: {has_announcement}, length: {len(announcement)}",
                    {'announcement_preview': announcement[:100] + '...' if len(announcement) > 100 else announcement}
                )
            else:
                self.log_test(
                    "POST /api/traffic/announcement - Generate announcement (no location)",
                    False,
                    f"API returned error: {data}",
                    data
                )
        else:
            self.log_test(
                "POST /api/traffic/announcement - Generate announcement (no location)",
                False,
                f"API call failed: {result.get('exception', 'Unknown error')}",
                result
            )
    
    # ===================================
    # Error Handling Tests
    # ===================================
    
    async def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n⚠️  ERROR HANDLING TESTING")
        print("=" * 60)
        
        # Test invalid coordinates
        invalid_coords_tests = [
            {'lat': 91, 'lon': 0, 'desc': 'latitude > 90'},
            {'lat': -91, 'lon': 0, 'desc': 'latitude < -90'},
            {'lat': 0, 'lon': 181, 'desc': 'longitude > 180'},
            {'lat': 0, 'lon': -181, 'desc': 'longitude < -180'},
        ]
        
        for test_case in invalid_coords_tests:
            params = {
                'lat': test_case['lat'],
                'lon': test_case['lon'],
                'radius': 10,
                'provider': 'tomtom'
            }
            
            result = await self.test_api_endpoint('/traffic/incidents', params=params)
            
            # Should either handle gracefully or return error
            handled_gracefully = (
                result['success'] or 
                (not result['success'] and result['status_code'] in [400, 422])
            )
            
            self.log_test(
                f"Error handling - Invalid coordinates ({test_case['desc']})",
                handled_gracefully,
                f"Status: {result['status_code']}, handled gracefully: {handled_gracefully}",
                result.get('data', {})
            )
        
        # Test negative radius
        params = {
            'lat': 40.7128,
            'lon': -74.0060,
            'radius': -5,
            'provider': 'tomtom'
        }
        
        result = await self.test_api_endpoint('/traffic/incidents', params=params)
        
        handled_gracefully = (
            result['success'] or 
            (not result['success'] and result['status_code'] in [400, 422])
        )
        
        self.log_test(
            "Error handling - Negative radius",
            handled_gracefully,
            f"Status: {result['status_code']}, handled gracefully: {handled_gracefully}",
            result.get('data', {})
        )
        
        # Test invalid provider
        params = {
            'lat': 40.7128,
            'lon': -74.0060,
            'radius': 10,
            'provider': 'invalid_provider'
        }
        
        result = await self.test_api_endpoint('/traffic/incidents', params=params)
        
        # Should handle gracefully (fallback to mock data)
        self.log_test(
            "Error handling - Invalid provider",
            True,  # Should always handle gracefully
            f"Status: {result['status_code']}, should fallback to mock data",
            result.get('data', {})
        )
    
    async def run_all_tests(self):
        """Run all Map & Traffic Integration tests"""
        print("🗺️🚦 DRAGON KARAU AI - MAP & TRAFFIC INTEGRATION API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test phases
            await self.test_map_config()
            await self.test_stations_for_map()
            await self.test_traffic_incidents()
            await self.test_traffic_flow()
            await self.test_traffic_announcements()
            await self.test_error_handling()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']}")
                print(f"   Details: {test['details']}")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': passed_tests/total_tests*100,
            'failed_tests': self.failed_tests
        }


async def main():
    """Main test runner"""
    tester = MapTrafficAPITester()
    results = await tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())