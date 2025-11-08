#!/usr/bin/env python
"""
Speed Comparison: Single Agent vs RoundRobin Team

Shows the performance difference with llama3.2:3b (3B params)
"""

import os
import django
import asyncio
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
django.setup()

from core.agents import create_content_discovery_agent, create_round_robin_team
from autogen_agentchat.messages import TextMessage

print("="*70)
print("⚡ SPEED COMPARISON: Single Agent vs Team")
print("="*70)
print()

# Simple task
task = "I'm user ID 1. Find 2 content items for me. Be brief."

print(f"📱 Task: {task}")
print()

async def test_single_agent():
    """Test single Discovery agent (baseline)."""
    print("="*70)
    print("TEST 1: Single Discovery Agent (Baseline)")
    print("="*70)
    
    discovery = create_content_discovery_agent()
    
    print("🏃 Running single agent...")
    start = time.time()
    
    response = await discovery.on_messages(
        [TextMessage(content=task, source="User")],
        cancellation_token=None,
    )
    
    elapsed = time.time() - start
    
    print(f"✅ Complete in {elapsed:.1f} seconds")
    print()
    print("Response preview:")
    content = response.chat_message.content
    print(f"  {content[:200]}...")
    print()
    
    return elapsed


async def test_team():
    """Test RoundRobin team with 3 agents."""
    print("="*70)
    print("TEST 2: RoundRobin Team (3 agents, 3 turns)")
    print("="*70)
    
    team = create_round_robin_team(max_turns=3)
    
    print(f"🏃 Running team with {len(team._participants)} agents...")
    start = time.time()
    
    result = await team.run(task=task)
    
    elapsed = time.time() - start
    
    print(f"✅ Complete in {elapsed:.1f} seconds")
    print(f"   Total messages: {len(result.messages)}")
    print()
    
    return elapsed


async def main():
    print("⏱️  Testing with llama3.2:3b (3B parameter model)")
    print()
    
    # Test single agent
    time1 = await test_single_agent()
    
    # Test team
    time2 = await test_team()
    
    # Comparison
    print("="*70)
    print("📊 COMPARISON")
    print("="*70)
    print(f"  Single Agent:  {time1:6.1f} seconds")
    print(f"  Team (3 agents): {time2:6.1f} seconds")
    print(f"  Slowdown:      {time2/time1:6.1f}x")
    print()
    print("Why is the team slower?")
    print("  • Each agent processes the full conversation history")
    print("  • Sequential turns (Discovery → Download → Summarizer)")
    print("  • Multiple tool calls across agents")
    print("  • Context grows with each turn")
    print()
    print("💡 With llama3.2:3b:")
    print("  • Inference is moderate (~2-3 sec per response, slower than 1b)")
    print("  • But 3 agents × multiple turns = 9-20 seconds total")
    print("  • Tool calls (DB queries) add 0.5-1 sec each")
    print("  • Better quality responses than 1b model")
    print()

asyncio.run(main())

