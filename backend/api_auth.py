"""
API Key Authentication and Request Logging
Secure API access with comprehensive request logging
"""

import json
import os
from datetime import datetime
from typing import Optional
from fastapi import Header, HTTPException, Request
from pathlib import Path
import logging

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Setup logger for API requests
api_logger = logging.getLogger('api_requests')
api_logger.setLevel(logging.INFO)

# File handler for API request logs
log_file = log_dir / 'api_requests.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
api_logger.addHandler(file_handler)


class APIKeyManager:
    """Manage API keys and request logging"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.api_keys_file = self.config_dir / 'api_keys.json'
        self.valid_keys = self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from configuration file"""
        if not self.api_keys_file.exists():
            # Return empty list if no keys file exists
            return []
        
        try:
            with open(self.api_keys_file, 'r') as f:
                data = json.load(f)
                # Extract active keys only
                return [
                    key_info['key'] 
                    for key_info in data.get('api_keys', []) 
                    if key_info.get('active', False)
                ]
        except Exception as e:
            api_logger.error(f"Failed to load API keys: {e}")
            return []
    
    def verify_api_key(self, api_key: Optional[str]) -> bool:
        """Verify if the provided API key is valid"""
        if not api_key:
            return False
        return api_key in self.valid_keys
    
    def log_request(
        self, 
        request: Request, 
        api_key: Optional[str],
        status: str,
        user_agent: Optional[str] = None,
        response_status: int = 200
    ):
        """Log API request with detailed information"""
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get forwarded IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Get real IP from Nginx
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        # Mask API key for logging (show only first/last 4 chars)
        masked_key = "None"
        if api_key:
            if len(api_key) > 8:
                masked_key = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                masked_key = "****"
        
        # Build log message
        log_message = (
            f"IP: {client_ip:15} | "
            f"Method: {request.method:6} | "
            f"Path: {request.url.path:40} | "
            f"Status: {status:10} | "
            f"HTTP: {response_status} | "
            f"Key: {masked_key} | "
            f"User-Agent: {user_agent or 'unknown'}"
        )
        
        # Log based on status
        if status == "SUCCESS":
            api_logger.info(log_message)
        elif status == "DENIED":
            api_logger.warning(log_message)
        else:
            api_logger.error(log_message)
        
        # Also write to JSON log for structured data
        self._write_json_log(request, client_ip, api_key, status, user_agent, response_status)
    
    def _write_json_log(
        self,
        request: Request,
        client_ip: str,
        api_key: Optional[str],
        status: str,
        user_agent: Optional[str],
        response_status: int
    ):
        """Write structured JSON log entry"""
        json_log_file = Path(__file__).parent.parent / 'logs' / 'api_requests.json'
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "status": status,
            "http_status": response_status,
            "api_key_used": api_key[:8] + "..." if api_key and len(api_key) > 8 else None,
            "user_agent": user_agent,
            "headers": {
                "content-type": request.headers.get("content-type"),
                "origin": request.headers.get("origin"),
            }
        }
        
        # Append to JSON log file
        try:
            # Read existing logs
            if json_log_file.exists():
                with open(json_log_file, 'r') as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []
            
            # Append new log
            logs.append(log_entry)
            
            # Keep only last 10000 logs
            if len(logs) > 10000:
                logs = logs[-10000:]
            
            # Write back
            with open(json_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            api_logger.error(f"Failed to write JSON log: {e}")


# Initialize API key manager
api_key_manager = APIKeyManager()


async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """
    Dependency to verify API key from request header
    
    Usage in FastAPI endpoint:
        @app.get("/api/protected", dependencies=[Depends(verify_api_key)])
        async def protected_endpoint():
            return {"message": "Access granted"}
    """
    user_agent = request.headers.get("user-agent")
    
    # Check if API key is valid
    if not api_key_manager.verify_api_key(x_api_key):
        # Log failed attempt
        api_key_manager.log_request(
            request=request,
            api_key=x_api_key,
            status="DENIED",
            user_agent=user_agent,
            response_status=401
        )
        
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include 'X-API-Key' header."
        )
    
    # Log successful access
    api_key_manager.log_request(
        request=request,
        api_key=x_api_key,
        status="SUCCESS",
        user_agent=user_agent,
        response_status=200
    )
    
    return True


async def optional_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """
    Optional API key verification - logs all requests
    Does not block access, just logs
    """
    user_agent = request.headers.get("user-agent")
    
    # Check if key is provided and valid
    if x_api_key:
        is_valid = api_key_manager.verify_api_key(x_api_key)
        status = "SUCCESS" if is_valid else "INVALID_KEY"
    else:
        status = "NO_KEY"
    
    # Log the request
    api_key_manager.log_request(
        request=request,
        api_key=x_api_key,
        status=status,
        user_agent=user_agent,
        response_status=200
    )
    
    return True

