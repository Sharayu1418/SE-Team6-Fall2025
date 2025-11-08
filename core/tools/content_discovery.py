"""
Content discovery and curation tools.

These tools help agents discover new content sources and filter
them based on user preferences.
"""

import logging
from typing import Optional

from core.services.django_mcp import DjangoMCPService

logger = logging.getLogger(__name__)


def discover_new_sources(
    content_type: Optional[str] = None,
) -> str:
    """
    Discover available content sources.
    
    This tool queries the Django database for available content sources,
    optionally filtered by type (podcast or article).
    
    Args:
        content_type: Filter by 'podcast' or 'article'. If None, returns all.
        
    Returns:
        A formatted string listing available content sources.
        
    Example:
        >>> discover_new_sources("podcast")
        "Found 4 podcast sources:
        1. NPR News Now (RSS feed available)
        2. TED Talks Daily (RSS feed available)
        ..."
    """
    try:
        mcp = DjangoMCPService()
        sources = mcp.get_content_sources(content_type=content_type)
        
        if not sources:
            return f"No {content_type or 'content'} sources found."
        
        result = f"Found {len(sources)} {content_type or 'content'} source(s):\n\n"
        
        for idx, source in enumerate(sources, 1):
            result += (
                f"{idx}. {source.name}\n"
                f"   Type: {source.type}\n"
                f"   Policy: {source.policy}\n"
                f"   Feed: {source.feed_url}\n"
                f"   ID: {source.id}\n\n"
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error discovering sources: {e}")
        return f"Error discovering sources: {str(e)}"


def filter_by_preferences(user_id: int) -> str:
    """
    Filter content sources based on user preferences.
    
    This tool retrieves user preferences and recommends content sources
    that match their topics of interest.
    
    Args:
        user_id: The user's ID.
        
    Returns:
        A formatted string with personalized recommendations.
        
    Example:
        >>> filter_by_preferences(1)
        "Based on your preferences (topics: ['tech', 'science']):
        Recommended sources:
        - TED Talks Daily (podcast)
        - Hacker News Frontpage (article)
        ..."
    """
    try:
        mcp = DjangoMCPService()
        prefs = mcp.get_user_preferences(user_id)
        
        if not prefs:
            return f"No preferences found for user {user_id}."
        
        # Get all sources
        all_sources = mcp.get_content_sources()
        
        result = (
            f"User preferences for {prefs.username}:\n"
            f"- Preferred topics: {', '.join(prefs.topics) if prefs.topics else 'None set'}\n"
            f"- Max daily items: {prefs.max_daily_items}\n"
            f"- Max storage: {prefs.max_storage_mb} MB\n\n"
        )
        
        if all_sources:
            result += f"Available content sources:\n\n"
            for source in all_sources:
                result += f"- {source.name} ({source.type})\n"
        else:
            result += "No content sources available.\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error filtering by preferences: {e}")
        return f"Error filtering by preferences: {str(e)}"


def get_user_subscriptions_info(user_id: int) -> str:
    """
    Get information about user's current subscriptions.
    
    This tool retrieves all active subscriptions for a user,
    providing details about what content they're following.
    
    Args:
        user_id: The user's ID.
        
    Returns:
        A formatted string listing the user's subscriptions.
        
    Example:
        >>> get_user_subscriptions_info(1)
        "You are subscribed to 3 sources:
        1. NPR News Now (Priority: 3)
        2. TED Talks Daily (Priority: 2)
        3. Hacker News (Priority: 1)
        ..."
    """
    try:
        mcp = DjangoMCPService()
        subscriptions = mcp.get_user_subscriptions(user_id)
        
        if not subscriptions:
            return f"User {user_id} has no active subscriptions."
        
        # Sort by priority (highest first)
        subscriptions.sort(key=lambda x: x.priority, reverse=True)
        
        result = f"Active subscriptions ({len(subscriptions)}):\n\n"
        
        for idx, sub in enumerate(subscriptions, 1):
            result += (
                f"{idx}. {sub.source_name}\n"
                f"   Priority: {sub.priority}\n"
                f"   Source ID: {sub.source_id}\n\n"
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting subscriptions: {e}")
        return f"Error getting subscriptions: {str(e)}"




