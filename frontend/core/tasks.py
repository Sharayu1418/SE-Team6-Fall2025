from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta, time
from django.db.models import CharField
from django.db.models.functions import Cast
import feedparser
import requests
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

            enclosure_url = None
            if entry.get('enclosures'):
                enclosure_url = entry.get('enclosures', [{}])[0].get('href')

            download_url = enclosure_url or link
            if not download_url:
                logger.debug(f"Skipping entry with no downloadable url for {source.name}: {entry}")
                continue

            download_type = 'AUDIO' if source.type == 'podcast' else 'TEXT'

            if source.policy != 'cache_allowed':
                # Respect policy: store metadata only, mark ready with available media URL if provided
                DownloadItem.objects.create(
                    user=user,
                    source=source,
                    title=title[:300],
                    original_url=link,
                    media_url=enclosure_url,
                    status='ready',
                    available_from=available_from,
                    metadata={
                        'origin': 'nightly_prepare_content',
                        'note': 'Metadata only - caching disabled for this source'
                    }
                )
                created_count += 1
                continue

            if _queue_download_task(
                user=user,
                source=source,
                title=title,
                download_url=download_url,
                original_link=link,
                download_type=download_type,
                available_from=available_from
            ):
                created_count += 1
    
    except Exception as e:
        logger.error(f"Error parsing feed {source.feed_url}: {e}")
    
    return created_count


def _queue_download_task(user, source, title, download_url, original_link, download_type, available_from):
    """Queue a download via the downloader service for automated scheduling."""
    downloader_endpoint = f"{settings.DOWNLOADER_SERVICE_URL}/api/download/"
    payload = {
        'url': download_url,
        'type': download_type
    }

    logger.info(f"Nightly scheduler queuing download for {user.username}: {download_url} ({download_type})")

    try:
        response = requests.post(downloader_endpoint, json=payload, timeout=15)
    except requests.RequestException as exc:
        logger.error(f"Downloader request failed for {download_url}: {exc}")
        DownloadItem.objects.create(
            user=user,
            source=source,
            title=title[:300] if title else None,
            original_url=original_link or download_url,
            download_type=download_type,
            status='failed',
            available_from=available_from,
            metadata={
                'origin': 'nightly_prepare_content',
                'error': str(exc)
            }
        )
        return False

    task_data = {}
    if response.status_code == 202:
        try:
            task_data = response.json()
        except ValueError:
            task_data = {}
        task_id = task_data.get('id')
        DownloadItem.objects.create(
            user=user,
            source=source,
            title=title[:300] if title else None,
            original_url=original_link or download_url,
            download_type=download_type,
            downloader_task_id=task_id,
            status='queued',
            available_from=available_from,
            metadata={
                'origin': 'nightly_prepare_content',
                'downloader_response': task_data
            }
        )
        return True

    # Non-202 response -> record failure for visibility
    error_detail = None
    try:
        error_payload = response.json()
        error_detail = error_payload.get('error') or str(error_payload)
    except ValueError:
        error_detail = response.text

    logger.error(
        "Downloader returned %s for %s: %s",
        response.status_code,
        download_url,
        error_detail[:200] if error_detail else 'Unknown error'
    )

    DownloadItem.objects.create(
        user=user,
        source=source,
        title=title[:300] if title else None,
        original_url=original_link or download_url,
        download_type=download_type,
        status='failed',
        available_from=available_from,
        metadata={
            'origin': 'nightly_prepare_content',
            'downloader_error': error_detail,
            'status_code': response.status_code
        }
    )
    return False

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

@shared_task
def poll_downloader_status():
    """
    Poll downloader service for status updates on pending/downloading items.
    Runs every few minutes to sync status from downloader service.
    """
    logger.info("Starting download status polling...")
    
    # Get items that are queued or downloading and have a downloader_task_id
    items_to_check = (
        DownloadItem.objects.annotate(
            task_id_str=Cast('downloader_task_id', CharField())
        )
        .filter(
            status__in=['queued', 'downloading'],
            task_id_str__isnull=False
        )
        .exclude(task_id_str='')
    )
    
    if not items_to_check.exists():
        logger.info("No items to poll")
        return {'checked': 0, 'updated': 0}
    
    updated_count = 0
    checked_count = 0
    downloader_url = settings.DOWNLOADER_SERVICE_URL
    
    for item in items_to_check:
        try:
            checked_count += 1
            # Try to get status from downloader service
            # Note: This assumes downloader service has GET /api/download/{task_id}/
            # If not implemented yet, this will fail gracefully
            status_url = f"{downloader_url}/api/download/{item.downloader_task_id}/"
            
            try:
                response = requests.get(status_url, timeout=5)
                
                if response.status_code == 200:
                    task_data = response.json()
                    
                    # Map downloader service status to frontend status
                    downloader_status = task_data.get('status', '').upper()
                    status_mapping = {
                        'PENDING': 'queued',
                        'DOWNLOADING': 'downloading',
                        'COMPLETED': 'ready',
                        'FAILED': 'failed'
                    }
                    
                    new_status = status_mapping.get(downloader_status, item.status)
                    
                    # Update item if status changed
                    if new_status != item.status:
                        item.status = new_status
                        item.title = task_data.get('title') or item.title
                        item.media_url = task_data.get('content_file') or item.media_url
                        if task_data.get('metadata'):
                            item.metadata.update(task_data.get('metadata', {}))
                        item.save()
                        updated_count += 1
                        logger.info(f"Updated DownloadItem {item.id} to status {new_status}")
                    
                elif response.status_code == 404:
                    # Task not found - might be deleted or invalid
                    logger.warning(f"Download task {item.downloader_task_id} not found in downloader service")
                    item.status = 'failed'
                    item.metadata.setdefault('errors', []).append('Task not found in downloader service')
                    item.save()
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error polling status for {item.downloader_task_id}: {e}")
                # Don't fail the entire task if one item fails
                continue
                
        except Exception as e:
            logger.error(f"Error processing DownloadItem {item.id}: {e}", exc_info=True)
            continue
    
    logger.info(f"Status polling complete: checked {checked_count}, updated {updated_count}")
    return {'checked': checked_count, 'updated': updated_count}