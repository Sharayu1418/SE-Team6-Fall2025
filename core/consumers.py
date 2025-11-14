"""
WebSocket consumers for Django Channels.

Handles real-time agent execution updates via WebSocket.
"""

import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from core.agents.groupchat import create_round_robin_team
from core.models import DownloadItem

logger = logging.getLogger(__name__)


class AgentExecutionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time agent execution.
    
    Handles:
    - WebSocket connections
    - Trigger agent execution
    - Send real-time updates to frontend
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Get user from scope (session-based auth)
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        self.user_id = self.user.id
        self.room_group_name = f'agent_execution_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connected. Ready to execute agents.',
        }))
        
        logger.info(f"WebSocket connected for user {self.user_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected for user {self.user_id}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'trigger_agents':
                max_items = data.get('max_items', 5)
                await self.handle_trigger_agents(max_items)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}',
            }))
    
    async def handle_trigger_agents(self, max_items: int):
        """Handle agent execution trigger."""
        try:
            # Send execution started message
            await self.send(text_data=json.dumps({
                'type': 'execution_started',
                'message': f'Starting agent execution for user {self.user_id} (max {max_items} items)',
            }))
            
            # Run agents in background
            asyncio.create_task(self.run_agents(max_items))
            
        except Exception as e:
            logger.error(f"Error triggering agents: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to start agent execution: {str(e)}',
            }))
    
    async def run_agents(self, max_items: int):
        """Run the agent team and send updates."""
        try:
            # Create task for agent execution
            task = f"I'm user ID {self.user_id}. Find and download up to {max_items} new content items for me based on my subscriptions and preferences."
            
            # Send agent message
            await self.send(text_data=json.dumps({
                'type': 'agent_message',
                'agent': 'System',
                'message': f'Creating agent team for user {self.user_id}...',
            }))
            
            # Create team
            team = await database_sync_to_async(create_round_robin_team)(
                max_turns=max_items * 2  # Allow enough turns for discovery and download
            )
            
            # Run team (this is async in the new API)
            await self.send(text_data=json.dumps({
                'type': 'agent_message',
                'agent': 'System',
                'message': 'Starting agent conversation...',
            }))
            
            # Run the team (check if it's async or sync)
            try:
                # Try async first (new API)
                if asyncio.iscoroutinefunction(team.run):
                    result = await team.run(task=task)
                else:
                    # Sync version - run in thread pool
                    result = await asyncio.to_thread(team.run, task=task)
            except AttributeError:
                # Fallback: run synchronously in thread
                result = await asyncio.to_thread(team.run, task=task)
            
            # Process results and send updates
            await self.process_agent_results(result)
            
        except Exception as e:
            logger.error(f"Error running agents: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Agent execution failed: {str(e)}',
            }))
    
    async def process_agent_results(self, result):
        """Process agent execution results and send summary."""
        try:
            # Get download statistics
            stats = await database_sync_to_async(self.get_download_stats)(self.user_id)
            
            # Send execution complete message
            await self.send(text_data=json.dumps({
                'type': 'execution_complete',
                'message': 'Agent execution completed successfully!',
                'summary': {
                    'total_downloads': stats['total'],
                    'queued': stats['queued'],
                    'downloading': stats['downloading'],
                    'ready': stats['ready'],
                    'failed': stats['failed'],
                },
            }))
            
        except Exception as e:
            logger.error(f"Error processing agent results: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing results: {str(e)}',
            }))
    
    @staticmethod
    def get_download_stats(user_id: int) -> dict:
        """Get download statistics for a user."""
        downloads = DownloadItem.objects.filter(user_id=user_id)
        
        return {
            'total': downloads.count(),
            'queued': downloads.filter(status='queued').count(),
            'downloading': downloads.filter(status='downloading').count(),
            'ready': downloads.filter(status='ready').count(),
            'failed': downloads.filter(status='failed').count(),
        }
    
    # Handler for group messages (not used in this implementation)
    async def agent_message(self, event):
        """Handle agent message from group."""
        await self.send(text_data=json.dumps(event))
