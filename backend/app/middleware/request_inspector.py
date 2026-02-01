"""
Request Inspector Middleware
Intercepts all HTTP requests for security analysis.
Performs real-time attack detection and logging.
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.engine.rules import RuleEngine
from app.engine.anomaly import AnomalyDetector
from app.engine.risk import RiskScorer
from app.services.logs import LogService
from app.services.alerts import AlertService
from app.ws.live_stream import LiveStreamService

class RequestInspectorMiddleware(BaseHTTPMiddleware):
    """
    Middleware that inspects incoming requests for security threats.
    Processes requests through the security pipeline:
    Request → Rule Engine → Anomaly Detector → Risk Scoring → Logging → Streaming
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()
        self.risk_scorer = RiskScorer()
        self.log_service = LogService()
        self.alert_service = AlertService()
        self.live_stream = LiveStreamService()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request through the security pipeline.
        """
        start_time = time.time()

        # Extract request data
        request_data = await self._extract_request_data(request)

        # Initialize security analysis result
        security_result = {
            "is_attack": False,
            "attack_type": None,
            "confidence_score": 0.0,
            "severity": "low",
            "explanation": "",
            "risk_score": 0.0
        }

        try:
            # 1. Rule-based detection
            rule_result = await self.rule_engine.analyze_request(request_data)
            if rule_result["is_attack"]:
                security_result.update(rule_result)

            # 2. Anomaly detection (if enabled)
            anomaly_result = await self.anomaly_detector.analyze_request(request_data)
            if anomaly_result["is_attack"] and anomaly_result["confidence_score"] > security_result["confidence_score"]:
                security_result.update(anomaly_result)

            # 3. Risk scoring
            if security_result["is_attack"]:
                risk_result = await self.risk_scorer.calculate_risk(
                    request_data, security_result
                )
                security_result["risk_score"] = risk_result["risk_score"]

            # Process the request
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Update request data with response info
            request_data.update({
                "response_status": response.status_code,
                "response_time": processing_time
            })

            # 4. Log the request
            log_entry = await self.log_service.log_request(
                request_data, security_result
            )

            # 5. Generate alerts if needed
            if security_result["is_attack"] and security_result["risk_score"] > 50:
                await self.alert_service.create_alert(
                    attack_type=security_result["attack_type"],
                    severity=security_result["severity"],
                    risk_score=security_result["risk_score"],
                    request_data=request_data
                )

            # 6. Stream live updates
            await self.live_stream.broadcast_attack_event(
                log_entry, security_result
            )

            return response

        except Exception as e:
            # Log security analysis errors but don't break the request
            print(f"Security analysis error: {str(e)}")
            response = await call_next(request)
            return response

    async def _extract_request_data(self, request: Request) -> dict:
        """
        Extract relevant data from the request for analysis.
        """
        # Get client IP (handle proxies)
        client_ip = self._get_client_ip(request)

        # Extract headers
        headers = dict(request.headers)

        # Extract body (limit size to prevent memory issues)
        body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if len(body_bytes) < 10000:  # 10KB limit
                    body = body_bytes.decode('utf-8', errors='ignore')
            except:
                body = "[binary or too large]"

        return {
            "ip_address": client_ip,
            "user_agent": headers.get("user-agent", ""),
            "method": request.method,
            "path": str(request.url.path),
            "query_string": str(request.url.query),
            "headers": headers,
            "body": body,
            "timestamp": time.time()
        }

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract real client IP, handling proxy headers.
        """
        # Check X-Forwarded-For header (most common)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # Take the first IP in the chain
            return x_forwarded_for.split(",")[0].strip()

        # Check X-Real-IP
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"