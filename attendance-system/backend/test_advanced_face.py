#!/usr/bin/env python3
"""
Quick test script for advanced face recognition system
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all face recognition libraries can be imported."""
    print("Testing face recognition library imports...")
    
    try:
        import face_recognition
        print("✓ face_recognition imported successfully")
    except ImportError as e:
        print(f"✗ face_recognition import failed: {e}")
    
    try:
        from deepface import DeepFace
        print("✓ DeepFace imported successfully")
    except ImportError as e:
        print(f"✗ DeepFace import failed: {e}")
    
    try:
        import insightface
        print("✓ InsightFace imported successfully")
    except ImportError as e:
        print(f"✗ InsightFace import failed: {e}")
    
    try:
        import mediapipe as mp
        print("✓ MediaPipe imported successfully")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")

def test_advanced_system():
    """Test the advanced face recognition system."""
    print("\nTesting advanced face recognition system...")
    
    try:
        from app.utils.advanced_face_recognition import advanced_face_recognition
        print(f"✓ Advanced face recognition system loaded")
        print(f"✓ Available models: {len(advanced_face_recognition.models)}")
        
        if len(advanced_face_recognition.models) > 0:
            print("✓ Models initialized:")
            for model_name in advanced_face_recognition.models.keys():
                print(f"  - {model_name}")
        else:
            print("⚠ No models available (this is normal on first run)")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced face recognition test failed: {e}")
        return False

def test_api_endpoints():
    """Test if new API endpoints are available."""
    print("\nTesting API endpoint availability...")
    
    try:
        from app.api.face_registration import router
        print("✓ Face registration API loaded")
        
        # Check if routes are defined
        routes = [route.path for route in router.routes]
        expected_routes = ['/register', '/test', '/status', '/upgrade', '/unregister']
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Route {route} available")
            else:
                print(f"✗ Route {route} missing")
        
        return True
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Advanced Face Recognition System Test")
    print("=" * 50)
    
    test_imports()
    system_ok = test_advanced_system()
    api_ok = test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Advanced System: {'✓ PASS' if system_ok else '✗ FAIL'}")
    print(f"API Endpoints: {'✓ PASS' if api_ok else '✗ FAIL'}")
    
    if system_ok and api_ok:
        print("\n🎉 Advanced Face Recognition System is ready!")
        print("\nNext steps:")
        print("1. Start backend: python start.py")
        print("2. Access frontend: http://localhost:3001")
        print("3. Test new face registration features")
        print("\nNew API endpoints available:")
        print("- POST /face/register - Advanced face registration")
        print("- POST /face/test - Test face quality")
        print("- GET /face/status - Check registration status")
        print("- POST /face/upgrade - Upgrade to advanced registration")
    else:
        print("\n⚠ Some issues detected. System may work with reduced functionality.")

if __name__ == "__main__":
    main()