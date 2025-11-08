#!/usr/bin/env python
"""
ETL Pipeline Verification Script

Run this script to verify that the ETL pipeline has completed successfully
and check the ingested content.

Usage:
    python verify_etl.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

from core.models import ContentSource, ContentItem
from django.utils import timezone
from datetime import timedelta

def main():
    print("=" * 60)
    print("ETL PIPELINE VERIFICATION")
    print("=" * 60)
    print()
    
    # 1. Check Content Sources
    print("1. CONTENT SOURCES")
    print("-" * 60)
    total_sources = ContentSource.objects.count()
    active_sources = ContentSource.objects.filter(is_active=True).count()
    print(f"Total Sources: {total_sources}")
    print(f"Active Sources: {active_sources}")
    print()
    
    # 2. Check Content Items
    print("2. CONTENT ITEMS")
    print("-" * 60)
    total_items = ContentItem.objects.count()
    print(f"Total Content Items Ingested: {total_items}")
    
    if total_items == 0:
        print("⚠️  WARNING: No content items found!")
        print("   Run: python manage.py run_etl")
        print()
        return
    
    print(f"✅ SUCCESS: {total_items} items ingested")
    print()
    
    # 3. Items by Source
    print("3. ITEMS BY SOURCE")
    print("-" * 60)
    sources_with_items = ContentSource.objects.filter(is_active=True).order_by('name')
    
    for source in sources_with_items:
        count = source.contentitem_set.count()
        if count > 0:
            print(f"✓ {source.name:<30} {count:>3} items")
        else:
            print(f"  {source.name:<30} {count:>3} items (none yet)")
    print()
    
    # 4. Recent Items
    print("4. LATEST 10 CONTENT ITEMS")
    print("-" * 60)
    latest_items = ContentItem.objects.order_by('-discovered_at')[:10]
    
    for i, item in enumerate(latest_items, 1):
        print(f"{i}. {item.title[:60]}")
        print(f"   Source: {item.source.name}")
        print(f"   Published: {item.published_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Discovered: {item.discovered_at.strftime('%Y-%m-%d %H:%M')}")
        if item.media_url:
            print(f"   Media: ✓ (URL: {item.media_url[:50]}...)")
        if item.storage_url:
            print(f"   Storage: ✓ ({item.storage_provider})")
        print()
    
    # 5. Storage Information
    print("5. STORAGE STATUS")
    print("-" * 60)
    items_with_storage = ContentItem.objects.exclude(storage_provider='none').count()
    items_without_storage = ContentItem.objects.filter(storage_provider='none').count()
    
    print(f"Items with cloud storage: {items_with_storage}")
    print(f"Items without storage (metadata only): {items_without_storage}")
    
    if items_without_storage == total_items:
        print("ℹ️  Storage provider is set to 'none' (local development mode)")
        print("   To enable storage, update .env with AWS S3 or Supabase credentials")
    print()
    
    # 6. Recent Activity
    print("6. RECENT INGESTION ACTIVITY")
    print("-" * 60)
    now = timezone.now()
    
    last_hour = ContentItem.objects.filter(
        discovered_at__gte=now - timedelta(hours=1)
    ).count()
    
    last_24h = ContentItem.objects.filter(
        discovered_at__gte=now - timedelta(days=1)
    ).count()
    
    print(f"Items ingested in last hour: {last_hour}")
    print(f"Items ingested in last 24 hours: {last_24h}")
    print()
    
    # 7. Content Type Breakdown
    print("7. CONTENT TYPE BREAKDOWN")
    print("-" * 60)
    podcasts = ContentItem.objects.filter(source__type='podcast').count()
    articles = ContentItem.objects.filter(source__type='article').count()
    
    print(f"Podcast episodes: {podcasts}")
    print(f"Articles: {articles}")
    print()
    
    # 8. Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if total_items > 0:
        print("✅ ETL Pipeline is working correctly!")
        print(f"✅ {total_items} content items successfully ingested")
        print(f"✅ {active_sources} active sources configured")
        
        if last_hour > 0:
            print(f"✅ Fresh content ingested in the last hour")
        
        print()
        print("Next steps:")
        print("- View content in admin panel: http://localhost:8000/admin")
        print("- Run ETL again: python manage.py run_etl")
        print("- Test AutoGen agents: See ETL_PIPELINE_GUIDE.md")
    else:
        print("⚠️  No content items found")
        print("Run: python manage.py run_etl")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

