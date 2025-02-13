# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

# Initialize SQLAlchemy and Redis extensions
# These are initialized *without* an app object,
# which is the recommended practice when using the
# application factory pattern.  They will be initialized
# later with the app object using init_app().

db = SQLAlchemy()
redis_client = FlaskRedis()