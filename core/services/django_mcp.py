"""
Django Model Context Protocol (MCP) Service.

This service provides a clean abstraction layer between AutoGen agents
and Django models. It's the ONLY module that should import Django models
directly, following the Dependency Inversion Principle.
"""

import logging
from typing import List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q

from core.models import (
    UserPreference,
    ContentSource,
    Subscription,
    DownloadItem,
    CommuteWindow,
)
from core.schemas.data_models import (
    UserPreferenceSchema,
    ContentSourceSchema,
    SubscriptionSchema,
    DownloadItemSchema,
    CommuteWindowSchema,
)

logger = logging.getLogger(__name__)


class DjangoMCPService:
    """
    MCP-style service for accessing Django models.
    
    This service converts Django ORM objects to Pydantic schemas,
    providing type-safe data access for AutoGen agents.
    """
    
    @staticmethod
    def get_user_preferences(user_id: int) -> Optional[UserPreferenceSchema]:
        """
        Get user preferences by user ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            UserPreferenceSchema if found, None otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            prefs, created = UserPreference.objects.get_or_create(user=user)
            
            return UserPreferenceSchema(
                id=prefs.id,
                user_id=user.id,
                username=user.username,
                topics=prefs.topics,
                max_daily_items=prefs.max_daily_items,
                max_storage_mb=prefs.max_storage_mb,
                created_at=prefs.created_at,
                updated_at=prefs.updated_at,
            )
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching preferences for user {user_id}: {e}")
            return None
    
    @staticmethod
    def get_content_sources(
        content_type: Optional[str] = None,
        is_active: bool = True,
    ) -> List[ContentSourceSchema]:
        """
        Get all content sources, optionally filtered by type.
        
        Args:
            content_type: Filter by 'podcast' or 'article' (None for all)
            is_active: Only return active sources
            
        Returns:
            List of ContentSourceSchema objects
        """
        try:
            queryset = ContentSource.objects.filter(is_active=is_active)
            
            if content_type:
                queryset = queryset.filter(type=content_type)
            
            sources = []
            for source in queryset:
                sources.append(ContentSourceSchema(
                    id=source.id,
                    name=source.name,
                    type=source.type,
                    feed_url=str(source.feed_url),
                    policy=source.policy,
                    is_active=source.is_active,
                    created_at=source.created_at,
                ))
            
            return sources
        except Exception as e:
            logger.error(f"Error fetching content sources: {e}")
            return []
    
    @staticmethod
    def get_user_subscriptions(user_id: int) -> List[SubscriptionSchema]:
        """
        Get all subscriptions for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of SubscriptionSchema objects
        """
        try:
            subscriptions = Subscription.objects.filter(
                user_id=user_id,
                is_active=True,
            ).select_related('source')
            
            results = []
            for sub in subscriptions:
                results.append(SubscriptionSchema(
                    id=sub.id,
                    user_id=sub.user_id,
                    source_id=sub.source_id,
                    source_name=sub.source.name,
                    priority=sub.priority,
                    is_active=sub.is_active,
                    created_at=sub.created_at,
                ))
            
            return results
        except Exception as e:
            logger.error(f"Error fetching subscriptions for user {user_id}: {e}")
            return []
    
    @staticmethod
    def create_download_item(
        user_id: int,
        source_id: int,
        title: str,
        original_url: str,
        available_from: datetime,
        description: str = None,
    ) -> Optional[DownloadItemSchema]:
        """
        Create a new download item.
        
        Args:
            user_id: The user's ID
            source_id: The content source ID
            title: Item title
            original_url: Original content URL
            available_from: When the content should be available
            description: Optional content description/summary
            
        Returns:
            DownloadItemSchema if created successfully, None otherwise
        """
        try:
            source = ContentSource.objects.get(id=source_id)
            user = User.objects.get(id=user_id)
            
            item = DownloadItem.objects.create(
                user=user,
                source=source,
                title=title,
                description=description,
                original_url=original_url,
                status='queued',
                available_from=available_from,
            )
            
            return DownloadItemSchema(
                id=item.id,
                user_id=item.user_id,
                source_id=item.source_id,
                source_name=source.name,
                title=item.title,
                original_url=str(item.original_url),
                media_url=str(item.media_url) if item.media_url else None,
                status=item.status,
                available_from=item.available_from,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        except (User.DoesNotExist, ContentSource.DoesNotExist) as e:
            logger.error(f"User or source not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating download item: {e}")
            return None
    
    @staticmethod
    def update_download_status(
        item_id: int,
        status: str,
        media_url: Optional[str] = None,
    ) -> bool:
        """
        Update download item status.
        
        Args:
            item_id: The download item ID
            status: New status (queued, downloading, ready, failed)
            media_url: Optional media URL if status is 'ready'
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            item = DownloadItem.objects.get(id=item_id)
            item.status = status
            
            if media_url:
                item.media_url = media_url
            
            item.save()
            logger.info(f"Updated download item {item_id} to status {status}")
            return True
        except DownloadItem.DoesNotExist:
            logger.error(f"Download item {item_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating download item {item_id}: {e}")
            return False
    
    @staticmethod
    def get_download_items(
        user_id: int,
        status: Optional[str] = None,
    ) -> List[DownloadItemSchema]:
        """
        Get download items for a user, optionally filtered by status.
        
        Args:
            user_id: The user's ID
            status: Optional status filter
            
        Returns:
            List of DownloadItemSchema objects
        """
        try:
            queryset = DownloadItem.objects.filter(
                user_id=user_id
            ).select_related('source')
            
            if status:
                queryset = queryset.filter(status=status)
            
            results = []
            for item in queryset:
                results.append(DownloadItemSchema(
                    id=item.id,
                    user_id=item.user_id,
                    source_id=item.source_id,
                    source_name=item.source.name,
                    title=item.title,
                    original_url=str(item.original_url),
                    media_url=str(item.media_url) if item.media_url else None,
                    status=item.status,
                    available_from=item.available_from,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                ))
            
            return results
        except Exception as e:
            logger.error(f"Error fetching download items for user {user_id}: {e}")
            return []
    
    @staticmethod
    def get_user_commute_windows(user_id: int) -> List[CommuteWindowSchema]:
        """
        Get all commute windows for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of CommuteWindowSchema objects
        """
        try:
            windows = CommuteWindow.objects.filter(
                user_id=user_id,
                is_active=True,
            )
            
            results = []
            for window in windows:
                results.append(CommuteWindowSchema(
                    id=window.id,
                    user_id=window.user_id,
                    label=window.label,
                    start_time=window.start_time,
                    end_time=window.end_time,
                    days_of_week=window.days_of_week,
                    is_active=window.is_active,
                    created_at=window.created_at,
                ))
            
            return results
        except Exception as e:
            logger.error(f"Error fetching commute windows for user {user_id}: {e}")
            return []




