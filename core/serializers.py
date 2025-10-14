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
    is_subscribed = serializers.SerializerMethodField()
    subscription_id = serializers.SerializerMethodField()

    class Meta:
        model = ContentSource
        # 2. Explicitly list all fields, including the new one
        fields = [
            'id', 'name', 'type', 'feed_url', 'policy', 'is_active', 
            'created_at', 'get_type_display', 'get_policy_display', 
            'is_subscribed', 'subscription_id'
        ]

    # 3. Add the method to calculate the value for the 'is_subscribed' field
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if a Subscription object exists for this source and the current user
            return Subscription.objects.filter(source=obj, user=request.user).exists()
        return False
    
    def get_subscription_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            subscription = Subscription.objects.filter(source=obj, user=request.user).first()
            return subscription.id if subscription else None
        return None

class SubscriptionSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.type', read_only=True)
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user']

class DownloadItemSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = DownloadItem
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']