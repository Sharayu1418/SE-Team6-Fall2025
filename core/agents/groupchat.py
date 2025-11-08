"""
AutoGen Team configuration (formerly GroupChat).

This module sets up the multi-agent conversation flow using AutoGen's
new Teams API (RoundRobinGroupChat, SelectorGroupChat).

Updated for autogen-agentchat 0.7.5
"""

import logging

try:
    from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.base import TaskResult
    autogen_teams_available = True
except ImportError as e:
    RoundRobinGroupChat = None
    SelectorGroupChat = None
    MaxMessageTermination = None
    TaskResult = None
    autogen_teams_available = False
    logging.warning(f"autogen-agentchat teams not available. Error: {e}")

from .definitions import (
    create_content_discovery_agent,
    create_content_download_agent,
    create_content_summarizer_agent,
    create_ollama_client,
)

logger = logging.getLogger(__name__)


def create_round_robin_team(
    max_turns: int = 10,
    team_name: str = "ContentPipelineTeam",
) -> "RoundRobinGroupChat":
    """
    Create a RoundRobinGroupChat team where agents take turns speaking.
    
    In the new API, RoundRobinGroupChat replaces the old GroupChat with
    a simpler turn-based conversation flow.
    
    Args:
        max_turns: Maximum number of conversation turns (default: 10)
        team_name: Name of the team (default: "ContentPipelineTeam")
        
    Returns:
        A RoundRobinGroupChat team with all agents configured.
        
    Example usage:
        team = create_round_robin_team(max_turns=5)
        result = await team.run(task="Find and download content for user 1")
    """
    if not autogen_teams_available:
        raise ImportError(
            "autogen-agentchat teams not available. "
            "Install with: pip install pyautogen 'autogen-ext[openai]'"
        )
    
    # Create all agents
    discovery_agent = create_content_discovery_agent()
    download_agent = create_content_download_agent()
    summarizer_agent = create_content_summarizer_agent()
    
    # In the new API, we don't use UserProxyAgent in teams
    # The team itself handles the conversation orchestration
    participants = [discovery_agent, download_agent, summarizer_agent]
    
    # Create termination condition
    termination = MaxMessageTermination(max_messages=max_turns)
    
    # Create RoundRobinGroupChat team
    team = RoundRobinGroupChat(
        participants=participants,
        name=team_name,
        description="A team of agents that discover, download, and analyze content",
        termination_condition=termination,
        max_turns=max_turns,
    )
    
    logger.info(
        f"Created RoundRobinGroupChat team '{team_name}' with "
        f"{len(participants)} agents, max {max_turns} turns"
    )
    return team


def create_selector_team(
    max_turns: int = 10,
    team_name: str = "ContentPipelineTeam",
) -> "SelectorGroupChat":
    """
    Create a SelectorGroupChat team where an LLM selects which agent speaks next.
    
    In the new API, SelectorGroupChat uses an LLM to intelligently choose
    which agent should respond based on the conversation context.
    
    Args:
        max_turns: Maximum number of conversation turns (default: 10)
        team_name: Name of the team (default: "ContentPipelineTeam")
        
    Returns:
        A SelectorGroupChat team with all agents configured.
        
    Example usage:
        team = create_selector_team(max_turns=5)
        result = await team.run(task="Find and download content for user 1")
    """
    if not autogen_teams_available:
        raise ImportError(
            "autogen-agentchat teams not available. "
            "Install with: pip install pyautogen 'autogen-ext[openai]'"
        )
    
    # Create all agents
    discovery_agent = create_content_discovery_agent()
    download_agent = create_content_download_agent()
    summarizer_agent = create_content_summarizer_agent()
    
    participants = [discovery_agent, download_agent, summarizer_agent]
    
    # Create termination condition
    termination = MaxMessageTermination(max_messages=max_turns)
    
    # Create a model client for the selector (to decide who speaks next)
    selector_model = create_ollama_client()
    
    # Custom selector prompt for content pipeline
    selector_prompt = """You are managing a content pipeline with these agents:

{roles}

Based on the conversation history, select which agent should speak next from {participants}.
Only return the agent name.

Workflow:
1. Discovery Agent finds and recommends content
2. Download Agent queues and processes downloads  
3. Summarizer Agent analyzes content quality

Conversation so far:
{history}

Who should speak next? Only return the agent name from {participants}."""
    
    # Create SelectorGroupChat team
    team = SelectorGroupChat(
        participants=participants,
        model_client=selector_model,
        name=team_name,
        description="A team of agents that discover, download, and analyze content",
        termination_condition=termination,
        max_turns=max_turns,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=False,  # Force different agents to speak
    )
    
    logger.info(
        f"Created SelectorGroupChat team '{team_name}' with "
        f"{len(participants)} agents, max {max_turns} turns"
    )
    return team


def create_content_pipeline(
    max_turns: int = 10,
    use_selector: bool = True,
) -> "RoundRobinGroupChat | SelectorGroupChat":
    """
    Create a complete content pipeline team.
    
    This is a convenience function that creates a team ready to run tasks.
    
    Args:
        max_turns: Maximum conversation turns (default: 10)
        use_selector: If True, use SelectorGroupChat (LLM selects speakers).
                     If False, use RoundRobinGroupChat (agents take turns).
        
    Returns:
        A team ready to run tasks via team.run(task="...")
        
    Example:
        # Create team
        team = create_content_pipeline(max_turns=5, use_selector=True)
        
        # Run a task
        result = await team.run(
            task="I'm user ID 1. Find and download 3 new items for me."
        )
        
        # Access results
        print(result.messages)  # All messages in the conversation
        print(result.stop_reason)  # Why the conversation ended
    """
    if not autogen_teams_available:
        raise ImportError(
            "autogen-agentchat teams not available. "
            "Install with: pip install pyautogen 'autogen-ext[openai]'"
        )
    
    if use_selector:
        team = create_selector_team(max_turns=max_turns)
        logger.info("Content pipeline created with SelectorGroupChat (LLM-based)")
    else:
        team = create_round_robin_team(max_turns=max_turns)
        logger.info("Content pipeline created with RoundRobinGroupChat (turn-based)")
    
    return team


# Backward compatibility aliases (deprecated, use create_*_team instead)
create_groupchat = create_round_robin_team  # Old name for compatibility
