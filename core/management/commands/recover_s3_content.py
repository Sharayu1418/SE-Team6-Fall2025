"""
Management command to recover ContentItem records from existing S3 content.

This scans the S3 bucket and recreates ContentItem database records
for any files that exist in S3 but are missing from the database.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from core.models import ContentSource, ContentItem
import boto3
import hashlib
import re
from datetime import datetime
from urllib.parse import unquote


class Command(BaseCommand):
    help = 'Recover ContentItem records from existing S3 content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be recovered without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        
        bucket_name = settings.AWS_S3_BUCKET_NAME
        region = settings.AWS_REGION
        
        self.stdout.write(f'Scanning S3 bucket: {bucket_name}')
        
        # List all objects in the bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        
        recovered = 0
        skipped = 0
        errors = 0
        
        # Get all sources for matching
        sources = {s.name.lower(): s for s in ContentSource.objects.all()}
        
        # Create normalized name mapping (remove special chars)
        sources_normalized = {}
        for source in ContentSource.objects.all():
            # Normalize: lowercase, remove parentheses, dashes, underscores
            normalized = source.name.lower()
            normalized = re.sub(r'[^a-z0-9\s]', '', normalized)  # Remove special chars
            normalized = re.sub(r'\s+', '', normalized)  # Remove spaces
            sources_normalized[normalized] = source
            
            # Also add without spaces
            sources_normalized[source.name.lower().replace(' ', '-')] = source
            sources_normalized[source.name.lower().replace(' ', '_')] = source
        
        # Also create a mapping by type for fallback
        source_by_type = {}
        for source in ContentSource.objects.all():
            if source.type not in source_by_type:
                source_by_type[source.type] = source
        
        self.stdout.write(f'Loaded {len(sources)} sources')
        
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                key = obj['Key']
                size = obj['Size']
                last_modified = obj['LastModified']
                
                # Skip empty files or directories
                if size == 0:
                    continue
                
                # Parse the key to extract info
                # Expected formats:
                # - podcasts/source-name/filename.mp3
                # - memes/source-name/filename.jpg
                # - news/source-name/filename.jpg
                # - content/type/filename.ext
                
                parts = key.split('/')
                
                if len(parts) < 2:
                    self.stdout.write(f'  Skipping (invalid path): {key}')
                    skipped += 1
                    continue
                
                # Determine content type and source from path
                content_type = parts[0].rstrip('s')  # podcasts -> podcast, memes -> meme
                if content_type == 'podcast':
                    content_type = 'podcast'
                elif content_type == 'meme':
                    content_type = 'meme'
                elif content_type == 'new':
                    content_type = 'news'
                elif content_type == 'article':
                    content_type = 'article'
                
                # Try to find source
                source = None
                source_name_from_path = parts[1] if len(parts) > 1 else None
                
                if source_name_from_path:
                    # Normalize the path name
                    path_normalized = source_name_from_path.lower()
                    path_normalized_clean = re.sub(r'[^a-z0-9]', '', path_normalized)
                    
                    # Try normalized match
                    if path_normalized_clean in sources_normalized:
                        source = sources_normalized[path_normalized_clean]
                    else:
                        # Try partial match
                        for name, src in sources.items():
                            name_clean = re.sub(r'[^a-z0-9]', '', name)
                            if path_normalized_clean in name_clean or name_clean in path_normalized_clean:
                                source = src
                                break
                        
                        # Try matching path parts
                        if not source:
                            path_words = set(re.findall(r'[a-z]+', path_normalized))
                            for name, src in sources.items():
                                name_words = set(re.findall(r'[a-z]+', name))
                                # If most words match
                                if len(path_words & name_words) >= min(2, len(path_words)):
                                    source = src
                                    break
                
                # Fallback to type-based source
                if not source and content_type in source_by_type:
                    source = source_by_type[content_type]
                
                if not source:
                    self.stdout.write(f'  Skipping (no matching source): {key}')
                    skipped += 1
                    continue
                
                # Generate storage URL
                storage_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
                
                # Create unique GUID from the S3 key
                guid = f"s3-recovered-{hashlib.md5(key.encode()).hexdigest()}"
                
                # Check if already exists
                if ContentItem.objects.filter(guid=guid).exists():
                    skipped += 1
                    continue
                
                # Also check by storage_url
                if ContentItem.objects.filter(storage_url=storage_url).exists():
                    skipped += 1
                    continue
                
                # Extract title from filename
                filename = parts[-1]
                title = unquote(filename)
                # Remove extension
                title = re.sub(r'\.[^.]+$', '', title)
                # Clean up
                title = title.replace('-', ' ').replace('_', ' ')
                title = ' '.join(word.capitalize() for word in title.split())
                
                if dry_run:
                    self.stdout.write(f'  Would recover: {title} ({source.name})')
                else:
                    try:
                        ContentItem.objects.create(
                            source=source,
                            title=title[:500],  # Truncate to field max length
                            description=f"Recovered from S3: {key}",
                            url=storage_url,  # Use S3 URL as original URL
                            media_url=storage_url,
                            storage_url=storage_url,
                            storage_provider='aws_s3',
                            file_size_bytes=size,
                            published_at=last_modified,
                            guid=guid,
                            topics=[content_type],
                        )
                        recovered += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Recovered: {title}'))
                    except Exception as e:
                        errors += 1
                        self.stdout.write(self.style.ERROR(f'  ✗ Error: {title} - {e}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Recovery complete!'))
        self.stdout.write(f'  Recovered: {recovered}')
        self.stdout.write(f'  Skipped: {skipped}')
        self.stdout.write(f'  Errors: {errors}')

