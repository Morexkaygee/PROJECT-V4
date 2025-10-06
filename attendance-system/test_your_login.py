#!/usr/bin/env python3
"""
Test login with your actual account
"""

import requests
import json

def test_your_login():
    """Test login with your actual credentials"""
    base_url = "http://localhost:8000"
    
    print("Testing Your Account Login...")
    print("=" * 40)
    
    # Your credentials
    matric_no = "IFT/19/0644"
    password = "newpass123"
    
    try:
        login_data = {
            "matric_no": matric_no,
            "password": password
        }
        
        print(f"Logging in with matric: {matric_no}")
        response = requests.post(f"{base_url}/auth/login/student", 
                               json=login_data, 
                               timeout=5)
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] Login successful!")
            print(f"Welcome: {result['user']['name']}")
            
            token = result.get('access_token')
            if token:
                print("\\nTesting dashboard APIs...")
                test_dashboard_with_your_account(base_url, token)
                return True
        else:
            print(f"[FAILED] Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        return False

def test_dashboard_with_your_account(base_url, token):
    """Test dashboard APIs with your account"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Dashboard API Tests:")
    print("-" * 30)
    
    # Test 1: Profile API
    try:
        response = requests.get(f"{base_url}/students/profile", 
                              headers=headers, 
                              timeout=10)
        print(f"Profile API: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"  Name: {profile.get('name')}")
            print(f"  Matric: {profile.get('matric_no')}")
            print(f"  Department: {profile.get('department')}")
            print(f"  Level: {profile.get('level')}")
            print(f"  Face Registered: {profile.get('face_registered')}")
            print(f"  Courses: {profile.get('course_count', 0)}")
        else:
            print(f"  [ERROR] Profile failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"  [ERROR] Profile API: {e}")
    
    # Test 2: Courses API
    try:
        response = requests.get(f"{base_url}/courses/student", 
                              headers=headers, 
                              timeout=10)
        print(f"Courses API: {response.status_code}")
        
        if response.status_code == 200:
            courses = response.json()
            print(f"  Enrolled Courses: {len(courses)}")
            for course in courses:
                print(f"    - {course.get('name')} ({course.get('code')})")
        else:
            print(f"  [ERROR] Courses failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"  [ERROR] Courses API: {e}")

if __name__ == "__main__":
    if test_your_login():
        print("\\n[SUCCESS] Your account is working!")
        print("\\nYou can now login to the dashboard with:")
        print("  Matric No: IFT/19/0644")
        print("  Password: newpass123")
    else:
        print("\\n[FAILED] There are still issues with your account")