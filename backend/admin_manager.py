"""
Admin Manager for API Key CRUD Operations
Provides functionality for creating, reading, updating, and deleting API keys
"""

import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

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

    def create_api_key(
        self,
        name: str,
        description: str = "",
        expiry_days: Optional[int] = None,
        rate_limit: Optional[int] = None
    ) -> Dict:
        """
        Create a new API key
        Args:
            name: Name of the API key
            description: Description of the API key
            expiry_days: Number of days until expiry (None for no expiry)
            rate_limit: Max requests per day (None for unlimited)
        Returns the complete key data including the actual key
        """
        # Generate secure API key
        api_key = secrets.token_hex(32)  # 64 character hex string

        # Calculate expiry date if specified
        expiry_date = None
        if expiry_days:
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()

        # Create key data
        key_data = {
            "key": api_key,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "description": description,
            "expiry_date": expiry_date,
            "rate_limit": rate_limit,  # requests per day
            "last_reset": datetime.now().isoformat(),  # for rate limit tracking
            "daily_usage": 0  # current day usage count
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

    def get_detailed_usage_logs(self, key_prefix: str, limit: int = 100) -> List[Dict]:
        """
        Get detailed usage logs for a specific API key
        Returns list of log entries for the specified key
        """
        if not self.json_log_file.exists():
            return []

        try:
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
        except Exception:
            return []

        # Filter logs for this key and limit results
        filtered_logs = []
        for log_entry in reversed(logs):  # Most recent first
            api_key_used = log_entry.get('api_key_used') or ''
            if api_key_used and api_key_used.startswith(key_prefix):
                filtered_logs.append(log_entry)
                if len(filtered_logs) >= limit:
                    break

        return filtered_logs

    def get_usage_timeline(self, days: int = 7) -> Dict:
        """
        Get usage statistics over time for visualization
        Returns daily usage counts for each API key
        """
        if not self.json_log_file.exists():
            return {}

        try:
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
        except Exception:
            return {}

        # Create timeline data
        timeline = defaultdict(lambda: defaultdict(int))

        for log_entry in logs:
            timestamp = log_entry.get('timestamp')
            api_key_used = log_entry.get('api_key_used')

            if timestamp and api_key_used:
                try:
                    # Parse date from ISO format
                    log_date = datetime.fromisoformat(timestamp).date()
                    key_prefix = api_key_used.split('...')[0]

                    # Count requests per day per key
                    date_str = log_date.isoformat()
                    timeline[date_str][key_prefix] += 1
                except Exception:
                    continue

        return dict(timeline)

    def check_api_key_validity(self, key: str) -> Dict:
        """
        Check if an API key is valid (not expired, not rate limited)
        Returns dict with validity status and reasons
        """
        data = self._load_api_keys_data()

        for key_info in data.get('api_keys', []):
            if key_info.get('key') == key:
                result = {
                    "valid": True,
                    "active": key_info.get('active', True),
                    "expired": False,
                    "rate_limited": False,
                    "remaining_requests": None
                }

                # Check if active
                if not key_info.get('active', True):
                    result['valid'] = False
                    return result

                # Check expiry
                expiry_date = key_info.get('expiry_date')
                if expiry_date:
                    try:
                        expiry = datetime.fromisoformat(expiry_date)
                        if datetime.now() > expiry:
                            result['valid'] = False
                            result['expired'] = True
                            return result
                    except Exception:
                        pass

                # Check rate limit
                rate_limit = key_info.get('rate_limit')
                if rate_limit:
                    # Reset counter if it's a new day
                    last_reset = key_info.get('last_reset')
                    daily_usage = key_info.get('daily_usage', 0)

                    if last_reset:
                        try:
                            last_reset_date = datetime.fromisoformat(last_reset).date()
                            today = datetime.now().date()

                            if last_reset_date < today:
                                # Reset counter for new day
                                key_info['daily_usage'] = 0
                                key_info['last_reset'] = datetime.now().isoformat()
                                daily_usage = 0
                                self._save_api_keys_data(data)
                        except Exception:
                            pass

                    # Check if rate limit exceeded
                    if daily_usage >= rate_limit:
                        result['valid'] = False
                        result['rate_limited'] = True
                        result['remaining_requests'] = 0
                    else:
                        result['remaining_requests'] = rate_limit - daily_usage

                return result

        # Key not found
        return {"valid": False, "active": False, "expired": False, "rate_limited": False}

    def increment_usage(self, key: str):
        """Increment daily usage counter for rate limiting"""
        data = self._load_api_keys_data()

        for key_info in data.get('api_keys', []):
            if key_info.get('key') == key:
                key_info['daily_usage'] = key_info.get('daily_usage', 0) + 1
                self._save_api_keys_data(data)
                break

    def verify_admin_password(self, password: str) -> bool:
        """
        Verify admin password
        In production, this should use environment variables and hashing
        """
        # TODO: Move to environment variable and use proper hashing
        return password == "srini1205"


# Initialize admin manager
admin_manager = AdminManager()
