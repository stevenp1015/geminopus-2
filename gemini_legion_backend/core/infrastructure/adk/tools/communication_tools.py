"""
ADK Communication Tools - Clean Event-Driven Implementation

These tools allow minions to communicate through the event bus.
No more custom queues, no more duplicate paths.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from google.genai import types
from google.genai.tools import Tool, tool

from ....infrastructure.adk.events import get_event_bus, EventType

logger = logging.getLogger(__name__)


@tool
class SendChannelMessageTool(Tool):
    """
    Send a message to a channel using the event bus.
    
    This is the PROPER way for minions to send messages.
    """
    
    name = "send_channel_message"
    description = "Send a message to a channel"
    
    def __init__(self, minion_id: str):
        """
        Initialize the tool.
        
        Args:
            minion_id: The ID of the minion using this tool
        """
        self.minion_id = minion_id
        self.event_bus = get_event_bus()
        # Set rate limit for this minion
        self.event_bus.set_rate_limit(f"minion:{minion_id}", 5)  # 5 messages per second max
    
    async def __call__(
        self,
        channel: str,
        message: str,
        message_type: str = "chat"
    ) -> Dict[str, Any]:
        """
        Send a message to a channel.
        
        Args:
            channel: Channel ID to send to
            message: Message content
            message_type: Type of message (chat, system, task)
            
        Returns:
            Result of the send operation
        """
        try:
            # Emit through event bus - THE way
            event = await self.event_bus.emit_channel_message(
                channel_id=channel,
                sender_id=self.minion_id,
                content=message,
                source=f"minion:{self.minion_id}",
                metadata={
                    "message_type": message_type,
                    "tool": "send_channel_message"
                }
            )
            
            return {
                "success": True,
                "event_id": event.id,
                "channel": channel,
                "timestamp": event.timestamp.isoformat()
            }
            
        except ValueError as e:
            # Probably rate limited
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Slow down - you're sending messages too fast"
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": "Failed to send message",
                "details": str(e)
            }


@tool
class ListenToChannelTool(Tool):
    """
    Subscribe to channel events.
    
    Note: In the proper architecture, minions receive events through
    their agent's event handler, not through polling or queues.
    """
    
    name = "listen_to_channel"
    description = "Start listening to messages in a channel"
    
    def __init__(self, minion_id: str):
        self.minion_id = minion_id
        self.subscribed_channels = set()
    
    async def __call__(self, channel: str) -> Dict[str, Any]:
        """
        Subscribe to a channel.
        
        Args:
            channel: Channel ID to listen to
            
        Returns:
            Subscription status
        """
        if channel in self.subscribed_channels:
            return {
                "success": False,
                "error": "Already subscribed to this channel"
            }
        
        self.subscribed_channels.add(channel)
        
        # In the real implementation, this would register
        # the agent's event handler for this channel
        
        return {
            "success": True,
            "channel": channel,
            "status": "listening",
            "subscribed_channels": list(self.subscribed_channels)
        }


@tool
class GetChannelInfoTool(Tool):
    """
    Get information about a channel.
    
    This demonstrates how tools can query the system through events
    rather than direct service calls.
    """
    
    name = "get_channel_info"
    description = "Get information about a channel"
    
    def __init__(self, minion_id: str):
        self.minion_id = minion_id
        self.event_bus = get_event_bus()
    
    async def __call__(self, channel: str) -> Dict[str, Any]:
        """
        Get channel information.
        
        Args:
            channel: Channel ID
            
        Returns:
            Channel information
        """
        # In a full implementation, this would query through events
        # For now, return basic info
        return {
            "channel_id": channel,
            "name": channel.title(),
            "type": "public" if channel in ["general", "announcements"] else "private",
            "member_count": "unknown",
            "description": f"Information about {channel} channel"
        }


class ADKCommunicationKit:
    """
    Complete communication toolkit for ADK minions.
    
    This replaces the old CommunicationCapability with clean,
    event-driven tools.
    """
    
    def __init__(self, minion_id: str):
        """
        Initialize communication kit for a minion.
        
        Args:
            minion_id: The minion's ID
        """
        self.minion_id = minion_id
        
        # Create tools
        self.send_message = SendChannelMessageTool(minion_id)
        self.listen_channel = ListenToChannelTool(minion_id)
        self.get_channel_info = GetChannelInfoTool(minion_id)
    
    def get_tools(self) -> list[Tool]:
        """Get all communication tools"""
        return [
            self.send_message,
            self.listen_channel,
            self.get_channel_info
        ]
    
    def get_tool_dict(self) -> Dict[str, Tool]:
        """Get tools as a dictionary"""
        return {
            tool.name: tool
            for tool in self.get_tools()
        }
