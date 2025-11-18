"""
Admin Manager for API Key CRUD Operations
Provides functionality for creating, reading, updating, and deleting API keys
"""

import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class AdminManager:
    """Manage API keys through admin interface"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.api_keys_file = self.config_dir / 'api_keys.json'
        self.logs_dir = Path(__file__).parent.parent / 'logs'
        self.json_log_file = self.logs_dir / 'api_requests.json'

        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def _load_api_keys_data(self) -> Dict:
        """Load complete API keys data from file"""
        if not self.api_keys_file.exists():
            return {"api_keys": [], "generated_at": datetime.now().isoformat()}

        try:
            with open(self.api_keys_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading API keys: {e}")
            return {"api_keys": [], "generated_at": datetime.now().isoformat()}

    def _save_api_keys_data(self, data: Dict):
        """Save API keys data to file"""
        try:
            with open(self.api_keys_file, 'w') as f:
                json.dump(data, f, indent=4)

            # Set file permissions to read-only for owner
            import os
            os.chmod(self.api_keys_file, 0o600)
        except Exception as e:
            print(f"Error saving API keys: {e}")
            raise

    def get_all_api_keys(self) -> List[Dict]:
        """Get all API keys with metadata (excluding full key for security)"""
        data = self._load_api_keys_data()

        # Return keys with masked values
        masked_keys = []
        for key_info in data.get('api_keys', []):
            masked_key = key_info.copy()
            # Keep the key for identification but it will be masked on frontend
            masked_keys.append(masked_key)

        return masked_keys

    def create_api_key(self, name: str, description: str = "") -> Dict:
        """
        Create a new API key
        Returns the complete key data including the actual key
        """
        # Generate secure API key
        api_key = secrets.token_hex(32)  # 64 character hex string

        # Create key data
        key_data = {
            "key": api_key,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "description": description
        }

        # Load existing data
        data = self._load_api_keys_data()

        # Add new key
        data['api_keys'].append(key_data)
        data['generated_at'] = datetime.now().isoformat()

        # Save
        self._save_api_keys_data(data)

        return key_data

    def delete_api_key(self, key_prefix: str) -> bool:
        """
        Delete an API key by its prefix (first 8 characters)
        Returns True if deleted, False if not found
        """
        data = self._load_api_keys_data()
        api_keys = data.get('api_keys', [])

        # Find and remove the key
        original_length = len(api_keys)
        data['api_keys'] = [
            k for k in api_keys
            if not k.get('key', '').startswith(key_prefix)
        ]

        # Check if anything was removed
        if len(data['api_keys']) < original_length:
            self._save_api_keys_data(data)
            return True

        return False

    def update_api_key_status(self, key_prefix: str, active: bool) -> bool:
        """
        Update API key active status
        Returns True if updated, False if not found
        """
        data = self._load_api_keys_data()
        api_keys = data.get('api_keys', [])

        # Find and update the key
        updated = False
        for key_info in api_keys:
            if key_info.get('key', '').startswith(key_prefix):
                key_info['active'] = active
                updated = True
                break

        if updated:
            self._save_api_keys_data(data)
            return True

        return False

    def get_api_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for each API key from logs
        Returns dict with key_prefix -> request_count
        """
        if not self.json_log_file.exists():
            return {}

        try:
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
        except Exception:
            return {}

        # Count requests per API key
        usage_stats = {}

        for log_entry in logs:
            api_key_used = log_entry.get('api_key_used')
            if api_key_used:
                # Extract key prefix (first part before "...")
                key_prefix = api_key_used.split('...')[0]
                usage_stats[key_prefix] = usage_stats.get(key_prefix, 0) + 1

        return usage_stats

    def verify_admin_password(self, password: str) -> bool:
        """
        Verify admin password
        In production, this should use environment variables and hashing
        """
        # TODO: Move to environment variable and use proper hashing
        return password == "srini1205"


# Initialize admin manager
admin_manager = AdminManager()
