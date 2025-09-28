#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Enhanced Kagema FM Radio Station
Tests all enhanced features including geolocation, weather, news, music, and AI services
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys
import os

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class KagemaFMAPITester:
    def __init__(self):
        self.base_url = API_BASE
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []

        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(f"{test_name}: {details}")
        print(result)
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "Kagema FM" in data.get("message", "") and data.get("version") == "2.0.0":
                    self.log_test("API Root Endpoint", True, "Enhanced API version 2.0.0 detected")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

def test_station_info():
    """Test GET /api/station-info - Get Kagema FM station details"""
    try:
        response = requests.get(f"{API_BASE}/station-info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required fields
            required_fields = ["name", "description", "streamUrl"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test("Station info endpoint", False, f"Missing required fields: {missing_fields}")
                return False
            
            # Verify Kagema FM specific data
            if data["name"] == "Kagema FM":
                log_test("Station info endpoint", True, f"Returns Kagema FM data with stream URL: {data['streamUrl']}")
                return True
            else:
                log_test("Station info endpoint", False, f"Expected 'Kagema FM', got: {data['name']}")
                return False
                
        else:
            log_test("Station info endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Station info endpoint", False, f"Request failed: {str(e)}")
        return False

def test_create_station():
    """Test POST /api/station - Create/update radio station"""
    try:
        # Test data for Kagema FM
        station_data = {
            "name": "Kagema FM Test Station",
            "description": "Test radio station for Kagema FM network",
            "streamUrl": "https://test-stream.kagema.fm/live",
            "currentShow": "Morning Drive with Sarah",
            "genre": "Talk & Music",
            "location": "Nairobi, Kenya",
            "frequency": "FM 103.5"
        }
        
        response = requests.post(
            f"{API_BASE}/station",
            json=station_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response contains expected fields
            if data.get("name") == station_data["name"] and "id" in data:
                log_test("Create station endpoint", True, f"Created station with ID: {data['id']}")
                return data["id"]  # Return station ID for further tests
            else:
                log_test("Create station endpoint", False, f"Unexpected response: {data}")
                return None
        else:
            log_test("Create station endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("Create station endpoint", False, f"Request failed: {str(e)}")
        return None

def test_get_all_stations():
    """Test GET /api/stations - Get all active stations"""
    try:
        response = requests.get(f"{API_BASE}/stations", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test("Get all stations endpoint", True, f"Returns list of {len(data)} stations")
                return True
            else:
                log_test("Get all stations endpoint", False, f"Expected list, got: {type(data)}")
                return False
        else:
            log_test("Get all stations endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Get all stations endpoint", False, f"Request failed: {str(e)}")
        return False

def test_update_current_show(station_id):
    """Test PUT /api/station/{station_id}/current-show - Update current show"""
    if not station_id:
        log_test("Update current show endpoint", False, "No station ID available for testing")
        return False
        
    try:
        show_data = {
            "currentShow": "Evening Jazz Hour with Michael"
        }
        
        response = requests.put(
            f"{API_BASE}/station/{station_id}/current-show",
            json=show_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Current show updated successfully":
                log_test("Update current show endpoint", True, "Successfully updated current show")
                return True
            else:
                log_test("Update current show endpoint", False, f"Unexpected response: {data}")
                return False
        else:
            log_test("Update current show endpoint", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Update current show endpoint", False, f"Request failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    try:
        # Test invalid station creation
        invalid_data = {"name": ""}  # Missing required fields
        response = requests.post(
            f"{API_BASE}/station",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code >= 400:
            log_test("Error handling - Invalid station data", True, f"Properly returns HTTP {response.status_code}")
        else:
            log_test("Error handling - Invalid station data", False, f"Should return error, got HTTP {response.status_code}")
            
        # Test updating non-existent station
        response = requests.put(
            f"{API_BASE}/station/non-existent-id/current-show",
            json={"currentShow": "Test Show"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 404:
            log_test("Error handling - Non-existent station", True, "Properly returns 404 for non-existent station")
        else:
            log_test("Error handling - Non-existent station", False, f"Expected 404, got HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Error handling tests", False, f"Request failed: {str(e)}")

def main():
    """Run all backend API tests for Kagema FM"""
    print("🎵 Starting Kagema FM Backend API Tests")
    print("=" * 50)
    
    # Test all endpoints
    test_root_endpoint()
    test_station_info()
    station_id = test_create_station()
    test_get_all_stations()
    test_update_current_show(station_id)
    test_error_handling()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    
    if test_results["errors"]:
        print("\n🚨 FAILED TESTS:")
        for error in test_results["errors"]:
            print(f"   • {error}")
    
    # Return exit code
    return 0 if test_results["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)