#!/usr/bin/env python3
"""
Test student login and dashboard API calls
"""

import requests
import json

def test_student_login():
    """Test student login with existing user"""
    base_url = "http://localhost:8000"
    
    print("Testing Student Login and Dashboard APIs...")
    print("=" * 60)
    
    # Test with your actual matric number
    matric_numbers_to_try = [
        "IFT/19/0644",  # Your matric number
        "TEST/2024/001",  # Test user
        "CSC/2020/001"   # Sample student
    ]
    
    # Common passwords to try
    passwords_to_try = ["password", "123456", "test123", "admin123"]
    
    for matric_no in matric_numbers_to_try:
        print(f"\\nTrying matric number: {matric_no}")
        
        for password in passwords_to_try:
            print(f"  Trying password: {password}")
            
            try:
                login_data = {
                    "matric_no": matric_no,
                    "password": password
                }
                
                response = requests.post(f"{base_url}/auth/login/student", 
                                       json=login_data, 
                                       timeout=5)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("    [SUCCESS] Login successful!")
                    print(f"    User: {result['user']['name']}")
                    
                    token = result.get('access_token')
                    if token:
                        print("    Testing dashboard APIs...")
                        test_dashboard_apis(base_url, token)
                        return True
                        
                elif response.status_code == 401:
                    print("    [FAILED] Invalid credentials")
                else:
                    print(f"    [ERROR] {response.text[:100]}")
                    
            except Exception as e:
                print(f"    [ERROR] {e}")
    
    print("\\n[FAILED] Could not login with any credentials")
    print("\\nTo fix this, you need to:")
    print("1. Check what password was set for your account")
    print("2. Or reset the password in the database")
    print("3. Or create a new test account with known credentials")
    
    return False

def test_dashboard_apis(base_url, token):
    """Test dashboard APIs with valid token"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\\n    Testing Dashboard APIs:")
    print("    " + "=" * 40)
    
    # Test 1: Student profile
    try:
        response = requests.get(f"{base_url}/students/profile", 
                              headers=headers, 
                              timeout=5)
        print(f"    Profile API - Status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"    [OK] Profile: {profile.get('name')} ({profile.get('matric_no')})")
            print(f"    Face registered: {profile.get('face_registered', False)}")
            print(f"    Courses: {profile.get('course_count', 0)}")
        else:
            print(f"    [ERROR] Profile: {response.text[:100]}")
            
    except Exception as e:
        print(f"    [ERROR] Profile API: {e}")
    
    # Test 2: Student courses
    try:
        response = requests.get(f"{base_url}/courses/student", 
                              headers=headers, 
                              timeout=5)
        print(f"    Courses API - Status: {response.status_code}")
        
        if response.status_code == 200:
            courses = response.json()
            print(f"    [OK] Enrolled courses: {len(courses)}")
            for course in courses[:3]:  # Show first 3 courses
                print(f"      - {course.get('name')} ({course.get('code')})")
        else:
            print(f"    [ERROR] Courses: {response.text[:100]}")
            
    except Exception as e:
        print(f"    [ERROR] Courses API: {e}")

if __name__ == "__main__":
    test_student_login()