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
from google.genai import types as genai_types

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
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.session_service = session_service
        self.event_bus = get_event_bus()
        
        # Active minions
        self.minions: Dict[str, Minion] = {}
        self.agents: Dict[str, ADKMinionAgent] = {}
        self.runners: Dict[str, Any] = {}  # ADK Runners for each agent
        
        logger.info("MinionServiceV2 initialized")
    
    async def update_minion_persona(self, minion_id: str, persona_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a minion's persona."""
        minion = self.minions.get(minion_id)
        if not minion:
            minion = await self.minion_repo.get_by_id(minion_id) # Try loading from repo
            if not minion:
                raise ValueError(f"Minion {minion_id} not found")
            self.minions[minion_id] = minion # Cache if found in repo

        agent = self.agents.get(minion_id)
        runner = self.runners.get(minion_id)

        # Update MinionPersona object
        updated_fields = False
        for key, value in persona_data.items():
            if hasattr(minion.persona, key) and value is not None:
                setattr(minion.persona, key, value)
                updated_fields = True
                logger.info(f"Minion {minion_id} persona field '{key}' updated to '{value}'.")

        if not updated_fields:
            logger.info(f"No persona fields provided or changed for minion {minion_id}.")
            return self._minion_to_dict(minion) # Return current state if nothing changed

        # If critical fields that affect the agent's instruction or model config change,
        # the agent might need to be re-initialized or its runner reconfigured.
        critical_persona_fields_changed = any(
            key in persona_data for key in ["name", "base_personality", "model_name", "temperature", "max_tokens"]
        )

        if agent and critical_persona_fields_changed:
            logger.info(f"Critical persona fields changed for minion {minion_id}. Re-evaluating agent/runner.")
            # This is a simplified re-evaluation. A full re-init might be:
            # await agent.stop()
            # new_agent = ADKMinionAgent(minion=minion, event_bus=self.event_bus, api_key=self.api_key)
            # await new_agent.start()
            # self.agents[minion_id] = new_agent
            # if self.session_service:
            #     new_runner = Runner(agent=new_agent, app_name="gemini-legion", session_service=self.session_service)
            #     self.runners[minion_id] = new_runner
            # logger.info(f"Re-initialized agent and runner for minion {minion_id} due to persona changes.")

            # For now, let's assume the ADKMinionAgent can dynamically build its instruction
            # or that its existing config (like model_name) is mostly static after init.
            # A more robust solution would involve updating agent.instruction and agent.generate_content_config
            # and possibly re-creating the runner if model_name changes.
            # The current ADKMinionAgent re-builds instruction text at init based on persona.
            # If the agent or runner needs full re-creation, that's a more involved step.
            # We will rely on the fact that the persona object itself is updated, and if the agent
            # references this persona object for its operations (e.g. _build_base_instruction called dynamically),
            # it might pick up changes. However, instruction is set at __init__.

            # A pragmatic approach for now:
            # If name changed, it primarily affects logging/display.
            # If base_personality, model_name, temperature, max_tokens change, ideally agent is reconfigured.
            # For this iteration, we'll log a warning if a full re-init would be needed.
            if any(key in persona_data for key in ["model_name"]):
                 logger.warning(f"Minion {minion_id} model_name changed. Full agent/runner re-initialization might be required for this to take effect in ADK predict calls.")

            # Update agent's internal persona reference if it's a copy, though it should be a direct reference.
            if hasattr(agent, 'persona'):
                # Note: The persona property is read-only, but the underlying _persona should be updated
                # For now, we rely on the fact that the persona object itself is updated in the repository
                logger.debug(f"Agent for {minion_id} has persona property - persona updates should be reflected")
            else:
                logger.warning(f"Agent for {minion_id} doesn't have persona property")


        await self.minion_repo.save(minion)

        updated_minion_data = self._minion_to_dict(minion)
        await self.event_bus.emit(
            EventType.MINION_STATE_CHANGED, # Using a general state change event for now
            data=updated_minion_data,
            source="minion_service:persona_update"
        )
        logger.info(f"Minion {minion_id} persona updated and event emitted.")
        return updated_minion_data

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
        model_name: str = "gemini-2.5-flash", # Changed default model
        allowed_tools: Optional[List[str]] = None
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
            allowed_tools=allowed_tools if allowed_tools is not None else ["send_channel_message", "listen_to_channel"],
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
            data={"minion": self._minion_to_dict(minion)}, # Use the full minion dict
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
            catchphrases=["Let's explore that!", "How fascinating!", "I'm here to help!"],
            allowed_tools=None # Explicitly pass None to use defaults in spawn_minion's Persona creation
        )
    
    async def _start_minion_agent(self, minion: Minion):
        """Start an agent for a minion"""
        try:
            os.environ['GOOGLE_API_KEY'] = self.api_key
            agent = ADKMinionAgent(
                minion=minion,
                event_bus=self.event_bus,
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
        """Convert minion to dict to match frontend MinionType"""

        # Status mapping
        domain_status = minion.status.health_status.lower() # e.g. "operational", "error"
        frontend_status = "idle" # Default
        if domain_status == "operational":
            frontend_status = "active"
        elif domain_status == "error":
            frontend_status = "error"
        # Add other mappings if MinionStatus.health_status becomes more varied (e.g., busy)

        persona_dict = {
            "minion_id": minion.minion_id, # Frontend MinionPersona expects minion_id
            "name": minion.persona.name,
            "base_personality": minion.persona.base_personality,
            "quirks": minion.persona.quirks,
            "catchphrases": minion.persona.catchphrases,
            "expertise_areas": minion.persona.expertise_areas,
            "allowed_tools": minion.persona.allowed_tools,
            "model_name": minion.persona.model_name,
            "temperature": minion.persona.temperature,
            "max_tokens": minion.persona.max_tokens
        }

        return {
            "minion_id": minion.minion_id,
            # "name": minion.persona.name, # Name is in persona dict
            "status": frontend_status,
            "creation_date": minion.creation_date.isoformat(), # Renamed from created_at
            "persona": persona_dict,
            "emotional_state": self._emotional_state_to_dict(minion.emotional_state),
            # "is_active": minion.minion_id in self.agents # is_active is implicit in status
            # current_task and memory_stats are optional in frontend, can be added if available
        }
    
    def _emotional_state_to_dict(self, state: EmotionalState) -> Dict[str, Any]:
        """Convert emotional state to dict"""
        # Ensure commander opinion exists for frontend
        if "commander" not in state.opinion_scores:
            state.get_opinion_of("commander")  # Creates default opinion if not exists
        
        # Convert opinion scores to the full object format expected by frontend
        opinion_scores_dict = {}
        for entity_id, opinion_score in state.opinion_scores.items():
            opinion_scores_dict[entity_id] = {
                "affection": opinion_score.affection * 100,  # Convert to 0-100 scale
                "trust": opinion_score.trust * 100,         # Convert to 0-100 scale  
                "respect": opinion_score.respect * 100,     # Convert to 0-100 scale
                "overall_sentiment": opinion_score.overall_sentiment
            }
        
        return {
            "mood": {
                "valence": state.mood.valence,
                "arousal": state.mood.arousal,
                "dominance": state.mood.dominance
            },
            "energy_level": state.energy_level,
            "stress_level": state.stress_level,
            "opinion_scores": opinion_scores_dict  # Now with proper object structure
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
                    
                    # Runner should have been fetched already for the current minion_id in the loop
                    # Construct a consistent session ID for the interaction
                    agent_instance = self.agents.get(minion_id) # Ensure agent_instance is correctly fetched
                    minion_obj = self.minions.get(minion_id)
                    runner = self.runners.get(minion_id)

                    if not all([agent_instance, minion_obj, runner]):
                        logger.warning(f"Missing agent, minion object, or runner for {minion_id}. Skipping.")
                        continue

                    # This part will be added/refined in Step 2.2.2
                    # For now, ensure the structure for session_state is ready

                    current_session_id = f"channel_{channel_id}_minion_{minion_id}"
                    # logger.info(f"Attempting predict for minion {minion_id} with session_id: {current_session_id} ...") # Already logged

                    # Get the emotional cue from the agent's emotional engine
                    emotional_cue = "feeling neutral" # Default cue
                    if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                        try:
                            emotional_cue = agent_instance.emotional_engine.get_current_state_summary_for_prompt()
                            logger.debug(f"Minion {minion_id} emotional cue for prompt: {emotional_cue}")
                        except Exception as e:
                            logger.error(f"Error getting emotional cue for {minion_id}: {e}")

                    # 1. Record incoming message to this minion's working memory
                    if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                        # Determine role for the incoming message
                        incoming_role = "user" # Default role for sender
                        if sender_id == minion_id:
                            incoming_role = agent_instance.persona.name
                        elif sender_id in self.agents: # If sender is another known minion
                            sender_minion_obj = self.minions.get(sender_id)
                            incoming_role = sender_minion_obj.persona.name if sender_minion_obj else sender_id
                        elif sender_id == "system":
                            incoming_role = "system"

                        agent_instance.memory_system.record_interaction(role=incoming_role, content=content)
                        logger.debug(f"Recorded incoming message from '{sender_id}' (as role '{incoming_role}') to {minion_id}'s working memory.")

                    current_session_id = f"channel_{channel_id}_minion_{minion_id}"

                    emotional_cue = "feeling neutral"
                    if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                        try:
                            emotional_cue = agent_instance.emotional_engine.get_current_state_summary_for_prompt()
                        except Exception as e:
                            logger.error(f"Error getting emotional cue for {minion_id}: {e}")

                    # 2. Get memory context for the prompt
                    memory_cue = "No recent conversation history available."
                    if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                        try:
                            memory_cue = agent_instance.memory_system.get_prompt_context()
                        except Exception as e:
                            logger.error(f"Error getting memory cue for {minion_id}: {e}")

                    session_state_for_predict = {
                        "current_emotional_cue": emotional_cue,
                        "conversation_history_cue": memory_cue
                    }
                    logger.debug(f"Session state for predict for {minion_id}: emotional_cue='{emotional_cue}', history_cue='{memory_cue[:60]}...'")

                    response_text = None # Initialize before try block
                    agent_response_content = None
                    try:
                        # Create proper Content format for ADK Runner
                        message_content = genai_types.Content(
                            role='user',
                            parts=[genai_types.Part(text=content)]
                        )
                        
                        # Update session state BEFORE calling runner
                        try:
                            # CREATE the session if it doesn't exist (ADK requirement)
                            session = await self.session_service.create_session(
                                app_name="gemini-legion",
                                user_id=sender_id,
                                session_id=current_session_id
                            )
                            
                            # Update session state with emotional and memory context
                            session.state.update({
                                "current_emotional_cue": emotional_cue,
                                "conversation_history_cue": memory_cue
                            })
                            
                            # InMemorySessionService auto-saves, no explicit save needed
                            logger.debug(f"Created and updated session state for {minion_id}: emotional_cue='{emotional_cue}', history_cue='{memory_cue[:60]}...'")
                            
                        except Exception as e:
                            logger.error(f"Failed to create/update session state for {minion_id}: {e}")
                            # Continue with execution but log the issue
                        
                        # Call runner with correct ADK parameters
                        agent_response_generator = runner.run_async(
                            user_id=sender_id,
                            session_id=current_session_id,
                            new_message=message_content
                        )

                        # Process events from ADK Runner
                        final_agent_response_content: Optional[Content] = None
                        async for event_obj in agent_response_generator:
                            # Log event for debugging
                            logger.debug(f"Received event from {minion_id}: type={type(event_obj).__name__}, final={event_obj.is_final_response()}")

                            # Check for content in the event
                            if event_obj.content and event_obj.content.parts:
                                # Look for text parts
                                text_parts = [part.text for part in event_obj.content.parts if hasattr(part, 'text') and part.text]
                                if text_parts:
                                    final_agent_response_content = event_obj.content
                                    logger.debug(f"Found text content in event from {minion_id}: {text_parts[0][:50]}...")

                            # Break on final response to avoid processing duplicate events
                            if event_obj.is_final_response():
                                logger.debug(f"Final response event received from {minion_id}")
                                break

                        if final_agent_response_content and final_agent_response_content.parts:
                            # Extract text from all text parts
                            text_parts = [part.text for part in final_agent_response_content.parts if hasattr(part, 'text') and part.text]
                            response_text = "".join(text_parts)
                            logger.info(f"Minion {minion_id} ({agent_instance.persona.name}) response: {response_text}")
                        else:
                            logger.warning(f"Minion {minion_id} returned no text response from ADK runner")

                    except Exception as e:
                        logger.error(f"Error during ADK runner execution for minion {minion_id} (session {current_session_id}): {str(e)}", exc_info=True)
                        
                        # Provide fallback response to prevent silent failures
                        # Safe access to persona name in case of initialization issues
                        persona_name = "Unknown Minion"
                        try:
                            persona_name = agent_instance.persona.name
                        except:
                            # Fallback if persona access fails
                            persona_name = minion_id
                        
                        response_text = f"[Error: {persona_name} encountered an issue processing your message]"
                        
                        # Emit error event for debugging
                        if self.event_bus:
                            await self.event_bus.emit(
                                EventType.MINION_ERROR,
                                data={
                                    "minion_id": minion_id,
                                    "error": str(e),
                                    "channel_id": channel_id,
                                    "message": content[:100]
                                },
                                source="minion_service:adk_runner_error"
                            )
                    
                    if response_text:
                        # 3. Record minion's own response to its working memory
                        if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                            # Safe access to persona name
                            persona_name = minion_id  # Fallback
                            try:
                                persona_name = agent_instance.persona.name
                            except:
                                pass  # Use fallback
                            
                            agent_instance.memory_system.record_interaction(role=persona_name, content=response_text)
                            logger.debug(f"Recorded own response from {minion_id} (as role '{persona_name}') to its working memory.")

                        # Update emotional state
                        if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                            agent_instance.emotional_engine.update_state_from_interaction(f"Responded to: {content[:30]} in channel {channel_id}")
                            emotional_state_dict = self._emotional_state_to_dict(agent_instance.emotional_engine.current_state)
                            await self.event_bus.emit(
                                EventType.MINION_EMOTIONAL_CHANGE,
                                data={"minion_id": minion_id, "emotional_state": emotional_state_dict},
                                source="minion_service:post_interaction"
                            )

                        # Send minion's response back to channel
                        await self.event_bus.emit_channel_message(
                            channel_id=channel_id,
                            sender_id=minion_id,
                            content=response_text,
                            source=f"minion:{minion_id}"
                        )
                        logger.info(f"Minion {minion_id} responded to message in channel {channel_id}")
                    else:
                        # This block now also catches cases where predict() failed and response_text is None
                        logger.warning(f"Minion {minion_id} generated no response or failed to predict for channel {channel_id} for message: '{content[:30]}...'")
                    
                except Exception as e:
                    logger.error(f"Error generating response for {minion_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling channel message: {e}")
