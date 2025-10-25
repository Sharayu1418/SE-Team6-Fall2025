import json
from tqdm import tqdm
import urllib.parse
import requests
from newspaper import Article
import wikipedia

# --- CONFIG ---
TAGS = ["artificial intelligence", "data visualization", "climate change"]
NEWS_SEARCH_URLS = [
    "https://www.bbc.com/search?q={query}",
    "https://www.nytimes.com/search?query={query}"
]
OUTPUT_FILE = "data/webpages.json"
MAX_ARTICLES_PER_TAG = 5

# --- FUNCTION TO FETCH WIKIPEDIA SUMMARY ---
def fetch_wikipedia_summary(tag):
    try:
        summary = wikipedia.summary(tag, sentences=3)
        url = f"https://en.wikipedia.org/wiki/{tag.replace(' ', '_')}"
        return {
            "title": tag,
            "url": url,
            "description": summary,
            "tags": [tag],
            "source": "wikipedia"
        }
    except Exception as e:
        print(f"Error fetching Wikipedia for {tag}: {e}")
        return None

# --- FUNCTION TO FETCH NEWS ARTICLES ---
def fetch_news_articles(tag):
    articles = []
    for search_template in NEWS_SEARCH_URLS:
        url = search_template.format(query=urllib.parse.quote(tag))
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            # Parse top article links
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=True)[:MAX_ARTICLES_PER_TAG]
            for a in links:
                href = a['href']
                if href.startswith("/"):
                    href = urllib.parse.urljoin(search_template, href)
                # Extract full article text using newspaper3k
                try:
                    article = Article(href)
                    article.download()
                    article.parse()
                    description = article.text[:2000]  # truncate if too long
                    title = article.title or a.get_text(strip=True) or href
                    articles.append({
                        "title": title,
                        "url": href,
                        "description": description,
                        "tags": [tag],
                        "source": "news"
                    })
                except Exception as e:
                    print(f"Error parsing article {href}: {e}")
        except Exception as e:
            print(f"Error fetching news search page for {tag}: {e}")
    return articles

# --- MAIN EXECUTION ---
all_content = []
for tag in tqdm(TAGS, desc="Collecting webpages"):
    # Wikipedia
    wiki = fetch_wikipedia_summary(tag)
    if wiki:
        all_content.append(wiki)
    # News articles
    news_articles = fetch_news_articles(tag)
    all_content.extend(news_articles)

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_content, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(all_content)} webpage entries to {OUTPUT_FILE}")
