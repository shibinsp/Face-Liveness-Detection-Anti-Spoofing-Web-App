"""
MediaPipe-based Liveness Detection Module
Includes blink detection and head movement tracking
"""

import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import time


class MediaPipeLiveness:
    """MediaPipe-based liveness detection with blink and head movement"""
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Eye landmarks indices (MediaPipe face mesh)
        # Left eye: 362, 385, 387, 263, 373, 380
        # Right eye: 33, 160, 158, 133, 153, 144
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # Face oval landmarks for head pose
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                          397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                          172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        # Blink detection parameters
        self.EAR_THRESHOLD = 0.21  # Eye Aspect Ratio threshold
        self.CONSECUTIVE_FRAMES = 2  # Frames to confirm blink
        self.blink_counter = 0
        self.total_blinks = 0
        self.blink_history = deque(maxlen=30)  # Last 30 frames
        
        # Head movement parameters
        self.head_pose_history = deque(maxlen=30)
        self.movement_detected = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'neutral': True
        }
        
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR)
        
        Args:
            eye_landmarks: List of 6 eye landmark coordinates
            
        Returns:
            EAR value
        """
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR calculation
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def detect_blink(self, landmarks, image_shape):
        """
        Detect eye blinks using EAR
        
        Args:
            landmarks: MediaPipe face landmarks
            image_shape: Image dimensions (height, width)
            
        Returns:
            (is_blinking, ear_left, ear_right, blink_count)
        """
        h, w = image_shape[:2]
        
        # Extract left eye landmarks
        left_eye_coords = np.array([(landmarks[i].x * w, landmarks[i].y * h) 
                                    for i in self.LEFT_EYE])
        
        # Extract right eye landmarks
        right_eye_coords = np.array([(landmarks[i].x * w, landmarks[i].y * h) 
                                     for i in self.RIGHT_EYE])
        
        # Calculate EAR for both eyes
        ear_left = self.calculate_eye_aspect_ratio(left_eye_coords)
        ear_right = self.calculate_eye_aspect_ratio(right_eye_coords)
        
        # Average EAR
        ear_avg = (ear_left + ear_right) / 2.0
        
        # Blink detection
        is_blinking = False
        if ear_avg < self.EAR_THRESHOLD:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.CONSECUTIVE_FRAMES:
                self.total_blinks += 1
                is_blinking = True
            self.blink_counter = 0
        
        # Update history
        self.blink_history.append(ear_avg)
        
        return is_blinking, ear_left, ear_right, self.total_blinks
    
    def calculate_head_pose(self, landmarks, image_shape):
        """
        Calculate head pose (pitch, yaw, roll)
        
        Args:
            landmarks: MediaPipe face landmarks
            image_shape: Image dimensions
            
        Returns:
            (pitch, yaw, roll, movement_direction)
        """
        h, w = image_shape[:2]
        
        # Key points for head pose estimation
        # Nose tip
        nose_tip = np.array([landmarks[1].x * w, landmarks[1].y * h])
        
        # Chin
        chin = np.array([landmarks[152].x * w, landmarks[152].y * h])
        
        # Left eye corner
        left_eye = np.array([landmarks[33].x * w, landmarks[33].y * h])
        
        # Right eye corner
        right_eye = np.array([landmarks[263].x * w, landmarks[263].y * h])
        
        # Forehead center
        forehead = np.array([landmarks[10].x * w, landmarks[10].y * h])
        
        # Calculate angles
        # Yaw (left/right): based on eye positions relative to nose
        eye_center = (left_eye + right_eye) / 2
        eye_to_nose = nose_tip[0] - eye_center[0]
        face_width = np.linalg.norm(left_eye - right_eye)
        yaw = (eye_to_nose / face_width) * 100  # Normalized
        
        # Pitch (up/down): based on nose to chin distance
        nose_to_chin = chin[1] - nose_tip[1]
        face_height = np.linalg.norm(forehead - chin)
        pitch = (nose_to_chin / face_height) * 100 - 30  # Normalized and centered
        
        # Roll (tilt): based on eye alignment
        eye_angle = np.arctan2(right_eye[1] - left_eye[1], 
                               right_eye[0] - left_eye[0])
        roll = np.degrees(eye_angle)
        
        # Determine movement direction
        movement = 'neutral'
        if yaw < -15:
            movement = 'left'
            self.movement_detected['left'] = True
        elif yaw > 15:
            movement = 'right'
            self.movement_detected['right'] = True
        elif pitch < -15:
            movement = 'up'
            self.movement_detected['up'] = True
        elif pitch > 15:
            movement = 'down'
            self.movement_detected['down'] = True
        
        # Update history
        self.head_pose_history.append((pitch, yaw, roll))
        
        return pitch, yaw, roll, movement
    
    def draw_landmarks(self, image, landmarks):
        """
        Draw face mesh landmarks on image
        
        Args:
            image: Input image
            landmarks: MediaPipe face landmarks
            
        Returns:
            Image with drawn landmarks
        """
        h, w = image.shape[:2]
        
        # Draw eye landmarks (green)
        for idx in self.LEFT_EYE + self.RIGHT_EYE:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
        
        # Draw face oval (blue)
        for idx in self.FACE_OVAL:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(image, (x, y), 1, (255, 0, 0), -1)
        
        # Draw nose tip (red)
        nose_x = int(landmarks[1].x * w)
        nose_y = int(landmarks[1].y * h)
        cv2.circle(image, (nose_x, nose_y), 3, (0, 0, 255), -1)
        
        return image
    
    def process_frame(self, frame):
        """
        Process a single frame for liveness detection
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            (processed_frame, blink_info, head_pose_info, is_live)
        """
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return frame, None, None, False
        
        # Get first face
        face_landmarks = results.multi_face_landmarks[0].landmark
        
        # Detect blinks
        is_blinking, ear_left, ear_right, blink_count = self.detect_blink(
            face_landmarks, frame.shape
        )
        
        # Calculate head pose
        pitch, yaw, roll, movement = self.calculate_head_pose(
            face_landmarks, frame.shape
        )
        
        # Draw landmarks
        annotated_frame = frame.copy()
        annotated_frame = self.draw_landmarks(annotated_frame, face_landmarks)
        
        # Add text overlays
        # Blink info
        blink_color = (0, 255, 0) if is_blinking else (255, 255, 255)
        cv2.putText(annotated_frame, f"Blinks: {blink_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, blink_color, 2)
        cv2.putText(annotated_frame, f"EAR: {((ear_left + ear_right) / 2):.3f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Head movement info
        movement_color = (0, 255, 255) if movement != 'neutral' else (255, 255, 255)
        cv2.putText(annotated_frame, f"Head: {movement.upper()}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, movement_color, 2)
        cv2.putText(annotated_frame, f"Yaw: {yaw:.1f} Pitch: {pitch:.1f}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Determine if live based on interaction
        # Consider live if: blinks detected OR significant head movement
        is_live = (blink_count > 0) or any([
            self.movement_detected['left'],
            self.movement_detected['right'],
            self.movement_detected['up'],
            self.movement_detected['down']
        ])
        
        blink_info = {
            'is_blinking': is_blinking,
            'ear_left': ear_left,
            'ear_right': ear_right,
            'total_blinks': blink_count
        }
        
        head_pose_info = {
            'pitch': pitch,
            'yaw': yaw,
            'roll': roll,
            'movement': movement,
            'movements_detected': self.movement_detected.copy()
        }
        
        return annotated_frame, blink_info, head_pose_info, is_live
    
    def reset_detection(self):
        """Reset all detection counters"""
        self.blink_counter = 0
        self.total_blinks = 0
        self.blink_history.clear()
        self.head_pose_history.clear()
        self.movement_detected = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'neutral': True
        }
    
    def get_liveness_score(self):
        """
        Calculate overall liveness score
        
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        # Blink detection (40% weight)
        if self.total_blinks > 0:
            score += 0.4
        
        # Head movement (60% weight - 15% per direction)
        if self.movement_detected['left']:
            score += 0.15
        if self.movement_detected['right']:
            score += 0.15
        if self.movement_detected['up']:
            score += 0.15
        if self.movement_detected['down']:
            score += 0.15
        
        return min(score, 1.0)


if __name__ == "__main__":
    # Test the liveness detection
    print("Testing MediaPipe Liveness Detection...")
    print("Press 'q' to quit, 'r' to reset counters")
    
    liveness = MediaPipeLiveness()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        processed_frame, blink_info, head_info, is_live = liveness.process_frame(frame)
        
        # Display liveness score
        score = liveness.get_liveness_score()
        cv2.putText(processed_frame, f"Liveness: {score:.2f}", (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if is_live else (0, 0, 255), 2)
        
        cv2.imshow('MediaPipe Liveness Detection', processed_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            liveness.reset_detection()
            print("Counters reset!")
    
    cap.release()
    cv2.destroyAllWindows()

