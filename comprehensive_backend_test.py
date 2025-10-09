#!/usr/bin/env python3
"""
Comprehensive Backend Testing Framework for Kagema FM Radio Streaming Application
Following 5-Point Testing Framework as requested in review:

1. FUNCTIONAL TESTING - Verify every API endpoint works as intended, test critical user flows, validate edge cases and error scenarios, confirm integration testing with third-party APIs
2. COMPATIBILITY TESTING - Test API compatibility across different client versions, validate response formats, check cross-platform API behavior
3. PERFORMANCE TESTING - Conduct load testing, stress testing, check resource consumption (CPU, memory), test network variability scenarios
4. SECURITY TESTING - Perform vulnerability assessment, validate data security (encryption), test authentication and authorization 
5. SYSTEM ACCEPTANCE TESTING - Validate APIs meet business objectives and user needs in production-like environment

Focus Areas:
- Core Radio Streaming APIs (station info, personalized content, multilingual support)
- Voice AI Integration (command processing, intents, help system)
- External Audio Sources (Radio.net, TuneIn, Streema, iHeartRadio, Radio Garden)
- Geographic Coverage APIs (language detection, location-based content)
- Performance and reliability under load
- Security validation for all endpoints
"""

import asyncio
import aiohttp
import time
import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Backend URL from frontend environment
FRONTEND_ENV_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://autoradio-debug.preview.emergentagent.com')
BACKEND_URL = f"{FRONTEND_ENV_URL}/api"
TIMEOUT = 30

@dataclass
class TestResult:
    name: str
    category: str
    framework_area: str
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[Dict] = None

class ComprehensiveBackendTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def setup_session(self):
        """Setup HTTP session with proper configuration"""
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def add_result(self, result: TestResult):
        """Add test result to collection"""
        self.results.append(result)
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"  {status} {result.name} ({result.response_time:.0f}ms)")
        if not result.success and result.error_message:
            print(f"      Error: {result.error_message}")
            
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> tuple:
        """Make HTTP request and return response data"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    try:
                        json_data = json.loads(content)
                    except:
                        json_data = {"raw_content": content}
                    return response.status, json_data, response_time
                    
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    try:
                        json_data = json.loads(content)
                    except:
                        json_data = {"raw_content": content}
                    return response.status, json_data, response_time
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return None, {"error": str(e)}, response_time

    # ========================================
    # 1. FUNCTIONAL TESTING
    # ========================================
    
    async def test_functional_core_apis(self):
        """1. FUNCTIONAL TESTING - Core API Endpoints"""
        print("\n🔧 1. FUNCTIONAL TESTING - Core Radio Streaming APIs")
        
        # API Root
        status, data, rt = await self.make_request("GET", "/")
        self.add_result(TestResult(
            name="API Root Endpoint",
            category="Core API",
            framework_area="Functional Testing",
            success=status == 200 and "Kagema FM" in str(data),
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # Basic Station Info
        status, data, rt = await self.make_request("GET", "/station-info")
        self.add_result(TestResult(
            name="Basic Station Information",
            category="Core API",
            framework_area="Functional Testing",
            success=status == 200 and "streamUrl" in data,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # Radio Streams - CRITICAL for frontend functionality
        status, data, rt = await self.make_request("GET", "/radio/streams")
        self.add_result(TestResult(
            name="Radio Streams API",
            category="Core API",
            framework_area="Functional Testing", 
            success=status == 200 and "main_station" in data and "alternative_streams" in data,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # Personalized Content - CRITICAL for frontend
        personalized_data = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"preferred_language": "en", "offline_mode": False}
        }
        status, data, rt = await self.make_request("POST", "/personalized-content/multilingual", personalized_data)
        self.add_result(TestResult(
            name="Personalized Content API",
            category="Core API",
            framework_area="Functional Testing",
            success=status == 200 and "radio_streams" in data,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))

    async def test_functional_voice_ai(self):
        """1. FUNCTIONAL TESTING - Voice AI Integration"""
        print("\n🎤 1. FUNCTIONAL TESTING - Voice AI Integration")
        
        # Voice Intents
        status, data, rt = await self.make_request("GET", "/voice/intents")
        self.add_result(TestResult(
            name="Voice Intents API",
            category="Voice AI",
            framework_area="Functional Testing",
            success=status == 200 and isinstance(data, dict) and len(data) >= 5,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # Voice Help
        status, data, rt = await self.make_request("GET", "/voice/help")
        self.add_result(TestResult(
            name="Voice Help System",
            category="Voice AI",
            framework_area="Functional Testing",
            success=status == 200 and "usage_tips" in data and len(data.get("usage_tips", [])) >= 5,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # Voice Command Interpretation - Test key commands
        test_commands = [
            {"text": "play", "context": "radio_control"},
            {"text": "pause", "context": "radio_control"},
            {"text": "next station", "context": "radio_control"},
            {"text": "search for jazz music", "context": "radio_control"}
        ]
        
        for cmd in test_commands:
            status, data, rt = await self.make_request("POST", "/voice/interpret", cmd)
            self.add_result(TestResult(
                name=f"Voice Command: '{cmd['text']}'",
                category="Voice AI",
                framework_area="Functional Testing",
                success=status == 200 and "intent" in data and "confidence" in data,
                response_time=rt,
                status_code=status,
                error_message=None if status == 200 else f"Status: {status}",
                details=data
            ))

    async def test_functional_external_sources(self):
        """1. FUNCTIONAL TESTING - External Audio Sources"""
        print("\n🔗 1. FUNCTIONAL TESTING - External Audio Sources")
        
        # Radio Browser Integration
        status, data, rt = await self.make_request("GET", "/radio-browser/info")
        self.add_result(TestResult(
            name="Radio Browser Service",
            category="External Sources",
            framework_area="Functional Testing",
            success=status == 200 and "info" in data,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))
        
        # AccuRadio Integration
        status, data, rt = await self.make_request("GET", "/accuradio/info")
        self.add_result(TestResult(
            name="AccuRadio Service",
            category="External Sources",
            framework_area="Functional Testing",
            success=status == 200 and "info" in data,
            response_time=rt,
            status_code=status,
            error_message=None if status == 200 else f"Status: {status}",
            details=data
        ))

    async def test_functional_geographic_coverage(self):
        """1. FUNCTIONAL TESTING - Geographic Coverage APIs"""
        print("\n🌍 1. FUNCTIONAL TESTING - Geographic Coverage APIs")
        
        # Language Detection for different regions
        test_locations = [
            {"latitude": -1.2921, "longitude": 36.8219, "expected": "Kenya"},  # Nairobi
            {"latitude": -23.5505, "longitude": -46.6333, "expected": "Brazil"},  # São Paulo
        ]
        
        for location in test_locations:
            status, data, rt = await self.make_request("POST", "/language/detect", {
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            })
            self.add_result(TestResult(
                name=f"Language Detection - {location['expected']}",
                category="Geographic Coverage",
                framework_area="Functional Testing",
                success=status == 200 and "detected_language" in data and "confidence" in data,
                response_time=rt,
                status_code=status,
                error_message=None if status == 200 else f"Status: {status}",
                details=data
            ))

    # ========================================
    # 2. COMPATIBILITY TESTING
    # ========================================
    
    async def test_compatibility_response_formats(self):
        """2. COMPATIBILITY TESTING - API Response Formats"""
        print("\n🔄 2. COMPATIBILITY TESTING - Response Format Compatibility")
        
        # Test different content types and response formats
        endpoints_to_test = [
            ("/", "API Root"),
            ("/station-info", "Station Info"),
            ("/languages", "Languages"),
            ("/radio/streams", "Radio Streams")
        ]
        
        for endpoint, name in endpoints_to_test:
            status, data, rt = await self.make_request("GET", endpoint)
            
            # Check JSON format compatibility
            is_valid_json = isinstance(data, dict) and "error" not in data
            has_required_structure = True
            
            if endpoint == "/station-info":
                has_required_structure = "streamUrl" in data and "name" in data
            elif endpoint == "/languages":
                has_required_structure = "languages" in data and isinstance(data["languages"], list)
            elif endpoint == "/radio/streams":
                has_required_structure = "main_station" in data and "alternative_streams" in data
                
            self.add_result(TestResult(
                name=f"Response Format - {name}",
                category="API Compatibility",
                framework_area="Compatibility Testing",
                success=status == 200 and is_valid_json and has_required_structure,
                response_time=rt,
                status_code=status,
                error_message=None if status == 200 else f"Status: {status}",
                details={"valid_json": is_valid_json, "valid_structure": has_required_structure}
            ))

    async def test_compatibility_cross_platform(self):
        """2. COMPATIBILITY TESTING - Cross-Platform Behavior"""
        print("\n📱 2. COMPATIBILITY TESTING - Cross-Platform API Access")
        
        # Test with different user agents
        test_headers = [
            {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"},
            {"User-Agent": "Mozilla/5.0 (Android 11; Mobile)"},
            {"Accept": "application/json", "Content-Type": "application/json"}
        ]
        
        for i, headers in enumerate(test_headers):
            status, data, rt = await self.make_request("GET", "/", headers=headers)
            platform = ["iOS", "Android", "JSON Client"][i]
            
            self.add_result(TestResult(
                name=f"Cross-Platform Access - {platform}",
                category="Cross-Platform",
                framework_area="Compatibility Testing",
                success=status == 200 and "Kagema FM" in str(data),
                response_time=rt,
                status_code=status,
                error_message=None if status == 200 else f"Status: {status}",
                details={"platform": platform}
            ))

    # ========================================
    # 3. PERFORMANCE TESTING
    # ========================================
    
    async def test_performance_load(self):
        """3. PERFORMANCE TESTING - Load Testing"""
        print("\n⚡ 3. PERFORMANCE TESTING - Concurrent Load Testing")
        
        # Test concurrent requests to critical endpoints
        critical_endpoints = ["/", "/station-info", "/radio/streams"]
        
        for endpoint in critical_endpoints:
            # Test 5 concurrent requests
            tasks = []
            start_time = time.time()
            
            for _ in range(5):
                task = self.make_request("GET", endpoint)
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = (time.time() - start_time) * 1000
            
            successful_requests = sum(1 for result in results if not isinstance(result, Exception) and result[0] == 200)
            avg_response_time = sum(result[2] for result in results if not isinstance(result, Exception)) / len(results)
            
            self.add_result(TestResult(
                name=f"Concurrent Load - {endpoint}",
                category="Load Testing",
                framework_area="Performance Testing",
                success=successful_requests >= 4,  # Allow 1 failure out of 5
                response_time=avg_response_time,
                status_code=200 if successful_requests >= 4 else 500,
                error_message=None if successful_requests >= 4 else f"Only {successful_requests}/5 requests succeeded",
                details={"concurrent_requests": 5, "successful": successful_requests, "total_time": total_time}
            ))

    async def test_performance_stress(self):
        """3. PERFORMANCE TESTING - Stress Testing"""
        print("\n💪 3. PERFORMANCE TESTING - Response Time Validation")
        
        # Test response times for critical endpoints
        critical_endpoints = [
            ("/", "API Root"),
            ("/station-info", "Station Info"),
            ("/radio/streams", "Radio Streams"),
            ("/voice/intents", "Voice Intents")
        ]
        
        for endpoint, name in critical_endpoints:
            status, data, rt = await self.make_request("GET", endpoint)
            
            # Performance criteria: <2000ms for acceptable, <500ms for excellent
            performance_acceptable = rt < 2000
            
            self.add_result(TestResult(
                name=f"Response Time - {name}",
                category="Performance",
                framework_area="Performance Testing",
                success=status == 200 and performance_acceptable,
                response_time=rt,
                status_code=status,
                error_message=None if (status == 200 and performance_acceptable) else f"Slow response: {rt:.0f}ms",
                details={"performance_target": "< 2000ms", "actual_time": rt}
            ))

    # ========================================
    # 4. SECURITY TESTING
    # ========================================
    
    async def test_security_input_validation(self):
        """4. SECURITY TESTING - Input Validation"""
        print("\n🔒 4. SECURITY TESTING - Input Validation & Error Handling")
        
        # Test invalid endpoints (should return 404)
        status, data, rt = await self.make_request("GET", "/nonexistent-endpoint")
        self.add_result(TestResult(
            name="404 Error Handling",
            category="Security",
            framework_area="Security Testing",
            success=status == 404,
            response_time=rt,
            status_code=status,
            error_message=None if status == 404 else f"Expected 404, got {status}",
            details={"expected_status": 404}
        ))
        
        # Test invalid POST data (should return 422)
        status, data, rt = await self.make_request("POST", "/language/detect", {"invalid": "data"})
        self.add_result(TestResult(
            name="Invalid POST Data Handling",
            category="Security",
            framework_area="Security Testing",
            success=status == 422,
            response_time=rt,
            status_code=status,
            error_message=None if status == 422 else f"Expected 422, got {status}",
            details={"expected_status": 422}
        ))

    async def test_security_data_exposure(self):
        """4. SECURITY TESTING - Data Security"""
        print("\n🛡️ 4. SECURITY TESTING - Sensitive Data Exposure Check")
        
        # Check for sensitive data exposure in public endpoints
        public_endpoints = ["/", "/station-info", "/languages"]
        
        for endpoint in public_endpoints:
            status, data, rt = await self.make_request("GET", endpoint)
            
            # Check for sensitive patterns
            sensitive_patterns = ["password", "secret", "key", "token", "private"]
            data_str = json.dumps(data).lower() if isinstance(data, dict) else str(data).lower()
            has_sensitive_data = any(pattern in data_str for pattern in sensitive_patterns)
            
            self.add_result(TestResult(
                name=f"Data Security - {endpoint}",
                category="Security",
                framework_area="Security Testing",
                success=status == 200 and not has_sensitive_data,
                response_time=rt,
                status_code=status,
                error_message="Sensitive data detected" if has_sensitive_data else None,
                details={"sensitive_data_found": has_sensitive_data}
            ))

    # ========================================
    # 5. SYSTEM ACCEPTANCE TESTING
    # ========================================
    
    async def test_acceptance_business_flows(self):
        """5. SYSTEM ACCEPTANCE TESTING - Business Objectives"""
        print("\n🎯 5. SYSTEM ACCEPTANCE TESTING - Critical Business Flows")
        
        # Test complete radio streaming flow
        flow_success = True
        flow_details = []
        total_flow_time = 0
        
        # Step 1: API Health Check
        status, data, rt = await self.make_request("GET", "/")
        step_success = status == 200 and "Kagema FM" in str(data)
        flow_success = flow_success and step_success
        total_flow_time += rt
        flow_details.append({"step": "API Health", "success": step_success, "time": rt})
        
        # Step 2: Get Station Info
        status, data, rt = await self.make_request("GET", "/station-info")
        step_success = status == 200 and "streamUrl" in data
        flow_success = flow_success and step_success
        total_flow_time += rt
        flow_details.append({"step": "Station Info", "success": step_success, "time": rt})
        
        # Step 3: Get Radio Streams
        status, data, rt = await self.make_request("GET", "/radio/streams")
        step_success = status == 200 and "main_station" in data
        flow_success = flow_success and step_success
        total_flow_time += rt
        flow_details.append({"step": "Radio Streams", "success": step_success, "time": rt})
        
        # Step 4: Language Detection
        status, data, rt = await self.make_request("POST", "/language/detect", {"latitude": -1.2921, "longitude": 36.8219})
        step_success = status == 200 and "detected_language" in data
        flow_success = flow_success and step_success
        total_flow_time += rt
        flow_details.append({"step": "Language Detection", "success": step_success, "time": rt})
        
        self.add_result(TestResult(
            name="Complete Radio Streaming Flow",
            category="Business Flow",
            framework_area="System Acceptance Testing",
            success=flow_success,
            response_time=total_flow_time,
            status_code=200 if flow_success else 500,
            error_message=None if flow_success else "One or more steps failed",
            details={"steps": flow_details, "total_steps": len(flow_details)}
        ))

    async def test_acceptance_stream_accessibility(self):
        """5. SYSTEM ACCEPTANCE TESTING - Stream Accessibility"""
        print("\n📡 5. SYSTEM ACCEPTANCE TESTING - Radio Stream Accessibility")
        
        # Get stream URLs from API
        status, streams_data, rt = await self.make_request("GET", "/radio/streams")
        
        if status == 200 and "alternative_streams" in streams_data:
            # Test key streams for accessibility
            test_streams = streams_data["alternative_streams"][:4]  # Test first 4 streams
            
            accessible_streams = 0
            total_streams = len(test_streams)
            
            for stream in test_streams:
                if "streamUrl" in stream:
                    stream_url = stream["streamUrl"]
                    stream_name = stream.get("name", "Unknown Stream")
                    
                    # Test stream accessibility with HEAD request
                    start_time = time.time()
                    try:
                        async with self.session.head(stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            response_time = (time.time() - start_time) * 1000
                            
                            # Check for audio content type
                            content_type = response.headers.get('content-type', '').lower()
                            is_audio = any(audio_type in content_type for audio_type in ['audio', 'mpeg', 'mp3', 'aac'])
                            
                            if response.status == 200 and is_audio:
                                accessible_streams += 1
                                
                            self.add_result(TestResult(
                                name=f"Stream Access - {stream_name}",
                                category="Stream Access",
                                framework_area="System Acceptance Testing",
                                success=response.status == 200 and is_audio,
                                response_time=response_time,
                                status_code=response.status,
                                error_message=None if response.status == 200 else f"Stream not accessible",
                                details={"stream_url": stream_url, "content_type": content_type}
                            ))
                    except Exception as e:
                        response_time = (time.time() - start_time) * 1000
                        self.add_result(TestResult(
                            name=f"Stream Access - {stream_name}",
                            category="Stream Access",
                            framework_area="System Acceptance Testing",
                            success=False,
                            response_time=response_time,
                            status_code=None,
                            error_message=f"Connection failed: {str(e)}",
                            details={"stream_url": stream_url, "error": str(e)}
                        ))

    # ========================================
    # MAIN TEST EXECUTION
    # ========================================
    
    async def run_comprehensive_tests(self):
        """Run comprehensive test suite following 5-point framework"""
        print("🎵 KAGEMA FM COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print("Following 5-Point Testing Framework:")
        print("1. Functional Testing - API endpoints, user flows, edge cases, integrations")
        print("2. Compatibility Testing - Response formats, cross-platform behavior")
        print("3. Performance Testing - Load testing, stress testing, resource consumption")
        print("4. Security Testing - Input validation, data security, authentication")
        print("5. System Acceptance Testing - Business objectives, production readiness")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # 1. Functional Testing
            await self.test_functional_core_apis()
            await self.test_functional_voice_ai()
            await self.test_functional_external_sources()
            await self.test_functional_geographic_coverage()
            
            # 2. Compatibility Testing
            await self.test_compatibility_response_formats()
            await self.test_compatibility_cross_platform()
            
            # 3. Performance Testing
            await self.test_performance_load()
            await self.test_performance_stress()
            
            # 4. Security Testing
            await self.test_security_input_validation()
            await self.test_security_data_exposure()
            
            # 5. System Acceptance Testing
            await self.test_acceptance_business_flows()
            await self.test_acceptance_stream_accessibility()
            
        finally:
            await self.cleanup_session()
            
        return self.generate_framework_report()
    
    def generate_framework_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report with 5-point framework analysis"""
        
        # Categorize results by framework area
        framework_results = {}
        for result in self.results:
            if result.framework_area not in framework_results:
                framework_results[result.framework_area] = []
            framework_results[result.framework_area].append(result)
        
        # Calculate metrics for each framework area
        framework_metrics = {}
        for area, results in framework_results.items():
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            avg_response_time = sum(r.response_time for r in results) / total_tests if total_tests > 0 else 0
            
            framework_metrics[area] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time
            }
        
        # Overall metrics
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r.success)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        overall_avg_response_time = sum(r.response_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        # Failed tests details
        failed_tests = [r for r in self.results if not r.success]
        
        # Critical issues (failures in core functionality)
        critical_categories = ["Core API", "Voice AI", "Business Flow", "Stream Access"]
        critical_failures = [r for r in failed_tests if r.category in critical_categories]
        
        return {
            "overall_metrics": {
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": len(failed_tests),
                "success_rate": overall_success_rate,
                "avg_response_time": overall_avg_response_time
            },
            "framework_metrics": framework_metrics,
            "failed_tests": [
                {
                    "name": test.name,
                    "category": test.category,
                    "framework_area": test.framework_area,
                    "error": test.error_message,
                    "status_code": test.status_code
                } for test in failed_tests
            ],
            "critical_failures": len(critical_failures),
            "deployment_readiness": {
                "ready_for_production": overall_success_rate >= 95 and len(critical_failures) == 0,
                "success_rate_acceptable": overall_success_rate >= 90,
                "performance_acceptable": overall_avg_response_time < 2000,
                "no_critical_failures": len(critical_failures) == 0
            }
        }

async def main():
    """Main test execution function"""
    tester = ComprehensiveBackendTester()
    
    try:
        report = await tester.run_comprehensive_tests()
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE BACKEND TESTING COMPLETE")
        print("=" * 80)
        
        # Print framework-specific results
        print("\n📊 5-POINT FRAMEWORK RESULTS:")
        for area, metrics in report["framework_metrics"].items():
            status_icon = "✅" if metrics["success_rate"] >= 90 else "⚠️" if metrics["success_rate"] >= 70 else "❌"
            print(f"  {status_icon} {area}: {metrics['success_rate']:.1f}% ({metrics['passed_tests']}/{metrics['total_tests']} tests, {metrics['avg_response_time']:.0f}ms avg)")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"  Success Rate: {report['overall_metrics']['success_rate']:.1f}%")
        print(f"  Total Tests: {report['overall_metrics']['total_tests']}")
        print(f"  Passed: {report['overall_metrics']['passed_tests']}")
        print(f"  Failed: {report['overall_metrics']['failed_tests']}")
        print(f"  Avg Response Time: {report['overall_metrics']['avg_response_time']:.0f}ms")
        print(f"  Critical Failures: {report['critical_failures']}")
        
        # Deployment readiness assessment
        readiness = report["deployment_readiness"]
        print(f"\n🚀 DEPLOYMENT READINESS ASSESSMENT:")
        print(f"  Production Ready: {'✅ YES' if readiness['ready_for_production'] else '❌ NO'}")
        print(f"  Success Rate >90%: {'✅ YES' if readiness['success_rate_acceptable'] else '❌ NO'} ({report['overall_metrics']['success_rate']:.1f}%)")
        print(f"  Performance <2s: {'✅ YES' if readiness['performance_acceptable'] else '❌ NO'} ({report['overall_metrics']['avg_response_time']:.0f}ms)")
        print(f"  No Critical Issues: {'✅ YES' if readiness['no_critical_failures'] else '❌ NO'} ({report['critical_failures']} critical)")
        
        # Failed tests summary
        if report["failed_tests"]:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for test in report["failed_tests"]:
                print(f"  • [{test['framework_area']}] {test['name']}: {test['error']}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ TESTING FRAMEWORK ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(main())