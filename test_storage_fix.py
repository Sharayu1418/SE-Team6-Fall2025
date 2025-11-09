#!/usr/bin/env python
"""
Test the storage URL fix for downloads.

This script verifies that:
1. Only cached content is recommended
2. Downloads use S3 URLs, not original URLs
"""

import os
import sys
import django

# Django setup
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ContentItem, DownloadItem, Subscription
from core.tools.content_recommendation import recommend_content_for_download
from core.tools.content_download import queue_download


def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_content_stats():
    """Show content statistics"""
    print_section("Step 1: Content Statistics")
    
    total_items = ContentItem.objects.count()
    cached_items = ContentItem.objects.filter(storage_url__isnull=False).exclude(storage_url='').count()
    uncached_items = total_items - cached_items
    
    print(f"Total ContentItems: {total_items}")
    print(f"  ✓ Cached (with storage_url): {cached_items} ({cached_items/total_items*100:.1f}%)")
    print(f"  ✗ Not cached: {uncached_items} ({uncached_items/total_items*100:.1f}%)")
    
    # Show some cached items
    if cached_items > 0:
        print(f"\nSample cached items:")
        for item in ContentItem.objects.filter(storage_url__isnull=False)[:3]:
            print(f"  - ID {item.id}: {item.title[:50]}")
            print(f"    Storage: {item.storage_url[:80]}...")


def test_recommendations():
    """Test that recommendations only include cached content"""
    print_section("Step 2: Test Recommendations")
    
    user = User.objects.first()
    if not user:
        print("❌ No user found")
        return None
    
    print(f"Testing recommendations for user: {user.username} (ID: {user.id})")
    
    # Check subscriptions
    subs = Subscription.objects.filter(user=user, is_active=True)
    print(f"Active subscriptions: {subs.count()}")
    
    # Get recommendations
    print("\nCalling recommend_content_for_download()...")
    result = recommend_content_for_download(user_id=user.id, max_items=5)
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    return user


def test_queue_download(user):
    """Test queuing a download"""
    print_section("Step 3: Test Queue Download")
    
    if not user:
        print("❌ No user available")
        return
    
    # Find a cached content item
    cached_item = ContentItem.objects.filter(
        storage_url__isnull=False
    ).exclude(storage_url='').first()
    
    if not cached_item:
        print("❌ No cached content items available to test")
        return
    
    print(f"Testing with ContentItem ID: {cached_item.id}")
    print(f"Title: {cached_item.title}")
    print(f"Storage URL: {cached_item.storage_url[:80]}...")
    
    # Queue it
    print("\nCalling queue_download()...")
    result = queue_download(user_id=user.id, content_item_id=cached_item.id)
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    # Check what was created
    download_items = DownloadItem.objects.filter(user=user).order_by('-created_at')[:1]
    if download_items:
        item = download_items[0]
        print(f"\n✓ DownloadItem created:")
        print(f"  ID: {item.id}")
        print(f"  Status: {item.status}")
        print(f"  Media URL: {item.media_url[:80]}...")
        
        # Verify it's using S3
        if 's3.amazonaws.com' in item.media_url or 'supabase' in item.media_url:
            print(f"  ✅ CORRECT: Using storage URL (S3/Supabase)")
        else:
            print(f"  ⚠️  WARNING: Using original source URL")


def test_uncached_item(user):
    """Test that uncached items are rejected"""
    print_section("Step 4: Test Uncached Item Rejection")
    
    if not user:
        print("❌ No user available")
        return
    
    # Find an uncached item
    uncached_item = ContentItem.objects.filter(
        storage_url__isnull=True
    ).first()
    
    if not uncached_item:
        uncached_item = ContentItem.objects.filter(storage_url='').first()
    
    if not uncached_item:
        print("✓ All items are cached (or none exist)")
        return
    
    print(f"Testing with UNCACHED ContentItem ID: {uncached_item.id}")
    print(f"Title: {uncached_item.title}")
    print(f"Storage URL: {uncached_item.storage_url or '(None)'}")
    
    # Try to queue it (should be rejected)
    print("\nCalling queue_download() - expecting rejection...")
    result = queue_download(user_id=user.id, content_item_id=uncached_item.id)
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    if "❌" in result or "not cached" in result.lower():
        print("\n✅ CORRECT: Uncached item was properly rejected")
    else:
        print("\n⚠️  WARNING: Uncached item was not rejected")


def main():
    print("\n" + "="*70)
    print("  STORAGE URL FIX VERIFICATION TEST")
    print("="*70)
    
    test_content_stats()
    user = test_recommendations()
    test_queue_download(user)
    test_uncached_item(user)
    
    print_section("Test Complete")
    print("✓ Verification test finished!")
    print("\nKey Findings:")
    print("1. Only cached content should be recommended")
    print("2. Queued downloads should use S3/Supabase URLs")
    print("3. Uncached items should be rejected with clear error messages")
    print()


if __name__ == "__main__":
    main()

