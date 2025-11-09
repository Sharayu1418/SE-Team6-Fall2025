"""
Content recommendation tools for the Discovery Agent.

These tools query ContentItem and recommend items based on:
- User preferences (topics, max items)
- Subscription priority
- Quality scores (when available)
"""

import logging
from typing import List, Optional

from core.services.django_mcp import DjangoMCPService
from core.models import ContentItem, Subscription

logger = logging.getLogger(__name__)


def recommend_content_for_download(
    user_id: int,
    max_items: int = 10,
) -> str:
    """
    Recommend specific content items for download based on user preferences.
    
    This is the KEY tool that the Discovery Agent uses to generate
    personalized recommendations for the Download Agent.
    
    The recommendation algorithm:
    1. Get user's active subscriptions (ordered by priority)
    2. Fetch ContentItem records from those sources (ALL available, no time filter)
    3. Filter by user's preferred topics (keyword matching)
    4. Return top N items with Content IDs
    
    Args:
        user_id: User ID
        max_items: Max number of items to recommend (default: 10)
        
    Returns:
        Formatted string with recommended content items and their IDs.
        The Download Agent will parse this to queue downloads.
        
    Example output:
        "📋 Recommended 5 items for download:
        
        1. How AI is Changing Everything
           Source: TED Talks Daily
           Published: 2025-11-03 10:30
           Content ID: 42
           Storage: Available on S3
           URL: https://example.com/episode
        
        ...
        
        💡 Download Agent: Queue these Content IDs: [42, 43, 44, 45, 46]"
    """
    try:
        mcp = DjangoMCPService()
        prefs = mcp.get_user_preferences(user_id)
        
        if not prefs:
            return f"No preferences found for user {user_id}. Please set up preferences first."
        
        # Get user subscriptions (ordered by priority)
        subscriptions = Subscription.objects.filter(
            user_id=user_id,
            is_active=True,
            source__is_active=True
        ).select_related('source').order_by('-priority')
        
        if not subscriptions.exists():
            return (
                "No active subscriptions found. "
                "Please subscribe to some content sources first."
            )
        
        # Get source IDs
        source_ids = [sub.source_id for sub in subscriptions]
        
        # Fetch ContentItem records from subscribed sources that have storage_url
        # IMPORTANT: Only recommend items that are cached in S3/Supabase
        # This prevents downloading from original URLs that may be blocked (403)
        available_items = ContentItem.objects.filter(
            source_id__in=source_ids,
            storage_url__isnull=False,  # MUST have storage URL
        ).exclude(
            storage_url=''  # Exclude empty strings
        ).select_related('source').order_by('-published_at')[:100]  # Limit to 100 most recent
        
        if not available_items:
            return (
                "No cached content available from your subscribed sources yet.\n\n"
                "Content needs to be successfully downloaded and stored in S3/Supabase "
                "during the ETL pipeline before it can be recommended for download.\n\n"
                "Tip: Check the ETL logs for download errors (403 Forbidden, etc.)"
            )
        
        # Filter by user topics (simple keyword matching)
        recommended = []
        
        for item in available_items:
            # Check if any user topic appears in title or description
            matches_topic = False
            
            if prefs.topics:
                for topic in prefs.topics:
                    topic_lower = topic.lower()
                    if (topic_lower in item.title.lower() or
                        topic_lower in item.description.lower()):
                        matches_topic = True
                        break
            else:
                # No topic filter set, accept all
                matches_topic = True
            
            if matches_topic:
                recommended.append(item)
            
            if len(recommended) >= max_items:
                break
        
        # Format response for Download Agent
        if not recommended:
            return (
                f"No content matches your preferences (topics: {', '.join(prefs.topics) if prefs.topics else 'none set'}).\n"
                f"Try adjusting your topic preferences or subscribing to more sources."
            )
        
        # Build formatted response
        result = f"📋 Recommended {len(recommended)} items for download:\n\n"
        content_ids = []
        
        for idx, item in enumerate(recommended, 1):
            content_ids.append(item.id)
            
            # Storage status
            storage_status = "Not cached"
            if item.storage_url:
                storage_status = f"Available on {item.storage_provider.upper()}"
            elif item.media_url:
                storage_status = "Original URL available"
            
            result += (
                f"{idx}. {item.title}\n"
                f"   Source: {item.source.name}\n"
                f"   Published: {item.published_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"   Content ID: {item.id}\n"
                f"   Storage: {storage_status}\n"
            )
            
            if item.description:
                # Show first 100 chars of description
                desc_preview = item.description[:100] + ('...' if len(item.description) > 100 else '')
                result += f"   Description: {desc_preview}\n"
            
            result += "\n"
        
        # Add clear instruction for Download Agent
        result += (
            f"💡 Download Agent: To queue these items, call queue_download for each Content ID.\n"
            f"Content IDs to queue: {content_ids}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error recommending content: {e}")
        return f"Error generating recommendations: {str(e)}"


def get_content_item_details(content_item_id: int) -> str:
    """
    Get detailed information about a specific content item.
    
    Useful for agents to inspect a content item before recommending
    or queuing it for download.
    
    Args:
        content_item_id: ID of the ContentItem
        
    Returns:
        Formatted string with detailed content item information
    """
    try:
        item = ContentItem.objects.select_related('source').get(id=content_item_id)
        
        result = f"Content Item #{item.id}:\n\n"
        result += f"Title: {item.title}\n"
        result += f"Source: {item.source.name} ({item.source.type})\n"
        result += f"Published: {item.published_at.strftime('%Y-%m-%d %H:%M')}\n"
        result += f"Discovered: {item.discovered_at.strftime('%Y-%m-%d %H:%M')}\n"
        result += f"\nOriginal URL: {item.url}\n"
        
        if item.media_url:
            result += f"Media URL: {item.media_url}\n"
        
        if item.storage_url:
            result += f"Storage URL: {item.storage_url}\n"
            result += f"Storage Provider: {item.storage_provider}\n"
        
        if item.file_size_bytes:
            size_mb = item.file_size_bytes / (1024 * 1024)
            result += f"File Size: {size_mb:.2f} MB\n"
        
        if item.duration_seconds:
            duration_min = item.duration_seconds / 60
            result += f"Duration: {duration_min:.1f} minutes\n"
        
        if item.description:
            result += f"\nDescription:\n{item.description}\n"
        
        if item.topics:
            result += f"\nTopics: {', '.join(item.topics)}\n"
        
        if item.quality_score:
            result += f"Quality Score: {item.quality_score}\n"
        
        return result
    
    except ContentItem.DoesNotExist:
        return f"Content item #{content_item_id} not found."
    except Exception as e:
        logger.error(f"Error getting content item details: {e}")
        return f"Error: {str(e)}"

