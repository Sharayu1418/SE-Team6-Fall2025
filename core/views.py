from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, login as django_login, logout as django_logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from asgiref.sync import sync_to_async
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import os
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
    pagination_class = None  # Disable pagination - each user has only one preference
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Check if user already has preferences
        if UserPreference.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("Preferences already exist. Use PATCH to update.")
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
    
    def get_permissions(self):
        """
        Allow unauthenticated users to list and retrieve sources (for registration page).
        Only authenticated users can create/update/delete sources.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

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


# New API Endpoints for React Frontend

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Endpoint to get CSRF cookie.
    Frontend should call this on app load to ensure CSRF cookie is set.
    """
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user with preferences and subscriptions.
    
    Expected payload:
    {
        "username": "string (required)",
        "password": "string (required)",
        "email": "string (optional)",
        "preferences": {
            "topics": ["string"],
            "max_daily_items": int,
            "max_storage_mb": int
        },
        "subscriptions": [int] (optional, array of source IDs)
    }
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        preferences_data = request.data.get('preferences', {})
        subscription_ids = request.data.get('subscriptions', [])
        
        # Validation
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user, preferences, and subscriptions atomically
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            
            # Create user preferences
            UserPreference.objects.create(
                user=user,
                topics=preferences_data.get('topics', []),
                max_daily_items=preferences_data.get('max_daily_items', 10),
                max_storage_mb=preferences_data.get('max_storage_mb', 500)
            )
            
            # Create subscriptions if any sources were selected
            if subscription_ids:
                subscriptions_to_create = []
                for source_id in subscription_ids:
                    try:
                        source = ContentSource.objects.get(id=source_id, is_active=True)
                        subscriptions_to_create.append(
                            Subscription(user=user, source=source, priority=1)
                        )
                    except ContentSource.DoesNotExist:
                        # Skip invalid source IDs
                        pass
                
                if subscriptions_to_create:
                    Subscription.objects.bulk_create(subscriptions_to_create)
        
        # Auto-login the user (handle both sync and async contexts)
        try:
            # Try sync login first
            django_login(request, user)
        except RuntimeError:
            # If in async context, skip auto-login
            # Frontend will need to login separately
            pass
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'subscriptions_created': len(subscription_ids),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_user(request):
    """
    Login a user with username and password.
    
    GET: Returns CSRF cookie for the frontend.
    POST: Performs login.
    
    Expected payload (POST):
    {
        "username": "string (required)",
        "password": "string (required)"
    }
    
    Returns:
    {
        "id": int,
        "username": "string",
        "email": "string",
        "message": "Login successful"
    }
    """
    # GET request just sets CSRF cookie
    if request.method == 'GET':
        return Response({'csrf': 'cookie set'})
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Login the user (creates session)
    django_login(request, user)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'message': 'Login successful'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout the current user.
    
    Returns:
    {
        "message": "Logout successful"
    }
    """
    django_logout(request)
    
    return Response({
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def current_user(request):
    """
    Get current authenticated user with preferences and stats.
    
    Also ensures the CSRF cookie is set for the frontend.
    
    Returns:
    {
        "id": int,
        "username": "string",
        "email": "string",
        "preferences": {
            "id": int,
            "topics": ["string"],
            "max_daily_items": int,
            "max_storage_mb": int
        },
        "stats": {
            "subscriptions": int,
            "downloads": int
        }
    }
    """
    user = request.user
    
    try:
        preferences = UserPreference.objects.get(user=user)
        preferences_data = {
            'id': preferences.id,
            'topics': preferences.topics,
            'max_daily_items': preferences.max_daily_items,
            'max_storage_mb': preferences.max_storage_mb
        }
    except UserPreference.DoesNotExist:
        preferences_data = None
    
    subscriptions_count = Subscription.objects.filter(user=user, is_active=True).count()
    downloads_count = DownloadItem.objects.filter(user=user).count()
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'preferences': preferences_data,
        'stats': {
            'subscriptions': subscriptions_count,
            'downloads': downloads_count
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, download_id):
    """
    Serve a download file for the authenticated user.
    
    Verifies:
    - User owns the download item
    - File exists on disk
    - Download status is 'ready'
    
    Returns: File download response
    """
    try:
        # Get the download item
        download_item = DownloadItem.objects.select_related('source').get(
            id=download_id,
            user=request.user
        )
        
        # Check if file is ready
        if download_item.status != 'ready':
            return Response(
                {'error': f'Download not ready. Status: {download_item.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if file exists
        if not download_item.local_file_path or not os.path.exists(download_item.local_file_path):
            return Response(
                {'error': 'File not found on server'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine content type based on file extension
        file_ext = os.path.splitext(download_item.local_file_path)[1].lower()
        content_type_map = {
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        
        # Serve the file
        file_handle = open(download_item.local_file_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)
        
        # Set download headers
        filename = os.path.basename(download_item.local_file_path)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(download_item.local_file_path)
        
        return response
    
    except DownloadItem.DoesNotExist:
        raise Http404('Download item not found')
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )