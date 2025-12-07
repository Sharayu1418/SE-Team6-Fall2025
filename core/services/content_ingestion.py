"""
Content Ingestion ETL Pipeline.

This service fetches content from RSS feeds and APIs, transforms it,
and loads it into the database. It does NOT involve agents - this is
pure data engineering.

The ETL process:
1. Extract: Fetch RSS feeds from ContentSource entries
2. Transform: Parse entries, download media (if cache_allowed)
3. Load: Store metadata in ContentItem, upload media to S3/Supabase
"""

import logging
import hashlib
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
from time import mktime

import feedparser
import requests
from django.utils import timezone
from django.conf import settings

from core.models import ContentSource, ContentItem
from core.services.storage_service import get_storage_service, StorageService

logger = logging.getLogger(__name__)


class ContentIngestionService:
    """
    ETL service for ingesting content from external sources.
    
    This is NOT an AutoGen agent - it's a scheduled background job
    that runs periodically (e.g., via Celery or cron).
    """
    
    def __init__(self, storage_provider: Optional[str] = None):
        """
        Initialize the ingestion service.
        
        Args:
            storage_provider: Storage provider to use ('aws_s3', 'supabase', or None)
                             If None, reads from settings.STORAGE_PROVIDER
        """
        self.storage_provider = storage_provider or getattr(settings, 'STORAGE_PROVIDER', 'none')
        self.storage_service: Optional[StorageService] = None
        
        # Initialize storage service if provider is configured
        if self.storage_provider in ['aws_s3', 'supabase']:
            try:
                self.storage_service = self._init_storage_service()
                logger.info(f"Storage service initialized: {self.storage_provider}")
            except Exception as e:
                logger.warning(f"Failed to initialize storage service: {e}")
                logger.warning("Will skip media uploads for cache_allowed sources")
                self.storage_service = None
    
    def _init_storage_service(self) -> StorageService:
        """Initialize the storage service based on configuration."""
        if self.storage_provider == 'aws_s3':
            return get_storage_service(
                provider='aws_s3',
                bucket_name=getattr(settings, 'AWS_S3_BUCKET_NAME', 'smartcache-media'),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region=getattr(settings, 'AWS_REGION', 'us-east-1'),
            )
        
        elif self.storage_provider == 'supabase':
            return get_storage_service(
                provider='supabase',
                supabase_url=getattr(settings, 'SUPABASE_URL'),
                supabase_key=getattr(settings, 'SUPABASE_KEY'),
                bucket_name=getattr(settings, 'SUPABASE_BUCKET', 'media'),
            )
        
        else:
            raise ValueError(f"Unsupported storage provider: {self.storage_provider}")
    
    def ingest_all_sources(self) -> Dict[str, any]:
        """
        Main ETL entry point: fetch content from all active sources.
        
        Returns:
            Summary stats: {source_name: items_added, ...}
        """
        sources = ContentSource.objects.filter(is_active=True)
        results = {}
        total_items = 0
        total_errors = 0
        
        logger.info(f"Starting ingestion for {sources.count()} sources")
        
        for source in sources:
            try:
                count = self.ingest_source(source)
                results[source.name] = count
                total_items += count
                logger.info(f"✓ {source.name}: {count} new items")
            except Exception as e:
                logger.error(f"✗ {source.name}: {e}")
                results[source.name] = f"ERROR: {str(e)}"
                total_errors += 1
        
        logger.info(f"Ingestion complete: {total_items} items, {total_errors} errors")
        
        return {
            'sources_processed': sources.count(),
            'total_items_added': total_items,
            'errors': total_errors,
            'details': results,
        }
    
    def ingest_source(self, source: ContentSource) -> int:
        """
        Fetch and parse content from a single source.
        
        Args:
            source: The ContentSource to ingest
            
        Returns:
            Number of new items added
        """
        logger.info(f"Ingesting source: {source.name} ({source.type})")
        
        if source.type in ['podcast', 'article']:
            return self._ingest_rss_feed(source)
        elif source.type == 'video':
            return self._ingest_youtube_channel(source)
        else:
            raise ValueError(f"Unsupported source type: {source.type}")
    
    def _ingest_rss_feed(self, source: ContentSource) -> int:
        """
        Parse an RSS feed and create ContentItem records.
        
        Args:
            source: ContentSource with RSS feed URL
            
        Returns:
            Number of new items created
        """
        try:
            # Parse RSS feed
            logger.info(f"Fetching feed: {source.feed_url}")
            feed = feedparser.parse(str(source.feed_url))
            
            if feed.bozo:
                logger.warning(f"Feed has issues: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {source.feed_url}")
                return 0
            
            new_items = 0
            
            # Process each entry
            for entry in feed.entries:
                try:
                    # Create item data dict
                    item_data = self._parse_feed_entry(entry, source)
                    
                    # Check if already exists
                    if ContentItem.objects.filter(guid=item_data['guid']).exists():
                        logger.debug(f"Skipping duplicate: {item_data['title']}")
                        continue
                    
                    # Create ContentItem
                    content_item = self._create_content_item(source, item_data)
                    new_items += 1
                    
                    logger.info(f"✓ Created: {content_item.title}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process entry: {e}")
                    continue
            
            return new_items
            
        except Exception as e:
            logger.error(f"Failed to parse feed {source.feed_url}: {e}")
            raise
    
    def _ingest_youtube_channel(self, source: ContentSource) -> int:
        """
        Fetch videos from a YouTube channel/playlist/search using yt-dlp.
        
        The feed_url for YouTube sources should be either:
        - A YouTube channel URL (e.g., https://www.youtube.com/@TEDx)
        - A YouTube playlist URL (e.g., https://www.youtube.com/playlist?list=...)
        - A search query prefixed with 'search:' (e.g., 'search:AI technology')
        
        Uses yt-dlp's native extraction instead of youtube-search-python.
        
        Args:
            source: ContentSource with YouTube channel/search info
            
        Returns:
            Number of new items created
        """
        try:
            import yt_dlp
            
            feed_url = str(source.feed_url)
            
            # Build the URL for yt-dlp
            if feed_url.startswith('search:'):
                # Search query - use ytsearch
                query = feed_url.replace('search:', '').strip()
                yt_url = f"ytsearch10:{query}"  # Search for 10 videos
                logger.info(f"Searching YouTube for: {query}")
            elif feed_url.startswith('http'):
                # Direct URL (channel or playlist)
                yt_url = feed_url
                logger.info(f"Fetching from YouTube URL: {feed_url}")
            else:
                # Assume it's a channel name, search for it
                yt_url = f"ytsearch10:{feed_url}"
                logger.info(f"Searching YouTube for channel: {feed_url}")
            
            # yt-dlp options for extracting metadata only (flat playlist)
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',  # Don't download, just get metadata
                'playlistend': 10,  # Limit to 10 videos per source
            }
            
            videos = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(yt_url, download=False)
                    
                    if result is None:
                        logger.warning(f"No results from yt-dlp for: {feed_url}")
                        return 0
                    
                    # Handle different result types
                    if 'entries' in result:
                        # Playlist or search results
                        videos = [v for v in result['entries'] if v is not None][:10]
                    else:
                        # Single video
                        videos = [result]
                        
                except Exception as e:
                    logger.error(f"yt-dlp extraction failed: {e}")
                    return 0
            
            if not videos:
                logger.warning(f"No videos found for: {feed_url}")
                return 0
            
            logger.info(f"Found {len(videos)} videos for {source.name}")
            new_items = 0
            
            for video in videos:
                try:
                    if video is None:
                        continue
                    
                    # Extract video data
                    video_id = video.get('id', '')
                    title = (video.get('title') or 'Untitled')[:500]
                    
                    if not video_id:
                        continue
                    
                    # Create GUID from video ID
                    guid = f"youtube_{video_id}"
                    
                    # Check if already exists
                    if ContentItem.objects.filter(guid=guid).exists():
                        logger.debug(f"Skipping duplicate: {title}")
                        continue
                    
                    # Extract metadata
                    channel_name = video.get('channel') or video.get('uploader') or 'Unknown'
                    description = (video.get('description') or '')[:2000]
                    duration_seconds = video.get('duration')
                    video_url = video.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Create item data
                    item_data = {
                        'title': f"{title} - {channel_name}",
                        'description': description,
                        'url': video_url,
                        'guid': guid,
                        'published_at': timezone.now(),
                        'media_url': video_url,
                        'duration_seconds': duration_seconds,
                    }
                    
                    # Download YouTube video using yt-dlp (actual download)
                    temp_file_path = self._download_youtube_video(video_url)
                    
                    storage_url = None
                    storage_provider = 'none'
                    
                    if temp_file_path and self.storage_service:
                        try:
                            # Get file extension
                            ext = os.path.splitext(temp_file_path)[1] or '.mp4'
                            storage_url = self.storage_service.upload_file(
                                temp_file_path, 
                                f"youtube/{guid}{ext}"
                            )
                            storage_provider = self.storage_provider
                            logger.info(f"✓ Uploaded to {storage_provider}: {storage_url}")
                        except Exception as e:
                            logger.warning(f"Failed to upload to storage: {e}")
                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)
                                # Also try to remove temp directory
                                try:
                                    os.rmdir(os.path.dirname(temp_file_path))
                                except:
                                    pass
                    
                    # Create ContentItem (store YouTube URL if no S3 upload)
                    content_item = ContentItem.objects.create(
                        source=source,
                        title=item_data['title'],
                        description=item_data['description'],
                        url=item_data['url'],
                        media_url=item_data['media_url'],
                        storage_url=storage_url or item_data['url'],
                        storage_provider=storage_provider,
                        duration_seconds=item_data.get('duration_seconds'),
                        published_at=item_data['published_at'],
                        guid=item_data['guid'],
                    )
                    
                    new_items += 1
                    logger.info(f"✓ Created: {content_item.title}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process video: {e}")
                    continue
            
            return new_items
            
        except ImportError:
            logger.error("yt-dlp not installed. Install with: pip install yt-dlp")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch YouTube videos: {e}")
            raise
    
    def _parse_feed_entry(self, entry: any, source: ContentSource) -> Dict[str, any]:
        """
        Parse a single RSS feed entry into a data dict.
        
        Args:
            entry: feedparser entry object
            source: ContentSource for context
            
        Returns:
            Dictionary with parsed entry data
        """
        # Extract basic info
        title = entry.get('title', 'Untitled')[:500]
        description = entry.get('summary', entry.get('description', ''))[:2000]
        url = entry.get('link', '')
        
        # Create GUID
        guid = entry.get('guid') or entry.get('id') or self._create_guid(url)
        
        # Parse published date
        published_at = self._parse_date(entry.get('published_parsed') or entry.get('updated_parsed'))
        
        # Extract media URL (for podcasts)
        media_url = None
        if hasattr(entry, 'enclosures') and entry.enclosures:
            # Get first audio/video enclosure
            for enclosure in entry.enclosures:
                if 'audio' in enclosure.get('type', '') or 'video' in enclosure.get('type', ''):
                    media_url = enclosure.get('href') or enclosure.get('url')
                    break
            
            # Fallback to any enclosure
            if not media_url and entry.enclosures:
                media_url = entry.enclosures[0].get('href') or entry.enclosures[0].get('url')
        
        # Try media:content tag (alternative media format)
        if not media_url and hasattr(entry, 'media_content'):
            media_url = entry.media_content[0].get('url')
        
        return {
            'title': title,
            'description': description,
            'url': url,
            'guid': guid,
            'published_at': published_at,
            'media_url': media_url,
        }
    
    def _create_content_item(self, source: ContentSource, item_data: Dict[str, any]) -> ContentItem:
        """
        Create a ContentItem from parsed data.
        
        If source.policy == 'cache_allowed', downloads media and uploads to storage.
        
        Args:
            source: ContentSource
            item_data: Parsed entry data
            
        Returns:
            Created ContentItem
        """
        storage_url = None
        storage_provider = 'none'
        file_size_bytes = None
        
        # Handle media caching
        if source.policy == 'cache_allowed' and item_data['media_url']:
            if self.storage_service:
                try:
                    # Download media to temp file
                    temp_file_path = self._download_media(item_data['media_url'])
                    
                    if temp_file_path:
                        # Get file size
                        file_size_bytes = os.path.getsize(temp_file_path)
                        
                        # Upload to storage
                        object_key = self._generate_object_key(source, item_data)
                        storage_url = self.storage_service.upload_file(temp_file_path, object_key)
                        storage_provider = self.storage_provider
                        
                        # Clean up temp file
                        os.remove(temp_file_path)
                        
                        logger.info(f"✓ Uploaded media to {storage_provider}: {storage_url}")
                    
                except Exception as e:
                    logger.error(f"Failed to download/upload media: {e}")
                    # Continue without storage_url
            else:
                logger.warning(f"Storage service not available, skipping media upload for: {item_data['title']}")
        
        # Create ContentItem
        content_item = ContentItem.objects.create(
            source=source,
            title=item_data['title'],
            description=item_data['description'],
            url=item_data['url'],
            media_url=item_data['media_url'],
            storage_url=storage_url,
            storage_provider=storage_provider,
            file_size_bytes=file_size_bytes,
            published_at=item_data['published_at'],
            guid=item_data['guid'],
        )
        
        return content_item
    
    def _download_media(self, url: str, timeout: int = 60) -> Optional[str]:
        """
        Download media file to a temporary location.
        
        Args:
            url: Media URL to download
            timeout: Request timeout in seconds
            
        Returns:
            Path to temporary file, or None if download fails
        """
        try:
            logger.info(f"Downloading media: {url}")
            
            # Browser-like headers to avoid 403 Forbidden errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/mpeg, audio/*, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/',
            }
            
            # Make request with streaming and browser headers
            response = requests.get(url, stream=True, timeout=timeout, headers=headers)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            ext = self._get_extension_from_content_type(content_type) or self._get_extension_from_url(url)
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                # Download in chunks
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                
                temp_file_path = temp_file.name
            
            logger.info(f"✓ Downloaded to: {temp_file_path}")
            return temp_file_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download media from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading media: {e}")
            return None
    
    def _download_youtube_video(self, url: str) -> Optional[str]:
        """
        Download a YouTube video using yt-dlp.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Path to downloaded file, or None if download fails
        """
        try:
            import yt_dlp
            
            # Create temp directory for download
            temp_dir = tempfile.mkdtemp()
            output_template = os.path.join(temp_dir, '%(id)s.%(ext)s')
            
            ydl_opts = {
                'format': 'bestaudio/best',  # Audio only to save space, change to 'best' for video
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            logger.info(f"Downloading YouTube video: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
                # Find the downloaded file
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    logger.info(f"✓ Downloaded YouTube video to: {file_path}")
                    return file_path
            
            return None
            
        except ImportError:
            logger.error("yt-dlp not installed. Install with: pip install yt-dlp")
            return None
        except Exception as e:
            logger.error(f"Failed to download YouTube video: {e}")
            return None
    
    def _generate_object_key(self, source: ContentSource, item_data: Dict[str, any]) -> str:
        """
        Generate a storage object key for the content item.
        
        Format: {source_type}/{source_name_slug}/{guid}.{ext}
        Example: podcasts/npr-news/abc123def456.mp3
        
        Args:
            source: ContentSource
            item_data: Parsed entry data
            
        Returns:
            Object key string
        """
        # Sanitize source name
        source_slug = source.name.lower().replace(' ', '-').replace('/', '-')[:50]
        
        # Get extension from media URL
        ext = self._get_extension_from_url(item_data.get('media_url', '')) or '.mp3'
        
        # Use first 12 chars of GUID as filename
        filename = item_data['guid'][:12]
        
        return f"{source.type}s/{source_slug}/{filename}{ext}"
    
    def _create_guid(self, url: str) -> str:
        """Create a GUID from URL hash."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _parse_date(self, date_tuple: Optional[any]) -> datetime:
        """
        Parse RSS date tuple or return now.
        
        Args:
            date_tuple: time.struct_time from feedparser
            
        Returns:
            Timezone-aware datetime
        """
        if date_tuple:
            try:
                timestamp = mktime(date_tuple)
                dt = datetime.fromtimestamp(timestamp)
                return timezone.make_aware(dt)
            except Exception as e:
                logger.warning(f"Failed to parse date: {e}")
        
        return timezone.now()
    
    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """Get file extension from content type."""
        content_type_map = {
            'audio/mpeg': '.mp3',
            'audio/mp3': '.mp3',
            'audio/mp4': '.m4a',
            'video/mp4': '.mp4',
            'audio/wav': '.wav',
            'audio/ogg': '.ogg',
            'application/pdf': '.pdf',
        }
        
        for ct, ext in content_type_map.items():
            if ct in content_type.lower():
                return ext
        
        return None
    
    def _get_extension_from_url(self, url: str) -> Optional[str]:
        """Extract file extension from URL."""
        if not url:
            return None
        
        # Get path from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
        
        # Extract extension
        if '.' in path:
            ext = os.path.splitext(path)[1]
            if ext and len(ext) <= 5:  # Reasonable extension length
                return ext
        
        return None

