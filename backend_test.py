#!/usr/bin/env python3
"""
Backend API Testing for Dragon KARAU AI - Frontend Bug Fixes Support
Testing the 3 critical endpoints that support frontend fixes:
1. Popular Stations API (GET /api/stations?limit=10)
2. Geocoding Service Status (GET /api/geocoding/stats)  
3. Core Radio API Health (GET /api/)
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any, Optional
import sys
import os
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://karauradio.preview.emergentagent.com"

class BackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Dragon-KARAU-AI-Backend-Tester/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            print(f"   Error: {details.get('error', 'Unknown error')}")
        else:
            print(f"   Details: {details.get('summary', 'Test passed')}")
        print()
    
    async def test_api_root(self):
        """Test 1: Core Radio API Health (GET /api/)"""
        test_name = "Core Radio API Health Check"
        try:
            url = f"{self.backend_url}/api/"
            async with self.session.get(url) as response:
                status_code = response.status
                data = await response.json()
                
                # Check status code
                if status_code != 200:
                    self.log_test(test_name, False, {
                        'error': f'Expected 200 OK, got {status_code}',
                        'response': data
                    })
                    return
                
                # Check version
                version = data.get('version')
                if version != '5.0.0':
                    self.log_test(test_name, False, {
                        'error': f'Expected version 5.0.0, got {version}',
                        'response': data
                    })
                    return
                
                # Check required fields
                required_fields = ['message', 'version', 'features']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test(test_name, False, {
                        'error': f'Missing required fields: {missing_fields}',
                        'response': data
                    })
                    return
                
                self.log_test(test_name, True, {
                    'summary': f'API v{version} healthy with {len(data.get("features", []))} features',
                    'version': version,
                    'features': data.get('features', []),
                    'message': data.get('message', '')
                })
                
        except Exception as e:
            self.log_test(test_name, False, {
                'error': f'Request failed: {str(e)}',
                'url': url
            })
    
    async def test_popular_stations_api(self):
        """Test 2: Popular Stations API (GET /api/stations?limit=10)"""
        test_name = "Popular Stations API"
        try:
            url = f"{self.backend_url}/api/stations?limit=10"
            async with self.session.get(url) as response:
                status_code = response.status
                data = await response.json()
                
                # Check status code
                if status_code != 200:
                    self.log_test(test_name, False, {
                        'error': f'Expected 200 OK, got {status_code}',
                        'response': data
                    })
                    return
                
                # Check response structure
                if data.get('status') != 'success':
                    self.log_test(test_name, False, {
                        'error': f'API returned status: {data.get("status")}',
                        'response': data
                    })
                    return
                
                # Check data structure
                stations_data = data.get('data', {})
                stations = stations_data.get('stations', [])
                
                if not isinstance(stations, list):
                    self.log_test(test_name, False, {
                        'error': 'Stations data is not a list',
                        'response': data
                    })
                    return
                
                # Check if we got stations (should be up to 10)
                if len(stations) == 0:
                    self.log_test(test_name, False, {
                        'error': 'No stations returned',
                        'response': data
                    })
                    return
                
                # Validate station structure
                required_station_fields = ['id', 'name', 'stream_url', 'country', 'quality_score']
                valid_stations = 0
                
                for i, station in enumerate(stations[:10]):  # Check up to 10 stations
                    missing_fields = [field for field in required_station_fields if field not in station]
                    if not missing_fields:
                        valid_stations += 1
                    elif i < 3:  # Only log first 3 invalid stations to avoid spam
                        print(f"   Station {i+1} missing fields: {missing_fields}")
                
                if valid_stations == 0:
                    self.log_test(test_name, False, {
                        'error': 'No stations have required fields (id, name, stream_url, country, quality_score)',
                        'stations_count': len(stations),
                        'sample_station': stations[0] if stations else None
                    })
                    return
                
                self.log_test(test_name, True, {
                    'summary': f'Retrieved {len(stations)} stations, {valid_stations} with complete data',
                    'stations_count': len(stations),
                    'valid_stations': valid_stations,
                    'sample_station': {
                        'name': stations[0].get('name'),
                        'country': stations[0].get('country'),
                        'quality_score': stations[0].get('quality_score')
                    } if stations else None
                })
                
        except Exception as e:
            self.log_test(test_name, False, {
                'error': f'Request failed: {str(e)}',
                'url': url
            })
    
    async def test_geocoding_stats(self):
        """Test 3: Geocoding Service Status (GET /api/geocoding/stats)"""
        test_name = "Geocoding Service Status"
        try:
            url = f"{self.backend_url}/api/geocoding/stats"
            async with self.session.get(url) as response:
                status_code = response.status
                data = await response.json()
                
                # Check status code
                if status_code != 200:
                    self.log_test(test_name, False, {
                        'error': f'Expected 200 OK, got {status_code}',
                        'response': data
                    })
                    return
                
                # Check response structure
                if data.get('status') != 'success':
                    self.log_test(test_name, False, {
                        'error': f'API returned status: {data.get("status")}',
                        'response': data
                    })
                    return
                
                # Check geocoding data
                geocoding_data = data.get('data', {})
                
                # Required fields for geocoding stats
                required_fields = ['total_stations', 'geocoded_stations']
                missing_fields = [field for field in required_fields if field not in geocoding_data]
                
                if missing_fields:
                    self.log_test(test_name, False, {
                        'error': f'Missing required geocoding fields: {missing_fields}',
                        'response': data
                    })
                    return
                
                total_stations = geocoding_data.get('total_stations', 0)
                geocoded_stations = geocoding_data.get('geocoded_stations', 0)
                
                # Calculate progress percentage
                if total_stations > 0:
                    progress_percentage = round((geocoded_stations / total_stations) * 100, 2)
                else:
                    progress_percentage = 0
                
                self.log_test(test_name, True, {
                    'summary': f'Geocoding progress: {geocoded_stations}/{total_stations} stations ({progress_percentage}%)',
                    'total_stations': total_stations,
                    'geocoded_stations': geocoded_stations,
                    'progress_percentage': progress_percentage,
                    'geocoding_active': geocoded_stations > 0 or total_stations > 0
                })
                
        except Exception as e:
            self.log_test(test_name, False, {
                'error': f'Request failed: {str(e)}',
                'url': url
            })
    
    async def run_all_tests(self):
        """Run all backend tests for frontend bug fixes support"""
        print("🎯 BACKEND VALIDATION - FRONTEND BUG FIXES SUPPORT")
        print("=" * 60)
        print(f"Testing backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run the 3 critical tests
        await self.test_api_root()
        await self.test_popular_stations_api()
        await self.test_geocoding_stats()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("=" * 60)
        print("🎯 BACKEND VALIDATION SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        print()
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED - Backend ready for frontend testing!")
        else:
            print("⚠️  Some tests failed - Backend needs attention before frontend testing")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details'].get('error', 'Unknown error')}")
        
        print()
        return passed_tests, failed_tests

async def main():
    """Execute comprehensive validation"""
    print("🚀 DRAGON KARAU AI - COMPREHENSIVE SYSTEM VALIDATION")
    print("Phase 1: Backend API & Geocoding Service Validation")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Validation Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    async with ComprehensiveValidator() as validator:
        # Execute all validation phases
        await validator.validate_core_api_endpoints()
        await validator.validate_multi_source_crawler()
        await validator.validate_favorites_system()
        await validator.validate_intelligent_search()
        await validator.validate_analytics_dashboard()
        await validator.validate_user_feedback()
        await validator.validate_monitoring_system()
        await validator.validate_content_compliance()
        await validator.validate_ab_testing()
        await validator.validate_distance_matrix()
        await validator.validate_geocoding_service()
        await validator.validate_removed_endpoints()
        await validator.validate_database_integrity()
        await validator.check_performance_benchmarks()
        
        # Generate final report
        final_results = validator.generate_final_report()
        
        return final_results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        if results["success_rate"] >= 95 and results["critical_failures"] == 0:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Issues found
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        sys.exit(3)