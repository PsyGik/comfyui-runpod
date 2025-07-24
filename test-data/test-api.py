#!/usr/bin/env python3
"""
Quick API testing script for the File Manager
"""

import requests
import json
import time

BASE_URL = "http://localhost:8189"

def test_api():
    print("🧪 Testing File Manager API")
    print("=" * 40)
    
    # Test 1: Get folders
    print("\n📁 Testing folder endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/folders")
        if response.status_code == 200:
            folders = response.json()
            print(f"✅ Found {len(folders)} folders:")
            for folder in folders[:3]:  # Show first 3
                print(f"   - {folder['name']}: {folder['path']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Get files in root
    print("\n📄 Testing files endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/files/")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print(f"✅ Found {len(files)} items in root:")
            for file in files[:5]:  # Show first 5
                print(f"   - {file['name']} ({file['type']})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test download endpoint (without actually downloading)
    print("\n⬇️ Testing download endpoint...")
    try:
        # Test with invalid data to see error handling
        response = requests.post(
            f"{BASE_URL}/api/download",
            headers={'Content-Type': 'application/json'},
            json={"url": "", "folder": ""}
        )
        if response.status_code == 400:
            print("✅ Download validation working correctly")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get downloads
    print("\n📊 Testing downloads endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/downloads")
        if response.status_code == 200:
            downloads = response.json()
            print(f"✅ Downloads endpoint working (found {len(downloads)} downloads)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 API testing complete!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_api()
