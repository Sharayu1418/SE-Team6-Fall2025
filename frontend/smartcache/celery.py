import os
from celery import Celery

# Default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')

app = Celery('smartcache')

# Load Celery config from Django settings with the prefix "CELERY_"
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
