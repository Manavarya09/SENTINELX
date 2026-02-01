"""
Dashboard Router
Provides API endpoints for dashboard data and analytics.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models.attack import Attack
from app.models.request import RequestLog
from app.models.alert import Alert
from app.routers.auth import get_current_active_user
from app.models.user import User
from app.services.logs import LogService

router = APIRouter()
log_service = LogService()

@router.get("/stats")
async def get_dashboard_stats(hours: int = 24, current_user: User = Depends(get_current_active_user)):
    """
    Get dashboard statistics for the last N hours.
    """
    # Check user permissions (admin/analyst can see all, users see limited)
    if current_user.role not in ["admin", "analyst"]:
        # For regular users, return limited stats
        return await get_limited_stats(hours)

    async for db in get_db():
        try:
            threshold = datetime.utcnow() - timedelta(hours=hours)

            # Total requests
            total_requests_query = select(func.count(RequestLog.id)).where(
                RequestLog.timestamp >= threshold
            )
            total_requests = (await db.execute(total_requests_query)).scalar() or 0

            # Attack count
            attack_count_query = select(func.count(Attack.id)).where(
                Attack.timestamp >= threshold
            )
            attack_count = (await db.execute(attack_count_query)).scalar() or 0

            # Attack rate
            attack_rate = (attack_count / total_requests * 100) if total_requests > 0 else 0

            # Top attack types
            attack_types_query = select(
                Attack.attack_type,
                func.count(Attack.id).label('count')
            ).where(
                Attack.timestamp >= threshold
            ).group_by(Attack.attack_type).order_by(desc('count')).limit(5)

            attack_types_result = await db.execute(attack_types_query)
            top_attack_types = [
                {"type": row.attack_type, "count": row.count}
                for row in attack_types_result
            ]

            # Severity distribution
            severity_query = select(
                Attack.severity,
                func.count(Attack.id).label('count')
            ).where(
                Attack.timestamp >= threshold
            ).group_by(Attack.severity)

            severity_result = await db.execute(severity_query)
            severity_dist = {row.severity: row.count for row in severity_result}

            # Recent alerts
            alerts_query = select(Alert).order_by(desc(Alert.created_at)).limit(10)
            alerts_result = await db.execute(alerts_query)
            recent_alerts = [{
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "created_at": alert.created_at.isoformat()
            } for alert in alerts_result.scalars()]

            return {
                "time_range_hours": hours,
                "total_requests": total_requests,
                "attack_count": attack_count,
                "attack_rate": round(attack_rate, 2),
                "top_attack_types": top_attack_types,
                "severity_distribution": severity_dist,
                "recent_alerts": recent_alerts
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/attacks/recent")
async def get_recent_attacks(limit: int = 50, current_user: User = Depends(get_current_active_user)):
    """
    Get recent attack events.
    """
    return await log_service.get_recent_attacks(limit)

@router.get("/attacks/{attack_id}")
async def get_attack_details(attack_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Get detailed information about a specific attack.
    """
    async for db in get_db():
        try:
            query = select(Attack).where(Attack.id == attack_id)
            result = await db.execute(query)
            attack = result.scalar_one_or_none()

            if not attack:
                raise HTTPException(status_code=404, detail="Attack not found")

            # Get associated request log
            request_query = select(RequestLog).where(RequestLog.id == attack.request_id)
            request_result = await db.execute(request_query)
            request_log = request_result.scalar_one_or_none()

            return {
                "id": attack.id,
                "timestamp": attack.timestamp.isoformat(),
                "attack_type": attack.attack_type,
                "severity": attack.severity,
                "confidence": attack.confidence,
                "risk_score": attack.final_risk_score,
                "explanation": attack.explanation,
                "payload": attack.payload,
                "request_details": {
                    "ip_address": request_log.ip_address if request_log else None,
                    "path": request_log.path if request_log else None,
                    "method": request_log.method if request_log else None,
                    "user_agent": request_log.user_agent if request_log else None
                } if request_log else None
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/geo/attacks")
async def get_attack_geography(hours: int = 24, current_user: User = Depends(get_current_active_user)):
    """
    Get attack data grouped by geographic location.
    """
    async for db in get_db():
        try:
            threshold = datetime.utcnow() - timedelta(hours=hours)

            # This would require IP geolocation data
            # For now, return mock geographic data
            return {
                "time_range_hours": hours,
                "locations": [
                    {"country": "United States", "attacks": 45, "lat": 37.0902, "lng": -95.7129},
                    {"country": "China", "attacks": 32, "lat": 35.8617, "lng": 104.1954},
                    {"country": "Russia", "attacks": 28, "lat": 61.5240, "lng": 105.3188},
                    {"country": "Germany", "attacks": 15, "lat": 51.1657, "lng": 10.4515},
                    {"country": "India", "attacks": 12, "lat": 20.5937, "lng": 78.9629}
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/timeline")
async def get_attack_timeline(hours: int = 24, current_user: User = Depends(get_current_active_user)):
    """
    Get attack count over time for timeline visualization.
    """
    async for db in get_db():
        try:
            threshold = datetime.utcnow() - timedelta(hours=hours)

            # Group attacks by hour
            timeline_query = select(
                func.date_trunc('hour', Attack.timestamp).label('hour'),
                func.count(Attack.id).label('count')
            ).where(
                Attack.timestamp >= threshold
            ).group_by(func.date_trunc('hour', Attack.timestamp)).order_by('hour')

            result = await db.execute(timeline_query)
            timeline_data = [
                {
                    "timestamp": row.hour.isoformat(),
                    "attacks": row.count
                }
                for row in result
            ]

            return {
                "time_range_hours": hours,
                "timeline": timeline_data
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_limited_stats(hours: int) -> Dict[str, Any]:
    """Get limited statistics for regular users."""
    return {
        "time_range_hours": hours,
        "total_requests": 0,  # Would implement user-specific filtering
        "attack_count": 0,
        "attack_rate": 0,
        "message": "Detailed statistics available for analysts and administrators only"
    }