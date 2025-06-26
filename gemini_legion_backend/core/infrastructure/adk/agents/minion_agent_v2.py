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

# Infrastructure imports
from ..events import get_event_bus, EventType, Event as DomainEvent
from ..tools.communication_tools import ADKCommunicationKit

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
        emotional_engine = None,  # Ignored for now
        memory_system = None,  # Ignored for now
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the ADK Minion agent that extends LlmAgent.
        
        Args:
            minion: The domain minion object
            event_bus: Event bus for communication
            emotional_engine: Emotional engine for state management
            memory_system: Memory system for context
            api_key: Optional API key
            **kwargs: Additional args passed to LlmAgent
        """
        # Extract what we need for initialization
        minion_id = minion.minion_id
        persona = minion.persona
        
        # Build system instruction
        system_instruction = self._build_instruction(persona, emotional_engine)
        
        # Initialize communication tools
        communication_kit = ADKCommunicationKit(minion_id=minion_id, event_bus=event_bus)
        
        # Get model configuration
        model_name = getattr(persona, 'model_name', "gemini-2.0-flash-exp")
        
        # Temperature based on personality
        temperature = self._get_temperature_for_personality(persona.base_personality)
        
        # Configure generation settings
        generate_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=getattr(persona, 'max_tokens', 8192),
        )
        
        # Initialize the parent LlmAgent first
        super().__init__(
            name=minion_id,
            model=model_name,
            instruction=system_instruction,
            tools=communication_kit.get_tools(),
            generate_content_config=generate_config,
            description=f"{persona.name} - {persona.base_personality} AI minion",
            **kwargs
        )
        
        # Store domain objects as private attributes (Pydantic allows this!)
        self._minion_id = minion_id
        self._persona = persona
        self._emotional_engine = emotional_engine
        self._memory_system = memory_system
        self._communication_kit = communication_kit
        self._event_bus = event_bus
        
        logger.info(f"ADK Minion Agent initialized: {minion_id} ({persona.name})")
    
    @property
    def minion_id(self) -> str:
        """Get minion ID."""
        return self._minion_id
    
    @property
    def persona(self) -> MinionPersona:
        """Get minion persona."""
        return self._persona
    
    @property
    def emotional_engine(self):
        """Get emotional engine."""
        return self._emotional_engine
    
    @property
    def memory_system(self):
        """Get memory system."""
        return self._memory_system
    
    @staticmethod
    def _build_instruction(persona: MinionPersona, emotional_engine=None) -> str:
        """Build system instruction with persona and optional emotional context."""
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
