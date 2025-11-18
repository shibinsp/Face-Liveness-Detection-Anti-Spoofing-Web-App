#!/usr/bin/env python3
"""
API Request Log Viewer
Analyze and display API request logs with statistics
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

def load_json_logs(log_file):
    """Load logs from JSON file"""
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        return []
    
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
            return logs if isinstance(logs, list) else []
    except json.JSONDecodeError:
        print(f"❌ Error reading log file")
        return []

def display_statistics(logs):
    """Display log statistics"""
    if not logs:
        print("📊 No logs available")
        return
    
    print("\n" + "="*70)
    print("📊 API REQUEST STATISTICS")
    print("="*70)
    
    # Total requests
    print(f"\n📈 Total Requests: {len(logs)}")
    
    # Status breakdown
    statuses = Counter(log['status'] for log in logs)
    print(f"\n📋 Status Breakdown:")
    for status, count in statuses.most_common():
        percentage = (count / len(logs)) * 100
        print(f"   • {status:15}: {count:5} ({percentage:5.1f}%)")
    
    # Method breakdown
    methods = Counter(log['method'] for log in logs)
    print(f"\n🔄 HTTP Methods:")
    for method, count in methods.most_common():
        print(f"   • {method:6}: {count}")
    
    # Top endpoints
    paths = Counter(log['path'] for log in logs)
    print(f"\n🎯 Top Endpoints:")
    for path, count in paths.most_common(10):
        print(f"   • {count:4} requests - {path}")
    
    # Top IPs
    ips = Counter(log['ip'] for log in logs)
    print(f"\n🌐 Top IP Addresses:")
    for ip, count in ips.most_common(10):
        print(f"   • {ip:20} - {count:4} requests")
    
    # API Key usage
    keys_used = sum(1 for log in logs if log.get('api_key_used'))
    print(f"\n🔑 API Key Usage:")
    print(f"   • With API Key: {keys_used} ({(keys_used/len(logs)*100):.1f}%)")
    print(f"   • Without Key:  {len(logs)-keys_used} ({((len(logs)-keys_used)/len(logs)*100):.1f}%)")
    
    # Time range
    if logs:
        timestamps = [datetime.fromisoformat(log['timestamp']) for log in logs]
        earliest = min(timestamps)
        latest = max(timestamps)
        print(f"\n⏰ Time Range:")
        print(f"   • First Request: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   • Last Request:  {latest.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   • Duration:      {latest - earliest}")

def display_recent_logs(logs, count=20):
    """Display recent log entries"""
    print("\n" + "="*70)
    print(f"📝 RECENT API REQUESTS (Last {count})")
    print("="*70)
    
    for log in logs[-count:]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        status_icon = {
            'SUCCESS': '✅',
            'NO_KEY': '⚠️',
            'INVALID_KEY': '❌',
            'ERROR': '🔥'
        }.get(log['status'], '❓')
        
        print(f"\n{status_icon} {timestamp}")
        print(f"   IP: {log['ip']:20} | {log['method']:6} {log['path']}")
        print(f"   Status: {log['status']:15} | HTTP: {log['http_status']}")
        if log.get('api_key_used'):
            print(f"   API Key: {log['api_key_used']}")

def search_logs(logs, search_term):
    """Search logs for specific term"""
    results = []
    for log in logs:
        log_str = json.dumps(log).lower()
        if search_term.lower() in log_str:
            results.append(log)
    
    print(f"\n🔍 Search Results for '{search_term}': {len(results)} matches")
    display_recent_logs(results, count=min(10, len(results)))

def main():
    """Main function"""
    log_file = Path(__file__).parent.parent / 'logs' / 'api_requests.json'
    
    print("\n" + "="*70)
    print("🔐 Face Authentication API - Request Log Viewer")
    print("="*70)
    
    logs = load_json_logs(log_file)
    
    if not logs:
        print("\n⚠️  No logs found. Make some API requests first.")
        return
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'stats':
            display_statistics(logs)
        elif command == 'recent':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            display_recent_logs(logs, count)
        elif command == 'search':
            if len(sys.argv) < 3:
                print("❌ Usage: python view_logs.py search <term>")
            else:
                search_logs(logs, sys.argv[2])
        else:
            print(f"❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python view_logs.py stats          - Show statistics")
            print("  python view_logs.py recent [N]     - Show N recent logs")
            print("  python view_logs.py search <term>  - Search logs")
    else:
        # Default: show stats and recent logs
        display_statistics(logs)
        display_recent_logs(logs, count=10)
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

