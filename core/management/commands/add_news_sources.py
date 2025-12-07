"""
Management command to add NewsAPI news sources.

Usage:
    python manage.py add_news_sources
"""

from django.core.management.base import BaseCommand
from core.models import ContentSource


class Command(BaseCommand):
    help = 'Add NewsAPI news sources to the database'

    def handle(self, *args, **options):
        # News sources - search queries for NewsAPI
        news_sources = [
            {
                'name': 'Tech News',
                'feed_url': 'technology',
                'policy': 'cache_allowed',
            },
            {
                'name': 'AI & Machine Learning News',
                'feed_url': 'artificial intelligence OR machine learning',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Science News',
                'feed_url': 'science discovery research',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Business News',
                'feed_url': 'business finance stocks',
                'policy': 'cache_allowed',
            },
            {
                'name': 'World News',
                'feed_url': 'world news international',
                'policy': 'cache_allowed',
            },
        ]

        created_count = 0
        skipped_count = 0

        for source_data in news_sources:
            source, created = ContentSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'type': 'news',
                    'feed_url': source_data['feed_url'],
                    'policy': source_data['policy'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {source.name} (query: {source_data["feed_url"]})')
                )
            else:
                skipped_count += 1
                self.stdout.write(f'- Skipped (exists): {source.name}')

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Done! Created {created_count} new sources, skipped {skipped_count} existing.'
            )
        )
        self.stdout.write('')
        self.stdout.write('⚠️  Make sure NEWSAPI_KEY is set in your .env file!')
        self.stdout.write('')
        self.stdout.write('To ingest news, run:')
        self.stdout.write('  python manage.py run_etl --source-type news')

