# downloader/services.py

import yt_dlp
import requests
from urllib.parse import urlparse
from .models import DownloadedContent
from django.core.files.base import ContentFile
from django.conf import settings
import os

def _download_with_yt_dlp(content_instance, audio_only=False):
    """Handles downloading from media platforms like YouTube."""
    # Ensure temp directory exists
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    output_template = os.path.join(temp_dir, '%(id)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        # Windows can hold onto .part files (antivirus, indexing, etc.) causing
        # rename failures.  Disable part-files and allow overwrites so yt-dlp
        # writes directly to the final filename.
        'nopart': True,
        'overwrites': True,
        'windowsfilenames': True,
    }

    if audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # It requests separate best video and audio streams and merges them with FFmpeg.
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(content_instance.source_url, download=True)
        file_path = ydl.prepare_filename(info_dict)
        file_name = os.path.basename(file_path)

        with open(file_path, 'rb') as f:
            content_instance.content_file.save(file_name, ContentFile(f.read()))

        content_instance.title = info_dict.get('title', 'N/A')
        content_instance.content_type = 'audio' if audio_only else 'video'
        content_instance.metadata = {"yt_dlp_info": "Metadata stored after successful download"}
        os.remove(file_path)

def _download_generic_file(content_instance):
    """Handles downloading generic files like PDFs, HTML, etc., with robust error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Use a timeout to prevent hanging on unresponsive servers
        with requests.get(content_instance.source_url, stream=True, headers=headers, timeout=30) as response:
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            content_type = response.headers.get('Content-Type', '').lower()
            
            # Reject if the content type is clearly not text-like
            if 'video' in content_type or 'audio' in content_type or 'image' in content_type:
                raise ValueError(f"Invalid content type for 'TEXT' download: {content_type}")

            # Try to get a filename from the URL
            parsed_url = urlparse(content_instance.source_url)
            file_name = os.path.basename(parsed_url.path) or "downloaded_file"

            content_instance.content_file.save(file_name, ContentFile(response.content))
            content_instance.title = file_name
            content_instance.content_type = content_type or 'application/octet-stream'
            content_instance.metadata = {"headers": dict(response.headers)}

    # Catch specific request errors
    except requests.exceptions.Timeout:
        raise ConnectionError("Download timed out after 30 seconds.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during download: {e}")


def _download_direct_media(content_instance, expected_kind='audio'):
    """Download media files directly without requiring FFmpeg."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with requests.get(content_instance.source_url, stream=True, headers=headers, timeout=60) as response:
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            if expected_kind == 'audio' and 'audio' not in content_type:
                raise ValueError(f"Expected audio content but received '{content_type}'")

            parsed_url = urlparse(content_instance.source_url)
            file_name = os.path.basename(parsed_url.path) or 'downloaded_media'

            content_instance.content_file.save(file_name, ContentFile(response.content))
            content_instance.title = file_name
            content_instance.content_type = content_type or 'application/octet-stream'
            content_instance.metadata = {
                "headers": dict(response.headers),
                "downloaded_via": "direct"
            }

    except requests.exceptions.Timeout:
        raise ConnectionError("Media download timed out.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during media download: {e}")


def download_media(content_id):
    """
    Dispatcher function that calls the appropriate download handler.
    """
    try:
        content_instance = DownloadedContent.objects.get(id=content_id)
    except DownloadedContent.DoesNotExist:
        print(f"Content with ID {content_id} not found.")
        return

    content_instance.status = DownloadedContent.DownloadStatus.DOWNLOADING
    content_instance.save()

    try:
        # Dispatch based on the requested type
        if content_instance.requested_type == DownloadedContent.DownloadType.VIDEO:
            _download_with_yt_dlp(content_instance, audio_only=False)
        elif content_instance.requested_type == DownloadedContent.DownloadType.AUDIO:
            url_lower = content_instance.source_url.lower()
            if any(host in url_lower for host in ['youtube.com', 'youtu.be', 'soundcloud.com', 'spotify.com']):
                _download_with_yt_dlp(content_instance, audio_only=True)
            else:
                _download_direct_media(content_instance, expected_kind='audio')
        elif content_instance.requested_type == DownloadedContent.DownloadType.TEXT:
            _download_generic_file(content_instance)

        content_instance.status = DownloadedContent.DownloadStatus.COMPLETED
        content_instance.save()

    except Exception as e:
        print(f"Download failed for {content_instance.source_url}: {e}")
        content_instance.status = DownloadedContent.DownloadStatus.FAILED
        content_instance.metadata = {"error": str(e)}
        content_instance.save()