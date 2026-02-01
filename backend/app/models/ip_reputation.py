"""
IP reputation model for tracking malicious IP behavior.
Used for risk scoring and blocking decisions.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, func, Index
from sqlalchemy.dialects.postgresql import INET
from app.database import Base

class IPReputation(Base):
    """IP address reputation tracking."""
    __tablename__ = "ip_reputation"

    ip_address = Column(INET, primary_key=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Reputation metrics
    total_requests = Column(Integer, default=0)
    attack_count = Column(Integer, default=0)
    block_count = Column(Integer, default=0)

    # Calculated scores
    reputation_score = Column(Float, default=0.0)  # 0-100, higher is worse
    confidence_score = Column(Float, default=0.0)  # 0-1, how confident we are

    # Geographic data (optional, populated by external service)
    country = Column(String(2))  # ISO country code
    city = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)

    # Status
    is_blocked = Column(Boolean, default=False)
    blocked_until = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_ip_reputation_score', 'reputation_score'),
        Index('idx_ip_reputation_country', 'country'),
        Index('idx_ip_reputation_blocked', 'is_blocked'),
    )

    def __repr__(self):
        return f"<IPReputation(ip={self.ip_address}, score={self.reputation_score}, blocked={self.is_blocked})>"