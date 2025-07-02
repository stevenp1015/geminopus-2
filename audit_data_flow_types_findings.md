# Data Flow & Type Consistency Audit

This document traces critical data flows and analyzes type consistency between frontend, API, backend services, and domain models.

## Critical User Action: Spawning a Minion

1.  **Frontend (UI Interaction):** User fills a form in `MinionConfig.tsx` (assumption).
    *   **Fields (Expected by `legionStore.ts` `spawnMinion` action):** `minion_id`, `name`, `base_personality`, `quirks`, `catchphrases`, `expertise_areas`, `model_name`, `allowed_tools`.
    *   **Types:** Mostly strings, arrays of strings.

2.  **Frontend (Zustand Store - `legionStore.ts`):** `spawnMinion` action.
    *   Calls `minionApi.spawnMinion(payload)`.
    *   **Payload to API (`SpawnMinionPayload` in `minionApi.ts`):** Matches the fields above.
    *   **Types:** Consistent with form.

3.  **Frontend (API Service - `minionApi.ts`):** `spawnMinion` function.
    *   Makes POST request to `/api/v2/minions/spawn`.
    *   **Request Body Sent:** JSON object of `SpawnMinionPayload`.
    *   **Types:** Consistent.

4.  **Backend (API Endpoint - `gemini_legion_backend/api/rest/endpoints/minion_endpoints.py`):** `spawn_minion_endpoint`.
    *   **Path:** `@router.post("/spawn", response_model=MinionResponse)`
    *   **Request Body Received (`payload: SpawnMinionRequestSchema`):**
        *   `minion_id: str`
        *   `name: str`
        *   `base_personality: str`
        *   `quirks: List[str]`
        *   `catchphrases: Optional[List[str]] = None`
        *   `expertise_areas: Optional[List[str]] = None`
        *   `model_name: Optional[str] = "gemini-1.5-flash"` (Note: Ideal architecture and `minion_service_v2.py` use `gemini-2.5-flash` or `gemini-2.0-flash` as default, `minion_agent_v2.py` uses `gemini-1.0-pro`) - **MINOR INCONSISTENCY (Default Model Name)**
        *   `allowed_tools: Optional[List[str]] = None`
    *   **Types:** Consistent with frontend.

5.  **Backend (Application Service - `MinionServiceV2.spawn_minion`):**
    *   **Parameters received:** `minion_id`, `name`, `base_personality`, `quirks`, `catchphrases`, `expertise_areas`, `model_name`, `allowed_tools`.
    *   **Types:** Consistent.
    *   **Logic:**
        *   Creates `MinionPersona` domain object.
        *   Creates `EmotionalState` domain object.
        *   Creates `Minion` domain object.
        *   Saves to `minion_repo`.
        *   Calls `_start_minion_agent`.
        *   Emits `MINION_SPAWNED` event with `self._minion_to_dict(minion)`.

6.  **Backend (Domain Model - `Minion`, `MinionPersona`, `EmotionalState`):**
    *   `MinionPersona` fields match incoming data. `model_name` defaults to "gemini-1.0-pro" if not provided to constructor, but `spawn_minion_endpoint` schema defaults to "gemini-1.5-flash" and `MinionServiceV2.spawn_minion` defaults to "gemini-2.5-flash". This is a chain of defaults. The API request schema default will likely take precedence if frontend sends `undefined`.
    *   `EmotionalState` initialized with default mood.
    *   `Minion` created with these objects.
    *   **Types:** Internally consistent.

7.  **Backend (ADK Agent - `ADKMinionAgent.__init__`):**
    *   Receives `Minion` object.
    *   Accesses `minion.persona.model_name`, `minion.persona.name`, etc. to configure `LlmAgent`.
    *   **Types:** Consistent.

**Overall Type Consistency (Spawning):** Good. Minor inconsistency in default model names across layers, but API payload would override.

## Critical User Action: Sending a Message (User to Minion)

1.  **Frontend (UI Interaction - `ChatInput.tsx`):** User types message.
    *   **Data:** `channelId: string`, `messageContent: string`.

2.  **Frontend (Zustand Store - `chatStore.ts`):** `sendMessage` action.
    *   Calls `channelApi.sendMessage(channelId, content)`.
    *   **Payload to API (`SendMessagePayload` in `channelApi.ts`):** `{ content: string }`. (Note: `sender_id` is not sent; backend infers from auth or defaults to "USER").
    *   **Types:** Consistent.

3.  **Frontend (API Service - `channelApi.ts`):** `sendMessage` function.
    *   Makes POST request to `/api/v2/channels/{channel_id}/messages`.
    *   **Request Body Sent:** JSON object `{ content: string }`.
    *   **Types:** Consistent.

4.  **Backend (API Endpoint - `gemini_legion_backend/api/rest/endpoints/channel_endpoints.py`):** `send_message_to_channel_endpoint`.
    *   **Path:** `@router.post("/{channel_id}/messages", response_model=MessageResponse)`
    *   **Request Body Received (`payload: MessageCreateSchema`):**
        *   `content: str`
        *   `sender_id: Optional[str] = "USER"` (Defaults to "USER")
    *   **Types:** Consistent.

5.  **Backend (Application Service - `ChannelServiceV2.add_message_to_channel`):**
    *   **Parameters received:** `channel_id`, `content`, `sender_id`.
    *   **Types:** Consistent.
    *   **Logic:**
        *   Creates `Message` domain object.
        *   Saves to `message_repo`.
        *   Emits `CHANNEL_MESSAGE` event with `message.to_dict()`.

6.  **Backend (Event Bus & `MinionServiceV2._handle_channel_message`):**
    *   `MinionServiceV2` receives `CHANNEL_MESSAGE` event.
    *   **Event Data Parsed:** `channel_id`, `sender_id`, `content`.
    *   **Types:** Consistent.
    *   **Logic (Key Part for Data Flow to ADK):**
        *   `current_session_id = f"channel_{channel_id}_minion_{minion_id}"`
        *   `emotional_cue`, `memory_cue` prepared (currently placeholders or simple).
        *   `session_state_for_predict` (which becomes `session.state` after `create_session`): `{"current_emotional_cue": string, "conversation_history_cue": string}`.
        *   `message_content = genai_types.Content(role='user', parts=[genai_types.Part(text=content)])`.
        *   Calls `runner.run_async(user_id=sender_id, session_id=current_session_id, new_message=message_content)`. (Or `predict` if that's fixed).

7.  **Backend (ADK Agent - `ADKMinionAgent` via Runner):**
    *   The `instruction` for `LlmAgent` is templated: `Your current emotional state is: {current_emotional_cue}. Conversation history: {conversation_history_cue}. User says: {user_query}` (Conceptual, actual template might vary but should use these).
    *   ADK framework passes `new_message.parts[0].text` (the user's message content) into the LLM prompt, likely as `user_query` or similar.
    *   `Session.state` variables (`current_emotional_cue`, `conversation_history_cue`) are interpolated into the instruction string by ADK if templated.
    *   **Type Check:** `content` (user message) is `str`. `current_emotional_cue` and `conversation_history_cue` from `Session.state` are `str`. All consistent for LLM prompt.

8.  **Backend (Minion Response via Event Bus to Frontend):**
    *   `MinionServiceV2` gets response from Runner, emits `CHANNEL_MESSAGE` with minion's response.
    *   **Payload:** `channel_id`, `sender_id` (minion's ID), `content` (minion's text).
    *   **Types:** Consistent.

**Overall Type Consistency (Sending Message):** Good. The flow of `content` string and contextual cues (as strings) into the ADK agent prompt seems compatible.

## WebSocket Event: `MINION_SPAWNED`

1.  **Backend (`MinionServiceV2.spawn_minion`):**
    *   Emits `EventType.MINION_SPAWNED`.
    *   Data: `{"minion": self._minion_to_dict(minion)}`.
    *   `_minion_to_dict` creates a structure compatible with frontend's `MinionType`.
        *   `minion_id: str`
        *   `status: str` ("active", "error", etc.)
        *   `creation_date: str` (ISO format)
        *   `persona: MinionPersonaResponseSchema` (which matches frontend's `MinionPersonaType`)
        *   `emotional_state: EmotionalStateResponseSchema` (which matches frontend's `EmotionalStateType`)

2.  **Backend (`WebSocketEventBridge`):** Relays this event and data to connected frontend clients.

3.  **Frontend (`legionStore.ts`):** Handles `MINION_SPAWNED` WebSocket event.
    *   **Expected Payload Structure (`MinionType` from `src/types/index.ts`):**
        ```typescript
        export interface MinionType {
          minion_id: string;
          // name: string; // Name is now nested under persona
          status: 'active' | 'inactive' | 'processing' | 'error' | 'idle';
          creation_date: string; // ISO date string
          persona: MinionPersonaType;
          emotional_state: EmotionalStateType;
          current_task?: any; // Consider defining TaskType
          memory_stats?: any; // Consider defining MemoryStatsType
          is_active_agent?: boolean; // Redundant with status
        }
        ```
    *   The `_minion_to_dict` in backend prepares a structure that matches this, including nested `persona` and `emotional_state`.
    *   The `status` mapping in `_minion_to_dict` (`domain_status.lower()` to frontend status) seems okay.

**Overall Type Consistency (MINION_SPAWNED WebSocket):** Appears good. The backend serialization `_minion_to_dict` is designed to match the frontend `MinionType`.

## Potential Issues & Areas for Deeper Dive:

*   **Default Model Name Consistency:** While minor, standardizing the default `model_name` across API schema, service layer, and domain model defaults would be cleaner.
*   **`sender_id` in `MessageCreateSchema`:** Currently defaults to "USER". If minions are to message channels autonomously, this will need to be populated with the minion's ID. The current `ChannelServiceV2.add_message_to_channel` already accepts `sender_id`.
*   **Richness of `Session.state`:** The current `emotional_cue` and `memory_cue` are simple strings. The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` implies much richer, structured data might eventually inform prompts. This is an evolution point, not a current type error.
*   **Error object serialization:** How errors from backend (e.g., ADK errors) are propagated to frontend via API responses or WebSocket events needs checking.
*   **Task data flow:** Not yet audited, will be important for `taskStore.ts` and `Task` domain.

---
*Audit in progress. More data flows (e.g., task updates, minion emotional changes via WebSocket) will be added.*
