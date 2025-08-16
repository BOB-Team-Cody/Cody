#!/usr/bin/env python3
"""
Quick test for the API server
"""

import time
import subprocess
import sys

# Test if server is running
try:
    import requests
    response = requests.get("http://127.0.0.1:8000/", timeout=5)
    print(f"✓ Server is running! Status: {response.status_code}")
    print(f"✓ Response: {response.json()}")
    
    # Test health endpoint
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    print(f"✓ Health check: {response.json()}")
    
except requests.exceptions.ConnectionError:
    print("✗ Server not running or not accessible")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nDone.")
