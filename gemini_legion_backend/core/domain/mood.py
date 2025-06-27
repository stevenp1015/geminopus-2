"""
Mood Domain Models for Gemini Legion

This module contains the MoodVector and related models that represent
the multi-dimensional emotional state of Minions.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import math

from .enums import MoodDimension


@dataclass
class MoodVector:
    """
    Multi-dimensional representation of a Minion's mood.
    
    Based on the PAD (Pleasure-Arousal-Dominance) emotional model with
    additional dimensions for personality expression.
    """
    # Primary dimensions (PAD model)
    valence: float = 0.0      # Positive-Negative (-1.0 to 1.0)
    arousal: float = 0.5      # Calm-Excited (0.0 to 1.0)
    dominance: float = 0.5    # Submissive-Dominant (0.0 to 1.0)
    
    # Secondary dimensions for personality nuance
    curiosity: float = 0.5    # Inquisitiveness level (0.0 to 1.0)
    creativity: float = 0.5   # Creative expression tendency (0.0 to 1.0)
    sociability: float = 0.5  # Desire for social interaction (0.0 to 1.0)
    
    def __post_init__(self):
        """Validate and clamp values to valid ranges."""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(0.0, min(1.0, self.dominance))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.creativity = max(0.0, min(1.0, self.creativity))
        self.sociability = max(0.0, min(1.0, self.sociability))
    
    def to_prompt_modifier(self) -> str:
        """
        Convert the mood vector to natural language that can be injected
        into LLM prompts to influence response generation.
        
        Returns:
            A string describing the current mood state in natural language
        """
        # Determine primary mood description
        mood_parts = []
        
        # Valence descriptions
        if self.valence > 0.7:
            mood_parts.append("very positive and upbeat")
        elif self.valence > 0.3:
            mood_parts.append("generally positive")
        elif self.valence > -0.3:
            mood_parts.append("neutral")
        elif self.valence > -0.7:
            mood_parts.append("somewhat negative")
        else:
            mood_parts.append("quite negative and down")
        
        # Arousal descriptions
        if self.arousal > 0.8:
            mood_parts.append("highly energetic and excited")
        elif self.arousal > 0.6:
            mood_parts.append("energetic")
        elif self.arousal > 0.4:
            mood_parts.append("moderately active")
        elif self.arousal > 0.2:
            mood_parts.append("calm")
        else:
            mood_parts.append("very calm and subdued")
        
        # Dominance descriptions
        if self.dominance > 0.8:
            mood_parts.append("feeling very confident and in control")
        elif self.dominance > 0.6:
            mood_parts.append("feeling confident")
        elif self.dominance > 0.4:
            mood_parts.append("feeling balanced")
        elif self.dominance > 0.2:
            mood_parts.append("feeling somewhat submissive")
        else:
            mood_parts.append("feeling very submissive and yielding")
        
        # Secondary dimension modifiers
        secondary_parts = []
        
        if self.curiosity > 0.7:
            secondary_parts.append("very curious and inquisitive")
        elif self.curiosity < 0.3:
            secondary_parts.append("not particularly curious")
        
        if self.creativity > 0.7:
            secondary_parts.append("feeling highly creative")
        elif self.creativity < 0.3:
            secondary_parts.append("in a practical mindset")
        
        if self.sociability > 0.7:
            secondary_parts.append("very social and talkative")
        elif self.sociability < 0.3:
            secondary_parts.append("preferring solitude")
        
        # Combine all parts
        base_mood = f"You are feeling {', '.join(mood_parts)}."
        
        if secondary_parts:
            return f"{base_mood} Additionally, you are {', '.join(secondary_parts)}."
        else:
            return base_mood
    
    def get_intensity(self) -> float:
        """
        Calculate the overall intensity of the mood.
        
        Returns:
            A value between 0.0 and 1.0 representing mood intensity
        """
        # Use Euclidean distance from neutral point
        valence_intensity = abs(self.valence)
        arousal_intensity = abs(self.arousal - 0.5) * 2
        dominance_intensity = abs(self.dominance - 0.5) * 2
        
        # Weight primary dimensions more heavily
        intensity = (valence_intensity * 0.4 + 
                    arousal_intensity * 0.3 + 
                    dominance_intensity * 0.3)
        
        return min(1.0, intensity)
    
    def blend_with(self, other: 'MoodVector', weight: float = 0.5) -> 'MoodVector':
        """
        Blend this mood vector with another, useful for gradual transitions.
        
        Args:
            other: The other mood vector to blend with
            weight: Weight for the other vector (0.0-1.0)
        
        Returns:
            A new MoodVector that is a blend of both
        """
        weight = max(0.0, min(1.0, weight))
        self_weight = 1.0 - weight
        
        return MoodVector(
            valence=self.valence * self_weight + other.valence * weight,
            arousal=self.arousal * self_weight + other.arousal * weight,
            dominance=self.dominance * self_weight + other.dominance * weight,
            curiosity=self.curiosity * self_weight + other.curiosity * weight,
            creativity=self.creativity * self_weight + other.creativity * weight,
            sociability=self.sociability * self_weight + other.sociability * weight
        )
    
    def distance_from(self, other: 'MoodVector') -> float:
        """
        Calculate the Euclidean distance between two mood vectors.
        
        Args:
            other: The other mood vector
        
        Returns:
            Distance between the two mood vectors
        """
        return math.sqrt(
            (self.valence - other.valence) ** 2 +
            (self.arousal - other.arousal) ** 2 +
            (self.dominance - other.dominance) ** 2 +
            (self.curiosity - other.curiosity) ** 2 +
            (self.creativity - other.creativity) ** 2 +
            (self.sociability - other.sociability) ** 2
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "curiosity": self.curiosity,
            "creativity": self.creativity,
            "sociability": self.sociability
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'MoodVector':
        """Create MoodVector from dictionary."""
        return cls(**data)
    
    @classmethod
    def neutral(cls) -> 'MoodVector':
        """Create a neutral mood vector."""
        return cls(valence=0.0, arousal=0.5, dominance=0.5)
    
    @classmethod
    def from_personality(cls, personality: str) -> 'MoodVector':
        """
        Create a default mood vector based on personality type.
        
        Args:
            personality: The base personality type
        
        Returns:
            A MoodVector with defaults for that personality
        """
        personality_moods = {
            "Analytical": cls(valence=0.1, arousal=0.4, dominance=0.6, 
                            curiosity=0.8, creativity=0.3, sociability=0.3),
            "Creative": cls(valence=0.3, arousal=0.7, dominance=0.5,
                          curiosity=0.7, creativity=0.9, sociability=0.6),
            "Chaotic": cls(valence=0.2, arousal=0.9, dominance=0.7,
                         curiosity=0.6, creativity=0.8, sociability=0.7),
            "Friendly": cls(valence=0.6, arousal=0.6, dominance=0.4,
                          curiosity=0.5, creativity=0.5, sociability=0.9),
            "Professional": cls(valence=0.1, arousal=0.4, dominance=0.7,
                              curiosity=0.4, creativity=0.3, sociability=0.4),
            "Witty": cls(valence=0.4, arousal=0.6, dominance=0.6,
                       curiosity=0.6, creativity=0.7, sociability=0.7),
            "Enthusiastic": cls(valence=0.7, arousal=0.8, dominance=0.5,
                              curiosity=0.7, creativity=0.6, sociability=0.8),
            "Wise": cls(valence=0.2, arousal=0.3, dominance=0.7,
                      curiosity=0.6, creativity=0.5, sociability=0.5),
            "Mischievous": cls(valence=0.5, arousal=0.7, dominance=0.6,
                             curiosity=0.8, creativity=0.8, sociability=0.6)
        }
        
        return personality_moods.get(personality, cls.neutral())
