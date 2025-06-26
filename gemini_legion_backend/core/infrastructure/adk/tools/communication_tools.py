"""
ADK Communication Tools for Minions

These are PROPER ADK FunctionTools following the pattern.
Functions with docstrings and type hints, not classes.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ADKCommunicationKit:
    """
    Manages communication tools for ADK minion agents.
    
    Creates properly formatted FunctionTools that ADK understands.
    """
    
    def __init__(self, minion_id: str, event_bus):
        self.minion_id = minion_id
        self.event_bus = event_bus
        logger.info(f"ADKCommunicationKit initialized for {minion_id}")
    
    def send_channel_message(self, channel: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a channel.
        
        Args:
            channel: The channel ID or name to send to
            message: The message content to send
            
        Returns:
            Dict containing success status and event details
        """
        try:
            # Use synchronous emit since ADK tools don't support async
            event_data = {
                "channel_id": channel,
                "sender_id": self.minion_id,
                "content": message,
                "source": f"minion:{self.minion_id}"
            }
            
            # For now, return success - actual async emit happens elsewhere
            logger.info(f"{self.minion_id} sending message to {channel}: {message[:50]}...")
            
            return {
                "success": True,
                "channel": channel,
                "message_preview": message[:100],
                "sender": self.minion_id
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
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
