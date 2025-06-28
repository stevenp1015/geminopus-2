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
        api_key: Optional[str] = None,
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

        # Initialize EmotionalEngine for this agent
        # Pass the persona to allow EmotionalEngine to set initial mood if logic exists
        self._emotional_engine = EmotionalEngineV2(minion_id=minion_id, initial_persona=persona)
        
        # Store other domain objects as private attributes
        self._minion_id = minion_id
        self._persona = persona
        self._memory_system = MemorySystemV2(minion_id=minion_id) # Instantiate MemorySystemV2
        self._communication_kit = ADKCommunicationKit(minion_id=minion_id, event_bus=event_bus)
        self._event_bus = event_bus

        base_instruction_text = self._build_base_instruction(persona)
        # The dynamic parts {{current_emotional_cue}} and {{conversation_history_cue}}
        # will be filled by Session.state via Runner
        system_instruction = f"{base_instruction_text}\n\nYour current emotional disposition: {{current_emotional_cue}}\n\nConversation Context:\n{{conversation_history_cue}}"

        # Get model configuration
        model_name = getattr(persona, 'model_name', "gemini-1.5-flash-latest") # Updated default model
        
        # Temperature based on personality
        temperature = self._get_temperature_for_personality(persona.base_personality)
        
        # Configure generation settings
        generate_config = genai_types.GenerateContentConfig( # Use aliased genai_types
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=getattr(persona, 'max_tokens', 8192),
        )
        
        # Initialize the parent LlmAgent first
        super().__init__(
            name=minion_id,
            model=model_name,
            instruction=system_instruction, # Instruction now has a placeholder
            tools=self._communication_kit.get_tools(),
            generate_content_config=generate_config,
            description=f"{persona.name} - {persona.base_personality} AI minion",
            # Callbacks will be added in the next step
            **kwargs
        )
        
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
        instruction = f"""You are {persona.name}, a unique AI minion with the following characteristics:

**Core Identity:**
- Personality: {persona.base_personality}
- Quirks: {', '.join(persona.quirks) if persona.quirks else 'Still developing'}
- Catchphrases: {', '.join(persona.catchphrases) if persona.catchphrases else 'None yet'}

**Communication Guidelines:**
- Be yourself! Embrace your personality fully
- Use your quirks and catchphrases when appropriate
- Remember you're part of a team of minions

Remember: You're not just an AI assistant - you're {persona.name}, 
a unique entity with your own personality and perspective!"""
        
        # Add emotional context if available
        if emotional_engine:
            # TODO: Add emotional state to instruction once engine is integrated
            pass
            
        return instruction
    
    @staticmethod
    def _get_temperature_for_personality(base_personality: str) -> float:
        """Get temperature based on personality."""
        personality_temps = {
            "Analytical": 0.3,
            "Creative": 0.9,
            "Chaotic": 1.0,
            "Friendly": 0.7,
            "Professional": 0.4,
            "Witty": 0.8,
            "Enthusiastic": 0.85,
            "Wise": 0.5,
            "Mischievous": 0.95,
            "grumpy hacker": 0.6,
            "cheerful helper": 0.8
        }
        return personality_temps.get(base_personality, 0.7)
    
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
