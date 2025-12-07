"""
Management command to manually trigger the ETL pipeline.

This command is useful for:
- Initial content ingestion during setup
- Testing the ETL pipeline
- Forcing a refresh of content sources
- Demo purposes

Usage:
    python manage.py run_etl                    # Ingest all sources
    python manage.py run_etl --source 1         # Ingest specific source by ID
    python manage.py run_etl --source-name NPR  # Ingest by source name
"""

import sys
import time
from django.core.management.base import BaseCommand, CommandError
from core.models import ContentSource, ContentItem
from core.services.content_ingestion import ContentIngestionService


class Command(BaseCommand):
    help = 'Manually trigger ETL pipeline to ingest content from RSS feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=int,
            help='ID of a specific ContentSource to ingest',
        )
        parser.add_argument(
            '--source-name',
            type=str,
            help='Name of a specific ContentSource to ingest (partial match)',
        )
        parser.add_argument(
            '--source-type',
            type=str,
            choices=['podcast', 'video', 'article', 'meme', 'news'],
            help='Filter by source type (podcast, video, article, meme, news)',
        )
        parser.add_argument(
            '--provider',
            type=str,
            default=None,
            choices=['aws_s3', 'supabase', 'none'],
            help='Storage provider to use (overrides settings)',
        )

    def print_progress_bar(self, current, total, prefix='Progress', suffix='', length=40):
        """Print a progress bar to the console."""
        percent = 100 * (current / float(total)) if total > 0 else 0
        filled_length = int(length * current // total) if total > 0 else 0
        bar = '█' * filled_length + '░' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}')
        sys.stdout.flush()
        if current == total:
            sys.stdout.write('\n')

    def print_stats(self, total_items, items_with_storage, sources_done, total_sources, errors):
        """Print current statistics."""
        self.stdout.write(
            f'\n📊 Stats: {total_items} items | {items_with_storage} with S3 | '
            f'{sources_done}/{total_sources} sources | {errors} errors'
        )

    def handle(self, *args, **options):
        source_id = options.get('source')
        source_name = options.get('source_name')
        source_type = options.get('source_type')
        provider = options.get('provider')

        # Get initial counts
        initial_items = ContentItem.objects.count()
        initial_with_storage = ContentItem.objects.exclude(
            storage_url__isnull=True
        ).exclude(storage_url='').count()

        # Initialize ETL service
        try:
            service = ContentIngestionService(storage_provider=provider)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Storage provider: {service.storage_provider}')
            )
        except Exception as e:
            raise CommandError(f'Failed to initialize ETL service: {e}')

        # Specific source by ID
        if source_id:
            try:
                source = ContentSource.objects.get(id=source_id)
                self.stdout.write(f'\n🔄 Ingesting source: {source.name} (ID: {source.id})\n')
                
                count = service.ingest_source(source)
                
                # Show final stats
                final_items = ContentItem.objects.count()
                final_with_storage = ContentItem.objects.exclude(
                    storage_url__isnull=True
                ).exclude(storage_url='').count()
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS(f'✓ {count} new items from {source.name}'))
                self.stdout.write(f'📦 Total items in DB: {final_items} (+{final_items - initial_items})')
                self.stdout.write(f'☁️  Items with S3 URL: {final_with_storage} (+{final_with_storage - initial_with_storage})')
                
            except ContentSource.DoesNotExist:
                raise CommandError(f'ContentSource with ID {source_id} not found')
            except Exception as e:
                raise CommandError(f'Error ingesting source: {e}')

        # Specific source by name
        elif source_name:
            sources = ContentSource.objects.filter(
                name__icontains=source_name,
                is_active=True
            )
            
            if not sources.exists():
                raise CommandError(
                    f'No active sources found matching "{source_name}"'
                )
            
            total_sources = sources.count()
            self.stdout.write(f'\n🔄 Found {total_sources} source(s) matching "{source_name}"\n')
            
            total_items = 0
            errors = 0
            
            for idx, source in enumerate(sources, 1):
                self.print_progress_bar(
                    idx - 1, total_sources, 
                    prefix='ETL Progress',
                    suffix=f'| {source.name[:30]}...'
                )
                
                try:
                    count = service.ingest_source(source)
                    total_items += count
                    if count > 0:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {source.name}: {count} items')
                        )
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {source.name}: {e}')
                    )
            
            self.print_progress_bar(total_sources, total_sources, prefix='ETL Progress', suffix='Complete!')
            
            # Show final stats
            final_items = ContentItem.objects.count()
            final_with_storage = ContentItem.objects.exclude(
                storage_url__isnull=True
            ).exclude(storage_url='').count()
            
            self.stdout.write('')
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS('✓ ETL Complete!'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'📥 New items added: {total_items}')
            self.stdout.write(f'📦 Total items in DB: {final_items}')
            self.stdout.write(f'☁️  Items with S3 URL: {final_with_storage} (ready for agents)')
            self.stdout.write(f'❌ Errors: {errors}')
            self.stdout.write('')
            
            if final_with_storage > 0:
                self.stdout.write(
                    self.style.SUCCESS('🚀 You can now run the agents to discover & download content!')
                )

        # Filter by source type
        elif source_type:
            sources = ContentSource.objects.filter(
                type=source_type,
                is_active=True
            )
            
            if not sources.exists():
                raise CommandError(
                    f'No active sources found with type "{source_type}"'
                )
            
            total_sources = sources.count()
            self.stdout.write(f'\n🔄 Found {total_sources} source(s) of type "{source_type}"\n')
            
            total_items = 0
            errors = 0
            
            start_time = time.time()
            
            for idx, source in enumerate(sources, 1):
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                eta = (total_sources - idx) / rate if rate > 0 else 0
                
                self.print_progress_bar(
                    idx, total_sources, 
                    prefix='ETL Progress',
                    suffix=f'| ETA: {int(eta)}s | {source.name[:25]}...'
                )
                
                try:
                    count = service.ingest_source(source)
                    total_items += count
                    if count > 0:
                        sys.stdout.write(f'\n  ✓ {source.name}: {count} items\n')
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'\n  ✗ {source.name}: {e}')
                    )
            
            self.print_progress_bar(total_sources, total_sources, prefix='ETL Progress', suffix='Complete!')
            
            elapsed_total = time.time() - start_time
            
            # Show final stats
            final_items = ContentItem.objects.count()
            final_with_storage = ContentItem.objects.exclude(
                storage_url__isnull=True
            ).exclude(storage_url='').count()
            
            self.stdout.write('')
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS(f'✓ ETL Complete for {source_type} sources!'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'⏱️  Time elapsed: {elapsed_total:.1f} seconds')
            self.stdout.write(f'📥 New items added: {total_items}')
            self.stdout.write(f'📦 Total items in DB: {final_items}')
            self.stdout.write(f'☁️  Items with S3 URL: {final_with_storage} (ready for agents)')
            self.stdout.write(f'❌ Errors: {errors}')
            self.stdout.write('')

        # All sources
        else:
            sources = ContentSource.objects.filter(is_active=True)
            total_sources = sources.count()
            
            self.stdout.write('')
            self.stdout.write('=' * 60)
            self.stdout.write(f'🔄 ETL Pipeline - {total_sources} sources')
            self.stdout.write('=' * 60)
            self.stdout.write('')
            
            total_new_items = 0
            errors = 0
            successful_sources = []
            failed_sources = []
            
            start_time = time.time()
            
            for idx, source in enumerate(sources, 1):
                # Update progress bar
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                eta = (total_sources - idx) / rate if rate > 0 else 0
                
                self.print_progress_bar(
                    idx, total_sources,
                    prefix='Progress',
                    suffix=f'| ETA: {int(eta)}s | {source.name[:25]}...'
                )
                
                try:
                    count = service.ingest_source(source)
                    total_new_items += count
                    
                    if count > 0:
                        successful_sources.append((source.name, count))
                        # Print success inline
                        sys.stdout.write(f'\n  ✓ {source.name}: {count} new items\n')
                        
                except Exception as e:
                    errors += 1
                    failed_sources.append((source.name, str(e)[:50]))
            
            # Final progress
            self.print_progress_bar(total_sources, total_sources, prefix='Progress', suffix='Complete!')
            
            elapsed_total = time.time() - start_time
            
            # Get final counts
            final_items = ContentItem.objects.count()
            final_with_storage = ContentItem.objects.exclude(
                storage_url__isnull=True
            ).exclude(storage_url='').count()
            
            # Summary
            self.stdout.write('')
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS('📊 ETL PIPELINE COMPLETE'))
            self.stdout.write('=' * 60)
            self.stdout.write('')
            self.stdout.write(f'⏱️  Time elapsed: {elapsed_total:.1f} seconds')
            self.stdout.write(f'📥 New items added: {total_new_items}')
            self.stdout.write(f'📦 Total items in DB: {final_items}')
            self.stdout.write(
                self.style.SUCCESS(f'☁️  Items with S3 URL: {final_with_storage} (ready for agents!)')
            )
            self.stdout.write(f'✅ Successful sources: {len(successful_sources)}')
            self.stdout.write(f'❌ Failed sources: {errors}')
            self.stdout.write('')
            
            # Show top successful sources
            if successful_sources:
                self.stdout.write('📈 Top sources by new items:')
                for name, count in sorted(successful_sources, key=lambda x: -x[1])[:10]:
                    self.stdout.write(f'   {count:3d} | {name}')
                self.stdout.write('')
            
            # Show failed sources
            if failed_sources:
                self.stdout.write(self.style.WARNING('⚠️  Failed sources:'))
                for name, error in failed_sources[:5]:
                    self.stdout.write(f'   ✗ {name}: {error}')
                if len(failed_sources) > 5:
                    self.stdout.write(f'   ... and {len(failed_sources) - 5} more')
                self.stdout.write('')
            
            # Final message
            if final_with_storage > 0:
                self.stdout.write('=' * 60)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🚀 Ready! {final_with_storage} items available for agents.'
                    )
                )
                self.stdout.write('   Run the frontend and click "Discover & Download Content"')
                self.stdout.write('=' * 60)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  No items with storage URLs. Check your S3/Supabase credentials.'
                    )
                )
