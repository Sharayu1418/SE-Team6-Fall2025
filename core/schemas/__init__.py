"""
Pydantic schemas for AutoGen agents.

These schemas mirror Django models and provide type-safe data exchange
between agents and the MCP service layer.
"""

from .data_models import (
    ContentSourceSchema,
    SubscriptionSchema,
    DownloadItemSchema,
    UserPreferenceSchema,
)

__all__ = [
    "ContentSourceSchema",
    "SubscriptionSchema",
    "DownloadItemSchema",
    "UserPreferenceSchema",
]




