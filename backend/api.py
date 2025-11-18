"""
FastAPI Backend for Face Authentication System
REST API endpoints for face recognition, liveness detection, and user management
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import cv2
import numpy as np
import os
import sys
import base64
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import HybridLivenessDetection
from core.database import UserDatabase
from core.face_recognition import FaceRecognitionSystem
from backend.api_auth import optional_api_key, api_key_manager
from backend.admin_manager import admin_manager

# Initialize FastAPI
app = FastAPI(
    title="Face Authentication API",
    description="REST API for face recognition with liveness detection",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with optional API key tracking"""
    # Get API key from header
    api_key = request.headers.get("x-api-key")
    user_agent = request.headers.get("user-agent")
    
    # Process request
    response = await call_next(request)
    
    # Log the request
    status = "SUCCESS" if response.status_code < 400 else "ERROR"
    if not api_key:
        status = "NO_KEY"
    elif not api_key_manager.verify_api_key(api_key):
        status = "INVALID_KEY"
    
    api_key_manager.log_request(
        request=request,
        api_key=api_key,
        status=status,
        user_agent=user_agent,
        response_status=response.status_code
    )
    
    return response

# Initialize systems
db = UserDatabase()
face_rec = FaceRecognitionSystem(model_name='Facenet512')
hybrid_detector = HybridLivenessDetection(
    security_level=3,
    variance_threshold=10,
    edge_threshold=1.0,
    confidence_threshold=0.20
)

# Pydantic models
class RegisterRequest(BaseModel):
    name: str
    email: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    confidence: Optional[float] = None
    liveness_score: Optional[float] = None
    antispoof_confidence: Optional[float] = None

class UserInfo(BaseModel):
    id: int
    name: str
    email: Optional[str]
    created_at: str
    last_login: Optional[str]
    image_path: Optional[str]

class LoginHistoryItem(BaseModel):
    id: int
    login_time: str
    liveness_score: float
    confidence_score: float
    status: str


# Helper functions
def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 image to numpy array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Decode base64
        img_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

def encode_image_to_base64(image: np.ndarray) -> str:
    """Encode numpy array to base64"""
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Face Authentication API",
        "version": "2.0.0",
        "endpoints": [
            "/api/users/count",
            "/api/register",
            "/api/login",
            "/api/user/{user_id}",
            "/api/user/{user_id}/history"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "face_recognition": "loaded",
            "liveness_detection": "loaded"
        }
    }

@app.get("/api/users/count")
async def get_user_count():
    """Get total number of registered users"""
    try:
        count = db.get_user_count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/register")
async def register_user(
    name: str = Form(...),
    email: Optional[str] = Form(None),
    image: str = Form(...)
):
    """Register a new user with face image"""
    try:
        # Decode image
        frame = decode_base64_image(image)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Detect faces
        faces = face_rec.detect_faces(frame)

        if not faces:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "No face detected in the image. Please ensure your face is clearly visible."
                }
            )

        # Get largest face
        largest_face = max(faces, key=lambda f: (f[2]-f[0]) * (f[3]-f[1]))

        # Extract face embedding
        embedding = face_rec.extract_face_embedding(frame, largest_face)

        if embedding is None:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Failed to extract face features. Please try again."
                }
            )

        # Save face image
        image_path = face_rec.save_face_image(frame, name)

        # Register user in database
        success, message = db.register_user(name, embedding, image_path, email)

        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": message
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login_user(
    image: str = Form(...),
    recognition_threshold: float = Form(0.6),
    security_level: int = Form(3)
):
    """
    Authenticate user with ANTI-SPOOFING FIRST, then face recognition

    NEW FLOW (Security-First Approach):
    1. Detect face and run anti-spoofing detection
    2. If FAKE/PHONE SCREEN detected -> Reject with "Show your real face"
    3. If REAL -> Proceed to face recognition
    4. If face matches registered user -> Allow login
    5. If face doesn't match -> Reject with "Face not recognized"
    """
    try:
        # Decode image
        frame = decode_base64_image(image)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Get all registered embeddings
        known_embeddings = db.get_all_face_embeddings()

        if not known_embeddings:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "No registered users found. Please register first."
                }
            )

        # STEP 1: ANTI-SPOOFING DETECTION (FIRST AND FOREMOST!)
        # This is the PRIMARY security check - detect real vs fake faces
        result = hybrid_detector.detect_hybrid(frame)

        # Draw bounding boxes and labels on the frame
        annotated_frame = hybrid_detector.draw_results(frame, result)
        annotated_image = encode_image_to_base64(annotated_frame)

        antispoof_result = result['antispoof_result']
        mediapipe_result = result['mediapipe_result']

        # Check if face was detected at all
        if not antispoof_result['face_detected']:
            return {
                "success": False,
                "message": "No face detected. Please position your face in the camera.",
                "user_id": None,
                "user_name": None,
                "confidence": 0.0,
                "liveness_score": 0.0,
                "antispoof_confidence": 0.0,
                "is_live": False,
                "is_real": False,
                "annotated_image": annotated_image,
                "spoofing_attempt": False
            }

        # CRITICAL: Check for PHONE SCREEN / FAKE FACE (Primary Security Check)
        is_phone_screen = antispoof_result.get('likely_phone', False)
        is_real_face = antispoof_result['is_real']
        is_live = mediapipe_result['is_live']

        # REJECT if phone screen or fake face detected
        if is_phone_screen:
            # Phone screen detected - specific message
            phone_indicators = antispoof_result.get('phone_indicators', 0)
            return {
                "success": False,
                "message": f"⚠️ PHONE SCREEN DETECTED! Show your REAL FACE, not a photo or video. ({phone_indicators} indicators detected)",
                "user_id": None,
                "user_name": None,
                "confidence": 0.0,
                "liveness_score": mediapipe_result['liveness_score'],
                "antispoof_confidence": antispoof_result['confidence'],
                "is_live": is_live,
                "is_real": False,
                "annotated_image": annotated_image,
                "spoofing_attempt": True,
                "spoofing_type": "phone_screen"
            }

        if not is_real_face:
            # Fake face detected (photo, video, etc.) but not identified as phone
            return {
                "success": False,
                "message": "⚠️ FAKE FACE DETECTED! Show your REAL FACE, not a photo or printed image.",
                "user_id": None,
                "user_name": None,
                "confidence": 0.0,
                "liveness_score": mediapipe_result['liveness_score'],
                "antispoof_confidence": antispoof_result['confidence'],
                "is_live": is_live,
                "is_real": False,
                "annotated_image": annotated_image,
                "spoofing_attempt": True,
                "spoofing_type": "fake_photo"
            }

        # REJECT if not live (no blinks/movement detected)
        if not result['verified']:
            # Real face detected but no liveness proof yet
            return {
                "success": False,
                "message": result['message'],  # Message from hybrid detector (e.g., "Waiting for liveness proof")
                "user_id": None,
                "user_name": None,
                "confidence": 0.0,
                "liveness_score": mediapipe_result['liveness_score'],
                "antispoof_confidence": antispoof_result['confidence'],
                "is_live": False,
                "is_real": True,
                "annotated_image": annotated_image,
                "spoofing_attempt": False
            }

        # STEP 2: FACE RECOGNITION (Only if anti-spoofing passed!)
        # Now that we've confirmed it's a REAL, LIVE face, check WHO they are
        # Recognize ALL faces in the frame
        all_recognized = face_rec.recognize_all_faces(
            frame, known_embeddings, threshold=recognition_threshold
        )

        # Get primary face (largest/first recognized face)
        primary_user_id = None
        primary_name = None
        primary_confidence = 0.0

        recognized_users = []
        for user_id, name, confidence, bbox in all_recognized:
            if user_id is not None:
                # Convert bbox numpy types to native Python types
                x1, y1, x2, y2 = bbox
                recognized_users.append({
                    "user_id": int(user_id),
                    "name": str(name),
                    "confidence": float(confidence),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })
                # Set primary user (first recognized or highest confidence)
                if primary_user_id is None or confidence > primary_confidence:
                    primary_user_id = user_id
                    primary_name = name
                    primary_confidence = confidence

        if primary_user_id is None:
            # Real face(s) detected but none recognized - not in database
            face_count = len(all_recognized)
            return {
                "success": False,
                "message": f"✅ {face_count} face(s) detected, but NOT RECOGNIZED. Please ensure you are registered.",
                "user_id": None,
                "user_name": None,
                "confidence": 0.0,
                "liveness_score": mediapipe_result['liveness_score'],
                "antispoof_confidence": antispoof_result['confidence'],
                "is_live": True,
                "is_real": True,
                "annotated_image": annotated_image,
                "spoofing_attempt": False,
                "face_count": face_count,
                "all_faces": []
            }

        # SUCCESS: Real, live face that matches a registered user
        # Update database for primary user
        db.update_last_login(primary_user_id)
        db.add_login_history(
            primary_user_id,
            mediapipe_result['liveness_score'],
            antispoof_result['confidence'],
            'success'
        )

        # Build success message
        if len(recognized_users) > 1:
            other_names = [u['name'] for u in recognized_users if u['user_id'] != primary_user_id]
            message = f"✅ Authentication successful! Welcome {primary_name}! (Also detected: {', '.join(other_names)})"
        else:
            message = f"✅ Authentication successful! Welcome {primary_name}!"

        return {
            "success": True,
            "message": message,
            "user_id": primary_user_id,
            "user_name": primary_name,
            "confidence": primary_confidence,
            "liveness_score": mediapipe_result['liveness_score'],
            "antispoof_confidence": antispoof_result['confidence'],
            "is_live": True,
            "is_real": True,
            "annotated_image": annotated_image,
            "spoofing_attempt": False,
            "verification_method": "hybrid",
            "face_count": len(all_recognized),
            "all_recognized_faces": recognized_users
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect-live")
async def detect_live_face(
    image: str = Form(...),
    security_level: int = Form(3)
):
    """
    Real-time face detection and anti-spoofing check (no login attempt)

    Use this endpoint for live camera preview to show bounding boxes
    and real-time feedback before the user clicks "Login"

    Returns:
        - Annotated image with bounding boxes
        - Real-time status (REAL/FAKE/PHONE SCREEN)
        - Liveness indicators
        - Information about ALL detected faces
    """
    try:
        # Decode image
        frame = decode_base64_image(image)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Run hybrid detection
        result = hybrid_detector.detect_hybrid(frame)

        # Draw bounding boxes and labels
        annotated_frame = hybrid_detector.draw_results(frame, result)
        annotated_image = encode_image_to_base64(annotated_frame)

        antispoof_result = result['antispoof_result']
        mediapipe_result = result['mediapipe_result']

        # Get ALL faces detected
        all_faces = antispoof_result.get('all_faces', [])
        face_count = len(all_faces)

        # Determine status message based on primary face
        if not antispoof_result['face_detected']:
            status = "NO_FACE"
            message = "No face detected"
        elif antispoof_result.get('likely_phone', False):
            status = "PHONE_SCREEN"
            message = "⚠️ Phone screen detected - Show your real face"
        elif not antispoof_result['is_real']:
            status = "FAKE"
            message = "⚠️ Fake face detected - Show your real face"
        elif not result['verified']:
            status = "WAITING_LIVENESS"
            message = result['message']
        else:
            status = "REAL"
            if face_count > 1:
                message = f"✅ {face_count} faces detected - Ready to authenticate"
            else:
                message = "✅ Real face detected - Ready to authenticate"

        # Prepare face details for all detected faces
        faces_info = []
        for face_data in all_faces:
            # Convert numpy types to native Python types for JSON serialization
            x, y, w, h = face_data['bbox']
            faces_info.append({
                "bbox": [int(x), int(y), int(w), int(h)],
                "is_real": bool(face_data['is_real']),
                "confidence": float(face_data['confidence']),
                "label": str(face_data['label'])
            })

        return {
            "status": status,
            "message": message,
            "annotated_image": annotated_image,
            "is_real": antispoof_result['is_real'],
            "is_live": mediapipe_result['is_live'],
            "liveness_score": mediapipe_result['liveness_score'],
            "antispoof_confidence": antispoof_result['confidence'],
            "phone_detected": antispoof_result.get('likely_phone', False),
            "blink_count": mediapipe_result['blink_count'],
            "head_movements": mediapipe_result['head_movements'],
            "face_count": face_count,
            "all_faces": faces_info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    """Get user information by ID"""
    try:
        user = db.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert SQLite Row to dict
        user_dict = dict(user) if user else {}

        # Get profile image as base64 if exists
        profile_image = None
        if user_dict.get('image_path') and os.path.exists(user_dict['image_path']):
            img = cv2.imread(user_dict['image_path'])
            if img is not None:
                profile_image = encode_image_to_base64(img)

        return {
            "id": user_dict.get("id"),
            "name": user_dict.get("name"),
            "email": user_dict.get("email"),
            "created_at": user_dict.get("created_at"),
            "last_login": user_dict.get("last_login"),
            "image_path": user_dict.get("image_path"),
            "profile_image": profile_image
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/history")
async def get_login_history(user_id: int, limit: int = 20):
    """Get login history for a user"""
    try:
        history = db.get_login_history(user_id, limit=limit)
        # Convert SQLite Rows to dicts
        history_list = [dict(row) for row in history] if history else []
        return {"history": history_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/user/{user_id}")
async def delete_user(user_id: int):
    """Delete a user account"""
    try:
        success = db.delete_user(user_id)

        if success:
            return {"success": True, "message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN ENDPOINTS - API Key Management
# ============================================================================

class CreateAPIKeyRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class UpdateAPIKeyRequest(BaseModel):
    active: bool

@app.get("/api/admin/api-keys")
async def get_api_keys():
    """Get all API keys (admin only)"""
    try:
        api_keys = admin_manager.get_all_api_keys()
        return {"success": True, "api_keys": api_keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/api-keys")
async def create_api_key(request: CreateAPIKeyRequest):
    """Create a new API key (admin only)"""
    try:
        key_data = admin_manager.create_api_key(
            name=request.name,
            description=request.description
        )
        return {
            "success": True,
            "message": "API key created successfully",
            "key": key_data['key'],
            "name": key_data['name'],
            "created_at": key_data['created_at']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/api-keys/{key_prefix}")
async def delete_api_key(key_prefix: str):
    """Delete an API key by its prefix (admin only)"""
    try:
        success = admin_manager.delete_api_key(key_prefix)
        if success:
            return {"success": True, "message": "API key deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="API key not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/api-keys/{key_prefix}")
async def update_api_key_status(key_prefix: str, request: UpdateAPIKeyRequest):
    """Update API key status (admin only)"""
    try:
        success = admin_manager.update_api_key_status(key_prefix, request.active)
        if success:
            return {
                "success": True,
                "message": f"API key {'activated' if request.active else 'deactivated'} successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="API key not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/api-usage")
async def get_api_usage():
    """Get API usage statistics (admin only)"""
    try:
        usage_stats = admin_manager.get_api_usage_stats()
        return {"success": True, "usage": usage_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
