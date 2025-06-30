# ADK Implementation Fix Guide
## Fixing Runner.run_async() and Session State Management

**This document provides the EXACT fixes needed to resolve the ADK implementation issues.**

---

## 🔧 FIX #1: Correct Runner.run_async() Call

**File:** `/gemini_legion_backend/core/application/services/minion_service_v2.py`
**Lines:** ~563-570

### Current Broken Code:
```python
agent_response_generator = runner.run_async(
    prompt=content,  # ❌ Wrong parameter name
    session_id=current_session_id,
    user_id=sender_id,
    session_state=session_state_for_predict,  # ❌ Wrong parameter name
)
```

### Correct Implementation:
```python
# Import required types at the top of the file
from google.genai import types as genai_types

# In the handle_channel_message method, replace the broken call with:

# 1. Create proper Content format for the message
message_content = genai_types.Content(
    role='user',
    parts=[genai_types.Part(text=content)]
)

# 2. Update session state BEFORE calling runner
try:
    # Get or create the session
    session = await self.session_service.get_session(
        app_name="gemini-legion",
        user_id=sender_id,
        session_id=current_session_id
    )
    
    # Update session state with emotional and memory context
    session.state.update({
        "current_emotional_cue": emotional_cue,
        "conversation_history_cue": memory_cue
    })
    
    # Save the updated session state
    await self.session_service.save_session(session)
    
    logger.debug(f"Updated session state for {minion_id}: emotional_cue='{emotional_cue}', history_cue='{memory_cue[:60]}...'")
    
except Exception as e:
    logger.error(f"Failed to update session state for {minion_id}: {e}")
    # Continue with execution but log the issue

# 3. Call runner with correct parameters
agent_response_generator = runner.run_async(
    user_id=sender_id,
    session_id=current_session_id,
    new_message=message_content  # ✅ Correct parameter name and format
)
```

---

## 🔧 FIX #2: Correct Response Processing

**File:** `/gemini_legion_backend/core/application/services/minion_service_v2.py`
**Line:** ~583

### Current Broken Code:
```python
response_text = "".join(part.text for part in agent_response.parts if hasattr(part, 'text'))
#                                               ^^^^^^^^^^^^^^ Wrong variable name!
```

### Correct Implementation:
```python
response_text = "".join(part.text for part in final_agent_response_content.parts if hasattr(part, 'text'))
```

---

## 🔧 FIX #3: Improved Event Processing Loop

**File:** `/gemini_legion_backend/core/application/services/minion_service_v2.py`
**Lines:** ~575-590

### Enhanced Implementation:
```python
# The run_async method returns an async generator of Events
final_agent_response_content: Optional[genai_types.Content] = None
response_text: Optional[str] = None

async for event_obj in agent_response_generator:
    # Log event for debugging (can be removed in production)
    logger.debug(f"Received event from {minion_id}: type={type(event_obj).__name__}, final={event_obj.is_final_response()}")
    
    # Check for content in the event
    if event_obj.content and event_obj.content.parts:
        # Look for text parts
        text_parts = [part.text for part in event_obj.content.parts if hasattr(part, 'text') and part.text]
        if text_parts:
            final_agent_response_content = event_obj.content
            logger.debug(f"Found text content in event from {minion_id}: {text_parts[0][:50]}...")
    
    # Break on final response to avoid processing duplicate events
    if event_obj.is_final_response():
        logger.debug(f"Final response event received from {minion_id}")
        break

# Extract response text
if final_agent_response_content and final_agent_response_content.parts:
    text_parts = [part.text for part in final_agent_response_content.parts if hasattr(part, 'text') and part.text]
    response_text = "".join(text_parts)
    logger.info(f"Minion {minion_id} ({agent_instance.persona.name}) response: {response_text}")
else:
    logger.warning(f"Minion {minion_id} returned no text response from ADK runner")
    response_text = None
```

---

## 🔧 FIX #4: Session Service Verification

**File:** `/gemini_legion_backend/core/dependencies_v2.py`

### Required Verification:
Ensure the session service is properly configured:

```python
# Check that this exists and is properly configured:
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from ..config.settings import settings

# Verify DATABASE_URL is set for persistent sessions
if settings.DATABASE_URL:
    session_service = DatabaseSessionService(database_url=settings.DATABASE_URL)
else:
    # Fallback to in-memory for development
    session_service = InMemorySessionService()
    logger.warning("Using in-memory session service - sessions will be lost on restart")
```

### Update settings.py if needed:
```python
# In /gemini_legion_backend/config/settings.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # ADK Session Service Configuration
    DATABASE_URL: Optional[str] = None  # For persistent sessions
    
    class Config:
        env_file = ".env"
```

---

## 🔧 FIX #5: Import Statements

**File:** `/gemini_legion_backend/core/application/services/minion_service_v2.py`

### Required Imports:
Add these imports at the top of the file:

```python
from google.genai import types as genai_types
from google.adk.events import Event
from typing import Optional, Dict, Any, List, AsyncGenerator
```

---

## 🔧 FIX #6: Error Handling Enhancement

### Improved Error Handling:
```python
try:
    # Session state update and runner call (from fixes above)
    
    response_text = None
    final_agent_response_content = None
    
    async for event_obj in agent_response_generator:
        # ... event processing from Fix #3 ...
        
except Exception as e:
    logger.error(f"Error during ADK runner execution for minion {minion_id} (session {current_session_id}): {str(e)}", exc_info=True)
    
    # Provide fallback response to prevent silent failures
    response_text = f"[Error: {agent_instance.persona.name} encountered an issue processing your message]"
    
    # Emit error event for debugging
    if self.event_bus:
        await self.event_bus.emit(
            EventType.MINION_ERROR,
            data={
                "minion_id": minion_id,
                "error": str(e),
                "channel_id": channel_id,
                "message": content[:100]
            },
            source="minion_service:adk_runner_error"
        )
```

---

## 🔧 FIX #7: Session ID Management

### Ensure Proper Session ID Format:
```python
# In the handle_channel_message method, ensure session ID is properly formatted
current_session_id = f"channel_{channel_id}_minion_{minion_id}"

# Log for debugging
logger.debug(f"Using session ID: {current_session_id} for minion {minion_id} in channel {channel_id}")
```

---

## 🧪 TESTING THE FIXES

### 1. Test Basic Minion Response:
```python
# Create a simple test to verify the fixes
async def test_minion_response():
    # Spawn a minion
    # Create a channel  
    # Add minion to channel
    # Send a message
    # Verify response appears
```

### 2. Verify Session State Templating:
Check that the instruction templates in `ADKMinionAgent` are getting the placeholders filled:

```python
# In ADKMinionAgent.__init__(), verify this pattern works:
system_instruction = f"{base_instruction_text}\n\nYour current emotional disposition: {{current_emotional_cue}}\n\nConversation Context:\n{{conversation_history_cue}}"
```

### 3. Debug Session State:
Add logging to verify session state is being set correctly:

```python
# After updating session.state, log it:
logger.debug(f"Session state for {minion_id}: {session.state}")
```

---

## 🔄 EXPECTED BEHAVIOR AFTER FIXES

1. **No More TypeError:** The `Runner.run_async() got an unexpected keyword argument 'prompt'` error should be gone
2. **Minion Responses:** Minions should generate and return text responses to channel messages  
3. **Emotional Context:** Responses should reflect emotional state (verify by checking response tone)
4. **Memory Context:** Responses should reference conversation history when relevant
5. **Frontend Updates:** Responses should appear in the frontend chat interface
6. **No Silent Failures:** All errors should be logged and handled gracefully

---

## 🚨 CRITICAL NOTES

1. **Test Incrementally:** Apply fixes one at a time and test each one
2. **Check Logs:** Monitor backend logs carefully during testing
3. **Verify Session Service:** Ensure the session service is working before testing the runner
4. **Frontend Connectivity:** Confirm WebSocket events are reaching the frontend
5. **Memory Usage:** Monitor memory usage with the session service changes

---

## 🔮 NEXT STEPS AFTER BASIC FIXES

1. **Default Echo Minion Auto-Subscription:** Fix the auto-subscription logic
2. **Persistence:** Consider moving to `DatabaseSessionService` for production
3. **Performance Optimization:** Implement connection pooling and caching
4. **Error Recovery:** Add retry logic for transient ADK failures
5. **Tool Integration:** Verify MCP tools work properly with ADK

---

**Remember:** These fixes address the CORE issues preventing minion responses. Once these are working, investigate the echo minion subscription and frontend refresh issues as separate problems.**
