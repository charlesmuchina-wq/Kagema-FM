#!/usr/bin/env python3
"""
Detailed Stream Debugging Test - Audio Stream Verification
"""

import requests
import time

def test_stream_detailed(url, name):
    """Test stream with detailed error reporting"""
    print(f"\n🔍 DETAILED TESTING: {name}")
    print(f"   URL: {url}")
    
    try:
        # Test HEAD request
        print("   Testing HEAD request...")
        head_response = requests.head(url, timeout=15, allow_redirects=True)
        print(f"   HEAD Status: {head_response.status_code}")
        print(f"   HEAD Headers: {dict(head_response.headers)}")
        
        # Test GET request with limited data
        print("   Testing GET request...")
        get_response = requests.get(url, timeout=15, stream=True)
        print(f"   GET Status: {get_response.status_code}")
        print(f"   GET Headers: {dict(get_response.headers)}")
        
        # Read a small amount of data to verify it's actually streaming
        if get_response.status_code == 200:
            try:
                chunk = next(get_response.iter_content(chunk_size=1024))
                print(f"   Data received: {len(chunk)} bytes")
                print(f"   First 50 bytes: {chunk[:50]}")
            except Exception as e:
                print(f"   Error reading stream data: {e}")
        
        get_response.close()
        
        return {
            "accessible": head_response.status_code == 200 or get_response.status_code == 200,
            "head_status": head_response.status_code,
            "get_status": get_response.status_code,
            "content_type": get_response.headers.get('content-type', ''),
            "headers": dict(get_response.headers)
        }
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return {"accessible": False, "error": str(e)}

def main():
    """Test specific streams with detailed debugging"""
    
    # Test streams from review request
    test_streams = [
        {
            "name": "Brazil Bahia (102.3 FM)",
            "url": "http://ice2.somafm.com/bagel-256-mp3"
        },
        {
            "name": "Kenya Nairobi (101.5 FM)", 
            "url": "http://ice1.somafm.com/groovesalad-256-mp3"
        },
        {
            "name": "Satellite Stream",
            "url": "http://ice1.somafm.com/spacestation-256-mp3"
        },
        {
            "name": "International Stream",
            "url": "http://ice3.somafm.com/beatblender-256-mp3"
        },
        {
            "name": "Secret Agent Stream",
            "url": "http://ice1.somafm.com/secretagent-256-mp3"
        },
        {
            "name": "DEF CON Stream",
            "url": "http://ice1.somafm.com/defcon-256-mp3"
        },
        {
            "name": "Lush Stream",
            "url": "http://ice1.somafm.com/lush-256-mp3"
        }
    ]
    
    print("🎵 DETAILED AUDIO STREAM DEBUGGING")
    print("=" * 60)
    
    results = {}
    for stream in test_streams:
        result = test_stream_detailed(stream["url"], stream["name"])
        results[stream["name"]] = result
        time.sleep(2)  # Rate limiting
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF STREAM ACCESSIBILITY")
    print("=" * 60)
    
    accessible_count = 0
    for name, result in results.items():
        if result.get("accessible", False):
            accessible_count += 1
            print(f"✅ {name}: ACCESSIBLE")
        else:
            print(f"❌ {name}: NOT ACCESSIBLE - {result.get('error', 'Unknown error')}")
    
    print(f"\nAccessibility Rate: {accessible_count}/{len(test_streams)} ({accessible_count/len(test_streams)*100:.1f}%)")

if __name__ == "__main__":
    main()