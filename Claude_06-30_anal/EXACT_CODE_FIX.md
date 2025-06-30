# EXACT CODE CHANGES NEEDED

## File: `/gemini_legion_backend/core/application/services/minion_service_v2.py`

### Line 384 - CRITICAL FIX

**BEFORE (BROKEN):**
```python
async def _start_minion_agent(self, minion: Minion):
    """Start an agent for a minion"""
    try:
        ADKMinionAgent
        minion=minion,
        event_bus=self.event_bus,
        api_key=self.api_key
    )
```

**AFTER (FIXED):**
```python
async def _start_minion_agent(self, minion: Minion):
    """Start an agent for a minion"""
    try:
        agent = ADKMinionAgent(
            minion=minion,
            event_bus=self.event_bus,
            api_key=self.api_key
        )
```

### Additional Cleanup - Remove These Lines:

- **Line 22**: `ADKMinionAgent` (standalone, no purpose)
- **Line 58**: `ADKMinionAgent` (standalone, no purpose)
- **Line 97**: `ADKMinionAgent` (standalone, no purpose)
- **Line 105**: `ADKMinionAgent` (standalone, no purpose)
- **Line 109**: `ADKMinionAgent` (standalone, no purpose)

## Visual Diff

```diff
@@ -381,7 +381,7 @@ class MinionServiceV2:
     async def _start_minion_agent(self, minion: Minion):
         """Start an agent for a minion"""
         try:
-            ADKMinionAgent
+            agent = ADKMinionAgent(
             minion=minion,
             event_bus=self.event_bus,
             api_key=self.api_key
```

## How to Apply

### Option 1: Manual Edit
1. Open the file in your editor
2. Go to line 384
3. Change `ADKMinionAgent` to `agent = ADKMinionAgent(`
4. Save

### Option 2: Command Line
```bash
cd /Users/ttig/projects/geminopus-2
# Backup first
cp gemini_legion_backend/core/application/services/minion_service_v2.py gemini_legion_backend/core/application/services/minion_service_v2.py.backup

# Apply fix (be careful with this command)
sed -i '' '384s/ADKMinionAgent/agent = ADKMinionAgent(/' gemini_legion_backend/core/application/services/minion_service_v2.py
```

### Option 3: Git Patch
Create a file `fix.patch`:
```patch
--- a/gemini_legion_backend/core/application/services/minion_service_v2.py
+++ b/gemini_legion_backend/core/application/services/minion_service_v2.py
@@ -381,7 +381,7 @@ class MinionServiceV2:
     async def _start_minion_agent(self, minion: Minion):
         """Start an agent for a minion"""
         try:
-            ADKMinionAgent
+            agent = ADKMinionAgent(
             minion=minion,
             event_bus=self.event_bus,
             api_key=self.api_key
```

Then apply:
```bash
git apply fix.patch
```

## Verification

After applying the fix, check that the line now reads:
```python
agent = ADKMinionAgent(
```

## Test the Fix

1. Restart the backend:
```bash
# Kill the existing process first
pkill -f "python3 -m gemini_legion_backend.main_v2"

# Start fresh
python3 -m gemini_legion_backend.main_v2
```

2. Look for successful initialization in logs:
```
ADK Minion Agent initialized for echo_prime (Echo) with EmotionalEngine
Started agent for Echo (echo_prime)
```

3. Send a test message in the frontend - you should get a response!

---

**That's literally it. One line. `agent = ` is all that's missing.**