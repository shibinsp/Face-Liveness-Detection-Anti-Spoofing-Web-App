#!/usr/bin/env python3
"""
Display API Key for Copy-Paste
Shows the active API key with usage examples
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    api_keys_file = Path(__file__).parent / 'api_keys.json'
    
    if not api_keys_file.exists():
        print("❌ API key file not found!")
        print("   Run: python generate_api_key.py")
        return
    
    try:
        with open(api_keys_file, 'r') as f:
            data = json.load(f)
        
        active_keys = [k for k in data.get('api_keys', []) if k.get('active', False)]
        
        if not active_keys:
            print("❌ No active API keys found!")
            return
        
        print("\n" + "="*70)
        print("🔐 API KEY INFORMATION - Face Authentication System")
        print("="*70)
        
        for i, key_info in enumerate(active_keys, 1):
            api_key = key_info['key']
            name = key_info.get('name', 'unnamed')
            created = key_info.get('created_at', 'unknown')
            description = key_info.get('description', 'No description')
            
            print(f"\n📋 Key #{i}: {name}")
            print(f"   Description: {description}")
            print(f"   Created: {created}")
            print(f"\n   🔑 API Key (copy this):")
            print(f"   ┌{'─'*66}┐")
            print(f"   │ {api_key} │")
            print(f"   └{'─'*66}┘")
        
        # Usage examples
        primary_key = active_keys[0]['key']
        
        print(f"\n" + "="*70)
        print("📖 USAGE EXAMPLES")
        print("="*70)
        
        print(f"\n1️⃣  cURL:")
        print(f"   curl -H 'X-API-Key: {primary_key}' \\")
        print(f"        https://3netra.in/api/health")
        
        print(f"\n2️⃣  Python (requests):")
        print(f"   headers = {{'X-API-Key': '{primary_key}'}}")
        print(f"   response = requests.get('https://3netra.in/api/health', headers=headers)")
        
        print(f"\n3️⃣  JavaScript (axios):")
        print(f"   const headers = {{ 'X-API-Key': '{primary_key}' }};")
        print(f"   axios.get('/api/health', {{ headers }});")
        
        print(f"\n4️⃣  Postman:")
        print(f"   • Headers tab")
        print(f"   • Key: X-API-Key")
        print(f"   • Value: {primary_key}")
        
        print(f"\n" + "="*70)
        print("⚠️  SECURITY REMINDERS")
        print("="*70)
        print("   • NEVER commit this key to git")
        print("   • NEVER share in public channels")
        print("   • Use HTTPS only (https://3netra.in)")
        print("   • Rotate keys periodically")
        print("   • Monitor logs for unauthorized access")
        print(f"\n   📊 View logs: python view_logs.py stats")
        print(f"   🔍 Search logs: python view_logs.py search <ip_or_path>")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"❌ Error reading API key file: {e}")

if __name__ == "__main__":
    main()

