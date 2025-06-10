"""
ADK Event Bus - The Single Source of Truth for All Communication

This replaces the custom InterMinionCommunicationSystem with a proper
event-driven architecture using ADK patterns.
"""

from typing import Dict, Any, Callable, List, Optional, Set
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All event types in the system"""
    # Channel events
    CHANNEL_MESSAGE = "channel.message"
    CHANNEL_CREATED = "channel.created"
    CHANNEL_UPDATED = "channel.updated"
    CHANNEL_DELETED = "channel.deleted"
    CHANNEL_MEMBER_ADDED = "channel.member.added"
    CHANNEL_MEMBER_REMOVED = "channel.member.removed"
    
    # Minion events  
    MINION_SPAWNED = "minion.spawned"
    MINION_DESPAWNED = "minion.despawned"
    MINION_STATE_CHANGED = "minion.state.changed"
    MINION_EMOTIONAL_CHANGE = "minion.emotional.change"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    # System events
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ERROR = "system.error"


@dataclass
class Event:
    """Base event structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.SYSTEM_HEALTH
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ChannelMessageEvent(Event):
    """Specialized event for channel messages"""
    type: EventType = EventType.CHANNEL_MESSAGE
    
    def __post_init__(self):
        # Ensure required fields
        required = ["channel_id", "sender_id", "content"]
        for field in required:
            if field not in self.data:
                raise ValueError(f"ChannelMessageEvent requires '{field}' in data")


class GeminiEventBus:
    """
    ADK-native event bus for all inter-component communication.
    
    This is the SINGLE source of truth for all events in the system.
    No more parallel paths, no more custom routers, just events.
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._history_limit = 1000
        self._processing_lock = asyncio.Lock()
        
        # Rate limiting per source
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        self._default_rate_limit = 10  # events per second
        
        logger.info("GeminiEventBus initialized - Single source of truth for all events")
    
    async def emit(self, event_type: EventType, data: Dict[str, Any], source: str = "system", metadata: Optional[Dict[str, Any]] = None) -> Event:
        """
        Emit an event to all subscribers.
        
        This is THE way to communicate in the system. No other paths.
        """
        # Check rate limit
        if not await self._check_rate_limit(source, event_type):
            logger.warning(f"Rate limit exceeded for {source} on {event_type}")
            raise ValueError(f"Rate limit exceeded for {source}")
        
        # Create event
        event = Event(
            type=event_type,
            source=source,
            data=data,
            metadata=metadata or {}
        )
        
        # Add to history
        async with self._processing_lock:
            self._event_history.append(event)
            if len(self._event_history) > self._history_limit:
                self._event_history = self._event_history[-self._history_limit:]
        
        # Log the event
        logger.debug(f"Event emitted: {event_type.value} from {source}")
        
        # Notify subscribers
        await self._notify_subscribers(event)
        
        return event
    
    async def emit_channel_message(self, channel_id: str, sender_id: str, content: str, source: str = "system", metadata: Optional[Dict[str, Any]] = None) -> Event:
        """
        Convenience method for emitting channel messages.
        
        THIS is how all messages should be sent. Period.
        """
        # Generate a proper unique message ID
        message_id = f"msg_{uuid.uuid4()}"
        
        data = {
            "message_id": message_id,
            "channel_id": channel_id,
            "sender_id": sender_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        event = ChannelMessageEvent(
            source=source,
            data=data,
            metadata=metadata or {}
        )
        
        # Use regular emit
        return await self.emit(EventType.CHANNEL_MESSAGE, data, source, metadata)
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], Any]) -> str:
        """
        Subscribe to an event type.
        
        Returns subscription ID for later unsubscribe.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        sub_id = f"sub_{event_type.value}_{len(self._subscribers[event_type])}"
        
        logger.info(f"Subscriber added for {event_type.value}: {sub_id}")
        return sub_id
    
    def subscribe_all(self, handler: Callable[[Event], Any]) -> List[str]:
        """Subscribe to all event types"""
        sub_ids = []
        for event_type in EventType:
            sub_ids.append(self.subscribe(event_type, handler))
        return sub_ids
    
    async def _notify_subscribers(self, event: Event):
        """Notify all subscribers of an event"""
        handlers = self._subscribers.get(event.type, [])
        
        if not handlers:
            logger.debug(f"No subscribers for {event.type.value}")
            return
        
        # Execute all handlers concurrently
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # Wrap sync handlers
                tasks.append(asyncio.create_task(asyncio.to_thread(handler, event)))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in event handler for {event.type.value}: {result}")
    
    async def _check_rate_limit(self, source: str, event_type: EventType) -> bool:
        """Check if source is within rate limit"""
        now = datetime.now()
        
        if source not in self._rate_limits:
            self._rate_limits[source] = {
                "events": [],
                "limit": self._default_rate_limit
            }
        
        source_limits = self._rate_limits[source]
        
        # Clean old events (older than 1 second)
        cutoff = now.timestamp() - 1.0
        source_limits["events"] = [ts for ts in source_limits["events"] if ts > cutoff]
        
        # Check limit
        if len(source_limits["events"]) >= source_limits["limit"]:
            return False
        
        # Add this event
        source_limits["events"].append(now.timestamp())
        return True
    
    def set_rate_limit(self, source: str, events_per_second: int):
        """Set custom rate limit for a source"""
        if source not in self._rate_limits:
            self._rate_limits[source] = {"events": []}
        self._rate_limits[source]["limit"] = events_per_second
    
    def get_recent_events(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get recent events from history"""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
        logger.info("Event history cleared")


# Global singleton instance
_event_bus: Optional[GeminiEventBus] = None


def get_event_bus() -> GeminiEventBus:
    """Get the global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = GeminiEventBus()
    return _event_bus


def reset_event_bus():
    """Reset the event bus (mainly for testing)"""
    global _event_bus
    _event_bus = None
