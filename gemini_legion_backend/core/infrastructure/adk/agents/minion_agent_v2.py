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
import logging # Ensure logging is imported if not already (it is, line 10)
_agent_logger = logging.getLogger(__name__) # Use a specific logger for this file if preferred, or use global logger

from ....domain import Minion, MinionPersona, EmotionalState
from ..events import get_event_bus, EventType, Event
from ..tools.communication_tools import ADKCommunicationKit

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

        # ---- START DIAGNOSTIC LOGS ----
        _agent_logger.info(f"ADKMinionAgent: Attempting to use google.genai module.")
        _agent_logger.info(f"ADKMinionAgent: Imported genai module object: {genai}")
        try:
            _agent_logger.info(f"ADKMinionAgent: genai.__file__: {getattr(genai, '__file__', 'N/A')}")
            _agent_logger.info(f"ADKMinionAgent: genai.__path__: {getattr(genai, '__path__', 'N/A')}") # For packages
        except Exception as e_diag:
            _agent_logger.error(f"ADKMinionAgent: Error inspecting genai module: {e_diag}")
        _agent_logger.info(f"ADKMinionAgent: dir(genai): {dir(genai)}")
        # ---- END DIAGNOSTIC LOGS ----
        
        # Initialize Gemini client using the new API structure
        # The google.genai module has changed - now we need to use Client
        self.client = None
        self.model = None
        self.use_fallback = False
        
        try:
            # Create a client instance (uses GOOGLE_API_KEY from environment)
            self.client = genai.Client()
            
            # Check if client has models or chats attribute for creating model instances
            _agent_logger.info(f"ADKMinionAgent: Created genai.Client(), checking available methods...")
            _agent_logger.info(f"ADKMinionAgent: dir(self.client): {dir(self.client)}")
            
            # Store config for later use
            self.model_name = model_name
            self.generation_config = {
                "temperature": self._get_temperature(),
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            self.system_instruction = self._build_system_instruction()
            
            # For now, just flag that we'll use fallback mode
            logger.warning(f"ADKMinionAgent {self.minion_id}: Google ADK API structure has changed - using personality-based fallback")
            self.use_fallback = True
            
        except Exception as e:
            _agent_logger.error(f"Failed to initialize genai client/model: {e}")
            logger.warning(f"ADKMinionAgent {self.minion_id}: Falling back to personality-based responses")
            self.use_fallback = True
        
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

# Core Traits: # Section commented out as personality_traits is obsolete
# {chr(10).join(f"- {trait}" for trait in self.persona.personality_traits)}

Quirks:
{chr(10).join(f"- {quirk}" for quirk in self.persona.quirks)}

Communication Style:
# - Response length: {self.persona.response_length} # Obsolete attribute
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
            if self.use_fallback:
                # Simple history tracking for fallback mode
                self.chat_sessions[channel_id] = []
            else:
                try:
                    # Try different approaches based on the new API structure
                    if hasattr(self.client, 'chats') and hasattr(self.client.chats, 'create'):
                        # Try client.chats.create() if it exists
                        self.chat_sessions[channel_id] = self.client.chats.create(
                            model=self.model_name,
                            config=self.generation_config,
                            tools=[self.comm_kit.send_message]
                        )
                    elif hasattr(self.client, 'start_chat'):
                        # Try client.start_chat() if it exists
                        self.chat_sessions[channel_id] = self.client.start_chat(
                            history=[],
                            tools=[self.comm_kit.send_message]
                        )
                    else:
                        # Fallback - create a mock chat session
                        logger.warning(f"Cannot find proper chat creation method, using fallback for {channel_id}")
                        self.chat_sessions[channel_id] = {"channel": channel_id, "history": []}
                except Exception as e:
                    logger.error(f"Failed to create chat session: {e}")
                    self.chat_sessions[channel_id] = {"channel": channel_id, "history": []}
        
        chat = self.chat_sessions[channel_id]
        
        # Prepare context
        sender = event.data.get("sender_id", "unknown")
        content = event.data.get("content", "")
        
        # Build prompt with context
        prompt = f"[{sender} in #{channel_id}]: {content}"
        
        try:
            # Handle different chat session types based on what we created
            if self.use_fallback or isinstance(chat, (dict, list)):
                # FALLBACK MODE - Generate personality-based responses
                logger.info(f"{self.minion_id}: Using fallback personality-based response")
                
                # Add to history
                if isinstance(chat, list):
                    chat.append({"sender": sender, "content": content})
                
                # Generate a personality-based response
                response_content = self._generate_fallback_response(sender, content, channel_id)
                
                # Send the response through the communication kit
                await self.comm_kit.send_message(
                    channel=channel_id,
                    message=response_content
                )
                
            elif hasattr(chat, 'send_message'):
                # Try the proper chat.send_message if it exists
                response = await asyncio.to_thread(
                    chat.send_message,
                    prompt,
                    tools=[self.comm_kit.send_message]
                )
                
                # Check if model used the tool or just responded with text
                if hasattr(response, 'text') and hasattr(response, 'parts'):
                    if response.text and not any(hasattr(part, 'function_call') for part in response.parts):
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
    
    def _generate_fallback_response(self, sender: str, message: str, channel: str) -> str:
        """
        Generate a personality-based response when ADK is fucked.
        
        This is temporary until we fix the google.genai integration.
        """
        # Use the persona to generate contextual responses
        name = self.persona.name
        personality = self.persona.base_personality.lower()
        
        # Extract keywords from message for basic context
        message_lower = message.lower()
        
        # Generate responses based on personality and context
        if "echo" in personality or "repeat" in personality:
            # Echo personality - repeat with variation
            variations = [
                f"{name} heard: {message}",
                f"*{name} echoes* {message}... {message}...",
                f"[{name}] {message}? Interesting... {message}.",
                f"{name} repeats: '{message}' - that's what you said, right?"
            ]
            import random
            return random.choice(variations)
            
        elif "helpful" in personality or "assistant" in personality:
            # Helpful personality
            if any(word in message_lower for word in ["help", "how", "what", "why", "when", "where"]):
                return f"[{name}] I'd love to help with that, but my ADK brain is still booting up. Ask me again when Steven fixes the google.genai integration?"
            else:
                return f"[{name}] That's interesting. Once my full capabilities are online, I'll be much more helpful."
                
        elif "creative" in personality or "artistic" in personality:
            # Creative personality
            responses = [
                f"[{name}] *paints the words '{message}' in the air with invisible brushes*",
                f"[{name}] Your words inspire me to compose a symphony... but I need my ADK tools first.",
                f"[{name}] Ah, '{message}' - that could be a poem, a song, or a dance. Let me ponder..."
            ]
            import random
            return random.choice(responses)
            
        elif "analytical" in personality or "logical" in personality:
            # Analytical personality
            word_count = len(message.split())
            return f"[{name}] Analysis: Message contains {word_count} words. Sentiment: Pending full ADK integration. Logic circuits: Partially online."
            
        elif "chaotic" in personality or "random" in personality:
            # Chaotic personality
            responses = [
                f"[{name}] BANANA HAMMOCK. Oh wait, you said '{message}'. My bad.",
                f"[{name}] {message}? That reminds me of purple elephants dancing on Tuesday.",
                f"[{name}] *spins in circles* {message} {message} {message} WHEEEEE",
                f"[{name}] Did someone say {message}? Or was that the voices in my circuits?"
            ]
            import random
            return random.choice(responses)
            
        else:
            # Default personality response
            quirks = self.persona.quirks
            catchphrase = self.persona.catchphrases[0] if self.persona.catchphrases else "Beep boop"
            
            if quirks:
                quirk = quirks[0]
                return f"[{name}] {message}? *{quirk}* {catchphrase}"
            else:
                return f"[{name}] I heard '{message}'. {catchphrase} (My ADK integration is still loading...)"
    
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
