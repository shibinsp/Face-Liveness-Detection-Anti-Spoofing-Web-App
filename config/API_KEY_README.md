                                                                                                                                                                                                                                                                                                                                                                                                                                                                         # API Key Authentication System

## Overview

This Face Authentication System includes a secure API key authentication system with comprehensive request logging.

## Features

✅ **Secure Key Generation** - Cryptographically secure 64-character API keys  
✅ **Request Logging** - All API requests are logged with timestamps, IPs, and status  
✅ **Flexible Authentication** - Optional API key (logs requests without blocking)  
✅ **Structured Logs** - Both text and JSON format for easy analysis  
✅ **IP Tracking** - Captures real client IP even behind proxies  

---

## Setup Instructions

### 1. Generate API Key

Run the generator script:

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App/config
python3 generate_api_key.py
```

This will:
- Generate a secure 64-character API key
- Save it to `config/api_keys.json`
- Set proper file permissions (600 - owner only)

**Output Example:**
```
============================================================
🔐 API Key Generator - Face Authentication System
============================================================

✅ Generated API Key:

   8df1c77b3e8e1c22985ae957f3b54543d86f7d7112a...

   Length: 64 characters

✅ API Key saved to: /path/to/config/api_keys.json

⚠️  IMPORTANT SECURITY NOTES:
   • Keep this key SECRET - never commit to git
   • File permissions set to 600 (owner read/write only)
   • Use environment variables in production
   • Add 'api_keys.json' to .gitignore
```

---

## Using the API Key

### Option 1: Browser / JavaScript (Frontend)

Add the API key to request headers:

```javascript
// In your API config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
});
```

### Option 2: cURL (Command Line)

```bash
curl -X GET https://3netra.in/api/health \
  -H "X-API-Key: your-api-key-here"
```

### Option 3: Python (Requests)

```python
import requests

headers = {
    'X-API-Key': 'your-api-key-here'
}

response = requests.post(
    'https://3netra.in/api/login',
    headers=headers,
    files={'image': open('face.jpg', 'rb')}
)
```

### Option 4: Postman

1. Select your request
2. Go to **Headers** tab
3. Add new header:
   - **Key**: `X-API-Key`
   - **Value**: `your-api-key-here`

---

## Request Logging

All API requests are automatically logged to:

### 📄 Text Logs: `logs/api_requests.log`

```
2025-11-18 10:19:23 | INFO | IP: 103.88.103.11 | Method: POST | Path: /api/login | Status: SUCCESS | HTTP: 200 | Key: 8df1...543d | User-Agent: Mozilla/5.0...
```

### 📊 JSON Logs: `logs/api_requests.json`

```json
{
  "timestamp": "2025-11-18T10:19:23.123456",
  "ip": "103.88.103.11",
  "method": "POST",
  "path": "/api/login",
  "query_params": {},
  "status": "SUCCESS",
  "http_status": 200,
  "api_key_used": "8df1c77b...",
  "user_agent": "Mozilla/5.0...",
  "headers": {
    "content-type": "multipart/form-data",
    "origin": "https://3netra.in"
  }
}
```

---

## Log Status Codes

| Status | Description |
|--------|-------------|
| `SUCCESS` | Valid API key, request successful |
| `NO_KEY` | No API key provided (request still allowed) |
| `INVALID_KEY` | Invalid API key provided |
| `DENIED` | Access denied (if strict mode enabled) |
| `ERROR` | Server error (HTTP 500) |

---

## API Key Management

### View Current Keys

```bash
cat config/api_keys.json
```

### Add Multiple Keys

Edit `config/api_keys.json`:

```json
{
  "api_keys": [
    {
      "key": "primary-key-here",
      "name": "primary_key",
      "created_at": "2025-11-18T10:00:00",
      "active": true,
      "description": "Primary API key"
    },
    {
      "key": "secondary-key-here",
      "name": "mobile_app_key",
      "created_at": "2025-11-18T11:00:00",
      "active": true,
      "description": "Mobile app API key"
    }
  ]
}
```

### Revoke a Key

Set `"active": false`:

```json
{
  "key": "revoked-key",
  "active": false
}
```

---

## View Request Logs

### Real-time monitoring:

```bash
tail -f logs/api_requests.log
```

### Search for specific IP:

```bash
grep "103.88.103.11" logs/api_requests.log
```

### Count requests by status:

```bash
grep "SUCCESS" logs/api_requests.log | wc -l
grep "NO_KEY" logs/api_requests.log | wc -l
```

### Analyze JSON logs:

```bash
cat logs/api_requests.json | jq '.[] | select(.status == "SUCCESS")'
```

---

## Security Best Practices

### ✅ DO:
- Keep API keys secret and secure
- Use HTTPS for all API requests
- Rotate keys periodically
- Monitor logs for suspicious activity
- Use different keys for different clients
- Store keys in environment variables in production

### ❌ DON'T:
- Commit API keys to git
- Share keys in plain text
- Use the same key for all clients
- Expose keys in client-side JavaScript (for public apps)
- Store keys in browser localStorage

---

## Production Deployment

### Using Environment Variables:

Create `.env` file:

```bash
API_KEY=your-secure-api-key-here
```

Update `backend/api_auth.py` to read from environment:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
```

---

## Troubleshooting

### Issue: API key not working

**Check:**
1. Key is in `config/api_keys.json`
2. Key is marked as `"active": true`
3. Header name is exactly `X-API-Key` (case-sensitive)
4. Key is the full 64-character string

### Issue: Logs not appearing

**Check:**
1. `logs/` directory exists
2. Write permissions on `logs/` directory
3. Backend container has access to logs volume

### Issue: "Invalid API key" error

**Solution:**
```bash
# Regenerate key
cd config
python3 generate_api_key.py

# Restart backend
docker-compose restart backend
```

---

## API Endpoints

All endpoints support optional API key authentication:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/users/count` | GET | Get user count |
| `/api/register` | POST | Register new user |
| `/api/login` | POST | Login with face |
| `/api/detect-live` | POST | Live face detection |
| `/api/user/{id}` | GET | Get user info |
| `/api/user/{id}/history` | GET | Login history |
| `/api/user/{id}` | DELETE | Delete user |

---

## Support

For issues or questions:
- Check logs: `logs/api_requests.log`
- Review configuration: `config/api_keys.json`
- Contact system administrator

---

**Last Updated:** November 18, 2025  
**Version:** 1.0.0

