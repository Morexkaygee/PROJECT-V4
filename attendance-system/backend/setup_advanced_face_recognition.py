#!/usr/bin/env python3
"""
Setup script for Advanced Face Recognition System
Installs dependencies and initializes the multi-model face recognition system
"""
import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_requirements():
    """Install required packages for advanced face recognition."""
    print("Installing advanced face recognition dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def download_models():
    """Download and initialize face recognition models."""
    print("Downloading and initializing face recognition models...")
    
    try:
        # Test imports and model initialization
        print("Testing face_recognition library...")
        import face_recognition
        print("face_recognition library loaded")
        
        print("Testing DeepFace library...")
        try:
            from deepface import DeepFace
            # This will download models on first use
            print("Initializing DeepFace models...")
            # Create a small test image to trigger model downloads
            import numpy as np
            test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            for model in ['Facenet', 'VGG-Face', 'OpenFace']:
                try:
                    print(f"  - Initializing {model}...")
                    DeepFace.represent(img_path=test_image, model_name=model, enforce_detection=False)
                    print(f"  {model} initialized")
                except Exception as e:
                    print(f"  ⚠ {model} initialization failed: {e}")
            
        except ImportError:
            print("⚠ DeepFace not available")
        except Exception as e:
            print(f"⚠ DeepFace initialization failed: {e}")
        
        print("Testing InsightFace library...")
        try:
            import insightface
            print("  - Downloading InsightFace models...")
            app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=0, det_size=(640, 640))
            print("  InsightFace initialized")
        except ImportError:
            print("⚠ InsightFace not available")
        except Exception as e:
            print(f"⚠ InsightFace initialization failed: {e}")
        
        print("Testing MediaPipe library...")
        try:
            import mediapipe as mp
            mp_face_detection = mp.solutions.face_detection
            face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7)
            print("  MediaPipe initialized")
        except ImportError:
            print("⚠ MediaPipe not available")
        except Exception as e:
            print(f"⚠ MediaPipe initialization failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"Model initialization failed: {e}")
        return False


def test_advanced_face_recognition():
    """Test the advanced face recognition system."""
    print("Testing advanced face recognition system...")
    
    try:
        from app.utils.advanced_face_recognition import advanced_face_recognition
        
        # Create a test image (simple colored rectangle)
        import numpy as np
        import base64
        import io
        from PIL import Image
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
        pil_image = Image.fromarray(test_image)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Test comprehensive analysis
        result = advanced_face_recognition.comprehensive_face_analysis(f"data:image/jpeg;base64,{image_data}")
        
        print(f"  - Models available: {len(advanced_face_recognition.models)}")
        print(f"  - Test analysis completed: {result.get('faces_detected', 0)} faces detected")
        
        if len(advanced_face_recognition.models) > 0:
            print("Advanced face recognition system is working!")
            return True
        else:
            print("⚠ No face recognition models available")
            return False
            
    except Exception as e:
        print(f"Advanced face recognition test failed: {e}")
        return False


def run_database_migration():
    """Run database migration for advanced face recognition."""
    print("Running database migration...")
    
    try:
        from migrate_advanced_face import migrate_database
        success = migrate_database()
        
        if success:
            print("Database migration completed!")
        else:
            print("Database migration failed!")
        
        return success
        
    except Exception as e:
        print(f"Database migration error: {e}")
        return False


def create_model_info_file():
    """Create a file with information about available models."""
    print("Creating model information file...")
    
    try:
        from app.utils.advanced_face_recognition import advanced_face_recognition
        from datetime import datetime
        import json
        
        model_info = {
            "available_models": list(advanced_face_recognition.models.keys()),
            "model_descriptions": {
                "mediapipe": "Google's MediaPipe face detection - Fast and lightweight",
                "insightface": "State-of-the-art face recognition with high accuracy",
                "dlib": "Traditional face recognition using HOG + Linear SVM",
                "deepface_facenet": "FaceNet model via DeepFace - High accuracy",
                "deepface_vgg-face": "VGG-Face model via DeepFace - Robust recognition",
                "deepface_openface": "OpenFace model via DeepFace - Lightweight option"
            },
            "setup_date": str(datetime.now()),
            "status": "initialized"
        }
        
        with open("face_recognition_models.json", "w") as f:
            json.dump(model_info, f, indent=2)
        
        print(f"Model info saved to face_recognition_models.json")
        print(f"   Available models: {len(model_info['available_models'])}")
        
        return True
        
    except Exception as e:
        print(f"Failed to create model info file: {e}")
        return False


def main():
    """Main setup function."""
    print("Setting up Advanced Face Recognition System")
    print("=" * 50)
    
    steps = [
        ("Install Dependencies", install_requirements),
        ("Download Models", download_models),
        ("Test System", test_advanced_face_recognition),
        ("Migrate Database", run_database_migration),
        ("Create Model Info", create_model_info_file)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\nStep: {step_name}")
        print("-" * 30)
        
        try:
            success = step_func()
            results.append((step_name, success))
            
            if success:
                print(f"{step_name} completed successfully!")
            else:
                print(f"{step_name} failed!")
                
        except Exception as e:
            print(f"{step_name} crashed: {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("SETUP SUMMARY")
    print("=" * 50)
    
    successful_steps = 0
    for step_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} {step_name}")
        if success:
            successful_steps += 1
    
    print(f"\nSuccess Rate: {successful_steps}/{len(results)} steps completed")
    
    if successful_steps == len(results):
        print("\nAdvanced Face Recognition System setup completed successfully!")
        print("\nNext Steps:")
        print("1. Start the backend server: python start.py")
        print("2. Test face registration in the frontend")
        print("3. Try the new advanced face recognition features")
        print("\nAPI Endpoints:")
        print("- POST /face/register - Register face with advanced models")
        print("- POST /face/test - Test face quality")
        print("- GET /face/status - Check registration status")
        print("- POST /face/upgrade - Upgrade to advanced registration")
    else:
        print("\nSetup completed with some issues.")
        print("The system may still work with reduced functionality.")
        print("Check the error messages above for details.")


if __name__ == "__main__":
    main()