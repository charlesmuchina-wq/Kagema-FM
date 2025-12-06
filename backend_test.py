#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM VALIDATION - Phase 1: Backend API & Geocoding
Dragon KARAU AI - Global Radio Platform Testing Suite

This script validates:
1. Backend API endpoint validation
2. Multi-source crawler verification (post-Radioplayer removal)
3. Database integrity checks
4. Geocoding service initiation and validation
5. Performance benchmarks
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any, Optional
import sys
import os

# Backend URL from frontend environment
BACKEND_URL = "https://dragon-radio.preview.emergentagent.com/api"

class ComprehensiveValidator:
    def __init__(self):
        self.session = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "critical_failures": [],
            "performance_metrics": {},
            "geocoding_progress": {},
            "test_details": []
        }
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result"""
        self.results["total_tests"] += 1
        if status == "PASS":
            self.results["passed"] += 1
            print(f"✅ {test_name}: {status} ({response_time:.0f}ms)")
        else:
            self.results["failed"] += 1
            print(f"❌ {test_name}: {status} - {details}")
            if "CRITICAL" in test_name.upper():
                self.results["critical_failures"].append(f"{test_name}: {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": response_time
        })
    
    async def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                          data: Dict = None, test_name: str = None) -> Dict:
        """Test a single endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"
        
        start_time = time.time()
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    
                    if response.status == expected_status:
                        self.log_test(test_name, "PASS", response_time=response_time)
                        return {"success": True, "data": response_data, "response_time": response_time}
                    else:
                        self.log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status}")
                        return {"success": False, "status": response.status, "data": response_data}
                        
            elif method.upper() == "POST":
                headers = {"Content-Type": "application/json"} if data else {}
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json()
                    
                    if response.status == expected_status:
                        self.log_test(test_name, "PASS", response_time=response_time)
                        return {"success": True, "data": response_data, "response_time": response_time}
                    else:
                        self.log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status}")
                        return {"success": False, "status": response.status, "data": response_data}
                        
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == expected_status:
                        self.log_test(test_name, "PASS", response_time=response_time)
                        return {"success": True, "data": response_data, "response_time": response_time}
                    else:
                        self.log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status}")
                        return {"success": False, "status": response.status, "data": response_data}
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return {"success": False, "error": str(e), "response_time": response_time}
    
    async def validate_core_api_endpoints(self):
        """1. CRITICAL API ENDPOINTS (All Must Pass)"""
        print("\n🔍 PHASE 1.1: CORE API ENDPOINTS VALIDATION")
        print("=" * 60)
        
        # Core API
        await self.test_endpoint("GET", "/", test_name="CRITICAL - API Root v5.0.0")
        await self.test_endpoint("GET", "/station-info", test_name="CRITICAL - Station Info")
        
        # Stations Management
        await self.test_endpoint("GET", "/stations", test_name="CRITICAL - List Stations")
        await self.test_endpoint("GET", "/stations/search?q=test", test_name="CRITICAL - Search Functionality")
        await self.test_endpoint("GET", "/stations/nearest?lat=40.7128&lon=-74.0060&limit=5", 
                                test_name="CRITICAL - Nearest Stations")
    
    async def validate_multi_source_crawler(self):
        """2. Multi-Source Crawler (CRITICAL - Post Radioplayer Removal)"""
        print("\n🕷️ PHASE 1.2: MULTI-SOURCE CRAWLER VALIDATION")
        print("=" * 60)
        
        # Crawler stats - must show ONLY 3 crawlers
        stats_result = await self.test_endpoint("GET", "/crawler/stats", 
                                               test_name="CRITICAL - Crawler Stats (3 sources only)")
        
        if stats_result.get("success"):
            crawlers = stats_result["data"].get("available_crawlers", [])
            expected_crawlers = ["dragon_ai", "radio_garden", "radio_browser_info"]
            
            if set(crawlers) == set(expected_crawlers) and len(crawlers) == 3:
                self.log_test("CRITICAL - Crawler Count Validation", "PASS", 
                            f"Exactly 3 crawlers: {crawlers}")
            else:
                self.log_test("CRITICAL - Crawler Count Validation", "FAIL", 
                            f"Expected {expected_crawlers}, got {crawlers}")
        
        # Source discovery
        await self.test_endpoint("GET", "/crawler/discover-sources", 
                                test_name="CRITICAL - Source Discovery")
        
        # Multi-source crawler start
        await self.test_endpoint("POST", "/crawler/start-multi-source", 
                                test_name="CRITICAL - Start Multi-Source Crawler")
        
        # Individual crawlers
        await self.test_endpoint("POST", "/crawler/start/dragon_ai", 
                                test_name="CRITICAL - Dragon AI Crawler")
        await self.test_endpoint("POST", "/crawler/start/radio_garden", 
                                test_name="CRITICAL - Radio Garden Crawler")
        await self.test_endpoint("POST", "/crawler/start/radio_browser_info", 
                                test_name="CRITICAL - Radio Browser Info Crawler")
        
        # Radioplayer must fail
        radioplayer_result = await self.test_endpoint("POST", "/crawler/start/radioplayer", 
                                                    expected_status=200,
                                                    test_name="CRITICAL - Radioplayer Rejection")
        
        if radioplayer_result.get("success") and "Unknown source" in str(radioplayer_result.get("data", {})):
            self.log_test("CRITICAL - Radioplayer Properly Removed", "PASS", 
                        "Radioplayer correctly rejected")
        else:
            self.log_test("CRITICAL - Radioplayer Properly Removed", "FAIL", 
                        "Radioplayer should return 'Unknown source' error")
    
    async def validate_favorites_system(self):
        """3. Favorites System"""
        print("\n❤️ PHASE 1.3: FAVORITES SYSTEM VALIDATION")
        print("=" * 60)
        
        test_user = "validation_user_2025"
        test_station = "test_station_validation"
        
        # Add favorite
        await self.test_endpoint("POST", f"/favorites/add?user_id={test_user}&station_id={test_station}", 
                                test_name="Favorites - Add Station")
        
        # Get user favorites
        await self.test_endpoint("GET", f"/favorites/{test_user}", 
                                test_name="Favorites - Get User Favorites")
        
        # Get user stats
        await self.test_endpoint("GET", f"/favorites/{test_user}/stats", 
                                test_name="Favorites - User Statistics")
        
        # Remove favorite
        await self.test_endpoint("DELETE", f"/favorites/remove?user_id={test_user}&station_id={test_station}", 
                                test_name="Favorites - Remove Station")
    
    async def validate_intelligent_search(self):
        """4. Intelligent Search"""
        print("\n🧠 PHASE 1.4: INTELLIGENT SEARCH VALIDATION")
        print("=" * 60)
        
        # AI search
        await self.test_endpoint("GET", "/search/intelligent?q=rock", 
                                test_name="Search - AI Intelligent Search")
        
        # Trending stations
        await self.test_endpoint("GET", "/search/trending", 
                                test_name="Search - Trending Stations")
        
        # Filter options
        await self.test_endpoint("GET", "/search/filters/countries", 
                                test_name="Search - Available Countries")
        
        await self.test_endpoint("GET", "/search/filters/languages", 
                                test_name="Search - Available Languages")
    
    async def validate_analytics_dashboard(self):
        """5. Analytics Dashboard"""
        print("\n📊 PHASE 1.5: ANALYTICS DASHBOARD VALIDATION")
        print("=" * 60)
        
        # Full analytics
        await self.test_endpoint("GET", "/analytics/dashboard", 
                                test_name="Analytics - Full Dashboard")
        
        # Analytics summary
        await self.test_endpoint("GET", "/analytics/stats", 
                                test_name="Analytics - Summary Stats")
    
    async def validate_user_feedback(self):
        """6. User Feedback"""
        print("\n💬 PHASE 1.6: USER FEEDBACK VALIDATION")
        print("=" * 60)
        
        # Submit feedback
        feedback_data = {
            "category": "app_performance",
            "rating": 4,
            "comment": "Validation test feedback",
            "user_metadata": {"platform": "validation", "version": "5.0.0"}
        }
        await self.test_endpoint("POST", "/feedback/submit", data=feedback_data,
                                test_name="Feedback - Submit Feedback")
        
        # Feedback stats
        await self.test_endpoint("GET", "/feedback/stats", 
                                test_name="Feedback - Statistics")
    
    async def validate_monitoring_system(self):
        """7. Real-Time Monitoring"""
        print("\n🔍 PHASE 1.7: REAL-TIME MONITORING VALIDATION")
        print("=" * 60)
        
        # System health
        await self.test_endpoint("GET", "/monitoring/status", 
                                test_name="Monitoring - System Health")
        
        # Alert list
        await self.test_endpoint("GET", "/monitoring/alerts", 
                                test_name="Monitoring - Alert List")
    
    async def validate_content_compliance(self):
        """8. Content Compliance"""
        print("\n⚖️ PHASE 1.8: CONTENT COMPLIANCE VALIDATION")
        print("=" * 60)
        
        # Compliance stats
        await self.test_endpoint("GET", "/compliance/stats", 
                                test_name="Compliance - Statistics")
        
        # Compliance report
        await self.test_endpoint("GET", "/compliance/report", 
                                test_name="Compliance - Report")
    
    async def validate_ab_testing(self):
        """9. A/B Testing"""
        print("\n🧪 PHASE 1.9: A/B TESTING VALIDATION")
        print("=" * 60)
        
        # Experiments summary
        await self.test_endpoint("GET", "/experiments/summary", 
                                test_name="A/B Testing - Experiments Summary")
    
    async def validate_distance_matrix(self):
        """10. Routing & Distance Matrix"""
        print("\n🗺️ PHASE 1.10: DISTANCE MATRIX VALIDATION")
        print("=" * 60)
        
        # Distance matrix calculation
        matrix_data = {
            "sources": [{"lat": 40.7128, "lon": -74.0060}],  # New York
            "targets": [{"lat": 41.8781, "lon": -87.6298}],  # Chicago
            "mode": "drive"
        }
        await self.test_endpoint("POST", "/routing/distance-matrix", data=matrix_data,
                                test_name="Distance Matrix - Calculate Matrix")
        
        # Matrix API status
        await self.test_endpoint("GET", "/routing/distance-matrix/status", 
                                test_name="Distance Matrix - API Status")
    
    async def validate_geocoding_service(self):
        """11. GEOCODING (CRITICAL FOR THIS PHASE)"""
        print("\n🌍 PHASE 1.11: GEOCODING SERVICE VALIDATION")
        print("=" * 60)
        
        # Current geocoding statistics
        stats_result = await self.test_endpoint("GET", "/geocoding/stats", 
                                               test_name="CRITICAL - Geocoding Statistics")
        
        if stats_result.get("success"):
            stats_data = stats_result["data"]
            self.results["geocoding_progress"]["before"] = {
                "total_stations": stats_data.get("total_stations", 0),
                "geocoded_stations": stats_data.get("geocoded_stations", 0),
                "geocoding_percentage": stats_data.get("geocoding_percentage", 0)
            }
            print(f"📍 Current Geocoding Status: {stats_data.get('geocoded_stations', 0)}/{stats_data.get('total_stations', 0)} stations ({stats_data.get('geocoding_percentage', 0):.1f}%)")
        
        # Start batch geocoding (500 stations)
        print("\n🚀 INITIATING BATCH GEOCODING (500 stations)...")
        geocoding_result = await self.test_endpoint("POST", "/geocoding/geocode-batch?limit=500", 
                                                   test_name="CRITICAL - Start Batch Geocoding")
        
        if geocoding_result.get("success"):
            geocoding_data = geocoding_result["data"]
            self.results["geocoding_progress"]["batch_result"] = geocoding_data
            print(f"📊 Batch Geocoding Result: {geocoding_data.get('processed', 0)} processed, {geocoding_data.get('successful', 0)} successful")
        
        # Check geocoding progress after batch
        await asyncio.sleep(2)  # Wait for processing
        final_stats = await self.test_endpoint("GET", "/geocoding/stats", 
                                              test_name="Geocoding - Final Statistics")
        
        if final_stats.get("success"):
            final_data = final_stats["data"]
            self.results["geocoding_progress"]["after"] = {
                "total_stations": final_data.get("total_stations", 0),
                "geocoded_stations": final_data.get("geocoded_stations", 0),
                "geocoding_percentage": final_data.get("geocoding_percentage", 0)
            }
            print(f"📍 Final Geocoding Status: {final_data.get('geocoded_stations', 0)}/{final_data.get('total_stations', 0)} stations ({final_data.get('geocoding_percentage', 0):.1f}%)")
    
    async def validate_removed_endpoints(self):
        """12. REMOVED ENDPOINTS (Must Return 404)"""
        print("\n🚫 PHASE 1.12: REMOVED ENDPOINTS VALIDATION")
        print("=" * 60)
        
        # These should return 404
        await self.test_endpoint("GET", "/radioplayer/auth-status", expected_status=404,
                                test_name="CRITICAL - Radioplayer Auth Status (404)")
        
        await self.test_endpoint("POST", "/radioplayer/test-fetch", expected_status=404,
                                test_name="CRITICAL - Radioplayer Test Fetch (404)")
    
    async def validate_database_integrity(self):
        """13. Database Validation"""
        print("\n🗄️ PHASE 1.13: DATABASE INTEGRITY VALIDATION")
        print("=" * 60)
        
        # Get stations to check database health
        stations_result = await self.test_endpoint("GET", "/stations?limit=1", 
                                                  test_name="Database - Station Count Check")
        
        if stations_result.get("success"):
            total_stations = stations_result["data"].get("total", 0)
            if total_stations > 15000:
                self.log_test("Database - Station Count > 15,000", "PASS", 
                            f"Total stations: {total_stations}")
            else:
                self.log_test("Database - Station Count > 15,000", "FAIL", 
                            f"Only {total_stations} stations (expected > 15,000)")
    
    async def check_performance_benchmarks(self):
        """14. Performance Checks"""
        print("\n⚡ PHASE 1.14: PERFORMANCE BENCHMARKS")
        print("=" * 60)
        
        # Calculate average response times
        total_time = 0
        test_count = 0
        
        for test in self.results["test_details"]:
            if test["response_time_ms"] > 0:
                total_time += test["response_time_ms"]
                test_count += 1
        
        if test_count > 0:
            avg_response_time = total_time / test_count
            self.results["performance_metrics"]["average_response_time"] = avg_response_time
            
            if avg_response_time < 300:
                self.log_test("Performance - API Response Time < 300ms", "PASS", 
                            f"Average: {avg_response_time:.0f}ms")
            else:
                self.log_test("Performance - API Response Time < 300ms", "FAIL", 
                            f"Average: {avg_response_time:.0f}ms (target: <300ms)")
    
    def generate_final_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE SYSTEM VALIDATION - PHASE 1 RESULTS")
        print("=" * 80)
        
        # Overall statistics
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests Executed: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   🎯 Success Rate: {success_rate:.1f}%")
        
        # Critical failures
        if self.results["critical_failures"]:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.results['critical_failures'])}):") 
            for failure in self.results["critical_failures"]:
                print(f"   ❌ {failure}")
        else:
            print(f"\n✅ NO CRITICAL FAILURES - All critical endpoints operational!")
        
        # Performance metrics
        if self.results["performance_metrics"]:
            print(f"\n⚡ PERFORMANCE METRICS:")
            avg_time = self.results["performance_metrics"].get("average_response_time", 0)
            print(f"   Average API Response Time: {avg_time:.0f}ms")
            
            if avg_time < 300:
                print(f"   ✅ Performance Target Met (<300ms)")
            else:
                print(f"   ⚠️ Performance Target Missed (target: <300ms)")
        
        # Geocoding progress
        if self.results["geocoding_progress"]:
            print(f"\n🌍 GEOCODING PROGRESS REPORT:")
            before = self.results["geocoding_progress"].get("before", {})
            after = self.results["geocoding_progress"].get("after", {})
            batch = self.results["geocoding_progress"].get("batch_result", {})
            
            if before:
                print(f"   Before Batch: {before.get('geocoded_stations', 0)}/{before.get('total_stations', 0)} ({before.get('geocoding_percentage', 0):.1f}%)")
            
            if batch:
                print(f"   Batch Processing: {batch.get('processed', 0)} processed, {batch.get('successful', 0)} successful")
            
            if after:
                print(f"   After Batch: {after.get('geocoded_stations', 0)}/{after.get('total_stations', 0)} ({after.get('geocoding_percentage', 0):.1f}%)")
        
        # Final assessment
        print(f"\n🎯 PHASE 1 ASSESSMENT:")
        if success_rate >= 95 and not self.results["critical_failures"]:
            print(f"   ✅ EXCELLENT - System ready for Phase 2")
        elif success_rate >= 85:
            print(f"   ⚠️ GOOD - Minor issues identified, system mostly operational")
        else:
            print(f"   ❌ NEEDS ATTENTION - Significant issues require resolution")
        
        print(f"\n📋 RECOMMENDATIONS FOR PHASE 2:")
        if not self.results["critical_failures"]:
            print(f"   ✅ All critical systems operational - proceed with Phase 2")
        else:
            print(f"   🔧 Resolve critical failures before Phase 2")
        
        if self.results["geocoding_progress"].get("after", {}).get("geocoding_percentage", 0) < 50:
            print(f"   📍 Continue geocoding process to improve location services")
        
        return {
            "success_rate": success_rate,
            "critical_failures": len(self.results["critical_failures"]),
            "total_tests": total,
            "passed_tests": passed,
            "performance_ok": self.results["performance_metrics"].get("average_response_time", 1000) < 300
        }

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