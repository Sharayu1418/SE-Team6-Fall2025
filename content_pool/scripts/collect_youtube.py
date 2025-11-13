from youtubesearchpython import VideosSearch
import json
from tqdm import tqdm
import os

def collect_youtube_videos(tags, limit_per_tag=10):
    all_results = []
    errors = []
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    for tag in tqdm(tags, desc="Fetching YouTube content"):
        try:
            videos_search = VideosSearch(tag, limit=limit_per_tag)
            search_result = videos_search.result()
            
            # Check if result exists and has 'result' key
            if not search_result or 'result' not in search_result:
                errors.append(f"No results for tag: {tag}")
                continue
            
            results = search_result['result']
            
            if not results:
                errors.append(f"Empty results for tag: {tag}")
                continue
            
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
                        'link': video.get('link', ''),
                        'duration': video.get('duration'),
                        'published_time': video.get('publishedTime'),
                        'views': video.get('viewCount', {}).get('short') if isinstance(video.get('viewCount'), dict) else video.get('viewCount'),
                        'description': description,
                        'tag': tag
                    })
                except Exception as e:
                    errors.append(f"Error processing video for tag '{tag}': {e}")
                    continue
                    
        except Exception as e:
            errors.append(f"Error fetching YouTube content for tag '{tag}': {e}")
            continue
    
    # Save results
    try:
        with open('data/youtube.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(all_results)} YouTube entries to data/youtube.json")
    except Exception as e:
        print(f"❌ Error saving YouTube data: {e}")
        return
    
    # Print errors if any
    if errors:
        print(f"\n⚠️  Encountered {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

if __name__ == "__main__":
    tags = ["AI ethics", "climate change", "cryptography", "data visualization"]
    collect_youtube_videos(tags)
