# CRITICAL UPDATE: Different Error Found!

## The Real Issue

After deeper investigation, the issue is **NOT** in `minion_service_v2.py` as initially thought. That file is actually fine!

The real error is in `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`

### Line 150 - The Actual Bug

```python
@staticmethod
def _build_base_instruction(persona: MinionPersona) -> str:
    """Builds the static part of the system instruction with persona."""
    instruction = f"""You are {persona.name}, ..."""
    
    # Add emotional context if available
    if emotional_engine:  # <-- THIS IS THE BUG! 'emotional_engine' is not defined
        # TODO: Add emotional state to instruction once engine is integrated
        pass
        
    return instruction
```

## The Problem

In a `@staticmethod` method, there's no access to instance variables. The code references `emotional_engine` which doesn't exist in this scope, causing:

```
Failed to start agent for echo_prime: name 'emotional_engine' is not defined
```

## The Fix

### Option 1: Remove the broken code (Recommended)
```python
# Add emotional context if available
# if emotional_engine:  # <-- Comment out or remove
#     # TODO: Add emotional state to instruction once engine is integrated
#     pass
```

### Option 2: Fix the logic
Since it's a static method and the comment says "TODO", just remove the if statement entirely.

## Updated Fix Instructions

1. Open `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`
2. Go to line 150
3. Comment out or delete the line: `if emotional_engine:`
4. Save and restart

## Why This Happened

Someone added placeholder code for future emotional context integration but made a scope error - referencing a variable that doesn't exist in a static method.

## Verification

After fixing, the agents should initialize without the "name 'emotional_engine' is not defined" error.

---

**My apologies for the initial misdiagnosis! The syntax in minion_service_v2.py is actually correct. The error is in the minion_agent_v2.py file.**