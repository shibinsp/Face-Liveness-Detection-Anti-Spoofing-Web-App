#!/usr/bin/env python3
"""
API Key Generator for Face Authentication System
Generates a secure API key and stores it safely
"""

import secrets
import json
from datetime import datetime
import os

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_hex(length)

def save_api_key(api_key, filename='api_keys.json'):
    """Save API key to a JSON file with metadata"""
    config_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(config_dir, filename)
    
    # Create API key data with metadata
    api_key_data = {
        "api_keys": [
            {
                "key": api_key,
                "name": "primary_key",
                "created_at": datetime.now().isoformat(),
                "active": True,
                "description": "Primary API key for Face Authentication System"
            }
        ],
        "generated_at": datetime.now().isoformat()
    }
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(api_key_data, f, indent=4)
    
    # Set file permissions to read-only for owner
    os.chmod(filepath, 0o600)
    
    return filepath

def main():
    print("=" * 60)
    print("🔐 API Key Generator - Face Authentication System")
    print("=" * 60)
    
    # Generate API key
    api_key = generate_api_key(32)
    
    print(f"\n✅ Generated API Key:\n")
    print(f"   {api_key}")
    print(f"\n   Length: {len(api_key)} characters")
    
    # Save to file
    filepath = save_api_key(api_key)
    
    print(f"\n✅ API Key saved to: {filepath}")
    print(f"\n⚠️  IMPORTANT SECURITY NOTES:")
    print(f"   • Keep this key SECRET - never commit to git")
    print(f"   • File permissions set to 600 (owner read/write only)")
    print(f"   • Use environment variables in production")
    print(f"   • Add 'api_keys.json' to .gitignore")
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    
    return api_key

if __name__ == "__main__":
    main()

