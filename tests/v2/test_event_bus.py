"""
Test Suite for V2 Architecture - Event Bus Tests

This tests the fucking HEART of the V2 architecture - the event bus.
If this doesn't work, nothing works.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Set

from gemini_legion_backend.core.infrastructure.adk.events import (
    get_event_bus,
    reset_event_bus,
    EventType,
    Event,
    GeminiEventBus
)


class EventCollector:
    """Collects events for testing - because we need to verify this shit works"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.event_types: Set[EventType] = set()
        self.call_count = 0
        
    async def collect(self, event: Event):
        """Collect an event"""
        self.events.append(event)
        self.event_types.add(event.type)
        self.call_count += 1
    
    def clear(self):
        """Clear collected events"""
        self.events.clear()
        self.event_types.clear()
        self.call_count = 0


@pytest.fixture
async def event_bus():
    """Fresh event bus for each test"""
    reset_event_bus()
    return get_event_bus()


@pytest.fixture
async def collector():
    """Event collector for testing"""
    return EventCollector()


class TestEventBusCore:
    """Test core event bus functionality"""
    
    async def test_event_bus_singleton(self):
        """Test that event bus is a proper singleton"""
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        
        assert bus1 is bus2, "Event bus should be a singleton"
        
        # Reset and check again
        reset_event_bus()
        bus3 = get_event_bus()
        
        assert bus3 is not bus1, "Reset should create new instance"
    
    async def test_basic_event_emission(self, event_bus):
        """Test basic event emission"""
        # Emit an event
        event = await event_bus.emit(
            EventType.SYSTEM_HEALTH,
            data={"status": "operational"},
            source="test_suite"
        )
        
        # Verify event structure
        assert event.type == EventType.SYSTEM_HEALTH
        assert event.data["status"] == "operational"
        assert event.source == "test_suite"
        assert isinstance(event.id, str)
        assert isinstance(event.timestamp, datetime)
    
    async def test_event_subscription(self, event_bus, collector):
        """Test event subscription and delivery"""
        # Subscribe to events
        sub_id = event_bus.subscribe(EventType.CHANNEL_MESSAGE, collector.collect)
        
        # Emit event
        await event_bus.emit_channel_message(
            channel_id="test_channel",
            sender_id="test_sender",
            content="Test message"
        )
        
        # Wait for async delivery
        await asyncio.sleep(0.1)
        
        # Verify collection
        assert collector.call_count == 1
        assert EventType.CHANNEL_MESSAGE in collector.event_types
        
        event = collector.events[0]
        assert event.data["channel_id"] == "test_channel"
        assert event.data["sender_id"] == "test_sender"
        assert event.data["content"] == "Test message"
    
    async def test_multiple_subscribers(self, event_bus):
        """Test that multiple subscribers all receive events"""
        collectors = [EventCollector() for _ in range(5)]
        
        # Subscribe all collectors
        for collector in collectors:
            event_bus.subscribe(EventType.MINION_SPAWNED, collector.collect)
        
        # Emit event
        await event_bus.emit(
            EventType.MINION_SPAWNED,
            data={"minion_id": "test_minion", "name": "TestBot"}
        )
        
        await asyncio.sleep(0.1)
        
        # All should receive
        for collector in collectors:
            assert collector.call_count == 1
            assert collector.events[0].data["minion_id"] == "test_minion"
    
    async def test_subscribe_all(self, event_bus, collector):
        """Test subscribing to all event types"""
        sub_ids = event_bus.subscribe_all(collector.collect)
        
        # Should get subscription for each event type
        assert len(sub_ids) == len(EventType)
        
        # Emit different event types
        await event_bus.emit(EventType.CHANNEL_CREATED, {"channel_id": "ch1"})
        await event_bus.emit(EventType.MINION_SPAWNED, {"minion_id": "m1"})
        await event_bus.emit(EventType.TASK_CREATED, {"task_id": "t1"})
        
        await asyncio.sleep(0.1)
        
        # Should receive all
        assert collector.call_count == 3
        assert len(collector.event_types) == 3


class TestEventPropagation:
    """Test event propagation patterns"""
    
    async def test_no_subscribers_no_error(self, event_bus):
        """Test that emitting with no subscribers doesn't error"""
        # This should not raise
        await event_bus.emit(
            EventType.SYSTEM_ERROR,
            data={"error": "test error"}
        )
    
    async def test_sync_handler_support(self, event_bus):
        """Test that sync handlers are properly wrapped"""
        results = []
        
        def sync_handler(event: Event):
            """Synchronous handler"""
            results.append(event.data)
        
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, sync_handler)
        
        await event_bus.emit_channel_message(
            channel_id="test",
            sender_id="test",
            content="Sync handler test"
        )
        
        await asyncio.sleep(0.2)  # Give thread time
        
        assert len(results) == 1
        assert results[0]["content"] == "Sync handler test"
    
    async def test_handler_exception_isolation(self, event_bus):
        """Test that one handler's exception doesn't affect others"""
        good_collector = EventCollector()
        bad_calls = []
        
        async def bad_handler(event: Event):
            """Handler that always fails"""
            bad_calls.append(1)
            raise ValueError("I'm a bad handler")
        
        # Subscribe both
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, bad_handler)
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, good_collector.collect)
        
        # Emit event
        await event_bus.emit_channel_message(
            channel_id="test",
            sender_id="test",
            content="Test with bad handler"
        )
        
        await asyncio.sleep(0.1)
        
        # Bad handler was called but good one still works
        assert len(bad_calls) == 1
        assert good_collector.call_count == 1
    
    async def test_event_ordering(self, event_bus, collector):
        """Test that events are delivered in order"""
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, collector.collect)
        
        # Emit multiple events rapidly
        for i in range(10):
            await event_bus.emit_channel_message(
                channel_id="test",
                sender_id="test",
                content=f"Message {i}"
            )
        
        await asyncio.sleep(0.2)
        
        # Verify order
        assert len(collector.events) == 10
        for i, event in enumerate(collector.events):
            assert event.data["content"] == f"Message {i}"


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    async def test_default_rate_limit(self, event_bus):
        """Test default rate limiting"""
        source = "spam_test"
        successful = 0
        limited = 0
        
        # Try to send more than default limit (10/sec)
        for i in range(15):
            try:
                await event_bus.emit(
                    EventType.CHANNEL_MESSAGE,
                    {"content": f"Spam {i}"},
                    source=source
                )
                successful += 1
            except ValueError:
                limited += 1
        
        assert successful == 10, "Should allow 10 events (default limit)"
        assert limited == 5, "Should rate limit 5 events"
    
    async def test_custom_rate_limit(self, event_bus):
        """Test custom rate limit setting"""
        source = "custom_limit"
        event_bus.set_rate_limit(source, 3)
        
        successful = 0
        for i in range(5):
            try:
                await event_bus.emit(
                    EventType.CHANNEL_MESSAGE,
                    {"content": f"Message {i}"},
                    source=source
                )
                successful += 1
            except ValueError:
                pass
        
        assert successful == 3, "Should respect custom limit"
    
    async def test_rate_limit_window(self, event_bus):
        """Test that rate limit resets after time window"""
        source = "window_test"
        event_bus.set_rate_limit(source, 2)
        
        # Send 2 (should work)
        for i in range(2):
            await event_bus.emit(
                EventType.CHANNEL_MESSAGE,
                {"content": f"Message {i}"},
                source=source
            )
        
        # Third should fail
        with pytest.raises(ValueError):
            await event_bus.emit(
                EventType.CHANNEL_MESSAGE,
                {"content": "Should fail"},
                source=source
            )
        
        # Wait for window to reset
        await asyncio.sleep(1.1)
        
        # Should work again
        await event_bus.emit(
            EventType.CHANNEL_MESSAGE,
            {"content": "After window"},
            source=source
        )


class TestEventHistory:
    """Test event history functionality"""
    
    async def test_event_history_storage(self, event_bus):
        """Test that events are stored in history"""
        # Emit some events
        for i in range(5):
            await event_bus.emit(
                EventType.CHANNEL_MESSAGE,
                {"content": f"Message {i}"},
                source=f"test_{i}"
            )
        
        # Get history
        history = event_bus.get_recent_events()
        
        assert len(history) >= 5
        
        # Verify order (most recent last)
        for i in range(5):
            event = history[-(5-i)]
            assert event.data["content"] == f"Message {i}"
    
    async def test_history_filtering(self, event_bus):
        """Test filtering history by event type"""
        # Emit different types
        await event_bus.emit(EventType.CHANNEL_MESSAGE, {"msg": 1})
        await event_bus.emit(EventType.MINION_SPAWNED, {"minion": 1})
        await event_bus.emit(EventType.CHANNEL_MESSAGE, {"msg": 2})
        await event_bus.emit(EventType.TASK_CREATED, {"task": 1})
        
        # Filter by type
        messages = event_bus.get_recent_events(EventType.CHANNEL_MESSAGE)
        
        assert len(messages) == 2
        assert all(e.type == EventType.CHANNEL_MESSAGE for e in messages)
    
    async def test_history_limit(self, event_bus):
        """Test history respects limit"""
        # Set up a fresh bus
        reset_event_bus()
        bus = get_event_bus()
        
        # Emit more than history limit
        for i in range(1500):
            await bus.emit(
                EventType.SYSTEM_HEALTH,
                {"index": i}
            )
        
        # History should be limited
        history = bus.get_recent_events()
        assert len(history) <= 1000  # Default limit
    
    async def test_clear_history(self, event_bus):
        """Test clearing history"""
        # Add some events
        for i in range(10):
            await event_bus.emit(EventType.SYSTEM_HEALTH, {"i": i})
        
        # Clear
        event_bus.clear_history()
        
        # Should be empty
        history = event_bus.get_recent_events()
        assert len(history) == 0


class TestChannelMessageSpecifics:
    """Test channel message specific functionality"""
    
    async def test_channel_message_convenience(self, event_bus):
        """Test the emit_channel_message convenience method"""
        result = await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_bot",
            content="Hello world",
            metadata={"mood": "happy"}
        )
        
        # Should create proper event
        assert result.type == EventType.CHANNEL_MESSAGE
        assert result.data["channel_id"] == "general"
        assert result.data["sender_id"] == "test_bot"
        assert result.data["content"] == "Hello world"
        assert result.data["message_id"].startswith("msg_")
        assert "timestamp" in result.data
    
    async def test_message_id_uniqueness(self, event_bus):
        """Test that message IDs are always unique"""
        ids = set()
        
        # Send many messages rapidly
        for i in range(100):
            event = await event_bus.emit_channel_message(
                channel_id="test",
                sender_id="test",
                content=f"Message {i}"
            )
            
            msg_id = event.data["message_id"]
            assert msg_id not in ids, f"Duplicate message ID: {msg_id}"
            ids.add(msg_id)


if __name__ == "__main__":
    # Run with proper async support
    pytest.main([__file__, "-v", "-s", "--asyncio-mode=auto"])
