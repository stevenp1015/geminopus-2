"""
Test ADK Minion Responses - Ensure REAL Responses, Not Placeholder Bullshit

This test verifies that minions are using proper ADK integration and not
returning garbage like "I'm processing but my ADK integration needs work"
"""

import pytest
import asyncio
import os
from typing import List, Dict, Any
from unittest.mock import MagicMock, AsyncMock

from gemini_legion_backend.core.infrastructure.adk.agents.minion_agent_v2 import ADKMinionAgent
from gemini_legion_backend.core.infrastructure.adk.events import (
    get_event_bus,
    reset_event_bus,
    EventType,
    Event
)
from gemini_legion_backend.core.domain import (
    Minion,
    MinionPersona,
    EmotionalState,
    MoodVector
)


class ResponseCollector:
    """Collects minion responses from the event bus"""
    
    def __init__(self):
        self.responses: List[Dict[str, Any]] = []
        self.minion_responses: Dict[str, List[str]] = {}  # minion_id -> [responses]
    
    async def collect_response(self, event: Event):
        """Collect response events"""
        if event.type == EventType.CHANNEL_MESSAGE:
            sender = event.data.get("sender_id", "")
            content = event.data.get("content", "")
            
            # Only collect minion responses (not user or system)
            if sender not in ["COMMANDER_PRIME", "system", "test_user"]:
                self.responses.append(event.data)
                if sender not in self.minion_responses:
                    self.minion_responses[sender] = []
                self.minion_responses[sender].append(content)
    
    def has_placeholder_responses(self) -> List[str]:
        """Check if any responses contain placeholder text"""
        placeholder_phrases = [
            "ADK integration needs work",
            "I'm processing this but",
            "I'm having trouble processing",
            "placeholder",
            "[No response]",
            "fallback"
        ]
        
        bad_responses = []
        for response in self.responses:
            content = response.get("content", "")
            for phrase in placeholder_phrases:
                if phrase.lower() in content.lower():
                    bad_responses.append(f"{response.get('sender_id')}: {content}")
        
        return bad_responses
    
    def get_response_quality_score(self, response: str) -> float:
        """Score response quality (0-1, higher is better)"""
        score = 1.0
        
        # Deduct for short/lazy responses
        if len(response) < 20:
            score -= 0.3
        
        # Deduct for generic responses
        generic_phrases = ["acknowledged", "received", "okay", "i see", "understood"]
        for phrase in generic_phrases:
            if phrase in response.lower() and len(response) < 50:
                score -= 0.2
        
        # Bonus for personality
        personality_indicators = ["!", "?", "...", "haha", "hmm", "*", "~"]
        if any(indicator in response for indicator in personality_indicators):
            score += 0.1
        
        return max(0, min(1, score))


@pytest.fixture
async def event_bus():
    """Fresh event bus for each test"""
    reset_event_bus()
    return get_event_bus()


@pytest.fixture
async def response_collector(event_bus):
    """Response collector subscribed to events"""
    collector = ResponseCollector()
    event_bus.subscribe(EventType.CHANNEL_MESSAGE, collector.collect_response)
    return collector


@pytest.fixture
def test_minion():
    """Create a test minion"""
    persona = MinionPersona(
        name="TestBot",
        base_personality="Enthusiastic and helpful test assistant",
        personality_traits=["curious", "energetic", "detail-oriented"],
        quirks=["Loves testing", "Gets excited about clean code"],
        response_length="medium",
        catchphrases=["Test all the things!", "Clean code is happy code!"],
        expertise_areas=["testing", "code quality"],
        allowed_tools=["send_channel_message"],
        model_name="gemini-2.0-flash-exp"
    )
    
    emotional_state = EmotionalState(
        mood=MoodVector(valence=0.8, arousal=0.7, dominance=0.6),
        energy_level=0.9,
        stress_level=0.1
    )
    
    return Minion(
        minion_id="test_minion_001",
        name="TestBot",
        persona=persona,
        emotional_state=emotional_state,
        status="active"
    )


class TestMinionResponses:
    """Test that minions give REAL responses"""
    
    async def test_no_placeholder_responses(self, test_minion, event_bus, response_collector):
        """Test that minions NEVER return placeholder text"""
        # Skip if no API key
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        # Create minion agent
        agent = ADKMinionAgent(test_minion)
        await agent.start()
        
        # Simulate incoming message
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",
            content="Hello TestBot! How are you doing today?"
        )
        
        # Wait for response
        await asyncio.sleep(3)  # Give real API time to respond
        
        # Check for placeholder responses
        bad_responses = response_collector.has_placeholder_responses()
        assert len(bad_responses) == 0, \
            f"Found placeholder responses:\n" + "\n".join(bad_responses)
        
        # Ensure we got at least one response
        assert len(response_collector.responses) > 0, \
            "Minion didn't respond at all"
        
        await agent.stop()
    
    async def test_response_quality(self, test_minion, event_bus, response_collector):
        """Test that responses are high quality and personality-driven"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        agent = ADKMinionAgent(test_minion)
        await agent.start()
        
        # Send a message that should trigger a personality response
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",
            content="TestBot, tell me about your favorite thing!"
        )
        
        await asyncio.sleep(3)
        
        # Check response quality
        for minion_id, responses in response_collector.minion_responses.items():
            for response in responses:
                score = response_collector.get_response_quality_score(response)
                assert score >= 0.5, \
                    f"Low quality response from {minion_id}: '{response}' (score: {score})"
        
        await agent.stop()
    
    async def test_minion_uses_tools_properly(self, test_minion, event_bus):
        """Test that minions use ADK tools to send messages"""
        tool_uses = []
        
        # Mock the send tool to track usage
        original_call = None
        
        async def track_tool_use(*args, **kwargs):
            tool_uses.append({"args": args, "kwargs": kwargs})
            # Don't actually send to avoid event loops in test
            return {"success": True, "event_id": "test_event_123"}
        
        # Create agent
        agent = ADKMinionAgent(test_minion)
        
        # Monkey patch the tool
        if hasattr(agent.comm_kit.send_message, '__call__'):
            original_call = agent.comm_kit.send_message.__call__
            agent.comm_kit.send_message.__call__ = track_tool_use
        
        await agent.start()
        
        # Trigger a response
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",  
            content="Hey TestBot, please respond to this!"
        )
        
        await asyncio.sleep(2)
        
        # Check tool was used
        assert len(tool_uses) > 0, "Minion didn't use send_message tool"
        
        # Verify tool was called with proper arguments
        tool_call = tool_uses[0]["kwargs"]
        assert "channel" in tool_call, "Tool call missing channel"
        assert "message" in tool_call, "Tool call missing message"
        assert tool_call["channel"] == "general", "Tool called with wrong channel"
        
        # Restore original if we modified it
        if original_call:
            agent.comm_kit.send_message.__call__ = original_call
        
        await agent.stop()
    
    async def test_minion_personality_consistency(self, event_bus, response_collector):
        """Test that minions maintain personality across responses"""
        # Create a minion with strong personality
        persona = MinionPersona(
            name="PirateBot",
            base_personality="A salty sea pirate who speaks in pirate dialect",
            personality_traits=["boisterous", "adventurous", "loves treasure"],
            quirks=["Says 'arr' a lot", "Mentions the sea constantly"],
            response_length="medium",
            catchphrases=["Ahoy matey!", "Shiver me timbers!", "Arr arr!"],
            expertise_areas=["sailing", "treasure hunting"],
            allowed_tools=["send_channel_message"],
            model_name="gemini-2.0-flash-exp"
        )
        
        pirate_minion = Minion(
            minion_id="pirate_bot_001",
            name="PirateBot",
            persona=persona,
            emotional_state=EmotionalState(
                mood=MoodVector(valence=0.7, arousal=0.8, dominance=0.9),
                energy_level=0.8,
                stress_level=0.2
            ),
            status="active"
        )
        
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        agent = ADKMinionAgent(pirate_minion)
        await agent.start()
        
        # Send multiple messages
        test_messages = [
            "Hello PirateBot!",
            "What's your favorite treasure?",
            "Tell me about the sea"
        ]
        
        for msg in test_messages:
            await event_bus.emit_channel_message(
                channel_id="general",
                sender_id="test_user",
                content=msg
            )
            await asyncio.sleep(2)
        
        # Check responses maintain personality
        pirate_responses = response_collector.minion_responses.get("pirate_bot_001", [])
        assert len(pirate_responses) >= 2, "PirateBot didn't respond enough"
        
        # Check for pirate-ness
        pirate_words = ["arr", "ahoy", "matey", "sea", "treasure", "sail", "captain"]
        personality_score = 0
        
        for response in pirate_responses:
            response_lower = response.lower()
            if any(word in response_lower for word in pirate_words):
                personality_score += 1
        
        personality_ratio = personality_score / len(pirate_responses)
        assert personality_ratio >= 0.5, \
            f"PirateBot not pirate-y enough. Only {personality_ratio*100}% of responses had pirate personality"
        
        await agent.stop()
    
    async def test_minion_handles_context(self, test_minion, event_bus, response_collector):
        """Test that minions maintain context across messages"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        agent = ADKMinionAgent(test_minion)
        await agent.start()
        
        # Send related messages
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",
            content="My name is Steven and I love coding"
        )
        
        await asyncio.sleep(2)
        
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",
            content="What's my name?"
        )
        
        await asyncio.sleep(2)
        
        # Check if minion remembered the name
        responses = response_collector.minion_responses.get("test_minion_001", [])
        assert len(responses) >= 2, "Not enough responses to test context"
        
        # The second response should mention "Steven"
        second_response = responses[1].lower()
        assert "steven" in second_response, \
            f"Minion forgot the name. Response: {responses[1]}"
        
        await agent.stop()


class TestADKIntegration:
    """Test proper ADK patterns are being used"""
    
    def test_minion_uses_genai_properly(self, test_minion):
        """Test that minion is set up with proper Gemini configuration"""
        agent = ADKMinionAgent(test_minion)
        
        # Check model is configured
        assert agent.model is not None, "Model not initialized"
        assert hasattr(agent.model, 'generate_content'), "Model missing generate_content method"
        
        # Check system instruction is set
        system_instruction = agent._build_system_instruction()
        assert "TestBot" in system_instruction, "System instruction missing minion name"
        assert "test assistant" in system_instruction, "System instruction missing personality"
        
        # Check temperature is reasonable
        temp = agent._get_temperature()
        assert 0.1 <= temp <= 1.0, f"Temperature out of range: {temp}"
    
    def test_minion_tools_are_proper_adk_tools(self, test_minion):
        """Test that communication tools follow ADK patterns"""
        agent = ADKMinionAgent(test_minion)
        
        # Check tools exist
        tools = agent.comm_kit.get_tools()
        assert len(tools) > 0, "No tools configured"
        
        # Check send_message tool
        send_tool = agent.comm_kit.send_message
        assert hasattr(send_tool, 'name'), "Tool missing name"
        assert hasattr(send_tool, 'description'), "Tool missing description"
        assert send_tool.name == "send_channel_message", "Wrong tool name"
    
    async def test_event_subscription_works(self, test_minion, event_bus):
        """Test that minions properly subscribe to events"""
        received_events = []
        
        # Create a custom handler to track
        async def track_handler(event: Event):
            received_events.append(event)
        
        # Create agent
        agent = ADKMinionAgent(test_minion)
        
        # Replace handler temporarily
        original_handler = agent._handle_channel_message
        agent._handle_channel_message = track_handler
        agent._setup_event_subscriptions()
        
        # Emit event
        await event_bus.emit_channel_message(
            channel_id="general",
            sender_id="test_user",
            content="Test subscription"
        )
        
        await asyncio.sleep(0.1)
        
        # Check event was received
        assert len(received_events) > 0, "Minion didn't receive events"
        
        # Restore handler
        agent._handle_channel_message = original_handler


if __name__ == "__main__":
    # Run with -v for verbose output
    pytest.main([__file__, "-v", "-s"])
