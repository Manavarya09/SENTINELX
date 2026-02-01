"""
SentinelX Backend - Real-time Web Attack Detection Platform

Main FastAPI application entry point.
Handles routing, middleware, and WebSocket connections.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.middleware.request_inspector import RequestInspectorMiddleware
from app.routers import auth, dashboard, attacks
from app.ws.live_stream import websocket_router
from app.database import init_db
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    # Add cleanup logic here if needed

app = FastAPI(
    title="SentinelX API",
    description="Real-time web attack detection and visualization platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware for request inspection
app.add_middleware(RequestInspectorMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(attacks.router, prefix="/attacks", tags=["Attacks"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "SentinelX API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",  # Add actual checks
            "redis": "connected",
            "websocket": "active"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )