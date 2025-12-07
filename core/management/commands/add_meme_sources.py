"""
Management command to add Meme sources (Reddit subreddits).

Usage:
    python manage.py add_meme_sources
"""

from django.core.management.base import BaseCommand
from core.models import ContentSource


class Command(BaseCommand):
    help = 'Add Meme sources (Reddit subreddits) to the database'

    def handle(self, *args, **options):
        # Meme sources - subreddit names
        meme_sources = [
            {
                'name': 'Dank Memes',
                'feed_url': 'dankmemes',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Wholesome Memes',
                'feed_url': 'wholesomememes',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Funny Memes',
                'feed_url': 'memes',
                'policy': 'cache_allowed',
            },
        ]

        created_count = 0
        skipped_count = 0

        for source_data in meme_sources:
            source, created = ContentSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'type': 'meme',
                    'feed_url': f"https://reddit.com/r/{source_data['feed_url']}",
                    'policy': source_data['policy'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {source.name} (r/{source_data["feed_url"]})')
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
        self.stdout.write('To ingest memes, run:')
        self.stdout.write('  python manage.py run_etl --source-type meme')

