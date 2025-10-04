#!/usr/bin/env python3
"""
Comprehensive Audio Stream Verification for Kagema FM - Phase 1 Testing
Focused on the specific requirements from the review request
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import sys

# Backend URL from frontend environment
BACKEND_URL = "https://carplay-hub-1.preview.emergentagent.com/api"

class AudioStreamVerifier:
    def __init__(self):
        self.results = {
            "backend_api_tests": [],
            "stream_accessibility_tests": [],
            "metadata_verification_tests": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
    def log_test(self, category: str, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        test_result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if category == "backend_api":
            self.results["backend_api_tests"].append(test_result)
        elif category == "stream_accessibility":
            self.results["stream_accessibility_tests"].append(test_result)
        elif category == "metadata_verification":
            self.results["metadata_verification_tests"].append(test_result)
            
        self.results["summary"]["total_tests"] += 1
        if status == "PASS":
            self.results["summary"]["passed_tests"] += 1
        else:
            self.results["summary"]["failed_tests"] += 1
            
    def test_stream_accessibility_detailed(self, stream_url: str, stream_name: str) -> Dict[str, Any]:
        """Test stream URL accessibility with detailed headers and metadata analysis"""
        try:
            print(f"🔍 Testing stream: {stream_name}")
            print(f"   URL: {stream_url}")
            
            # Test with HEAD request first for efficiency
            response = requests.head(stream_url, timeout=10, allow_redirects=True)
            
            result = {
                "url": stream_url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "accessible": response.status_code == 200,
                "content_type": response.headers.get('content-type', 'unknown'),
                "icy_headers": {},
                "audio_format": "unknown",
                "bitrate": "unknown",
                "server": response.headers.get('server', 'unknown')
            }
            
            # Check for ICY streaming headers
            for header, value in response.headers.items():
                if header.lower().startswith('icy-'):
                    result["icy_headers"][header] = value
                    
            # Determine audio format from content-type
            content_type = response.headers.get('content-type', '').lower()
            if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                result["audio_format"] = "MP3"
            elif 'audio/aac' in content_type:
                result["audio_format"] = "AAC"
            elif 'audio/ogg' in content_type:
                result["audio_format"] = "OGG"
            elif 'application/ogg' in content_type:
                result["audio_format"] = "OGG"
                
            # Extract bitrate from ICY headers or URL
            if 'icy-br' in result["icy_headers"]:
                result["bitrate"] = f"{result['icy_headers']['icy-br']} kbps"
            elif '256' in stream_url:
                result["bitrate"] = "256 kbps"
            elif '320' in stream_url:
                result["bitrate"] = "320 kbps"
            elif '192' in stream_url:
                result["bitrate"] = "192 kbps"
            elif '128' in stream_url:
                result["bitrate"] = "128 kbps"
                
            # If HEAD request successful, try GET for more metadata
            if response.status_code == 200:
                try:
                    get_response = requests.get(stream_url, timeout=5, stream=True)
                    # Read just a small chunk to get streaming headers
                    chunk_count = 0
                    for chunk in get_response.iter_content(chunk_size=1024):
                        chunk_count += 1
                        if chunk_count >= 3:  # Read first 3KB
                            break
                    get_response.close()
                    
                    # Update with GET response headers if different
                    for header, value in get_response.headers.items():
                        if header.lower().startswith('icy-'):
                            result["icy_headers"][header] = value
                            
                    result["stream_test"] = "successful"
                    
                except Exception as e:
                    result["get_request_error"] = str(e)
                    result["stream_test"] = "partial"
            else:
                result["stream_test"] = "failed"
                
            # Print detailed results
            if result["accessible"]:
                print(f"   ✅ Status: {result['status_code']} OK")
                print(f"   🎵 Format: {result['audio_format']}")
                print(f"   📊 Bitrate: {result['bitrate']}")
                print(f"   📡 ICY Headers: {len(result['icy_headers'])}")
                if result["icy_headers"]:
                    for icy_header, value in result["icy_headers"].items():
                        print(f"      {icy_header}: {value}")
            else:
                print(f"   ❌ Status: {result['status_code']} - Not accessible")
                
            return result
            
        except requests.exceptions.RequestException as e:
            error_result = {
                "url": stream_url,
                "status_code": 0,
                "accessible": False,
                "error": str(e),
                "content_type": "unknown",
                "icy_headers": {},
                "audio_format": "unknown",
                "bitrate": "unknown",
                "stream_test": "error"
            }
            print(f"   ❌ Error: {str(e)}")
            return error_result
            
    def test_backend_api_station_info(self) -> Dict[str, Any]:
        """Test /api/station-info endpoint for radio streams data"""
        try:
            print("🔍 Testing GET /api/station-info...")
            response = requests.get(f"{BACKEND_URL}/station-info", timeout=10)
            
            result = {
                "endpoint": "/api/station-info",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                result["data"] = data
                result["has_stream_url"] = "streamUrl" in data
                result["stream_url"] = data.get("streamUrl", "")
                result["station_name"] = data.get("name", "")
                
                # Validate required fields
                required_fields = ["name", "description", "streamUrl"]
                missing_fields = [field for field in required_fields if field not in data]
                result["missing_fields"] = missing_fields
                result["valid_response"] = len(missing_fields) == 0
                
                print(f"   ✅ Station: {result['station_name']}")
                print(f"   🎵 Stream URL: {result['stream_url']}")
            else:
                result["error"] = response.text
                result["valid_response"] = False
                print(f"   ❌ Failed: {response.status_code}")
                
            return result
            
        except Exception as e:
            error_result = {
                "endpoint": "/api/station-info",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "valid_response": False
            }
            print(f"   ❌ Error: {str(e)}")
            return error_result
            
    def test_backend_api_personalized_content(self) -> Dict[str, Any]:
        """Test /api/personalized-content/multilingual endpoint for radio_streams data"""
        try:
            print("🔍 Testing POST /api/personalized-content/multilingual...")
            
            # Test with Kenya coordinates (Nairobi) - correct format
            payload = {
                "location": {
                    "latitude": -1.286389,
                    "longitude": 36.817223
                },
                "preferences": {
                    "user_id": "test-audio-verification",
                    "theme": "light",
                    "language": "en",
                    "region": "KE",
                    "notifications": {
                        "enabled": True,
                        "show_reminders": True,
                        "news_updates": True,
                        "music_discovery": True,
                        "app_updates": True,
                        "quiet_hours_enabled": False,
                        "quiet_start_time": "22:00",
                        "quiet_end_time": "08:00",
                        "sound_enabled": True,
                        "vibration_enabled": True
                    },
                    "audio": {
                        "quality": "high",
                        "volume": 0.8,
                        "auto_play": False,
                        "background_play": True,
                        "equalizer_preset": "default"
                    },
                    "offline_mode": False,
                    "data_saver": False,
                    "analytics_enabled": True
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/personalized-content/multilingual",
                json=payload,
                timeout=15
            )
            
            result = {
                "endpoint": "/api/personalized-content/multilingual",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                result["data"] = data
                
                # Check for radio_streams data (CRITICAL for frontend)
                result["has_radio_streams"] = "radio_streams" in data
                if "radio_streams" in data:
                    radio_streams = data["radio_streams"]
                    result["radio_streams_structure"] = {
                        "has_main_station": "main_station" in radio_streams,
                        "has_alternative_streams": "alternative_streams" in radio_streams,
                        "alternative_streams_count": len(radio_streams.get("alternative_streams", [])),
                        "main_station_url": radio_streams.get("main_station", {}).get("streamUrl", "")
                    }
                    
                    # Extract all stream URLs for testing
                    stream_urls = []
                    if "main_station" in radio_streams:
                        main_url = radio_streams["main_station"].get("streamUrl")
                        if main_url:
                            stream_urls.append(("Main Station", main_url))
                            
                    if "alternative_streams" in radio_streams:
                        for i, stream in enumerate(radio_streams["alternative_streams"]):
                            stream_url = stream.get("streamUrl")
                            stream_name = stream.get("name", f"Alternative Stream {i+1}")
                            if stream_url:
                                stream_urls.append((stream_name, stream_url))
                                
                    result["extracted_stream_urls"] = stream_urls
                    
                    print(f"   ✅ Radio streams data found")
                    print(f"   🎵 Main station: {result['radio_streams_structure']['has_main_station']}")
                    print(f"   📻 Alternative streams: {result['radio_streams_structure']['alternative_streams_count']}")
                else:
                    result["radio_streams_structure"] = {}
                    result["extracted_stream_urls"] = []
                    print(f"   ❌ No radio_streams data found")
                    
                # Check other required fields
                result["has_language_detection"] = "language_detection" in data
                result["has_content_disclaimers"] = "content_disclaimers" in data
                result["has_compliance_info"] = "compliance_info" in data
                
            else:
                result["error"] = response.text
                print(f"   ❌ Failed: {response.status_code}")
                
            return result
            
        except Exception as e:
            error_result = {
                "endpoint": "/api/personalized-content/multilingual",
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ Error: {str(e)}")
            return error_result
            
    def run_comprehensive_audio_stream_verification(self):
        """Run comprehensive audio stream verification tests per review request"""
        print("🎵 COMPREHENSIVE AUDIO STREAM VERIFICATION FOR KAGEMA FM - PHASE 1")
        print("=" * 80)
        print("Focus: Audio streaming functionality, stream accessibility, metadata verification")
        print("=" * 80)
        
        # Test 1: Backend API - Station Info
        print("\n1️⃣ BACKEND API INTEGRATION - Station Info")
        print("-" * 50)
        station_info_result = self.test_backend_api_station_info()
        
        if station_info_result["success"] and station_info_result.get("valid_response"):
            self.log_test("backend_api", "GET /api/station-info", "PASS", station_info_result)
        else:
            self.log_test("backend_api", "GET /api/station-info", "FAIL", station_info_result)
            
        # Test 2: Backend API - Personalized Content with Radio Streams
        print("\n2️⃣ BACKEND API INTEGRATION - Personalized Content")
        print("-" * 50)
        personalized_result = self.test_backend_api_personalized_content()
        
        if personalized_result["success"] and personalized_result.get("has_radio_streams"):
            self.log_test("backend_api", "POST /api/personalized-content/multilingual", "PASS", personalized_result)
        else:
            self.log_test("backend_api", "POST /api/personalized-content/multilingual", "FAIL", personalized_result)
                
        # Test 3: Main Kenya Stream Accessibility (Groove Salad)
        print("\n3️⃣ MAIN KENYA STREAM VERIFICATION")
        print("-" * 50)
        main_stream_url = "https://ice1.somafm.com/groovesalad-256-mp3"
        main_stream_result = self.test_stream_accessibility_detailed(main_stream_url, "Main Kagema FM Stream (Groove Salad)")
        
        if main_stream_result["accessible"] and main_stream_result["audio_format"] in ["MP3", "AAC"]:
            self.log_test("stream_accessibility", "Main Kenya Stream", "PASS", main_stream_result)
        else:
            self.log_test("stream_accessibility", "Main Kenya Stream", "FAIL", main_stream_result)
            
        # Test 4: Alternative Streams from Backend API
        print("\n4️⃣ ALTERNATIVE STREAMS VERIFICATION")
        print("-" * 50)
        
        # Get alternative streams from personalized content API
        alternative_streams = []
        if personalized_result["success"] and "extracted_stream_urls" in personalized_result:
            alternative_streams = personalized_result["extracted_stream_urls"]
            print(f"Found {len(alternative_streams)} streams from backend API")
        else:
            # Fallback to known alternative streams from backend code
            alternative_streams = [
                ("Radio Paradise AAC", "https://stream.radioparadise.com/aac-320"),
                ("Radio Paradise MP3", "https://stream.radioparadise.com/mp3-192"),
                ("FIP Radio France AAC", "https://icecast.radiofrance.fr/fip-hifi.aac"),
                ("FIP Radio France MP3", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
                ("SomaFM Drone Zone", "http://ice1.somafm.com/dronezone-256-mp3"),
                ("SomaFM DEF CON Radio", "http://ice1.somafm.com/defcon-256-mp3")
            ]
            print(f"Using fallback streams: {len(alternative_streams)} streams")
            
        working_streams = 0
        total_alternative_streams = len(alternative_streams)
        
        for stream_name, stream_url in alternative_streams:
            if stream_url == main_stream_url:  # Skip main stream as already tested
                continue
                
            stream_result = self.test_stream_accessibility_detailed(stream_url, stream_name)
            
            if stream_result["accessible"] and stream_result["audio_format"] in ["MP3", "AAC", "OGG"]:
                self.log_test("stream_accessibility", f"Alternative Stream: {stream_name}", "PASS", stream_result)
                working_streams += 1
            else:
                self.log_test("stream_accessibility", f"Alternative Stream: {stream_name}", "FAIL", stream_result)
                
        # Test 5: Stream Metadata and ICY Headers Analysis
        print("\n5️⃣ STREAM METADATA & ICY HEADERS VERIFICATION")
        print("-" * 50)
        
        # Analyze ICY headers from working streams
        icy_header_analysis = {}
        audio_format_distribution = {}
        bitrate_analysis = {}
        
        for test_result in self.results["stream_accessibility_tests"]:
            if test_result["status"] == "PASS":
                details = test_result["details"]
                
                # Count ICY headers
                icy_count = len(details.get("icy_headers", {}))
                if icy_count > 0:
                    icy_header_analysis[test_result["test_name"]] = {
                        "count": icy_count,
                        "headers": details.get("icy_headers", {})
                    }
                    
                # Count audio formats
                audio_format = details.get("audio_format", "unknown")
                audio_format_distribution[audio_format] = audio_format_distribution.get(audio_format, 0) + 1
                
                # Count bitrates
                bitrate = details.get("bitrate", "unknown")
                bitrate_analysis[bitrate] = bitrate_analysis.get(bitrate, 0) + 1
                
        metadata_result = {
            "icy_headers_found": len(icy_header_analysis) > 0,
            "streams_with_icy_headers": len(icy_header_analysis),
            "audio_format_distribution": audio_format_distribution,
            "bitrate_analysis": bitrate_analysis,
            "metadata_quality": "good" if len(icy_header_analysis) > 0 else "poor",
            "icy_header_details": icy_header_analysis
        }
        
        if metadata_result["icy_headers_found"]:
            self.log_test("metadata_verification", "ICY Headers Verification", "PASS", metadata_result)
            print(f"✅ ICY Headers: Found on {len(icy_header_analysis)} streams")
            for stream_name, header_info in icy_header_analysis.items():
                print(f"   📡 {stream_name}: {header_info['count']} ICY headers")
                for header, value in header_info['headers'].items():
                    print(f"      {header}: {value}")
        else:
            self.log_test("metadata_verification", "ICY Headers Verification", "FAIL", metadata_result)
            print(f"❌ ICY Headers: No streaming metadata found")
            
        print(f"\n📊 Audio Format Distribution: {audio_format_distribution}")
        print(f"🎵 Bitrate Analysis: {bitrate_analysis}")
        
        # Test 6: Stream Reliability Assessment
        print("\n6️⃣ STREAM RELIABILITY ASSESSMENT")
        print("-" * 50)
        
        if total_alternative_streams > 0:
            stream_reliability = (working_streams / total_alternative_streams) * 100
            print(f"📡 Stream Reliability: {working_streams}/{total_alternative_streams} ({stream_reliability:.1f}%)")
            
            reliability_result = {
                "working_streams": working_streams,
                "total_streams": total_alternative_streams,
                "reliability_percentage": stream_reliability,
                "meets_target": stream_reliability >= 85.0,
                "target_percentage": 85.0
            }
            
            if stream_reliability >= 85.0:
                self.log_test("stream_accessibility", "Stream Reliability Target (85%+)", "PASS", reliability_result)
                print("✅ Stream Reliability: Meets 85%+ target")
            else:
                self.log_test("stream_accessibility", "Stream Reliability Target (85%+)", "FAIL", reliability_result)
                print("❌ Stream Reliability: Below 85% target")
                print(f"   Need to fix {int((85.0 - stream_reliability) / 100 * total_alternative_streams)} more streams")
                
        # Final Summary
        self.results["summary"]["success_rate"] = (
            self.results["summary"]["passed_tests"] / self.results["summary"]["total_tests"] * 100
            if self.results["summary"]["total_tests"] > 0 else 0
        )
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE AUDIO STREAM VERIFICATION COMPLETE")
        print("=" * 80)
        print(f"📊 Overall Success Rate: {self.results['summary']['passed_tests']}/{self.results['summary']['total_tests']} ({self.results['summary']['success_rate']:.1f}%)")
        print(f"✅ Passed Tests: {self.results['summary']['passed_tests']}")
        print(f"❌ Failed Tests: {self.results['summary']['failed_tests']}")
        
        # Critical Success Criteria Assessment
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA ASSESSMENT:")
        main_stream_working = any(test["status"] == "PASS" for test in self.results["stream_accessibility_tests"] if "Main Kenya Stream" in test["test_name"])
        backend_apis_working = all(test["status"] == "PASS" for test in self.results["backend_api_tests"])
        has_icy_headers = metadata_result["icy_headers_found"]
        
        print(f"   • Main Kenya stream accessible: {'✅' if main_stream_working else '❌'}")
        print(f"   • Backend APIs provide radio_streams: {'✅' if backend_apis_working else '❌'}")
        print(f"   • ICY streaming headers present: {'✅' if has_icy_headers else '❌'}")
        print(f"   • Stream reliability target: {'✅' if stream_reliability >= 85.0 else '❌'}")
        
        return self.results

def main():
    """Main test execution"""
    verifier = AudioStreamVerifier()
    results = verifier.run_comprehensive_audio_stream_verification()
    
    # Save detailed results to file
    with open('/app/audio_stream_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\n📄 Detailed results saved to: /app/audio_stream_verification_results.json")
    
    # Return exit code based on success rate
    success_rate = results["summary"]["success_rate"]
    if success_rate >= 80.0:
        print("🎉 AUDIO STREAM VERIFICATION: OVERALL SUCCESS")
        return 0
    else:
        print("⚠️  AUDIO STREAM VERIFICATION: ISSUES FOUND")
        return 1

if __name__ == "__main__":
    sys.exit(main())