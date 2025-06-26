"""
Opinion Domain Models for Gemini Legion

This module contains the OpinionScore and related models that represent
how Minions perceive and relate to other entities in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

from .enums import EntityType


class OpinionImpact(str, Enum):
    """Impact level of an opinion event."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class OpinionEvent:
    """
    Represents a significant event that shaped a Minion's opinion of an entity.
    """
    timestamp: datetime
    description: str
    impact: OpinionImpact
    
    # Changes to opinion metrics caused by this event
    trust_change: float = 0.0
    respect_change: float = 0.0
    affection_change: float = 0.0
    
    # Optional context
    context: Optional[str] = None
    
    def total_impact(self) -> float:
        """Calculate the total magnitude of opinion change."""
        return abs(self.trust_change) + abs(self.respect_change) + abs(self.affection_change)


@dataclass
class OpinionScore:
    """
    Structured representation of a Minion's opinion about another entity.
    
    This tracks not just current sentiment but also the history and
    evolution of the relationship.
    """
    entity_id: str
    entity_type: EntityType
    
    # Core opinion metrics (-100 to 100)
    trust: float = 0.0        # How much the minion trusts this entity
    respect: float = 0.0      # How much the minion respects this entity
    affection: float = 0.0    # How much the minion likes this entity
    
    # Interaction history
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    first_interaction: Optional[datetime] = None
    
    # Notable events that shaped this opinion
    notable_events: List[OpinionEvent] = field(default_factory=list)
    
    # Behavioral modifiers
    interaction_frequency: float = 0.5  # How often they prefer to interact (0.0-1.0)
    communication_style: str = "neutral"  # How they communicate with this entity
    
    def __post_init__(self):
        """Validate and clamp values to valid ranges."""
        self.trust = max(-100.0, min(100.0, self.trust))
        self.respect = max(-100.0, min(100.0, self.respect))
        self.affection = max(-100.0, min(100.0, self.affection))
        self.interaction_frequency = max(0.0, min(1.0, self.interaction_frequency))
    
    @property
    def overall_sentiment(self) -> float:
        """
        Calculate overall sentiment towards the entity.
        
        Returns:
            Average of trust, respect, and affection (-100 to 100)
        """
        return (self.trust + self.respect + self.affection) / 3.0
    
    @property
    def relationship_strength(self) -> float:
        """
        Calculate the strength/intensity of the relationship.
        
        Returns:
            A value between 0.0 and 100.0 representing relationship strength
        """
        # Consider both sentiment magnitude and interaction history
        sentiment_strength = (abs(self.trust) + abs(self.respect) + abs(self.affection)) / 3.0
        
        # Interaction frequency bonus (max 20 points)
        if self.interaction_count > 0:
            interaction_bonus = min(20.0, self.interaction_count / 5.0)
        else:
            interaction_bonus = 0.0
        
        return min(100.0, sentiment_strength + interaction_bonus)
    
    def get_relationship_type(self) -> str:
        """
        Categorize the relationship based on opinion scores.
        
        Returns:
            A string describing the relationship type
        """
        sentiment = self.overall_sentiment
        
        # Strong positive relationships
        if sentiment > 66:
            if self.trust > 80 and self.affection > 80:
                return "close_friend"
            elif self.respect > 80:
                return "mentor" if self.entity_type == EntityType.USER else "role_model"
            else:
                return "friend"
        
        # Moderate positive relationships
        elif sentiment > 33:
            if self.respect > self.affection:
                return "respected_colleague"
            else:
                return "friendly_acquaintance"
        
        # Neutral relationships
        elif sentiment > -33:
            if self.interaction_count == 0:
                return "stranger"
            else:
                return "neutral_acquaintance"
        
        # Negative relationships
        elif sentiment > -66:
            if self.trust < -60:
                return "distrusted"
            else:
                return "disliked"
        
        # Strong negative relationships
        else:
            if self.respect < -80:
                return "despised"
            else:
                return "enemy"
    
    def apply_event(self, event: OpinionEvent) -> None:
        """
        Apply an opinion event, updating scores and history.
        
        Args:
            event: The opinion event to apply
        """
        # Update scores
        self.trust = max(-100.0, min(100.0, self.trust + event.trust_change))
        self.respect = max(-100.0, min(100.0, self.respect + event.respect_change))
        self.affection = max(-100.0, min(100.0, self.affection + event.affection_change))
        
        # Update interaction tracking
        self.interaction_count += 1
        self.last_interaction = event.timestamp
        
        if self.first_interaction is None:
            self.first_interaction = event.timestamp
        
        # Add to notable events if significant
        if event.impact in [OpinionImpact.MAJOR, OpinionImpact.CRITICAL] or event.total_impact() > 15:
            self.notable_events.append(event)
            
            # Keep only the most recent 20 notable events
            if len(self.notable_events) > 20:
                self.notable_events = sorted(
                    self.notable_events, 
                    key=lambda e: e.timestamp, 
                    reverse=True
                )[:20]
    
    def to_prompt_context(self) -> str:
        """
        Convert opinion to context that can be injected into prompts.
        
        Returns:
            A string describing the relationship for LLM context
        """
        relationship = self.get_relationship_type()
        sentiment = self.overall_sentiment
        
        # Base description
        if relationship == "close_friend":
            base = f"You consider them a close friend and trusted ally"
        elif relationship == "friend":
            base = f"You consider them a good friend"
        elif relationship == "mentor":
            base = f"You deeply respect them as a mentor figure"
        elif relationship == "respected_colleague":
            base = f"You respect them as a capable colleague"
        elif relationship == "friendly_acquaintance":
            base = f"You have a friendly but casual relationship"
        elif relationship == "stranger":
            base = f"You don't know them yet"
        elif relationship == "neutral_acquaintance":
            base = f"You have a neutral, professional relationship"
        elif relationship == "distrusted":
            base = f"You don't fully trust them"
        elif relationship == "disliked":
            base = f"You don't particularly enjoy their company"
        elif relationship == "despised":
            base = f"You have very negative feelings toward them"
        elif relationship == "enemy":
            base = f"You consider them an adversary"
        else:
            base = f"You have mixed feelings"
        
        # Add specific details
        details = []
        
        if abs(self.trust - self.respect) > 30:
            if self.trust > self.respect:
                details.append("though you trust them more than you respect them")
            else:
                details.append("though you respect them more than you trust them")
        
        if self.affection > 70:
            details.append("and feel genuine warmth toward them")
        elif self.affection < -70:
            details.append("and feel cold toward them")
        
        if self.interaction_count > 50:
            details.append("after many interactions")
        elif self.interaction_count < 5:
            details.append("based on limited interaction")
        
        # Combine
        if details:
            return f"{base} {', '.join(details)}."
        else:
            return f"{base}."
    
    def suggest_interaction_approach(self) -> str:
        """
        Suggest how the Minion should approach interactions with this entity.
        
        Returns:
            A string describing the suggested interaction style
        """
        relationship = self.get_relationship_type()
        
        style_map = {
            "close_friend": "Be warm, open, and supportive. Share thoughts freely.",
            "friend": "Be friendly and engaging. Show interest in their wellbeing.",
            "mentor": "Be respectful and eager to learn. Ask thoughtful questions.",
            "role_model": "Show admiration and respect. Seek their perspective.",
            "respected_colleague": "Be professional but warm. Value their input.",
            "friendly_acquaintance": "Be pleasant and polite. Keep things light.",
            "stranger": "Be polite and welcoming. Introduce yourself properly.",
            "neutral_acquaintance": "Be professional and courteous. Stick to relevant topics.",
            "distrusted": "Be cautious but fair. Verify information when needed.",
            "disliked": "Be civil but brief. Focus on necessary interactions.",
            "despised": "Be minimal and strictly professional. Avoid unnecessary contact.",
            "enemy": "Be extremely cautious. Document all interactions."
        }
        
        return style_map.get(relationship, "Be professional and appropriate.")
