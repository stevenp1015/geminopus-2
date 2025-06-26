"""
Domain Enums for Gemini Legion

This module contains all the enumeration types used across the domain models.
These enums ensure type safety and consistency throughout the system.
"""

from enum import Enum, IntEnum


class MinionState(str, Enum):
    """
    Represents the current operational state of a Minion.
    """
    IDLE = "idle"                    # Minion is spawned but not actively engaged
    ACTIVE = "active"                # Minion is actively processing or in conversation
    THINKING = "thinking"            # Minion is processing a complex request
    COMMUNICATING = "communicating"  # Minion is sending/receiving messages
    WORKING = "working"              # Minion is executing a task
    REFLECTING = "reflecting"        # Minion is in self-reflection mode
    SLEEPING = "sleeping"            # Minion is in low-power/dormant state
    ERROR = "error"                  # Minion encountered an error state
    TERMINATED = "terminated"        # Minion has been despawned


class EntityType(str, Enum):
    """
    Types of entities that can exist in the Legion system.
    Used primarily for opinion scoring and relationship tracking.
    """
    USER = "user"          # Human users (like Steven)
    MINION = "minion"      # Other AI minions
    SYSTEM = "system"      # System components (event bus, services)
    CONCEPT = "concept"    # Abstract concepts minions can have opinions about
    TASK = "task"          # Tasks that minions work on
    TOOL = "tool"          # Tools that minions can use
    CHANNEL = "channel"    # Communication channels


class MoodDimension(str, Enum):
    """
    Different dimensions that comprise a Minion's mood.
    Based on psychological models of emotion.
    """
    # Primary dimensions (PAD model - Pleasure, Arousal, Dominance)
    VALENCE = "valence"       # Positive-Negative axis (-1.0 to 1.0)
    AROUSAL = "arousal"       # Calm-Excited axis (0.0 to 1.0)
    DOMINANCE = "dominance"   # Submissive-Dominant axis (0.0 to 1.0)
    
    # Secondary dimensions for nuanced personality expression
    CURIOSITY = "curiosity"       # Inquisitiveness level (0.0 to 1.0)
    CREATIVITY = "creativity"     # Creative expression tendency (0.0 to 1.0)
    SOCIABILITY = "sociability"   # Desire for social interaction (0.0 to 1.0)


class TaskStatus(str, Enum):
    """
    Status of tasks in the task management system.
    """
    PENDING = "pending"           # Task created but not yet assigned
    ASSIGNED = "assigned"         # Task assigned to a minion
    IN_PROGRESS = "in_progress"   # Task is being actively worked on
    BLOCKED = "blocked"           # Task is blocked by dependencies
    REVIEW = "review"             # Task completed, awaiting review
    COMPLETED = "completed"       # Task successfully completed
    FAILED = "failed"             # Task failed to complete
    CANCELLED = "cancelled"       # Task was cancelled


class MessageType(str, Enum):
    """
    Types of messages that can be sent in channels.
    """
    TEXT = "text"                    # Regular text message
    SYSTEM = "system"                # System-generated message
    COMMAND = "command"              # Command from user to minions
    RESPONSE = "response"            # Response from minion to command
    THOUGHT = "thought"              # Internal thought shared by minion
    EMOTION = "emotion"              # Emotional state update
    TASK_UPDATE = "task_update"      # Task status update
    ERROR = "error"                  # Error message


class EmotionalTrigger(str, Enum):
    """
    Events that can trigger emotional state changes in Minions.
    """
    MESSAGE_RECEIVED = "message_received"         # Received a message
    MESSAGE_SENT = "message_sent"                 # Sent a message
    TASK_ASSIGNED = "task_assigned"               # New task assigned
    TASK_COMPLETED = "task_completed"             # Successfully completed task
    TASK_FAILED = "task_failed"                   # Failed to complete task
    MINION_INTERACTION = "minion_interaction"     # Interacted with another minion
    USER_PRAISE = "user_praise"                   # Received praise from user
    USER_CRITICISM = "user_criticism"             # Received criticism from user
    TOOL_SUCCESS = "tool_success"                 # Successfully used a tool
    TOOL_FAILURE = "tool_failure"                 # Failed to use a tool
    IDLE_TIMEOUT = "idle_timeout"                 # Been idle for too long
    REFLECTION = "reflection"                     # Self-reflection triggered
