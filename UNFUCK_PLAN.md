# Plan to Unfuck Gemini Legion Back to Original Design

## The Problem
The codebase has completely diverged from the IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md. Instead of a clean ADK-native implementation, we have:

1. **Custom communication system** fighting with ADK
2. **Message duplication** from multiple broadcast paths
3. **Broken ADK integration** with fallback placeholders
4. **Monolithic service implementations** instead of clean domain separation

## The Original Vision (What We Need to Get Back To)

### Core Principles from Design Doc:
1. **Domain-Driven Design** - Clean separation of Minion, Communication, Task, Tool, and Session domains
2. **Event-Driven Architecture** - All state changes emit events, loose coupling via event bus
3. **ADK-Idiomatic Design** - Full leveraging of Google ADK's strengths
4. **Distributed Intelligence** - Not monolithic prompts but specialized reasoning engines

### Key Architecture Components:

```
┌─────────────────────────────────────────────────────┐
│            Legion Commander GUI (React/TS)           │
├─────────────────────────────────────────────────────┤
│           API Gateway (FastAPI + WebSocket)          │
├─────────────────────────────────────────────────────┤
│              Application Services Layer              │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │   Minion    │ │     Task     │ │   Channel    │ │
│  │  Service    │ │   Service    │ │   Service    │ │
│  └─────────────┘ └──────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────┤
│                 Core Domain Layer                    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │   Minion    │ │  Emotional   │ │   Memory     │ │
│  │   Engine    │ │    Engine    │ │   Engine     │ │
│  └─────────────┘ └──────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────┤
│              Infrastructure Layer                    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │     ADK     │ │   Database   │ │    Event     │ │
│  │  Adapters   │ │   Adapters   │ │     Bus      │ │
│  └─────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

## What Needs to Be Torn Out

### 1. Custom Communication System
- `InterMinionCommunicationSystem` - Replace with ADK event bus
- `ConversationalLayer` - Use ADK's native messaging
- `MessageRouter` - ADK handles this
- Custom turn-taking - ADK has rate limiting

### 2. Duplicate Message Paths
- Remove `_notify_active_minions` completely
- Single message flow through ADK events

### 3. Custom Message Queuing
- `CommunicationCapability.message_queue` - Use ADK sessions
- Manual message processing loops - ADK handles async

## Step-by-Step Refactoring Plan

### Phase 1: Create ADK-Native Communication (Week 1)

1. **Create ADKEventBus adapter**:
```python
# gemini_legion_backend/core/infrastructure/adk/event_bus.py
from google.adk.events import EventBus
from typing import Dict, Any, Callable

class GeminiEventBus:
    """ADK-native event bus for all inter-component communication"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self._setup_event_handlers()
    
    async def emit_channel_message(self, channel_id: str, sender_id: str, content: str, metadata: Dict[str, Any] = None):
        """Emit a channel message event"""
        await self.event_bus.emit("channel.message", {
            "channel_id": channel_id,
            "sender_id": sender_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        })
    
    def subscribe_to_channel_messages(self, handler: Callable):
        """Subscribe to channel message events"""
        self.event_bus.on("channel.message", handler)
```

2. **Replace ChannelService message sending**:
```python
# In channel_service.py
async def send_message(self, channel_id: str, sender_id: str, content: str, ...):
    # Create message domain object
    message = Message(...)
    
    # Persist
    await self.message_repo.save(message)
    
    # Single event emission
    await self.event_bus.emit_channel_message(
        channel_id, sender_id, content, metadata
    )
    
    # That's it! No dual paths, no direct minion notification
```

### Phase 2: Proper ADK Agent Integration (Week 2)

1. **Create proper ADK communication tool**:
```python
# gemini_legion_backend/core/infrastructure/adk/tools/channel_tool.py
from google.adk.tools import Tool
from google.adk.decorators import tool

@tool
class SendChannelMessageTool(Tool):
    """ADK-native tool for channel communication"""
    
    name = "send_channel_message"
    description = "Send a message to a channel"
    
    parameters = {
        "channel": {"type": "string", "required": True, "description": "Channel ID or name"},
        "message": {"type": "string", "required": True, "description": "Message content"}
    }
    
    def __init__(self, minion_id: str, event_bus: GeminiEventBus):
        self.minion_id = minion_id
        self.event_bus = event_bus
    
    async def execute(self, channel: str, message: str) -> Dict[str, Any]:
        # Emit through event bus
        await self.event_bus.emit_channel_message(
            channel_id=channel,
            sender_id=self.minion_id,
            content=message
        )
        
        return {"success": True, "channel": channel}
```

2. **Fix MinionAgent to use ADK patterns**:
```python
# In minion_agent.py
class MinionAgent(LlmAgent):
    """ADK-native Minion implementation"""
    
    async def handle_channel_event(self, event: Dict[str, Any]):
        """Handle incoming channel messages via event subscription"""
        # Skip own messages
        if event["sender_id"] == self.minion_id:
            return
        
        # Build context
        context = {
            "channel": event["channel_id"],
            "sender": event["sender_id"],
            "timestamp": event["timestamp"]
        }
        
        # Use ADK session for state
        session = self.get_or_create_session(event["channel_id"])
        
        # Generate response using predict
        response = await self.predict(
            event["content"],
            session=session,
            context=context
        )
        
        # Response is sent via tool, not direct call
        if        # Response is sent via tool, not direct call
        if response:
            await self.tools["send_channel_message"].execute(
                channel=event["channel_id"],
                message=response
            )
```

### Phase 3: Clean Domain Separation (Week 3)

1. **Separate domain models from infrastructure**:
```python
# gemini_legion_backend/core/domain/minion.py
@dataclass
class Minion:
    """Pure domain model - no ADK dependencies"""
    minion_id: str
    name: str
    persona: MinionPersona
    emotional_state: EmotionalState
    # No agent reference, no tools - pure domain
```

2. **Create proper application services**:
```python
# gemini_legion_backend/core/application/services/minion_orchestrator.py
class MinionOrchestrator:
    """Orchestrates minion operations using domain and infrastructure"""
    
    def __init__(
        self,
        minion_repo: MinionRepository,
        agent_factory: ADKAgentFactory,
        event_bus: GeminiEventBus
    ):
        self.minion_repo = minion_repo
        self.agent_factory = agent_factory
        self.event_bus = event_bus
    
    async def spawn_minion(self, config: MinionConfig) -> Minion:
        # Create domain object
        minion = Minion(...)
        
        # Persist
        await self.minion_repo.save(minion)
        
        # Create ADK agent
        agent = await self.agent_factory.create_agent(minion)
        
        # Subscribe agent to events
        self.event_bus.subscribe_to_channel_messages(
            agent.handle_channel_event
        )
        
        # Emit spawn event
        await self.event_bus.emit("minion.spawned", {
            "minion_id": minion.minion_id,
            "name": minion.name
        })
        
        return minion
```

### Phase 4: Event-Driven Everything (Week 4)

1. **All state changes through events**:
```python
# Every significant action emits an event
await self.event_bus.emit("minion.emotional_state_changed", {...})
await self.event_bus.emit("task.assigned", {...})
await self.event_bus.emit("memory.stored", {...})
```

2. **WebSocket updates via event subscriptions**:
```python
# In connection_manager.py
def setup_event_subscriptions(self):
    # Subscribe to all events that need WebSocket broadcast
    self.event_bus.on("channel.message", self.broadcast_channel_message)
    self.event_bus.on("minion.spawned", self.broadcast_minion_update)
    # etc...
```

## Immediate Fixes While Refactoring

### Fix 1: Stop the duplication NOW
```python
# In channel_service.py, completely gut the send_message method:
async def send_message(self, channel_id: str, sender_id: str, content: str, ...):
    # Create and persist message
    message = Message(...)
    await self.message_repo.save(message)
    
    # ONLY broadcast via WebSocket - no other paths
    message_dict = self._message_to_dict(message)
    await connection_manager.broadcast_service_event(
        "message_sent",
        {"channel_id": channel_id, "message": message_dict}
    )
    
    return message_dict
```

### Fix 2: Disable minion auto-responses temporarily
```python
# In minion_agent.py _process_messages_loop
async def _process_messages_loop(self):
    """TEMPORARILY DISABLED - Moving to event-driven"""
    return  # Just return immediately
```

### Fix 3: Create a simple test endpoint
```python
# Add to channels.py
@router.post("/test_simple", response_model=Dict[str, Any])
async def test_simple_message(channel_id: str, content: str):
    """Simple test endpoint that only does WebSocket broadcast"""
    message_dict = {
        "message_id": str(uuid.uuid4()),
        "channel_id": channel_id,
        "sender_id": "TEST_USER",
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    await connection_manager.broadcast_service_event(
        "message_sent",
        {"channel_id": channel_id, "message": message_dict}
    )
    
    return {"success": True, "message": message_dict}
```

## Migration Timeline

### Week 1: Stop the bleeding
- Apply immediate fixes
- Disable all automatic minion responses
- Single message path only

### Week 2: ADK Event Bus
- Implement GeminiEventBus
- Replace custom communication system
- All messages through events

### Week 3: Proper ADK Agents
- Rewrite MinionAgent to use predict()
- Implement proper ADK tools
- Remove all custom message queuing

### Week 4: Clean Architecture
- Separate domain from infrastructure
- Event-driven state changes
- Remove all direct coupling

## Success Metrics

1. **No message duplication** - Each message appears exactly once
2. **Real ADK responses** - No placeholders, actual predict() calls
3. **Clean separation** - Domain objects have no infrastructure dependencies
4. **Event-driven** - All updates flow through event bus
5. **ADK-native** - Using ADK patterns, not fighting them

## The Bottom Line

The current implementation is fundamentally broken because it's trying to build a custom system on top of ADK instead of using ADK properly. The fix isn't to patch the current system - it's to tear out all the custom bullshit and rebuild using ADK's native patterns as described in the original design document.

This will take about 4 weeks of focused refactoring, but the result will be the clean, scalable architecture that was originally designed.
