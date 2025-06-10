"""
Memory System V2 - Event-Driven Multi-Layer Memory Architecture

This implements the sophisticated memory system from the original design doc
with proper event-driven patterns. No more isolated memory - everything flows
through the glorious event bus.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import asyncio
import logging
import json
import numpy as np
from enum import Enum
import uuid

from ...domain import (
    Experience,
    Memory,
    MemoryType,
    Knowledge,
    Skill,
    Pattern,
    ConceptEmbedding
)
from ...infrastructure.adk.events import get_event_bus, EventType

logger = logging.getLogger(__name__)


@dataclass
class WorkingMemoryItem:
    """Item in working memory with decay"""
    content: Any
    timestamp: datetime
    relevance: float = 1.0
    access_count: int = 0


@dataclass
class EpisodicMemory:
    """Episodic memory with rich context"""
    memory_id: str
    minion_id: str
    experience: Experience
    embedding: Optional[List[float]] = None
    significance: float = 0.5
    emotional_context: Optional[Dict[str, float]] = None
    participants: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    decay_rate: float = 0.1


@dataclass
class SemanticKnowledge:
    """Semantic knowledge representation"""
    knowledge_id: str
    concept: str
    facts: List[str]
    relationships: Dict[str, List[str]]
    confidence: float = 0.7
    source_memories: List[str] = field(default_factory=list)
    last_accessed: datetime = field(default_factory=datetime.now)


class MemoryImportance(Enum):
    """Memory importance levels"""
    TRIVIAL = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    CRITICAL = 0.9


class MemorySystemV2:
    """
    Event-driven multi-layered memory system for minions.
    
    Implements Miller's Law for working memory, episodic memory with embeddings,
    semantic knowledge extraction, and procedural skill learning - all through events.
    """
    
    def __init__(self, minion_id: str):
        """
        Initialize the memory system.
        
        Args:
            minion_id: ID of the minion this system serves
        """
        self.minion_id = minion_id
        self.event_bus = get_event_bus()
        
        # Layer 1: Working Memory (Miller's Law - 7±2 items)
        self.working_memory: deque[WorkingMemoryItem] = deque(maxlen=7)
        self._working_memory_lock = asyncio.Lock()
        
        # Layer 2: Short-term Memory
        self.short_term_memory: deque[Experience] = deque(maxlen=100)
        self.short_term_ttl = timedelta(minutes=30)
        
        # Layer 3: Episodic Memory (specific experiences)
        self.episodic_memory: Dict[str, EpisodicMemory] = {}
        self.episodic_embeddings: Dict[str, List[float]] = {}  # For vector search
        self.episodic_threshold = 0.6  # Significance threshold
        
        # Layer 4: Semantic Memory (learned knowledge)
        self.semantic_memory: Dict[str, SemanticKnowledge] = {}
        self.concept_graph: Dict[str, Set[str]] = {}  # Concept relationships
        
        # Layer 5: Procedural Memory (learned skills/patterns)
        self.procedural_memory: Dict[str, Skill] = {}
        self.skill_patterns: Dict[str, Pattern] = {}
        
        # Memory consolidation
        self._consolidation_task: Optional[asyncio.Task] = None
        self._forgetting_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self._memory_stats = {
            "working_hits": 0,
            "working_misses": 0,
            "episodic_recalls": 0,
            "semantic_extractions": 0,
            "skills_learned": 0
        }
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()
        
        logger.info(f"MemorySystemV2 initialized for minion {minion_id}")
    
    def _setup_event_subscriptions(self):
        """Subscribe to events that create memories"""
        # Channel interactions create memories
        self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
        
        # Task events are significant experiences
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._handle_task_completed)
        self.event_bus.subscribe(EventType.TASK_FAILED, self._handle_task_failed)
        
        # Emotional events affect memory significance
        self.event_bus.subscribe(EventType.MINION_EMOTIONAL_CHANGE, self._handle_emotional_change)
        
        # System requests for memory operations
        self.event_bus.subscribe(EventType.SYSTEM_HEALTH, self._handle_memory_request)
    
    async def start(self):
        """Start the memory system"""
        # Start background tasks
        self._consolidation_task = asyncio.create_task(self._consolidation_loop())
        self._forgetting_task = asyncio.create_task(self._forgetting_curve_loop())
        
        # Emit startup event
        await self.event_bus.emit(
            EventType.MINION_STATE_CHANGED,
            data={
                "minion_id": self.minion_id,
                "state_type": "memory_system",
                "state": "started"
            },
            source=f"memory_system:{self.minion_id}"
        )
        
        logger.info(f"Memory system started for {self.minion_id}")
    
    async def stop(self):
        """Stop the memory system"""
        # Cancel background tasks
        if self._consolidation_task:
            self._consolidation_task.cancel()
        if self._forgetting_task:
            self._forgetting_task.cancel()
        
        # Save critical memories before shutdown
        await self._save_critical_memories()
        
        logger.info(f"Memory system stopped for {self.minion_id}")
    
    async def store_experience(self, experience: Experience):
        """
        Store an experience across appropriate memory layers.
        
        This is the main entry point for new memories.
        """
        # Layer 1: Working memory (immediate use)
        async with self._working_memory_lock:
            working_item = WorkingMemoryItem(
                content=experience,
                timestamp=datetime.now(),
                relevance=experience.significance
            )
            self.working_memory.append(working_item)
        
        # Layer 2: Short-term memory
        self.short_term_memory.append(experience)
        
        # Layer 3: Episodic memory (if significant)
        if experience.significance > self.episodic_threshold:
            await self._store_episodic_memory(experience)
        
        # Layer 4: Extract semantic knowledge
        knowledge = await self._extract_knowledge(experience)
        if knowledge:
            await self._integrate_semantic_knowledge(knowledge)
        
        # Layer 5: Learn procedural patterns
        if experience.involves_task_completion:
            await self._learn_from_experience(experience)
        
        # Update stats
        self._memory_stats["working_hits"] += 1
        
        # Emit memory stored event
        await self.event_bus.emit(
            EventType.MINION_STATE_CHANGED,
            data={
                "minion_id": self.minion_id,
                "state_type": "memory",
                "action": "stored",
                "memory_type": "experience",
                "significance": experience.significance
            },
            source=f"memory_system:{self.minion_id}"
        )
    
    async def recall_relevant(self, query: str, limit: int = 5) -> List[Memory]:
        """
        Recall memories relevant to a query.
        
        Searches across all memory layers with appropriate algorithms.
        """
        relevant_memories = []
        
        # Check working memory first (fastest)
        async with self._working_memory_lock:
            for item in self.working_memory:
                if self._is_relevant(item.content, query):
                    relevant_memories.append(Memory(
                        memory_id=f"working_{id(item)}",
                        content=item.content,
                        memory_type=MemoryType.WORKING,
                        relevance=item.relevance,
                        timestamp=item.timestamp
                    ))
                    item.access_count += 1
        
        # Search short-term memory
        for exp in self.short_term_memory:
            if self._is_relevant(exp, query) and len(relevant_memories) < limit:
                relevant_memories.append(Memory(
                    memory_id=f"short_{id(exp)}",
                    content=exp,
                    memory_type=MemoryType.SHORT_TERM,
                    relevance=0.7,
                    timestamp=exp.timestamp
                ))
        
        # Vector search in episodic memory
        if len(relevant_memories) < limit:
            episodic_results = await self._search_episodic_memory(query, limit - len(relevant_memories))
            relevant_memories.extend(episodic_results)
        
        # Semantic memory search
        if len(relevant_memories) < limit:
            semantic_results = await self._search_semantic_memory(query, limit - len(relevant_memories))
            relevant_memories.extend(semantic_results)
        
        # Update stats
        self._memory_stats["episodic_recalls"] += len([m for m in relevant_memories if m.memory_type == MemoryType.EPISODIC])
        
        # Sort by relevance
        relevant_memories.sort(key=lambda m: m.relevance, reverse=True)
        
        return relevant_memories[:limit]
    
    async def _handle_channel_message(self, event):
        """Create memories from channel messages"""
        if event.data.get("sender_id") == self.minion_id:
            # Store our own messages as experiences
            content = event.data.get("content", "")
            channel = event.data.get("channel_id", "")
            
            experience = Experience(
                experience_id=str(uuid.uuid4()),
                minion_id=self.minion_id,
                experience_type="message_sent",
                content=f"Sent to #{channel}: {content}",
                timestamp=datetime.now(),
                significance=0.3,
                emotional_impact={"confidence": 0.1},
                participants=[self.minion_id],
                metadata={"channel": channel}
            )
            
            await self.store_experience(experience)
        
        elif event.data.get("channel_id") in ["general", "task_coordination"]:  # Channels we care about
            # Store others' messages
            sender = event.data.get("sender_id", "unknown")
            content = event.data.get("content", "")
            channel = event.data.get("channel_id", "")
            
            # Higher significance if we're mentioned
            significance = 0.7 if f"@{self.minion_id}" in content else 0.4
            
            experience = Experience(
                experience_id=str(uuid.uuid4()),
                minion_id=self.minion_id,
                experience_type="message_received",
                content=f"{sender} in #{channel}: {content}",
                timestamp=datetime.now(),
                significance=significance,
                emotional_impact={"interest": 0.2},
                participants=[sender, self.minion_id],
                metadata={"channel": channel, "sender": sender}
            )
            
            await self.store_experience(experience)
    
    async def _handle_task_completed(self, event):
        """Store task completion as significant memory"""
        if event.data.get("assigned_to") != self.minion_id:
            return
        
        task_id = event.data.get("task_id", "unknown")
        task_description = event.data.get("description", "task")
        
        experience = Experience(
            experience_id=str(uuid.uuid4()),
            minion_id=self.minion_id,
            experience_type="task_completed",
            content=f"Successfully completed task: {task_description}",
            timestamp=datetime.now(),
            significance=0.8,
            emotional_impact={"pride": 0.7, "satisfaction": 0.8},
            participants=[self.minion_id, "commander"],
            involves_task_completion=True,
            metadata={"task_id": task_id, "success": True}
        )
        
        await self.store_experience(experience)
    
    async def _handle_task_failed(self, event):
        """Store task failure as learning experience"""
        if event.data.get("assigned_to") != self.minion_id:
            return
        
        task_id = event.data.get("task_id", "unknown")
        task_description = event.data.get("description", "task")
        failure_reason = event.data.get("failure_reason", "unknown")
        
        experience = Experience(
            experience_id=str(uuid.uuid4()),
            minion_id=self.minion_id,
            experience_type="task_failed",
            content=f"Failed task: {task_description}. Reason: {failure_reason}",
            timestamp=datetime.now(),
            significance=0.9,  # Failures are highly significant for learning
            emotional_impact={"disappointment": 0.6, "determination": 0.4},
            participants=[self.minion_id, "commander"],
            involves_task_completion=False,
            metadata={"task_id": task_id, "success": False, "failure_reason": failure_reason}
        )
        
        await self.store_experience(experience)
    
    async def _handle_emotional_change(self, event):
        """Adjust memory significance based on emotional state"""
        if event.data.get("minion_id") != self.minion_id:
            return
        
        # Recent memories during high emotional states become more significant
        emotional_state = event.data.get("emotional_state", {})
        stress = emotional_state.get("stress_level", 0.5)
        arousal = emotional_state.get("mood", {}).get("arousal", 0.5)
        
        if stress > 0.7 or abs(arousal) > 0.7:
            # Boost recent memory significance
            async with self._working_memory_lock:
                for item in self.working_memory:
                    item.relevance *= 1.2
    
    async def _handle_memory_request(self, event):
        """Handle system requests for memory operations"""
        if event.data.get("request_type") == "memory_stats" and \
           event.data.get("minion_id") == self.minion_id:
            # Return memory statistics
            await self.event_bus.emit(
                EventType.MINION_STATE_CHANGED,
                data={
                    "minion_id": self.minion_id,
                    "state_type": "memory_stats",
                    "stats": {
                        **self._memory_stats,
                        "working_memory_size": len(self.working_memory),
                        "short_term_size": len(self.short_term_memory),
                        "episodic_size": len(self.episodic_memory),
                        "semantic_concepts": len(self.semantic_memory),
                        "learned_skills": len(self.procedural_memory)
                    }
                },
                source=f"memory_system:{self.minion_id}"
            )
    
    async def _store_episodic_memory(self, experience: Experience):
        """Store experience as episodic memory with embeddings"""
        memory_id = f"episodic_{self.minion_id}_{uuid.uuid4()}"
        
        # Create embedding (simplified - in reality would use sentence transformer)
        embedding = await self._create_embedding(experience.content)
        
        episodic = EpisodicMemory(
            memory_id=memory_id,
            minion_id=self.minion_id,
            experience=experience,
            embedding=embedding,
            significance=experience.significance,
            emotional_context=experience.emotional_impact,
            participants=experience.participants,
            timestamp=experience.timestamp
        )
        
        self.episodic_memory[memory_id] = episodic
        self.episodic_embeddings[memory_id] = embedding
        
        logger.debug(f"Stored episodic memory: {memory_id}")
    
    async def _extract_knowledge(self, experience: Experience) -> Optional[Knowledge]:
        """Extract semantic knowledge from experience"""
        # Simplified knowledge extraction
        content_lower = experience.content.lower()
        
        # Look for factual patterns
        if any(word in content_lower for word in ["completed", "learned", "discovered", "found"]):
            facts = [experience.content]
            
            # Extract concepts (simplified)
            concepts = []
            if "task" in content_lower:
                concepts.append("task_completion")
            if "fail" in content_lower:
                concepts.append("failure_recovery")
            
            if concepts:
                knowledge = Knowledge(
                    knowledge_id=str(uuid.uuid4()),
                    concepts=concepts,
                    facts=facts,
                    source_experience=experience.experience_id,
                    confidence=0.7
                )
                
                self._memory_stats["semantic_extractions"] += 1
                return knowledge
        
        return None
    
    async def _integrate_semantic_knowledge(self, knowledge: Knowledge):
        """Integrate new knowledge into semantic memory"""
        for concept in knowledge.concepts:
            if concept not in self.semantic_memory:
                self.semantic_memory[concept] = SemanticKnowledge(
                    knowledge_id=str(uuid.uuid4()),
                    concept=concept,
                    facts=[],
                    relationships={},
                    confidence=knowledge.confidence,
                    source_memories=[knowledge.source_experience]
                )
            
            # Add new facts
            semantic = self.semantic_memory[concept]
            semantic.facts.extend(knowledge.facts)
            semantic.facts = list(set(semantic.facts))  # Deduplicate
            semantic.last_accessed = datetime.now()
            
            # Update concept graph
            if concept not in self.concept_graph:
                self.concept_graph[concept] = set()
            
            # Link related concepts
            for other_concept in knowledge.concepts:
                if other_concept != concept:
                    self.concept_graph[concept].add(other_concept)
    
    async def _learn_from_experience(self, experience: Experience):
        """Learn procedural patterns from task experiences"""
        task_type = experience.metadata.get("task_type", "general")
        success = experience.metadata.get("success", False)
        
        skill_id = f"skill_{task_type}"
        
        if skill_id not in self.procedural_memory:
            self.procedural_memory[skill_id] = Skill(
                skill_id=skill_id,
                skill_name=task_type,
                proficiency=0.5,
                successful_applications=0,
                failed_applications=0,
                learned_patterns=[]
            )
        
        skill = self.procedural_memory[skill_id]
        
        if success:
            skill.successful_applications += 1
            skill.proficiency = min(1.0, skill.proficiency + 0.1)
        else:
            skill.failed_applications += 1
            skill.proficiency = max(0.1, skill.proficiency - 0.05)
        
        self._memory_stats["skills_learned"] += 1
    
    async def _search_episodic_memory(self, query: str, limit: int) -> List[Memory]:
        """Vector search in episodic memory"""
        if not self.episodic_memory:
            return []
        
        # Create query embedding
        query_embedding = await self._create_embedding(query)
        
        # Calculate similarities
        similarities = []
        for memory_id, embedding in self.episodic_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((memory_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to Memory objects
        results = []
        for memory_id, similarity in similarities[:limit]:
            episodic = self.episodic_memory[memory_id]
            results.append(Memory(
                memory_id=memory_id,
                content=episodic.experience,
                memory_type=MemoryType.EPISODIC,
                relevance=similarity,
                timestamp=episodic.timestamp
            ))
        
        return results
    
    async def _search_semantic_memory(self, query: str, limit: int) -> List[Memory]:
        """Search semantic memory for relevant knowledge"""
        results = []
        query_lower = query.lower()
        
        for concept, knowledge in self.semantic_memory.items():
            # Simple keyword matching (could be enhanced)
            if concept in query_lower or any(word in query_lower for word in concept.split("_")):
                results.append(Memory(
                    memory_id=knowledge.knowledge_id,
                    content={"concept": concept, "facts": knowledge.facts[:3]},
                    memory_type=MemoryType.SEMANTIC,
                    relevance=knowledge.confidence,
                    timestamp=knowledge.last_accessed
                ))
        
        return results[:limit]
    
    async def _consolidation_loop(self):
        """Periodic memory consolidation"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Move important short-term memories to episodic
                important_memories = [
                    exp for exp in self.short_term_memory
                    if exp.significance > 0.7 and exp.experience_id not in self.episodic_memory
                ]
                
                for exp in important_memories:
                    await self._store_episodic_memory(exp)
                
                # Compress episodic memories into semantic knowledge
                await self._compress_episodic_to_semantic()
                
                # Emit consolidation event
                await self.event_bus.emit(
                    EventType.MINION_STATE_CHANGED,
                    data={
                        "minion_id": self.minion_id,
                        "state_type": "memory",
                        "action": "consolidated",
                        "consolidated_count": len(important_memories)
                    },
                    source=f"memory_system:{self.minion_id}"
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consolidation loop: {e}")
    
    async def _forgetting_curve_loop(self):
        """Apply forgetting curve to memories"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Decay episodic memories
                memories_to_forget = []
                for memory_id, episodic in self.episodic_memory.items():
                    age_hours = (datetime.now() - episodic.timestamp).total_seconds() / 3600
                    decay = episodic.decay_rate * age_hours
                    
                    # Reduce significance
                    episodic.significance *= (1 - decay)
                    
                    # Forget if significance too low
                    if episodic.significance < 0.1:
                        memories_to_forget.append(memory_id)
                
                # Remove forgotten memories
                for memory_id in memories_to_forget:
                    del self.episodic_memory[memory_id]
                    del self.episodic_embeddings[memory_id]
                
                logger.debug(f"Forgot {len(memories_to_forget)} low-significance memories")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in forgetting loop: {e}")
    
    async def _compress_episodic_to_semantic(self):
        """Extract patterns from episodic memories"""
        # Group recent episodic memories by type
        recent_cutoff = datetime.now() - timedelta(days=1)
        recent_memories = [
            ep for ep in self.episodic_memory.values()
            if ep.timestamp > recent_cutoff
        ]
        
        # Look for patterns (simplified)
        task_memories = [m for m in recent_memories if "task" in m.experience.content.lower()]
        
        if len(task_memories) >= 3:
            # Extract task completion patterns
            success_rate = sum(1 for m in task_memories if m.experience.metadata.get("success", False)) / len(task_memories)
            
            knowledge = Knowledge(
                knowledge_id=str(uuid.uuid4()),
                concepts=["task_performance"],
                facts=[f"Recent task success rate: {success_rate:.1%}"],
                source_experience="multiple",
                confidence=min(0.9, len(task_memories) / 10)
            )
            
            await self._integrate_semantic_knowledge(knowledge)
    
    async def _save_critical_memories(self):
        """Save critical memories before shutdown"""
        critical_memories = [
            ep for ep in self.episodic_memory.values()
            if ep.significance > 0.8
        ]
        
        logger.info(f"Saving {len(critical_memories)} critical memories for {self.minion_id}")
        
        # In a real implementation, would persist to disk
    
    async def _create_embedding(self, text: str) -> List[float]:
        """Create text embedding (simplified - would use sentence transformer)"""
        # Simplified embedding - just random for now
        # In reality, would use a proper embedding model
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(768).tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def _is_relevant(self, content: Any, query: str) -> bool:
        """Simple relevance check (could be enhanced)"""
        if hasattr(content, 'content'):
            content_str = str(content.content)
        else:
            content_str = str(content)
        
        query_lower = query.lower()
        content_lower = content_str.lower()
        
        # Simple keyword matching
        query_words = query_lower.split()
        matches = sum(1 for word in query_words if word in content_lower)
        
        return matches >= len(query_words) * 0.3
