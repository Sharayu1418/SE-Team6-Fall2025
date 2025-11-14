"""
Content Discovery Service

Integrates content_pool functionality for discovering content based on user tags.
This service adapts content_pool collection scripts to work within Django context.
"""

import sys
import os
from pathlib import Path
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Import dependencies directly (functions will be implemented inline)
try:
    from youtubesearchpython import VideosSearch
    import feedparser
    import wikipedia
    from bs4 import BeautifulSoup
    import urllib.parse
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Content pool dependencies not available: {e}")
    VideosSearch = None
    DEPENDENCIES_AVAILABLE = False

# RSS Feeds for podcasts
PODCAST_RSS_FEEDS = {
    "Lex Fridman Podcast": "https://lexfridman.com/feed/podcast/",
    "Data Skeptic": "https://dataskeptic.com/feed/podcast/",
    "Science Vs": "https://gimletmedia.com/shows/science-vs/feed"
}

# News search URLs
NEWS_SEARCH_URLS = [
    "https://www.bbc.com/search?q={query}",
    "https://www.nytimes.com/search?query={query}"
]


def discover_youtube_content(tags: List[str], limit_per_tag: int = 10) -> Dict:
    """
    Discover YouTube videos based on tags.
    Returns dictionary with results and errors.
    """
    if VideosSearch is None:
        return {'results': [], 'errors': ['YouTube search not available - dependencies missing']}
    
    all_results = []
    errors = []
    
    for tag in tags:
        try:
            videos_search = VideosSearch(tag, limit=limit_per_tag)
            search_result = videos_search.result()
            
            if not search_result:
                errors.append(f"No results for tag: {tag}")
                continue
            
            # Handle different response formats
            results = None
            if isinstance(search_result, dict):
                results = search_result.get('result')
            elif isinstance(search_result, list):
                results = search_result
            
            # Ensure results is iterable
            if results is None:
                errors.append(f"No results for tag: {tag}")
                continue
                
            if not isinstance(results, (list, tuple)):
                # If it's not a list, try to convert or skip
                try:
                    results = list(results) if hasattr(results, '__iter__') else []
                except:
                    results = []
            
            if not results:
                errors.append(f"Empty results for tag: {tag}")
                continue
            
            # Now safely iterate
            for video in results:
                try:
                    # Safely extract channel name
                    channel_name = 'Unknown'
                    if 'channel' in video and video['channel']:
                        if isinstance(video['channel'], dict) and 'name' in video['channel']:
                            channel_name = video['channel']['name']
                        elif isinstance(video['channel'], str):
                            channel_name = video['channel']
                    
                    # Safely extract description
                    description = ''
                    if video.get('descriptionSnippet'):
                        if isinstance(video['descriptionSnippet'], list) and len(video['descriptionSnippet']) > 0:
                            if isinstance(video['descriptionSnippet'][0], dict) and 'text' in video['descriptionSnippet'][0]:
                                description = video['descriptionSnippet'][0]['text']
                        elif isinstance(video['descriptionSnippet'], str):
                            description = video['descriptionSnippet']
                    
                    all_results.append({
                        'title': video.get('title', 'Untitled'),
                        'channel': channel_name,
                        'url': video.get('link', ''),
                        'duration': video.get('duration'),
                        'published_time': video.get('publishedTime'),
                        'views': video.get('viewCount', {}).get('short') if isinstance(video.get('viewCount'), dict) else video.get('viewCount'),
                        'description': description,
                        'tag': tag,
                        'type': 'video',
                        'source': 'youtube'
                    })
                except Exception as e:
                    errors.append(f"Error processing video for tag '{tag}': {e}")
                    continue
                    
        except Exception as e:
            errors.append(f"Error fetching YouTube content for tag '{tag}': {e}")
            continue
    
    return {'results': all_results, 'errors': errors}


def discover_podcast_content(tags: List[str]) -> Dict:
    """
    Discover podcast episodes based on tags.
    Returns dictionary with results and errors.
    """
    if not DEPENDENCIES_AVAILABLE:
        return {'results': [], 'errors': ['Podcast search not available - dependencies missing']}
    
    all_episodes = []
    errors = []
    
    for show_name, feed_url in PODCAST_RSS_FEEDS.items():
        try:
            # Parse feed (feedparser handles SSL internally)
            feed = feedparser.parse(feed_url)
            
            # Check for feed parsing errors
            if feed.bozo and feed.bozo_exception:
                error_msg = str(feed.bozo_exception)
                # Don't fail completely - try to use what we can parse
                if not hasattr(feed, 'entries') or not feed.entries:
                    errors.append(f"Feed parsing error for {show_name}: {error_msg[:100]}")
                    continue
            
            # Check if feed has entries
            if not hasattr(feed, 'entries') or not feed.entries:
                errors.append(f"No entries found in feed for {show_name}")
                continue
            
            for entry in feed.entries:
                try:
                    title = entry.get("title", "Untitled")
                    description = entry.get("summary", "")
                    combined_text = (title + " " + description).lower()
                    
                    matched_tags = [tag for tag in tags if tag.lower() in combined_text]
                    if matched_tags:
                        # Safely extract audio URL
                        audio_url = None
                        if hasattr(entry, 'enclosures') and entry.enclosures:
                            if isinstance(entry.enclosures, list) and len(entry.enclosures) > 0:
                                if hasattr(entry.enclosures[0], 'href'):
                                    audio_url = entry.enclosures[0].href
                                elif isinstance(entry.enclosures[0], dict) and 'href' in entry.enclosures[0]:
                                    audio_url = entry.enclosures[0]['href']
                                elif isinstance(entry.enclosures[0], str):
                                    audio_url = entry.enclosures[0]
                        
                        all_episodes.append({
                            'title': title,
                            'url': audio_url or entry.get('link', ''),
                            'description': description,
                            'source': show_name,
                            'tags': matched_tags,
                            'type': 'audio'
                        })
                except Exception as e:
                    errors.append(f"Error processing entry from {show_name}: {e}")
                    continue
                    
        except Exception as e:
            errors.append(f"Error fetching feed for {show_name} ({feed_url}): {e}")
            continue
    
    return {'results': all_episodes, 'errors': errors}


def discover_webpage_content(tags: List[str], max_per_tag: int = 3) -> Dict:
    """
    Discover webpages (Wikipedia + news) based on tags.
    Returns dictionary with results and errors.
    """
    if not DEPENDENCIES_AVAILABLE:
        return {'results': [], 'errors': ['Webpage search not available - dependencies missing']}
    
    all_content = []
    errors = []
    
    for tag in tags:
        # Wikipedia - sanitize tag name
        try:
            # Clean tag name: remove special characters, normalize spaces
            clean_tag = tag.strip().replace(';', '').replace(':', '').replace('/', '')
            if not clean_tag:
                continue
                
            # Try searching first, then get summary
            try:
                search_results = wikipedia.search(clean_tag, results=1)
                if search_results:
                    page_title = search_results[0]
                else:
                    page_title = clean_tag
            except:
                page_title = clean_tag
            
            summary = wikipedia.summary(page_title, sentences=3)
            url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            all_content.append({
                'title': page_title,
                'url': url,
                'description': summary,
                'tags': [tag],
                'source': 'wikipedia',
                'type': 'text'
            })
        except wikipedia.exceptions.DisambiguationError as e:
            # If disambiguation, use first option
            try:
                page_title = e.options[0]
                summary = wikipedia.summary(page_title, sentences=3)
                url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                all_content.append({
                    'title': page_title,
                    'url': url,
                    'description': summary,
                    'tags': [tag],
                    'source': 'wikipedia',
                    'type': 'text'
                })
            except:
                errors.append(f"Wikipedia disambiguation error for {tag}")
        except Exception as e:
            errors.append(f"Error fetching Wikipedia for {tag}: {str(e)[:100]}")
        
        # News articles (simplified - just return Wikipedia for now to avoid scraping issues)
        # Full news scraping can be added later if needed
    
    return {'results': all_content, 'errors': errors}


def discover_content(tags: List[str], sources: List[str] = None, limit_per_source: int = 10) -> Dict:
    """
    Main content discovery function.
    
    Args:
        tags: List of tags to search for (e.g., ["AI", "Technology"])
        sources: List of sources to search ("youtube", "podcasts", "webpages")
                If None, searches all sources
        limit_per_source: Limit results per source per tag
    
    Returns:
        Dictionary with:
        - 'results': List of discovered content items
        - 'errors': List of error messages
        - 'summary': Statistics
    """
    if not tags:
        return {'results': [], 'errors': ['No tags provided'], 'summary': {}}
    
    if sources is None:
        sources = ['youtube', 'podcasts', 'webpages']
    
    all_results = []
    all_errors = []
    
    # Discover from each source
    if 'youtube' in sources:
        logger.info(f"Discovering YouTube content for tags: {tags}")
        youtube_data = discover_youtube_content(tags, limit_per_tag=limit_per_source)
        all_results.extend(youtube_data['results'])
        all_errors.extend(youtube_data['errors'])
    
    if 'podcasts' in sources:
        logger.info(f"Discovering podcast content for tags: {tags}")
        podcast_data = discover_podcast_content(tags)
        all_results.extend(podcast_data['results'])
        all_errors.extend(podcast_data['errors'])
    
    if 'webpages' in sources:
        logger.info(f"Discovering webpage content for tags: {tags}")
        webpage_data = discover_webpage_content(tags, max_per_tag=limit_per_source)
        all_results.extend(webpage_data['results'])
        all_errors.extend(webpage_data['errors'])
    
    # Summary statistics
    summary = {
        'total_results': len(all_results),
        'youtube_count': len([r for r in all_results if r.get('source') == 'youtube']),
        'podcast_count': len([r for r in all_results if r.get('source') == 'podcast']),
        'webpage_count': len([r for r in all_results if r.get('source') in ['wikipedia', 'news']]),
        'error_count': len(all_errors)
    }
    
    return {
        'results': all_results,
        'errors': all_errors,
        'summary': summary
    }

