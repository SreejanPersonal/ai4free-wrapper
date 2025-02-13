from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, BigInteger, Index
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

# ----------------------------------------------------------------
# 1. User Model (users table)
# ----------------------------------------------------------------
class User(Base):
    """Represents a user in the database."""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_last_request', 'last_request_time'),
        Index('idx_users_cost', 'total_cost'),
    )

    user_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_input_tokens = Column(BigInteger, default=0)
    total_output_tokens = Column(BigInteger, default=0)
    total_cost = Column(Numeric(12, 6), default=0.0)
    last_request_time = Column(DateTime(timezone=True))
    external_user_id = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    telegram_user_link = Column(String(255), nullable=False)

    # Relationships
    api_keys = relationship("APIKey", back_populates="user")

    def __repr__(self):
        return f"<User(external_user_id='{self.external_user_id}', username='{self.username}')>"

# ----------------------------------------------------------------
# 2. API Metrics Table (Usage)
# ----------------------------------------------------------------
class Usage(Base):
    """
    Aggregates usage data for an API key with respect to a specific model.
    There will be only one row per (api_key, model) combination.
    """
    __tablename__ = "api_metrics"
    
    # Composite primary key: one row per API key per model.
    api_key = Column(String(60), ForeignKey("api_keys.api_key"), primary_key=True)
    model = Column(String(50), primary_key=True)
    
    # Last updated timestamp for reference.
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    input_tokens = Column(BigInteger, default=0)
    output_tokens = Column(BigInteger, default=0)
    cost = Column(Numeric(12, 6), default=0.0)
    
    def __repr__(self):
        return f"<Usage(api_key='{self.api_key}', model='{self.model}')>"

# ----------------------------------------------------------------
# 3. Total API Usage Table (TotalAPIUsage)
# ----------------------------------------------------------------
class TotalAPIUsage(Base):
    """
    Aggregates the overall API usage data.
    This table will contain a single row that is updated on every request.
    """
    __tablename__ = "total_api_usage"
    
    # Fixed singleton row using a constant id (1).
    id = Column(Integer, primary_key=True, autoincrement=False, default=1)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_input_tokens = Column(BigInteger, default=0)
    total_output_tokens = Column(BigInteger, default=0)
    total_cost = Column(Numeric(12, 6), default=0.0)
    
    def __repr__(self):
        return f"<TotalAPIUsage(id={self.id})>"

# ----------------------------------------------------------------
# 4. Global Model Usage Table (ModelUsage)
# ----------------------------------------------------------------
class ModelUsage(Base):
    """
    Aggregates global usage data for each model.
    There will be one row per model.
    """
    __tablename__ = "model_usage"
    
    # One row per model.
    model = Column(String(50), primary_key=True)
    
    # Last updated timestamp.
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_input_tokens = Column(BigInteger, default=0)
    total_output_tokens = Column(BigInteger, default=0)
    total_cost = Column(Numeric(12, 6), default=0.0)
    
    def __repr__(self):
        return f"<ModelUsage(model='{self.model}')>"