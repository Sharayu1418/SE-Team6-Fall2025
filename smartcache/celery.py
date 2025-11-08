import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')

app = Celery('smartcache')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'ingest-content-hourly': {
        'task': 'core.tasks.ingest_content_sources',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
    'cleanup-old-content-weekly': {
        'task': 'core.tasks.cleanup_old_content',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')