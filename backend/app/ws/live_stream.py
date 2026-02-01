"""
Live Stream Service
Manages WebSocket connections for real-time attack updates.
Broadcasts security events to connected dashboard clients.
"""

from typing import Dict, Any, List
import json
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Mark for removal if send fails
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

class LiveStreamService:
    """
    Service for streaming live security events via WebSocket.
    Manages connections and broadcasts attack events.
    """

    def __init__(self):
        self.manager = ConnectionManager()
        self.event_queue = asyncio.Queue()

    async def broadcast_attack_event(self, log_entry: Dict[str, Any],
                                   security_result: Dict[str, Any]):
        """
        Broadcast an attack event to all connected clients.
        """
        event = {
            "type": "attack_detected",
            "timestamp": log_entry.get("timestamp", ""),
            "data": {
                "attack_type": security_result.get("attack_type"),
                "severity": security_result.get("severity"),
                "confidence": security_result.get("confidence_score", 0),
                "risk_score": security_result.get("risk_score", 0),
                "ip_address": log_entry.get("ip_address"),
                "path": log_entry.get("path"),
                "explanation": security_result.get("explanation"),
                "log_id": log_entry.get("log_id")
            }
        }

        await self.manager.broadcast(event)

    async def broadcast_stats_update(self, stats: Dict[str, Any]):
        """
        Broadcast statistics update to all clients.
        """
        event = {
            "type": "stats_update",
            "timestamp": "",  # Would be current timestamp
            "data": stats
        }

        await self.manager.broadcast(event)

    async def broadcast_alert(self, alert: Dict[str, Any]):
        """
        Broadcast a security alert to all clients.
        """
        event = {
            "type": "alert",
            "timestamp": alert.get("created_at", ""),
            "data": {
                "alert_id": alert.get("id"),
                "title": alert.get("title"),
                "message": alert.get("message"),
                "severity": alert.get("severity"),
                "alert_type": alert.get("alert_type")
            }
        }

        await self.manager.broadcast(event)

# Global instance
live_stream = LiveStreamService()

# WebSocket endpoint handler
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live dashboard updates.
    """
    await live_stream.manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for client messages
            data = await websocket.receive_text()
            # For now, we don't process client messages
            # Could be extended for client-side filtering, etc.
    except WebSocketDisconnect:
        live_stream.manager.disconnect(websocket)

# Router for WebSocket
from fastapi import APIRouter
websocket_router = APIRouter()

@websocket_router.websocket("/live")
async def live_websocket(websocket: WebSocket):
    """WebSocket endpoint for live security events."""
    await websocket_endpoint(websocket)