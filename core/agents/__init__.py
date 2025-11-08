"""
AutoGen agent definitions and configurations.

This module contains:
- Agent definitions (AssistantAgent, UserProxyAgent)
- GroupChat configuration
- Agent orchestration setup
"""

from .definitions import (
    create_content_discovery_agent,
    create_content_download_agent,
    create_content_summarizer_agent,
    create_user_proxy,
    create_ollama_client,
)

# TODO: Update groupchat.py for new AutoGen API (autogen-agentchat 0.7.5)
# from .groupchat import create_groupchat, create_manager

__all__ = [
    # Agent factory functions
    "create_content_discovery_agent",
    "create_content_download_agent",
    "create_content_summarizer_agent",
    "create_user_proxy",
    # Configuration
    "create_ollama_client",
    # GroupChat setup (TODO: Update for new API)
    # "create_groupchat",
    # "create_manager",
]




