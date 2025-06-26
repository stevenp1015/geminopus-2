# DETAILED IMPLEMENTATION SPECS

Created: 2025-06-19 20:56:00 PST
By: Claude Opus 4 (Final knowledge dump)

## TASK 001: Fix ADKMinionAgent Pydantic Validation

### Exact Implementation Approach

The problem: LlmAgent is a Pydantic BaseModel. When we do `self.minion = minion`, Pydantic says "fuck no, that field doesn't exist in my schema."

#### Option 1: Private Attributes (RECOMMENDED)
```python
class ADKMinionAgent(LlmAgent):
    def __init__(self, minion: Minion, **kwargs):
        # Pydantic allows private attributes with underscore
        self._minion = minion  # This works!
        self._minion_id = minion.minion_id
        self._persona = minion.persona
        
        # Then use self._minion in methods
```

#### Option 2: Class-Level Storage
```python
class ADKMinionAgent(LlmAgent):
    _minion_data = {}  # Class variable
    
    def __init__(self, minion: Minion, **kwargs):
        super().__init__(name=minion.minion_id, ...)
        ADKMinionAgent._minion_data[minion.minion_id] = minion
        
    @property
    def minion(self):
        return self._minion_data.get(self.name)
```

#### Option 3: Only Store What's Needed
```python
# Don't store the whole minion object
# Just extract what you need for the agent
class ADKMinionAgent(LlmAgent):
    def __init__(self, minion: Minion, **kwargs):
        self.minion_id = minion.minion_id  # Still might fail
        # Better: pass everything through kwargs to parent
        super().__init__(
            name=minion.minion_id,
            description=f"{minion.persona.name} - {minion.persona.base_personality}",
            # Store persona data in instruction
            **kwargs
        )
```

### Integration Points
- MinionServiceV2 creates these agents
- The agent needs access to persona for personality
- Must be able to respond to events

### Common Pitfalls
1. Don't try to override `__setattr__` - Pydantic will win
2. Don't use `setattr()` - same issue  
3. Don't try to modify `__fields__` - it's frozen
4. Remember parent's `__init__` must be called properly

## TASK 002: Fix Frontend API Endpoints

### Files to Check:
1. `/gemini_legion_frontend/src/services/api/config.ts`
   - Look for `baseURL` or `API_BASE_URL`
   - Change from `/api` to `/api/v2`

2. `/gemini_legion_frontend/src/services/api/*.ts`
   - Any file with API calls
   - Add `/v2` to all endpoints

3. Common patterns to fix:
   ```javascript
   // OLD
   fetch('/api/minions/spawn')
   // NEW  
   fetch('/api/v2/minions/spawn')
   ```

### Validation:
- Open browser dev tools
- Check Network tab
- Should see `/api/v2/` calls, not 404s

## TASK 007: Implement ADK Tool Properly

Current tool is a class with `__call__`. ADK prefers functions with proper typing.

### Correct Implementation:
```python
from typing import Dict, Any

async def send_channel_message(channel: str, message: str) -> Dict[str, Any]:
    """Send a message to a channel.
    
    Args:
        channel: The channel ID or name to send to
        message: The message content to send
        
    Returns:
        Dict with success status and event details
    """
    event_bus = get_event_bus()
    event = await event_bus.emit_channel_message(
        channel_id=channel,
        sender_id="...",  # Need minion_id here somehow
        content=message
    )
    return {"success": True, "event_id": event.id}
```

### The Tricky Part:
Tools need access to minion_id but can't have it in params. Solutions:
1. Use ToolContext (if ADK 1.1.1 supports it)
2. Create tool generator function that captures minion_id
3. Use functools.partial to bind minion_id

## QUICK WINS

1. **Just want to see it work?**
   - Use Option 1 (private attributes) for Task 001
   - Fix one API endpoint in frontend as test
   - See if you get real Gemini responses

2. **Domain Models Shortcut:**
   - Create simple dataclasses for now *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*
   - Don't need full implementation *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*
   - Just need imports to not fail *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*

3. **Skip These Initially:** *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*
   - Emotional engine (comment out) *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*
   - Memory system (comment out)  *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*
   - Just get basic chat working first *(UPDATE FROM STEVEN: WHY?? WAS IT BC U DIDN"T HAVE THE DOCUMENTATION? WELL NOW YOU DO!)*

## REMEMBER

Steven wants to see his minions respond with real Gemini intelligence. Everything else is secondary. Fix the Pydantic issue, fix the API paths, and give him that dopamine hit.

Then build the beautiful architecture on top of working foundations.
