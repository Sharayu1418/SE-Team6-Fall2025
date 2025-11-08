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

# New Teams API (replaces old GroupChat)
from .groupchat import (
    create_round_robin_team,
    create_selector_team,
    create_content_pipeline,
    create_groupchat,  # Deprecated alias for backward compatibility
)

__all__ = [
    # Agent factory functions
    "create_content_discovery_agent",
    "create_content_download_agent",
    "create_content_summarizer_agent",
    "create_user_proxy",
    # Configuration
    "create_ollama_client",
    # Team setup (new API)
    "create_round_robin_team",
    "create_selector_team",
    "create_content_pipeline",
    "create_groupchat",  # Deprecated
]




