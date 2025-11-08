"""
AutoGen agent tools.

These functions are the "skills" that agents can execute.
They are registered with the UserProxyAgent and called during agent conversations.
"""

from .content_discovery import (
    discover_new_sources,
    filter_by_preferences,
    get_user_subscriptions_info,
)
from .content_recommendation import (
    recommend_content_for_download,
    get_content_item_details,
)
from .content_download import (
    queue_download,
    check_download_status,
    process_download_queue,
)
from .llm_tools import (
    summarize_content,
    assess_quality,
)

__all__ = [
    # Discovery tools
    "discover_new_sources",
    "filter_by_preferences",
    "get_user_subscriptions_info",
    # Recommendation tools
    "recommend_content_for_download",
    "get_content_item_details",
    # Download tools
    "queue_download",
    "check_download_status",
    "process_download_queue",
    # LLM tools
    "summarize_content",
    "assess_quality",
]




