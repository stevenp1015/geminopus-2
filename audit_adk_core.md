# ADK Core Component Audit Checklist

This checklist is used to audit the core ADK components within the Gemini Legion project, ensuring they align with ADK best practices and the official ADK documentation.

## 1. `ADKMinionAgent` (`LlmAgent` Subclass)

**File:** `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`

| Item                                       | Status (OK/Issue/N/A) | Notes / Path to Fix                                   |
| :----------------------------------------- | :-------------------- | :---------------------------------------------------- |
| **Initialization (`__init__`)**            |                       |                                                       |
| Correctly subclasses `google.adk.agents.LlmAgent` |                       |                                                       |
| `name` parameter (minion_id) correctly set |                       |                                                       |
| `model` parameter (persona.model_name) correctly set |                       |                                                       |
| `instruction` parameter:                     |                       |                                                       |
|   - Built from persona                     |                       |                                                       |
|   - Includes `{{current_emotional_cue}}` placeholder |                       |                                                       |
|   - Includes `{{conversation_history_cue}}` placeholder |                       |                                                       |
|   - Uses other persona details appropriately |                       |                                                       |
| `tools` parameter:                         |                       |                                                       |
|   - Provided by `ADKCommunicationKit.get_tools()` |                       |                                                       |
|   - Tools are valid ADK tool types (e.g., `FunctionTool` or callable) |                       |                                                       |
| `generate_content_config` parameter:       |                       |                                                       |
|   - Uses `google.genai.types.GenerateContentConfig` |                       |                                                       |
|   - `temperature` set (e.g., from persona)   |                       |                                                       |
|   - `max_output_tokens` set (e.g., from persona) |                       |                                                       |
|   - Other relevant configs (top_p, top_k) set |                       |                                                       |
| `description` parameter set (for multi-agent awareness if applicable) |                       |                                                       |
| Passes `api_key` if necessary              |                       |                                                       |
| Handles `**kwargs` correctly to parent `LlmAgent` |                       |                                                       |
| Internal emotional engine (`_emotional_engine`) initialized |                       |                                                       |
| Internal memory system (`_memory_system`) initialized |                       |                                                       |
| **Agent's `run_async` method (or equivalent for `LlmAgent`)** |                       | This is handled by LlmAgent's `generate_content_async` or tool flows, orchestrated by Runner. |
|   - How it's intended to be called by `Runner` |                       |                                                       |
|   - Correctly yields `Event` objects (if overridden, typically not for basic `LlmAgent`) |                       |                                                       |
| **Tool Handling**                            |                       |                                                       |
|   - Agent correctly processes `FunctionCall` from LLM |                       | (Handled by `LlmAgent` base class)                  |
|   - Agent correctly executes the identified tool |                       | (Handled by `LlmAgent` base class)                  |
|   - Agent correctly forms `FunctionResponse` to send back to LLM |                       | (Handled by `LlmAgent` base class)                  |
| **Lifecycle Methods**                      |                       |                                                       |
| `start()` method implemented (if needed)   |                       |                                                       |
| `stop()` method implemented (if needed)    |                       |                                                       |
| **Callbacks**                              |                       |                                                       |
|   - Usage of `before_model_callback`, `after_model_callback`, etc. (if any) |                       |                                                       |

## 2. `Runner` Usage

**File:** `gemini_legion_backend/core/application/services/minion_service_v2.py` (primarily `_start_minion_agent` and `_handle_channel_message`)

| Item                                       | Status (OK/Issue/N/A) | Notes / Path to Fix                                   |
| :----------------------------------------- | :-------------------- | :---------------------------------------------------- |
| **Runner Instantiation**                   |                       |                                                       |
|   - `google.adk.Runner` correctly imported |                       |                                                       |
|   - Instantiated with `agent` (the `ADKMinionAgent` instance) |                       |                                                       |
|   - Instantiated with `app_name`           |                       |                                                       |
|   - Instantiated with `session_service`    |                       |                                                       |
|   - Other necessary parameters (e.g., `artifact_service`, `memory_service` if used directly by Runner) |                       |                                                       |
| **Runner Execution (`run_async`)**         |                       |                                                       |
|   - Correct method called on `Runner` instance (e.g., `runner.run_async(...)`) |                       |                                                       |
|   - `prompt` (user message) correctly passed |                       |                                                       |
|   - `session_id` correctly passed/managed  |                       |                                                       |
|   - `user_id` correctly passed (if applicable) |                       |                                                       |
|   - `session_state` correctly passed (for instruction templating) |                       |                                                       |
|     - Contains `current_emotional_cue`     |                       |                                                       |
|     - Contains `conversation_history_cue`  |                       |                                                       |
|   - `request_id` passed (optional, for tracing) |                       |                                                       |
|   - Return value (async generator of `Event` objects) correctly handled |                       |                                                       |
|   - Iteration `async for event in runner.run_async(...)` |                       |                                                       |
|   - Extraction of final response from events (e.g., text from last relevant `Event.content`) |                       |                                                       |
|   - Handling of tool call events (if service needs to be aware, usually Runner handles tool execution via Agent) |                       |                                                       |
|   - Error handling around `runner.run_async()` call |                       |                                                       |

## 3. Tools (`ADKCommunicationKit`)

**File:** `gemini_legion_backend/core/infrastructure/adk/tools/communication_tools.py`

| Item                                       | Status (OK/Issue/N/A) | Notes / Path to Fix                                   |
| :----------------------------------------- | :-------------------- | :---------------------------------------------------- |
| **Tool Definition**                        |                       |                                                       |
|   - Tools are functions or methods         |                       |                                                       |
|   - Clear, descriptive docstrings (used by LLM for tool selection) |                       |                                                       |
|   - Correct Python type hints for parameters and return types (used for schema generation) |                       |                                                       |
|   - If a tool is async, defined with `async def` |                       | (e.g., `send_channel_message`)                      |
|   - If a tool is sync, defined with `def`  |                       |                                                       |
|   - Return type is compatible with ADK (e.g., JSON serializable, dict) |                       |                                                       |
| **Tool Registration**                      |                       |                                                       |
|   - `ADKCommunicationKit.get_tools()` returns a list of these callables |                       |                                                       |
|   - These are correctly passed to `LlmAgent(tools=...)` |                       |                                                       |
| **Tool Execution**                         |                       |                                                       |
|   - Logic within tools is sound            |                       |                                                       |
|   - Async tools correctly use `await` for async operations |                       |                                                       |
|   - Error handling within tools            |                       |                                                       |
|   - Logging within tools                   |                       |                                                       |

## 4. Session Management

**Files:** `MinionServiceV2`, `dependencies_v2.py` (or wherever `SessionService` is instantiated)

| Item                                       | Status (OK/Issue/N/A) | Notes / Path to Fix                                   |
| :----------------------------------------- | :-------------------- | :---------------------------------------------------- |
| **`SessionService`**                       |                       |                                                       |
|   - Appropriate `SessionService` implementation used (e.g., `InMemorySessionService`, or a persistent one) |                       |                                                       |
|   - `SessionService` instance provided to `Runner` |                       |                                                       |
| **Session Lifecycle**                      |                       |                                                       |
|   - `session_id` generation/management strategy (is it consistent per conversation thread?) |                       |                                                       |
|   - `Runner` uses `SessionService` to load/save session state and event history (implicitly via `run_async` interaction with agent-yielded events) |                       |                                                       |
|   - If agent logic directly interacts with `ctx.session.state` or `ctx.session.events`: |                       | (More advanced usage)                                 |
|     - Reads from `ctx.session.state` are understood (potential "dirty reads") |                       |                                                       |
|     - Writes to `ctx.session.state` are correctly part of an `EventAction`'s `state_delta` to be committed by Runner |                       |                                                       |

## 5. Event Bus Integration (Custom)

**Files:** `ADKMinionAgent`, `MinionServiceV2`, `ADKCommunicationKit`, `event_bus.py`

| Item                                       | Status (OK/Issue/N/A) | Notes / Path to Fix                                   |
| :----------------------------------------- | :-------------------- | :---------------------------------------------------- |
| **Clarity of Roles**                       |                       |                                                       |
|   - Distinction between ADK `Event` objects (yielded by agent to Runner) and custom domain events (e.g., `EventType` on `event_bus.py`) |                       |                                                       |
| **Event Emission**                         |                       |                                                       |
|   - Custom events emitted at appropriate times (e.g., after state changes are committed) |                       |                                                       |
|   - `ADKCommunicationKit` tools emitting custom events (e.g., `emit_channel_message`) |                       |                                                       |
|     - If tool is sync but event emission is async, how is this handled? (Was an issue, now `send_channel_message` is async) |                       |                                                       |
| **Event Consumption**                      |                       |                                                       |
|   - Services (`MinionServiceV2`) subscribe to relevant custom events |                       |                                                       |
|   - Agent (`ADKMinionAgent`) itself subscribing to custom events (if any) |                       |                                                       |

This checklist provides a starting point and should be expanded based on specific findings or areas of concern.
---
