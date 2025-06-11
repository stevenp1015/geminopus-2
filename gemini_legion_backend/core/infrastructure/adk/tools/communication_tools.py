"""
ADK Communication Tools - Clean Event-Driven Implementation

These are the PROPER ADK tools for communication, not the old custom bullshit.
Everything flows through the event bus.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime

from ..events import get_event_bus, EventType

logger = logging.getLogger(__name__)


class ADKCommunicationKit:
    """
    Clean communication tools for ADK minions.
    
    No more custom queues, no more parallel paths, just events.
    """
    
    def __init__(self, minion_id: str):
        """
        Initialize communication kit for a minion.
        
        Args:
            minion_id: ID of the minion using these tools
        """
        self.minion_id = minion_id
        self.event_bus = get_event_bus()
        
        # Create tool instances
        self.send_message = SendChannelMessageTool(minion_id, self.event_bus)
        self.listen_to_channel = ListenToChannelTool(minion_id)
        
        logger.info(f"ADKCommunicationKit initialized for {minion_id}")
    
    def get_tools(self) -> List[Any]:
        """Get all communication tools for ADK agent"""
        return [self.send_message, self.listen_to_channel]


class SendChannelMessageTool:
    """
    ADK tool for sending messages to channels.
    
    This is THE way minions send messages. Through events. Period.
    """
    
    def __init__(self, minion_id: str, event_bus):
        self.minion_id = minion_id
        self.event_bus = event_bus
        
        # Tool metadata for ADK
        self.name = "send_channel_message"
        self.description = "Send a message to a channel"
        self.parameters = {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The channel ID or name to send to"
                },
                "message": {
                    "type": "string", 
                    "description": "The message content to send"
                }
            },
            "required": ["channel", "message"]
        }
    
    async def __call__(self, channel: str, message: str) -> Dict[str, Any]:
        """Execute the tool - send a message via event bus"""
        try:
            # Emit channel message event - THE ONLY WAY
            event = await self.event_bus.emit_channel_message(
                channel_id=channel,
                sender_id=self.minion_id,
                content=message,
                source=f"minion:{self.minion_id}"
            )
            
            logger.info(f"{self.minion_id} sent message to {channel}")
            
            return {
                "success": True,
                "event_id": event.id,
                "channel": channel,
                "timestamp": event.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Support both async and sync calling patterns
    def __sync_wrapper(self, channel: str, message: str) -> Dict[str, Any]:
        """Synchronous wrapper for tools that don't support async"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__call__(channel, message))
    
    # Make it callable both ways
    call = __call__  # For async contexts
    execute = __sync_wrapper  # For sync contexts


class ListenToChannelTool:
    """
    ADK tool for listening to channel events.
    
    This is more of a declaration than an active tool - it tells the
    system which channels the minion wants to receive events from.
    """
    
    def __init__(self, minion_id: str):
        self.minion_id = minion_id
        self.subscribed_channels: set[str] = {"general", "announcements", "task_coordination"}
        
        # Tool metadata
        self.name = "listen_to_channel"
        self.description = "Subscribe to receive messages from a channel"
        self.parameters = {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The channel ID to listen to"
                },
                "action": {
                    "type": "string",
                    "enum": ["subscribe", "unsubscribe"],
                    "description": "Whether to subscribe or unsubscribe"
                }
            },
            "required": ["channel", "action"]
        }
    
    async def __call__(self, channel: str, action: str = "subscribe") -> Dict[str, Any]:
        """Execute the tool - update channel subscriptions"""
        try:
            if action == "subscribe":
                self.subscribed_channels.add(channel)
                logger.info(f"{self.minion_id} subscribed to {channel}")
            else:
                self.subscribed_channels.discard(channel)
                logger.info(f"{self.minion_id} unsubscribed from {channel}")
            
            return {
                "success": True,
                "action": action,
                "channel": channel,
                "subscribed_channels": list(self.subscribed_channels)
            }
            
        except Exception as e:
            logger.error(f"Error updating channel subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_subscribed(self, channel: str) -> bool:
        """Check if minion is subscribed to a channel"""
        return channel in self.subscribed_channels
