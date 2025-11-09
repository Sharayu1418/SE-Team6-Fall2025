"""
AutoGen agent definitions.

This module creates and configures all AutoGen agents for the SmartCache system.
Each agent has a specific role defined by its system_message.
"""

import logging

try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelCapabilities
    autogen_available = True
except ImportError as e:
    AssistantAgent = None
    UserProxyAgent = None
    OpenAIChatCompletionClient = None
    ModelCapabilities = None
    autogen_available = False
    logging.warning(f"pyautogen not installed. Install with: pip install pyautogen. Error: {e}")

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


def create_ollama_client() -> "OpenAIChatCompletionClient":
    """
    Create an OpenAI-compatible client for Ollama.
    
    Returns:
        OpenAIChatCompletionClient configured to use local Ollama server.
    """
    if OpenAIChatCompletionClient is None:
        raise ImportError("autogen-ext[openai] is required. Install with: pip install 'autogen-ext[openai]'")
    
    # Create model capabilities for Ollama
    capabilities = ModelCapabilities(
        function_calling=True,
        json_output=True,
        vision=False,
    )
    
    return OpenAIChatCompletionClient(
        model="llama3.2:3b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # Required but value doesn't matter for local Ollama
        temperature=0.7,
        model_capabilities=capabilities,
    )


def create_content_discovery_agent() -> "AssistantAgent":
    """
    Create the Content Discovery Agent.
    
    This agent is responsible for:
    - Discovering available content sources
    - Filtering sources based on user preferences
    - Managing user subscriptions
    
    Returns:
        An AutoGen AssistantAgent configured for content discovery.
    """
    if not autogen_available:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen 'autogen-ext[openai]'")
    
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
    
    model_client = create_ollama_client()
    
    # Tools for discovery agent
    tools = [
        discover_new_sources,
        get_user_subscriptions_info,
        recommend_content_for_download,
        get_content_item_details,
    ]
    
    agent = AssistantAgent(
        name="ContentDiscoveryAgent",
        model_client=model_client,
        tools=tools,
        system_message=system_message,
    )
    
    logger.info("Created ContentDiscoveryAgent with new API")
    return agent


def create_content_download_agent() -> "AssistantAgent":
    """
    Create the Content Download Agent.
    
    This agent is responsible for:
    - Queuing content downloads
    - Checking download status
    - Processing download queues
    
    Returns:
        An AutoGen AssistantAgent configured for download management.
    """
    if not autogen_available:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen 'autogen-ext[openai]'")
    
    system_message = """You are a Download Manager for SmartCache AI.

Your role is to queue and manage content downloads recommended by the Discovery Agent.
You can download files from S3/Supabase to local storage for offline access.

You have access to these tools:
- queue_download(user_id, content_item_id): Add content to download queue using Content ID
- check_download_status(download_item_id): Check status of a specific download
- process_download_queue(user_id): Start background downloads for all queued items

Your workflow:
1. Listen for recommendations from the Discovery Agent
2. When you receive Content IDs (e.g., [123, 124, 125]), call queue_download for each one
3. After queuing all items, call process_download_queue(user_id) to start downloads
4. Report back with Download Item IDs and confirm download tasks started

Example:
Discovery Agent says: "Download Agent, queue these Content IDs: [123, 124, 125]"

You respond:
- queue_download(user_id=1, content_item_id=123) → Download ID 501 queued
- queue_download(user_id=1, content_item_id=124) → Download ID 502 queued
- queue_download(user_id=1, content_item_id=125) → Download ID 503 queued
- process_download_queue(user_id=1) → Started 3 background download tasks

"✓ Queued 3 items successfully! Download IDs: [501, 502, 503]

Started 3 background download tasks.
Files will be downloaded from S3/Supabase to /media/downloads/user_1/
Check status with check_download_status(download_item_id)"

Communication style:
- Be clear about download status and task progress
- Provide specific Download Item IDs
- Confirm each action with detailed feedback
- Explain that downloads happen in the background via Celery
- Alert users about any issues

When managing downloads, ALWAYS use the tools to interact with the system.
The queue_download tool requires content_item_id from Discovery Agent recommendations."""
    
    model_client = create_ollama_client()
    
    # Tools for download agent
    tools = [
        queue_download,
        check_download_status,
        process_download_queue,
    ]
    
    agent = AssistantAgent(
        name="ContentDownloadAgent",
        model_client=model_client,
        tools=tools,
        system_message=system_message,
    )
    
    logger.info("Created ContentDownloadAgent with new API")
    return agent


def create_content_summarizer_agent() -> "AssistantAgent":
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
    if not autogen_available:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen 'autogen-ext[openai]'")
    
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
    
    model_client = create_ollama_client()
    
    # Tools for summarizer agent (stubs)
    tools = [
        summarize_content,
        assess_quality,
    ]
    
    agent = AssistantAgent(
        name="ContentSummarizerAgent",
        model_client=model_client,
        tools=tools,
        system_message=system_message,
    )
    
    logger.info("Created ContentSummarizerAgent (skeleton) with new API")
    return agent


def create_user_proxy() -> "UserProxyAgent":
    """
    Create the User Proxy Agent.
    
    In the new AutoGen API, the UserProxyAgent is simpler and doesn't require
    tool registration. Tools are passed directly to AssistantAgent instances.
    
    Returns:
        An AutoGen UserProxyAgent configured for user interaction.
    """
    if not autogen_available:
        raise ImportError("pyautogen is required. Install with: pip install pyautogen 'autogen-ext[openai]'")
    
    # In the new API, UserProxyAgent is much simpler
    # It mainly handles human interaction
    user_proxy = UserProxyAgent(
        name="UserProxy",
        description="A proxy agent for the user",
    )
    
    logger.info("Created UserProxy with new API (tools are registered with AssistantAgents)")
    return user_proxy




