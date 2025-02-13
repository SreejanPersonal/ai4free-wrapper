# app/services/api_key_service.py

from ..models.api_key import APIKey
from ..models.usage import User
from ..extensions import db
from ..utils.helpers import generate_api_key  # Import the key generation function
from flask import request
from sqlalchemy.exc import IntegrityError
import logging

log = logging.getLogger(__name__)

def create_new_api_key(external_user_id, telegram_user_link, first_name=None, last_name=None, username=None):
    """
    Creates a new API key and associates it with a user.
    """
    try:
        # 1. Create or retrieve the user
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

        # Check if user already has an API key.
        # Note: Reference the primary key as 'user.user_id' instead of 'user.id'
        existing_key = APIKey.query.filter_by(user_id=user.user_id).first()
        if existing_key:
            log.warning(f"User {external_user_id} already has an API key.")
            raise ValueError("User already has an API Key")

        # 2. Generate the API key
        api_key_str = generate_api_key()

        # 3. Create the APIKey record using the new attribute 'user_id'
        api_key = APIKey(api_key=api_key_str, user_id=user.user_id)
        db.session.add(api_key)
        db.session.commit()

        return api_key_str

    except IntegrityError as e:
        db.session.rollback()
        log.error(f"Error creating API key: {e}")
        raise  # Re-raise so it can be handled by controller
    except Exception as e:
        db.session.rollback()
        log.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise for further handling

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