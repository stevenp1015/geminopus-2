"""
ADK Communication Tools for Minions

These are PROPER ADK FunctionTools following the pattern.
Functions with docstrings and type hints, not classes.
"""
import asyncio # Add this import at the top of the file
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ADKCommunicationKit:
    """
    Manages communication tools for ADK minion agents.
    
    Creates properly formatted FunctionTools that ADK understands.
    """
    
    def __init__(self, minion_id: str, event_bus: Any): # Added type hint for clarity
        self.minion_id = minion_id
        self.event_bus = event_bus
        logger.info(f"ADKCommunicationKit initialized for {minion_id}")
    
    async def send_channel_message(self, channel: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a channel by emitting an event through the event bus.
        This is an async tool.
        
        Args:
            channel: The channel ID or name to send to
            message: The message content to send
            
        Returns:
            Dict containing success status and event details for the LLM.
        """
        tool_name = "send_channel_message"
        logger.info(f"Async Tool '{tool_name}' called by {self.minion_id} for channel '{channel}' with message: '{message[:50]}...'")

        if not self.event_bus:
            logger.error(f"Event bus not available for minion {self.minion_id} in {tool_name} tool.")
            return {
                "success": False,
                "error": "Event bus not configured for this tool.",
                "tool_used": tool_name,
                "channel": channel,
                "message_preview": message[:100]
            }

        try:
            await self.event_bus.emit_channel_message(
                channel_id=channel,
                sender_id=self.minion_id,
                content=message,
                source=f"tool:{tool_name}:{self.minion_id}"
            )
            logger.info(f"Message from {self.minion_id} to channel {channel} emitted via event bus.")
            return {
                "success": True,
                "status": "Message successfully emitted to channel.",
                "tool_used": tool_name,
                "channel": channel,
                "message_preview": message[:100]
            }
        except Exception as e:
            logger.error(f"Error in async send_channel_message tool for {self.minion_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tool_used": "send_channel_message",
                "channel": channel,
                "message_preview": message[:100]
            }
    
    def listen_to_channel(self, channel: str, duration: int = 60) -> Dict[str, Any]:
        """
        Listen to a channel for messages (placeholder for now).
        
        Args:
            channel: The channel ID to listen to
            duration: How long to listen in seconds
            
        Returns:
            Dict containing messages heard
        """
        logger.info(f"{self.minion_id} listening to channel {channel}")
        return {
            "success": True,
            "channel": channel,
            "message": f"Listening to {channel} for {duration} seconds",
            "note": "Full implementation pending"
        }
    
    def get_channel_history(self, channel: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent message history from a channel.
        
        Args:
            channel: The channel ID to get history from
            limit: Maximum number of messages to retrieve
            
        Returns:
            Dict containing channel history
        """
        logger.info(f"{self.minion_id} requesting history for {channel}")
        return {
            "success": True,
            "channel": channel,
            "limit": limit,
            "note": "Full implementation pending",
            "messages": []
        }
    
    def send_direct_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send a direct message to another minion.
        
        Args:
            recipient: The minion ID to send to
            message: The message content
            
        Returns:
            Dict containing success status
        """
        logger.info(f"{self.minion_id} sending DM to {recipient}")
        return {
            "success": True,
            "recipient": recipient,
            "message_preview": message[:100],
            "sender": self.minion_id,
            "note": "Full implementation pending"
        }
    
    def get_tools(self) -> List[Any]:
        """Get all communication tools as functions for ADK"""
        # Return methods directly - ADK will convert them to tools
        tools = [
            self.send_channel_message,
            self.listen_to_channel,
            self.get_channel_history,
            self.send_direct_message
        ]
        
        logger.info(f"Created {len(tools)} communication tools for {self.minion_id}")
        return tools
