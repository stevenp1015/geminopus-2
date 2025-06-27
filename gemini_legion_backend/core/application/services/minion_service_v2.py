"""
Minion Service V2 - Clean Event-Driven Implementation

This service manages minions using proper ADK patterns and event-driven architecture.
No more circular dependencies, no more custom communication systems.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
import os

# ADK imports
from google.adk import Runner
from google.genai.types import Content, Part

from ...domain import Minion, MinionPersona, EmotionalState, MoodVector, WorkingMemory
from ...infrastructure.persistence.repositories import MinionRepository
from ...infrastructure.adk.events import get_event_bus, EventType
from ...infrastructure.adk.agents.minion_agent_v2 import ADKMinionAgent

logger = logging.getLogger(__name__)


class MinionServiceV2:
    """
    Minion Service with proper architecture.
    
    Key principles:
    1. Clean separation from channel service (no circular deps)
    2. Event-driven state changes
    3. Proper ADK agent management
    4. No custom communication systems
    """
    
    def __init__(
        self,
        minion_repository: MinionRepository,
        api_key: Optional[str] = None,
        session_service: Optional[Any] = None  # ADK session service
    ):
        """
        Initialize the minion service.
        
        Args:
            minion_repository: Repository for minion persistence
            api_key: Optional Gemini API key
            session_service: ADK session service for Runner
        """
        self.minion_repo = minion_repository
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.session_service = session_service
        self.event_bus = get_event_bus()
        
        # Active minions
        self.minions: Dict[str, Minion] = {}
        self.agents: Dict[str, ADKMinionAgent] = {}
        self.runners: Dict[str, Any] = {}  # ADK Runners for each agent
        
        logger.info("MinionServiceV2 initialized")
    
    async def start(self):
        """Start the service"""
        logger.info("Starting MinionServiceV2...")
        
        # Subscribe to channel messages
        self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
        
        # Load existing minions
        await self._load_minions()
        
        # Start all active minions
        for minion in self.minions.values():
            if minion.status == "active":
                await self._start_minion_agent(minion)
        
        logger.info(f"MinionServiceV2 started with {len(self.agents)} active minions")
    
    async def stop(self):
        """Stop the service"""
        logger.info("Stopping MinionServiceV2...")
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Clear agents and runners
        self.agents.clear()
        self.runners.clear()
        
        logger.info("MinionServiceV2 stopped")
    
    async def spawn_minion(
        self,
        minion_id: str,
        name: str,
        base_personality: str,
        # personality_traits: List[str], # Obsolete for current MinionPersona model
        quirks: List[str],
        # response_length: str = "medium", # Obsolete for current MinionPersona model
        catchphrases: Optional[List[str]] = None,
        expertise_areas: Optional[List[str]] = None,
        model_name: str = "gemini-2.0-flash-exp"
    ) -> Dict[str, Any]:
        """Spawn a new minion"""
        # Check if exists
        if minion_id in self.minions:
            raise ValueError(f"Minion {minion_id} already exists")
        
        # Create persona
        persona = MinionPersona(
            name=name,
            base_personality=base_personality,
            # personality_traits=personality_traits, # Obsolete for current MinionPersona model
            quirks=quirks,
            # response_length=response_length, # Obsolete for current MinionPersona model
            catchphrases=catchphrases or [],
            expertise_areas=expertise_areas or [],
            allowed_tools=["send_channel_message", "listen_to_channel"],
            model_name=model_name
        )
        
        # Create emotional state
        emotional_state = EmotionalState(
            minion_id=minion_id,  # Pass the minion_id
            mood=MoodVector(
                valence=0.5,
                arousal=0.5,
                dominance=0.5
            ),
            energy_level=0.8, # Overrides default of 0.7
            stress_level=0.2  # Overrides default of 0.3
        )
        
        # Create minion
        minion = Minion(
            minion_id=minion_id,
            # name=name, # Name is part of persona
            persona=persona,
            emotional_state=emotional_state,
            working_memory=WorkingMemory(), # Add required working_memory
            # created_at is handled by default_factory in Minion
            # status is handled by default_factory in Minion
        )
        
        # Save to repository
        await self.minion_repo.save(minion)
        
        # Cache
        self.minions[minion_id] = minion
        
        # Start agent
        await self._start_minion_agent(minion)
        
        # Emit spawn event - agents will hear this
        await self.event_bus.emit(
            EventType.MINION_SPAWNED,
            data={
                "minion_id": minion_id,
                "name": name,
                "personality": base_personality,
                "status": "active"
            },
            source="minion_service"
        )
        
        logger.info(f"Spawned minion: {name} ({minion_id})")
        
        return self._minion_to_dict(minion)
    
    async def despawn_minion(self, minion_id: str) -> Dict[str, Any]:
        """Despawn a minion"""
        minion = self.minions.get(minion_id)
        if not minion:
            raise ValueError(f"Minion {minion_id} not found")
        
        # Stop agent if running
        if minion_id in self.agents:
            await self.agents[minion_id].stop()
            del self.agents[minion_id]
        
        # Update status
        minion.status = "inactive"
        await self.minion_repo.save(minion)
        
        # Emit despawn event
        await self.event_bus.emit(
            EventType.MINION_DESPAWNED,
            data={
                "minion_id": minion_id,
                "name": minion.persona.name
            },
            source="minion_service"
        )
        
        logger.info(f"Despawned minion: {minion.persona.name} ({minion_id})")
        
        return {"status": "despawned", "minion_id": minion_id}
    
    async def list_minions(
        self,
        status_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List minions with filtering"""
        minions = list(self.minions.values())
        
        # Apply filter
        if status_filter:
            minions = [m for m in minions if m.status == status_filter]
        
        # Apply pagination
        minions = minions[offset:offset + limit]
        
        return [self._minion_to_dict(m) for m in minions]
    
    async def get_minion(self, minion_id: str) -> Optional[Dict[str, Any]]:
        """Get minion details"""
        minion = self.minions.get(minion_id)
        if not minion:
            minion = await self.minion_repo.get_by_id(minion_id)
            if not minion:
                return None
        
        return self._minion_to_dict(minion)
    
    async def update_emotional_state(
        self,
        minion_id: str,
        mood_delta: Optional[Dict[str, float]] = None,
        energy_delta: Optional[float] = None,
        stress_delta: Optional[float] = None
    ) -> Dict[str, Any]:
        """Update minion's emotional state"""
        minion = self.minions.get(minion_id)
        if not minion:
            raise ValueError(f"Minion {minion_id} not found")
        
        # Update mood
        if mood_delta:
            for key, delta in mood_delta.items():
                if hasattr(minion.emotional_state.mood, key):
                    current = getattr(minion.emotional_state.mood, key)
                    # Clamp between -1 and 1 (or 0 and 1 for some)
                    new_value = max(-1, min(1, current + delta))
                    setattr(minion.emotional_state.mood, key, new_value)
        
        # Update energy
        if energy_delta is not None:
            minion.emotional_state.energy_level = max(
                0, min(1, minion.emotional_state.energy_level + energy_delta)
            )
        
        # Update stress
        if stress_delta is not None:
            minion.emotional_state.stress_level = max(
                0, min(1, minion.emotional_state.stress_level + stress_delta)
            )
        
        # Save
        await self.minion_repo.save(minion)
        
        # Emit event
        await self.event_bus.emit(
            EventType.MINION_EMOTIONAL_CHANGE,
            data={
                "minion_id": minion_id,
                "emotional_state": self._emotional_state_to_dict(minion.emotional_state)
            },
            source="minion_service"
        )
        
        return self._minion_to_dict(minion)
    
    async def _load_minions(self):
        """Load minions from repository"""
        try:
            minions = await self.minion_repo.list_all()
            
            for minion in minions:
                self.minions[minion.minion_id] = minion
            
            logger.info(f"Loaded {len(minions)} minions from repository")
            
            # Ensure at least one default minion exists
            if not minions:
                await self._create_default_minion()
                
        except Exception as e:
            logger.error(f"Failed to load minions: {e}")
    
    async def _create_default_minion(self):
        """Create a default minion"""
        await self.spawn_minion(
            minion_id="echo_prime",
            name="Echo",
            base_personality="Friendly and helpful assistant",
            # personality_traits=["curious", "enthusiastic", "supportive"], # Obsolete, merged into quirks below
            quirks=["Uses lots of exclamation points!", "Loves learning new things", "curious", "enthusiastic", "supportive"],
            # response_length="medium", # Obsolete
            catchphrases=["Let's explore that!", "How fascinating!", "I'm here to help!"]
        )
    
    async def _start_minion_agent(self, minion: Minion):
        """Start an agent for a minion"""
        try:
            agent = ADKMinionAgent(
                minion=minion,
                event_bus=self.event_bus,
                api_key=self.api_key
            )
            
            await agent.start()
            
            # Create Runner for this agent
            if self.session_service:
                runner = Runner(
                    agent=agent,
                    app_name="gemini-legion",
                    session_service=self.session_service
                )
                self.runners[minion.minion_id] = runner
                logger.info(f"Created Runner for {minion.persona.name}")
            else:
                logger.warning(f"No session service available for Runner creation")
            
            self.agents[minion.minion_id] = agent
            
            logger.info(f"Started agent for {minion.persona.name} ({minion.minion_id})")
            
        except Exception as e:
            logger.error(f"Failed to start agent for {minion.minion_id}: {e}")
    
    def _minion_to_dict(self, minion: Minion) -> Dict[str, Any]:
        """Convert minion to dict"""
        return {
            "minion_id": minion.minion_id,
            "name": minion.persona.name, # Correctly access name from persona
            "status": minion.status.health_status, # Access health_status from MinionStatus object
            "created_at": minion.creation_date.isoformat(), # Correct attribute is creation_date
            "persona": {
                "base_personality": minion.persona.base_personality,
                # "personality_traits": minion.persona.personality_traits, # Obsolete
                "quirks": minion.persona.quirks,
                # "response_length": minion.persona.response_length, # Obsolete
                "catchphrases": minion.persona.catchphrases,
                "expertise_areas": minion.persona.expertise_areas,
                "model_name": minion.persona.model_name
            },
            "emotional_state": self._emotional_state_to_dict(minion.emotional_state),
            "is_active": minion.minion_id in self.agents
        }
    
    def _emotional_state_to_dict(self, state: EmotionalState) -> Dict[str, Any]:
        """Convert emotional state to dict"""
        return {
            "mood": {
                "valence": state.mood.valence,
                "arousal": state.mood.arousal,
                "dominance": state.mood.dominance
            },
            "energy_level": state.energy_level,
            "stress_level": state.stress_level
        }
    
    async def _handle_channel_message(self, event: Any):
        """
        Handle incoming channel messages and make minions respond.
        
        This is where the magic happens - minions come alive!
        """
        try:
            # Extract data from event object
            event_data = event.data if hasattr(event, 'data') else event
            
            channel_id = event_data.get("channel_id")
            sender_id = event_data.get("sender_id")
            content = event_data.get("content")
            
            # Don't respond to system messages or other minions for now
            if sender_id == "system" or sender_id in self.agents:
                return
            
            logger.info(f"Channel message in {channel_id}: {content[:50]}...")
            
            # For now, have all active minions in channel respond
            # In future, could add logic for who responds when
            for minion_id, agent in self.agents.items():
                minion = self.minions.get(minion_id)
                if not minion:
                    continue
                
                # Check if minion is in this channel (simplified check)
                # In real implementation, would check channel membership
                
                # Generate response using Runner
                try:
                    runner = self.runners.get(minion_id)
                    if not runner:
                        logger.warning(f"No runner found for minion {minion_id}")
                        continue
                    
                    # Use predict for simpler request-response
                    try:
                        response_text = await runner.predict(
                            message=content,
                            session_id=f"{channel_id}_{minion_id}",
                            user_id=sender_id
                        )
                    except Exception as e:
                        logger.error(f"Error with predict: {e}")
                        # Try without session_id if session not found
                        try:
                            response_text = await runner.predict(
                                message=content,
                                user_id=sender_id
                            )
                        except Exception as e2:
                            logger.error(f"Error with predict (no session): {e2}")
                            continue
                    
                    if response_text:
                        # Send minion's response back to channel
                        await self.event_bus.emit_channel_message(
                            channel_id=channel_id,
                            sender_id=minion_id,
                            content=response_text,
                            source=f"minion:{minion_id}"
                        )
                        
                        logger.info(f"Minion {minion_id} responded to message")
                    else:
                        logger.warning(f"Minion {minion_id} generated empty response")
                    
                except Exception as e:
                    logger.error(f"Error generating response for {minion_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling channel message: {e}")
