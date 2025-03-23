# testing/API_Endpoint_Testing.py
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Default to localhost if not set
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:5000")
SYSTEM_SECRET = os.getenv("SYSTEM_SECRET")

def generate_api_key(user_id, telegram_user_link, email=None, first_name="Test", last_name="User", username="test_user"):
    """
    Generates a new API key for testing.
    
    Args:
        user_id (str): The user ID
        telegram_user_link (str): The Telegram user link
        email (str, optional): The email for Firebase/Supabase validation
        first_name (str, optional): The user's first name
        last_name (str, optional): The user's last name
        username (str, optional): The user's username
        
    Returns:
        str: The generated API key, or None if generation failed
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
            
        # Make the API request
        response = requests.post(
            f"{LOCAL_API_URL}/v1/api-keys",
            json=request_data
        )
        
        # Print the full response for debugging
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Return the API key if successful
        if response.status_code in (200, 201):
            api_key = response.json().get('api_key')
            print(f"API Key: {api_key}")
            return api_key
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

if __name__ == '__main__':
    # Generate an API key - email is now required for Firebase/Supabase validation
    api_key = generate_api_key(
        user_id="test_user_125",
        telegram_user_link="tg://user?id=1234567890",
        email="halkatcall12@gmail.com"  # Use a valid email that exists in Firebase
    )
    
    if not api_key:
        print("API key generation failed. Exiting.")
        exit()
