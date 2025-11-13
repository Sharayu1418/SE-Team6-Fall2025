#!/usr/bin/env python3
"""
Content Pool Collection Orchestrator

This script coordinates the collection of content from YouTube, podcasts, and webpages.
It can run all collectors or individual ones based on command-line arguments.
"""

import argparse
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def main():
    parser = argparse.ArgumentParser(
        description='Collect content from YouTube, podcasts, and webpages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --all                    # Run all collectors
  python main.py --youtube --podcasts     # Run YouTube and podcast collectors
  python main.py --youtube --limit 5       # Collect YouTube with custom limit
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all content collectors (YouTube, podcasts, webpages)'
    )
    parser.add_argument(
        '--youtube',
        action='store_true',
        help='Collect YouTube videos'
    )
    parser.add_argument(
        '--podcasts',
        action='store_true',
        help='Collect podcast episodes from RSS feeds'
    )
    parser.add_argument(
        '--webpages',
        action='store_true',
        help='Collect webpages (Wikipedia + news articles)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Limit per tag for YouTube collection (default: 10)'
    )
    parser.add_argument(
        '--tags',
        nargs='+',
        help='Custom tags to use (overrides default tags)'
    )
    
    args = parser.parse_args()
    
    # If no specific collectors are selected, default to --all
    if not any([args.all, args.youtube, args.podcasts, args.webpages]):
        args.all = True
    
    # Determine which collectors to run
    collectors = []
    if args.all:
        collectors = ['youtube', 'podcasts', 'webpages']
    else:
        if args.youtube:
            collectors.append('youtube')
        if args.podcasts:
            collectors.append('podcasts')
        if args.webpages:
            collectors.append('webpages')
    
    print(f"🚀 Starting content collection for: {', '.join(collectors)}\n")
    
    results = {}
    
    # Run YouTube collector
    if 'youtube' in collectors:
        print("=" * 60)
        print("📹 Collecting YouTube videos...")
        print("=" * 60)
        try:
            from collect_youtube import collect_youtube_videos
            tags = args.tags if args.tags else ["AI ethics", "climate change", "cryptography", "data visualization"]
            collect_youtube_videos(tags, limit_per_tag=args.limit)
            results['youtube'] = 'success'
        except Exception as e:
            print(f"❌ YouTube collection failed: {e}")
            results['youtube'] = f'failed: {e}'
        print()
    
    # Run Podcast collector
    if 'podcasts' in collectors:
        print("=" * 60)
        print("🎙️  Collecting podcast episodes...")
        print("=" * 60)
        try:
            from collect_podcasts import fetch_episodes_by_tags, RSS_FEEDS, OUTPUT_FILE
            import json
            
            tags = args.tags if args.tags else ["artificial intelligence", "data visualization", "cryptography"]
            episodes = fetch_episodes_by_tags(tags, RSS_FEEDS)
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(episodes, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(episodes)} episodes to {OUTPUT_FILE}")
            results['podcasts'] = 'success'
        except Exception as e:
            print(f"❌ Podcast collection failed: {e}")
            results['podcasts'] = f'failed: {e}'
        print()
    
    # Run Webpage collector
    if 'webpages' in collectors:
        print("=" * 60)
        print("📄 Collecting webpages...")
        print("=" * 60)
        try:
            from collect_webpages import (
                fetch_wikipedia_summary, fetch_news_articles,
                OUTPUT_FILE, NEWS_SEARCH_URLS, MAX_ARTICLES_PER_TAG
            )
            from tqdm import tqdm
            import json
            
            tags = args.tags if args.tags else ["artificial intelligence", "data visualization", "climate change"]
            all_content = []
            
            for tag in tqdm(tags, desc="Collecting webpages"):
                wiki = fetch_wikipedia_summary(tag)
                if wiki:
                    all_content.append(wiki)
                news_articles = fetch_news_articles(tag)
                all_content.extend(news_articles)
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_content, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(all_content)} webpage entries to {OUTPUT_FILE}")
            results['webpages'] = 'success'
        except Exception as e:
            print(f"❌ Webpage collection failed: {e}")
            results['webpages'] = f'failed: {e}'
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Collection Summary")
    print("=" * 60)
    for collector, status in results.items():
        status_icon = "✅" if status == "success" else "❌"
        print(f"{status_icon} {collector.capitalize()}: {status}")
    
    # Exit code based on results
    if all(status == 'success' for status in results.values()):
        print("\n🎉 All collections completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some collections failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
