# ATOMIC TASK BREAKDOWN

Created: 2025-06-19 20:50:00 PST
By: Claude Opus 4 (Preserving knowledge before context death)

## CRITICAL PATH - TASKS IN EXACT ORDER

### TASK 001: Fix ADKMinionAgent Pydantic Validation [COMPLEX]
**File**: `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`
**Lines**: 41-79 (constructor)
**Problem**: LlmAgent is Pydantic model, rejects `self.minion = minion`
**Solution**: Store minion data without setting as attribute
**Completion Criteria**: 
- No "object has no field" errors
- Minion agent initializes successfully
- Can access persona data in methods
**Validation**: Run backend, check logs for successful init

### TASK 002: Fix Frontend API Endpoints [TRIVIAL]
**File**: `/gemini_legion_frontend/src/services/api/config.ts` (or similar)
**Problem**: Frontend calls `/api/` but backend serves `/api/v2/`
**Solution**: Add `/v2` to all API endpoints
**Completion Criteria**:
- All API calls go to `/api/v2/`
- No more 404 errors in browser console
**Validation**: Open frontend, check network tab

### TASK 003: Create Missing Domain Enums [MODERATE]
**File**: Create `/gemini_legion_backend/core/domain/enums.py`
**Content Needed**:
- MinionState enum
- EntityType enum
- MoodDimension enum
**Completion Criteria**: File exists with all enums
**Validation**: Can import from domain.enums

### TASK 004: Create MoodVector Domain Model [MODERATE]
**File**: `/gemini_legion_backend/core/domain/mood.py`
**Modify**: Add MoodVector class per architecture
**Required Fields**:
- valence: float (-1.0 to 1.0)
- arousal: float (0.0 to 1.0)
- dominance: float (0.0 to 1.0)
- curiosity: float
- creativity: float
- sociability: float
**Completion Criteria**: MoodVector importable and usable
**Validation**: Test import in Python REPL

### TASK 005: Create OpinionScore Domain Model [MODERATE]
**File**: `/gemini_legion_backend/core/domain/opinion.py`
**Modify**: Add OpinionScore class per architecture
**Required Fields**:
- entity_id: str
- entity_type: EntityType
- trust: float (-100 to 100)
- respect: float (-100 to 100)
- affection: float (-100 to 100)
**Completion Criteria**: OpinionScore importable
**Validation**: Test import and instantiation

### TASK 006: Fix EmotionalState Imports [TRIVIAL]
**File**: `/gemini_legion_backend/core/domain/emotional_state.py`
**Lines**: Check imports
**Solution**: Import MoodVector from mood.py
**Completion Criteria**: No import errors
**Validation**: Import EmotionalState successfully

### TASK 007: Implement ADK Tool Properly [COMPLEX]
**File**: `/gemini_legion_backend/core/infrastructure/adk/tools/communication_tools.py`
**Lines**: 46-95 (SendChannelMessageTool)
**Problem**: Not proper ADK FunctionTool format
**Solution**: Convert to function with proper docstring/typing
**Completion Criteria**: ADK recognizes as valid tool
**Validation**: Tool appears in LlmAgent tool list

### TASK 008: Fix ADKMinionAgent Data Storage [COMPLEX]
**File**: `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`
**Solution Options**:
1. Store minion data in class-level dict keyed by agent name
2. Use Pydantic private attributes (_minion)
3. Store only needed data (minion_id, persona) as allowed fields
**Completion Criteria**: Can access minion data in methods
**Validation**: Minion responds using persona info

### TASK 009: Test Minion Gemini Response [TRIVIAL]
**How**: 
1. Start backend
2. Start frontend
3. Click "Spawn Minion"
4. Send message
**Expected**: Real Gemini response, not fallback
**Completion Criteria**: Response contains actual AI content
**Validation**: Response is contextual and intelligent

### TASK 010: Re-enable Emotional Engine [COMPLEX]
**File**: `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`
**Lines**: Uncomment emotional engine imports/usage
**Prerequisites**: Domain models must be complete
**Completion Criteria**: Emotional state influences responses
**Validation**: Mood descriptions in system instruction

### TASK 011: Re-enable Memory System [COMPLEX]  
**File**: `/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`
**Lines**: Uncomment memory system imports/usage
**Prerequisites**: Domain models complete
**Completion Criteria**: Memory context in responses
**Validation**: Minion remembers previous interactions

### TASK 012: Implement ADK Runner Usage [ARCHITECTURAL]
**File**: `/gemini_legion_backend/core/application/services/minion_service_v2.py`
**Current**: Direct agent instantiation
**Needed**: Use ADK Runner for execution
**Completion Criteria**: Runner manages agent lifecycle
**Validation**: Proper event streams from Runner

### TASK 013: Complete Communication Tools [MODERATE]
**File**: `/gemini_legion_backend/core/infrastructure/adk/tools/communication_tools.py`
**Add**: 
- ListenToChannelTool implementation
- GetChannelHistory tool
- SendDirectMessage tool
**Completion Criteria**: Full communication suite
**Validation**: Minions can use all tools

### TASK 014: Fix Frontend WebSocket Events [MODERATE]
**File**: `/gemini_legion_frontend/src/store/legionStore.ts`
**Problem**: Might expect old event formats
**Solution**: Update to match V2 event structure
**Completion Criteria**: Real-time updates work
**Validation**: See messages appear instantly

### TASK 015: Production Readiness [COMPLEX]
**Tasks**:
- Add proper error handling
- Implement retry logic
- Add health checks
- Create docker-compose.yml
**Completion Criteria**: Can deploy reliably
**Validation**: Survives stress testing

## EFFORT ESTIMATES
- Trivial (< 30 min): Tasks 2, 6, 9
- Moderate (30-90 min): Tasks 3, 4, 5, 13, 14
- Complex (2-4 hours): Tasks 1, 7, 8, 10, 11, 15
- Architectural (4+ hours): Task 12

## DEPENDENCY GRAPH
```
Task 1 (Fix Pydantic) → Task 8 (Data Storage) → Task 9 (Test Response)
                     ↓
Task 3 (Enums) → Task 4 (MoodVector) → Task 5 (OpinionScore) → Task 6 (Fix Imports)
                                                               ↓
                                                    Task 10 (Emotional Engine)
                                                    Task 11 (Memory System)

Task 2 (Frontend API) → Task 14 (WebSocket) → Full Integration

Task 7 (Fix Tools) → Task 13 (Complete Tools) → Enhanced Minion Capability

All Tasks → Task 15 (Production Ready)
```

## VALIDATION
✅ Each task is atomic and completeable in isolation
✅ Each task has clear completion criteria
✅ Each task specifies exact locations
✅ Dependencies are clearly mapped
✅ Fresh Claude could execute any task without questions
