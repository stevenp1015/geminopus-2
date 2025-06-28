# In gemini_legion_backend/core/domain/memory.py
from dataclasses import dataclass, field
from typing import List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class MemoryInteraction:
    role: str  # e.g., "user", "model", or specific minion name
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class WorkingMemory:
    interactions: List[MemoryInteraction] = field(default_factory=list)
    capacity: int = 10  # Max number of interactions to store

    def add_interaction(self, role: str, content: str):
        self.interactions.append(MemoryInteraction(role=role, content=content))
        # Keep only the most recent 'capacity' interactions
        if len(self.interactions) > self.capacity:
            self.interactions = self.interactions[-self.capacity:]
        logger.debug(f"Added to working memory. Role: {role}, Content: '{content[:30]}...'. Count: {len(self.interactions)}")


    def get_recent_context_for_prompt(self, max_tokens: int = 500) -> str:
        """Formats recent interactions as a string for LLM prompts."""
        if not self.interactions:
            return "No recent conversation history available."

        context_str = "Recent conversation history (oldest to newest relevant messages):\n"
        formatted_interactions: List[str] = []
        current_token_count = 0 # Rough token count

        # Iterate from oldest to newest to build context chronologically for the prompt
        for interaction in self.interactions:
            line = f"{interaction.role}: {interaction.content}"
            # Rough token estimation (words + role label)
            # A common heuristic is that 1 token ~ 0.75 words, or 1 word ~ 1.33 tokens.
            # For simplicity, let's use a factor like 1.5 for words to tokens, plus some for role/formatting.
            line_tokens = len(interaction.content.split()) * 1.5 + len(interaction.role.split()) + 5 # 5 for ": \n" etc.

            if current_token_count + line_tokens > max_tokens:
                if not formatted_interactions: # If even the first message is too long, take a snippet
                     # Estimate max content characters based on remaining tokens
                    remaining_chars_estimate = int((max_tokens - (len(interaction.role) + 5)) / 1.5)
                    formatted_interactions.append(f"{interaction.role}: {interaction.content[:max(0, remaining_chars_estimate)]}...")
                break

            formatted_interactions.append(line)
            current_token_count += line_tokens

        if not formatted_interactions:
             return "No recent conversation history fits within token limit."

        return context_str + "\n".join(formatted_interactions)

    def clear(self):
        self.interactions.clear()
        logger.info("Working memory cleared.")

@dataclass
class MemorySystemV2:
    minion_id: str
    working_memory: WorkingMemory = field(default_factory=WorkingMemory)
    # episodic_memory: Optional[Any] = None # Placeholder for future
    # semantic_memory: Optional[Any] = None # Placeholder for future

    def __post_init__(self):
        logger.info(f"MemorySystemV2 initialized for {self.minion_id}")

    def record_interaction(self, role: str, content: str):
        self.working_memory.add_interaction(role, content)
        # Logging is handled by WorkingMemory.add_interaction

    def get_prompt_context(self) -> str:
        context = self.working_memory.get_recent_context_for_prompt()
        logger.debug(f"MemorySystem for {self.minion_id} providing context (first 100 chars): '{context[:100]}...'")
        return context