# app/utils/external_auth.py

import firebase_admin
import random
import string
from firebase_admin import credentials, auth
from supabase import create_client, Client
import logging
from ..config import Config

# Set up logging
log = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with the service account credentials"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
            log.info("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        log.error(f"Error initializing Firebase: {e}")
        return False

# Initialize Supabase client
def get_supabase_client():
    """Get a Supabase client instance"""
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        return supabase
    except Exception as e:
        log.error(f"Error creating Supabase client: {e}")
        return None

def check_firebase_user(email):
    """
    Check if a user exists in Firebase Authentication
    
    Args:
        email (str): The email address to check
        
    Returns:
        bool: True if the user exists, False otherwise
    """
    try:
        user = auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        return False
    except Exception as e:
        log.error(f"Firebase error: {e}")
        return False

def get_supabase_user_by_id(user_id):
    """
    Get a user from Supabase by their ID
    
    Args:
        user_id: The ID of the user to fetch
        
    Returns:
        tuple: (bool, dict) - (True, user_data) if the user exists, (False, None) otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, None
            
        response = supabase.table("beta_api_keys").select("*").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return True, response.data[0]
        return False, None
    except Exception as e:
        log.error(f"Supabase error: {e}")
        return False, None

def check_supabase_user(email):
    """
    Check if a user exists in Supabase and return their data if found
    
    Args:
        email (str): The email address to check
        
    Returns:
        tuple: (bool, dict) - (True, user_data) if the user exists, (False, None) otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, None
            
        response = supabase.table("beta_api_keys").select("*").eq("user_email", email).execute()
        
        if response.data and len(response.data) > 0:
            return True, response.data[0]
        return False, None
    except Exception as e:
        log.error(f"Supabase error: {e}")
        return False, None

def delete_supabase_user(user_id):
    """
    Delete a user from Supabase by their ID
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        tuple: (bool, response) - (True, response) if successful, (False, None) otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, None
            
        response = supabase.table("beta_api_keys").delete().eq("id", user_id).execute()
        return True, response
    except Exception as e:
        log.error(f"Error deleting user: {e}")
        return False, None

def generate_random_api_string(length=Config.RANDOM_VALUE_LENGTH):
    """
    Generate a random string of specified length for API key
    
    Args:
        length (int): The length of the random string to generate
        
    Returns:
        str: A random string of the specified length
    """
    # Use only letters and digits, explicitly excluding hyphens
    # Remove characters that might be mistaken for hyphens
    characters = ''.join(c for c in string.ascii_letters + string.digits if c != '-')
    return ''.join(random.choice(characters) for _ in range(length))

def update_complete_api_key(user_id, new_api_key):
    """
    Update the complete_api_key for a user in Supabase
    
    Args:
        user_id: The ID of the user to update
        new_api_key (str): The new complete API key
        
    Returns:
        tuple: (bool, response) - (True, response) if successful, (False, None) otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, None
            
        response = supabase.table("beta_api_keys").update({"complete_api_key": new_api_key}).eq("id", user_id).execute()
        return True, response
    except Exception as e:
        log.error(f"Error updating complete API key: {e}")
        return False, None

def create_supabase_user(email, api_key=None):
    """
    Create a new user in Supabase with the given email and API key
    
    Args:
        email (str): The email address of the user
        api_key (str, optional): The API key to store. If not provided, a placeholder will be created.
        
    Returns:
        tuple: (bool, response) - (True, response) if successful, (False, None) otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, None
        
        # Generate a prefix for the API key if not provided
        if not api_key:
            from ..utils.helpers import generate_api_key_for_supabase
            api_key_with_xxx = generate_api_key_for_supabase()
        else:
            # Extract prefix from existing API key and add xxx
            prefix = api_key[:len(Config.API_KEY_PREFIX) + Config.API_KEY_PREFIX_LENGTH]
            api_key_with_xxx = f"{prefix}xxx"
            
        # Create a new user with the API key containing 'xxx' placeholder
        response = supabase.table("beta_api_keys").insert({
            "user_email": email,
            "api_key": api_key_with_xxx,
            "complete_api_key": None
        }).execute()
        
        if response.data and len(response.data) > 0:
            return True, response.data[0]
        return False, None
    except Exception as e:
        log.error(f"Error creating Supabase user: {e}")
        return False, None

def verify_partial_api_key(partial_key, user_data):
    """
    Verify if the partial API key matches the stored API key in Supabase
    
    Args:
        partial_key (str): The partial API key to verify
        user_data (dict): The user data from Supabase
        
    Returns:
        bool: True if the partial key matches, False otherwise
    """
    if not partial_key or not user_data:
        return False
        
    # Get the stored API key from user data
    stored_key = user_data.get('api_key')
    if not stored_key:
        return False
        
    # Check if the partial key is a substring of the stored key
    return partial_key in stored_key

def process_user_for_api_key(email, current_api_key=None):
    """
    Process a user by checking both systems and updating API key if needed
    
    This function exactly follows the flow in test_final.py:
    1. Check if user exists in Firebase
    2. Check if user exists in Supabase
    3. If user exists in Supabase but not Firebase, delete from Supabase
    4. If user exists in both systems:
       - If complete_api_key exists, return it
       - If api_key contains 'xxx', replace with random string and update
    5. Otherwise, return appropriate error
    
    Args:
        email (str): The email address of the user
        current_api_key (str, optional): The current API key if available
        
    Returns:
        dict: A dictionary containing the result of the operation
    """
    # Check Firebase
    firebase_exists = check_firebase_user(email)
    
    # Check Supabase
    supabase_exists, user_data = check_supabase_user(email)
    
    # If user exists in Supabase but not in Firebase, delete from Supabase
    if supabase_exists and not firebase_exists:
        success, response = delete_supabase_user(user_data['id'])
        return {
            "success": False,
            "message": "User deleted from Supabase as they do not exist in Firebase",
            "email": email,
            "status_code": 404
        }
    
    # If user exists in both systems
    if firebase_exists and supabase_exists:
        # Always prioritize returning an existing complete API key if it exists
        if user_data.get('complete_api_key'):
            log.info(f"Found existing complete API key for email {email}, returning it")
            return {
                "success": True,
                "message": "API key already exists",
                "email": email,
                "complete_api_key": user_data.get('complete_api_key'),
                "status_code": 200
            }
        
        # If no complete API key exists, check if we need to generate one
        current_api_key = user_data.get('api_key', '')
        
        # Check if API key contains the "xxx" pattern
        if 'xxx' in current_api_key:
            # Extract the prefix part before 'xxx'
            prefix = current_api_key.split('xxx')[0]
            log.info(f"Prefix: {prefix}")
            # Generate random value
            random_value = generate_random_api_string()
            
            # Create new API key - ensure no hyphens are added
            new_api_key = prefix + random_value
            
            # Update complete_api_key in Supabase (leave api_key untouched)
            success, response = update_complete_api_key(user_data['id'], new_api_key)
            
            if success:
                log.info(f"Generated new complete API key for email {email}")
                return {
                    "success": True,
                    "message": "Complete API key generated successfully",
                    "email": email,
                    "original_api_key": current_api_key,
                    "complete_api_key": new_api_key,
                    "status_code": 201
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to update complete API key",
                    "email": email,
                    "status_code": 500
                }
        else:
            return {
                "success": False,
                "message": "API key does not contain 'xxx' pattern for replacement",
                "email": email,
                "status_code": 400
            }
    elif firebase_exists and not supabase_exists:
        # User exists in Firebase but not in Supabase
        # Create a new entry in Supabase with a placeholder API key
        success, user_data = create_supabase_user(email)
        if success:
            log.info(f"Created new Supabase user for email {email}")
            return process_user_for_api_key(email)
        else:
            return {
                "success": False,
                "message": "Failed to create user in Supabase",
                "email": email,
                "status_code": 500
            }
    else:
        # User not found in one or both systems
        return {
            "success": False,
            "message": f"User not found in one or both systems. Firebase: {firebase_exists}, Supabase: {supabase_exists}",
            "email": email,
            "status_code": 404
        }
