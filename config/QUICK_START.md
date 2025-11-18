# 🚀 API Key System - Quick Start Guide

## ✅ System Status: ACTIVE

Your Face Authentication System now has a secure API key authentication and logging system installed!

---

## 📁 Files Created

```
config/
  ├── generate_api_key.py    # Generate new API keys
  ├── show_api_key.py         # View current API key
  ├── view_logs.py            # Analyze request logs
  ├── api_keys.json           # API keys storage (NEVER commit!)
  ├── API_KEY_README.md       # Full documentation
  └── QUICK_START.md          # This file

backend/
  └── api_auth.py             # Authentication middleware

logs/
  ├── api_requests.log        # Text format logs
  └── api_requests.json       # JSON format logs
```

---

## 🔑 Your API Key

Run this command to see your API key:

```bash
cd /root/Face-Liveness-Detection-Anti-Spoofing-Web-App/config
python3 show_api_key.py
```

---

## 📊 View Request Logs

### Show Statistics
```bash
python3 view_logs.py stats
```

### Show Recent Requests
```bash
python3 view_logs.py recent 20
```

### Search Logs
```bash
python3 view_logs.py search "103.88"     # Search by IP
python3 view_logs.py search "/api/login" # Search by endpoint
```

### Real-time Monitoring
```bash
tail -f /root/Face-Liveness-Detection-Anti-Spoofing-Web-App/logs/api_requests.log
```

---

## 🧪 Test API Key

```bash
# Without API key (works but logs as NO_KEY)
curl https://3netra.in/api/health

# With API key (logs as SUCCESS)
curl -H "X-API-Key: YOUR_KEY_HERE" https://3netra.in/api/health
```

---

## 🔐 How It Works

### Request Flow

1. **Client makes request** → API endpoint
2. **Middleware checks** for `X-API-Key` header
3. **Logs request** with:
   - Timestamp
   - IP address (real IP, even behind proxy)
   - HTTP method
   - Endpoint path
   - API key status (SUCCESS/NO_KEY/INVALID_KEY)
   - HTTP response code
   - User agent
4. **Returns response** (API key is optional, doesn't block)

### Log Statuses

| Status | Meaning |
|--------|---------|
| **SUCCESS** | Valid API key provided |
| **NO_KEY** | No API key provided (request still allowed) |
| **INVALID_KEY** | Invalid API key provided |
| **ERROR** | Server error occurred |

---

## 🎯 Common Commands

### Generate New API Key
```bash
cd config && python3 generate_api_key.py
```

### View Current Key
```bash
cd config && python3 show_api_key.py
```

### Check Recent Activity
```bash
cd config && python3 view_logs.py recent 10
```

### View Full Statistics
```bash
cd config && python3 view_logs.py stats
```

### Monitor Live
```bash
tail -f ../logs/api_requests.log
```

---

## 🌐 Using in Your Application

### Frontend (JavaScript/React)

```javascript
// Add to your API config
import axios from 'axios';

const API_KEY = 'fef150353dc16f5067e49bf2ab31653b5bfecb0d34914bf1e9d1fcfbdcfc6d16';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'X-API-Key': API_KEY
  }
});

// All requests will include the API key
api.get('/health');
api.post('/login', formData);
```

### Backend (Python)

```python
import requests

API_KEY = 'fef150353dc16f5067e49bf2ab31653b5bfecb0d34914bf1e9d1fcfbdcfc6d16'

headers = {
    'X-API-Key': API_KEY
}

response = requests.post(
    'https://3netra.in/api/login',
    headers=headers,
    files={'image': open('face.jpg', 'rb')}
)
```

---

## ⚠️ Security Notes

### ✅ DO:
- Keep API key in environment variables
- Use HTTPS only
- Monitor logs for unusual activity
- Rotate keys periodically
- Use different keys for different clients

### ❌ DON'T:
- Commit API keys to git (already in .gitignore)
- Share keys publicly
- Use HTTP
- Store in client-side code (for public apps)
- Use same key for all environments

---

## 📈 Log Analysis Examples

### Find all failed requests
```bash
grep "INVALID_KEY" ../logs/api_requests.log
```

### Count requests by IP
```bash
grep "IP:" ../logs/api_requests.log | cut -d'|' -f2 | sort | uniq -c | sort -rn
```

### Find login attempts
```bash
grep "/api/login" ../logs/api_requests.log
```

### View only successful authenticated requests
```bash
grep "SUCCESS" ../logs/api_requests.log
```

---

## 🔄 Adding More API Keys

1. Edit `config/api_keys.json`
2. Add new key entry:

```json
{
  "api_keys": [
    {
      "key": "existing-key",
      "name": "primary_key",
      "active": true
    },
    {
      "key": "new-key-here",
      "name": "mobile_app",
      "active": true,
      "description": "Mobile app API key"
    }
  ]
}
```

3. Restart backend: `docker-compose restart backend`

---

## 🛠️ Troubleshooting

### API key not working
1. Check key is in `config/api_keys.json`
2. Verify `"active": true`
3. Restart backend: `docker-compose restart backend`
4. Check logs: `docker-compose logs backend`

### Logs not appearing
1. Check `logs/` directory exists
2. Verify write permissions
3. Check backend logs for errors

### Need to regenerate key
```bash
cd config
python3 generate_api_key.py
docker-compose restart backend
```

---

## 📚 Full Documentation

For complete documentation, see:
- `config/API_KEY_README.md` - Full API key documentation
- `docker-compose logs backend` - Backend logs
- `logs/api_requests.log` - Request logs

---

**Last Updated:** November 18, 2025  
**Version:** 1.0.0  
**Status:** ✅ Active & Monitoring
