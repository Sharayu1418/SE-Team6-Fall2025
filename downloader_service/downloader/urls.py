from django.urls import path
from .views import DownloadAPIView

urlpatterns = [
    path('download/', DownloadAPIView.as_view(), name='create-download-task'),
]