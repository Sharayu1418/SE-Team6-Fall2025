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

from django.core.management.base import BaseCommand, CommandError
from core.models import ContentSource
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
            '--provider',
            type=str,
            default=None,
            choices=['aws_s3', 'supabase', 'none'],
            help='Storage provider to use (overrides settings)',
        )

    def handle(self, *args, **options):
        source_id = options.get('source')
        source_name = options.get('source_name')
        provider = options.get('provider')

        # Initialize ETL service
        try:
            service = ContentIngestionService(storage_provider=provider)
        except Exception as e:
            raise CommandError(f'Failed to initialize ETL service: {e}')

        # Specific source by ID
        if source_id:
            try:
                source = ContentSource.objects.get(id=source_id)
                self.stdout.write(f'\n🔄 Ingesting source: {source.name} (ID: {source.id})\n')
                
                count = service.ingest_source(source)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully ingested {count} new items from {source.name}'
                    )
                )
                
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
            
            if sources.count() > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {sources.count()} sources matching "{source_name}":'
                    )
                )
                for src in sources:
                    self.stdout.write(f'  - {src.name} (ID: {src.id})')
                
                self.stdout.write('\nIngesting all matching sources...\n')
            
            total_items = 0
            for source in sources:
                self.stdout.write(f'\n🔄 Ingesting: {source.name} (ID: {source.id})')
                
                try:
                    count = service.ingest_source(source)
                    total_items += count
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {count} new items')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Total: {total_items} new items from {sources.count()} source(s)'
                )
            )

        # All sources
        else:
            active_sources = ContentSource.objects.filter(is_active=True).count()
            
            self.stdout.write(
                f'\n🔄 Starting ETL pipeline for {active_sources} active source(s)...\n'
            )
            
            try:
                results = service.ingest_all_sources()
                
                # Display results
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('ETL Pipeline Complete'))
                self.stdout.write('='*60 + '\n')
                
                self.stdout.write(
                    f"Sources Processed: {results.get('sources_processed', 0)}"
                )
                self.stdout.write(
                    f"Total New Items: {results.get('total_items_added', 0)}"
                )
                self.stdout.write(
                    f"Errors: {results.get('errors', 0)}"
                )
                
                # Show per-source details
                if 'details' in results:
                    self.stdout.write('\nDetails by source:')
                    for source_name, count in results['details'].items():
                        if isinstance(count, int):
                            if count > 0:
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✓ {source_name}: {count} items')
                                )
                            else:
                                self.stdout.write(
                                    f'  - {source_name}: No new items'
                                )
                        else:
                            # Error message
                            self.stdout.write(
                                self.style.ERROR(f'  ✗ {source_name}: {count}')
                            )
                
                self.stdout.write('')
                
            except Exception as e:
                raise CommandError(f'ETL pipeline failed: {e}')

