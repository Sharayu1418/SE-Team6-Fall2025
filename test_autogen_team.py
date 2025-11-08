#!/usr/bin/env python
"""
AutoGen Multi-Agent Team Test - Tests team collaboration with llama3.2:3b

This demonstrates multiple AutoGen agents working together as a team to:
1. Discover content (Discovery Agent)
2. Queue downloads (Download Agent)
3. Analyze content (Summarizer Agent)

Tests both RoundRobinGroupChat (turn-based) and SelectorGroupChat (LLM-selected).
"""

import os
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

try:
    from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
except ImportError:
    print("ERROR: autogen-agentchat not installed. Install with: pip install pyautogen 'autogen-ext[openai]'")
    exit(1)

from core.agents import (
    create_round_robin_team,
    create_selector_team,
    create_content_pipeline,
)

print("="*70)
print("🤖 AUTOGEN MULTI-AGENT TEAM TEST - llama3.2:3b")
print("="*70)
print()


async def test_round_robin():
    """Test RoundRobinGroupChat where agents take turns."""
    print("="*70)
    print("📦 TEST 1: RoundRobinGroupChat (Turn-Based)")
    print("="*70)
    print()
    
    # Create team
    print("Creating RoundRobin team...")
    team = create_round_robin_team(max_turns=6)
    print(f"✓ Team created with {len(team._participants)} agents")
    print(f"  Agents: {[agent.name for agent in team._participants]}")
    print()
    
    # Test query
    task = """
I'm user ID 1. Please work together to:
1. Find 3 new content items I might like
2. Queue them for download
3. Let me know when done

Be concise in your responses.
"""
    
    print("📱 TASK:")
    print("-"*70)
    print(task.strip())
    print("-"*70)
    print()
    
    print("🔄 Starting team conversation...")
    print("   (Agents will take turns: Discovery -> Download -> Summarizer -> ...)")
    print("-"*70)
    print()
    
    try:
        # Run the team task
        result = await team.run(task=task)
        
        print()
        print("="*70)
        print("✅ ROUND ROBIN TEAM TEST COMPLETE!")
        print("="*70)
        print()
        
        # Display results
        print(f"🎯 Results:")
        print(f"  - Total messages: {len(result.messages)}")
        print(f"  - Stop reason: {result.stop_reason}")
        print()
        
        print("📝 Conversation Summary:")
        print("-"*70)
        for i, msg in enumerate(result.messages[-6:], 1):  # Show last 6 messages
            source = getattr(msg, 'source', 'Unknown')
            content = getattr(msg, 'content', str(msg))
            # Truncate long messages
            content_preview = content[:150] + "..." if len(content) > 150 else content
            print(f"{i}. [{source}] {content_preview}")
        print("-"*70)
        print()
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR during RoundRobin test: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_selector():
    """Test SelectorGroupChat where LLM selects who speaks next."""
    print("="*70)
    print("📦 TEST 2: SelectorGroupChat (LLM-Selected)")
    print("="*70)
    print()
    
    # Create team
    print("Creating Selector team...")
    team = create_selector_team(max_turns=6)
    print(f"✓ Team created with {len(team._participants)} agents")
    print(f"  Agents: {[agent.name for agent in team._participants]}")
    print(f"  Selector: Uses llama3.2:3b to pick who speaks next")
    print()
    
    # Test query
    task = """
I'm user ID 1. I want to download some technology podcasts for my commute.

Can you:
1. Find 2-3 tech-related items from my subscriptions
2. Queue them for download

Keep responses brief.
"""
    
    print("📱 TASK:")
    print("-"*70)
    print(task.strip())
    print("-"*70)
    print()
    
    print("🔄 Starting team conversation...")
    print("   (LLM will intelligently select which agent should respond)")
    print("-"*70)
    print()
    
    try:
        # Run the team task
        result = await team.run(task=task)
        
        print()
        print("="*70)
        print("✅ SELECTOR TEAM TEST COMPLETE!")
        print("="*70)
        print()
        
        # Display results
        print(f"🎯 Results:")
        print(f"  - Total messages: {len(result.messages)}")
        print(f"  - Stop reason: {result.stop_reason}")
        print()
        
        print("📝 Conversation Summary:")
        print("-"*70)
        for i, msg in enumerate(result.messages[-6:], 1):  # Show last 6 messages
            source = getattr(msg, 'source', 'Unknown')
            content = getattr(msg, 'content', str(msg))
            # Truncate long messages
            content_preview = content[:150] + "..." if len(content) > 150 else content
            print(f"{i}. [{source}] {content_preview}")
        print("-"*70)
        print()
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR during Selector test: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_content_pipeline():
    """Test the convenience function for creating a content pipeline."""
    print("="*70)
    print("📦 TEST 3: create_content_pipeline() - Convenience Function")
    print("="*70)
    print()
    
    # Create pipeline (defaults to SelectorGroupChat)
    print("Creating content pipeline...")
    team = create_content_pipeline(max_turns=5, use_selector=True)
    print(f"✓ Pipeline created")
    print()
    
    task = "I'm user 1. Show me 2 items to download, then queue them."
    
    print("📱 TASK:")
    print("-"*70)
    print(task)
    print("-"*70)
    print()
    
    try:
        result = await team.run(task=task)
        
        print()
        print("="*70)
        print("✅ CONTENT PIPELINE TEST COMPLETE!")
        print("="*70)
        print()
        print(f"  Total messages: {len(result.messages)}")
        print()
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR during pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests."""
    
    print("🚀 Starting AutoGen Multi-Agent Team Tests")
    print()
    print("These tests demonstrate:")
    print("  1. RoundRobinGroupChat - Agents take turns")
    print("  2. SelectorGroupChat - LLM picks who speaks")
    print("  3. create_content_pipeline() - Convenience function")
    print()
    
    # Test 1: Round Robin
    result1 = await test_round_robin()
    
    print("\n" + "="*70)
    print()
    
    # Test 2: Selector
    result2 = await test_selector()
    
    print("\n" + "="*70)
    print()
    
    # Test 3: Pipeline convenience function
    result3 = await test_content_pipeline()
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 ALL TESTS COMPLETE!")
    print("="*70)
    print()
    print("Summary:")
    print(f"  ✓ RoundRobin: {'PASSED' if result1 else 'FAILED'}")
    print(f"  ✓ Selector: {'PASSED' if result2 else 'FAILED'}")
    print(f"  ✓ Pipeline: {'PASSED' if result3 else 'FAILED'}")
    print()
    print("Key Learnings:")
    print("  - RoundRobinGroupChat: Simple, predictable turn-taking")
    print("  - SelectorGroupChat: Intelligent, context-aware speaker selection")
    print("  - Both support async/await and return TaskResult")
    print("  - Tools are automatically called by agents as needed")
    print()


if __name__ == "__main__":
    # Check if Ollama is running
    print("Checking Ollama availability...")
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            print("✓ Ollama is running")
        else:
            print("⚠ Ollama responded but with unexpected status")
    except Exception as e:
        print(f"❌ Ollama not available: {e}")
        print("   Start Ollama with: ollama serve")
        exit(1)
    
    print()
    
    # Run tests
    asyncio.run(main())

