"""
Anomaly Detection Engine
Uses machine learning to detect unusual request patterns.
Currently implements basic statistical anomaly detection.
Can be extended with Isolation Forest or other ML models.
"""

from typing import Dict, Any
import statistics
from collections import defaultdict
import time

class AnomalyDetector:
    """
    Anomaly detection using statistical methods.
    Can be extended with ML models like Isolation Forest.
    """

    def __init__(self):
        # In-memory storage for baseline (in production, use Redis/database)
        self.baseline_stats = defaultdict(lambda: {
            "request_count": 0,
            "avg_response_time": 0,
            "path_frequency": defaultdict(int),
            "ip_frequency": defaultdict(int),
            "last_updated": time.time()
        })

    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze request for anomalies using statistical methods.
        """
        # For now, implement basic anomaly detection
        # In production, this would use trained ML models

        anomaly_score = 0.0
        reasons = []

        # Check for unusual request patterns
        path = request_data.get("path", "")
        ip = request_data.get("ip_address", "")

        # Simple frequency analysis
        current_time = time.time()
        time_window = 300  # 5 minutes

        # Track path frequency
        path_count = self.baseline_stats[path]["path_frequency"][ip]
        if path_count > 10:  # Threshold for suspicious frequency
            anomaly_score += 0.3
            reasons.append(f"Unusual request frequency from IP {ip} to path {path}")

        # Track IP activity
        ip_activity = sum(self.baseline_stats[p]["path_frequency"][ip]
                         for p in self.baseline_stats.keys())
        if ip_activity > 50:  # High activity threshold
            anomaly_score += 0.4
            reasons.append(f"High activity from IP {ip} ({ip_activity} requests)")

        # Update baseline (sliding window)
        self._update_baseline(request_data)

        confidence = min(anomaly_score, 1.0)
        severity = "medium" if confidence > 0.5 else "low"

        return {
            "is_attack": confidence > 0.6,
            "attack_type": "anomaly",
            "confidence_score": confidence,
            "severity": severity,
            "explanation": "; ".join(reasons) if reasons else "No anomalies detected"
        }

    def _update_baseline(self, request_data: Dict[str, Any]):
        """Update baseline statistics with new request data."""
        path = request_data.get("path", "")
        ip = request_data.get("ip_address", "")

        stats = self.baseline_stats[path]
        stats["request_count"] += 1
        stats["path_frequency"][ip] += 1
        stats["last_updated"] = time.time()

        # Clean old entries (simple cleanup)
        current_time = time.time()
        for p in list(self.baseline_stats.keys()):
            if current_time - self.baseline_stats[p]["last_updated"] > 3600:  # 1 hour
                del self.baseline_stats[p]