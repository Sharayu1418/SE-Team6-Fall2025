"""
Management command to deactivate sources that don't download content.

This removes:
- All 'article' type sources (metadata_only, no downloads)
- All 'video' type sources (YouTube blocked)
- Any source with policy='metadata_only'

Usage:
    python manage.py cleanup_sources
"""

from django.core.management.base import BaseCommand
from core.models import ContentSource, ContentItem


class Command(BaseCommand):
    help = 'Deactivate sources that do not download content (metadata_only)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete the sources instead of just deactivating them',
        )

    def handle(self, *args, **options):
        delete_mode = options.get('delete', False)
        
        # Find sources to remove (metadata_only articles and blocked videos)
        # Keep: podcast, meme, news (all cache_allowed)
        sources_to_remove = ContentSource.objects.filter(
            policy='metadata_only'
        ) | ContentSource.objects.filter(
            type__in=['article', 'video']  # Articles (RSS) and Videos (YouTube blocked)
        )
        
        count = sources_to_remove.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No metadata_only sources found. All clean!'))
            return
        
        self.stdout.write(f'\nFound {count} sources to {"delete" if delete_mode else "deactivate"}:\n')
        
        for source in sources_to_remove:
            items_count = ContentItem.objects.filter(source=source).count()
            self.stdout.write(f'  ❌ {source.name} ({source.type}, {source.policy}) - {items_count} items')
        
        if delete_mode:
            # Delete the sources (and their content items via CASCADE)
            sources_to_remove.delete()
            self.stdout.write(self.style.SUCCESS(f'\n🗑️  Deleted {count} sources and their content items.'))
        else:
            # Just deactivate them
            sources_to_remove.update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f'\n✅ Deactivated {count} sources.'))
        
        # Show remaining active sources
        active_sources = ContentSource.objects.filter(is_active=True)
        self.stdout.write(f'\n📋 Remaining active sources ({active_sources.count()}):')
        for source in active_sources:
            items_count = ContentItem.objects.filter(source=source, storage_provider__in=['aws_s3', 'supabase']).count()
            self.stdout.write(self.style.SUCCESS(f'  ✅ {source.name} ({source.type}) - {items_count} items with S3'))

