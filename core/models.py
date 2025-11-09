from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics = models.JSONField(default=list, help_text="List of preferred topics")
    max_daily_items = models.IntegerField(default=10)
    max_storage_mb = models.IntegerField(default=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} preferences"

class CommuteWindow(models.Model):
    DAYS_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, help_text="e.g., 'Morning Commute'")
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_week = models.JSONField(
        default=list,
        help_text="List of days like ['Mon', 'Tue', 'Wed']"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"

class ContentSource(models.Model):
    TYPE_CHOICES = [
        ('podcast', 'Podcast'),
        ('article', 'Article'),
    ]
    
    POLICY_CHOICES = [
        ('metadata_only', 'Metadata Only'),
        ('cache_allowed', 'Cache Allowed'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    feed_url = models.URLField()
    policy = models.CharField(
        max_length=20, 
        choices=POLICY_CHOICES, 
        default='metadata_only'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class ContentItem(models.Model):
    """
    Individual content item discovered from a source.
    This is what gets recommended and downloaded.
    """
    STORAGE_PROVIDER_CHOICES = [
        ('aws_s3', 'AWS S3'),
        ('supabase', 'Supabase Storage'),
        ('none', 'No Storage'),
    ]
    
    source = models.ForeignKey(ContentSource, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField()  # Original URL to the content
    
    # Media info
    media_url = models.URLField(null=True, blank=True)  # Direct audio/video URL
    duration_seconds = models.IntegerField(null=True, blank=True)
    file_size_mb = models.FloatField(null=True, blank=True)
    
    # Storage info
    storage_url = models.URLField(null=True, blank=True, help_text="URL to media in S3/Supabase storage")
    storage_provider = models.CharField(
        max_length=20,
        choices=STORAGE_PROVIDER_CHOICES,
        default='none',
        help_text="Storage provider used for this content"
    )
    file_size_bytes = models.BigIntegerField(null=True, blank=True, help_text="Actual file size in bytes")
    
    # Metadata
    published_at = models.DateTimeField()
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    # Quality/relevance scores (set by summarizer agent later)
    quality_score = models.FloatField(null=True, blank=True)
    topics = models.JSONField(default=list)  # Extracted topics
    
    # Prevent duplicates
    guid = models.CharField(max_length=500, unique=True)  # RSS GUID or hash
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['source', '-published_at']),
            models.Index(fields=['guid']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.source.name})"

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(ContentSource, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1, help_text="Higher number = higher priority")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'source']
    
    def __str__(self):
        return f"{self.user.username} -> {self.source.name}"

class DownloadItem(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('downloading', 'Downloading'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(ContentSource, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    original_url = models.URLField()
    media_url = models.URLField(null=True, blank=True)
    local_file_path = models.CharField(max_length=500, null=True, blank=True, help_text="Local path to downloaded file")
    file_size_bytes = models.BigIntegerField(null=True, blank=True, help_text="Size of downloaded file in bytes")
    error_message = models.TextField(null=True, blank=True, help_text="Error message if download failed")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    available_from = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

class EventLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('view', 'View'),
        ('play', 'Play'),
        ('finish', 'Finish'),
        ('save', 'Save'),
        ('skip', 'Skip'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(DownloadItem, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    duration_sec = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(default=dict, help_text="Additional context data")
    
    def __str__(self):
        return f"{self.user.username} - {self.event_type} - {self.item.title}"