# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
import redis
from urllib.parse import urlparse
import os

# Initialize SQLAlchemy and Redis extensions
# These are initialized *without* an app object,
# which is the recommended practice when using the
# application factory pattern.  They will be initialized
# later with the app object using init_app().

db = SQLAlchemy()

# Configure Redis client with Upstash-specific settings if needed
def get_redis_config():
    redis_url = os.getenv('REDIS_URL')
    if redis_url and ('upstash.io' in redis_url or '1panel' in redis_url or '1Panel' in redis_url):
        # Upstash-specific configuration
        return {
            'config_prefix': 'REDIS',
            'ssl': True,
            'ssl_certfile': None,
            'decode_responses': True,
            'socket_timeout': 5,
            'retry_on_timeout': True
        }
    # Default configuration for local Redis
    return {
        'config_prefix': 'REDIS',
        'decode_responses': True,
        'socket_timeout': 5
    }

redis_client = FlaskRedis(**get_redis_config())
