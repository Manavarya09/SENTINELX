"""
Attack model for storing detected attack instances.
Links to request logs with detailed analysis.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class Attack(Base):
    """Detected attack with analysis details."""
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('request_logs.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Attack classification
    attack_type = Column(String(50), nullable=False, index=True)  # sqli, xss, brute_force, etc.
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    confidence = Column(Float, nullable=False)  # 0-1 confidence score

    # Analysis details
    explanation = Column(Text, nullable=False)  # Human-readable explanation
    payload = Column(Text)  # The malicious payload
    matched_patterns = Column(JSONB)  # Patterns that triggered detection
    risk_factors = Column(JSONB)  # Contributing risk factors

    # Risk scoring
    base_score = Column(Float, nullable=False)  # Base risk score
    frequency_multiplier = Column(Float, default=1.0)  # Based on attack frequency
    complexity_multiplier = Column(Float, default=1.0)  # Based on payload complexity
    final_risk_score = Column(Float, nullable=False)  # Final calculated score

    # Relationships
    request = relationship("RequestLog", backref="attacks")

    # Indexes
    __table_args__ = (
        Index('idx_attacks_timestamp_type', 'timestamp', 'attack_type'),
        Index('idx_attacks_severity', 'severity'),
        Index('idx_attacks_risk_score', 'final_risk_score'),
    )

    def __repr__(self):
        return f"<Attack(id={self.id}, type={self.attack_type}, severity={self.severity}, risk={self.final_risk_score})>"