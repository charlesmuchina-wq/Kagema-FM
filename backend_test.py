#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Kagema FM Radio Station
Testing all critical radio streaming APIs and enhanced features per Phase 2 review request
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'frontend' / '.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class KagemaFMBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.start_time = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test result with timing information"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'response_time_ms': round(response_time * 1000, 2),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({response_time*1000:.0f}ms) - {details}")
        
    async def test_api_connectivity(self) -> bool:
        """Test basic API connectivity"""
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    expected_message = "Kagema FM Satellite & Offline Radio API"
                    if data.get("message") == expected_message:
                        self.log_test_result(
                            "API Root Connectivity", 
                            True, 
                            response_time,
                            f"API v{data.get('version', 'unknown')} responding correctly"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "API Root Connectivity", 
                            False, 
                            response_time,
                            f"Unexpected message: {data.get('message', 'none')}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "API Root Connectivity", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "API Root Connectivity", 
                False, 
                0,
                f"Connection error: {str(e)}"
            )
            return False
            
    async def test_station_info_basic(self) -> bool:
        """Test GET /api/station-info endpoint"""
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/station-info") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['name', 'description', 'streamUrl', 'frequency']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get('name') == 'Kagema FM':
                        self.log_test_result(
                            "Basic Station Info", 
                            True, 
                            response_time,
                            f"Complete station data with stream URL: {data.get('streamUrl', 'none')}"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Basic Station Info", 
                            False, 
                            response_time,
                            f"Missing fields: {missing_fields}" if missing_fields else "Invalid station name"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Basic Station Info", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Basic Station Info", 
                False, 
                0,
                f"Request error: {str(e)}"
            )
            return False
            
    async def test_multilingual_station_info(self) -> Dict[str, bool]:
        """Test POST /api/station-info/multilingual for different regions"""
        test_locations = {
            "Kenya": {"latitude": -1.2921, "longitude": 36.8219},  # Nairobi
            "Brazil": {"latitude": -23.5505, "longitude": -46.6333},  # São Paulo
            "Global": {"latitude": 40.7128, "longitude": -74.0060}  # New York
        }
        
        results = {}
        
        for region, location in test_locations.items():
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{API_BASE_URL}/station-info/multilingual",
                    json=location
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        required_fields = ['name', 'description', 'streamUrl', 'detected_language']
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            self.log_test_result(
                                f"Multilingual Station Info ({region})", 
                                True, 
                                response_time,
                                f"Language: {data.get('detected_language')}, Stream: {data.get('streamUrl')}"
                            )
                            results[region] = True
                        else:
                            self.log_test_result(
                                f"Multilingual Station Info ({region})", 
                                False, 
                                response_time,
                                f"Missing fields: {missing_fields}"
                            )
                            results[region] = False
                    else:
                        self.log_test_result(
                            f"Multilingual Station Info ({region})", 
                            False, 
                            response_time,
                            f"HTTP {response.status}"
                        )
                        results[region] = False
                        
            except Exception as e:
                self.log_test_result(
                    f"Multilingual Station Info ({region})", 
                    False, 
                    0,
                    f"Request error: {str(e)}"
                )
                results[region] = False
                
        return results
        
    async def test_personalized_content_multilingual(self) -> bool:
        """Test POST /api/personalized-content/multilingual - CRITICAL for frontend radio functionality"""
        try:
            # Test with Kenya location and basic preferences
            location = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
            preferences = {
                "user_id": "test_user_001",
                "preferred_language": "en",
                "theme": "dark",
                "offline_mode": False,
                "audio": {
                    "quality": "high",
                    "volume": 0.8,
                    "auto_play": True
                },
                "notifications": {
                    "enabled": True,
                    "news_updates": True,
                    "music_recommendations": True
                }
            }
            
            payload = {**location, **preferences}
            
            start_time = time.time()
            async with self.session.post(
                f"{API_BASE_URL}/personalized-content/multilingual",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for critical radio_streams data
                    has_radio_streams = 'radio_streams' in data
                    has_main_station = has_radio_streams and 'main_station' in data['radio_streams']
                    has_alternative_streams = has_radio_streams and 'alternative_streams' in data['radio_streams']
                    
                    # Check for other content sections
                    has_news = 'news' in data
                    has_music = 'music' in data
                    has_language_detection = 'language_detection' in data
                    
                    if has_radio_streams and has_main_station:
                        main_station = data['radio_streams']['main_station']
                        alt_streams_count = len(data['radio_streams'].get('alternative_streams', []))
                        
                        self.log_test_result(
                            "Personalized Content Multilingual", 
                            True, 
                            response_time,
                            f"Complete content with radio_streams: main + {alt_streams_count} alternatives, news: {has_news}, music: {has_music}"
                        )
                        return True
                    else:
                        missing_components = []
                        if not has_radio_streams:
                            missing_components.append("radio_streams")
                        if not has_main_station:
                            missing_components.append("main_station")
                            
                        self.log_test_result(
                            "Personalized Content Multilingual", 
                            False, 
                            response_time,
                            f"CRITICAL: Missing radio streaming data - {', '.join(missing_components)}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "Personalized Content Multilingual", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Personalized Content Multilingual", 
                False, 
                0,
                f"Request error: {str(e)}"
            )
            return False
            
    async def test_stream_accessibility(self) -> Dict[str, bool]:
        """Test accessibility of main Kagema FM stream and alternatives"""
        # Get stream URLs from the personalized content API first
        try:
            location = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
            preferences = {
                "user_id": "test_user_stream",
                "preferred_language": "en",
                "offline_mode": False,
                "audio": {"quality": "high", "volume": 0.8, "auto_play": True},
                "notifications": {"enabled": True, "news_updates": True, "music_recommendations": True}
            }
            
            payload = {**location, **preferences}
            
            async with self.session.post(
                f"{API_BASE_URL}/personalized-content/multilingual",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    radio_streams = data.get('radio_streams', {})
                    
                    # Test main station stream
                    main_station = radio_streams.get('main_station', {})
                    main_stream_url = main_station.get('streamUrl')
                    
                    # Test alternative streams
                    alternative_streams = radio_streams.get('alternative_streams', [])
                    
                    stream_results = {}
                    
                    # Test main stream
                    if main_stream_url:
                        stream_results['Main Kagema FM Stream'] = await self.test_single_stream(
                            main_stream_url, 
                            "Main Kagema FM Stream"
                        )
                    
                    # Test up to 5 alternative streams
                    for i, stream in enumerate(alternative_streams[:5]):
                        stream_name = stream.get('name', f'Alternative Stream {i+1}')
                        stream_url = stream.get('streamUrl')
                        if stream_url:
                            stream_results[stream_name] = await self.test_single_stream(
                                stream_url, 
                                stream_name
                            )
                    
                    return stream_results
                else:
                    self.log_test_result(
                        "Stream Accessibility Setup", 
                        False, 
                        0,
                        f"Failed to get stream URLs from API: HTTP {response.status}"
                    )
                    return {}
                    
        except Exception as e:
            self.log_test_result(
                "Stream Accessibility Setup", 
                False, 
                0,
                f"Error getting stream URLs: {str(e)}"
            )
            return {}
            
    async def test_single_stream(self, stream_url: str, stream_name: str) -> bool:
        """Test accessibility of a single audio stream"""
        try:
            start_time = time.time()
            async with self.session.head(stream_url, allow_redirects=True) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    icy_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('icy-')}
                    
                    is_audio = any(audio_type in content_type.lower() for audio_type in ['audio/', 'application/ogg'])
                    
                    if is_audio or icy_headers:
                        self.log_test_result(
                            f"Stream: {stream_name}", 
                            True, 
                            response_time,
                            f"Accessible - {content_type}, {len(icy_headers)} ICY headers"
                        )
                        return True
                    else:
                        self.log_test_result(
                            f"Stream: {stream_name}", 
                            False, 
                            response_time,
                            f"Not audio content: {content_type}"
                        )
                        return False
                else:
                    self.log_test_result(
                        f"Stream: {stream_name}", 
                        False, 
                        response_time,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                f"Stream: {stream_name}", 
                False, 
                0,
                f"Connection error: {str(e)}"
            )
            return False
            
    async def test_enhanced_features(self) -> Dict[str, bool]:
        """Test enhanced features from review request"""
        results = {}
        
        # Test language detection
        try:
            location = {"latitude": -1.2921, "longitude": 36.8219}  # Nairobi
            start_time = time.time()
            async with self.session.post(f"{API_BASE_URL}/language/detect", json=location) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_detection = 'detected_language' in data and 'confidence' in data
                    
                    self.log_test_result(
                        "Language Detection", 
                        has_detection, 
                        response_time,
                        f"Language: {data.get('detected_language', 'none')}, Confidence: {data.get('confidence', 0)}"
                    )
                    results['language_detection'] = has_detection
                else:
                    self.log_test_result("Language Detection", False, response_time, f"HTTP {response.status}")
                    results['language_detection'] = False
        except Exception as e:
            self.log_test_result("Language Detection", False, 0, f"Error: {str(e)}")
            results['language_detection'] = False
            
        # Test content compliance
        try:
            compliance_request = {
                "country_code": "KE",
                "language_code": "en",
                "content_types": ["radio_streams", "music", "news"]
            }
            start_time = time.time()
            async with self.session.post(f"{API_BASE_URL}/compliance/disclaimers", json=compliance_request) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_disclaimers = 'content_disclaimers' in data and len(data['content_disclaimers']) > 0
                    
                    self.log_test_result(
                        "Content Compliance", 
                        has_disclaimers, 
                        response_time,
                        f"Disclaimers: {len(data.get('content_disclaimers', []))}"
                    )
                    results['content_compliance'] = has_disclaimers
                else:
                    self.log_test_result("Content Compliance", False, response_time, f"HTTP {response.status}")
                    results['content_compliance'] = False
        except Exception as e:
            self.log_test_result("Content Compliance", False, 0, f"Error: {str(e)}")
            results['content_compliance'] = False
            
        # Test satellite status
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE_URL}/satellite/status") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    has_status = 'connection_type' in data and 'signal_strength' in data
                    
                    self.log_test_result(
                        "Satellite Status", 
                        has_status, 
                        response_time,
                        f"Connection: {data.get('connection_type', 'none')}, Signal: {data.get('signal_strength', 'none')}"
                    )
                    results['satellite_status'] = has_status
                else:
                    self.log_test_result("Satellite Status", False, response_time, f"HTTP {response.status}")
                    results['satellite_status'] = False
        except Exception as e:
            self.log_test_result("Satellite Status", False, 0, f"Error: {str(e)}")
            results['satellite_status'] = False
            
        return results
        
    async def run_comprehensive_test(self):
        """Run all comprehensive backend tests"""
        print("🎵 STARTING COMPREHENSIVE KAGEMA FM BACKEND API VERIFICATION")
        print(f"Testing against: {API_BASE_URL}")
        print("=" * 80)
        
        # Phase 1: Critical Radio Streaming APIs
        print("\n📡 PHASE 1: CRITICAL RADIO STREAMING APIs")
        connectivity_ok = await self.test_api_connectivity()
        station_info_ok = await self.test_station_info_basic()
        multilingual_results = await self.test_multilingual_station_info()
        personalized_content_ok = await self.test_personalized_content_multilingual()
        
        # Phase 2: Stream Accessibility
        print("\n🎶 PHASE 2: STREAM ACCESSIBILITY VERIFICATION")
        stream_results = await self.test_stream_accessibility()
        
        # Phase 3: Enhanced Features
        print("\n⚡ PHASE 3: ENHANCED FEATURES")
        enhanced_results = await self.test_enhanced_features()
        
        # Calculate overall results
        total_time = time.time() - self.start_time
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance metrics
        response_times = [result['response_time_ms'] for result in self.test_results if result['response_time_ms'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE BACKEND TESTING COMPLETE")
        print("=" * 80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Total Time: {total_time:.1f}s")
        print(f"   • Avg Response Time: {avg_response_time:.0f}ms")
        print(f"   • Max Response Time: {max_response_time:.0f}ms")
        
        # Critical endpoints summary
        critical_endpoints = {
            'API Root': connectivity_ok,
            'Station Info': station_info_ok,
            'Multilingual Station (Kenya)': multilingual_results.get('Kenya', False),
            'Multilingual Station (Brazil)': multilingual_results.get('Brazil', False),
            'Multilingual Station (Global)': multilingual_results.get('Global', False),
            'Personalized Content': personalized_content_ok
        }
        
        critical_success = sum(critical_endpoints.values())
        critical_total = len(critical_endpoints)
        critical_rate = (critical_success / critical_total * 100) if critical_total > 0 else 0
        
        print(f"\n🎯 CRITICAL RADIO STREAMING APIs: {critical_success}/{critical_total} ({critical_rate:.1f}%)")
        for endpoint, status in critical_endpoints.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {endpoint}")
            
        # Stream accessibility summary
        if stream_results:
            working_streams = sum(stream_results.values())
            total_streams = len(stream_results)
            stream_rate = (working_streams / total_streams * 100) if total_streams > 0 else 0
            
            print(f"\n📡 STREAM ACCESSIBILITY: {working_streams}/{total_streams} ({stream_rate:.1f}%)")
            for stream_name, status in stream_results.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {stream_name}")
        
        # Enhanced features summary
        if enhanced_results:
            enhanced_success = sum(enhanced_results.values())
            enhanced_total = len(enhanced_results)
            enhanced_rate = (enhanced_success / enhanced_total * 100) if enhanced_total > 0 else 0
            
            print(f"\n⚡ ENHANCED FEATURES: {enhanced_success}/{enhanced_total} ({enhanced_rate:.1f}%)")
            for feature, status in enhanced_results.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {feature.replace('_', ' ').title()}")
        
        # Performance assessment
        print(f"\n⚡ PERFORMANCE ASSESSMENT:")
        if avg_response_time < 2000:
            print(f"   ✅ Response Time: EXCELLENT ({avg_response_time:.0f}ms avg)")
        elif avg_response_time < 5000:
            print(f"   ⚠️  Response Time: ACCEPTABLE ({avg_response_time:.0f}ms avg)")
        else:
            print(f"   ❌ Response Time: SLOW ({avg_response_time:.0f}ms avg)")
            
        # Final assessment
        if success_rate >= 95 and critical_rate >= 90:
            print(f"\n🎉 DEPLOYMENT STATUS: ✅ PRODUCTION READY")
            print(f"   Backend API endpoints are fully operational and meet all requirements")
        elif success_rate >= 85 and critical_rate >= 80:
            print(f"\n⚠️  DEPLOYMENT STATUS: 🔶 MOSTLY READY")
            print(f"   Minor issues detected but core functionality working")
        else:
            print(f"\n❌ DEPLOYMENT STATUS: 🔴 NEEDS ATTENTION")
            print(f"   Critical issues found that require resolution")
            
        return {
            'success_rate': success_rate,
            'critical_rate': critical_rate,
            'stream_accessibility': stream_results,
            'enhanced_features': enhanced_results,
            'performance': {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time
            },
            'test_results': self.test_results
        }

async def main():
    """Main test execution function"""
    async with KagemaFMBackendTester() as tester:
        results = await tester.run_comprehensive_test()
        return results

if __name__ == "__main__":
    asyncio.run(main())