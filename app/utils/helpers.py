# app/utils/helpers.py

import random
import string
from ..config import Config  # Import the Config class

def generate_api_key():
    """
    Generates a unique API key.

    Returns:
        A randomly generated API key string.
    """
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choices(characters, k=Config.API_KEY_LENGTH))
    return f"{Config.API_KEY_PREFIX}{random_part}"