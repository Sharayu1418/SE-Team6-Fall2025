from youtubesearchpython import VideosSearch
import json
from tqdm import tqdm

def collect_youtube_videos(tags, limit_per_tag=10):
    all_results = []
    for tag in tqdm(tags, desc="Fetching YouTube content"):
        videos_search = VideosSearch(tag, limit=limit_per_tag)
        results = videos_search.result()['result']
        
        for video in results:
            all_results.append({
                'title': video['title'],
                'channel': video['channel']['name'],
                'link': video['link'],
                'duration': video.get('duration'),
                'published_time': video.get('publishedTime'),
                'views': video.get('viewCount', {}).get('short'),
                'description': video.get('descriptionSnippet', [{'text': ''}])[0]['text'] if video.get('descriptionSnippet') else '',
                'tag': tag
            })
    
    with open('data/youtube.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(all_results)} YouTube entries to data/youtube.json")

if __name__ == "__main__":
    tags = ["AI ethics", "climate change", "cryptography", "data visualization"]
    collect_youtube_videos(tags)
