"""
test_api_endpoints.py

Tests for API endpoints including API key generation and authentication.
"""

import requests
import os
import json
import time
from dotenv import load_dotenv
import sys
sys.path.append('../..')  # Add parent directory to path for imports
from testing.utils.test_helpers import print_section_header, print_test_case

# Load environment variables
load_dotenv()

# Default to localhost if not set
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")
SYSTEM_SECRET = os.getenv("SYSTEM_SECRET")
# Sample partial API key for testing - should match a substring of an existing API key in Supabase
VALID_PARTIAL_API_KEY = "ddc-beta-rh88uzo5dq-xxx"
# Invalid partial API key for testing
INVALID_PARTIAL_API_KEY = "invalid-key-prefix"

def generate_api_key(user_id, telegram_user_link, email=None, first_name="Test", last_name="User", username="test_user", partial_api_key=None, id=None):
    """
    Generates a new API key for testing.
    
    Args:
        user_id (str): The user ID
        telegram_user_link (str): The Telegram user link
        email (str, optional): The email for Firebase/Supabase validation
        first_name (str, optional): The user's first name
        last_name (str, optional): The user's last name
        username (str, optional): The user's username
        partial_api_key (str, optional): The partial API key for authentication
        id (str, optional): The Supabase user ID. If provided, email and partial_api_key are not required.
        
    Returns:
        tuple: (api_key, status_code, response_json) - The generated API key, status code, and full response
    """
    try:
        # Prepare request data
        request_data = {
            'secret': SYSTEM_SECRET,
            'user_id': user_id,
            'telegram_user_link': telegram_user_link,
            'first_name': first_name,
            'last_name': last_name,
            'username': username
        }
        
        # Add email if provided
        if email:
            request_data['email'] = email
            
        # Add partial API key if provided
        if partial_api_key:
            request_data['partial_api_key'] = partial_api_key
            
        # Add ID if provided
        if id:
            request_data['id'] = id
            
        print(request_data)
        # Make the API request
        response = requests.post(
            f"{LOCAL_API_URL}/v1/api-keys",
            json=request_data
        )
        
        # Print the full response for debugging
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Parse the response JSON if possible
        response_json = None
        try:
            response_json = response.json()
        except:
            response_json = {"error": "Failed to parse JSON response"}
        
        # Return the tuple (api_key, status_code, response_json)
        api_key = None
        if response.status_code in (200, 201):
            api_key = response_json.get('api_key')
            if api_key:
                print(f"API Key: {api_key}")
                
        return (api_key, response.status_code, response_json)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {e}"
        print(error_msg)
        return (None, 500, {"error": error_msg})

def test_partial_api_key_authentication():
    """
    Test the partial API key authentication feature with three scenarios:
    1. Missing partial API key
    2. Invalid partial API key
    3. Valid partial API key
    """
    test_email = "friday.era.industries@gmail.com"  # Use a valid email that exists in Firebase
    
    print_section_header("TESTING PARTIAL API KEY AUTHENTICATION")
    
    # Test Case 1: Missing partial API key
    print_test_case("Missing partial API key")
    api_key, status_code, response = generate_api_key(
        user_id="test_user_126",
        telegram_user_link="tg://user?id=1234567890",
        email=test_email
    )
    print(f"Status Code: {status_code}")
    print(f"Expected: 400 Bad Request (Missing required field)")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test Case 2: Invalid partial API key
    print_test_case("Invalid partial API key")
    api_key, status_code, response = generate_api_key(
        user_id="test_user_127",
        telegram_user_link="tg://user?id=1234567890",
        email=test_email,
        partial_api_key=INVALID_PARTIAL_API_KEY
    )
    print(f"Status Code: {status_code}")
    print(f"Expected: 401 Unauthorized (Invalid partial API key)")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test Case 3: Valid partial API key
    print_test_case("Valid partial API key")
    api_key, status_code, response = generate_api_key(
        user_id="test_user_128",
        telegram_user_link="tg://user?id=1234567890",
        email=test_email,
        partial_api_key=VALID_PARTIAL_API_KEY
    )
    print(f"Status Code: {status_code}")
    print(f"Expected: 200 or 201 (Success)")
    print(f"Response: {json.dumps(response, indent=2)}")

def test_id_authentication():
    """
    Test the ID authentication feature with two scenarios:
    1. Valid ID (existing in Supabase)
    2. Invalid ID (not existing in Supabase)
    """
    test_email = "friday.era.industries@gmail.com"  # Use a valid email that exists in Firebase
    
    print_section_header("TESTING ID AUTHENTICATION")
    
    # Test Case 1: Valid ID
    print_test_case("Valid ID")
    # Replace with a valid ID from your Supabase database
    valid_id = "wHxT4AoaP3OuDo77N9nIdJ3QFw33"  # Example ID, replace with an actual ID from your Supabase database
    api_key, status_code, response = generate_api_key(
        user_id="test_user_129",
        telegram_user_link="tg://user?id=1234567890",
        email=test_email,
        id=valid_id
    )
    print(f"Status Code: {status_code}")
    print(f"Expected: 200 or 201 (Success)")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test Case 2: Invalid ID
    print_test_case("Invalid ID")
    invalid_id = "999999"  # An ID that doesn't exist in your Supabase database
    api_key, status_code, response = generate_api_key(
        user_id="test_user_130",
        telegram_user_link="tg://user?id=1234567890",
        email=test_email,
        id=invalid_id
    )
    print(f"Status Code: {status_code}")
    print(f"Expected: 404 Not Found (ID not found in Supabase)")
    print(f"Response: {json.dumps(response, indent=2)}")

if __name__ == '__main__':
    # Test partial API key authentication
    test_partial_api_key_authentication()
    
    # Test ID authentication
    test_id_authentication()
