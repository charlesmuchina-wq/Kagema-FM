#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for Kagema FM
Post-Cache-Clear System Validation & ERR_NGROK_3200 Resolution Persistence Testing

This test suite validates:
1. Core System Functionality
2. ERR_NGROK_3200 Resolution Persistence  
3. Performance After Clean Start
4. Build System Validation
5. Integration Testing
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KagemaFMBackendTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://carmedia-hub-1.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        self.start_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'KagemaFM-Backend-Tester/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          expected_status: int = 200, timeout: int = 10) -> Dict[str, Any]:
        """Make HTTP request with error handling and performance tracking"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    content = await response.text()
                    
                    if response.status == expected_status:
                        try:
                            json_data = json.loads(content)
                            return {
                                'success': True,
                                'status_code': response.status,
                                'data': json_data,
                                'response_time_ms': response_time,
                                'content_length': len(content)
                            }
                        except json.JSONDecodeError:
                            return {
                                'success': True,
                                'status_code': response.status,
                                'data': content,
                                'response_time_ms': response_time,
                                'content_length': len(content)
                            }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'error': content,
                            'response_time_ms': response_time
                        }
                        
            elif method.upper() == 'POST':
                json_data = json.dumps(data) if data else None
                async with self.session.post(url, data=json_data, 
                                           timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    
                    if response.status == expected_status:
                        try:
                            json_response = json.loads(content)
                            return {
                                'success': True,
                                'status_code': response.status,
                                'data': json_response,
                                'response_time_ms': response_time,
                                'content_length': len(content)
                            }
                        except json.JSONDecodeError:
                            return {
                                'success': True,
                                'status_code': response.status,
                                'data': content,
                                'response_time_ms': response_time,
                                'content_length': len(content)
                            }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'error': content,
                            'response_time_ms': response_time
                        }
                        
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'error': 'Request timeout',
                'response_time_ms': response_time
            }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': response_time
            }
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", 
                       response_time: float = 0, critical: bool = False):
        """Log test result with details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL" if critical else "⚠️ MINOR FAIL"
            
        result = {
            'test_name': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_time_ms': response_time,
            'critical': critical,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        logger.info(f"{status} - {test_name} ({response_time:.0f}ms) - {details}")
        
    async def test_core_api_endpoints(self):
        """Test Core API Endpoints - Critical for system functionality"""
        logger.info("🔍 Testing Core API Endpoints...")
        
        # Test API Root
        result = await self.make_request('GET', '/')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'message' in data and 'version' in data:
                self.log_test_result(
                    "API Root Endpoint", True, 
                    f"API v{data.get('version', 'unknown')} responding", 
                    result['response_time_ms'], critical=True
                )
            else:
                self.log_test_result(
                    "API Root Endpoint", False, 
                    "Invalid response format", 
                    result['response_time_ms'], critical=True
                )
        else:
            self.log_test_result(
                "API Root Endpoint", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0), critical=True
            )
        
        # Test Basic Station Info
        result = await self.make_request('GET', '/station-info')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'streamUrl' in data and 'name' in data:
                self.log_test_result(
                    "Basic Station Info", True, 
                    f"Station: {data.get('name', 'Unknown')}", 
                    result['response_time_ms'], critical=True
                )
            else:
                self.log_test_result(
                    "Basic Station Info", False, 
                    "Missing required fields", 
                    result['response_time_ms'], critical=True
                )
        else:
            self.log_test_result(
                "Basic Station Info", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0), critical=True
            )
            
        # Test App Info
        result = await self.make_request('GET', '/app/info')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'name' in data and 'version' in data:
                self.log_test_result(
                    "App Info Endpoint", True, 
                    f"App: {data.get('name', 'Unknown')} v{data.get('version', 'unknown')}", 
                    result['response_time_ms']
                )
            else:
                self.log_test_result(
                    "App Info Endpoint", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "App Info Endpoint", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
            
        # Test App Version (for ERR_NGROK_3200 resolution persistence)
        result = await self.make_request('GET', '/app/version')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'version' in data and 'external_sources' in data:
                update_available = data.get('update_available', True)
                self.log_test_result(
                    "App Version Check", True, 
                    f"Version: {data.get('version', 'unknown')}, Update available: {update_available}", 
                    result['response_time_ms']
                )
                
                # Check for no legacy ngrok references
                external_sources = data.get('external_sources', {})
                ngrok_found = any('ngrok' in str(value).lower() for value in external_sources.values())
                if not ngrok_found:
                    self.log_test_result(
                        "ERR_NGROK_3200 Resolution Check", True, 
                        "No legacy ngrok references found in external sources", 
                        result['response_time_ms'], critical=True
                    )
                else:
                    self.log_test_result(
                        "ERR_NGROK_3200 Resolution Check", False, 
                        "Legacy ngrok references still present", 
                        result['response_time_ms'], critical=True
                    )
            else:
                self.log_test_result(
                    "App Version Check", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "App Version Check", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
    
    async def test_database_connectivity(self):
        """Test Database Connectivity and Data Retrieval"""
        logger.info("🔍 Testing Database Connectivity...")
        
        # Test language detection (requires database)
        test_location = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi coordinates
        result = await self.make_request('POST', '/language/detect', test_location)
        
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'detected_language' in data:
                detected_lang = data.get('detected_language', 'unknown')
                confidence = data.get('confidence', 0)
                self.log_test_result(
                    "Database Language Detection", True, 
                    f"Detected: {detected_lang} (confidence: {confidence})", 
                    result['response_time_ms'], critical=True
                )
            else:
                self.log_test_result(
                    "Database Language Detection", False, 
                    "Invalid response format", 
                    result['response_time_ms'], critical=True
                )
        else:
            self.log_test_result(
                "Database Language Detection", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0), critical=True
            )
            
        # Test supported languages (database-backed)
        result = await self.make_request('GET', '/languages')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'languages' in data:
                lang_count = len(data.get('languages', []))
                self.log_test_result(
                    "Supported Languages", True, 
                    f"{lang_count} languages supported", 
                    result['response_time_ms']
                )
            else:
                self.log_test_result(
                    "Supported Languages", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "Supported Languages", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
    
    async def test_service_integration(self):
        """Test Service Integration and Microservices Communication"""
        logger.info("🔍 Testing Service Integration...")
        
        # Test personalized content (integrates multiple services)
        test_request = {
            "location": {"latitude": -1.2921, "longitude": 36.8219},
            "preferences": {"offline_mode": False, "preferred_language": "en"}
        }
        
        result = await self.make_request('POST', '/personalized-content/multilingual', test_request, timeout=15)
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'radio_streams' in data:
                radio_streams = data.get('radio_streams', {})
                main_station = radio_streams.get('main_station', {})
                alternatives = radio_streams.get('alternative_streams', [])
                
                self.log_test_result(
                    "Personalized Content Integration", True, 
                    f"Main station + {len(alternatives)} alternatives", 
                    result['response_time_ms'], critical=True
                )
                
                # Verify radio_streams structure is complete
                if main_station and alternatives:
                    self.log_test_result(
                        "Radio Streams Data Structure", True, 
                        "Complete radio_streams data with main + alternatives", 
                        result['response_time_ms'], critical=True
                    )
                else:
                    self.log_test_result(
                        "Radio Streams Data Structure", False, 
                        "Incomplete radio_streams data structure", 
                        result['response_time_ms'], critical=True
                    )
            else:
                self.log_test_result(
                    "Personalized Content Integration", False, 
                    "Missing radio_streams data", 
                    result['response_time_ms'], critical=True
                )
        else:
            self.log_test_result(
                "Personalized Content Integration", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0), critical=True
            )
            
        # Test satellite connectivity
        result = await self.make_request('GET', '/satellite/status')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'connection_type' in data:
                conn_type = data.get('connection_type', 'unknown')
                signal_strength = data.get('signal_strength', 'unknown')
                self.log_test_result(
                    "Satellite Connectivity", True, 
                    f"Connection: {conn_type}, Signal: {signal_strength}", 
                    result['response_time_ms']
                )
            else:
                self.log_test_result(
                    "Satellite Connectivity", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "Satellite Connectivity", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
    
    async def test_voice_ai_integration(self):
        """Test Voice AI Integration"""
        logger.info("🔍 Testing Voice AI Integration...")
        
        # Test voice command interpretation
        test_commands = [
            {"text": "play music", "context": "radio"},
            {"text": "pause", "context": "radio"},
            {"text": "next station", "context": "radio"},
            {"text": "volume up", "context": "radio"},
            {"text": "search for jazz music", "context": "radio"},
            {"text": "tune to classical station", "context": "radio"}
        ]
        
        successful_commands = 0
        total_commands = len(test_commands)
        
        for cmd in test_commands:
            result = await self.make_request('POST', '/voice/interpret', cmd)
            if result['success']:
                data = result['data']
                if isinstance(data, dict) and 'intent' in data and 'confidence' in data:
                    confidence = data.get('confidence', 0)
                    intent = data.get('intent', 'unknown')
                    successful_commands += 1
                    self.log_test_result(
                        f"Voice Command: {cmd['text']}", True, 
                        f"Intent: {intent}, Confidence: {confidence}", 
                        result['response_time_ms']
                    )
                else:
                    self.log_test_result(
                        f"Voice Command: {cmd['text']}", False, 
                        "Invalid response format", 
                        result['response_time_ms']
                    )
            else:
                self.log_test_result(
                    f"Voice Command: {cmd['text']}", False, 
                    f"Failed: {result.get('error', 'Unknown error')}", 
                    result.get('response_time_ms', 0)
                )
        
        # Overall voice AI success rate
        success_rate = (successful_commands / total_commands) * 100
        self.log_test_result(
            "Voice AI Integration Overall", success_rate >= 80, 
            f"{successful_commands}/{total_commands} commands successful ({success_rate:.1f}%)", 
            0, critical=True
        )
        
        # Test voice intents and help
        result = await self.make_request('GET', '/voice/intents')
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'intents' in data:
                intent_count = len(data.get('intents', []))
                self.log_test_result(
                    "Voice Intents List", True, 
                    f"{intent_count} intents available", 
                    result['response_time_ms']
                )
            else:
                self.log_test_result(
                    "Voice Intents List", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "Voice Intents List", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
    
    async def test_radio_stream_accessibility(self):
        """Test Radio Stream URLs for Accessibility"""
        logger.info("🔍 Testing Radio Stream Accessibility...")
        
        # Get radio streams
        result = await self.make_request('GET', '/radio/streams')
        if result['success']:
            data = result['data']
            main_station = data.get('main_station', {})
            alternatives = data.get('alternative_streams', [])
            
            # Test main station stream
            if main_station and 'streamUrl' in main_station:
                stream_url = main_station['streamUrl']
                accessible = await self.test_stream_url(stream_url)
                self.log_test_result(
                    f"Main Stream: {main_station.get('name', 'Unknown')}", accessible, 
                    f"URL: {stream_url}", 0, critical=True
                )
            
            # Test alternative streams
            accessible_streams = 0
            for stream in alternatives:
                if 'streamUrl' in stream:
                    stream_url = stream['streamUrl']
                    accessible = await self.test_stream_url(stream_url)
                    if accessible:
                        accessible_streams += 1
                    self.log_test_result(
                        f"Alt Stream: {stream.get('name', 'Unknown')}", accessible, 
                        f"URL: {stream_url}", 0
                    )
            
            # Overall stream accessibility
            total_streams = len(alternatives) + (1 if main_station else 0)
            accessible_total = accessible_streams + (1 if main_station else 0)
            accessibility_rate = (accessible_total / total_streams) * 100 if total_streams > 0 else 0
            
            self.log_test_result(
                "Radio Stream Accessibility Overall", accessibility_rate >= 80, 
                f"{accessible_total}/{total_streams} streams accessible ({accessibility_rate:.1f}%)", 
                0, critical=True
            )
        else:
            self.log_test_result(
                "Radio Streams Endpoint", False, 
                f"Failed to get streams: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0), critical=True
            )
    
    async def test_stream_url(self, stream_url: str) -> bool:
        """Test if a stream URL is accessible"""
        try:
            async with self.session.head(stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                # Check for audio content types or successful response
                content_type = response.headers.get('content-type', '').lower()
                is_audio = any(audio_type in content_type for audio_type in 
                             ['audio/', 'application/ogg', 'video/mp2t'])
                
                # Check for ICY streaming headers (common for radio streams)
                has_icy_headers = any(header.startswith('icy-') for header in response.headers.keys())
                
                return response.status == 200 and (is_audio or has_icy_headers)
        except:
            return False
    
    async def test_performance_metrics(self):
        """Test Performance After Clean Start"""
        logger.info("🔍 Testing Performance Metrics...")
        
        # Collect response times from previous tests
        response_times = [result['response_time_ms'] for result in self.test_results 
                         if result.get('response_time_ms', 0) > 0]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance thresholds
            avg_acceptable = avg_response_time < 2000  # 2 seconds average
            max_acceptable = max_response_time < 5000  # 5 seconds max
            
            self.log_test_result(
                "Average Response Time", avg_acceptable, 
                f"{avg_response_time:.0f}ms (target: <2000ms)", 
                avg_response_time, critical=True
            )
            
            self.log_test_result(
                "Maximum Response Time", max_acceptable, 
                f"{max_response_time:.0f}ms (target: <5000ms)", 
                max_response_time
            )
            
            self.log_test_result(
                "Minimum Response Time", True, 
                f"{min_response_time:.0f}ms", 
                min_response_time
            )
        
        # Test concurrent requests
        await self.test_concurrent_requests()
    
    async def test_concurrent_requests(self):
        """Test system handling of concurrent requests"""
        logger.info("🔍 Testing Concurrent Request Handling...")
        
        # Create multiple concurrent requests
        concurrent_tasks = []
        endpoints_to_test = [
            '/',
            '/station-info',
            '/languages',
            '/radio/streams',
            '/satellite/status'
        ]
        
        start_time = time.time()
        
        for endpoint in endpoints_to_test:
            task = self.make_request('GET', endpoint)
            concurrent_tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        
        total_time = (time.time() - start_time) * 1000
        successful_concurrent = sum(1 for result in results 
                                  if isinstance(result, dict) and result.get('success', False))
        
        self.log_test_result(
            "Concurrent Request Handling", successful_concurrent >= 4, 
            f"{successful_concurrent}/{len(endpoints_to_test)} concurrent requests successful in {total_time:.0f}ms", 
            total_time, critical=True
        )
    
    async def test_error_handling(self):
        """Test Error Handling and Edge Cases"""
        logger.info("🔍 Testing Error Handling...")
        
        # Test invalid endpoints
        result = await self.make_request('GET', '/invalid-endpoint', expected_status=404)
        self.log_test_result(
            "Invalid Endpoint Handling", result['status_code'] == 404, 
            f"Status: {result['status_code']}", 
            result.get('response_time_ms', 0)
        )
        
        # Test invalid POST data
        result = await self.make_request('POST', '/language/detect', 
                                       {"invalid": "data"}, expected_status=422)
        self.log_test_result(
            "Invalid POST Data Handling", result['status_code'] in [400, 422], 
            f"Status: {result['status_code']}", 
            result.get('response_time_ms', 0)
        )
        
        # Test malformed JSON
        try:
            url = f"{self.base_url}/language/detect"
            async with self.session.post(url, data="invalid json") as response:
                self.log_test_result(
                    "Malformed JSON Handling", response.status in [400, 422], 
                    f"Status: {response.status}", 0
                )
        except Exception as e:
            self.log_test_result(
                "Malformed JSON Handling", False, 
                f"Exception: {str(e)}", 0
            )
    
    async def test_integration_endpoints(self):
        """Test Integration Endpoints (iHeartRadio, Streema, etc.)"""
        logger.info("🔍 Testing Integration Endpoints...")
        
        # Test platform integrations initialization
        integration_types = ["google_maps", "spotify", "voice_control", "general"]
        
        for integration_type in integration_types:
            result = await self.make_request('POST', '/integrations/initialize', 
                                           {"type": integration_type})
            if result['success']:
                data = result['data']
                if isinstance(data, dict) and 'status' in data:
                    status = data.get('status', 'unknown')
                    self.log_test_result(
                        f"Integration: {integration_type}", status == 'initialized', 
                        f"Status: {status}", 
                        result['response_time_ms']
                    )
                else:
                    self.log_test_result(
                        f"Integration: {integration_type}", False, 
                        "Invalid response format", 
                        result['response_time_ms']
                    )
            else:
                self.log_test_result(
                    f"Integration: {integration_type}", False, 
                    f"Failed: {result.get('error', 'Unknown error')}", 
                    result.get('response_time_ms', 0)
                )
        
        # Test content compliance
        compliance_request = {
            "country_code": "KE",
            "language_code": "en",
            "content_types": ["radio_streams", "music"]
        }
        
        result = await self.make_request('POST', '/compliance/disclaimers', compliance_request)
        if result['success']:
            data = result['data']
            if isinstance(data, dict) and 'content_disclaimers' in data:
                disclaimer_count = len(data.get('content_disclaimers', []))
                self.log_test_result(
                    "Content Compliance", True, 
                    f"{disclaimer_count} disclaimers for KE", 
                    result['response_time_ms']
                )
            else:
                self.log_test_result(
                    "Content Compliance", False, 
                    "Invalid response format", 
                    result['response_time_ms']
                )
        else:
            self.log_test_result(
                "Content Compliance", False, 
                f"Failed: {result.get('error', 'Unknown error')}", 
                result.get('response_time_ms', 0)
            )
    
    def generate_summary_report(self):
        """Generate comprehensive test summary report"""
        total_time = (time.time() - self.start_time) if self.start_time else 0
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Count critical failures
        critical_failures = [result for result in self.test_results 
                           if not result['success'] and result.get('critical', False)]
        
        # Calculate average response time
        response_times = [result['response_time_ms'] for result in self.test_results 
                         if result.get('response_time_ms', 0) > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE KAGEMA FM BACKEND TESTING COMPLETE")
        print("="*80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   • Total Tests: {self.total_tests}")
        print(f"   • Passed: {self.passed_tests} ✅")
        print(f"   • Failed: {self.failed_tests} ❌")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Critical Failures: {len(critical_failures)}")
        print(f"   • Average Response Time: {avg_response_time:.0f}ms")
        print(f"   • Total Test Duration: {total_time:.1f}s")
        
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        if success_rate >= 95 and len(critical_failures) == 0:
            print("   ✅ PRODUCTION READY - All critical systems operational")
        elif success_rate >= 85 and len(critical_failures) <= 2:
            print("   ⚠️ MOSTLY READY - Minor issues present, monitor closely")
        else:
            print("   ❌ NOT READY - Critical issues require resolution")
        
        # ERR_NGROK_3200 Resolution Status
        ngrok_tests = [result for result in self.test_results 
                      if 'ngrok' in result['test_name'].lower()]
        if ngrok_tests:
            ngrok_resolved = all(result['success'] for result in ngrok_tests)
            print(f"\n🔧 ERR_NGROK_3200 RESOLUTION STATUS:")
            if ngrok_resolved:
                print("   ✅ RESOLVED - No legacy ngrok references detected")
            else:
                print("   ❌ UNRESOLVED - Legacy ngrok issues persist")
        
        # Performance Assessment
        print(f"\n⚡ PERFORMANCE ASSESSMENT:")
        if avg_response_time < 1000:
            print("   ✅ EXCELLENT - Average response time under 1 second")
        elif avg_response_time < 2000:
            print("   ✅ GOOD - Average response time under 2 seconds")
        else:
            print("   ⚠️ NEEDS IMPROVEMENT - Response times above optimal")
        
        # Critical Failures Detail
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES REQUIRING ATTENTION:")
            for failure in critical_failures:
                print(f"   • {failure['test_name']}: {failure['details']}")
        
        print("\n" + "="*80)
        
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'success_rate': success_rate,
            'critical_failures': len(critical_failures),
            'avg_response_time': avg_response_time,
            'total_duration': total_time,
            'deployment_ready': success_rate >= 85 and len(critical_failures) <= 2
        }
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Kagema FM Backend Testing...")
        print("🎯 Focus: Post-Cache-Clear System Validation & ERR_NGROK_3200 Resolution Persistence")
        print("="*80)
        
        self.start_time = time.time()
        
        try:
            await self.setup_session()
            
            # Core System Functionality Tests
            await self.test_core_api_endpoints()
            
            # Database Connectivity Tests
            await self.test_database_connectivity()
            
            # Service Integration Tests
            await self.test_service_integration()
            
            # Voice AI Integration Tests
            await self.test_voice_ai_integration()
            
            # Radio Stream Accessibility Tests
            await self.test_radio_stream_accessibility()
            
            # Performance Tests
            await self.test_performance_metrics()
            
            # Error Handling Tests
            await self.test_error_handling()
            
            # Integration Endpoints Tests
            await self.test_integration_endpoints()
            
            # Generate final report
            summary = self.generate_summary_report()
            
            return summary
            
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
            return {
                'error': str(e),
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests
            }
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = KagemaFMBackendTester()
    summary = await tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if summary.get('deployment_ready', False):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    asyncio.run(main())