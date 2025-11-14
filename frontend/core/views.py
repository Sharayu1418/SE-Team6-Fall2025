from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
import logging
from .models import (
    UserPreference, CommuteWindow, ContentSource, 
    Subscription, DownloadItem, Tag, Category
)
from .serializers import (
    UserPreferenceSerializer, CommuteWindowSerializer,
    ContentSourceSerializer, SubscriptionSerializer, DownloadItemSerializer
)
from .content_discovery import discover_content

logger = logging.getLogger(__name__)

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
def discover(request):
    """Content discovery page - browse content by tags"""
    # Load all available tags from database
    categories = Category.objects.prefetch_related('tags').all()
    
    # If no categories exist, suggest loading tags
    if not categories.exists():
        messages.info(request, 'No tags loaded. Run: python manage.py load_tags')
    
    # Get discovered content if tags were selected
    discovered_content = []
    selected_tags = []
    if request.method == 'POST':
        selected_tags = request.POST.getlist('tags')
        if selected_tags:
            sources = request.POST.getlist('sources') or ['youtube', 'podcasts', 'webpages']
            discovery_result = discover_content(
                tags=selected_tags,
                sources=sources,
                limit_per_source=10
            )
            discovered_content = discovery_result.get('results', [])
            
            # Debug info
            logger.info(f"Discovery result: {len(discovered_content)} items found")
            if discovered_content:
                logger.info(f"First item: {discovered_content[0]}")
            
            if discovery_result.get('errors'):
                for error in discovery_result['errors'][:5]:  # Show first 5 errors
                    messages.warning(request, error)
            
            # Show success message if content found
            if discovered_content:
                messages.success(request, f"Found {len(discovered_content)} items! Scroll down to see them.")
    
    return render(request, 'discover.html', {
        'categories': categories,
        'discovered_content': discovered_content,
        'selected_tags': selected_tags
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
    """Toggle subscription via HTMX - returns HTML button to swap"""
    source = get_object_or_404(ContentSource, id=source_id)
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        source=source,
        defaults={'priority': 1}
    )
    
    if not created:
        subscription.delete()
        is_subscribed = False
    else:
        is_subscribed = True
    
    # Return HTML button that HTMX can swap
    from django.urls import reverse
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    subscription_url = reverse('core:toggle_subscription', args=[source.id])
    
    # Build button HTML - escape curly braces properly in f-string
    if is_subscribed:
        button_html = (
            f'<button class="btn btn-success" '
            f'hx-post="{subscription_url}" '
            f'hx-target="#subscription-{source.id}" '
            f'hx-swap="outerHTML" '
            f'hx-headers=\'{{"X-CSRFToken": "{csrf_token}"}}\' '
            f'id="subscription-{source.id}">✓ Subscribed</button>'
        )
    else:
        button_html = (
            f'<button class="btn btn-outline-primary" '
            f'hx-post="{subscription_url}" '
            f'hx-target="#subscription-{source.id}" '
            f'hx-swap="outerHTML" '
            f'hx-headers=\'{{"X-CSRFToken": "{csrf_token}"}}\' '
            f'id="subscription-{source.id}">Subscribe</button>'
        )
    
    return HttpResponse(button_html)

@login_required
@require_http_methods(["POST"])
def request_download(request):
    """
    Handle download request from user-entered URL.
    Integrates with downloader service API.
    """
    url = request.POST.get('url', '').strip()
    # Handle both 'type' and 'download_type' parameter names
    download_type = request.POST.get('type') or request.POST.get('download_type')
    if download_type:
        download_type = download_type.upper()
    else:
        download_type = 'VIDEO'
    
    if not url:
        messages.error(request, 'Please provide a valid URL.')
        logger.warning("Download request missing URL")
        return redirect('core:downloads')
    
    # Validate download type
    valid_types = ['VIDEO', 'AUDIO', 'TEXT']
    if download_type not in valid_types:
        logger.warning(f"Invalid download_type '{download_type}', defaulting to VIDEO")
        download_type = 'VIDEO'
    
    logger.info(f"Download request - URL: {url}, Type: {download_type}, POST data: {dict(request.POST)}")
    
    try:
        # Call downloader service
        downloader_url = f"{settings.DOWNLOADER_SERVICE_URL}/api/download/"
        payload = {
            'url': url,
            'type': download_type
        }
        
        logger.info(f"Submitting download request to {downloader_url} with payload: {payload}")
        response = requests.post(
            downloader_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 202:
            # Success - download task created
            task_data = response.json()
            task_id = task_data.get('id')
            
            # Create DownloadItem in frontend DB
            download_item = DownloadItem.objects.create(
                user=request.user,
                original_url=url,
                download_type=download_type,
                downloader_task_id=task_id,
                status='queued',
                available_from=timezone.now(),
                metadata={'downloader_response': task_data}
            )
            
            messages.success(request, f'Download task created! Status: {download_item.get_status_display()}')
            logger.info(f"Created DownloadItem {download_item.id} for task {task_id}")
        else:
            # Downloader service error
            error_msg = f"Downloader service error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('error', 'Unknown error')}"
            except:
                error_msg += f" - {response.text[:100]}"
            
            logger.error(error_msg)
            messages.error(request, error_msg)
            
    except requests.exceptions.ConnectionError:
        error_msg = f"Cannot connect to downloader service at {settings.DOWNLOADER_SERVICE_URL}"
        logger.error(error_msg)
        messages.error(request, error_msg + ". Please check if the service is running.")
    except requests.exceptions.Timeout:
        error_msg = "Downloader service request timed out"
        logger.error(error_msg)
        messages.error(request, error_msg)
    except Exception as e:
        error_msg = f"Error submitting download request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        messages.error(request, error_msg)
    
    return redirect('core:downloads')

@login_required
@require_http_methods(["POST"])
def discover_content_api(request):
    """
    API endpoint for content discovery.
    Accepts POST with tags and returns discovered content.
    """
    tags = request.POST.getlist('tags') or (request.data.get('tags', []) if hasattr(request, 'data') else [])
    sources = request.POST.getlist('sources') or (request.data.get('sources', ['youtube', 'podcasts', 'webpages']) if hasattr(request, 'data') else ['youtube', 'podcasts', 'webpages'])
    limit = int(request.POST.get('limit', request.data.get('limit', 10) if hasattr(request, 'data') else 10))
    
    if not tags:
        return JsonResponse({'error': 'Tags are required'}, status=400)
    
    try:
        discovery_result = discover_content(
            tags=tags,
            sources=sources,
            limit_per_source=limit
        )
        
        return JsonResponse(discovery_result, safe=False)
    except Exception as e:
        logger.error(f"Content discovery error: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

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
    
    @action(detail=False, methods=['post'])
    def request_download(self, request):
        """
        API endpoint to request a download from a URL.
        Body: {"url": "...", "type": "VIDEO|AUDIO|TEXT"}
        """
        url = request.data.get('url', '').strip()
        download_type = request.data.get('type', 'VIDEO').upper()
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate download type
        valid_types = ['VIDEO', 'AUDIO', 'TEXT']
        if download_type not in valid_types:
            download_type = 'VIDEO'
        
        try:
            # Call downloader service
            downloader_url = f"{settings.DOWNLOADER_SERVICE_URL}/api/download/"
            payload = {
                'url': url,
                'type': download_type
            }
            
            logger.info(f"API: Submitting download request to {downloader_url}: {url}")
            response = requests.post(
                downloader_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 202:
                # Success
                task_data = response.json()
                task_id = task_data.get('id')
                
                # Create DownloadItem
                download_item = DownloadItem.objects.create(
                    user=request.user,
                    original_url=url,
                    download_type=download_type,
                    downloader_task_id=task_id,
                    status='queued',
                    available_from=timezone.now(),
                    metadata={'downloader_response': task_data}
                )
                
                serializer = self.get_serializer(download_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                error_msg = f"Downloader service error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                
                logger.error(error_msg)
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_502_BAD_GATEWAY
                )
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to downloader service at {settings.DOWNLOADER_SERVICE_URL}"
            logger.error(error_msg)
            return Response(
                {'error': error_msg},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            error_msg = f"Error submitting download request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return Response(
                {'error': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )