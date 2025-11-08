#!/usr/bin/env python
"""
Test Agent-to-Agent Communication in RoundRobin Team

This test verifies that:
1. Discovery Agent finds content and outputs Content IDs
2. Download Agent receives those IDs in the conversation
3. Download Agent calls queue_download with the correct IDs
"""

import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

from core.agents import create_round_robin_team

print("="*70)
print("🔍 AGENT COMMUNICATION TEST")
print("="*70)
print()

# Create team
print("📦 Creating RoundRobin team...")
team = create_round_robin_team(max_turns=5)
print(f"✓ Team: {[agent.name for agent in team._participants]}")
print()

# Task that requires agent collaboration
task = """
I'm user ID 1. Please work together:
1. Discovery Agent: Find exactly 2 content items for me
2. Download Agent: Queue those 2 items for download
3. Confirm the download IDs
"""

print("📱 TASK:")
print("-"*70)
print(task.strip())
print("-"*70)
print()

async def run_test():
    print("🔄 Starting conversation...")
    print()
    
    try:
        result = await team.run(task=task)
        
        print()
        print("="*70)
        print("📊 DETAILED CONVERSATION ANALYSIS")
        print("="*70)
        print()
        
        # Analyze each message
        for i, msg in enumerate(result.messages, 1):
            source = getattr(msg, 'source', 'Unknown')
            content = getattr(msg, 'content', '')
            
            # Check message type
            msg_type = type(msg).__name__
            
            print(f"\n{'='*70}")
            print(f"MESSAGE {i}: {source} ({msg_type})")
            print(f"{'='*70}")
            
            # For TextMessages, show the content
            if hasattr(msg, 'content') and isinstance(msg.content, str) and msg.content:
                print(f"\n📝 Content:")
                print(f"{msg.content[:500]}{'...' if len(msg.content) > 500 else ''}")
            
            # For ToolCallMessages, show what tool is being called
            elif hasattr(msg, 'content') and isinstance(msg.content, list):
                for item in msg.content:
                    if hasattr(item, 'name') and hasattr(item, 'arguments'):  # FunctionCall
                        print(f"\n🔧 Tool Call:")
                        print(f"   Function: {item.name}")
                        print(f"   Arguments: {item.arguments}")
                    elif hasattr(item, 'content'):  # FunctionExecutionResult
                        result_content = item.content
                        print(f"\n✅ Tool Result:")
                        print(f"   {result_content[:300]}{'...' if len(str(result_content)) > 300 else ''}")
        
        print()
        print("="*70)
        print("🎯 VERIFICATION CHECKLIST")
        print("="*70)
        
        # Check if Discovery Agent provided Content IDs
        discovery_found_ids = False
        content_ids = []
        for msg in result.messages:
            if hasattr(msg, 'source') and 'Discovery' in msg.source:
                if hasattr(msg, 'content') and 'Content ID' in str(msg.content):
                    discovery_found_ids = True
                    # Try to extract content IDs from the message
                    import re
                    ids = re.findall(r'Content ID[:\s]+(\d+)', str(msg.content))
                    content_ids.extend(ids)
        
        print(f"\n✓ Discovery Agent found content: {'YES' if discovery_found_ids else 'NO'}")
        if content_ids:
            print(f"  Content IDs mentioned: {content_ids}")
        
        # Check if Download Agent called queue_download
        download_called = False
        download_ids = []
        for msg in result.messages:
            if hasattr(msg, 'source') and 'Download' in msg.source:
                # Check for queue_download tool calls
                if hasattr(msg, 'content') and isinstance(msg.content, list):
                    for item in msg.content:
                        if hasattr(item, 'name') and 'queue_download' in item.name.lower():
                            download_called = True
                            # Extract the content_item_id from arguments
                            import json
                            try:
                                args = json.loads(item.arguments)
                                if 'content_item_id' in args:
                                    download_ids.append(args['content_item_id'])
                            except:
                                pass
        
        print(f"\n✓ Download Agent called queue_download: {'YES' if download_called else 'NO'}")
        if download_ids:
            print(f"  Downloaded Content IDs: {download_ids}")
        
        # Check if they match
        if content_ids and download_ids:
            # Convert to sets for comparison
            found_set = set(content_ids)
            downloaded_set = set(str(did) for did in download_ids)
            
            if found_set.intersection(downloaded_set):
                print(f"\n✅ SUCCESS: Download Agent used IDs from Discovery Agent!")
                print(f"   Matched IDs: {found_set.intersection(downloaded_set)}")
            else:
                print(f"\n⚠️  WARNING: IDs don't match")
                print(f"   Found: {found_set}")
                print(f"   Downloaded: {downloaded_set}")
        else:
            print(f"\n⚠️  Could not verify ID matching (parsing may have failed)")
        
        print()
        print("="*70)
        print("💡 HOW AGENTS COMMUNICATE")
        print("="*70)
        print("""
In RoundRobinGroupChat:
1. Each agent sees the FULL conversation history
2. Discovery Agent outputs: "Content ID: 123, Content ID: 456"
3. Download Agent reads that message in the history
4. Download Agent extracts IDs and calls queue_download(content_item_id=123)
5. The conversation context grows with each turn

This is different from direct function returns - agents communicate
through natural language messages that include structured data.
""")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(run_test())

