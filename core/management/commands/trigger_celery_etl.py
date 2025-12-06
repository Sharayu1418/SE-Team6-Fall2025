"""
Management command to manually trigger the Celery ETL task.

Use this during presentations to demonstrate Celery working.

Usage:
    python manage.py trigger_celery_etl
    python manage.py trigger_celery_etl --source-id 1
    python manage.py trigger_celery_etl --wait  # Wait for result
"""

from django.core.management.base import BaseCommand
from core.tasks import ingest_content_sources, manual_ingest_source


class Command(BaseCommand):
    help = 'Manually trigger the Celery ETL task'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='Specific source ID to ingest (optional)',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for the task to complete and show result',
        )

    def handle(self, *args, **options):
        source_id = options.get('source_id')
        wait = options.get('wait')
        
        if source_id:
            self.stdout.write(f'🚀 Triggering Celery ETL for source ID: {source_id}')
            result = manual_ingest_source.delay(source_id)
        else:
            self.stdout.write('🚀 Triggering Celery ETL for all sources...')
            result = ingest_content_sources.delay()
        
        self.stdout.write(self.style.SUCCESS(f'✅ Task queued! Task ID: {result.id}'))
        self.stdout.write('📡 Check Celery worker terminal to see it executing.')
        
        if wait:
            self.stdout.write('⏳ Waiting for task to complete...')
            try:
                task_result = result.get(timeout=300)  # 5 min timeout
                self.stdout.write(self.style.SUCCESS(f'✅ Task completed: {task_result}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Task failed: {e}'))

