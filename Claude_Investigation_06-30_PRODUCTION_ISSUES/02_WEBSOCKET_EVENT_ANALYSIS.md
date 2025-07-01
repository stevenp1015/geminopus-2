# WebSocket Event System Analysis - Critical Findings

**Date:** June 30, 2025  
**Analysis:** WebSocket Event Bridge Deep Dive  
**Status:** CRITICAL EVENT MISMATCH FOUND

## Critical Discovery: WebSocket Event Name Mismatch

### The Smoking Gun 🔥

**Backend WebSocket Bridge:**
```python
# In /gemini_legion_backend/api/websocket/event_bridge.py (Line ~116)
async def _handle_channel_message(self, event: Event):
    # ... processing logic ...
    
    # Emit to all subscribers  
    for sid in subscribers:
        await self.sio.emit("message", ws_message, to=sid)  # ❌ Emits "message"
        
    logger.debug(f"Broadcast message to {len(subscribers)} clients for channel {channel_id}")
```

**Frontend WebSocket Listener:**
```typescript
// In /gemini_legion_frontend/src/hooks/useWebSocket.ts (Line ~32)
const handleMessageSent = (data: MessageSentPayload) => {
  console.log('[useWebSocket] Received "message_sent" event:', data);
  // ... handle message logic ...
};
websocket.on('message_sent', handleMessageSent);  // ❌ Listening for "message_sent"
```

**Impact:** ALL CHAT MESSAGES ARE LOST! Backend sends chat messages via `"message"` events, but frontend only listens for `"message_sent"` events. This explains why:
- ✅ Messages send successfully (backend receives and processes them)
- ✅ Minions generate responses (ADK/LLM integration works)  
- ❌ Messages never appear in frontend UI (event mismatch)
- ❌ Chat appears completely broken to users

---

## WebSocket Event Flow Analysis

### Current Backend Event Bridge Configuration

```python
# Event subscriptions (✅ Correctly set up)
self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_event)
# ... other subscriptions

# Backend emits these WebSocket events:
- "message"          # ❌ Should be "message_sent"
- "channel_event"    # ✅ Frontend listens for this
- "minion_spawned"   # ❌ Frontend may not listen for this
- "task_event"       # ✅ Frontend has handler for this
```

### Frontend Event Listeners

```typescript
// In /gemini_legion_frontend/src/hooks/useWebSocket.ts
websocket.on('message_sent', handleMessageSent);        // ❌ Backend doesn't emit this
websocket.on('minion_status_changed', handleMinion);    // ❌ Backend emits different names

// In /gemini_legion_frontend/src/store/legionStore.ts  
ws.on('minion_spawned', handleMinionSpawned);          // ✅ May match backend
ws.on('channel_updated', handleChannelUpdate);         // ❌ Backend emits "channel_event"
ws.on('channel_member_added', handleMemberAdded);      // ❌ Backend emits "channel_event"
```

### Event Name Standardization Required

**Backend Emits → Frontend Expects**
- `"message"` → `"message_sent"` ❌
- `"channel_event"` → `"channel_updated"`, `"channel_member_added"`, etc. ❌  
- `"minion_spawned"` → `"minion_spawned"` ✅
- `"task_event"` → `"task_event"` ✅

---

## Channel Subscription Flow Analysis

### Frontend Channel Subscription (✅ Correct)
```typescript
// In /gemini_legion_frontend/src/store/chatStore.ts
websocket.emit('subscribe_channel', { channel_id: channelId });
```

### Backend Subscription Handler (✅ Correct)
```python
# In /gemini_legion_backend/main_v2.py
@sio.on("subscribe_channel")
async def handle_subscribe_channel(sid, data):
    channel_id = data.get("channel_id")
    if container.websocket_bridge:
        await container.websocket_bridge.subscribe_to_channel(sid, channel_id)
```

### Subscription Storage (✅ Correct)
```python
# In /gemini_legion_backend/api/websocket/event_bridge.py
self.channel_subscriptions: Dict[str, Set[str]] = {}  # channel_id -> set of sids
```

**Subscription Logic Appears Sound:** The issue is NOT subscription management, it's the event name mismatch preventing message delivery.

---

## Message Flow Trace (Actual vs Expected)

### Actual Flow (Currently Broken)
1. ✅ User sends message via frontend → `POST /api/v2/channels/{id}/messages`
2. ✅ Backend channel service receives message → Stores in memory  
3. ✅ Backend emits `EventType.CHANNEL_MESSAGE` on event bus
4. ✅ WebSocket bridge receives event → Processes for subscribers
5. ❌ **Bridge emits `"message"` event** → Frontend not listening for this
6. ❌ Frontend UI never updates → Chat appears broken

### Expected Flow (How It Should Work)
1. ✅ User sends message via frontend → `POST /api/v2/channels/{id}/messages`
2. ✅ Backend channel service receives message → Stores in memory
3. ✅ Backend emits `EventType.CHANNEL_MESSAGE` on event bus  
4. ✅ WebSocket bridge receives event → Processes for subscribers
5. ✅ **Bridge emits `"message_sent"` event** → Frontend receives
6. ✅ Frontend UI updates with new message → Chat works

### Minion Response Flow (Also Broken)
1. ✅ Minion processes message via ADK → Generates response
2. ✅ Minion service emits response to event bus
3. ✅ WebSocket bridge processes response
4. ❌ **Bridge emits `"message"` event** → Frontend misses minion responses
5. ❌ Minion responses never appear in UI → Appears like minions aren't responding

---

## Fix Priority Matrix

### 🔴 CRITICAL (Immediate Fix Required)
1. **Change backend event name:** `"message"` → `"message_sent"`
2. **Align channel events:** Map backend `"channel_event"` to specific frontend events
3. **Test message round-trip:** User message → minion response → UI display

### 🟡 HIGH (Next 24 Hours)
1. **Standardize all event names** between backend and frontend
2. **Add event debugging** to see what events are actually being emitted
3. **Implement missing events** like minion auto-subscription

### 🟢 MEDIUM (Following Week)
1. **Create event specification document** to prevent future mismatches
2. **Add WebSocket event testing** to catch these issues in development  
3. **Implement event versioning** for backward compatibility

---

## Immediate Action Plan

### Step 1: Quick Fix (30 minutes)
```python
# In /gemini_legion_backend/api/websocket/event_bridge.py
# Change line ~116:
await self.sio.emit("message_sent", ws_message, to=sid)  # Fix event name
```

### Step 2: Test & Verify (15 minutes)  
1. Spawn a minion
2. Send a message in a channel
3. Verify message appears in frontend UI
4. Check if minion responds and response appears

### Step 3: Full Event Audit (2 hours)
1. Document all backend emitted events
2. Document all frontend listened events  
3. Create mapping table and fix all mismatches

**Steven: This single event name change should immediately restore chat functionality. The core architecture is solid, just a naming convention issue preventing communication.**

---

*Continuing analysis in next document...*