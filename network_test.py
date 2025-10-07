#!/usr/bin/env python3
"""
Comprehensive Network Connectivity and Stability Testing - Phase 2
Focus: Network diagnostics, performance testing, and stability testing for Kagema FM backend
Per review request: Test all critical API endpoints, measure response times, test concurrent connections,
check for network timeout errors, monitor backend service health, verify CORS configuration
"""

import asyncio
import aiohttp
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://car-radio-app.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class NetworkConnectivityTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.performance_metrics = {}
        
        print(f"🌐 Network Testing Backend URL: {BACKEND_URL}")
        print(f"📡 API Base URL: {API_BASE_URL}")
        
    async def setup_session(self):
        """Setup aiohttp session with proper timeout and connection settings"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'Content-Type': 'application/json'}
        )
    
    async def cleanup_session(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def ping_endpoint(self, endpoint: str, method: str = 'GET', data: dict = None) -> Dict[str, Any]:
        """Test single endpoint with latency measurement"""
        start_time = time.time()
        try:
            if method == 'GET':
                async with self.session.get(f"{API_BASE_URL}{endpoint}") as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    content = await response.text()
                    return {
                        'endpoint': endpoint,
                        'method': method,
                        'status_code': response.status,
                        'response_time_ms': response_time,
                        'content_length': len(content),
                        'success': 200 <= response.status < 300,
                        'headers': dict(response.headers),
                        'error': None
                    }
            elif method == 'POST':
                async with self.session.post(f"{API_BASE_URL}{endpoint}", json=data) as response:
                    response_time = (time.time() - start_time) * 1000
                    content = await response.text()
                    return {
                        'endpoint': endpoint,
                        'method': method,
                        'status_code': response.status,
                        'response_time_ms': response_time,
                        'content_length': len(content),
                        'success': 200 <= response.status < 300,
                        'headers': dict(response.headers),
                        'error': None
                    }
        except asyncio.TimeoutError:
            return {
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'response_time_ms': (time.time() - start_time) * 1000,
                'content_length': 0,
                'success': False,
                'headers': {},
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'response_time_ms': (time.time() - start_time) * 1000,
                'content_length': 0,
                'success': False,
                'headers': {},
                'error': str(e)
            }
    
    async def test_critical_endpoints(self) -> List[Dict[str, Any]]:
        """Test all critical API endpoints as specified in review request"""
        print("🔍 Testing Critical API Endpoints...")
        
        # Critical endpoints from review request
        endpoints = [
            {'endpoint': '/', 'method': 'GET'},
            {'endpoint': '/station-info', 'method': 'GET'},
            {'endpoint': '/personalized-content/multilingual', 'method': 'POST', 
             'data': {
                 'location': {'latitude': -1.286389, 'longitude': 36.817223},
                 'preferences': {
                     'user_id': 'test-network-user',
                     'preferred_language': 'en',
                     'offline_mode': False,
                     'user_age': 25,
                     'theme': 'dark',
                     'notifications': {'enabled': True},
                     'audio': {'quality': 'high', 'volume': 0.8},
                     'data_saver': False,
                     'analytics_enabled': True
                 }
             }},
            {'endpoint': '/station-info/multilingual', 'method': 'POST',
             'data': {'latitude': -1.286389, 'longitude': 36.817223}},
            {'endpoint': '/language/detect', 'method': 'POST',
             'data': {'latitude': -1.286389, 'longitude': 36.817223}},
            {'endpoint': '/languages', 'method': 'GET'},
            {'endpoint': '/compliance/disclaimers', 'method': 'POST',
             'data': {'country_code': 'KE', 'language_code': 'en', 'content_types': ['radio_streams']}},
            {'endpoint': '/satellite/status', 'method': 'GET'},
            {'endpoint': '/integrations/initialize', 'method': 'POST',
             'data': {'type': 'general', 'config': {}}}
        ]
        
        results = []
        for endpoint_config in endpoints:
            result = await self.ping_endpoint(
                endpoint_config['endpoint'], 
                endpoint_config['method'],
                endpoint_config.get('data')
            )
            results.append(result)
            print(f"  {'✅' if result['success'] else '❌'} {endpoint_config['method']} {endpoint_config['endpoint']} - {result['response_time_ms']:.1f}ms")
        
        return results
    
    async def test_concurrent_connections(self, endpoint: str = '/', concurrent_users: int = 10) -> Dict[str, Any]:
        """Test concurrent connections to simulate multiple users"""
        print(f"🚀 Testing Concurrent Connections ({concurrent_users} users)...")
        
        start_time = time.time()
        tasks = []
        
        for i in range(concurrent_users):
            task = self.ping_endpoint(endpoint)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = [r for r in results if isinstance(r, dict) and r['success']]
        failed_requests = [r for r in results if isinstance(r, dict) and not r['success']]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        response_times = [r['response_time_ms'] for r in successful_requests]
        
        return {
            'concurrent_users': concurrent_users,
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'exceptions': len(exceptions),
            'success_rate': len(successful_requests) / len(results) * 100,
            'total_time_seconds': total_time,
            'requests_per_second': len(results) / total_time,
            'avg_response_time_ms': statistics.mean(response_times) if response_times else 0,
            'min_response_time_ms': min(response_times) if response_times else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'median_response_time_ms': statistics.median(response_times) if response_times else 0
        }
    
    async def test_bandwidth_monitoring(self) -> Dict[str, Any]:
        """Monitor API response times and data transfer rates"""
        print("📊 Testing Bandwidth and Data Transfer Rates...")
        
        # Test different endpoints with varying data sizes
        test_cases = [
            {'endpoint': '/', 'method': 'GET', 'description': 'Small response'},
            {'endpoint': '/languages', 'method': 'GET', 'description': 'Medium response'},
            {'endpoint': '/personalized-content/multilingual', 'method': 'POST', 
             'data': {
                 'location': {'latitude': -1.286389, 'longitude': 36.817223},
                 'preferences': {
                     'user_id': 'test-network-user',
                     'preferred_language': 'en',
                     'offline_mode': False,
                     'user_age': 25,
                     'theme': 'dark',
                     'notifications': {'enabled': True},
                     'audio': {'quality': 'high', 'volume': 0.8},
                     'data_saver': False,
                     'analytics_enabled': True
                 }
             },
             'description': 'Large response with personalized content'}
        ]
        
        bandwidth_results = []
        for test_case in test_cases:
            result = await self.ping_endpoint(
                test_case['endpoint'], 
                test_case['method'],
                test_case.get('data')
            )
            
            if result['success'] and result['response_time_ms'] > 0:
                # Calculate data transfer rate (bytes per second)
                transfer_rate_bps = (result['content_length'] / (result['response_time_ms'] / 1000))
                transfer_rate_kbps = transfer_rate_bps / 1024
                
                bandwidth_results.append({
                    'endpoint': result['endpoint'],
                    'description': test_case['description'],
                    'content_length_bytes': result['content_length'],
                    'response_time_ms': result['response_time_ms'],
                    'transfer_rate_kbps': transfer_rate_kbps,
                    'success': True
                })
            else:
                bandwidth_results.append({
                    'endpoint': result['endpoint'],
                    'description': test_case['description'],
                    'content_length_bytes': result['content_length'],
                    'response_time_ms': result['response_time_ms'],
                    'transfer_rate_kbps': 0,
                    'success': False,
                    'error': result.get('error')
                })
        
        return {
            'bandwidth_tests': bandwidth_results,
            'avg_transfer_rate_kbps': statistics.mean([r['transfer_rate_kbps'] for r in bandwidth_results if r['success']]) if any(r['success'] for r in bandwidth_results) else 0
        }
    
    async def test_cors_configuration(self) -> Dict[str, Any]:
        """Verify CORS configuration for frontend connectivity"""
        print("🌐 Testing CORS Configuration...")
        
        # Test CORS headers
        result = await self.ping_endpoint('/')
        
        cors_headers = {
            'access-control-allow-origin': result['headers'].get('access-control-allow-origin'),
            'access-control-allow-methods': result['headers'].get('access-control-allow-methods'),
            'access-control-allow-headers': result['headers'].get('access-control-allow-headers'),
            'access-control-allow-credentials': result['headers'].get('access-control-allow-credentials')
        }
        
        cors_properly_configured = (
            cors_headers['access-control-allow-origin'] is not None and
            cors_headers['access-control-allow-methods'] is not None
        )
        
        return {
            'cors_configured': cors_properly_configured,
            'cors_headers': cors_headers,
            'frontend_compatible': cors_headers['access-control-allow-origin'] in ['*', BACKEND_URL]
        }
    
    async def test_connection_stability(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Test connection stability over time"""
        print(f"⏱️ Testing Connection Stability ({duration_seconds}s)...")
        
        start_time = time.time()
        test_results = []
        request_count = 0
        
        while (time.time() - start_time) < duration_seconds:
            result = await self.ping_endpoint('/')
            test_results.append(result)
            request_count += 1
            await asyncio.sleep(1)  # Test every second
        
        successful_requests = [r for r in test_results if r['success']]
        failed_requests = [r for r in test_results if not r['success']]
        
        # Check for connection drops (consecutive failures)
        connection_drops = 0
        consecutive_failures = 0
        max_consecutive_failures = 0
        
        for result in test_results:
            if not result['success']:
                consecutive_failures += 1
                max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)
            else:
                if consecutive_failures >= 2:  # Consider 2+ consecutive failures as a drop
                    connection_drops += 1
                consecutive_failures = 0
        
        response_times = [r['response_time_ms'] for r in successful_requests]
        
        return {
            'duration_seconds': duration_seconds,
            'total_requests': len(test_results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'connection_drops': connection_drops,
            'max_consecutive_failures': max_consecutive_failures,
            'stability_percentage': len(successful_requests) / len(test_results) * 100,
            'avg_response_time_ms': statistics.mean(response_times) if response_times else 0,
            'response_time_variance': statistics.variance(response_times) if len(response_times) > 1 else 0
        }
    
    async def test_stream_accessibility(self) -> Dict[str, Any]:
        """Test accessibility of radio stream URLs"""
        print("📡 Testing Radio Stream Accessibility...")
        
        # Get stream URLs from personalized content API
        personalized_content_result = await self.ping_endpoint(
            '/personalized-content/multilingual',
            'POST',
            {
                'location': {'latitude': -1.286389, 'longitude': 36.817223},
                'preferences': {
                    'user_id': 'test-network-user',
                    'preferred_language': 'en',
                    'offline_mode': False,
                    'user_age': 25,
                    'theme': 'dark',
                    'notifications': {'enabled': True},
                    'audio': {'quality': 'high', 'volume': 0.8},
                    'data_saver': False,
                    'analytics_enabled': True
                }
            }
        )
        
        stream_results = []
        
        if personalized_content_result['success']:
            try:
                # Parse the response to get stream URLs
                async with self.session.post(
                    f"{API_BASE_URL}/personalized-content/multilingual",
                    json={
                        'location': {'latitude': -1.286389, 'longitude': 36.817223},
                        'preferences': {
                            'user_id': 'test-network-user',
                            'preferred_language': 'en',
                            'offline_mode': False,
                            'user_age': 25,
                            'theme': 'dark',
                            'notifications': {'enabled': True},
                            'audio': {'quality': 'high', 'volume': 0.8},
                            'data_saver': False,
                            'analytics_enabled': True
                        }
                    }
                ) as response:
                    content = await response.json()
                    radio_streams = content.get('radio_streams', {})
                    
                    # Test main station stream
                    main_station = radio_streams.get('main_station', {})
                    if main_station.get('streamUrl'):
                        stream_result = await self.test_stream_url(main_station['streamUrl'], 'Main Station')
                        stream_results.append(stream_result)
                    
                    # Test alternative streams
                    alternative_streams = radio_streams.get('alternative_streams', [])
                    for stream in alternative_streams[:5]:  # Test first 5 alternative streams
                        if stream.get('streamUrl'):
                            stream_result = await self.test_stream_url(stream['streamUrl'], stream.get('name', 'Unknown'))
                            stream_results.append(stream_result)
                            
            except Exception as e:
                stream_results.append({
                    'stream_name': 'API Error',
                    'stream_url': 'N/A',
                    'accessible': False,
                    'error': f"Failed to parse API response: {str(e)}"
                })
        
        working_streams = [s for s in stream_results if s['accessible']]
        
        return {
            'total_streams_tested': len(stream_results),
            'working_streams': len(working_streams),
            'stream_accessibility_rate': len(working_streams) / len(stream_results) * 100 if stream_results else 0,
            'stream_details': stream_results
        }
    
    async def test_stream_url(self, stream_url: str, stream_name: str) -> Dict[str, Any]:
        """Test individual stream URL accessibility"""
        try:
            start_time = time.time()
            async with self.session.head(stream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'stream_name': stream_name,
                    'stream_url': stream_url,
                    'accessible': response.status == 200,
                    'status_code': response.status,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'response_time_ms': response_time,
                    'icy_headers': {k: v for k, v in response.headers.items() if k.lower().startswith('icy-')},
                    'error': None
                }
        except Exception as e:
            return {
                'stream_name': stream_name,
                'stream_url': stream_url,
                'accessible': False,
                'status_code': 0,
                'content_type': 'unknown',
                'response_time_ms': 0,
                'icy_headers': {},
                'error': str(e)
            }
    
    async def run_comprehensive_network_test(self) -> Dict[str, Any]:
        """Run comprehensive network connectivity and stability testing"""
        print("🎵 COMPREHENSIVE NETWORK CONNECTIVITY AND STABILITY TESTING - PHASE 2")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # 1. Test critical API endpoints
            endpoint_results = await self.test_critical_endpoints()
            
            # 2. Test concurrent connections
            concurrent_results = await self.test_concurrent_connections(concurrent_users=10)
            
            # 3. Test bandwidth monitoring
            bandwidth_results = await self.test_bandwidth_monitoring()
            
            # 4. Test CORS configuration
            cors_results = await self.test_cors_configuration()
            
            # 5. Test connection stability
            stability_results = await self.test_connection_stability(duration_seconds=30)
            
            # 6. Test stream accessibility
            stream_results = await self.test_stream_accessibility()
            
            # Calculate overall performance metrics
            successful_endpoints = [r for r in endpoint_results if r['success']]
            response_times = [r['response_time_ms'] for r in successful_endpoints]
            
            overall_results = {
                'test_summary': {
                    'total_endpoints_tested': len(endpoint_results),
                    'successful_endpoints': len(successful_endpoints),
                    'endpoint_success_rate': len(successful_endpoints) / len(endpoint_results) * 100,
                    'avg_response_time_ms': statistics.mean(response_times) if response_times else 0,
                    'max_response_time_ms': max(response_times) if response_times else 0,
                    'performance_target_met': all(rt < 2000 for rt in response_times),  # Under 2 seconds
                    'backend_url': BACKEND_URL
                },
                'endpoint_tests': endpoint_results,
                'concurrent_connection_test': concurrent_results,
                'bandwidth_monitoring': bandwidth_results,
                'cors_configuration': cors_results,
                'connection_stability': stability_results,
                'stream_accessibility': stream_results
            }
            
            return overall_results
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = NetworkConnectivityTester()
    results = await tester.run_comprehensive_network_test()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE NETWORK TESTING RESULTS")
    print("=" * 80)
    
    summary = results['test_summary']
    print(f"🎯 OVERALL PERFORMANCE:")
    print(f"  • Backend URL: {summary['backend_url']}")
    print(f"  • Endpoints Tested: {summary['total_endpoints_tested']}")
    print(f"  • Success Rate: {summary['endpoint_success_rate']:.1f}%")
    print(f"  • Average Response Time: {summary['avg_response_time_ms']:.1f}ms")
    print(f"  • Max Response Time: {summary['max_response_time_ms']:.1f}ms")
    print(f"  • Performance Target Met (< 2s): {'✅' if summary['performance_target_met'] else '❌'}")
    
    print(f"\n🚀 CONCURRENT CONNECTION TEST:")
    concurrent = results['concurrent_connection_test']
    print(f"  • Concurrent Users: {concurrent['concurrent_users']}")
    print(f"  • Success Rate: {concurrent['success_rate']:.1f}%")
    print(f"  • Requests/Second: {concurrent['requests_per_second']:.1f}")
    print(f"  • Avg Response Time: {concurrent['avg_response_time_ms']:.1f}ms")
    
    print(f"\n📊 BANDWIDTH MONITORING:")
    bandwidth = results['bandwidth_monitoring']
    print(f"  • Average Transfer Rate: {bandwidth['avg_transfer_rate_kbps']:.1f} KB/s")
    for test in bandwidth['bandwidth_tests']:
        status = '✅' if test['success'] else '❌'
        print(f"  • {status} {test['description']}: {test['transfer_rate_kbps']:.1f} KB/s")
    
    print(f"\n🌐 CORS CONFIGURATION:")
    cors = results['cors_configuration']
    print(f"  • CORS Configured: {'✅' if cors['cors_configured'] else '❌'}")
    print(f"  • Frontend Compatible: {'✅' if cors['frontend_compatible'] else '❌'}")
    
    print(f"\n⏱️ CONNECTION STABILITY:")
    stability = results['connection_stability']
    print(f"  • Stability: {stability['stability_percentage']:.1f}%")
    print(f"  • Connection Drops: {stability['connection_drops']}")
    print(f"  • Max Consecutive Failures: {stability['max_consecutive_failures']}")
    
    print(f"\n📡 STREAM ACCESSIBILITY:")
    streams = results['stream_accessibility']
    print(f"  • Streams Tested: {streams['total_streams_tested']}")
    print(f"  • Working Streams: {streams['working_streams']}")
    print(f"  • Accessibility Rate: {streams['stream_accessibility_rate']:.1f}%")
    
    # Performance assessment
    print(f"\n🎉 PERFORMANCE ASSESSMENT:")
    performance_score = 0
    max_score = 6
    
    if summary['endpoint_success_rate'] >= 90:
        performance_score += 1
        print("  ✅ Endpoint Success Rate >= 90%")
    else:
        print("  ❌ Endpoint Success Rate < 90%")
    
    if summary['performance_target_met']:
        performance_score += 1
        print("  ✅ All endpoints respond under 2 seconds")
    else:
        print("  ❌ Some endpoints exceed 2 second target")
    
    if concurrent['success_rate'] >= 90:
        performance_score += 1
        print("  ✅ Concurrent connections handle well")
    else:
        print("  ❌ Concurrent connection issues detected")
    
    if cors['cors_configured']:
        performance_score += 1
        print("  ✅ CORS properly configured")
    else:
        print("  ❌ CORS configuration issues")
    
    if stability['stability_percentage'] >= 95:
        performance_score += 1
        print("  ✅ Connection stability excellent")
    else:
        print("  ❌ Connection stability issues detected")
    
    if streams['stream_accessibility_rate'] >= 70:
        performance_score += 1
        print("  ✅ Stream accessibility acceptable")
    else:
        print("  ❌ Stream accessibility issues")
    
    final_score = (performance_score / max_score) * 100
    print(f"\n🏆 FINAL NETWORK PERFORMANCE SCORE: {final_score:.1f}% ({performance_score}/{max_score})")
    
    if final_score >= 85:
        print("🎉 EXCELLENT - Network performance meets all requirements!")
    elif final_score >= 70:
        print("✅ GOOD - Network performance is acceptable with minor issues")
    else:
        print("⚠️ NEEDS IMPROVEMENT - Network performance issues require attention")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
