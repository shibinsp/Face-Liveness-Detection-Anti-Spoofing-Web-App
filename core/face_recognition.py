"""
Face Recognition Module
Uses YOLO v11 for face detection and DeepFace for face recognition
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import os

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed. YOLO face detection unavailable.")

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("Warning: deepface not installed. Using fallback face recognition.")


class FaceRecognitionSystem:
    """Face recognition system with YOLO v11 detection"""
    
    def __init__(self, model_name='Facenet512'):
        """
        Initialize face recognition system
        
        Args:
            model_name: DeepFace model ('VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib', 'SFace')
        """
        self.model_name = model_name
        self.yolo_model = None
        
        # Load YOLO v11 face detection model if available
        if YOLO_AVAILABLE:
            try:
                # Try to load YOLO v11 face detection model
                # You can download a pretrained YOLO face model or use general YOLO
                self.yolo_model = YOLO('yolo11n.pt')  # Using YOLOv11 nano
                print(f"✓ YOLO v11 loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load YOLO model: {e}")
                self.yolo_model = None
        
        # Initialize DeepFace model
        if DEEPFACE_AVAILABLE:
            try:
                # Preload the model
                DeepFace.build_model(model_name=self.model_name)
                print(f"✓ DeepFace model '{self.model_name}' loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load DeepFace model: {e}")
    
    def detect_faces_yolo(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using YOLO v11
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of face bounding boxes (x1, y1, x2, y2)
        """
        if not self.yolo_model:
            return []
        
        try:
            # Run YOLO detection
            results = self.yolo_model(image, verbose=False)
            
            faces = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Filter for person class (class 0 in COCO)
                    # For face-specific YOLO, adjust class filter
                    if box.cls[0] == 0:  # Person class
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        faces.append((int(x1), int(y1), int(x2), int(y2)))
            
            return faces
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []
    
    def detect_faces_cv2(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Fallback face detection using OpenCV Haar Cascade
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of face bounding boxes (x1, y1, x2, y2)
        """
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces_rect = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )
        
        # Convert (x, y, w, h) to (x1, y1, x2, y2)
        faces = []
        for (x, y, w, h) in faces_rect:
            faces.append((x, y, x+w, y+h))
        
        return faces
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using available method
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of face bounding boxes (x1, y1, x2, y2)
        """
        # Try YOLO first, fallback to OpenCV
        if self.yolo_model:
            faces = self.detect_faces_yolo(image)
            if faces:
                return faces
        
        # Fallback to OpenCV
        return self.detect_faces_cv2(image)
    
    def extract_face_embedding(self, image: np.ndarray, 
                              face_bbox: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Extract face embedding from image
        
        Args:
            image: Input image (BGR)
            face_bbox: Optional face bounding box (x1, y1, x2, y2)
            
        Returns:
            Face embedding vector or None
        """
        if not DEEPFACE_AVAILABLE:
            print("DeepFace not available")
            return None
        
        try:
            # Extract face region if bbox provided
            if face_bbox:
                x1, y1, x2, y2 = face_bbox
                face_img = image[y1:y2, x1:x2]
            else:
                face_img = image
            
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            
            # Get embedding using DeepFace
            # Use 'opencv' detector to avoid retinaface keras3 validation issues
            embedding_objs = DeepFace.represent(
                img_path=face_rgb,
                model_name=self.model_name,
                detector_backend='opencv',
                enforce_detection=False
            )
            
            if embedding_objs:
                embedding = np.array(embedding_objs[0]['embedding'])
                return embedding
            
            return None
            
        except Exception as e:
            print(f"Embedding extraction error: {e}")
            return None
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Convert to 0-1 range
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def recognize_face(self, image: np.ndarray,
                      known_embeddings: List[Tuple[int, str, np.ndarray]],
                      threshold: float = 0.6) -> Tuple[Optional[int], Optional[str], float]:
        """
        Recognize face from image against known embeddings

        Args:
            image: Input image (BGR)
            known_embeddings: List of (user_id, name, embedding)
            threshold: Similarity threshold for recognition

        Returns:
            (user_id, name, confidence) or (None, None, 0.0) if no match
        """
        # Detect faces
        faces = self.detect_faces(image)

        if not faces:
            return None, None, 0.0

        # Use largest face (closest to camera)
        largest_face = max(faces, key=lambda f: (f[2]-f[0]) * (f[3]-f[1]))

        # Extract embedding
        embedding = self.extract_face_embedding(image, largest_face)

        if embedding is None:
            return None, None, 0.0

        # Compare with known embeddings
        best_match_id = None
        best_match_name = None
        best_similarity = 0.0

        for user_id, name, known_embedding in known_embeddings:
            similarity = self.calculate_similarity(embedding, known_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = user_id
                best_match_name = name

        # Check if above threshold
        if best_similarity >= threshold:
            return best_match_id, best_match_name, best_similarity

        return None, None, best_similarity

    def recognize_all_faces(self, image: np.ndarray,
                           known_embeddings: List[Tuple[int, str, np.ndarray]],
                           threshold: float = 0.6) -> List[Tuple[Optional[int], Optional[str], float, Tuple[int, int, int, int]]]:
        """
        Recognize ALL faces from image against known embeddings

        Args:
            image: Input image (BGR)
            known_embeddings: List of (user_id, name, embedding)
            threshold: Similarity threshold for recognition

        Returns:
            List of (user_id, name, confidence, bbox) for each detected face
        """
        # Detect all faces
        faces = self.detect_faces(image)

        if not faces:
            return []

        results = []

        # Process EACH face
        for face_bbox in faces:
            # Extract embedding for this face
            embedding = self.extract_face_embedding(image, face_bbox)

            if embedding is None:
                results.append((None, None, 0.0, face_bbox))
                continue

            # Compare with known embeddings
            best_match_id = None
            best_match_name = None
            best_similarity = 0.0

            for user_id, name, known_embedding in known_embeddings:
                similarity = self.calculate_similarity(embedding, known_embedding)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_id = user_id
                    best_match_name = name

            # Check if above threshold
            if best_similarity >= threshold:
                results.append((best_match_id, best_match_name, best_similarity, face_bbox))
            else:
                results.append((None, None, best_similarity, face_bbox))

        return results
    
    def save_face_image(self, image: np.ndarray, user_name: str, 
                       save_dir: str = 'data/faces') -> str:
        """
        Save face image to disk
        
        Args:
            image: Face image (BGR)
            user_name: User's name
            save_dir: Directory to save images
            
        Returns:
            Path to saved image
        """
        # Create directory if not exists
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{user_name.replace(' ', '_').lower()}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        # Save image
        cv2.imwrite(filepath, image)
        
        return filepath


# Simplified face recognition for cases without DeepFace
class SimpleFaceRecognition:
    """Simple face recognition using feature matching"""
    
    def __init__(self):
        """Initialize simple face recognition"""
        self.orb = cv2.ORB_create(nfeatures=500)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    def extract_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract ORB features from image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        return descriptors
    
    def match_faces(self, descriptors1, descriptors2) -> float:
        """Match two sets of descriptors"""
        if descriptors1 is None or descriptors2 is None:
            return 0.0
        
        try:
            matches = self.bf.match(descriptors1, descriptors2)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Calculate similarity score
            if len(matches) > 0:
                avg_distance = sum([m.distance for m in matches[:50]]) / min(50, len(matches))
                similarity = max(0, 1 - (avg_distance / 100))
                return similarity
            
            return 0.0
        except:
            return 0.0

