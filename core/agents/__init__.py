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
    OLLAMA_CONFIG,
)
from .groupchat import create_groupchat, create_manager

__all__ = [
    # Agent factory functions
    "create_content_discovery_agent",
    "create_content_download_agent",
    "create_content_summarizer_agent",
    "create_user_proxy",
    # Configuration
    "OLLAMA_CONFIG",
    # GroupChat setup
    "create_groupchat",
    "create_manager",
]




