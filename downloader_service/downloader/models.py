from django.db import models
import uuid

class DownloadedContent(models.Model):
    class DownloadType(models.TextChoices):
        VIDEO = 'VIDEO', 'Video'
        AUDIO = 'AUDIO', 'Audio'
        TEXT = 'TEXT', 'Text'

    class DownloadStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DOWNLOADING = 'DOWNLOADING', 'Downloading'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_url = models.URLField(max_length=1024)
 
    requested_type = models.CharField(
        max_length=20,
        choices=DownloadType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=DownloadStatus.choices,
        default=DownloadStatus.PENDING
    )
    content_file = models.FileField(upload_to='content/%Y/%m/%d/', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or str(self.id)