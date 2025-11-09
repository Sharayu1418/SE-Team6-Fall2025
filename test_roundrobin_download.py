#!/usr/bin/env python
"""
Test RoundRobinGroupChat with Discovery and Download Agents.

This script:
1. Creates a RoundRobinGroupChat with Discovery and Download agents
2. Asks Discovery Agent to recommend content for user 1
3. Asks Download Agent to queue and process downloads
4. Verifies files are downloaded to local storage
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Django setup
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')

import django
django.setup()

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from core.models import ContentItem, DownloadItem, Subscription
from core.agents.groupchat import create_round_robin_team

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


@sync_to_async
def check_setup():
    """Check prerequisites"""
    print_section("SETUP CHECK")
    
    user = User.objects.first()
    if not user:
        logger.error("❌ No users found")
        return None
    
    logger.info(f"✓ User: {user.username} (ID: {user.id})")
    
    # Check subscriptions
    subs = Subscription.objects.filter(user=user, is_active=True)
    logger.info(f"✓ Active subscriptions: {subs.count()}")
    
    # Check cached content
    cached_items = ContentItem.objects.filter(
        storage_url__isnull=False
    ).exclude(storage_url='').count()
    logger.info(f"✓ Cached content items: {cached_items}")
    
    if cached_items == 0:
        logger.error("❌ No cached content available. Run ETL pipeline first.")
        return None
    
    return user


@sync_to_async
def show_initial_state(user):
    """Show initial download state"""
    print_section("INITIAL STATE")
    
    downloads = DownloadItem.objects.filter(user=user)
    logger.info(f"Existing download items: {downloads.count()}")
    
    if downloads.exists():
        status_counts = {}
        for d in downloads:
            status_counts[d.status] = status_counts.get(d.status, 0) + 1
        
        logger.info("Status breakdown:")
        for status, count in status_counts.items():
            logger.info(f"  {status}: {count}")


async def run_roundrobin_chat(user):
    """Run the RoundRobinGroupChat"""
    print_section("STARTING ROUNDROBIN GROUPCHAT")
    
    logger.info("Creating RoundRobinGroupChat team...")
    
    try:
        # Create team with Discovery and Download agents
        team = create_round_robin_team(
            max_turns=12,
            team_name="DiscoveryDownloadTeam"
        )
        
        logger.info("✓ Team created with agents:")
        logger.info("  1. ContentDiscoveryAgent")
        logger.info("  2. ContentDownloadAgent")
        logger.info("  3. ContentSummarizerAgent")
        
        # Create task for the agents
        task = f"""
I am User ID {user.id} ({user.username}).

TASK: Find and download content for me.

Step 1 - Discovery Agent:
- Call recommend_content_for_download(user_id={user.id}, max_items=3)
- Present the recommendations with Content IDs clearly listed

Step 2 - Download Agent:
- Queue ALL recommended Content IDs using queue_download()
- After queuing, call process_download_queue(user_id={user.id})
- Report the Download Item IDs and task status

Step 3 - Summarizer Agent:
- Summarize what was accomplished

Please work together to complete this task efficiently.
"""
        
        logger.info("\n📋 TASK:")
        logger.info("-" * 80)
        logger.info(task.strip())
        logger.info("-" * 80 + "\n")
        
        logger.info("🤖 Starting agent conversation...\n")
        
        # Run the team
        result = await team.run(task=task)
        
        logger.info("\n✓ Conversation completed!")
        logger.info(f"Stop reason: {result.stop_reason}")
        logger.info(f"Total messages: {len(result.messages)}")
        
        # Display conversation
        print_section("AGENT CONVERSATION")
        
        for idx, msg in enumerate(result.messages, 1):
            # Extract source/author from message
            source = "Unknown"
            content = str(msg)
            
            if hasattr(msg, 'source'):
                source = msg.source
            elif hasattr(msg, 'name'):
                source = msg.name
            
            if hasattr(msg, 'content'):
                content = msg.content
            
            print(f"\n{'='*80}")
            print(f"[Message {idx}] {source}")
            print(f"{'='*80}")
            print(content)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error running team: {e}")
        import traceback
        traceback.print_exc()
        return False


@sync_to_async
def verify_downloads(user):
    """Verify download results"""
    print_section("DOWNLOAD VERIFICATION")
    
    # Get recent downloads
    downloads = DownloadItem.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    if not downloads:
        logger.warning("⚠️  No downloads found")
        return
    
    logger.info(f"Recent downloads (showing {downloads.count()}):\n")
    
    status_counts = {
        'queued': 0,
        'downloading': 0,
        'ready': 0,
        'failed': 0,
    }
    
    for idx, download in enumerate(downloads, 1):
        status_counts[download.status] = status_counts.get(download.status, 0) + 1
        
        logger.info(f"{idx}. [{download.id}] {download.title[:60]}")
        logger.info(f"   Status: {download.status}")
        logger.info(f"   Media URL: {download.media_url[:70] if download.media_url else 'None'}...")
        
        # Check if using S3
        if download.media_url:
            if 's3.amazonaws.com' in download.media_url or 'supabase' in download.media_url:
                logger.info(f"   ✅ Using storage URL (S3/Supabase)")
            else:
                logger.info(f"   ⚠️  Using original source URL")
        
        if download.local_file_path:
            logger.info(f"   Local: {download.local_file_path}")
            if os.path.exists(download.local_file_path):
                size_mb = os.path.getsize(download.local_file_path) / (1024 * 1024)
                logger.info(f"   ✅ File exists ({size_mb:.2f} MB)")
            else:
                logger.info(f"   ⚠️  File not found")
        
        if download.error_message:
            logger.info(f"   Error: {download.error_message[:100]}")
        
        print()
    
    # Summary
    logger.info("Status Summary:")
    for status, count in status_counts.items():
        if count > 0:
            logger.info(f"  {status}: {count}")


def check_download_directory(user):
    """Check the download directory"""
    print_section("DOWNLOAD DIRECTORY CHECK")
    
    download_dir = f"media/downloads/user_{user.id}"
    full_path = os.path.join(project_root, download_dir)
    
    logger.info(f"Directory: {full_path}")
    
    if not os.path.exists(full_path):
        logger.warning("⚠️  Directory does not exist yet")
        logger.info("   Downloads may still be processing in background (Celery)")
        return
    
    # List files
    files = []
    for root, dirs, filenames in os.walk(full_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            file_size = os.path.getsize(filepath)
            files.append((filename, file_size))
    
    if not files:
        logger.warning("⚠️  No files found")
        logger.info("   Check Celery worker logs for download progress")
        return
    
    logger.info(f"\n✅ Found {len(files)} file(s):\n")
    
    total_size = 0
    for filename, size in files:
        size_mb = size / (1024 * 1024)
        total_size += size
        logger.info(f"  - {filename}")
        logger.info(f"    Size: {size_mb:.2f} MB")
    
    total_mb = total_size / (1024 * 1024)
    logger.info(f"\nTotal: {total_mb:.2f} MB")


async def main():
    """Main execution"""
    print("\n" + "="*80)
    print("  ROUNDROBIN GROUPCHAT TEST: DISCOVERY + DOWNLOAD")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Step 1: Check setup
    user = await check_setup()
    if not user:
        logger.error("\n❌ Setup check failed. Exiting.")
        return
    
    # Step 2: Show initial state
    await show_initial_state(user)
    
    # Step 3: Run RoundRobin chat
    success = await run_roundrobin_chat(user)
    
    if not success:
        logger.error("\n❌ RoundRobin chat failed")
        return
    
    # Step 4: Verify downloads
    await verify_downloads(user)
    
    # Step 5: Check download directory
    check_download_directory(user)
    
    # Final summary
    print_section("TEST COMPLETE")
    
    logger.info("✓ RoundRobin GroupChat test completed!")
    logger.info("\nNext steps:")
    logger.info("1. Check Celery logs: Look for download task progress")
    logger.info("2. Wait a few moments for background downloads")
    logger.info("3. Re-run verification: python test_roundrobin_download.py")
    logger.info("4. Check download directory: media/downloads/user_1/")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

