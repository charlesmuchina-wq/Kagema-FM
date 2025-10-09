#!/usr/bin/env python3
"""
Test streams returned by the API endpoints
"""

import requests
import json

def test_api_streams():
    """Test streams returned by API endpoints"""
    
    print("🎵 TESTING STREAMS RETURNED BY API ENDPOINTS")
    print("=" * 60)
    
    # Test basic station info
    print("\n📡 Testing Basic Station Info API...")
    try:
        response = requests.get("https://autoradio-debug.preview.emergentagent.com/api/station-info")
        if response.status_code == 200:
            data = response.json()
            stream_url = data.get("streamUrl")
            print(f"✅ Basic Station Info API: {response.status_code}")
            print(f"   Stream URL: {stream_url}")
            
            # Test the stream
            if stream_url:
                stream_response = requests.head(stream_url, timeout=10)
                print(f"   Stream Status: {stream_response.status_code}")
                print(f"   Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
        else:
            print(f"❌ Basic Station Info API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic Station Info API error: {e}")
    
    # Test personalized content for Kenya
    print("\n📡 Testing Personalized Content API (Kenya)...")
    try:
        payload = {
            "location": {"latitude": -1.286389, "longitude": 36.817223},
            "preferences": {
                "interests": ["music", "news"],
                "favorite_genres": ["pop", "jazz"],
                "offline_mode": False
            }
        }
        
        response = requests.post(
            "https://autoradio-debug.preview.emergentagent.com/api/personalized-content/multilingual",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            radio_streams = data.get("radio_streams", {})
            print(f"✅ Personalized Content API (Kenya): {response.status_code}")
            
            # Test main station stream
            main_station = radio_streams.get("main_station", {})
            if main_station.get("streamUrl"):
                stream_url = main_station["streamUrl"]
                print(f"   Main Station: {main_station.get('name')} - {stream_url}")
                
                stream_response = requests.head(stream_url, timeout=10)
                print(f"   Main Stream Status: {stream_response.status_code}")
                print(f"   Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
            
            # Test regional stations
            regional_stations = radio_streams.get("regional_stations", [])
            print(f"   Regional Stations Count: {len(regional_stations)}")
            for i, station_url in enumerate(regional_stations[:2]):  # Test first 2
                print(f"   Testing Regional Station {i+1}: {station_url}")
                try:
                    stream_response = requests.head(station_url, timeout=10)
                    print(f"     Status: {stream_response.status_code}")
                    print(f"     Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
                except Exception as e:
                    print(f"     Error: {e}")
            
            # Test alternative streams
            alternative_streams = radio_streams.get("alternative_streams", [])
            print(f"   Alternative Streams Count: {len(alternative_streams)}")
            for i, stream in enumerate(alternative_streams[:2]):  # Test first 2
                stream_url = stream.get("streamUrl")
                stream_name = stream.get("name")
                print(f"   Testing Alternative Stream {i+1}: {stream_name} - {stream_url}")
                try:
                    stream_response = requests.head(stream_url, timeout=10)
                    print(f"     Status: {stream_response.status_code}")
                    print(f"     Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
                except Exception as e:
                    print(f"     Error: {e}")
                    
        else:
            print(f"❌ Personalized Content API (Kenya) failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Personalized Content API (Kenya) error: {e}")
    
    # Test personalized content for Brazil
    print("\n📡 Testing Personalized Content API (Brazil)...")
    try:
        payload = {
            "location": {"latitude": -12.971398, "longitude": -38.501234},
            "preferences": {
                "interests": ["music", "news"],
                "favorite_genres": ["pop", "jazz"],
                "offline_mode": False
            }
        }
        
        response = requests.post(
            "https://autoradio-debug.preview.emergentagent.com/api/personalized-content/multilingual",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            radio_streams = data.get("radio_streams", {})
            print(f"✅ Personalized Content API (Brazil): {response.status_code}")
            
            # Test main station stream
            main_station = radio_streams.get("main_station", {})
            if main_station.get("streamUrl"):
                stream_url = main_station["streamUrl"]
                print(f"   Main Station: {main_station.get('name')} - {stream_url}")
                
                stream_response = requests.head(stream_url, timeout=10)
                print(f"   Main Stream Status: {stream_response.status_code}")
                print(f"   Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
            
            # Test regional stations
            regional_stations = radio_streams.get("regional_stations", [])
            print(f"   Regional Stations Count: {len(regional_stations)}")
            for i, station_url in enumerate(regional_stations[:2]):  # Test first 2
                print(f"   Testing Regional Station {i+1}: {station_url}")
                try:
                    stream_response = requests.head(station_url, timeout=10)
                    print(f"     Status: {stream_response.status_code}")
                    print(f"     Content-Type: {stream_response.headers.get('content-type', 'N/A')}")
                except Exception as e:
                    print(f"     Error: {e}")
                    
        else:
            print(f"❌ Personalized Content API (Brazil) failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Personalized Content API (Brazil) error: {e}")

if __name__ == "__main__":
    test_api_streams()