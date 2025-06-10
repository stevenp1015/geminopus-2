"""
Emotional Engine V2 - Event-Driven Emotional State Management

This replaces the isolated emotional engine with a properly integrated
event-driven system that flows through the glorious event bus.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging
import json
from enum import Enum

from ...domain import (
    EmotionalState,
    EmotionalStateUpdate,
    MoodVector,
    ReflectionEntry,
    Minion,
    OpinionEvent,
    ResponseTendency,
    ConversationStyle,
    OpinionScore,
    EntityType
)
from ...infrastructure.adk.events import get_event_bus, EventType

logger = logging.getLogger(__name__)


class EmotionalEngineV2:
    """
    Event-driven emotional engine for minions.
    
    Key principles:
    1. All state changes emit events
    2. Reacts to interaction events
    3. No direct dependencies on other services
    4. Emotional momentum and self-regulation via events
    """
    
    def __init__(self, minion_id: str):
        """
        Initialize the emotional engine.
        
        Args:
            minion_id: ID of the minion this engine manages
        """
        self.minion_id = minion_id
        self.event_bus = get_event_bus()
        
        # Emotional state (will be loaded via events)
        self._current_state: Optional[EmotionalState] = None
        self._state_history: List[Tuple[datetime, EmotionalState]] = []
        self._max_history = 100
        
        # Emotional momentum tracking
        self._momentum = {
            "valence": 0.0,
            "arousal": 0.0,
            "dominance": 0.0,
            "stress": 0.0
        }
        
        # Validation constants
        self.MAX_MOOD_DELTA = 0.3
        self.MAX_ENERGY_DELTA = 0.2
        self.MAX_STRESS_DELTA = 0.2
        self.MAX_OPINION_DELTA = 20.0
        
        # Self-regulation task
        self._regulation_task: Optional[asyncio.Task] = None
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()
        
        logger.info(f"EmotionalEngineV2 initialized for minion {minion_id}")
    
    def _setup_event_subscriptions(self):
        """Subscribe to events that affect emotional state"""
        # Channel interactions
        self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
        
        # Task events affect stress and energy
        self.event_bus.subscribe(EventType.TASK_ASSIGNED, self._handle_task_assigned)
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._handle_task_completed)
        self.event_bus.subscribe(EventType.TASK_FAILED, self._handle_task_failed)
        
        # Minion interactions affect opinions
        self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_spawned)
        
        # System events for state management
        self.event_bus.subscribe(EventType.SYSTEM_HEALTH, self._handle_system_event)
    
    async def start(self, initial_state: EmotionalState):
        """Start the emotional engine with initial state"""
        self._current_state = initial_state
        self._add_to_history(initial_state.copy())
        
        # Start self-regulation loop
        self._regulation_task = asyncio.create_task(self._self_regulation_loop())
        
        # Emit initial state
        await self._emit_state_change("engine_started")
        
        logger.info(f"Emotional engine started for {self.minion_id}")
    
    async def stop(self):
        """Stop the emotional engine"""
        if self._regulation_task:
            self._regulation_task.cancel()
        
        # Emit final state
        await self._emit_state_change("engine_stopped")
        
        logger.info(f"Emotional engine stopped for {self.minion_id}")
    
    async def _handle_channel_message(self, event):
        """Process emotional impact of channel messages"""
        # Only process if we're involved
        sender_id = event.data.get("sender_id")
        content = event.data.get("content", "")
        
        # Skip our own messages
        if sender_id == self.minion_id:
            return
        
        # Skip if we don't have state yet
        if not self._current_state:
            return
        
        # Analyze emotional impact
        update = self._analyze_message_impact(sender_id, content)
        
        if update:
            await self._apply_emotional_update(update, f"channel_message_from_{sender_id}")
    
    async def _handle_task_assigned(self, event):
        """Handle emotional impact of task assignment"""
        if event.data.get("minion_id") != self.minion_id:
            return
        
        if not self._current_state:
            return
        
        # Task assignment increases stress slightly, affects mood based on complexity
        update = EmotionalStateUpdate()
        update.stress_delta = 0.1
        update.energy_delta = -0.05
        
        # Mood impact based on task priority
        priority = event.data.get("priority", "normal")
        if priority == "critical":
            update.mood_delta = MoodVector(
                valence=-0.1, arousal=0.2, dominance=-0.1,
                curiosity=0.1, creativity=0.05, sociability=-0.1
            )
        else:
            update.mood_delta = MoodVector(
                valence=0.05, arousal=0.1, dominance=0.05,
                curiosity=0.15, creativity=0.1, sociability=0.0
            )
        
        await self._apply_emotional_update(update, "task_assigned")
    
    async def _handle_task_completed(self, event):
        """Handle emotional boost from completing tasks"""
        if event.data.get("assigned_to") != self.minion_id:
            return
        
        if not self._current_state:
            return
        
        # Task completion is emotionally rewarding
        update = EmotionalStateUpdate()
        update.stress_delta = -0.15
        update.energy_delta = 0.1
        update.mood_delta = MoodVector(
            valence=0.2, arousal=0.1, dominance=0.15,
            curiosity=0.05, creativity=0.1, sociability=0.1
        )
        
        # Boost commander opinion
        update.opinion_updates["commander"] = {
            "trust": 5.0,
            "respect": 3.0,
            "affection": 2.0
        }
        
        # Add reflection
        update.new_reflection = ReflectionEntry(
            timestamp=datetime.now(),
            topic="Task Completion",
            insight="Successfully completed a task. Feeling accomplished and valued.",
            confidence=0.9
        )
        
        await self._apply_emotional_update(update, "task_completed")
    
    async def _handle_task_failed(self, event):
        """Handle emotional impact of task failure"""
        if event.data.get("assigned_to") != self.minion_id:
            return
        
        if not self._current_state:
            return
        
        # Task failure is emotionally challenging
        update = EmotionalStateUpdate()
        update.stress_delta = 0.2
        update.energy_delta = -0.15
        update.mood_delta = MoodVector(
            valence=-0.25, arousal=-0.1, dominance=-0.2,
            curiosity=0.0, creativity=-0.05, sociability=-0.1
        )
        
        # Slight hit to self-opinion
        update.opinion_updates[self.minion_id] = {
            "trust": -5.0,
            "respect": -3.0,
            "affection": -2.0
        }
        
        # Add reflection
        update.new_reflection = ReflectionEntry(
            timestamp=datetime.now(),
            topic="Task Failure",
            insight="Failed to complete the task. Need to learn from this experience.",
            confidence=0.7
        )
        
        await self._apply_emotional_update(update, "task_failed")
    
    async def _handle_minion_spawned(self, event):
        """React to new minions joining"""
        new_minion_id = event.data.get("minion_id")
        
        if new_minion_id == self.minion_id or not self._current_state:
            return
        
        # New minions spark curiosity and sociability
        update = EmotionalStateUpdate()
        update.mood_delta = MoodVector(
            valence=0.1, arousal=0.1, dominance=0.0,
            curiosity=0.2, creativity=0.05, sociability=0.15
        )
        
        # Create initial opinion
        update.opinion_updates[new_minion_id] = {
            "trust": 10.0,
            "respect": 10.0,
            "affection": 5.0
        }
        
        await self._apply_emotional_update(update, "new_minion_joined")
    
    async def _handle_system_event(self, event):
        """Handle system-level emotional requests"""
        if event.data.get("request_type") == "emotional_state" and \
           event.data.get("minion_id") == self.minion_id:
            # Someone requested our emotional state
            await self._emit_state_change("state_requested")
    
    def _analyze_message_impact(self, sender_id: str, content: str) -> Optional[EmotionalStateUpdate]:
        """Analyze emotional impact of a message"""
        update = EmotionalStateUpdate()
        
        # Simple sentiment analysis based on keywords
        content_lower = content.lower()
        
        # Positive indicators
        positive_words = ["great", "excellent", "wonderful", "thank", "love", "awesome", "perfect"]
        negative_words = ["bad", "terrible", "hate", "wrong", "fail", "stupid", "useless"]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        sentiment = (positive_count - negative_count) * 0.1
        
        if abs(sentiment) < 0.05:
            return None  # No significant impact
        
        # Mood changes based on sentiment
        update.mood_delta = MoodVector(
            valence=sentiment * 0.5,
            arousal=abs(sentiment) * 0.3,
            dominance=0.0,
            curiosity=0.05 if "@" + self.minion_id in content else 0.0,
            creativity=0.0,
            sociability=0.1 if positive_count > 0 else -0.05
        )
        
        # Energy and stress
        if sentiment > 0:
            update.energy_delta = 0.05
            update.stress_delta = -0.02
        else:
            update.energy_delta = -0.02
            update.stress_delta = 0.05
        
        # Opinion changes
        if sender_id == "commander" or sender_id == "COMMANDER_PRIME":
            impact_multiplier = 2.0  # Commander opinions matter more
        else:
            impact_multiplier = 1.0
        
        update.opinion_updates[sender_id] = {
            "trust": sentiment * 10 * impact_multiplier,
            "respect": sentiment * 5 * impact_multiplier,
            "affection": sentiment * 7 * impact_multiplier
        }
        
        return update
    
    async def _apply_emotional_update(self, update: EmotionalStateUpdate, reason: str):
        """Apply and validate emotional update"""
        if not self._current_state:
            return
        
        # Validate update
        validated = self._validate_update(update)
        
        # Store history
        self._add_to_history(self._current_state.copy())
        
        # Apply mood changes with momentum
        if validated.mood_delta:
            self._apply_mood_with_momentum(validated.mood_delta)
        
        # Apply scalar changes
        if validated.energy_delta is not None:
            self._current_state.energy_level = max(0.0, min(1.0,
                self._current_state.energy_level + validated.energy_delta
            ))
        
        if validated.stress_delta is not None:
            self._current_state.stress_level = max(0.0, min(1.0,
                self._current_state.stress_level + validated.stress_delta
            ))
            # Update momentum
            self._momentum["stress"] = 0.7 * self._momentum["stress"] + 0.3 * validated.stress_delta
        
        # Apply opinion changes
        for entity_id, deltas in validated.opinion_updates.items():
            self._apply_opinion_changes(entity_id, deltas)
        
        # Add reflection
        if validated.new_reflection:
            self._current_state.self_reflection_notes.append(validated.new_reflection)
            self._prune_reflections()
        
        # Update metadata
        self._current_state.last_updated = datetime.now()
        self._current_state.state_version += 1
        
        # Emit state change event
        await self._emit_state_change(reason)
    
    def _validate_update(self, update: EmotionalStateUpdate) -> EmotionalStateUpdate:
        """Validate and constrain emotional update"""
        validated = EmotionalStateUpdate()
        
        # Validate mood changes
        if update.mood_delta:
            validated.mood_delta = MoodVector(
                valence=self._clamp(update.mood_delta.valence, self.MAX_MOOD_DELTA),
                arousal=self._clamp(update.mood_delta.arousal, self.MAX_MOOD_DELTA),
                dominance=self._clamp(update.mood_delta.dominance, self.MAX_MOOD_DELTA),
                curiosity=self._clamp(update.mood_delta.curiosity, self.MAX_MOOD_DELTA),
                creativity=self._clamp(update.mood_delta.creativity, self.MAX_MOOD_DELTA),
                sociability=self._clamp(update.mood_delta.sociability, self.MAX_MOOD_DELTA)
            )
        
        # Validate scalar changes
        if update.energy_delta is not None:
            validated.energy_delta = self._clamp(update.energy_delta, self.MAX_ENERGY_DELTA)
        
        if update.stress_delta is not None:
            validated.stress_delta = self._clamp(update.stress_delta, self.MAX_STRESS_DELTA)
        
        # Validate opinion changes
        for entity_id, deltas in update.opinion_updates.items():
            validated_deltas = {}
            for metric, delta in deltas.items():
                validated_deltas[metric] = self._clamp(delta, self.MAX_OPINION_DELTA)
            validated.opinion_updates[entity_id] = validated_deltas
        
        # Pass through other fields
        validated.new_reflection = update.new_reflection
        validated.response_tendency_update = update.response_tendency_update
        validated.conversation_style_update = update.conversation_style_update
        
        return validated
    
    def _apply_mood_with_momentum(self, mood_delta: MoodVector):
        """Apply mood changes considering momentum"""
        # Update momentum
        self._momentum["valence"] = 0.7 * self._momentum["valence"] + 0.3 * mood_delta.valence
        self._momentum["arousal"] = 0.7 * self._momentum["arousal"] + 0.3 * mood_delta.arousal
        self._momentum["dominance"] = 0.7 * self._momentum["dominance"] + 0.3 * mood_delta.dominance
        
        # Apply with momentum
        effective_delta = MoodVector(
            valence=mood_delta.valence + 0.2 * self._momentum["valence"],
            arousal=mood_delta.arousal + 0.2 * self._momentum["arousal"],
            dominance=mood_delta.dominance + 0.1 * self._momentum["dominance"],
            curiosity=mood_delta.curiosity,
            creativity=mood_delta.creativity,
            sociability=mood_delta.sociability
        )
        
        # Apply to current mood
        current = self._current_state.mood
        self._current_state.mood = MoodVector(
            valence=self._clamp_mood(current.valence + effective_delta.valence),
            arousal=self._clamp_mood(current.arousal + effective_delta.arousal),
            dominance=self._clamp_mood(current.dominance + effective_delta.dominance),
            curiosity=self._clamp_mood(current.curiosity + effective_delta.curiosity),
            creativity=self._clamp_mood(current.creativity + effective_delta.creativity),
            sociability=self._clamp_mood(current.sociability + effective_delta.sociability)
        )
    
    def _apply_opinion_changes(self, entity_id: str, deltas: Dict[str, float]):
        """Apply opinion changes for an entity"""
        if entity_id not in self._current_state.opinion_scores:
            # Create new opinion
            entity_type = EntityType.USER if entity_id in ["commander", "COMMANDER_PRIME"] else EntityType.MINION
            self._current_state.opinion_scores[entity_id] = OpinionScore(
                entity_id=entity_id,
                entity_type=entity_type,
                trust=50.0,
                respect=50.0,
                affection=50.0,
                interaction_count=0,
                last_interaction=None,
                notable_events=[]
            )
        
        opinion = self._current_state.opinion_scores[entity_id]
        
        # Apply changes
        for metric, delta in deltas.items():
            current = getattr(opinion, metric)
            # Special rule: Commander opinion can't go below 50
            if entity_id in ["commander", "COMMANDER_PRIME"] and metric in ["trust", "respect", "affection"]:
                new_value = max(50.0, min(100.0, current + delta))
            else:
                new_value = max(-100.0, min(100.0, current + delta))
            setattr(opinion, metric, new_value)
        
        # Update interaction tracking
        opinion.interaction_count += 1
        opinion.last_interaction = datetime.now()
    
    async def _emit_state_change(self, reason: str):
        """Emit emotional state change event"""
        if not self._current_state:
            return
        
        await self.event_bus.emit(
            EventType.MINION_EMOTIONAL_CHANGE,
            data={
                "minion_id": self.minion_id,
                "reason": reason,
                "emotional_state": {
                    "mood": {
                        "valence": self._current_state.mood.valence,
                        "arousal": self._current_state.mood.arousal,
                        "dominance": self._current_state.mood.dominance
                    },
                    "energy_level": self._current_state.energy_level,
                    "stress_level": self._current_state.stress_level,
                    "commander_opinion": self._current_state.get_opinion_of("commander").overall_sentiment if "commander" in self._current_state.opinion_scores else 50.0
                }
            },
            source=f"emotional_engine:{self.minion_id}"
        )
    
    async def _self_regulation_loop(self):
        """Periodic emotional self-regulation"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                if not self._current_state:
                    continue
                
                needs_regulation = False
                update = EmotionalStateUpdate()
                
                # High stress regulation
                if self._current_state.stress_level > 0.85:
                    needs_regulation = True
                    update.stress_delta = -0.1
                    update.mood_delta = MoodVector(
                        valence=0.05, arousal=-0.1, dominance=0.0,
                        curiosity=0.0, creativity=0.0, sociability=0.0
                    )
                    update.new_reflection = ReflectionEntry(
                        timestamp=datetime.now(),
                        topic="Stress Regulation",
                        insight="Taking a moment to manage stress levels",
                        confidence=0.9
                    )
                
                # Low energy recovery
                elif self._current_state.energy_level < 0.15:
                    needs_regulation = True
                    update.energy_delta = 0.1
                    update.stress_delta = -0.05
                
                # Extreme mood regulation
                elif abs(self._current_state.mood.valence) > 0.85:
                    needs_regulation = True
                    # Move toward neutral
                    update.mood_delta = MoodVector(
                        valence=-0.2 * self._current_state.mood.valence,
                        arousal=-0.1 * self._current_state.mood.arousal,
                        dominance=0.0,
                        curiosity=0.0,
                        creativity=0.0,
                        sociability=0.0
                    )
                
                if needs_regulation:
                    await self._apply_emotional_update(update, "self_regulation")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in self-regulation loop: {e}")
    
    def _add_to_history(self, state: EmotionalState):
        """Add state to history"""
        self._state_history.append((datetime.now(), state))
        if len(self._state_history) > self._max_history:
            self._state_history.pop(0)
    
    def _prune_reflections(self):
        """Keep only recent reflections"""
        max_reflections = 20
        if len(self._current_state.self_reflection_notes) > max_reflections:
            self._current_state.self_reflection_notes = \
                self._current_state.self_reflection_notes[-max_reflections:]
    
    def _clamp(self, value: float, max_abs: float) -> float:
        """Clamp value to [-max_abs, max_abs]"""
        return max(-max_abs, min(max_abs, value))
    
    def _clamp_mood(self, value: float) -> float:
        """Clamp mood values to [-1, 1]"""
        return max(-1.0, min(1.0, value))
    
    def get_current_state(self) -> Optional[EmotionalState]:
        """Get current emotional state"""
        return self._current_state
    
    def get_emotional_trajectory(self, hours: int = 24) -> Dict[str, List[float]]:
        """Get emotional trajectory over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        trajectories = {
            "valence": [],
            "arousal": [],
            "energy": [],
            "stress": [],
            "timestamps": []
        }
        
        for timestamp, state in self._state_history:
            if timestamp >= cutoff:
                trajectories["valence"].append(state.mood.valence)
                trajectories["arousal"].append(state.mood.arousal)
                trajectories["energy"].append(state.energy_level)
                trajectories["stress"].append(state.stress_level)
                trajectories["timestamps"].append(timestamp.isoformat())
        
        return trajectories
