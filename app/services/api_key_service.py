# app/services/api_key_service.py

from ..models.api_key import APIKey
from ..models.usage import User
from ..extensions import db
from ..utils.external_auth import (
    initialize_firebase, 
    process_user_for_api_key, 
    check_firebase_user,
    check_supabase_user,
    delete_supabase_user
)
from flask import request
from sqlalchemy.exc import IntegrityError
import logging

log = logging.getLogger(__name__)

def create_new_api_key(external_user_id, telegram_user_link, email=None, first_name=None, last_name=None, username=None):
    """
    Creates a new API key and associates it with a user.
    
    This function follows the exact flow from test_final.py:
    1. Initialize Firebase
    2. If email is provided (required):
       - Check if user exists in Firebase (must exist)
       - Check if user exists in Supabase
       - Process based on existence in both systems
    3. Create or update the user in PostgreSQL database
    4. Return the API key with appropriate status code and message
    
    Args:
        external_user_id (str): The external user ID (Telegram ID)
        telegram_user_link (str): The Telegram user link
        email (str, required): The user's email address for Firebase/Supabase validation
        first_name (str, optional): The user's first name
        last_name (str, optional): The user's last name
        username (str, optional): The user's username
        
    Returns:
        tuple: (api_key_str, status_code, message) - The API key, status code, and message
        
    Raises:
        ValueError: If the user already has an API key
        IntegrityError: If there's a database integrity error
        Exception: For any other unexpected errors
    """
    try:
        # Initialize Firebase
        initialize_firebase()
        
        # Email is required for Firebase/Supabase validation
        if not email:
            return None, 400, "Email is required for authentication"
        
        # Check if user exists in Firebase and Supabase
        firebase_exists = check_firebase_user(email)
        supabase_exists, supabase_user_data = check_supabase_user(email)
        
        # If user exists in Supabase but not in Firebase, delete from Supabase
        if supabase_exists and not firebase_exists:
            log.info(f"User with email {email} exists in Supabase but not in Firebase. Deleting from Supabase.")
            success, response = delete_supabase_user(supabase_user_data['id'])
            if success:
                log.info(f"Successfully deleted user with email {email} from Supabase.")
            else:
                log.warning(f"Failed to delete user with email {email} from Supabase.")
            return None, 404, f"User with email {email} not found in Firebase Authentication (Supabase entry cleaned up)"
        
        # If user doesn't exist in Firebase, return error
        if not firebase_exists:
            return None, 404, f"User with email {email} not found in Firebase Authentication"
        
        # 1. Create or retrieve the user in PostgreSQL
        user = User.query.filter_by(external_user_id=external_user_id).first()
        if not user:
            user = User(
                external_user_id=external_user_id, 
                telegram_user_link=telegram_user_link,
                first_name=first_name, 
                last_name=last_name, 
                username=username
            )
            db.session.add(user)
            db.session.flush()  # Flush to obtain user.user_id after insertion

        # Check if user already has an API key in PostgreSQL
        existing_key = APIKey.query.filter_by(user_id=user.user_id).first()
        
        # Process user with Firebase and Supabase
        result = process_user_for_api_key(email, existing_key.api_key if existing_key else None)
        
        if result["success"]:
            # User exists in both Firebase and Supabase
            if "complete_api_key" in result:
                api_key_str = result["complete_api_key"]
                
                # Update or create the API key in PostgreSQL
                if existing_key:
                    # Update existing key if needed
                    if existing_key.api_key != api_key_str:
                        existing_key.api_key = api_key_str
                        db.session.commit()
                else:
                    # Create new API key record
                    api_key = APIKey(api_key=api_key_str, user_id=user.user_id)
                    db.session.add(api_key)
                    db.session.commit()
                
                return api_key_str, result["status_code"], result["message"]
        else:
            # Error occurred during processing
            if existing_key:
                # If user already has an API key in PostgreSQL but processing failed,
                # return the existing key with an appropriate message
                return existing_key.api_key, 200, "Using existing API key from database"
            else:
                # If no existing key and processing failed, return the error
                return None, result["status_code"], result["message"]
        
        # If we reach here, something went wrong
        return None, 500, "Unexpected error during API key creation"

    except IntegrityError as e:
        db.session.rollback()
        log.error(f"Error creating API key: {e}")
        return None, 500, f"Database integrity error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        log.error(f"An unexpected error occurred: {e}")
        return None, 500, f"Unexpected error: {str(e)}"

def validate_api_key_header(request):
    """
    Validates the API key provided in the request header.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False

    api_key = auth_header.split(' ')[1]
    return validate_api_key(api_key)

def validate_api_key(api_key):
    """Validates an API key against the database."""
    api_key_record = APIKey.query.filter_by(api_key=api_key, is_active=True).first()
    return api_key_record is not None

def get_api_key_from_request(request):
    """Retrieves the APIKey object from the request header."""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header.split(' ')[1]
        return get_api_key_record(api_key)
    return None

def get_api_key_record(api_key):
    """Retrieves the APIKey object from the database."""
    return APIKey.query.filter_by(api_key=api_key, is_active=True).first()