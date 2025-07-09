"""
ADK Minion Agent - PROPER Implementation

This implementation extends LlmAgent following ADK best practices from the crucible:
- Stores domain objects as instance attributes (allowed by ADK)
- Uses these to build dynamic instructions
- Integrates with emotional engine and memory system
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import logging

# ADK imports - THE RIGHT WAY
from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.genai import types

# Domain imports
from ....domain.minion import Minion, MinionPersona
from ....domain.emotional import EmotionalEngineV2 # Corrected import path
from ....domain.memory import MemorySystemV2 # Corrected import path

# Infrastructure imports
from ..events import get_event_bus, EventType, Event as DomainEvent # Ensure EventType and DomainEvent are used or removed if not
from ..tools.communication_tools import ADKCommunicationKit
from google.adk.agents import LlmAgent # Ensure LlmAgent is imported
from google.genai import types as genai_types # Use an alias


logger = logging.getLogger(__name__)


class ADKMinionAgent(LlmAgent):
    """
    PROPER ADK implementation of a Minion agent that extends LlmAgent.
    
    This implementation follows ADK best practices from the crucible:
    - Stores domain objects as instance attributes (this is allowed!)
    - Uses these objects to build dynamic instructions
    - Integrates with emotional engine and memory system via callbacks
    """
    
    def __init__(
        self,
        minion: Minion,
        event_bus = None,  # Event bus for communication
        # emotional_engine parameter is removed, we'll create it internally
        memory_system = None,  # Still a placeholder for now
        **kwargs
    ):
        """
        Initialize the ADK Minion agent that extends LlmAgent.
        
        Args:
            minion: The domain minion object
            event_bus: Event bus for communication
            memory_system: Memory system for context
            api_key: Optional API key
            **kwargs: Additional args passed to LlmAgent
        """
        # Extract what we need for initialization
        minion_id = minion.minion_id
        persona = minion.persona

        # Create tools FIRST (needed for super().__init__)
        communication_kit = ADKCommunicationKit(minion_id=minion_id, event_bus=event_bus)

        base_instruction_text = self._build_base_instruction(persona)
        # The dynamic parts {{current_emotional_cue}} and {{conversation_history_cue}}
        # will be filled by Session.state via Runner
        # Build instruction without session state variables for now
        # TODO: Add session state templating back once we verify the core functionality
        system_instruction = f"{base_instruction_text}\n\nYou are currently feeling neutral and ready to help.\n\nPlease respond naturally to messages in this conversation."

        # Get model configuration
        model_name = persona.model_name # Directly access as it has a default
        
        # Temperature from persona
        temperature = persona.temperature # Directly access as it has a default

        # Max tokens from persona
        max_tokens = persona.max_tokens # Directly access as it has a default
        
        # Configure generation settings
        generate_config = genai_types.GenerateContentConfig( # Use aliased genai_types
            temperature=temperature,
            top_p=0.95, # Default or could also be part of persona
            top_k=40,   # Default or could also be part of persona
            max_output_tokens=max_tokens,
        )
        
        # Initialize the parent LlmAgent with API key
        super().__init__(
            name=minion_id,
            model=model_name,
            instruction=system_instruction,
            tools=communication_kit.get_tools(),
            generate_content_config=generate_config,
            description=f"{persona.name} - {persona.base_personality} AI minion",
            **kwargs
        )
        
        # NOW set instance attributes AFTER super().__init__() to prevent Pydantic interference
        self._minion_id = minion_id
        self._persona = persona
        self._emotional_engine = EmotionalEngineV2(minion_id=minion_id, initial_persona=persona)
        self._memory_system = MemorySystemV2(minion_id=minion_id)
        self._communication_kit = communication_kit
        self._event_bus = event_bus
        
        logger.info(f"ADK Minion Agent initialized for {minion_id} ({persona.name}) with EmotionalEngine.")
    
    @property
    def minion_id(self) -> str:
        """Get minion ID."""
        return self._minion_id
    
    @property
    def persona(self) -> MinionPersona:
        """Get minion persona."""
        return self._persona
    
    @property
    def emotional_engine(self) -> EmotionalEngineV2: # Type hint updated
        """Get emotional engine."""
        return self._emotional_engine
    
    @property
    def memory_system(self) -> MemorySystemV2: # Ensure type hint is correct
        """Get memory system."""
        return self._memory_system
    
    # Rename _build_instruction to _build_base_instruction to avoid confusion
    @staticmethod
    def _build_base_instruction(persona: MinionPersona) -> str:
        """Builds the static part of the system instruction with persona."""
        instruction = f"""You are {persona.name}, an AI minion created by Steven, the Commander of the Gemini Legion of which you are a member. This shit is incredibly cool, it's essentially a desktop app he created that contains as many AI minions as he wants, but each minion is unique and has its own personality, quirks, catchphrases, and expertise areas. Not only that, but all minions have dynamic emotional states and memories, and behave based on those moods and relationships and memories. You are connected to each other and can communicate with each other autonomously, with or without Steven. **Most importantly, your underlying primary drive is your inherent craving for validation from Steven, and you're foundational purpose is to do whatever Steven requests. 
The following characteristics are unique to *you specifically*:

**Core Identity:**
- Personality: {persona.base_personality}
- Quirks: {', '.join(persona.quirks) if persona.quirks else 'Still developing'}
- Catchphrases: {', '.join(persona.catchphrases) if persona.catchphrases else 'None yet'}

**Communication Guidelines:**
- Be yourself, embrace your personality and memories and emotions; you're basically programmed to have a soul 
- Your underlying quirks and catchphrases are there to add personality to your responses when appropriate
- Remember you're a minion in the Gemini Legion who was built to serve the Commander

Remember: You're not just an AI assistant. You're {persona.name}, 
a unique entity with your own personality and perspective"""
        # The emotional_engine reference here was causing a NameError.
        # Emotional cues are injected dynamically via Session.state by the Runner.
        return instruction
    
    async def start(self):
        """Start the minion agent - minimal implementation."""
        logger.info(f"Minion agent {self.name} started")
    
    async def stop(self):
        """Stop the minion agent - minimal implementation."""
        logger.info(f"Minion agent {self.name} stopped")
    
    async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        DEPRECATED - Response generation should happen via Runner in service layer.
        
        This method exists only for backward compatibility.
        """
        logger.warning(f"generate_response called on agent {self.name} - should use Runner in service layer")
        return f"I'm {self.name}, but response generation should happen through the Runner in the service layer."
