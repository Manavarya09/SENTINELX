"""
Rule Engine for Attack Detection
Implements pattern-based detection for common web attacks.
Each rule returns confidence score and explanation.
"""

import re
from typing import Dict, Any, List
from app.config import settings

class RuleEngine:
    """
    Rule-based attack detection engine.
    Analyzes requests against known attack patterns.
    """

    def __init__(self):
        self.rules = {
            "sqli": self._detect_sqli,
            "xss": self._detect_xss,
            "path_traversal": self._detect_path_traversal,
            "command_injection": self._detect_command_injection,
            "rate_abuse": self._detect_rate_abuse
        }

    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze request against all detection rules.
        Returns the highest confidence attack detection.
        """
        max_confidence = 0.0
        best_result = {
            "is_attack": False,
            "attack_type": None,
            "confidence_score": 0.0,
            "severity": "low",
            "explanation": ""
        }

        for attack_type, rule_func in self.rules.items():
            result = await rule_func(request_data)
            if result["confidence_score"] > max_confidence:
                max_confidence = result["confidence_score"]
                best_result = result

        return best_result

    async def _detect_sqli(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect SQL Injection attacks.
        Looks for SQL keywords, patterns, and entropy analysis.
        """
        text_to_analyze = self._combine_request_text(request_data)
        confidence = 0.0
        reasons = []

        # Check for SQL keywords
        sql_keywords = settings.sql_injection_keywords
        found_keywords = []
        for keyword in sql_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_analyze, re.IGNORECASE):
                found_keywords.append(keyword)
                confidence += 0.2

        if found_keywords:
            reasons.append(f"Found SQL keywords: {', '.join(found_keywords)}")

        # Check for SQL patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(FROM|INTO|TABLE|WHERE)\b)",
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bOR\b.*\d+\s*=\s*\d+)",
            r"(\bAND\b.*\d+\s*=\s*\d+)",
            r"(--|#|/\*|\*/)",  # Comments
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text_to_analyze, re.IGNORECASE):
                confidence += 0.3
                reasons.append(f"Matched SQL pattern: {pattern}")

        # Entropy analysis (high entropy may indicate encoded attacks)
        entropy = self._calculate_entropy(text_to_analyze)
        if entropy > 4.5:  # High entropy threshold
            confidence += 0.2
            reasons.append(".2f")

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        severity = self._calculate_severity(confidence, "sqli")

        return {
            "is_attack": confidence > 0.3,
            "attack_type": "sqli",
            "confidence_score": confidence,
            "severity": severity,
            "explanation": "; ".join(reasons) if reasons else "No SQL injection patterns detected"
        }

    async def _detect_xss(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Cross-Site Scripting attacks.
        Looks for script tags, JavaScript events, and HTML injection.
        """
        text_to_analyze = self._combine_request_text(request_data)
        confidence = 0.0
        reasons = []

        # Check for XSS patterns
        xss_patterns = settings.xss_patterns + [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"eval\s*\(",
            r"document\.cookie",
            r"document\.write",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, text_to_analyze, re.IGNORECASE):
                confidence += 0.25
                reasons.append(f"Matched XSS pattern: {pattern}")

        # Check for HTML entities that might be evasion attempts
        html_entities = ["&lt;", "&gt;", "&amp;", "&#x", "&#"]
        entity_count = sum(1 for entity in html_entities if entity in text_to_analyze)
        if entity_count > 2:
            confidence += 0.1
            reasons.append(f"Found {entity_count} HTML entities (possible evasion)")

        confidence = min(confidence, 1.0)
        severity = self._calculate_severity(confidence, "xss")

        return {
            "is_attack": confidence > 0.2,
            "attack_type": "xss",
            "confidence_score": confidence,
            "severity": severity,
            "explanation": "; ".join(reasons) if reasons else "No XSS patterns detected"
        }

    async def _detect_path_traversal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Path Traversal attacks.
        Looks for ../ patterns and attempts to access sensitive files.
        """
        path = request_data.get("path", "")
        query = request_data.get("query_string", "")
        text_to_analyze = path + query

        confidence = 0.0
        reasons = []

        # Check for traversal patterns
        traversal_patterns = [
            r"\.\./",  # Directory traversal
            r"\.\.\\",  # Windows traversal
            r"%2e%2e%2f",  # URL encoded ../
            r"%2e%2e/",  # Mixed encoding
            r"\.\.%2f",  # Mixed encoding
        ]

        for pattern in traversal_patterns:
            if re.search(pattern, text_to_analyze):
                confidence += 0.4
                reasons.append(f"Found path traversal pattern: {pattern}")

        # Check for sensitive file access attempts
        sensitive_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/proc/self/environ",
            "/windows/system32",
            "web.config",
            ".htaccess",
            ".env",
            "config.php",
            "application.yml"
        ]

        for sensitive_file in sensitive_files:
            if sensitive_file.lower() in text_to_analyze.lower():
                confidence += 0.5
                reasons.append(f"Attempted access to sensitive file: {sensitive_file}")

        confidence = min(confidence, 1.0)
        severity = self._calculate_severity(confidence, "path_traversal")

        return {
            "is_attack": confidence > 0.3,
            "attack_type": "path_traversal",
            "confidence_score": confidence,
            "severity": severity,
            "explanation": "; ".join(reasons) if reasons else "No path traversal patterns detected"
        }

    async def _detect_command_injection(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Command Injection attacks.
        Looks for shell metacharacters and command chaining.
        """
        text_to_analyze = self._combine_request_text(request_data)
        confidence = 0.0
        reasons = []

        # Command injection patterns
        cmd_patterns = [
            r"[;&|`$()<>]",  # Shell metacharacters
            r"\b(cmd|bash|sh|powershell|exec)\b",
            r"\b(system|shell_exec|passthru|proc_open)\b",
            r"(\|\||&&)",  # Command chaining
            r"\b(cat|ls|dir|whoami|netstat|ps)\b.*\|",  # Piping to system commands
        ]

        for pattern in cmd_patterns:
            if re.search(pattern, text_to_analyze, re.IGNORECASE):
                confidence += 0.3
                reasons.append(f"Matched command injection pattern: {pattern}")

        confidence = min(confidence, 1.0)
        severity = self._calculate_severity(confidence, "command_injection")

        return {
            "is_attack": confidence > 0.4,
            "attack_type": "command_injection",
            "confidence_score": confidence,
            "severity": severity,
            "explanation": "; ".join(reasons) if reasons else "No command injection patterns detected"
        }

    async def _detect_rate_abuse(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Rate Abuse (handled by rate limiter, this is a placeholder).
        Rate limiting is implemented at the middleware level with Redis.
        """
        # This would be integrated with Redis-based rate limiting
        # For now, return no detection (handled elsewhere)
        return {
            "is_attack": False,
            "attack_type": "rate_abuse",
            "confidence_score": 0.0,
            "severity": "low",
            "explanation": "Rate limiting handled by Redis counter"
        }

    def _combine_request_text(self, request_data: Dict[str, Any]) -> str:
        """Combine relevant request fields for analysis."""
        return " ".join([
            request_data.get("path", ""),
            request_data.get("query_string", ""),
            request_data.get("body", ""),
            str(request_data.get("headers", ""))
        ])

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0

        entropy = 0.0
        text_length = len(text)

        for char in set(text):
            p = text.count(char) / text_length
            if p > 0:
                entropy -= p * (p ** 0.5)  # Simplified entropy calculation

        return entropy

    def _calculate_severity(self, confidence: float, attack_type: str) -> str:
        """Calculate severity level based on confidence and attack type."""
        if confidence > 0.8:
            return "critical"
        elif confidence > 0.6:
            return "high"
        elif confidence > 0.4:
            return "medium"
        else:
            return "low"