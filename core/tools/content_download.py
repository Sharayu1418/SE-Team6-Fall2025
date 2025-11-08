"""
Content download and processing tools.

These tools handle queuing, tracking, and processing content downloads.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from core.services.django_mcp import DjangoMCPService

logger = logging.getLogger(__name__)


def queue_download(
    user_id: int,
    content_item_id: int,
) -> str:
    """
    Queue a content item for download.
    
    This tool creates a new DownloadItem based on an existing ContentItem.
    The ContentItem ID is provided by the Discovery Agent's recommendations.
    
    Args:
        user_id: The user's ID.
        content_item_id: ID of the ContentItem to download (from recommendations).
        
    Returns:
        A confirmation message with the download item details and storage URL.
        
    Example:
        >>> queue_download(1, 42)
        "✓ Download queued successfully!
        
        Title: How AI is Changing Everything
        Source: TED Talks Daily
        Status: queued
        Download Item ID: 123
        Storage URL: https://s3.amazonaws.com/smartcache/podcasts/ted/abc123.mp3
        
        You can download this content from the storage URL above."
    """
    try:
        from core.models import ContentItem, DownloadItem
        from django.utils import timezone
        
        # Fetch the ContentItem
        try:
            content_item = ContentItem.objects.select_related('source').get(id=content_item_id)
        except ContentItem.DoesNotExist:
            return f"Error: Content item #{content_item_id} not found. Please check the Content ID."
        
        # Check if already queued or downloaded for this user
        existing = DownloadItem.objects.filter(
            user_id=user_id,
            original_url=content_item.url,
        ).first()
        
        if existing:
            return (
                f"This content is already in your download queue:\n\n"
                f"Title: {existing.title}\n"
                f"Status: {existing.status}\n"
                f"Download Item ID: {existing.id}\n"
                f"Media URL: {existing.media_url or 'Not available'}"
            )
        
        # Create DownloadItem
        download_item = DownloadItem.objects.create(
            user_id=user_id,
            source=content_item.source,
            title=content_item.title,
            original_url=content_item.url,
            media_url=content_item.storage_url or content_item.media_url,  # Prefer storage_url
            status='queued',
            available_from=timezone.now(),
        )
        
        result = (
            f"✓ Download queued successfully!\n\n"
            f"Title: {download_item.title}\n"
            f"Source: {content_item.source.name}\n"
            f"Status: {download_item.status}\n"
            f"Download Item ID: {download_item.id}\n"
        )
        
        # Add storage information
        if content_item.storage_url:
            result += (
                f"\n📦 Storage URL: {content_item.storage_url}\n"
                f"Provider: {content_item.storage_provider.upper()}\n"
            )
            
            if content_item.file_size_bytes:
                size_mb = content_item.file_size_bytes / (1024 * 1024)
                result += f"File Size: {size_mb:.2f} MB\n"
            
            result += "\n💾 You can download this content from the storage URL above."
            
        elif content_item.media_url:
            result += (
                f"\n📡 Original Media URL: {content_item.media_url}\n"
                f"Note: This content is not cached in storage. You'll download from the original source."
            )
        else:
            result += "\n⚠️ No media URL available for this content."
        
        return result
    
    except Exception as e:
        logger.error(f"Error queuing download: {e}")
        return f"Error queuing download: {str(e)}"


def check_download_status(item_id: int) -> str:
    """
    Check the status of a specific download item.
    
    This tool retrieves the current status and details of a download item.
    
    Args:
        item_id: The download item's ID.
        
    Returns:
        A formatted string with the download item's status and details.
        
    Example:
        >>> check_download_status(123)
        "Download Item #123:
        Title: Tech News Episode 42
        Status: ready
        Available: 2025-10-22 10:30:00
        Media URL: https://cdn.example.com/cached/123.mp3"
    """
    try:
        mcp = DjangoMCPService()
        
        # Get all items and filter (inefficient but works for now)
        # In production, would add get_download_item_by_id to MCP service
        items = mcp.get_download_items(user_id=1)  # TODO: Better filtering
        
        item = None
        for i in items:
            if i.id == item_id:
                item = i
                break
        
        if not item:
            return f"Download item #{item_id} not found."
        
        result = (
            f"Download Item #{item.id}:\n\n"
            f"Title: {item.title}\n"
            f"Source: {item.source_name}\n"
            f"Status: {item.status}\n"
            f"Original URL: {item.original_url}\n"
        )
        
        if item.media_url:
            result += f"Media URL: {item.media_url}\n"
        
        result += (
            f"\nAvailable from: {item.available_from.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Created: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Updated: {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error checking download status: {e}")
        return f"Error checking download status: {str(e)}"


def process_download_queue(user_id: int) -> str:
    """
    Process all queued downloads for a user.
    
    This tool retrieves all queued download items for a user and
    initiates the download process. Currently a stub that will be
    implemented with actual download logic in Sprint 2.
    
    Args:
        user_id: The user's ID.
        
    Returns:
        A summary of the download processing results.
        
    Example:
        >>> process_download_queue(1)
        "Processing download queue for user 1...
        Found 3 queued items:
        - Tech News Episode 42
        - TED Talk: Future of AI
        - Article: Python Best Practices
        
        [STUB] Download processing not yet implemented.
        Items remain in 'queued' status."
    """
    try:
        mcp = DjangoMCPService()
        
        # Get all queued items
        queued_items = mcp.get_download_items(user_id=user_id, status='queued')
        
        if not queued_items:
            return f"No queued downloads found for user {user_id}."
        
        result = (
            f"Processing download queue for user {user_id}...\n"
            f"Found {len(queued_items)} queued item(s):\n\n"
        )
        
        for item in queued_items:
            result += f"- {item.title} (ID: {item.id})\n"
        
        # TODO: Implement actual download logic in Sprint 2
        result += (
            f"\n[STUB] Download processing not yet implemented.\n"
            f"In Sprint 2, this will:\n"
            f"1. Fetch content from original URLs\n"
            f"2. Store/cache content appropriately\n"
            f"3. Update download status to 'ready'\n"
            f"4. Set media_url for cached content\n\n"
            f"For now, items remain in 'queued' status."
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing download queue: {e}")
        return f"Error processing download queue: {str(e)}"


def get_user_download_summary(user_id: int) -> str:
    """
    Get a summary of all downloads for a user, grouped by status.
    
    This tool provides an overview of a user's download items,
    showing counts and details for each status category.
    
    Args:
        user_id: The user's ID.
        
    Returns:
        A formatted summary of the user's downloads.
        
    Example:
        >>> get_user_download_summary(1)
        "Download Summary for User 1:
        
        Queued: 3 items
        Downloading: 1 item
        Ready: 15 items
        Failed: 0 items
        
        Total: 19 items"
    """
    try:
        mcp = DjangoMCPService()
        
        # Get all items
        all_items = mcp.get_download_items(user_id=user_id)
        
        if not all_items:
            return f"No downloads found for user {user_id}."
        
        # Count by status
        status_counts = {
            'queued': 0,
            'downloading': 0,
            'ready': 0,
            'failed': 0,
        }
        
        for item in all_items:
            if item.status in status_counts:
                status_counts[item.status] += 1
        
        result = (
            f"Download Summary for User {user_id}:\n\n"
            f"Queued: {status_counts['queued']} item(s)\n"
            f"Downloading: {status_counts['downloading']} item(s)\n"
            f"Ready: {status_counts['ready']} item(s)\n"
            f"Failed: {status_counts['failed']} item(s)\n\n"
            f"Total: {len(all_items)} item(s)"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting download summary: {e}")
        return f"Error getting download summary: {str(e)}"




