# Gemini Legion: Architecture Translation Guide

## 1. Introduction

This guide serves as a bridge between the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` and the current codebase of Gemini Legion (both backend and frontend). It aims to provide developers with a clear understanding of how different components are structured, how they interact, and critically, how they integrate with or map to the Agent Development Kit (ADK) framework.

This document will explore:
- Key classes and their roles.
- Module structures and their dependencies.
- Important functions/methods representing core logic.
- Data structures and schemas.
- Event systems and typical workflows.
- Configuration patterns.
- API integrations (REST and WebSocket).
- State management mechanisms.
- Communication protocols.

Throughout this guide, connections will be drawn to ADK principles, relevant sections of the `adk_integration_masterclass.md`, and the target vision from the ideal architecture document.

## 2. Backend Architecture (`gemini_legion_backend`)

The backend is built using FastAPI for REST APIs and Socket.IO for real-time WebSocket communication. It follows an event-driven approach, though the primary event bus (`GeminiEventBus`) is custom to the project, distinct from ADK's internal event stream.

### 2.1 Modules and Their Dependencies

The backend is primarily structured into `api`, `config`, `core`, and `main_v2.py`.

*   **`main_v2.py` (Entry Point)**
    *   **Purpose:** Initializes the FastAPI application, manages the application lifecycle (startup/shutdown), and sets up Socket.IO.
    *   **Dependencies:** `api` (for routers), `core.dependencies_v2` (for service container), `api.websocket.event_bridge`.
    *   **ADK Link:** The `lifespan` manager initializes services. ADK services like `SessionService`, `ArtifactService`, and `Runner` instances *should* ideally be managed here or within `dependencies_v2.py` as part of the global service container. Currently, they are not explicitly initialized at this top level.

*   **`config/`**
    *   **`settings.py`**: Defines application settings using Pydantic `BaseSettings`, loadable from `.env` files and environment variables. Includes `DATABASE_URL` which is crucial for a persistent ADK `SessionService`.
    *   **ADK Link:** The `DATABASE_URL` would be used by ADK's `DatabaseSessionService`. API keys defined here would be used by ADK `LlmAgent` model configurations.

*   **`core/`**
    *   **`dependencies_v2.py`**:
        *   **Purpose:** Sets up a `ServiceContainerV2` for dependency injection. Initializes repositories (currently in-memory) and application services.
        *   **ADK Link:** This is the logical place for ADK `SessionService`, `ArtifactService`, `Runner` initializations. Currently, these are absent. `MinionServiceV2` gets an API key, which it passes to `ADKMinionAgent`. It also instantiates the custom `GeminiEventBus`.
    *   **`domain/`**: Contains Pydantic models for core entities like `Minion`, `MinionPersona`, `EmotionalState`, `Channel`, `Message`, `Task`.
        *   **ADK Link:** `MinionPersona` directly informs the `instruction` and configuration of an ADK `LlmAgent`. `EmotionalState` and `WorkingMemory` from the domain would need to be bridged to ADK's `Session.state` for Minions to use them contextually in ADK-driven interactions.
    *   **`application/services/`**:
        *   **`minion_service_v2.py`**: Manages Minion lifecycles. Instantiates `ADKMinionAgent`.
            *   **ADK Link:** This service *should* be the primary user of ADK `Runner.predict()` or `Runner.run_async()` to execute Minion methods. It currently instantiates `ADKMinionAgent` but doesn't seem to use a shared ADK Runner.
        *   **`channel_service_v2.py`**: Manages channels and messages.
    *   **`infrastructure/`**:
        *   **`persistence/repositories/memory/`**: Contains in-memory repository implementations.
            *   **ADK Link:** If ADK's `DatabaseSessionService` is used, it will manage its own persistence separately from these in-memory stores. Integration would be needed if ADK session state needs to reference or be influenced by data held in these repositories.
        *   **`adk/`**: Contains project-specific ADK integrations.
            *   `agents/minion_agent_v2.py`: Current implementation of the Minion as an agent. Uses `genai.Client` directly, with a fallback mode. This is a key area for deeper ADK integration (see `adk_integration_masterclass.md`).
            *   `events/event_bus.py`: Defines the custom `GeminiEventBus`.
            *   `tools/`: Adapters for MCP tools (`mcp_adapter.py`) and the `ToolIntegrationManager`.

*   **`api/`**
    *   **`rest/`**: FastAPI routers and Pydantic schemas.
        *   **ADK Link:** None directly. These expose the backend services.
    *   **`websocket/`**:
        *   **`event_bridge.py`**: Connects the `GeminiEventBus` to Socket.IO clients, forwarding relevant internal events to the frontend.
        *   **ADK Link:** None directly. ADK's streaming capabilities (e.g., for `Runner.run_live()`) would be a separate WebSocket setup if used for direct agent-client streaming, as detailed in ADK streaming docs. The current `event_bridge` is for project-specific event broadcasting.

### 2.2 Key Classes

*   **`ServiceContainerV2` (`dependencies_v2.py`)**: Central point for accessing application services and repositories.
*   **`MinionServiceV2`**: Manages Minion domain objects and `ADKMinionAgent` instances.
    *   **ADK Integration**: Instantiates `ADKMinionAgent`. Should ideally use an ADK `Runner` for agent invocations.
*   **`ADKMinionAgent` (`minion_agent_v2.py`)**: The project's attempt to wrap a Minion's logic within an ADK-like structure. Currently uses `google.genai.Client` directly due to noted API issues.
    *   **ADK Integration**: Intended to be an `LlmAgent`. The `adk_integration_masterclass.md` details how it *should* align with `LlmAgent` (using `instruction`, `tools` list, `predict` method, ADK session state).
*   **`EmotionalEngineV2`, `MemorySystemV2`**: Custom systems managing Minion's internal states.
    *   **ADK Integration**: Their state needs to be exposed to `ADKMinionAgent` (e.g., via `Session.state` or callbacks) to influence ADK LLM interactions.
*   **`MCPToolRegistry`, `MCPToADKAdapter`, `ToolIntegrationManager`**: Manage and provide tools to Minions.
    *   **ADK Integration**: `MCPToADKAdapter` converts MCP tools to ADK `BaseTool` compatible instances. `ToolIntegrationManager` supplies the `tools` list to `ADKMinionAgent` for use with an ADK `LlmAgent`.
*   **`GeminiEventBus`**: Custom project-wide event bus.
    *   **ADK Integration**: Distinct from ADK's internal `Event` stream processed by the `Runner`. `ADKMinionAgent`s might emit events to this bus as a side effect of their actions (e.g., via a tool or callback).
*   **`WebSocketEventBridge`**: Relays `GeminiEventBus` events to the frontend.

### 2.3 Data Structures and Schemas

*   **Domain Models (`core/domain/*.py`)**: Pydantic models like `Minion`, `MinionPersona`, `EmotionalState`, `Channel`, `Message`, `Task`. These are the internal representation of data.
*   **API Schemas (`api/rest/schemas.py`)**: Pydantic models for REST API request and response validation (e.g., `CreateMinionRequest`, `MinionResponse`). These are derived from or map to domain models.
    *   **ADK Link**: Information from `MinionPersona` (like `model_name`, `temperature`, tool lists) is used to configure the `ADKMinionAgent`. Data from `EmotionalState` or `MemorySystem` might be serialized into ADK `Session.state` if needed by the ADK agent's prompt.

### 2.4 Event Systems and Workflows

*   **`GeminiEventBus`**: The primary event system for inter-service communication within the backend (e.g., `MinionService` emitting `MINION_SPAWNED`, `EmotionalEngine` reacting to messages).
*   **ADK Event Stream**: When/if `ADKMinionAgent` uses `Runner.run_async()` or `Runner.predict()` idiomatically, ADK generates its own stream of `Event` objects for that specific invocation (user input -> tool calls -> tool responses -> agent response). This stream is managed by the `Runner`.
*   **Typical Workflow (e.g., User sends message via API)**:
    1.  REST API (`channels_v2.py`) receives message.
    2.  Calls `ChannelServiceV2.send_message()`.
    3.  `ChannelServiceV2` saves message and emits `CHANNEL_MESSAGE` to `GeminiEventBus`.
    4.  `ADKMinionAgent._handle_channel_message` (subscribed to `GeminiEventBus`) is triggered.
    5.  `ADKMinionAgent` processes the message (currently using its internal `genai.Client` chat session).
    6.  If `ADKMinionAgent` responds, it uses its `ADKCommunicationKit` tool, which likely emits another `CHANNEL_MESSAGE` via `GeminiEventBus` (this part needs to be confirmed but is the clean event-driven way).
    7.  `WebSocketEventBridge` picks up these `CHANNEL_MESSAGE` events from `GeminiEventBus` and sends them to subscribed frontend clients.
*   **ADK Workflow Integration**:
    *   The `adk_integration_masterclass.md` describes how `ADKMinionAgent` should ideally use ADK's `predict` method. This method encapsulates an ADK event workflow (handling tool calls, etc.).
    *   Custom emotional/memory processing can be hooked into this ADK flow via callbacks or by preparing context in `Session.state` before calling `predict`.

### 2.5 Configuration Patterns

*   **`config/settings.py`**: Centralized Pydantic-based configuration.
*   Environment variables and `.env` files are supported.
*   **ADK Link**: `settings.database_url` is vital for persistent ADK `SessionService`. `settings.GOOGLE_API_KEY` is used by `MinionServiceV2` for `ADKMinionAgent`.

### 2.6 State Management Systems (Backend)

*   **Domain Object State**: Managed by services (e.g., `MinionServiceV2`) and stored in in-memory repositories.
*   **ADK Session State**: If ADK `Runner.predict()` or `run_async()` with a `session` object were used by `MinionServiceV2`, ADK's `SessionService` (e.g., `DatabaseSessionService`) would manage the state for individual ADK agent invocations. This state can hold conversational history and any data needed by the LLM prompt templating. The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` implies this level of integration.
    *   **Current Discrepancy**: `ADKMinionAgent` seems to manage its own chat history per channel internally due to `genai.Client` issues, bypassing ADK session state for conversation turns. The masterclass guides on how to use ADK session state.

### 2.7 Communication Protocols (Backend)

*   **Internal**: `GeminiEventBus` for asynchronous inter-service communication.
*   **External**:
    *   REST API (FastAPI) for client-server requests.
    *   Socket.IO (via `python-socketio` library) for real-time bidirectional communication with the frontend, managed by `WebSocketEventBridge`.

## 3. Frontend Architecture (`gemini_legion_frontend`)

The frontend is a React application (likely using Vite, based on `vite.config.ts` and `main.tsx`) with TypeScript.

### 3.1 Key Modules and Components

*   **`src/main.tsx`**: Entry point, renders `App.tsx`.
*   **`src/App.tsx`**: Main application component, sets up routing/views, initializes WebSocket connection via `useWebSocket` hook (which uses `legionStore`), and triggers initial data fetches.
*   **`src/store/`**: Zustand stores for state management.
    *   `legionStore.ts`: Manages minions, global WebSocket connection, and some high-level actions.
    *   `chatStore.ts`: Manages channels, messages, and chat-related actions.
    *   `taskStore.ts`: Manages tasks.
*   **`src/services/api/`**: Contains functions for making REST API calls to the backend (e.g., `minionApi.ts`, `channelApi.ts`). Uses `fetch`.
*   **`src/hooks/useWebSocket.ts`**: Provides WebSocket connection status and instance, but actual event handling is more distributed (primarily in `legionStore`).
*   **`src/components/`**: UI components.
    *   `Legion/LegionDashboard.tsx`: Displays minion information.
    *   `Chat/ChatInterface.tsx`: Handles channel display, message lists, and message input.

### 3.2 State Management (Frontend)

*   Zustand is used for global state.
*   `legionStore` holds minion data, WebSocket instance.
*   `chatStore` holds channel and message data.
*   `taskStore` holds task data.
*   State is updated based on API responses and incoming WebSocket events.

### 3.3 API Integrations and Interfaces (Frontend)

*   **REST APIs**: Functions in `src/services/api/*.ts` make `fetch` requests to the backend REST endpoints. These are called by actions in the Zustand stores.
*   **WebSocket**:
    *   `legionStore.connectWebSocket()` establishes the Socket.IO connection.
    *   Event handlers for various backend events (e.g., `minion_spawned`, `message_sent`) are defined within `legionStore` and `useWebSocket` hook. These update the Zustand stores, causing UI re-renders.
    *   The frontend sends commands like `subscribe_channel` via Socket.IO, handled by `main_v2.py` which then calls `WebSocketEventBridge` methods.

### 3.4 Communication with Backend and ADK

*   Frontend talks to the Gemini Legion Backend (FastAPI/Socket.IO).
*   ADK is not directly exposed to the frontend. Any ADK-driven behavior (e.g., a Minion's response generated by ADK `LlmAgent.predict()`) is proxied through the backend.
*   For example, a user types a message in `ChatInterface.tsx` -> `chatStore.sendMessage()` -> `channelApi.sendMessage()` (REST) -> Backend `ChannelServiceV2.send_message()` -> `GeminiEventBus` (`CHANNEL_MESSAGE`) -> `ADKMinionAgent._handle_channel_message()`. The Minion's response generation (which *should* use ADK `LlmAgent` logic) -> `ADKCommunicationKit` tool -> `GeminiEventBus` (`CHANNEL_MESSAGE`) -> `WebSocketEventBridge` -> Frontend `legionStore` (WebSocket listener) -> `chatStore.handleNewMessage()` -> UI update.

## 4. Mapping Ideal Architecture to Current Code & ADK

*   **MinionAgent (Ideal) vs. `ADKMinionAgent` (Current)**:
    *   **Ideal**: Extends ADK `LlmAgent`, uses ADK `Runner` via `MinionService`, integrates Emotional/Memory engines into ADK `Session.state` or via callbacks.
    *   **Current (`minion_agent_v2.py`)**: Attempts to use `genai.Client` directly, has a fallback mode, and seems to manage its own chat history. Less integrated with ADK `Runner` and `SessionService` than ideal.
    *   **Translation**: The guide should highlight that `ADKMinionAgent` needs to more fully embrace ADK `LlmAgent` patterns (using `instruction`, `tools` list fed by `ToolIntegrationManager`, and methods like `predict`). `MinionServiceV2` should use an ADK `Runner` to call `ADKMinionAgent.predict()`.

*   **Emotional/Memory Engines**:
    *   **Ideal**: Integrated with `MinionAgent` to influence ADK LLM prompts, possibly via `Session.state` or callbacks.
    *   **Current**: Custom `EmotionalEngineV2` and `MemorySystemV2` exist. Their integration into `ADKMinionAgent`'s ADK-driven flow is not fully clear in `minion_agent_v2.py` and seems to rely on the custom event bus rather than ADK's context objects.
    *   **Translation**: Explain how to pass snapshots or cues from these engines into ADK `Session.state` before `predict` calls, or how to use ADK callbacks to update/query these engines during an ADK invocation.

*   **MCP Toolbelt**:
    *   **Ideal & Current**: The backend's `MCPToolRegistry` and `MCPToADKAdapter` align well with the ideal architecture. `ToolIntegrationManager` correctly provides these to Minions.
    *   **Translation**: This part is fairly well-aligned. The guide should confirm that the `tools` list passed to `ADKMinionAgent` constructor contains `BaseTool` instances ready for ADK.

*   **Inter-Minion Communication**:
    *   **Ideal**: Uses various layers, potentially ADK `AgentTool` for direct calls or events.
    *   **Current**: Primarily uses the custom `GeminiEventBus`. `ADKCommunicationKit` is a tool Minions use, which likely publishes to this event bus.
    *   **Translation**: Clarify that ADK `AgentTool` could be an option for direct synchronous calls between Minions if needed, supplementing the `GeminiEventBus`.

*   **State Management**:
    *   **Ideal**: Scalable, persistent state (e.g., `DatabaseSessionService` for ADK sessions).
    *   **Current**: Backend domain object persistence is in-memory. ADK `SessionService` is not explicitly managed by `dependencies_v2.py`. `ADKMinionAgent` manages chat history internally.
    *   **Translation**: Strongly recommend initializing and using ADK's `DatabaseSessionService` (using `settings.database_url`) within `dependencies_v2.py` and passing it to `MinionServiceV2` for use with an ADK `Runner` when invoking Minions. This would handle ADK-specific session state, including conversational history for `LlmAgent.predict`.

*   **Event Systems**:
    *   **Ideal**: Event-Driven Architecture.
    *   **Current**: `GeminiEventBus` for backend inter-service events. `WebSocketEventBridge` for backend-to-frontend. ADK's internal `Event` stream for agent invocations.
    *   **Translation**: Differentiate these. ADK's `Event` stream is for the lifecycle of a single agent call. `GeminiEventBus` is for broader application-level notifications.

## 5. Conclusion

The Gemini Legion project has a solid foundation with its V2 architecture aiming for cleaner, event-driven patterns. However, the integration with ADK, particularly for `ADKMinionAgent`'s execution and session management, is not yet fully aligned with idiomatic ADK usage, partly due to external `google.genai` library issues. This guide, along with the `adk_integration_masterclass.md`, should help developers bridge this gap by showing how the current components map to ADK concepts and how to deepen the integration for a more robust and ADK-idiomatic system as envisioned in the ideal architecture.

The key is to leverage ADK's `Runner`, `SessionService` (with persistence), and `LlmAgent`'s built-in capabilities (instruction processing, tool handling, session state usage via `predict` or `run_async`) more directly within `MinionServiceV2` and `ADKMinionAgent`.
The Architecture Translation Guide has been created. It maps out the backend and frontend structures, identifies key components, analyzes their interactions, and details how they relate to or should integrate with ADK, referencing the Ideal Architecture and the ADK Integration Masterclass.
