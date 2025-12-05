"""
Quick API Test Script
Run: python TEST_API.py (while API is running)
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("SMART EXPENSE NER API - TEST SCRIPT")
print("=" * 60)

# Test 1: Health Check
print("\n[TEST 1] Health Check")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    print("✓ PASSED" if response.status_code == 200 else "✗ FAILED")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 2: Root Endpoint
print("\n[TEST 2] Root Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    print("✓ PASSED" if response.status_code == 200 else "✗ FAILED")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 3: Parse Endpoint
print("\n[TEST 3] Parse Single Text")
print("-" * 60)
try:
    payload = {"text": "grab food 60rb"}
    response = requests.post(
        f"{BASE_URL}/api/parse",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Input: {payload['text']}")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    print("✓ PASSED" if response.status_code == 200 else "✗ FAILED")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 4: Batch Parse
print("\n[TEST 4] Batch Parse")
print("-" * 60)
try:
    payload = {
        "texts": [
            "grab food 60rb",
            "beli pulsa 25k",
            "parkir 10k"
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/batch-parse",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Input: {len(payload['texts'])} texts")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    print("✓ PASSED" if response.status_code == 200 else "✗ FAILED")
except Exception as e:
    print(f"✗ FAILED: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)