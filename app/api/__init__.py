# app/api/__init__.py

# This file marks the 'api' directory as a Python package.
# It can be left mostly empty, but it's good practice to
# explicitly import key components that you want to be
# accessible directly from the 'api' package.

from .routes import api_blueprint  # Make the blueprint accessible

# You could also import specific controllers or schemas here
# if you want them to be available via 'from app.api import ...'