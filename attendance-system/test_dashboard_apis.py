#!/usr/bin/env python3
"""
Test the specific API endpoints used by the student dashboard
"""

import requests
import json

def test_endpoints():
    """Test the dashboard API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Dashboard API Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if /students/profile endpoint exists (without auth)
    print("1. Testing /students/profile endpoint (without auth):")
    try:
        response = requests.get(f"{base_url}/students/profile", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   [EXPECTED] Requires authentication")
        elif response.status_code == 422:
            print("   [EXPECTED] Validation error (missing auth)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 2: Check if /courses/student endpoint exists (without auth)
    print("\\n2. Testing /courses/student endpoint (without auth):")
    try:
        response = requests.get(f"{base_url}/courses/student", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   [EXPECTED] Requires authentication")
        elif response.status_code == 422:
            print("   [EXPECTED] Validation error (missing auth)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 3: Check general courses endpoint
    print("\\n3. Testing /courses/ endpoint (public):")
    try:
        response = requests.get(f"{base_url}/courses/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()
            print(f"   [OK] Found {len(courses)} courses")
            if courses:
                print(f"   Sample course: {courses[0]}")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 4: Try to create a test login
    print("\\n4. Testing login endpoint:")
    try:
        login_data = {
            "email": "student@test.com",
            "password": "test123"
        }
        response = requests.post(f"{base_url}/auth/login", 
                               json=login_data, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   [OK] Login successful")
            token = result.get('access_token')
            if token:
                print("   Token received, testing authenticated endpoints...")
                test_authenticated_endpoints(base_url, token)
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")

def test_authenticated_endpoints(base_url, token):
    """Test endpoints with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\\n   Testing authenticated endpoints:")
    
    # Test profile endpoint
    try:
        response = requests.get(f"{base_url}/students/profile", 
                              headers=headers, 
                              timeout=5)
        print(f"   Profile endpoint status: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"   [OK] Profile loaded: {profile.get('name', 'Unknown')}")
        else:
            print(f"   Profile error: {response.text[:200]}")
    except Exception as e:
        print(f"   Profile error: {e}")
    
    # Test student courses endpoint
    try:
        response = requests.get(f"{base_url}/courses/student", 
                              headers=headers, 
                              timeout=5)
        print(f"   Student courses status: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()
            print(f"   [OK] Found {len(courses)} enrolled courses")
        else:
            print(f"   Courses error: {response.text[:200]}")
    except Exception as e:
        print(f"   Courses error: {e}")

if __name__ == "__main__":
    test_endpoints()