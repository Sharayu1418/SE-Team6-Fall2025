from django.contrib import admin
from .models import DownloadedContent

# This makes your model visible on the admin page
admin.site.register(DownloadedContent)
