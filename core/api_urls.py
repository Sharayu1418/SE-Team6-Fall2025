from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'preferences', views.UserPreferenceViewSet, basename='preferences')
router.register(r'commute', views.CommuteWindowViewSet, basename='commute')
router.register(r'sources', views.ContentSourceViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')
router.register(r'downloads', views.DownloadItemViewSet, basename='downloads')

urlpatterns = [
    path('', include(router.urls)),
    # CSRF token endpoint (call this first to get cookie)
    path('csrf/', views.get_csrf_token, name='csrf'),
    # Auth endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/me/', views.current_user, name='current_user'),
    # Download file endpoint
    path('downloads/<int:download_id>/file/', views.download_file, name='download_file'),
    # ETL Pipeline endpoints (for demo/presentation)
    path('etl/trigger/', views.trigger_etl_pipeline, name='trigger_etl'),
    path('etl/clear/', views.clear_content_pool, name='clear_content'),
    path('etl/status/', views.get_etl_status, name='etl_status'),
]