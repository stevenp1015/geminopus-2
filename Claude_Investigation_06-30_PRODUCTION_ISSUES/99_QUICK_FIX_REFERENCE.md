# QUICK FIX REFERENCE - Exact Code Changes Needed

**Use this as your copy-paste reference for the 3 critical fixes.**

---

## Fix #1: WebSocket Event Name (CRITICAL)

**File:** `/Users/ttig/projects/geminopus-2/gemini_legion_backend/api/websocket/event_bridge.py`  
**Line:** 116  
**Function:** `_handle_channel_message`

**FIND THIS CODE:**
```python
# Emit to all subscribers
for sid in subscribers:
    await self.sio.emit("message", ws_message, to=sid)
```

**CHANGE TO:**
```python
# Emit to all subscribers  
for sid in subscribers:
    await self.sio.emit("message_sent", ws_message, to=sid)
```

**Why:** Frontend listens for "message_sent" but backend emits "message"

---

## Fix #2: Minion Creation Endpoint (CRITICAL)

**File:** `/Users/ttig/projects/geminopus-2/gemini_legion_backend/api/rest/endpoints/minions_v2.py`  
**Line:** 133  
**Function:** `spawn_minion`

**FIND THIS CODE:**
```python
@router.post("/spawn", response_model=MinionResponse)
async def spawn_minion(
```

**CHANGE TO:**  
```python
@router.post("/", response_model=MinionResponse) 
async def spawn_minion(
```

**Why:** Frontend calls POST /api/v2/minions/ but backend serves /api/v2/minions/spawn

---

## Fix #3A: Schema Field Name (HIGH)

**File:** `/Users/ttig/projects/geminopus-2/gemini_legion_backend/api/rest/schemas.py`  
**Line:** 64  
**Class:** `CreateMinionRequest`

**FIND THIS CODE:**
```python
class CreateMinionRequest(BaseModel):
    """Request to create a new minion"""
    name: str = Field(..., min_length=1, max_length=50)
    personality: str = Field(..., min_length=1, max_length=200)
    quirks: List[str] = Field(default_factory=list, max_items=10)
```

**CHANGE TO:**
```python
class CreateMinionRequest(BaseModel):
    """Request to create a new minion"""
    name: str = Field(..., min_length=1, max_length=50)
    base_personality: str = Field(..., min_length=1, max_length=200)
    quirks: List[str] = Field(default_factory=list, max_items=10)
```

**Why:** Frontend sends "base_personality" but backend expects "personality"

---

## Fix #3B: Update Endpoint Mapping (HIGH)

**File:** `/Users/ttig/projects/geminopus-2/gemini_legion_backend/api/rest/endpoints/minions_v2.py`  
**Line:** 148  
**Function:** `spawn_minion`

**FIND THIS CODE:**
```python
minion_data = await minion_service.spawn_minion(
    minion_id=agent_name,
    name=request.name,
    base_personality=request.personality,  # Map 'personality' to 'base_personality'
    quirks=request.quirks,
```

**CHANGE TO:**
```python
minion_data = await minion_service.spawn_minion(
    minion_id=agent_name,  
    name=request.name,
    base_personality=request.base_personality,  # Direct mapping
    quirks=request.quirks,
```

**Why:** Now that schema uses base_personality, we can map directly

---

## Test Commands After Fixes

```bash
# 1. Restart backend
cd /Users/ttig/projects/geminopus-2
python -m gemini_legion_backend.main_v2

# 2. Open frontend  
# Navigate to http://localhost:5173

# 3. Test chat
# Send message in general channel → should appear immediately

# 4. Test minion creation
# Click + button → create minion → should appear without refresh

# 5. Test minion response  
# Send "Hello minions!" → should see responses from all minions
```

---

## Expected Results After Fixes

### ✅ Chat Functionality
- Messages appear instantly in UI
- Minions respond with personality  
- No refresh needed for new messages
- WebSocket stays connected

### ✅ Minion Management
- Create minion button works
- New minions appear immediately  
- Personality data flows correctly
- Status updates in real-time

### ✅ Real-time Features  
- Channel subscriptions work
- Message broadcasting works
- Event flow is seamless
- No duplicate or missing events

---

## If Something Still Doesn't Work

### Check Browser Console
```javascript
// Look for these events being received:
// "message_sent" ✅ 
// "minion_spawned" ✅
// "channel_event" ✅

// NOT these (old event names):
// "message" ❌
// "minion_created" ❌  
```

### Check Backend Logs
```bash
# Look for these log messages:
# "Broadcast message to X clients for channel Y" ✅
# "Minion spawned successfully" ✅  
# "WebSocket client connected" ✅

# If you see errors about:
# "AttributeError: '_persona'" → Check _persona vs persona in agent files
# "404 Not Found" → Double-check endpoint changes
```

### Verify WebSocket Connection
```javascript
// In browser console:
console.log('WebSocket connected:', !!window.io && window.io.connected);
```

---

## Notes

- **Backup First:** Consider backing up the files before making changes
- **Test Incrementally:** Apply Fix #1, test chat, then Fix #2, test minion creation, etc.  
- **Check Dependencies:** Make sure both backend and frontend are running
- **Clear Cache:** Try hard refresh (Ctrl+F5) if frontend doesn't update

**Total time to implement: 10-15 minutes**  
**Total time to test: 5-10 minutes**  
**Expected result: Fully functional chat system with intelligent minion responses**