import json
import feedparser
from tqdm import tqdm
import os

# --- CONFIG ---
TAGS = ["artificial intelligence", "data visualization", "cryptography"]

RSS_FEEDS = {
    "Lex Fridman Podcast": "https://lexfridman.com/feed/podcast/",
    "Data Skeptic": "https://dataskeptic.com/feed/podcast/",
    "Science Vs": "https://gimletmedia.com/shows/science-vs/feed"
}

OUTPUT_FILE = "data/podcasts.json"

# --- FUNCTION TO FILTER EPISODES BY TAGS ---
def fetch_episodes_by_tags(tag_list, rss_feeds):
    all_episodes = []
    errors = []
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    for show_name, feed_url in tqdm(rss_feeds.items(), desc="Processing RSS feeds"):
        try:
            feed = feedparser.parse(feed_url)
            
            # Check for feed parsing errors
            if feed.bozo and feed.bozo_exception:
                errors.append(f"Feed parsing error for {show_name}: {feed.bozo_exception}")
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
                    
                    matched_tags = [tag for tag in tag_list if tag.lower() in combined_text]
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
                            "title": title,
                            "description": description,
                            "url": audio_url,
                            "source": show_name,
                            "tags": matched_tags
                        })
                except Exception as e:
                    errors.append(f"Error processing entry from {show_name}: {e}")
                    continue
                    
        except Exception as e:
            errors.append(f"Error fetching feed for {show_name} ({feed_url}): {e}")
            continue
    
    # Print errors if any
    if errors:
        print(f"\n⚠️  Encountered {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    return all_episodes

# --- MAIN EXECUTION ---
episodes = fetch_episodes_by_tags(TAGS, RSS_FEEDS)

# Save JSON
try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(episodes)} episodes to {OUTPUT_FILE}")
except Exception as e:
    print(f"❌ Error saving podcast data: {e}")
