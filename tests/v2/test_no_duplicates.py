"""
Test Suite for V2 Architecture - No Duplicates Test

This test ensures that messages are NEVER duplicated in the new architecture.
If this test fails, we've fucked up somewhere.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any

from gemini_legion_backend.core.infrastructure.adk.events import (
    get_event_bus,
    reset_event_bus,
    EventType,
    Event
)
from gemini_legion_backend.core.application.services.channel_service_v2 import ChannelServiceV2
from gemini_legion_backend.core.infrastructure.persistence.repositories import (
    ChannelRepository,
    MessageRepository
)


class MessageCollector:
    """Collects all messages that go through the event bus"""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.channel_events: List[Event] = []
        
    async def collect_message(self, event: Event):
        """Collect message events"""
        if event.type == EventType.CHANNEL_MESSAGE:
            self.messages.append(event.data)
            self.channel_events.append(event)
    
    def get_message_count(self, content: str) -> int:
        """Count how many times a message with specific content appears"""
        return len([m for m in self.messages if m.get("content") == content])
    
    def get_unique_message_ids(self) -> set:
        """Get all unique message IDs"""
        return {m.get("message_id") for m in self.messages if m.get("message_id")}
    
    def clear(self):
        """Clear collected messages"""
        self.messages.clear()
        self.channel_events.clear()


@pytest.fixture
async def event_bus():
    """Get a fresh event bus for each test"""
    reset_event_bus()
    return get_event_bus()


@pytest.fixture
async def channel_service():
    """Create a channel service for testing"""
    service = ChannelServiceV2(
        channel_repository=ChannelRepository(),
        message_repository=MessageRepository()
    )
    await service.start()
    yield service
    await service.stop()


@pytest.fixture
async def message_collector(event_bus):
    """Create a message collector subscribed to events"""
    collector = MessageCollector()
    event_bus.subscribe(EventType.CHANNEL_MESSAGE, collector.collect_message)
    return collector


@pytest.fixture
async def test_channel(channel_service):
    """Create a test channel"""
    channel_id = f"test_channel_{uuid.uuid4()}"
    channel_data = await channel_service.create_channel(
        channel_id=channel_id,
        name="Test Channel",
        channel_type="public",
        description="Channel for testing",
        creator="test_suite"
    )
    return channel_data


class TestNoDuplicates:
    """Test suite to ensure NO FUCKING DUPLICATES"""
    
    async def test_single_message_single_event(self, channel_service, test_channel, message_collector):
        """Test that sending one message produces exactly one event"""
        # Clear any startup events
        message_collector.clear()
        
        # Send a message
        test_content = f"Test message {uuid.uuid4()}"
        message_data = await channel_service.send_message(
            channel_id=test_channel["channel_id"],
            sender_id="test_user",
            content=test_content
        )
        
        # Wait a bit for any duplicate events
        await asyncio.sleep(0.1)
        
        # Check we got exactly one event
        assert message_collector.get_message_count(test_content) == 1, \
            f"Expected 1 message event, got {message_collector.get_message_count(test_content)}"
        
        # Check message ID is unique
        assert message_data["message_id"] in message_collector.get_unique_message_ids()
    
    async def test_multiple_messages_no_duplicates(self, channel_service, test_channel, message_collector):
        """Test that multiple messages don't create duplicates"""
        message_collector.clear()
        
        # Send multiple messages
        num_messages = 10
        test_messages = []
        
        for i in range(num_messages):
            content = f"Test message {i} - {uuid.uuid4()}"
            test_messages.append(content)
            
            await channel_service.send_message(
                channel_id=test_channel["channel_id"],
                sender_id="test_user",
                content=content
            )
        
        # Wait for any stragglers
        await asyncio.sleep(0.2)
        
        # Check each message appears exactly once
        for content in test_messages:
            count = message_collector.get_message_count(content)
            assert count == 1, f"Message '{content}' appeared {count} times, expected 1"
        
        # Check total count
        assert len(message_collector.messages) == num_messages, \
            f"Expected {num_messages} total events, got {len(message_collector.messages)}"
        
        # Check all message IDs are unique
        unique_ids = message_collector.get_unique_message_ids()
        assert len(unique_ids) == num_messages, \
            f"Expected {num_messages} unique IDs, got {len(unique_ids)}"
    
    async def test_concurrent_messages_no_duplicates(self, channel_service, test_channel, message_collector):
        """Test that concurrent message sending doesn't create duplicates"""
        message_collector.clear()
        
        # Send messages concurrently
        num_concurrent = 20
        
        async def send_message(index: int):
            content = f"Concurrent message {index} - {uuid.uuid4()}"
            await channel_service.send_message(
                channel_id=test_channel["channel_id"],
                sender_id=f"user_{index}",
                content=content
            )
            return content
        
        # Send all messages at once
        tasks = [send_message(i) for i in range(num_concurrent)]
        sent_messages = await asyncio.gather(*tasks)
        
        # Wait for events to settle
        await asyncio.sleep(0.3)
        
        # Check each message appears exactly once
        for content in sent_messages:
            count = message_collector.get_message_count(content)
            assert count == 1, f"Concurrent message appeared {count} times, expected 1"
        
        # Verify total count
        assert len(message_collector.messages) == num_concurrent, \
            f"Expected {num_concurrent} events from concurrent sends, got {len(message_collector.messages)}"
    
    async def test_message_ids_are_unique(self, channel_service, test_channel, message_collector):
        """Test that message IDs are ALWAYS unique"""
        message_collector.clear()
        
        # Send a bunch of messages rapidly
        num_messages = 50
        message_ids = []
        
        for i in range(num_messages):
            result = await channel_service.send_message(
                channel_id=test_channel["channel_id"],
                sender_id="test_user",
                content=f"Message {i}"
            )
            message_ids.append(result["message_id"])
        
        # Check all IDs are unique
        unique_ids = set(message_ids)
        assert len(unique_ids) == num_messages, \
            f"Message IDs are not unique! Expected {num_messages} unique IDs, got {len(unique_ids)}"
        
        # Verify they're proper UUIDs
        for msg_id in message_ids:
            assert msg_id.startswith("msg_"), f"Message ID doesn't start with 'msg_': {msg_id}"
            # Try to parse the UUID part
            uuid_part = msg_id.replace("msg_", "")
            try:
                uuid.UUID(uuid_part)
            except ValueError:
                pytest.fail(f"Message ID doesn't contain valid UUID: {msg_id}")
    
    async def test_no_event_bus_loops(self, channel_service, test_channel, event_bus):
        """Test that event handlers don't trigger infinite loops"""
        loop_detector = []
        
        async def potential_loop_handler(event: Event):
            """Handler that could cause a loop if not careful"""
            loop_detector.append(event.id)
            
            # If we're not careful, this could trigger another event
            if len(loop_detector) < 10:  # Safety limit
                # DON'T DO THIS - but test that it doesn't cause issues
                # await channel_service.send_message(...)
                pass
        
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, potential_loop_handler)
        
        # Send a message
        await channel_service.send_message(
            channel_id=test_channel["channel_id"],
            sender_id="test_user",
            content="Loop test message"
        )
        
        await asyncio.sleep(0.1)
        
        # Should only have one event
        assert len(loop_detector) == 1, f"Event loop detected! Got {len(loop_detector)} events"
    
    async def test_system_messages_no_duplicates(self, channel_service, test_channel, message_collector):
        """Test that system-generated messages (like join notifications) don't duplicate"""
        message_collector.clear()
        
        # Add a member (should generate a system message)
        await channel_service.add_member(
            channel_id=test_channel["channel_id"],
            member_id="new_member",
            role="member",
            added_by="test_suite"
        )
        
        # Wait for events
        await asyncio.sleep(0.1)
        
        # Should have exactly one system message
        system_messages = [
            m for m in message_collector.messages 
            if m.get("sender_id") == "system" and "joined the channel" in m.get("content", "")
        ]
        
        assert len(system_messages) == 1, \
            f"Expected 1 system message for member join, got {len(system_messages)}"


class TestEventBusIntegrity:
    """Test the event bus itself doesn't create duplicates"""
    
    async def test_single_emission_single_delivery(self, event_bus):
        """Test that one emission results in one delivery per subscriber"""
        received_events = []
        
        async def handler(event: Event):
            received_events.append(event)
        
        # Subscribe once
        event_bus.subscribe(EventType.CHANNEL_MESSAGE, handler)
        
        # Emit once
        await event_bus.emit_channel_message(
            channel_id="test",
            sender_id="test",
            content="Single emission test"
        )
        
        await asyncio.sleep(0.05)
        
        assert len(received_events) == 1, \
            f"Expected 1 event delivery, got {len(received_events)}"
    
    async def test_rate_limiting_works(self, event_bus):
        """Test that rate limiting prevents spam"""
        # Set low rate limit
        event_bus.set_rate_limit("spammer", 2)  # 2 per second
        
        # Try to spam
        successful = 0
        failed = 0
        
        for i in range(5):
            try:
                await event_bus.emit(
                    EventType.CHANNEL_MESSAGE,
                    {"content": f"Spam {i}"},
                    source="spammer"
                )
                successful += 1
            except ValueError:
                failed += 1
        
        assert successful == 2, f"Expected 2 successful emissions, got {successful}"
        assert failed == 3, f"Expected 3 rate-limited emissions, got {failed}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
