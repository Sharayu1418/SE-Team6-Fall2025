"""
Pydantic data models that mirror Django models.

These schemas provide type-safe data validation and serialization
for communication between AutoGen agents and the Django MCP service layer.
"""

from datetime import datetime, time
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class UserPreferenceSchema(BaseModel):
    """User content preferences."""
    
    id: Optional[int] = None
    user_id: int
    username: str
    topics: List[str] = Field(default_factory=list)
    max_daily_items: int = 10
    max_storage_mb: int = 500
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentSourceSchema(BaseModel):
    """Content source (podcast or article feed)."""
    
    id: Optional[int] = None
    name: str
    type: Literal["podcast", "article"]
    feed_url: HttpUrl
    policy: Literal["metadata_only", "cache_allowed"] = "metadata_only"
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubscriptionSchema(BaseModel):
    """User subscription to a content source."""
    
    id: Optional[int] = None
    user_id: int
    source_id: int
    source_name: str
    priority: int = 1
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DownloadItemSchema(BaseModel):
    """Download item with status tracking."""
    
    id: Optional[int] = None
    user_id: int
    source_id: int
    source_name: str
    title: str
    original_url: HttpUrl
    media_url: Optional[HttpUrl] = None
    status: Literal["queued", "downloading", "ready", "failed"] = "queued"
    available_from: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CommuteWindowSchema(BaseModel):
    """User commute time window."""
    
    id: Optional[int] = None
    user_id: int
    label: str
    start_time: time
    end_time: time
    days_of_week: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True




