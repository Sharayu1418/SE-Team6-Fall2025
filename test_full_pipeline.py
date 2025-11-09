#!/usr/bin/env python
"""
Complete ETL and AutoGen Pipeline Test

This script tests the entire flow:
1. Run ETL pipeline to ingest content from RSS feeds
2. Use RoundRobinGroupChat to discover and queue downloads
3. Verify downloads were processed
"""

import os
import sys
import logging
import asyncio
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')

import django
django.setup()

from django.contrib.auth.models import User
from core.models import (
    ContentSource,
    ContentItem,
    Subscription,
    UserPreference,
    DownloadItem
)
from core.services.content_ingestion import ContentIngestionService
from core.agents.groupchat import create_round_robin_team

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print_section("STEP 1: Checking Prerequisites")
    
    # Check user
    users = User.objects.all()
    if not users.exists():
        logger.error("❌ No users found. Please create a user first.")
        return False
    
    test_user = users.first()
    logger.info(f"✓ Found test user: {test_user.username} (ID: {test_user.id})")
    
    # Check preferences
    prefs, created = UserPreference.objects.get_or_create(
        user=test_user,
        defaults={
            'topics': ['technology', 'science', 'AI', 'programming', 'news'],
            'max_daily_items': 10,
            'max_storage_mb': 500,
        }
    )
    
    if created:
        logger.info(f"✓ Created preferences for {test_user.username}")
    else:
        logger.info(f"✓ Preferences exist for {test_user.username}")
    
    logger.info(f"  Topics: {', '.join(prefs.topics)}")
    
    # Check content sources
    sources = ContentSource.objects.filter(is_active=True)
    if not sources.exists():
        logger.error("❌ No active content sources found.")
        logger.info("   Run: python manage.py seed_defaults")
        return False
    
    logger.info(f"✓ Found {sources.count()} active content sources:")
    for source in sources:
        logger.info(f"  - {source.name} ({source.type})")
    
    # Check/create subscriptions
    for source in sources[:3]:  # Subscribe to first 3 sources
        sub, created = Subscription.objects.get_or_create(
            user=test_user,
            source=source,
            defaults={'priority': 3}
        )
        if created:
            logger.info(f"✓ Subscribed to: {source.name}")
    
    subs = Subscription.objects.filter(user=test_user, is_active=True)
    logger.info(f"✓ User has {subs.count()} active subscriptions")
    
    return True, test_user


def run_etl_pipeline():
    """Run the ETL pipeline to ingest content"""
    print_section("STEP 2: Running ETL Pipeline")
    
    logger.info("Starting content ingestion from RSS feeds...")
    
    # Get initial count
    initial_count = ContentItem.objects.count()
    logger.info(f"Current ContentItem count: {initial_count}")
    
    try:
        service = ContentIngestionService(storage_provider='aws_s3')
        results = service.ingest_all_sources()
        
        logger.info(f"✓ ETL Pipeline completed!")
        logger.info(f"  Sources processed: {results.get('sources_processed', 0)}")
        logger.info(f"  New items added: {results.get('total_items_added', 0)}")
        logger.info(f"  Errors: {results.get('errors', 0)}")
        
        # Show per-source details
        if 'details' in results:
            logger.info("\n  Details by source:")
            for source_name, count in results['details'].items():
                if isinstance(count, int):
                    logger.info(f"    {source_name}: {count} items")
                else:
                    logger.info(f"    {source_name}: {count}")
        
        # Final count
        final_count = ContentItem.objects.count()
        logger.info(f"\nTotal ContentItem count: {final_count}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_available_content(user: User):
    """Display available content for the user"""
    print_section("STEP 3: Available Content Preview")
    
    # Get subscribed sources
    subs = Subscription.objects.filter(
        user=user,
        is_active=True
    ).select_related('source')
    
    source_ids = [sub.source_id for sub in subs]
    
    # Get recent content from subscribed sources
    recent_items = ContentItem.objects.filter(
        source_id__in=source_ids
    ).select_related('source').order_by('-published_at')[:10]
    
    if not recent_items:
        logger.warning("⚠️  No content items found from subscribed sources")
        return
    
    logger.info(f"Recent content from your subscriptions (showing 10/{recent_items.count()}):\n")
    
    for idx, item in enumerate(recent_items, 1):
        storage = "✓ S3" if item.storage_url else "✗ No cache"
        logger.info(
            f"{idx}. [{item.id}] {item.title[:60]}\n"
            f"   Source: {item.source.name}\n"
            f"   Published: {item.published_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"   Storage: {storage}"
        )
        if idx < len(recent_items):
            print()


async def run_autogen_team(user: User):
    """Run the AutoGen RoundRobinGroupChat team"""
    print_section("STEP 4: Running AutoGen RoundRobinGroupChat Team")
    
    logger.info("Creating agent team...")
    
    try:
        # Create the team
        team = create_round_robin_team(max_turns=15, team_name="ETL_Test_Pipeline")
        
        logger.info("✓ Team created successfully")
        logger.info("  Agents: ContentDiscoveryAgent, ContentDownloadAgent, ContentSummarizerAgent")
        
        # Define the task
        task = f"""
User ID: {user.id}
Username: {user.username}

Task: I need you to recommend new content for me to download and then queue the downloads.

Here's what I need:
1. Discovery Agent: Find and recommend 5 content items for me based on my subscriptions and preferences
2. Download Agent: Queue ALL the recommended items for download
3. Download Agent: After queuing, process the download queue to start the background tasks
4. Summarizer Agent: Provide a brief summary of what was accomplished

Please work together to complete this task. When done, report what was accomplished.
"""
        
        logger.info("\n📋 Task sent to team:")
        logger.info("-" * 70)
        logger.info(task.strip())
        logger.info("-" * 70 + "\n")
        
        logger.info("🤖 Starting agent conversation...\n")
        
        # Run the team
        result = await team.run(task=task)
        
        logger.info("\n✓ Agent conversation completed!")
        logger.info(f"  Stop reason: {result.stop_reason}")
        logger.info(f"  Total messages: {len(result.messages)}")
        
        # Display conversation
        print_section("Agent Conversation")
        
        for idx, msg in enumerate(result.messages, 1):
            source_name = getattr(msg, 'source', 'Unknown')
            content = getattr(msg, 'content', str(msg))
            
            logger.info(f"\n[Message {idx}] {source_name}:")
            logger.info("-" * 70)
            logger.info(content)
        
        return True
    
    except Exception as e:
        logger.error(f"❌ AutoGen team failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_downloads(user: User):
    """Verify that downloads were queued and processed"""
    print_section("STEP 5: Verifying Downloads")
    
    # Get download items
    downloads = DownloadItem.objects.filter(
        user=user
    ).select_related('source').order_by('-created_at')
    
    if not downloads.exists():
        logger.error("❌ No download items found!")
        return False
    
    logger.info(f"✓ Found {downloads.count()} download items\n")
    
    # Group by status
    status_counts = {}
    for download in downloads:
        status_counts[download.status] = status_counts.get(download.status, 0) + 1
    
    logger.info("Status breakdown:")
    for status, count in status_counts.items():
        logger.info(f"  {status}: {count}")
    
    # Show recent downloads
    logger.info(f"\nRecent downloads (showing 5):\n")
    
    for idx, download in enumerate(downloads[:5], 1):
        logger.info(
            f"{idx}. [{download.id}] {download.title[:60]}\n"
            f"   Source: {download.source.name}\n"
            f"   Status: {download.status}\n"
            f"   Created: {download.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if download.local_file_path:
            logger.info(f"   Local path: {download.local_file_path}")
            
            # Check if file exists
            if os.path.exists(download.local_file_path):
                file_size = os.path.getsize(download.local_file_path)
                size_mb = file_size / (1024 * 1024)
                logger.info(f"   File exists: ✓ ({size_mb:.2f} MB)")
            else:
                logger.info(f"   File exists: ✗")
        
        if download.error_message:
            logger.info(f"   Error: {download.error_message}")
        
        if idx < len(downloads[:5]):
            print()
    
    return True


def check_download_directory(user: User):
    """Check the download directory for files"""
    print_section("STEP 6: Checking Download Directory")
    
    download_dir = f"/Users/anitejsrivastava/Documents/SE-Team6-Fall2025-anitej-etl-pipeline/media/downloads/user_{user.id}"
    
    logger.info(f"Download directory: {download_dir}")
    
    if not os.path.exists(download_dir):
        logger.warning(f"⚠️  Directory does not exist yet")
        logger.info("   This is normal if downloads are still processing in the background")
        return
    
    # List files
    files = []
    for root, dirs, filenames in os.walk(download_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            file_size = os.path.getsize(filepath)
            files.append((filename, file_size))
    
    if not files:
        logger.warning("⚠️  No files found in download directory")
        logger.info("   Downloads may still be processing in the background")
        return
    
    logger.info(f"\n✓ Found {len(files)} file(s):\n")
    
    for filename, size in files:
        size_mb = size / (1024 * 1024)
        logger.info(f"  - {filename} ({size_mb:.2f} MB)")


def main():
    """Main test execution"""
    print("\n" + "=" * 70)
    print("  SMARTCACHE ETL + AUTOGEN FULL PIPELINE TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Step 1: Prerequisites
    result = check_prerequisites()
    if not result:
        logger.error("\n❌ Prerequisites not met. Exiting.")
        return
    
    success, test_user = result
    
    # Step 2: Run ETL
    if not run_etl_pipeline():
        logger.error("\n❌ ETL pipeline failed. Exiting.")
        return
    
    # Step 3: Show available content
    show_available_content(test_user)
    
    # Step 4: Run AutoGen team
    success = asyncio.run(run_autogen_team(test_user))
    
    if not success:
        logger.error("\n❌ AutoGen team failed.")
        return
    
    # Step 5: Verify downloads
    verify_downloads(test_user)
    
    # Step 6: Check download directory
    check_download_directory(test_user)
    
    # Final summary
    print_section("TEST COMPLETE")
    
    logger.info("✓ All steps completed!")
    logger.info("\nNext steps:")
    logger.info("1. Check Celery logs to see download task progress")
    logger.info("2. Wait a few moments for background downloads to complete")
    logger.info("3. Re-run verify_downloads() to check updated statuses")
    logger.info("4. Check the download directory for files")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

