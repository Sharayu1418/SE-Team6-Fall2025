from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('commutes/', views.commutes, name='commutes'),
    path('sources/', views.sources, name='sources'),
    path('downloads/', views.downloads, name='downloads'),
    path('discover/', views.discover, name='discover'),
    
    # HTMX endpoints
    path('api/toggle-subscription/<int:source_id>/', 
         views.toggle_subscription, name='toggle_subscription'),
    path('api/request-download/', 
         views.request_download, name='request_download'),
    path('api/discover/', 
         views.discover_content_api, name='discover_content_api'),
    
    # Auth views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:index'), name='logout'),
]