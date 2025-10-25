import json
import feedparser
from tqdm import tqdm

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
    
    for show_name, feed_url in tqdm(rss_feeds.items(), desc="Processing RSS feeds"):
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            title = entry.title
            description = entry.get("summary", "")
            combined_text = (title + " " + description).lower()
            
            matched_tags = [tag for tag in tag_list if tag.lower() in combined_text]
            if matched_tags:
                audio_url = entry.enclosures[0].href if entry.enclosures else None
                all_episodes.append({
                    "title": title,
                    "description": description,
                    "url": audio_url,
                    "source": show_name,
                    "tags": matched_tags
                })
    return all_episodes

# --- MAIN EXECUTION ---
episodes = fetch_episodes_by_tags(TAGS, RSS_FEEDS)

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(episodes, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(episodes)} episodes to {OUTPUT_FILE}")
