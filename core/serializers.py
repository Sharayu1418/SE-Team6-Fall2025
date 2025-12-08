from rest_framework import serializers
from .models import (
    UserPreference, CommuteWindow, ContentSource, 
    Subscription, DownloadItem
)

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'
        read_only_fields = ['user']

class CommuteWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommuteWindow
        fields = '__all__'
        read_only_fields = ['user']

class ContentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentSource
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user']

class DownloadItemSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    
    class Meta:
        model = DownloadItem
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']