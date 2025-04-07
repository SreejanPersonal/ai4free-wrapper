"""
test_api_usage.py

Tests for API usage tracking and reporting.
"""

import os
import json
import requests
from dotenv import load_dotenv
import sys
sys.path.append('../..')  # Add parent directory to path for imports
from testing.utils.test_helpers import print_section_header, print_test_case

# Load environment variables from .env file
load_dotenv()

# Configuration variables
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")  # Default if not set
USAGE_ENDPOINT = f"{LOCAL_API_URL}/usage"

def test_api_usage(api_key):
    """
    Tests the usage API endpoint by sending a POST request with the given API key
    and prints out the returned usage details.
    
    Args:
        api_key (str): The API key to test usage for
        
    Returns:
        dict: The usage data returned by the API, or None if the request failed
    """
    print_section_header(f"TESTING API USAGE FOR KEY: {api_key}")
    
    payload = {
        "api_key": api_key
    }
    try:
        response = requests.post(USAGE_ENDPOINT, json=payload)
        response.raise_for_status()  # Raise an error on bad status

        # Parse and print the returned usage details
        data = response.json()
        print("Usage details received:")
        print(json.dumps(data, indent=2))
        return data

    except requests.exceptions.RequestException as e:
        print(f"API usage test failed: {e}")
        return None

def test_multiple_api_keys():
    """
    Tests the usage API endpoint with multiple API keys to verify
    that usage tracking works correctly for different users.
    """
    # List of API keys to test
    api_keys = [
        "ddc-EcAsBdRXr20WbkSwvcyAxeS6SvHLzVOBxGPsbM3Bu5U8RMQIqw",  # Replace with actual test keys
        # Add more API keys as needed
    ]
    
    print_section_header("TESTING MULTIPLE API KEYS")
    
    results = {}
    for key in api_keys:
        print_test_case(f"API Key: {key}")
        result = test_api_usage(key)
        results[key] = result
    
    return results

if __name__ == '__main__':
    # Test with a single API key
    test_api_key = "ddc-EcAsBdRXr20WbkSwvcyAxeS6SvHLzVOBxGPsbM3Bu5U8RMQIqw"  # Replace with your test API key
    test_api_usage(test_api_key)
    
    # Uncomment to test with multiple API keys
    # test_multiple_api_keys()
