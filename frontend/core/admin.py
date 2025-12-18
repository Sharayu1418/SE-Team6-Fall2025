from django.contrib import admin
from .models import (
    UserPreference, CommuteWindow, ContentSource, 
    Subscription, DownloadItem, EventLog
)

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'max_daily_items', 'max_storage_mb', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'user__email']

@admin.register(CommuteWindow)
class CommuteWindowAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'label']

@admin.register(ContentSource)
class ContentSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'policy', 'is_active', 'created_at']
    list_filter = ['type', 'policy', 'is_active']
    search_fields = ['name', 'feed_url']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'source', 'priority', 'is_active', 'created_at']
    list_filter = ['is_active', 'priority', 'source__type']
    search_fields = ['user__username', 'source__name']

@admin.register(DownloadItem)
class DownloadItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'source', 'status', 'available_from']
    list_filter = ['status', 'source__type', 'created_at']
    search_fields = ['title', 'user__username', 'source__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'item', 'duration_sec', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['user__username', 'item__title']
    readonly_fields = ['timestamp']