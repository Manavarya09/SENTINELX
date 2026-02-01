"""
Log Service
Handles logging of requests and attacks to database.
Provides query methods for analytics.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import json

from app.database import get_db
from app.models.request import RequestLog
from app.models.attack import Attack

class LogService:
    """
    Service for logging requests and attacks.
    Provides methods for storing and retrieving security events.
    """

    async def log_request(self, request_data: Dict[str, Any],
                         security_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log a request with security analysis results.
        """
        async for db in get_db():
            try:
                # Create request log entry
                log_entry = RequestLog(
                    ip_address=request_data["ip_address"],
                    user_agent=request_data.get("user_agent", ""),
                    method=request_data["method"],
                    path=request_data["path"],
                    query_string=request_data.get("query_string", ""),
                    headers=json.dumps(request_data.get("headers", {})),
                    body=request_data.get("body", ""),
                    response_status=request_data.get("response_status", 200),
                    response_time=request_data.get("response_time", 0.0),
                    is_attack=security_result.get("is_attack", False),
                    attack_type=security_result.get("attack_type"),
                    confidence_score=security_result.get("confidence_score", 0.0),
                    risk_score=security_result.get("risk_score", 0.0)
                )

                db.add(log_entry)
                await db.flush()  # Get the ID

                # If it's an attack, create attack record
                if security_result.get("is_attack"):
                    attack_entry = Attack(
                        request_id=log_entry.id,
                        attack_type=security_result["attack_type"],
                        severity=security_result["severity"],
                        confidence=security_result["confidence_score"],
                        explanation=security_result["explanation"],
                        payload=self._extract_payload(request_data),
                        matched_patterns=json.dumps([]),  # Would be populated by rules
                        risk_factors=json.dumps({}),
                        base_score=security_result["confidence_score"] * 100,
                        final_risk_score=security_result["risk_score"]
                    )
                    db.add(attack_entry)

                await db.commit()

                return {
                    "log_id": log_entry.id,
                    "attack_id": attack_entry.id if security_result.get("is_attack") else None,
                    "logged": True
                }

            except Exception as e:
                await db.rollback()
                print(f"Logging error: {str(e)}")
                return {"logged": False, "error": str(e)}

    async def get_recent_attacks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent attack logs."""
        async for db in get_db():
            try:
                query = select(Attack).order_by(desc(Attack.timestamp)).limit(limit)
                result = await db.execute(query)
                attacks = result.scalars().all()

                return [{
                    "id": attack.id,
                    "timestamp": attack.timestamp.isoformat(),
                    "attack_type": attack.attack_type,
                    "severity": attack.severity,
                    "confidence": attack.confidence,
                    "risk_score": attack.final_risk_score,
                    "explanation": attack.explanation
                } for attack in attacks]

            except Exception as e:
                print(f"Error fetching attacks: {str(e)}")
                return []

    async def get_attack_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get attack statistics for the last N hours."""
        async for db in get_db():
            try:
                # Calculate time threshold
                from datetime import datetime, timedelta
                threshold = datetime.utcnow() - timedelta(hours=hours)

                # Query attack counts by type
                query = select(
                    Attack.attack_type,
                    func.count(Attack.id).label('count')
                ).where(
                    Attack.timestamp >= threshold
                ).group_by(Attack.attack_type)

                result = await db.execute(query)
                type_counts = {row.attack_type: row.count for row in result}

                # Query severity distribution
                severity_query = select(
                    Attack.severity,
                    func.count(Attack.id).label('count')
                ).where(
                    Attack.timestamp >= threshold
                ).group_by(Attack.severity)

                severity_result = await db.execute(severity_query)
                severity_counts = {row.severity: row.count for row in severity_result}

                # Total attacks
                total_query = select(func.count(Attack.id)).where(Attack.timestamp >= threshold)
                total_result = await db.execute(total_query)
                total_attacks = total_result.scalar() or 0

                return {
                    "total_attacks": total_attacks,
                    "by_type": type_counts,
                    "by_severity": severity_counts,
                    "time_range_hours": hours
                }

            except Exception as e:
                print(f"Error fetching attack stats: {str(e)}")
                return {"error": str(e)}

    async def get_ip_attack_history(self, ip_address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get attack history for a specific IP."""
        async for db in get_db():
            try:
                query = select(Attack).join(RequestLog).where(
                    RequestLog.ip_address == ip_address
                ).order_by(desc(Attack.timestamp)).limit(limit)

                result = await db.execute(query)
                attacks = result.scalars().all()

                return [{
                    "id": attack.id,
                    "timestamp": attack.timestamp.isoformat(),
                    "attack_type": attack.attack_type,
                    "severity": attack.severity,
                    "risk_score": attack.final_risk_score,
                    "explanation": attack.explanation
                } for attack in attacks]

            except Exception as e:
                print(f"Error fetching IP history: {str(e)}")
                return []

    def _extract_payload(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract the malicious payload from request data."""
        # Try to identify the most suspicious part
        candidates = [
            request_data.get("query_string", ""),
            request_data.get("body", ""),
            request_data.get("path", "")
        ]

        # Return the longest candidate (likely to contain the payload)
        return max(candidates, key=len) if candidates else None