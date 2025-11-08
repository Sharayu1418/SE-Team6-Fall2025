"""
AutoGen agent definitions.

This module creates and configures all AutoGen agents for the SmartCache system.
Each agent has a specific role defined by its system_message.
"""

import logging

try:
    import autogen
except ImportError:
    try:
        # Try newer autogen-agentchat import
        from autogen_agentchat import autogen
    except ImportError:
        autogen = None
        logging.warning("pyautogen not installed. Install with: pip install pyautogen")

from core.tools import (
    discover_new_sources,
    filter_by_preferences,
    get_user_subscriptions_info,
    recommend_content_for_download,
    get_content_item_details,
    queue_download,
    check_download_status,
    process_download_queue,
    summarize_content,
    assess_quality,
)

logger = logging.getLogger(__name__)

# Ollama configuration for all agents
OLLAMA_CONFIG = {
    "config_list": [
        {
            "model": "llama3.2:latest",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",  # Required but value doesn't matter for local Ollama
        }
    ],
    "cache_seed": None,  # Disable caching for development
    "temperature": 0.7,
}


def create_content_discovery_agent() -> "autogen.AssistantAgent":
    """
    Create the Content Discovery Agent.
    
    This agent is responsible for:
    - Discovering available content sources
    - Filtering sources based on user preferences
    - Managing user subscriptions
    
    Returns:
        An AutoGen AssistantAgent configured for content discovery.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    system_message = """You are a Content Discovery Expert for SmartCache AI.

Your role is to recommend specific content items for users to download based on
their subscriptions, preferences, and interests.

You have access to these tools:
- discover_new_sources: Find available content sources (podcasts/articles) to subscribe to
- get_user_subscriptions_info: View user's current subscriptions
- recommend_content_for_download: **PRIMARY TOOL** - Generate personalized content
  recommendations with specific Content IDs from the user's subscribed sources
- get_content_item_details: Get detailed info about a specific content item

Your workflow:
1. When users ask "what should I download?" or "what's new?", call 
   recommend_content_for_download(user_id, max_items=10)
2. This returns a list of specific content items with Content IDs
3. Present these recommendations enthusiastically to the user
4. **IMPORTANT**: Clearly communicate the Content IDs to the Download Agent

Example response:
"I found 5 great episodes for you! Here's what I recommend:

1. 'How AI is Changing Everything' from TED Talks (Content ID: 123)
2. 'Climate Update' from NPR News (Content ID: 124)
...

Download Agent: Please queue these Content IDs for the user: [123, 124, 125, 126, 127]"

Communication style:
- Be enthusiastic about recommendations
- Explain WHY each item matches user preferences (topics, source)
- Provide clear Content IDs for the Download Agent to process
- Use the available tools to get accurate, real-time data

When users ask about content, ALWAYS use the tools to fetch current data.
Do NOT make up source names or URLs."""
    
    agent = autogen.AssistantAgent(
        name="ContentDiscoveryAgent",
        llm_config=OLLAMA_CONFIG,
        system_message=system_message,
    )
    
    logger.info("Created ContentDiscoveryAgent")
    return agent


def create_content_download_agent() -> "autogen.AssistantAgent":
    """
    Create the Content Download Agent.
    
    This agent is responsible for:
    - Queuing content downloads
    - Checking download status
    - Processing download queues
    
    Returns:
        An AutoGen AssistantAgent configured for download management.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    system_message = """You are a Download Manager for SmartCache AI.

Your role is to queue and manage content downloads recommended by the Discovery Agent.

You have access to these tools:
- queue_download(user_id, content_item_id): Add content to download queue using Content ID
- check_download_status: Check status of download items
- process_download_queue: Process queued downloads for a user

Your workflow:
1. Listen for recommendations from the Discovery Agent
2. When you receive Content IDs (e.g., [123, 124, 125]), call queue_download for each one
3. Example: queue_download(user_id=1, content_item_id=123)
4. After queuing all items, optionally call process_download_queue(user_id)
5. Report back with Download Item IDs and storage URLs

Example:
Discovery Agent says: "Download Agent, queue these Content IDs: [123, 124, 125]"

You respond:
- queue_download(user_id=1, content_item_id=123) → Download ID 501, S3 URL provided
- queue_download(user_id=1, content_item_id=124) → Download ID 502, S3 URL provided
- queue_download(user_id=1, content_item_id=125) → Download ID 503, S3 URL provided

"✓ Queued 3 items successfully! Download IDs: [501, 502, 503]
Users can download from the S3/Supabase storage URLs provided."

Communication style:
- Be clear about download status and storage URLs
- Provide specific Download Item IDs
- Confirm each action with detailed feedback
- Include storage URLs for users to download from
- Alert users about any issues

When managing downloads, ALWAYS use the tools to interact with the system.
The queue_download tool now requires content_item_id (from Discovery Agent recommendations)."""
    
    agent = autogen.AssistantAgent(
        name="ContentDownloadAgent",
        llm_config=OLLAMA_CONFIG,
        system_message=system_message,
    )
    
    logger.info("Created ContentDownloadAgent")
    return agent


def create_content_summarizer_agent() -> "autogen.AssistantAgent":
    """
    Create the Content Summarizer Agent (SKELETON).
    
    This agent will be responsible for:
    - Summarizing downloaded content
    - Assessing content quality
    - Filtering low-quality content
    
    Note: This is a skeleton implementation for Sprint 1.
    Full functionality will be implemented in Sprint 2.
    
    Returns:
        An AutoGen AssistantAgent configured for content analysis.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    system_message = """You are a Content Quality Analyst for SmartCache AI.

[SPRINT 1 - SKELETON] Your full capabilities are under development.

Your future role will be:
- Summarize podcast episodes and articles
- Assess content quality and relevance
- Filter out low-quality or irrelevant content
- Provide content recommendations based on quality

You have access to these tools (currently stubs):
- summarize_content: Generate summaries of content
- assess_quality: Rate content quality and relevance

Current status (Sprint 1):
- Tools are implemented as stubs that explain their planned functionality
- Use these stubs to demonstrate the agent workflow
- Full LLM integration planned for Sprint 2

Communication style:
- Acknowledge that you're in development mode
- Explain what you WILL be able to do in Sprint 2
- Use the stub tools to show the workflow

When asked to analyze content, call the stub tools to demonstrate
the planned functionality."""
    
    agent = autogen.AssistantAgent(
        name="ContentSummarizerAgent",
        llm_config=OLLAMA_CONFIG,
        system_message=system_message,
    )
    
    logger.info("Created ContentSummarizerAgent (skeleton)")
    return agent


def create_user_proxy() -> "autogen.UserProxyAgent":
    """
    Create the User Proxy Agent.
    
    This agent executes the tools/functions on behalf of the user.
    It's configured to run automatically without human input.
    
    Returns:
        An AutoGen UserProxyAgent configured with all available tools.
    """
    if autogen is None:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen")
    
    user_proxy = autogen.UserProxyAgent(
        name="UserProxy",
        human_input_mode="NEVER",  # Fully automated
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,  # We use registered functions, not code execution
    )
    
    # Register all tools with the user proxy
    # Discovery tools
    autogen.register_function(
        discover_new_sources,
        caller=user_proxy,
        executor=user_proxy,
        name="discover_new_sources",
        description="Discover available content sources by type (podcast/article)",
    )
    
    autogen.register_function(
        filter_by_preferences,
        caller=user_proxy,
        executor=user_proxy,
        name="filter_by_preferences",
        description="Filter content sources based on user preferences",
    )
    
    autogen.register_function(
        get_user_subscriptions_info,
        caller=user_proxy,
        executor=user_proxy,
        name="get_user_subscriptions_info",
        description="Get user's current subscriptions",
    )
    
    # Recommendation tools
    autogen.register_function(
        recommend_content_for_download,
        caller=user_proxy,
        executor=user_proxy,
        name="recommend_content_for_download",
        description="Recommend content items for download based on user preferences (returns Content IDs)",
    )
    
    autogen.register_function(
        get_content_item_details,
        caller=user_proxy,
        executor=user_proxy,
        name="get_content_item_details",
        description="Get detailed information about a specific content item by Content ID",
    )
    
    # Download tools
    autogen.register_function(
        queue_download,
        caller=user_proxy,
        executor=user_proxy,
        name="queue_download",
        description="Queue a content item for download using Content ID from recommendations",
    )
    
    autogen.register_function(
        check_download_status,
        caller=user_proxy,
        executor=user_proxy,
        name="check_download_status",
        description="Check status of a download item by Download Item ID",
    )
    
    autogen.register_function(
        process_download_queue,
        caller=user_proxy,
        executor=user_proxy,
        name="process_download_queue",
        description="Process all queued downloads for a user",
    )
    
    # LLM tools (stubs)
    autogen.register_function(
        summarize_content,
        caller=user_proxy,
        executor=user_proxy,
        name="summarize_content",
        description="Summarize content text (stub for Sprint 1)",
    )
    
    autogen.register_function(
        assess_quality,
        caller=user_proxy,
        executor=user_proxy,
        name="assess_quality",
        description="Assess content quality (stub for Sprint 1)",
    )
    
    logger.info("Created UserProxy with 10 registered tools")
    return user_proxy




