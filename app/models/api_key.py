from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from .base import Base
from datetime import datetime

class APIKey(Base):
    """
    Represents an API key in the database.
    """
    __tablename__ = "api_keys"

    # Use the api_key itself as the primary key.
    api_key = Column(String(60), primary_key=True)
    # Reference the user using the renamed primary key (user_id) and enforce one-to-one uniqueness.
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    # Use MutableDict to track in-place changes to the JSONB column.
    model_usage = Column(MutableDict.as_mutable(JSONB), nullable=False, server_default=text("'{}'::jsonb"))

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(api_key='{self.api_key}', user_id={self.user_id})>"