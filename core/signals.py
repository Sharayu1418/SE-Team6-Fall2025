"""
Django signals for automatic processing.

This module provides signals that automatically trigger actions when
certain model events occur (e.g., auto-processing download queues).
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from core.models import DownloadItem

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DownloadItem)
def auto_process_download_queue(sender, instance, created, **kwargs):
    """
    Automatically process download queue when a new DownloadItem is created.
    
    This signal triggers background download tasks when items are queued,
    eliminating the need to manually call process_download_queue().
    
    Note: This can be disabled by setting AUTO_PROCESS_DOWNLOADS=False in settings.
    """
    # Only process newly created items with 'queued' status
    if not created or instance.status != 'queued':
        return
    
    # Check if auto-processing is enabled (default: True)
    auto_process = getattr(settings, 'AUTO_PROCESS_DOWNLOADS', True)
    if not auto_process:
        logger.debug(f"Auto-processing disabled for DownloadItem {instance.id}")
        return
    
    try:
        from core.tasks import download_content_file
        
        # Trigger Celery task for this download item
        task = download_content_file.delay(instance.id)
        
        logger.info(
            f"Auto-processed download queue: "
            f"DownloadItem {instance.id} → Celery task {task.id}"
        )
        
    except Exception as e:
        logger.error(
            f"Error auto-processing download queue for DownloadItem {instance.id}: {e}",
            exc_info=True
        )

