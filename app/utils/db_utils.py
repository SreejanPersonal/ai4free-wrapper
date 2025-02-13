# app/utils/db_utils.py
from functools import wraps
from flask import current_app

def with_app_context(f):
    """
    Decorator to wrap a function with the Flask application context.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with current_app.app_context():
            return f(*args, **kwargs)
    return decorated_function