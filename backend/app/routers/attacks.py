"""
Attacks Router
Provides endpoints for attack management and analysis.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.models.attack import Attack
from app.models.ip_reputation import IPReputation
from app.routers.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_attacks(page: int = 1, limit: int = 50,
                     attack_type: str = None, severity: str = None,
                     current_user: User = Depends(get_current_active_user)):
    """
    Get paginated list of attacks with optional filtering.
    """
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    async for db in get_db():
        try:
            query = select(Attack)

            # Apply filters
            if attack_type:
                query = query.where(Attack.attack_type == attack_type)
            if severity:
                query = query.where(Attack.severity == severity)

            # Pagination
            offset = (page - 1) * limit
            query = query.order_by(Attack.timestamp.desc()).offset(offset).limit(limit)

            result = await db.execute(query)
            attacks = result.scalars().all()

            # Get total count for pagination
            count_query = select(func.count(Attack.id))
            if attack_type:
                count_query = count_query.where(Attack.attack_type == attack_type)
            if severity:
                count_query = count_query.where(Attack.severity == severity)

            total_count = (await db.execute(count_query)).scalar() or 0

            return {
                "attacks": [{
                    "id": attack.id,
                    "timestamp": attack.timestamp.isoformat(),
                    "attack_type": attack.attack_type,
                    "severity": attack.severity,
                    "confidence": attack.confidence,
                    "risk_score": attack.final_risk_score,
                    "explanation": attack.explanation
                } for attack in attacks],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/types")
async def get_attack_types(current_user: User = Depends(get_current_active_user)):
    """
    Get list of unique attack types.
    """
    async for db in get_db():
        try:
            query = select(Attack.attack_type).distinct()
            result = await db.execute(query)
            types = [row.attack_type for row in result]

            return {"attack_types": types}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/severities")
async def get_attack_severities(current_user: User = Depends(get_current_active_user)):
    """
    Get list of unique severity levels.
    """
    async for db in get_db():
        try:
            query = select(Attack.severity).distinct()
            result = await db.execute(query)
            severities = [row.severity for row in result]

            return {"severities": severities}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/{attack_id}/acknowledge")
async def acknowledge_attack(attack_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Acknowledge an attack (mark as reviewed).
    """
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    async for db in get_db():
        try:
            # For now, we'll add an acknowledged field to Attack model if needed
            # This is a placeholder for attack acknowledgment functionality
            query = select(Attack).where(Attack.id == attack_id)
            result = await db.execute(query)
            attack = result.scalar_one_or_none()

            if not attack:
                raise HTTPException(status_code=404, detail="Attack not found")

            # Could add acknowledged_at timestamp, etc.
            return {"message": "Attack acknowledged", "attack_id": attack_id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/ip/{ip_address}")
async def get_attacks_by_ip(ip_address: str, current_user: User = Depends(get_current_active_user)):
    """
    Get all attacks from a specific IP address.
    """
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    async for db in get_db():
        try:
            from app.models.request import RequestLog

            query = select(Attack).join(RequestLog).where(
                RequestLog.ip_address == ip_address
            ).order_by(Attack.timestamp.desc()).limit(100)

            result = await db.execute(query)
            attacks = result.scalars().all()

            return {
                "ip_address": ip_address,
                "attacks": [{
                    "id": attack.id,
                    "timestamp": attack.timestamp.isoformat(),
                    "attack_type": attack.attack_type,
                    "severity": attack.severity,
                    "risk_score": attack.final_risk_score,
                    "explanation": attack.explanation
                } for attack in attacks],
                "total_attacks": len(attacks)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/ip/{ip_address}/block")
async def block_ip(ip_address: str, current_user: User = Depends(get_current_active_user)):
    """
    Block an IP address.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")

    async for db in get_db():
        try:
            # Update or create IP reputation record
            query = select(IPReputation).where(IPReputation.ip_address == ip_address)
            result = await db.execute(query)
            ip_rep = result.scalar_one_or_none()

            if ip_rep:
                ip_rep.is_blocked = True
                ip_rep.blocked_until = None  # Permanent block
            else:
                ip_rep = IPReputation(
                    ip_address=ip_address,
                    is_blocked=True,
                    reputation_score=100.0  # Maximum bad score
                )
                db.add(ip_rep)

            await db.commit()

            return {"message": f"IP {ip_address} blocked successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/ip/{ip_address}/unblock")
async def unblock_ip(ip_address: str, current_user: User = Depends(get_current_active_user)):
    """
    Unblock an IP address.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")

    async for db in get_db():
        try:
            query = select(IPReputation).where(IPReputation.ip_address == ip_address)
            result = await db.execute(query)
            ip_rep = result.scalar_one_or_none()

            if ip_rep:
                ip_rep.is_blocked = False
                ip_rep.blocked_until = None
                await db.commit()
                return {"message": f"IP {ip_address} unblocked successfully"}
            else:
                raise HTTPException(status_code=404, detail="IP not found in reputation database")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")