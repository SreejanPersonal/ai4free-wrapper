import random
import string
from ..config import Config 

def generate_api_key():
    """
    Generates a unique API key.
    
    The API key consists of a prefix (Config.API_KEY_PREFIX) followed by a random string
    of characters with a length of Config.API_KEY_LENGTH.

    Returns:
        A randomly generated API key string.
    """
    # Use only letters and digits, explicitly excluding hyphens
    # Remove characters that might be mistaken for hyphens
    characters = ''.join(c for c in string.ascii_letters + string.digits if c != '-')
    random_part = ''.join(random.choices(characters, k=Config.API_KEY_LENGTH))
    return f"{Config.API_KEY_PREFIX}{random_part}"

def generate_api_key_for_supabase():
    """
    Generates an API key with a placeholder for Supabase integration.
    
    The API key consists of a prefix (Config.API_KEY_PREFIX) followed by a random string
    of characters with a length of Config.API_KEY_PREFIX_LENGTH, followed by 'xxx' placeholder.
    The 'xxx' placeholder will be replaced with a random string of length Config.RANDOM_VALUE_LENGTH
    when the complete API key is generated.

    Returns:
        A partially generated API key string with 'xxx' placeholder.
    """
    # Use only letters and digits, explicitly excluding hyphens
    # Remove characters that might be mistaken for hyphens
    characters = ''.join(c for c in string.ascii_letters + string.digits if c != '-')
    prefix_part = ''.join(random.choices(characters, k=Config.API_KEY_PREFIX_LENGTH))
    return f"{Config.API_KEY_PREFIX}{prefix_part}xxx"
