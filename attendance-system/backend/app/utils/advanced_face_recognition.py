"""
Advanced Face Recognition Module
Integrates multiple state-of-the-art face recognition models for enhanced accuracy
"""
import cv2
import numpy as np
import base64
import io
from PIL import Image
from typing import Optional, Dict, List, Tuple
import logging

# Import face recognition libraries
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

logger = logging.getLogger(__name__)


class AdvancedFaceRecognition:
    """Advanced face recognition using multiple models for enhanced accuracy"""
    
    def __init__(self):
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available face recognition models"""
        
        # Initialize MediaPipe Face Detection
        if MEDIAPIPE_AVAILABLE:
            try:
                mp_face_detection = mp.solutions.face_detection
                self.models['mediapipe'] = mp_face_detection.FaceDetection(
                    model_selection=1, min_detection_confidence=0.7
                )
                logger.info("MediaPipe face detection initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize MediaPipe: {e}")
        
        # Initialize InsightFace
        if INSIGHTFACE_AVAILABLE:
            try:
                app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
                app.prepare(ctx_id=0, det_size=(640, 640))
                self.models['insightface'] = app
                logger.info("InsightFace initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize InsightFace: {e}")
    
    def _decode_image(self, image_data: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        return np.array(image)
    
    def detect_faces_mediapipe(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using MediaPipe"""
        if 'mediapipe' not in self.models:
            return []
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.models['mediapipe'].process(rgb_image)
            
            faces = []
            if results.detections:
                h, w = image.shape[:2]
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    faces.append({
                        'bbox': (x, y, width, height),
                        'confidence': detection.score[0],
                        'model': 'mediapipe'
                    })
            return faces
        except Exception as e:
            logger.error(f"MediaPipe face detection error: {e}")
            return []
    
    def detect_faces_insightface(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using InsightFace"""
        if 'insightface' not in self.models:
            return []
        
        try:
            faces = self.models['insightface'].get(image)
            results = []
            
            for face in faces:
                bbox = face.bbox.astype(int)
                results.append({
                    'bbox': tuple(bbox),
                    'confidence': float(face.det_score),
                    'embedding': face.embedding,
                    'model': 'insightface'
                })
            return results
        except Exception as e:
            logger.error(f"InsightFace detection error: {e}")
            return []
    
    def detect_faces_dlib(self, image: np.ndarray) -> List[Dict]:
        """Detect faces using dlib (face_recognition library)"""
        if not FACE_RECOGNITION_AVAILABLE:
            return []
        
        try:
            face_locations = face_recognition.face_locations(image, model="hog")
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            results = []
            for i, (location, encoding) in enumerate(zip(face_locations, face_encodings)):
                top, right, bottom, left = location
                results.append({
                    'bbox': (left, top, right - left, bottom - top),
                    'confidence': 0.9,  # dlib doesn't provide confidence scores
                    'encoding': encoding,
                    'model': 'dlib'
                })
            return results
        except Exception as e:
            logger.error(f"Dlib face detection error: {e}")
            return []
    
    def get_face_embedding_deepface(self, image: np.ndarray, model_name: str = "Facenet") -> Optional[np.ndarray]:
        """Get face embedding using DeepFace"""
        if not DEEPFACE_AVAILABLE:
            return None
        
        try:
            # DeepFace expects RGB format
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            embedding = DeepFace.represent(
                img_path=rgb_image,
                model_name=model_name,
                enforce_detection=False
            )
            return np.array(embedding[0]["embedding"])
        except Exception as e:
            logger.error(f"DeepFace embedding error: {e}")
            return None
    
    def comprehensive_face_analysis(self, image_data: str) -> Dict:
        """Perform comprehensive face analysis using all available models"""
        try:
            image = self._decode_image(image_data)
            
            results = {
                'faces_detected': 0,
                'models_used': [],
                'face_data': [],
                'quality_score': 0.0,
                'best_face': None
            }
            
            # Detect faces with different models
            all_faces = []
            
            # MediaPipe detection
            mp_faces = self.detect_faces_mediapipe(image)
            if mp_faces:
                all_faces.extend(mp_faces)
                results['models_used'].append('mediapipe')
            
            # InsightFace detection
            if_faces = self.detect_faces_insightface(image)
            if if_faces:
                all_faces.extend(if_faces)
                results['models_used'].append('insightface')
            
            # Dlib detection
            dlib_faces = self.detect_faces_dlib(image)
            if dlib_faces:
                all_faces.extend(dlib_faces)
                results['models_used'].append('dlib')
            
            if not all_faces:
                return results
            
            # Find consensus faces (faces detected by multiple models)
            consensus_faces = self._find_consensus_faces(all_faces)
            
            # Get best face based on confidence and size
            best_face = self._select_best_face(consensus_faces, image.shape)
            
            if best_face:
                # Get multiple embeddings for the best face
                face_region = self._extract_face_region(image, best_face['bbox'])
                
                embeddings = {}
                
                # Get DeepFace embeddings with different models
                for model in ['Facenet', 'VGG-Face', 'OpenFace']:
                    embedding = self.get_face_embedding_deepface(face_region, model)
                    if embedding is not None:
                        embeddings[f'deepface_{model.lower()}'] = embedding
                
                # Get InsightFace embedding if available
                if 'embedding' in best_face:
                    embeddings['insightface'] = best_face['embedding']
                
                # Get dlib encoding if available
                if 'encoding' in best_face:
                    embeddings['dlib'] = best_face['encoding']
                
                results.update({
                    'faces_detected': len(consensus_faces),
                    'face_data': consensus_faces,
                    'best_face': best_face,
                    'embeddings': embeddings,
                    'quality_score': self._calculate_quality_score(best_face, image.shape)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive face analysis error: {e}")
            return {'faces_detected': 0, 'error': str(e)}
    
    def _find_consensus_faces(self, all_faces: List[Dict]) -> List[Dict]:
        """Find faces that are detected by multiple models"""
        if len(all_faces) <= 1:
            return all_faces
        
        consensus_faces = []
        used_indices = set()
        
        for i, face1 in enumerate(all_faces):
            if i in used_indices:
                continue
                
            similar_faces = [face1]
            used_indices.add(i)
            
            for j, face2 in enumerate(all_faces[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                if self._faces_overlap(face1['bbox'], face2['bbox']):
                    similar_faces.append(face2)
                    used_indices.add(j)
            
            # Create consensus face
            if len(similar_faces) > 1:
                consensus_face = self._merge_face_detections(similar_faces)
                consensus_faces.append(consensus_face)
            else:
                consensus_faces.append(face1)
        
        return consensus_faces
    
    def _faces_overlap(self, bbox1: Tuple, bbox2: Tuple, threshold: float = 0.5) -> bool:
        """Check if two face bounding boxes overlap significantly"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        intersection = x_overlap * y_overlap
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        # Calculate IoU
        iou = intersection / union if union > 0 else 0
        return iou > threshold
    
    def _merge_face_detections(self, faces: List[Dict]) -> Dict:
        """Merge multiple face detections into a consensus"""
        # Average bounding boxes
        bboxes = [face['bbox'] for face in faces]
        avg_bbox = tuple(int(np.mean([bbox[i] for bbox in bboxes])) for i in range(4))
        
        # Average confidence
        confidences = [face['confidence'] for face in faces]
        avg_confidence = np.mean(confidences)
        
        # Collect all embeddings/encodings
        merged_face = {
            'bbox': avg_bbox,
            'confidence': avg_confidence,
            'models': [face['model'] for face in faces],
            'consensus_count': len(faces)
        }
        
        # Add embeddings from different models
        for face in faces:
            if 'embedding' in face:
                merged_face['embedding'] = face['embedding']
            if 'encoding' in face:
                merged_face['encoding'] = face['encoding']
        
        return merged_face
    
    def _select_best_face(self, faces: List[Dict], image_shape: Tuple) -> Optional[Dict]:
        """Select the best face based on confidence, size, and consensus"""
        if not faces:
            return None
        
        best_face = None
        best_score = 0
        
        h, w = image_shape[:2]
        
        for face in faces:
            x, y, width, height = face['bbox']
            
            # Calculate face area ratio
            face_area = width * height
            image_area = w * h
            area_ratio = face_area / image_area
            
            # Calculate position score (prefer centered faces)
            center_x, center_y = x + width/2, y + height/2
            image_center_x, image_center_y = w/2, h/2
            center_distance = np.sqrt((center_x - image_center_x)**2 + (center_y - image_center_y)**2)
            max_distance = np.sqrt((w/2)**2 + (h/2)**2)
            position_score = 1 - (center_distance / max_distance)
            
            # Calculate consensus score
            consensus_score = face.get('consensus_count', 1) / 3  # Normalize by max possible models
            
            # Combined score
            score = (
                face['confidence'] * 0.4 +
                min(area_ratio * 10, 1.0) * 0.3 +  # Prefer faces that are 10% of image
                position_score * 0.2 +
                consensus_score * 0.1
            )
            
            if score > best_score:
                best_score = score
                best_face = face
        
        return best_face
    
    def _extract_face_region(self, image: np.ndarray, bbox: Tuple) -> np.ndarray:
        """Extract face region from image"""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
    
    def _calculate_quality_score(self, face: Dict, image_shape: Tuple) -> float:
        """Calculate overall quality score for the face"""
        x, y, w, h = face['bbox']
        img_h, img_w = image_shape[:2]
        
        # Size score
        face_area = w * h
        image_area = img_w * img_h
        area_ratio = face_area / image_area
        size_score = min(area_ratio * 10, 1.0)  # Optimal at 10% of image
        
        # Position score
        center_x, center_y = x + w/2, y + h/2
        img_center_x, img_center_y = img_w/2, img_h/2
        center_distance = np.sqrt((center_x - img_center_x)**2 + (center_y - img_center_y)**2)
        max_distance = np.sqrt((img_w/2)**2 + (img_h/2)**2)
        position_score = 1 - (center_distance / max_distance)
        
        # Confidence score
        confidence_score = face['confidence']
        
        # Consensus score
        consensus_score = face.get('consensus_count', 1) / 3
        
        return (size_score * 0.3 + position_score * 0.2 + confidence_score * 0.4 + consensus_score * 0.1)
    
    def compare_faces_advanced(self, known_embeddings: Dict, test_image_data: str, threshold: float = 0.6) -> Dict:
        """Advanced face comparison using multiple models"""
        test_analysis = self.comprehensive_face_analysis(test_image_data)
        
        if test_analysis['faces_detected'] == 0:
            return {
                'match': False,
                'confidence': 0.0,
                'reason': 'No face detected in test image'
            }
        
        test_embeddings = test_analysis.get('embeddings', {})
        if not test_embeddings:
            return {
                'match': False,
                'confidence': 0.0,
                'reason': 'Could not extract embeddings from test image'
            }
        
        # Compare embeddings from different models
        model_results = {}
        
        for model_name in known_embeddings:
            if model_name in test_embeddings:
                similarity = self._calculate_similarity(
                    known_embeddings[model_name],
                    test_embeddings[model_name],
                    model_name
                )
                model_results[model_name] = similarity
        
        if not model_results:
            return {
                'match': False,
                'confidence': 0.0,
                'reason': 'No compatible embeddings found'
            }
        
        # Weighted average of model results
        weights = {
            'insightface': 0.35,
            'deepface_facenet': 0.25,
            'dlib': 0.20,
            'deepface_vgg-face': 0.15,
            'deepface_openface': 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for model, score in model_results.items():
            weight = weights.get(model, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        final_confidence = weighted_score / total_weight if total_weight > 0 else 0.0
        is_match = final_confidence > threshold
        
        return {
            'match': is_match,
            'confidence': final_confidence,
            'model_results': model_results,
            'threshold': threshold,
            'quality_score': test_analysis.get('quality_score', 0.0)
        }
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray, model_name: str) -> float:
        """Calculate similarity between two embeddings"""
        try:
            if model_name.startswith('deepface') or model_name == 'insightface':
                # Cosine similarity for deep learning models
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                similarity = dot_product / (norm1 * norm2)
                return (similarity + 1) / 2  # Normalize to 0-1
            
            elif model_name == 'dlib':
                # Euclidean distance for dlib (lower is better)
                distance = np.linalg.norm(embedding1 - embedding2)
                return max(0, 1 - distance)  # Convert to similarity score
            
            else:
                # Default cosine similarity
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                similarity = dot_product / (norm1 * norm2)
                return (similarity + 1) / 2
                
        except Exception as e:
            logger.error(f"Similarity calculation error for {model_name}: {e}")
            return 0.0


# Global instance
advanced_face_recognition = AdvancedFaceRecognition()