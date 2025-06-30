# Geminopus-2 Critical Issues Analysis
## Investigation Report - June 30, 2025

**TL;DR: The core issue is incorrect ADK Runner.run_async() parameter usage, along with several implementation bugs that prevent minions from responding to messages. The architecture is sound but the execution has deviated from ADK best practices.**

---

## 🔥 CRITICAL ERROR #1: Runner.run_async() Incorrect Parameters

**Location:** `/gemini_legion_backend/core/application/services/minion_service_v2.py:563`

**Current Broken Code:**
```python
agent_response_generator = runner.run_async(
    prompt=content,  # ❌ WRONG! 'prompt' is not a valid parameter
    session_id=current_session_id,
    user_id=sender_id,
    session_state=session_state_for_predict,  # ❌ WRONG! 'session_state' is not a valid parameter
)
```

**Correct ADK Usage:**
```python
# Create proper content format
from google.genai import types as genai_types

message_content = genai_types.Content(
    role='user', 
    parts=[genai_types.Part(text=content)]
)

agent_response_generator = runner.run_async(
    user_id=sender_id,
    session_id=current_session_id,
    new_message=message_content,  # ✅ Correct parameter name
    # run_config=run_config  # Optional, for streaming etc.
)
```

**Impact:** This is the **PRIMARY CAUSE** of the error Steven is seeing. The TypeError breaks all minion responses.

---

## 🐛 CRITICAL ERROR #2: Variable Name Bug

**Location:** `/gemini_legion_backend/core/application/services/minion_service_v2.py:583`

**Current Broken Code:**
```python
if final_agent_response_content and final_agent_response_content.parts:
    # Assuming the response is text and in the first part
    response_text = "".join(part.text for part in agent_response.parts if hasattr(part, 'text'))
    #                                                   ^^^^^^^^^^^^^^
    #                                                   WRONG VARIABLE!
```

**Fix:**
```python
response_text = "".join(part.text for part in final_agent_response_content.parts if hasattr(part, 'text'))
```

**Impact:** Even if the Runner call was fixed, this bug would prevent response text extraction.

---

## 🏗️ ARCHITECTURAL ISSUE #3: Session State Management

**Problem:** The code attempts to pass `session_state` as a parameter to `runner.run_async()`, but ADK manages session state through the `SessionService` and `session.state` dictionary.

**Current Misunderstanding:**
The code tries to manually inject emotional and memory cues via a `session_state` parameter, but ADK doesn't work this way.

**Correct ADK Pattern:**
1. Update `session.state` through the `SessionService` BEFORE calling `runner.run_async()`
2. The `LlmAgent` instruction template (with `{{current_emotional_cue}}` placeholders) gets filled from `session.state`
3. The Runner automatically handles this templating

**Required Implementation:**
```python
# Get or create session
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

# Save session state
await self.session_service.save_session(session)

# Now call runner with correct parameters
agent_response_generator = runner.run_async(
    user_id=sender_id,
    session_id=current_session_id,
    new_message=message_content
)
```

---

## 🔄 FRONTEND-BACKEND CONNECTIVITY STATUS

**✅ GOOD NEWS:** Frontend API calls are correctly configured for V2 endpoints.

**Evidence:**
- Frontend config uses `/api/v2/` paths consistently
- Channel API: `/api/v2/channels/{id}/messages`
- Minion API: `/api/v2/minions/`
- No V1/V2 endpoint mismatch found

**The issue is NOT frontend-backend API path misalignment.**

---

## 📊 SESSION SERVICE INVESTIGATION NEEDED

**Question:** Is the `SessionService` properly initialized and configured?

**Location to Check:** `/gemini_legion_backend/core/dependencies_v2.py`

**Required Verification:**
1. Is `DatabaseSessionService` being used with proper `DATABASE_URL`?
2. Are sessions being created/retrieved correctly?
3. Is session state templating working in `LlmAgent` instructions?

---

## 🎭 ADKMinionAgent Implementation Assessment

**✅ GOOD NEWS:** The `ADKMinionAgent` implementation appears architecturally sound:

1. **Proper Inheritance:** Extends `LlmAgent` correctly
2. **Instruction Templating:** Uses `{{current_emotional_cue}}` and `{{conversation_history_cue}}` placeholders
3. **Tool Integration:** Includes communication tools via `ADKCommunicationKit`
4. **Emotional Engine:** Integrates `EmotionalEngineV2`
5. **Memory System:** Includes `MemorySystemV2`

**Location:** `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`

---

## 🔧 EVENT BUS AND WEBSOCKET STATUS

**Requires Investigation:** The custom `GeminiEventBus` and WebSocket integration.

**Potential Issue:** Even if minions start responding via the fixed Runner calls, the responses might not reach the frontend if:
1. Event bus message routing is broken
2. WebSocket event bridge has issues
3. Channel message emission is faulty

**Files to Investigate:**
- `/gemini_legion_backend/core/infrastructure/events/event_bus_v2.py`
- `/gemini_legion_backend/api/websocket/event_bridge.py`

---

## 🚨 DEFAULT ECHO MINION SUBSCRIPTION ISSUE

**Steven's Report:** "Default echo minion doesn't automatically subscribe to any chat channels anymore"

**Investigation Needed:**
1. Check minion auto-subscription logic in channel creation
2. Verify echo minion spawn and channel membership
3. Examine channel member management in V2 API

**Likely Location:** Channel service and minion management integration.

---

## 💾 MEMORY AND PERSISTENCE CONCERNS

**Current State:** V2 backend uses in-memory repositories:
- `MinionRepositoryMemory`
- `ChannelRepositoryMemory`
- etc.

**Impact:** All state lost on restart, which could affect:
1. Channel memberships
2. Minion-channel associations
3. Conversation history
4. Emotional states

**This explains:** Why subscriptions and associations might be "lost" and need manual re-setup.

---

## 🎯 IMMEDIATE ACTION PLAN

### Priority 1: Fix Runner Call (CRITICAL)
1. Fix `runner.run_async()` parameters in `minion_service_v2.py`
2. Fix variable name bug in response processing
3. Implement proper session state management

### Priority 2: Verify Session Service
1. Check `SessionService` initialization in dependencies
2. Verify session state templating works
3. Test emotional/memory cue injection

### Priority 3: Test End-to-End Flow
1. Verify minion responses reach event bus
2. Check WebSocket message propagation
3. Confirm frontend receives responses

### Priority 4: Fix Default Subscriptions
1. Investigate auto-subscription logic
2. Fix echo minion default behavior
3. Verify channel membership persistence

---

## 📋 TESTING CHECKLIST

After implementing fixes:

- [ ] Minion spawning works without errors
- [ ] Channel message sending doesn't crash backend
- [ ] Minions generate responses to messages
- [ ] Responses appear in frontend chat UI
- [ ] Default echo minion auto-subscribes to new channels
- [ ] Page refresh doesn't lose minion responses
- [ ] Emotional cues are properly injected into responses
- [ ] Memory context influences minion behavior

---

## 🔮 ADDITIONAL INVESTIGATION AREAS

1. **Tool Integration:** Are MCP tools properly integrated with ADK?
2. **Callback Implementation:** Are emotional/memory callbacks working?
3. **Error Handling:** Comprehensive error recovery for ADK failures
4. **Performance:** ADK runner efficiency and resource usage
5. **Scalability:** Multiple concurrent minion conversations

---

**Bottom Line:** The architecture is solid, but the implementation has deviated from ADK best practices. The primary issue is incorrect Runner usage, compounded by variable bugs and session state mismanagement. Once these core issues are fixed, the system should function as designed.**
