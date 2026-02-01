"""
Alert model for security notifications and user alerts.
Supports different alert types and escalation levels.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Alert(Base):
    """Security alert for notifications."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Null for system alerts
    attack_id = Column(Integer, ForeignKey('attacks.id'), nullable=True)

    # Alert details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=False, index=True)  # attack_detected, threshold_exceeded, etc.
    severity = Column(String(20), nullable=False)  # critical, high, medium, low

    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")
    attack = relationship("Attack", backref="alerts")

    # Indexes
    __table_args__ = (
        Index('idx_alerts_user_type', 'user_id', 'alert_type'),
        Index('idx_alerts_severity_created', 'severity', 'created_at'),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity}, read={self.is_read})>"