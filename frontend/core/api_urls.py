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
    path('auth/', include('rest_framework.urls')),
]