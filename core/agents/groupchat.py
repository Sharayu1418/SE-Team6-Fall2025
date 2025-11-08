"""
AutoGen GroupChat configuration.

This module sets up the multi-agent conversation flow using AutoGen's
GroupChat and GroupChatManager.
"""

import logging

try:
    import autogen
except ImportError:
    autogen = None
    logging.warning("pyautogen not installed. Install with: pip install pyautogen")

from .definitions import (
    create_content_discovery_agent,
    create_content_download_agent,
    create_content_summarizer_agent,
    create_user_proxy,
    OLLAMA_CONFIG,
)

logger = logging.getLogger(__name__)


def create_groupchat(
    max_round: int = 10,
    admin_name: str = "UserProxy",
) -> "autogen.GroupChat":
    """
    Create a GroupChat with all agents.
    
    The GroupChat manages the conversation flow between agents,
    allowing them to collaborate on tasks.
    
    Args:
        max_round: Maximum number of conversation rounds (default: 10)
        admin_name: Name of the admin agent (default: "UserProxy")
        
    Returns:
        An AutoGen GroupChat instance with all agents configured.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    # Create all agents
    discovery_agent = create_content_discovery_agent()
    download_agent = create_content_download_agent()
    summarizer_agent = create_content_summarizer_agent()
    user_proxy = create_user_proxy()
    
    # Create GroupChat
    groupchat = autogen.GroupChat(
        agents=[user_proxy, discovery_agent, download_agent, summarizer_agent],
        messages=[],
        max_round=max_round,
        admin_name=admin_name,
        # speaker_selection_method="auto",  # Let AutoGen decide who speaks next
    )
    
    logger.info(f"Created GroupChat with {len(groupchat.agents)} agents, max {max_round} rounds")
    return groupchat


def create_manager(groupchat: "autogen.GroupChat") -> "autogen.GroupChatManager":
    """
    Create a GroupChatManager for the GroupChat.
    
    The GroupChatManager orchestrates the conversation, deciding which
    agent should speak next based on the conversation context.
    
    Args:
        groupchat: The GroupChat instance to manage
        
    Returns:
        An AutoGen GroupChatManager instance.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=OLLAMA_CONFIG,
    )
    
    logger.info("Created GroupChatManager")
    return manager


def create_content_pipeline(max_round: int = 10):
    """
    Create a complete content pipeline with agents and manager.
    
    This is a convenience function that creates and returns all
    components needed for the multi-agent system.
    
    Args:
        max_round: Maximum conversation rounds (default: 10)
        
    Returns:
        Tuple of (user_proxy, manager) ready to initiate chat
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    # Create GroupChat
    groupchat = create_groupchat(max_round=max_round)
    
    # Create Manager
    manager = create_manager(groupchat)
    
    # Get user_proxy from the groupchat
    user_proxy = groupchat.agents[0]  # First agent is UserProxy
    
    logger.info("Content pipeline created and ready")
    return user_proxy, manager




