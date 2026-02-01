"""
Request log model for storing HTTP request data.
Optimized for security analysis and performance.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func, Index
from sqlalchemy.dialects.postgresql import INET, JSONB
from app.database import Base

class RequestLog(Base):
    """HTTP request log with security metadata."""
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(INET, index=True, nullable=False)
    user_agent = Column(Text)
    method = Column(String(10), nullable=False)
    path = Column(Text, nullable=False)
    query_string = Column(Text)
    headers = Column(JSONB)  # Store headers as JSON
    body = Column(Text)  # Request body (truncated if too large)
    response_status = Column(Integer)
    response_time = Column(Float)  # Response time in seconds
    user_id = Column(Integer, index=True, nullable=True)  # If authenticated

    # Security analysis results
    is_attack = Column(Boolean, default=False, index=True)
    attack_type = Column(String(50), index=True, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1
    risk_score = Column(Float, nullable=True)  # 0-100

    # Indexes for performance
    __table_args__ = (
        Index('idx_request_logs_timestamp_ip', 'timestamp', 'ip_address'),
        Index('idx_request_logs_attack_type', 'attack_type'),
        Index('idx_request_logs_risk_score', 'risk_score'),
    )

    def __repr__(self):
        return f"<RequestLog(id={self.id}, ip={self.ip_address}, path={self.path}, is_attack={self.is_attack})>"