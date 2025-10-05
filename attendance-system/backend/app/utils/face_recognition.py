import face_recognition
import numpy as np
from typing import Optional, List, Dict
from PIL import Image
import io
import base64
import logging
from app.utils.advanced_face_recognition import advanced_face_recognition

logger = logging.getLogger(__name__)


def encode_face_from_base64(image_data: str) -> Optional[str]:
    """Extract face encoding from base64 image data."""
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return None
            
        # Return first face encoding as string
        encoding = face_encodings[0]
        return ','.join(map(str, encoding))
        
    except Exception:
        return None


def validate_and_encode_face_advanced(image_data: str, test_only: bool = False) -> dict:
    """Advanced face validation and encoding using multiple models."""
    try:
        # Use advanced face recognition for comprehensive analysis
        analysis = advanced_face_recognition.comprehensive_face_analysis(image_data)
        
        if analysis['faces_detected'] == 0:
            return {
                "success": False,
                "error": "no_face_detected",
                "message": "No face detected in image"
            }
        
        if analysis['faces_detected'] > 1:
            return {
                "success": False,
                "error": "multiple_faces",
                "message": "Multiple faces detected",
                "error_details": {"face_count": analysis['faces_detected']}
            }
        
        quality_score = analysis.get('quality_score', 0.0)
        
        # Quality threshold check
        if quality_score < 0.4:
            return {
                "success": False,
                "error": "poor_quality",
                "message": "Image quality too poor for registration",
                "error_details": {"quality_score": quality_score}
            }
        
        result = {
            "success": True,
            "quality_score": quality_score,
            "confidence": analysis['best_face']['confidence'],
            "models_used": analysis['models_used'],
            "face_location": analysis['best_face']['bbox']
        }
        
        if not test_only:
            # Store all embeddings as JSON for multi-model verification
            embeddings = analysis.get('embeddings', {})
            if embeddings:
                # Convert numpy arrays to lists for JSON serialization
                serializable_embeddings = {}
                for model, embedding in embeddings.items():
                    if isinstance(embedding, np.ndarray):
                        serializable_embeddings[model] = embedding.tolist()
                    else:
                        serializable_embeddings[model] = embedding
                
                import json
                result["advanced_encoding"] = json.dumps(serializable_embeddings)
            
            # Fallback to traditional encoding for backward compatibility
            if 'dlib' in embeddings:
                result["encoding"] = ','.join(map(str, embeddings['dlib']))
        
        return result
        
    except Exception as e:
        logger.error(f"Advanced face validation error: {e}")
        # Fallback to original method
        return validate_and_encode_face(image_data, test_only)


def validate_and_encode_face(image_data: str, test_only: bool = False) -> dict:
    """Original face validation method (kept for backward compatibility)."""
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Check image dimensions
        height, width = image_array.shape[:2]
        if width < 200 or height < 200:
            return {
                "success": False,
                "error": "poor_quality",
                "message": "Image resolution too low",
                "error_details": {"quality_issues": ["image too small (minimum 200x200 pixels)"]}
            }
        
        # Get face locations and encodings
        face_locations = face_recognition.face_locations(image_array)
        
        if len(face_locations) == 0:
            return {
                "success": False,
                "error": "no_face_detected",
                "message": "No face detected in image"
            }
        
        if len(face_locations) > 1:
            return {
                "success": False,
                "error": "multiple_faces",
                "message": "Multiple faces detected",
                "error_details": {"face_count": len(face_locations)}
            }
        
        # Get face encoding
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if not face_encodings:
            return {
                "success": False,
                "error": "no_face_detected",
                "message": "Could not encode face"
            }
        
        # Quality checks
        face_location = face_locations[0]
        top, right, bottom, left = face_location
        
        # Face size check
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        image_area = width * height
        face_ratio = face_area / image_area
        
        quality_issues = []
        quality_score = 1.0
        
        # Face should occupy reasonable portion of image
        if face_ratio < 0.05:
            quality_issues.append("face too small in image")
            quality_score -= 0.3
        elif face_ratio > 0.8:
            quality_issues.append("face too close to camera")
            quality_score -= 0.2
        
        # Check if face is roughly centered
        face_center_x = (left + right) / 2
        face_center_y = (top + bottom) / 2
        image_center_x = width / 2
        image_center_y = height / 2
        
        center_offset_x = abs(face_center_x - image_center_x) / width
        center_offset_y = abs(face_center_y - image_center_y) / height
        
        if center_offset_x > 0.3 or center_offset_y > 0.3:
            quality_issues.append("face not centered")
            quality_score -= 0.1
        
        # Check aspect ratio (face should be roughly oval)
        face_aspect_ratio = face_width / face_height
        if face_aspect_ratio < 0.6 or face_aspect_ratio > 1.4:
            quality_issues.append("unusual face proportions")
            quality_score -= 0.2
        
        # Brightness check (simple)
        face_region = image_array[top:bottom, left:right]
        if len(face_region.shape) == 3:
            face_brightness = np.mean(face_region)
        else:
            face_brightness = np.mean(face_region)
        
        if face_brightness < 50:
            quality_issues.append("image too dark")
            quality_score -= 0.3
        elif face_brightness > 200:
            quality_issues.append("image too bright")
            quality_score -= 0.2
        
        # Final quality assessment
        if quality_score < 0.4 and quality_issues:
            return {
                "success": False,
                "error": "poor_quality",
                "message": "Image quality too poor for registration",
                "error_details": {"quality_issues": quality_issues}
            }
        
        # Calculate confidence based on encoding quality
        encoding = face_encodings[0]
        confidence = min(1.0, max(0.0, 1.0 - (np.std(encoding) / 2.0)))
        
        result = {
            "success": True,
            "quality_score": max(0.0, quality_score),
            "confidence": confidence,
            "face_location": face_location,
            "face_ratio": face_ratio
        }
        
        if not test_only:
            result["encoding"] = ','.join(map(str, encoding))
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": "invalid_image",
            "message": f"Image processing failed: {str(e)}"
        }


def verify_face_advanced(known_embeddings_json: str, image_data: str, tolerance: float = 0.6) -> Dict:
    """Advanced face verification using multiple models."""
    try:
        import json
        
        # Parse known embeddings
        known_embeddings = json.loads(known_embeddings_json)
        
        # Convert lists back to numpy arrays
        for model, embedding in known_embeddings.items():
            if isinstance(embedding, list):
                known_embeddings[model] = np.array(embedding)
        
        # Compare using advanced face recognition
        result = advanced_face_recognition.compare_faces_advanced(
            known_embeddings, image_data, tolerance
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Advanced face verification error: {e}")
        # Fallback to original method if advanced fails
        if 'dlib' in known_embeddings_json:
            try:
                known_embeddings = json.loads(known_embeddings_json)
                if 'dlib' in known_embeddings:
                    dlib_encoding = ','.join(map(str, known_embeddings['dlib']))
                    is_match = verify_face(dlib_encoding, image_data, tolerance)
                    return {
                        'match': is_match,
                        'confidence': 0.8 if is_match else 0.2,
                        'method': 'fallback_dlib'
                    }
            except:
                pass
        
        return {
            'match': False,
            'confidence': 0.0,
            'reason': f'Verification failed: {str(e)}'
        }


def verify_face(known_encoding_str: str, image_data: str, tolerance: float = 0.6) -> bool:
    """Original face verification method (kept for backward compatibility)."""
    try:
        # Parse known encoding
        known_encoding = np.array([float(x) for x in known_encoding_str.split(',')])
        
        # Get encoding from new image
        new_encoding_str = encode_face_from_base64(image_data)
        if not new_encoding_str:
            return False
            
        new_encoding = np.array([float(x) for x in new_encoding_str.split(',')])
        
        # Compare faces
        results = face_recognition.compare_faces([known_encoding], new_encoding, tolerance=tolerance)
        return results[0] if results else False
        
    except Exception:
        return False