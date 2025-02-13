# app/services/rate_limit_service.py

from flask import request, jsonify, current_app
from functools import wraps
import time
import logging
from .api_key_service import get_api_key_from_request
from ..extensions import redis_client

log = logging.getLogger(__name__)

# Lua script for atomic rate limiting
RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

def init_rate_limiter(app):
    """Initializes the rate limiter (loads the Lua script)."""
    with app.app_context():
        global rate_limiter
        rate_limiter = redis_client.register_script(RATE_LIMIT_SCRIPT)

def rate_limit(f):
    """
    Decorator to apply rate limiting to a route.
    Uses the configured REQUEST_LIMIT and RATE_LIMIT_WINDOW from the app configuration.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key_record = get_api_key_from_request(request)
        if not api_key_record:
            return jsonify({"error": "Invalid API Key", "status": 401}), 401

        api_key = api_key_record.api_key
        rate_limit_key = f"rate_limit:{api_key}"

        # Get the limit and window from config (default is 1 request per 60 seconds)
        limit = current_app.config.get("REQUEST_LIMIT", 1)
        window = current_app.config.get("RATE_LIMIT_WINDOW", 60)

        try:
            current = rate_limiter(keys=[rate_limit_key], args=[window], client=redis_client)
            if int(current) > limit:
                log.warning(f"Rate limit exceeded for API key: {api_key}")
                return jsonify({
                    "error": f"Rate limit exceeded - {limit} request(s) per {window} seconds",
                    "status": 429
                }), 429
        except Exception as e:
            log.error(f"Rate limiting error: {e}")
            # Fail open if an error occurs with rate limiting
            return f(*args, **kwargs)

        return f(*args, **kwargs)
    return decorated_function