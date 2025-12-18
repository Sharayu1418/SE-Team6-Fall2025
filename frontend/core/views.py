from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    UserPreference, CommuteWindow, ContentSource, 
    Subscription, DownloadItem
)
from .serializers import (
    UserPreferenceSerializer, CommuteWindowSerializer,
    ContentSourceSerializer, SubscriptionSerializer, DownloadItemSerializer
)

# Template Views
def index(request):
    """Dashboard/Index page"""
    context = {
        'title': 'SmartCache AI - Intelligent Offline Content Curator',
        'focus': 'Initial Focus: Subway Riders',
    }
    
    if request.user.is_authenticated:
        context.update({
            'commute_count': CommuteWindow.objects.filter(user=request.user).count(),
            'subscription_count': Subscription.objects.filter(user=request.user).count(),
            'download_count': DownloadItem.objects.filter(user=request.user).count(),
        })
    
    return render(request, 'index.html', context)

@login_required
def commutes(request):
    """Commute windows management"""
    user_commutes = CommuteWindow.objects.filter(user=request.user)
    return render(request, 'commutes.html', {'commutes': user_commutes})

@login_required
def sources(request):
    """Content sources and subscription management"""
    available_sources = ContentSource.objects.filter(is_active=True)
    user_subscriptions = Subscription.objects.filter(user=request.user).values_list('source_id', flat=True)
    
    return render(request, 'sources.html', {
        'sources': available_sources,
        'subscribed_ids': list(user_subscriptions)
    })

@login_required
def downloads(request):
    """Downloads listing"""
    user_downloads = DownloadItem.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'downloads.html', {'downloads': user_downloads})

# HTMX Views for dynamic interactions
@login_required
@require_http_methods(["POST"])
def toggle_subscription(request, source_id):
    """Toggle subscription via HTMX"""
    source = get_object_or_404(ContentSource, id=source_id)
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        source=source,
        defaults={'priority': 1}
    )
    
    if not created:
        subscription.delete()
        action = 'unsubscribed'
    else:
        action = 'subscribed'
    
    return JsonResponse({
        'action': action,
        'source_name': source.name
    })

# API ViewSets
class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommuteWindowViewSet(viewsets.ModelViewSet):
    serializer_class = CommuteWindowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CommuteWindow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContentSourceViewSet(viewsets.ModelViewSet):
    queryset = ContentSource.objects.filter(is_active=True)
    serializer_class = ContentSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DownloadItemViewSet(viewsets.ModelViewSet):
    serializer_class = DownloadItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DownloadItem.objects.filter(user=self.request.user)