"""
AutoGen Multi-Agent System Entry Point.

This module provides the main interface for running the SmartCache
AutoGen agent system. It can be invoked from Django management commands,
Celery tasks, or run standalone.

Usage:
    # From Django shell
    from core.autogen_main import run_content_pipeline
    run_content_pipeline(user_id=1, task="Discover new podcasts about AI")
    
    # Standalone
    python -c "import django; django.setup(); from core.autogen_main import run_content_pipeline; run_content_pipeline(1, 'Show my subscriptions')"
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

# Import AutoGen components
try:
    import autogen
    from core.agents.groupchat import create_content_pipeline
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure pyautogen is installed: pip install pyautogen")
    autogen = None


def run_content_pipeline(user_id: int, task: str, max_rounds: int = 10) -> str:
    """
    Run the AutoGen multi-agent content pipeline.
    
    This function initializes the agent system and processes a user task
    through the multi-agent workflow.
    
    Args:
        user_id: The user's ID for personalized operations
        task: The task description for agents to process
        max_rounds: Maximum conversation rounds (default: 10)
        
    Returns:
        A summary of the conversation and results
        
    Example:
        >>> result = run_content_pipeline(
        ...     user_id=1,
        ...     task="Find me some tech podcasts and queue them for download"
        ... )
        >>> print(result)
    """
    if autogen is None:
        error_msg = (
            "AutoGen is not available. Please install it:\n"
            "pip install pyautogen\n\n"
            "Also ensure ollama is installed if using local LLM:\n"
            "pip install ollama"
        )
        logger.error(error_msg)
        return error_msg
    
    try:
        logger.info(f"Starting content pipeline for user {user_id}")
        logger.info(f"Task: {task}")
        
        # Create the agent pipeline
        user_proxy, manager = create_content_pipeline(max_round=max_rounds)
        
        # Enhance task with user context
        enhanced_task = f"""
User ID: {user_id}

Task: {task}

Please coordinate between the discovery, download, and summarizer agents
to complete this task. Use the available tools to interact with the system.

When finished, summarize what was accomplished and reply with TERMINATE.
"""
        
        # Initiate the conversation
        logger.info("Initiating agent conversation...")
        user_proxy.initiate_chat(
            manager,
            message=enhanced_task,
        )
        
        # Extract results from conversation history
        logger.info("Conversation completed")
        
        # Get the last few messages
        messages = user_proxy.chat_messages[manager]
        
        result_summary = "\n" + "="*60 + "\n"
        result_summary += "AGENT CONVERSATION SUMMARY\n"
        result_summary += "="*60 + "\n\n"
        
        for msg in messages[-5:]:  # Last 5 messages
            role = msg.get("role", "unknown")
            name = msg.get("name", role)
            content = msg.get("content", "")
            result_summary += f"[{name}]:\n{content}\n\n"
        
        result_summary += "="*60 + "\n"
        
        logger.info("Pipeline execution completed successfully")
        return result_summary
    
    except Exception as e:
        error_msg = f"Error running content pipeline: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


def run_discovery_task(user_id: int, content_type: str = None) -> str:
    """
    Run a simple content discovery task.
    
    Args:
        user_id: The user's ID
        content_type: Optional type filter ('podcast' or 'article')
        
    Returns:
        Discovery results
    """
    task = f"Discover available {content_type or 'content'} sources"
    if content_type:
        task += f" of type '{content_type}'"
    task += f" and show me my current subscriptions."
    
    return run_content_pipeline(user_id=user_id, task=task, max_rounds=5)


def run_download_task(user_id: int, source_id: int, title: str, url: str) -> str:
    """
    Run a content download task.
    
    Args:
        user_id: The user's ID
        source_id: Content source ID
        title: Content title
        url: Content URL
        
    Returns:
        Download task results
    """
    task = (
        f"Queue a download for:\n"
        f"- Title: {title}\n"
        f"- URL: {url}\n"
        f"- Source ID: {source_id}\n"
        f"Then check the download status."
    )
    
    return run_content_pipeline(user_id=user_id, task=task, max_rounds=5)


# Example usage and testing
if __name__ == "__main__":
    """
    Standalone execution example.
    
    To run this script standalone, first set up Django:
    
    export DJANGO_SETTINGS_MODULE=smartcache.settings
    python core/autogen_main.py
    """
    
    # Check if Django is set up
    try:
        import django
        if not apps.apps.ready:
            django.setup()
    except Exception as e:
        logger.warning(f"Django setup issue: {e}")
        logger.info("Trying to import Django settings...")
        
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcache.settings')
        
        try:
            import django
            django.setup()
            logger.info("Django setup successful")
        except Exception as setup_error:
            logger.error(f"Could not set up Django: {setup_error}")
            logger.error("Please run from Django shell or set DJANGO_SETTINGS_MODULE")
            sys.exit(1)
    
    # Example: Run discovery task
    print("\n" + "="*60)
    print("EXAMPLE: Content Discovery Task")
    print("="*60 + "\n")
    
    result = run_discovery_task(user_id=1, content_type="podcast")
    print(result)
    
    print("\n" + "="*60)
    print("EXAMPLE: General Task")
    print("="*60 + "\n")
    
    result = run_content_pipeline(
        user_id=1,
        task="Show me my preferences and recommend some content based on them",
        max_rounds=8,
    )
    print(result)




