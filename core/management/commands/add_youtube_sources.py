"""
Management command to add YouTube video sources.

Usage:
    python manage.py add_youtube_sources
"""

from django.core.management.base import BaseCommand
from core.models import ContentSource


class Command(BaseCommand):
    help = 'Add YouTube video sources to the database'

    def handle(self, *args, **options):
        # YouTube sources - using search queries for topics
        youtube_sources = [
            {
                'name': 'Tech News Videos',
                'feed_url': 'search:technology news 2024',
                'policy': 'metadata_only',
            },
            {
                'name': 'AI & Machine Learning',
                'feed_url': 'search:artificial intelligence machine learning tutorial',
                'policy': 'metadata_only',
            },
            {
                'name': 'Science Explained',
                'feed_url': 'search:science explained documentary',
                'policy': 'metadata_only',
            },
            {
                'name': 'TED Talks',
                'feed_url': 'search:TED talk inspiration',
                'policy': 'metadata_only',
            },
            {
                'name': 'Programming Tutorials',
                'feed_url': 'search:programming tutorial python javascript',
                'policy': 'metadata_only',
            },
            {
                'name': 'World News Videos',
                'feed_url': 'search:world news today',
                'policy': 'metadata_only',
            },
            {
                'name': 'Space & Astronomy',
                'feed_url': 'search:space astronomy NASA',
                'policy': 'metadata_only',
            },
            {
                'name': 'Business & Finance',
                'feed_url': 'search:business finance investing',
                'policy': 'metadata_only',
            },
            {
                'name': 'Health & Wellness',
                'feed_url': 'search:health wellness fitness tips',
                'policy': 'metadata_only',
            },
            {
                'name': 'Climate & Environment',
                'feed_url': 'search:climate change environment documentary',
                'policy': 'metadata_only',
            },
        ]

        created_count = 0
        skipped_count = 0

        for source_data in youtube_sources:
            source, created = ContentSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'type': 'video',
                    'feed_url': source_data['feed_url'],
                    'policy': source_data['policy'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {source.name}')
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
        self.stdout.write('To ingest YouTube videos, run:')
        self.stdout.write('  python manage.py run_etl --source-name "Tech News"')
        self.stdout.write('  python manage.py run_etl --source-name "AI"')


