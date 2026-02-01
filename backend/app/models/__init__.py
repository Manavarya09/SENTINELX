"""
Database models for SentinelX.
All models inherit from Base and include proper indexing.
"""

from .user import User
from .request import RequestLog
from .attack import Attack
from .ip_reputation import IPReputation
from .alert import Alert

__all__ = ["User", "RequestLog", "Attack", "IPReputation", "Alert"]