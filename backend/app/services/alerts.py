"""
Alert Service
Manages security alerts and notifications.
Creates alerts for high-risk attacks and system events.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.alert import Alert
from app.models.user import User

class AlertService:
    """
    Service for creating and managing security alerts.
    Handles alert generation, escalation, and notifications.
    """

    async def create_alert(self, attack_type: str, severity: str,
                          risk_score: float, request_data: Dict[str, Any],
                          user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a security alert for a detected attack.
        """
        async for db in get_db():
            try:
                # Create alert message based on attack type
                title, message = self._generate_alert_content(
                    attack_type, severity, risk_score, request_data
                )

                alert = Alert(
                    user_id=user_id,
                    title=title,
                    message=message,
                    alert_type=f"attack_{attack_type}",
                    severity=severity
                )

                db.add(alert)
                await db.commit()

                return {
                    "alert_id": alert.id,
                    "created": True,
                    "severity": severity
                }

            except Exception as e:
                await db.rollback()
                print(f"Alert creation error: {str(e)}")
                return {"created": False, "error": str(e)}

    async def get_user_alerts(self, user_id: int, limit: int = 50,
                             unread_only: bool = False) -> list:
        """Get alerts for a specific user."""
        async for db in get_db():
            try:
                query = select(Alert).where(Alert.user_id == user_id)

                if unread_only:
                    query = query.where(Alert.is_read == False)

                query = query.order_by(Alert.created_at.desc()).limit(limit)

                result = await db.execute(query)
                alerts = result.scalars().all()

                return [{
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "is_read": alert.is_read,
                    "is_acknowledged": alert.is_acknowledged,
                    "created_at": alert.created_at.isoformat(),
                    "escalated": alert.escalated
                } for alert in alerts]

            except Exception as e:
                print(f"Error fetching user alerts: {str(e)}")
                return []

    async def mark_alert_read(self, alert_id: int, user_id: int) -> bool:
        """Mark an alert as read."""
        async for db in get_db():
            try:
                query = select(Alert).where(
                    Alert.id == alert_id,
                    Alert.user_id == user_id
                )
                result = await db.execute(query)
                alert = result.scalar_one_or_none()

                if alert:
                    alert.is_read = True
                    await db.commit()
                    return True
                return False

            except Exception as e:
                await db.rollback()
                print(f"Error marking alert read: {str(e)}")
                return False

    async def get_system_alerts(self, limit: int = 100) -> list:
        """Get system-wide alerts (no specific user)."""
        async for db in get_db():
            try:
                query = select(Alert).where(Alert.user_id.is_(None)).order_by(
                    Alert.created_at.desc()
                ).limit(limit)

                result = await db.execute(query)
                alerts = result.scalars().all()

                return [{
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "created_at": alert.created_at.isoformat(),
                    "escalated": alert.escalated
                } for alert in alerts]

            except Exception as e:
                print(f"Error fetching system alerts: {str(e)}")
                return []

    def _generate_alert_content(self, attack_type: str, severity: str,
                               risk_score: float, request_data: Dict[str, Any]) -> tuple:
        """Generate alert title and message based on attack details."""

        ip = request_data.get("ip_address", "unknown")
        path = request_data.get("path", "/")

        # Base messages by attack type
        attack_messages = {
            "sqli": {
                "title": "SQL Injection Attempt Detected",
                "message": f"Potential SQL injection attack from {ip} targeting {path}. Risk score: {risk_score:.1f}"
            },
            "xss": {
                "title": "Cross-Site Scripting Attempt Detected",
                "message": f"Potential XSS attack from {ip} targeting {path}. Risk score: {risk_score:.1f}"
            },
            "path_traversal": {
                "title": "Path Traversal Attempt Detected",
                "message": f"Potential path traversal attack from {ip} attempting to access restricted files. Risk score: {risk_score:.1f}"
            },
            "command_injection": {
                "title": "Command Injection Attempt Detected",
                "message": f"Potential command injection attack from {ip}. Risk score: {risk_score:.1f}"
            },
            "brute_force": {
                "title": "Brute Force Attack Detected",
                "message": f"Brute force login attempts from {ip}. Risk score: {risk_score:.1f}"
            },
            "rate_abuse": {
                "title": "Rate Limit Exceeded",
                "message": f"Excessive requests from {ip} exceeding rate limits. Risk score: {risk_score:.1f}"
            },
            "anomaly": {
                "title": "Anomalous Request Pattern Detected",
                "message": f"Unusual request pattern detected from {ip}. Risk score: {risk_score:.1f}"
            }
        }

        default = {
            "title": "Security Threat Detected",
            "message": f"Unknown attack type '{attack_type}' detected from {ip}. Risk score: {risk_score:.1f}"
        }

        content = attack_messages.get(attack_type, default)

        # Add severity indicator
        if severity in ["critical", "high"]:
            content["title"] = f"🚨 {content['title']}"
        elif severity == "medium":
            content["title"] = f"⚠️ {content['title']}"

        return content["title"], content["message"]