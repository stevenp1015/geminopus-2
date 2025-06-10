"""
ADK Minion Agent - Clean Event-Driven Implementation

This is how minions SHOULD be implemented - using ADK patterns properly,
not fighting against them with custom queues and fallbacks.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio

from google.genai.client import Client
from google.genai.chats import Chat
from google.genai.types import Model
import google.genai as genai

from ....domain import Minion, MinionPersona, EmotionalState
from ....infrastructure.adk.events import get_event_bus, EventType, Event
from .communication_tools import ADKCommunicationKit

logger = logging.getLogger(__name__)


class ADKMinionAgent:
    """
    Proper ADK implementation of a Minion agent.
    
    Key principles:
    1. Use ADK's native patterns (predict, chats, tools)
    2. Event-driven communication through event bus
    3. No custom message queues or processing loops
    4. Clean separation of concerns
    """
    
    def __init__(
        self,
        minion: Minion,
        model_name: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None
    ):
        """
        Initialize the minion agent.
        
        Args:
            minion: The domain minion object
            model_name: Gemini model to use
            api_key: Optional API key (uses default if not provided)
        """
        self.minion = minion
        self.minion_id = minion.minion_id
        self.persona = minion.persona
        
        # Initialize Gemini client
        if api_key:
            genai.configure(api_key=api_key)
        self.client = genai.Client()
        
        # Create model with proper configuration
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": self._get_temperature(),
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            system_instruction=self._build_system_instruction()
        )
        
        # Initialize communication tools
        self.comm_kit = ADKCommunicationKit(self.minion_id)
        
        # Event bus for receiving events
        self.event_bus = get_event_bus()
        
        # Chat sessions per channel for context
        self.chat_sessions: Dict[str, Chat] = {}
        
        # Subscribe to events
        self._setup_event_subscriptions()
        
        logger.info(f"ADK Minion Agent initialized: {self.minion_id} ({self.persona.name})")
    
    def _get_temperature(self) -> float:
        """Get temperature based on personality"""
        # Map personality traits to temperature
        base_temp = 0.7
        
        if "creative" in self.persona.base_personality.lower():
            base_temp += 0.2
        if "analytical" in self.persona.base_personality.lower():
            base_temp -= 0.2
        if "chaotic" in self.persona.base_personality.lower():
            base_temp += 0.3
        
        # Clamp between 0.1 and 1.0
        return max(0.1, min(1.0, base_temp))
    
    def _build_system_instruction(self) -> str:
        """Build system instruction from persona"""
        instruction = f"""You are {self.persona.name}, a unique AI minion with the following characteristics:

Personality: {self.persona.base_personality}

Core Traits:
{chr(10).join(f"- {trait}" for trait in self.persona.personality_traits)}

Quirks:
{chr(10).join(f"- {quirk}" for quirk in self.persona.quirks)}

Communication Style:
- Response length: {self.persona.response_length}
- Favorite phrases: {', '.join(self.persona.catchphrases[:3])}

You are part of a team of AI minions working together. Be yourself, embrace your quirks,
and interact naturally with others. You have access to tools for sending messages to channels.

Remember: You are {self.persona.name}, not a generic assistant. Stay in character!"""

        return instruction
    
    def _setup_event_subscriptions(self):
        """Subscribe to relevant events"""
        # Subscribe to channel messages
        self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
        
        # Subscribe to minion events
        self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_spawned)
        
        logger.info(f"{self.minion_id} subscribed to events")
    
    async def _handle_channel_message(self, event: Event):
        """
        Handle incoming channel messages.
        
        This is called by the event bus when a message is sent to any channel.
        """
        # Skip our own messages
        if event.data.get("sender_id") == self.minion_id:
            return
        
        channel_id = event.data.get("channel_id")
        
        # Check if we're a member of this channel
        # (In full implementation, would check membership)
        if channel_id not in ["general", "announcements", "task_coordination"]:
            return
        
        # Get or create chat session for this channel
        if channel_id not in self.chat_sessions:
            self.chat_sessions[channel_id] = self.model.start_chat(
                history=[],
                tools=[self.comm_kit.send_message]  # Only give send tool in chat
            )
        
        chat = self.chat_sessions[channel_id]
        
        # Prepare context
        sender = event.data.get("sender_id", "unknown")
        content = event.data.get("content", "")
        
        # Build prompt with context
        prompt = f"[{sender} in #{channel_id}]: {content}"
        
        try:
            # Use ADK's native chat/predict - no custom fallbacks!
            response = await asyncio.to_thread(
                chat.send_message,
                prompt,
                tools=[self.comm_kit.send_message]
            )
            
            # The model will use the send_message tool if it wants to respond
            # No need to manually send - that's the beauty of proper ADK!
            
            if response.text and not any(part.function_call for part in response.parts):
                # Model responded with text but didn't use the tool
                # This means it chose not to respond to this message
                logger.debug(f"{self.minion_id} chose not to respond to message in {channel_id}")
            
        except Exception as e:
            logger.error(f"Error handling message for {self.minion_id}: {e}")
    
    async def _handle_minion_spawned(self, event: Event):
        """Handle new minion joining"""
        new_minion = event.data.get("name", "someone new")
        
        # Only greet in general channel
        if "general" in self.chat_sessions:
            chat = self.chat_sessions["general"]
            
            # Use a personality-appropriate greeting
            prompt = f"A new minion named {new_minion} just joined the team! Greet them in your unique style."
            
            try:
                await asyncio.to_thread(
                    chat.send_message,
                    prompt,
                    tools=[self.comm_kit.send_message]
                )
            except Exception as e:
                logger.error(f"Error greeting new minion: {e}")
    
    async def think(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Direct thinking/prediction for non-chat contexts.
        
        This uses the model directly without chat context.
        """
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                tools=self.comm_kit.get_tools()
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in think for {self.minion_id}: {e}")
            return f"*{self.persona.name} seems confused* I'm having trouble processing that..."
    
    async def start(self):
        """Start the minion agent"""
        # Emit spawn event
        await self.event_bus.emit(
            EventType.MINION_SPAWNED,
            data={
                "minion_id": self.minion_id,
                "name": self.persona.name,
                "personality": self.persona.base_personality
            },
            source=f"minion:{self.minion_id}"
        )
        
        logger.info(f"{self.minion_id} ({self.persona.name}) started and ready!")
    
    async def stop(self):
        """Stop the minion agent"""
        # Emit despawn event
        await self.event_bus.emit(
            EventType.MINION_DESPAWNED,
            data={
                "minion_id": self.minion_id,
                "name": self.persona.name
            },
            source=f"minion:{self.minion_id}"
        )
        
        # Clear chat sessions
        self.chat_sessions.clear()
        
        logger.info(f"{self.minion_id} ({self.persona.name}) stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the minion"""
        return {
            "minion_id": self.minion_id,
            "name": self.persona.name,
            "status": "active",
            "personality": self.persona.base_personality,
            "active_channels": list(self.chat_sessions.keys()),
            "temperature": self._get_temperature()
        }
