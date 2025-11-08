from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

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