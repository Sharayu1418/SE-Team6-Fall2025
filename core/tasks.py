from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, time
import feedparser
import logging
from .models import (
    CommuteWindow, Subscription, ContentSource, DownloadItem
)

logger = logging.getLogger(__name__)

@shared_task
def nightly_prepare_content():
    """
    Nightly task to prepare content for users based on their commute windows
    and subscriptions. This is a stub implementation for Sprint-1.
    """
    logger.info("Starting nightly content preparation...")
    
    processed_users = 0
    created_items = 0
    
    # Get all users with active commute windows
    users_with_commutes = User.objects.filter(
        commutewindow__is_active=True
    ).distinct()
    
    for user in users_with_commutes:
        try:
            # Get user's active subscriptions
            subscriptions = Subscription.objects.filter(
                user=user, 
                is_active=True,
                source__is_active=True
            ).select_related('source')
            
            if not subscriptions.exists():
                continue
            
            # Get user's commute windows for tomorrow
            tomorrow = timezone.now().date() + timedelta(days=1)
            day_name = tomorrow.strftime('%a')  # Mon, Tue, etc.
            
            commute_windows = CommuteWindow.objects.filter(
                user=user,
                is_active=True,
                days_of_week__contains=day_name
            )
            
            if not commute_windows.exists():
                continue
            
            # Set availability time to 8 AM tomorrow (simulated)
            available_from = timezone.make_aware(
                datetime.combine(tomorrow, time(8, 0))
            )
            
            # Process each subscription
            for subscription in subscriptions:
                try:
                    items_created = _process_content_source(
                        user, subscription.source, available_from
                    )
                    created_items += items_created
                except Exception as e:
                    logger.error(f"Error processing {subscription.source.name}: {e}")
            
            processed_users += 1
            
        except Exception as e:
            logger.error(f"Error processing user {user.username}: {e}")
    
    logger.info(f"Nightly preparation complete: {processed_users} users, {created_items} items created")
    return {'processed_users': processed_users, 'created_items': created_items}

def _process_content_source(user, source, available_from):
    """
    Process a single content source for a user.
    For Sprint-1, this creates placeholder items based on RSS feed parsing.
    """
    created_count = 0
    
    try:
        # Parse RSS feed
        feed = feedparser.parse(source.feed_url)
        
        # Process up to 5 latest items
        for entry in feed.entries[:5]:
            title = entry.get('title', 'Untitled')
            link = entry.get('link', '')
            
            # Skip if we already have this item
            if DownloadItem.objects.filter(
                user=user, 
                source=source, 
                original_url=link
            ).exists():
                continue
            
            # Create download item
            DownloadItem.objects.create(
                user=user,
                source=source,
                title=title[:300],  # Truncate to fit field
                original_url=link,
                media_url=entry.get('enclosures', [{}])[0].get('href') if entry.get('enclosures') else None,
                status='ready',  # Simulated ready state for Sprint-1
                available_from=available_from
            )
            created_count += 1
    
    except Exception as e:
        logger.error(f"Error parsing feed {source.feed_url}: {e}")
    
    return created_count

@shared_task
def cleanup_old_content():
    """
    Clean up old content items.
    Placeholder task for Sprint-1.
    """
    logger.info("Starting content cleanup...")
    
    # For now, just log - no actual cleanup in Sprint-1
    cutoff_date = timezone.now() - timedelta(days=30)
    old_items_count = DownloadItem.objects.filter(
        created_at__lt=cutoff_date
    ).count()
    
    logger.info(f"Found {old_items_count} items older than 30 days (not deleted in Sprint-1)")
    
    return {'old_items_found': old_items_count, 'deleted': 0}