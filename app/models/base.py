# app/models/base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from ..extensions import db

# Define metadata outside the Base class
metadata = MetaData()

Base = declarative_base(metadata=metadata)
Base.query = db.session.query_property()

# You can add common methods or properties here