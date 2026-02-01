"""
Risk Scoring Engine
Calculates unified risk scores based on multiple factors.
Combines attack confidence, frequency, complexity, and IP reputation.
"""

from typing import Dict, Any
import time
from app.services.logs import LogService

class RiskScorer:
    """
    Calculates risk scores for detected attacks.
    Uses multiple factors to determine overall threat level.
    """

    def __init__(self):
        self.log_service = LogService()

    async def calculate_risk(self, request_data: Dict[str, Any],
                           security_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an attack.
        """
        base_score = security_result.get("confidence_score", 0) * 100  # Convert to 0-100 scale

        # Factor 1: Attack confidence
        confidence_multiplier = security_result.get("confidence_score", 0)

        # Factor 2: Attack frequency from this IP
        frequency_data = await self._get_attack_frequency(request_data["ip_address"])
        frequency_multiplier = min(frequency_data["recent_attacks"] / 10, 2.0)  # Cap at 2x

        # Factor 3: Payload complexity
        complexity_multiplier = self._calculate_complexity(request_data)

        # Factor 4: IP reputation
        reputation_data = await self._get_ip_reputation(request_data["ip_address"])
        reputation_multiplier = reputation_data.get("risk_multiplier", 1.0)

        # Factor 5: Attack type severity weight
        type_weight = self._get_attack_type_weight(security_result.get("attack_type", ""))

        # Calculate final risk score
        risk_score = (
            base_score *
            confidence_multiplier *
            frequency_multiplier *
            complexity_multiplier *
            reputation_multiplier *
            type_weight
        )

        # Cap at 100
        risk_score = min(risk_score, 100.0)

        return {
            "risk_score": risk_score,
            "factors": {
                "base_score": base_score,
                "confidence_multiplier": confidence_multiplier,
                "frequency_multiplier": frequency_multiplier,
                "complexity_multiplier": complexity_multiplier,
                "reputation_multiplier": reputation_multiplier,
                "type_weight": type_weight
            }
        }

    async def _get_attack_frequency(self, ip_address: str) -> Dict[str, Any]:
        """Get recent attack frequency for an IP."""
        # In production, query database for recent attacks
        # For now, return mock data
        return {
            "recent_attacks": 2,  # Mock: 2 recent attacks
            "time_window": 3600   # 1 hour
        }

    def _calculate_complexity(self, request_data: Dict[str, Any]) -> float:
        """Calculate payload complexity score."""
        text = self._combine_request_text(request_data)
        complexity = 1.0

        # Length factor
        if len(text) > 1000:
            complexity += 0.5
        elif len(text) > 500:
            complexity += 0.2

        # Special character density
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(text) if text else 0
        if special_ratio > 0.3:
            complexity += 0.3

        # Encoding attempts
        encoding_indicators = ["%20", "%3C", "%3E", "&#", "&lt;", "&gt;"]
        encoding_count = sum(1 for indicator in encoding_indicators if indicator in text)
        complexity += encoding_count * 0.1

        return min(complexity, 2.0)  # Cap at 2x

    async def _get_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Get IP reputation data."""
        # In production, query IP reputation database
        # For now, return neutral reputation
        return {
            "risk_multiplier": 1.0,
            "reputation_score": 50.0
        }

    def _get_attack_type_weight(self, attack_type: str) -> float:
        """Get severity weight for attack type."""
        weights = {
            "sqli": 1.5,      # SQL injection is very dangerous
            "xss": 1.3,       # XSS can lead to session hijacking
            "path_traversal": 1.4,  # Can expose sensitive files
            "command_injection": 1.6,  # Direct system access
            "brute_force": 1.1,     # Resource exhaustion
            "rate_abuse": 1.0,      # Performance impact
            "anomaly": 1.2         # Unknown threats
        }
        return weights.get(attack_type, 1.0)

    def _combine_request_text(self, request_data: Dict[str, Any]) -> str:
        """Combine request fields for analysis."""
        return " ".join([
            request_data.get("path", ""),
            request_data.get("query_string", ""),
            request_data.get("body", "")
        ])