#!/usr/bin/env python3
"""
Simple test for user features to debug issues
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://radio-resilient.preview.emergentagent.com/api"
TEST_USER_ID = "test-user-123"

def test_user_preferences():
    print("Testing user preferences...")
    
    # Test GET preferences
    try:
        response = requests.get(f"{BACKEND_URL}/user/{TEST_USER_ID}/preferences", timeout=10)
        print(f"GET preferences: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"GET preferences error: {e}")
    
    # Test PUT preferences with correct model structure
    preferences_data = {
        "user_id": TEST_USER_ID,
        "theme": "dark",
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
    
    try:
        response = requests.put(f"{BACKEND_URL}/user/{TEST_USER_ID}/preferences", 
                               json=preferences_data, timeout=10)
        print(f"PUT preferences: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"PUT preferences error: {e}")

def test_favorites():
    print("\nTesting favorites...")
    
    # Test adding a favorite with correct model structure
    favorite_data = {
        "user_id": TEST_USER_ID,
        "type": "radio_station",
        "title": "Kagema FM Nairobi",
        "description": "Premier radio station in Nairobi",
        "url": "https://kagema-fm.com",
        "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
        "metadata": {
            "frequency": "101.5 FM",
            "location": "Nairobi, Kenya"
        },
        "tags": ["kenyan", "music", "news"],
        "is_private": False
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/user/{TEST_USER_ID}/favorites", 
                                json=favorite_data, timeout=10)
        print(f"POST favorite: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"POST favorite error: {e}")

def test_listening_session():
    print("\nTesting listening session...")
    
    # Test starting a listening session with correct model structure
    session_data = {
        "user_id": TEST_USER_ID,
        "station_name": "Kagema FM Nairobi",
        "stream_url": "https://ice1.somafm.com/groovesalad-256-mp3",
        "started_at": datetime.now().isoformat(),
        "quality": "high",
        "device_info": {
            "type": "web",
            "browser": "Chrome",
            "os": "Linux"
        }
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/user/{TEST_USER_ID}/listening-session", 
                                json=session_data, timeout=10)
        print(f"POST listening session: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"POST listening session error: {e}")

if __name__ == "__main__":
    test_user_preferences()
    test_favorites()
    test_listening_session()