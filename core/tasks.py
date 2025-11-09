from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging
import requests
import os
from pathlib import Path
import re

from core.models import ContentSource, ContentItem, DownloadItem
from core.services.content_ingestion import ContentIngestionService

logger = logging.getLogger(__name__)


@shared_task
def ingest_content_sources():
    """
    Scheduled ETL task: Fetch content from all active sources.
    Runs every hour via Celery Beat.
    
    This task uses the ContentIngestionService to:
    1. Parse RSS feeds from all active ContentSource entries
    2. Download media files (if cache_allowed)
    3. Upload to S3/Supabase storage
    4. Create ContentItem records
    
    Returns:
        dict: Summary of ingestion results
    """
    logger.info("Starting scheduled content ingestion...")
    
    try:
        service = ContentIngestionService()
        results = service.ingest_all_sources()
        
        logger.info(f"ETL complete: {results}")
        return results
        
    except Exception as e:
        logger.error(f"ETL task failed: {e}")
        return {'error': str(e)}


@shared_task
def manual_ingest_source(source_id: int):
    """
    Manual trigger: Ingest a specific source on-demand.
    
    Useful for:
    - Testing new sources
    - Forcing refresh of a specific source
    - Demo purposes
    
    Args:
        source_id: ID of the ContentSource to ingest
        
    Returns:
        dict: Summary with source name and items added
    """
    logger.info(f"Manual ingestion triggered for source ID: {source_id}")
    
    try:
        source = ContentSource.objects.get(id=source_id)
        service = ContentIngestionService()
        count = service.ingest_source(source)
        
        result = {
            'source_id': source_id,
            'source': source.name,
            'items_added': count,
        }
        
        logger.info(f"Manual ingestion complete: {result}")
        return result
        
    except ContentSource.DoesNotExist:
        error_msg = f"ContentSource with ID {source_id} not found"
        logger.error(error_msg)
        return {'error': error_msg}
        
    except Exception as e:
        logger.error(f"Manual ingestion failed: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_old_content(days: int = 30):
    """
    Clean up old content items and download records.
    
    Removes:
    - ContentItem records older than specified days
    - DownloadItem records older than specified days (except 'ready' status)
    
    Args:
        days: Age threshold in days (default: 30)
        
    Returns:
        dict: Summary of cleanup operation
    """
    logger.info(f"Starting content cleanup (older than {days} days)...")
    
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Clean up old ContentItems
        content_items_deleted = ContentItem.objects.filter(
            discovered_at__lt=cutoff_date
        ).delete()[0]
        
        # Clean up old DownloadItems (except ready ones users might still use)
        download_items_deleted = DownloadItem.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(
            status='ready'
        ).delete()[0]
        
        result = {
            'cutoff_date': cutoff_date.isoformat(),
            'content_items_deleted': content_items_deleted,
            'download_items_deleted': download_items_deleted,
        }
        
        logger.info(f"Cleanup complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return {'error': str(e)}


@shared_task
def download_content_file(download_item_id: int):
    """
    Download a content file from S3/Supabase to local storage.
    
    This Celery task downloads media files from remote storage (S3/Supabase)
    to the local file system for offline access.
    
    Args:
        download_item_id: ID of the DownloadItem to download
        
    Returns:
        dict: Status dictionary with 'status', 'file_path', or 'error'
    """
    logger.info(f"Starting download for DownloadItem ID: {download_item_id}")
    
    try:
        # Get DownloadItem
        try:
            download_item = DownloadItem.objects.select_related('user', 'source').get(id=download_item_id)
        except DownloadItem.DoesNotExist:
            error_msg = f"DownloadItem {download_item_id} not found"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}
        
        # Validate media_url exists
        if not download_item.media_url:
            error_msg = (
                "No media URL available for download. "
                "Content was not cached in storage during ETL pipeline."
            )
            logger.error(f"{error_msg} for DownloadItem {download_item_id}")
            download_item.status = 'failed'
            download_item.error_message = error_msg
            download_item.save()
            return {'status': 'failed', 'error': error_msg}
        
        # Log whether we're downloading from storage or original source
        if 's3.amazonaws.com' in download_item.media_url or 'supabase' in download_item.media_url:
            logger.info(f"✓ Downloading from cached storage: {download_item.media_url[:100]}...")
        else:
            logger.warning(
                f"⚠️  Downloading from ORIGINAL source (not cached): {download_item.media_url[:100]}...\n"
                f"   This may fail if the source blocks downloads (403 Forbidden).\n"
                f"   Ideally, content should be cached in S3/Supabase during ETL."
            )
        
        # Update status to downloading
        download_item.status = 'downloading'
        download_item.save()
        logger.info(f"Status updated to 'downloading' for DownloadItem {download_item_id}")
        
        # Create download directory
        download_dir = getattr(settings, 'DOWNLOAD_DIR', settings.MEDIA_ROOT / 'downloads')
        user_dir = Path(download_dir) / f"user_{download_item.user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        # Clean title and add timestamp to avoid collisions
        safe_title = re.sub(r'[^\w\s-]', '', download_item.title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:100]  # Limit length
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        # Get file extension from URL or default to .mp3
        url_path = download_item.media_url.split('?')[0]  # Remove query params
        extension = os.path.splitext(url_path)[1] or '.mp3'
        
        filename = f"{safe_title}_{timestamp}{extension}"
        file_path = user_dir / filename
        
        # Download file with streaming (logging already done above)
        max_size_mb = getattr(settings, 'MAX_DOWNLOAD_SIZE_MB', 500)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        response = requests.get(download_item.media_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check content length
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > max_size_bytes:
            error_msg = f"File too large: {int(content_length) / (1024*1024):.1f}MB exceeds limit of {max_size_mb}MB"
            logger.error(error_msg)
            download_item.status = 'failed'
            download_item.error_message = error_msg
            download_item.save()
            return {'status': 'failed', 'error': error_msg}
        
        # Download in chunks
        chunk_size = 8192
        total_size = 0
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
                    
                    # Check size limit during download
                    if total_size > max_size_bytes:
                        error_msg = f"Download exceeded size limit of {max_size_mb}MB"
                        logger.error(error_msg)
                        os.remove(file_path)  # Clean up partial file
                        download_item.status = 'failed'
                        download_item.error_message = error_msg
                        download_item.save()
                        return {'status': 'failed', 'error': error_msg}
        
        # Update DownloadItem with success
        download_item.status = 'ready'
        download_item.local_file_path = str(file_path)
        download_item.file_size_bytes = total_size
        download_item.error_message = None
        download_item.save()
        
        logger.info(f"Download complete for DownloadItem {download_item_id}: {file_path} ({total_size / (1024*1024):.2f}MB)")
        
        return {
            'status': 'success',
            'file_path': str(file_path),
            'file_size_bytes': total_size,
            'download_item_id': download_item_id,
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Download failed: {str(e)}"
        logger.error(f"{error_msg} for DownloadItem {download_item_id}")
        try:
            download_item = DownloadItem.objects.get(id=download_item_id)
            download_item.status = 'failed'
            download_item.error_message = error_msg
            download_item.save()
        except:
            pass
        return {'status': 'failed', 'error': error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{error_msg} for DownloadItem {download_item_id}", exc_info=True)
        try:
            download_item = DownloadItem.objects.get(id=download_item_id)
            download_item.status = 'failed'
            download_item.error_message = error_msg
            download_item.save()
        except:
            pass
        return {'status': 'failed', 'error': error_msg}