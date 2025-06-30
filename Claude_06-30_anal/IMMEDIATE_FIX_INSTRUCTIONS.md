# CRITICAL CODE FIXES REQUIRED

## IMMEDIATE FIX #1: Broken Agent Instantiation

**File**: `/gemini_legion_backend/core/application/services/minion_service_v2.py`
**Line**: 384

### Current BROKEN Code:
```python
async def _start_minion_agent(self, minion: Minion):
    """Start an agent for a minion"""
    try:
        ADKMinionAgent  # <- THIS IS BROKEN
        minion=minion,
        event_bus=self.event_bus,
        api_key=self.api_key
    )
```

### REQUIRED Fix:
```python
async def _start_minion_agent(self, minion: Minion):
    """Start an agent for a minion"""
    try:
        agent = ADKMinionAgent(  # <- ADD "agent = " and opening parenthesis
            minion=minion,
            event_bus=self.event_bus,
            api_key=self.api_key
        )
```

## Additional Issues Found

### Issue #2: Import Organization
The service file has some redundant/incomplete imports. Line 21-22 shows:
```python
from ...infrastructure.adk.agents.minion_agent_v2 import ADKMinionAgent
ADKMinionAgent  # <- Random line, should be removed
```

### Issue #3: Multiple References
Lines 58-59, 97-98, 105, 109 all have random `ADKMinionAgent` statements that should be removed.

### Issue #4: Missing Error Recovery
If agent initialization fails, the system doesn't gracefully handle it. Messages pile up with no response capability.

## Step-by-Step Fix Instructions

1. **Open** `/gemini_legion_backend/core/application/services/minion_service_v2.py`

2. **Fix Line 384** - Change:
   ```python
   ADKMinionAgent
   ```
   To:
   ```python
   agent = ADKMinionAgent(
   ```

3. **Remove spurious lines**:
   - Line 22: Delete standalone `ADKMinionAgent`
   - Line 58: Delete standalone `ADKMinionAgent`
   - Line 97: Delete standalone `ADKMinionAgent`
   - Line 105: Delete standalone `ADKMinionAgent`
   - Line 109: Delete standalone `ADKMinionAgent`

4. **Verify imports** at top of file are clean

5. **Test** by:
   - Restarting the backend
   - Checking logs for successful agent initialization
   - Sending a message in the frontend

## Expected Log Output After Fix

### Before (BROKEN):
```
2025-06-29 13:46:39,683 - ERROR - Failed to start agent for echo_prime: name 'emotional_engine' is not defined
```

### After (FIXED):
```
2025-06-29 13:46:39,683 - INFO - ADK Minion Agent initialized for echo_prime (Echo) with EmotionalEngine.
2025-06-29 13:46:39,684 - INFO - Created Runner for Echo
2025-06-29 13:46:39,684 - INFO - Started agent for Echo (echo_prime)
```

## Testing the Fix

1. **Restart Backend**:
   ```bash
   # Kill existing process
   # Then:
   cd /Users/ttig/projects/geminopus-2
   python3 -m gemini_legion_backend.main_v2
   ```

2. **Check Startup Logs** for successful agent initialization

3. **Test in Frontend**:
   - Open http://localhost:5173
   - Go to a channel
   - Send a message
   - You should see the Minion respond!

## Why This Happened

This appears to be a result of either:
1. **Incomplete refactoring** - Someone was updating the code and didn't finish
2. **Merge conflict resolution gone wrong** - Git merge might have corrupted the code
3. **Find/Replace error** - A bulk edit operation might have broken the syntax

The pattern of random `ADKMinionAgent` lines throughout the file suggests an editing mistake rather than intentional code.

## Prevention

1. **Use a linter** - This syntax error would be caught immediately
2. **Run tests** before committing
3. **Use version control properly** - Review diffs before committing
4. **Have a CI/CD pipeline** that catches syntax errors

---

This is literally a **one-character fix** (adding `agent = `) that will unblock the entire system!