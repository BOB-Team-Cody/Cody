#!/usr/bin/env python3
"""
Test client for Code Weaver API
"""

import requests
import json
import os
from pathlib import Path


def test_api():
    """Test the Code Weaver API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Code Weaver API...")
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test analyze endpoint with our sample project
        print("\n3. Testing analyze endpoint...")
        sample_project_path = str(Path("sample_project").absolute())
        
        analyze_payload = {
            "path": sample_project_path
        }
        
        response = requests.post(
            f"{base_url}/analyze",
            json=analyze_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Nodes: {result.get('nodes_count')}")
            print(f"Edges: {result.get('edges_count')}")
        else:
            print(f"Error: {response.text}")
        
        # Test graph-data endpoint (will fail if Neo4j not connected)
        print("\n4. Testing graph-data endpoint...")
        response = requests.get(f"{base_url}/graph-data")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Nodes in graph: {len(result.get('nodes', []))}")
            print(f"Links in graph: {len(result.get('links', []))}")
        else:
            print(f"Error: {response.text}")
        
        # Test statistics endpoint
        print("\n5. Testing statistics endpoint...")
        response = requests.get(f"{base_url}/statistics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Statistics: {result}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error testing API: {e}")


if __name__ == "__main__":
    test_api()
