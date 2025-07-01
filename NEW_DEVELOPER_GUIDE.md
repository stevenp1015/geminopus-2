# Gemini Legion: New Developer Getting Started Guide

Welcome to Gemini Legion! This guide will help you understand the project, set up your development environment, and get started with contributing.

## 1. Project Overview

Gemini Legion is a sophisticated multi-agent AI system. The vision is to create a "Company of Besties" – a team of personality-driven, emotionally aware AI agents (called "Minions") that work collaboratively under the direction of a Legion Commander.

**Key Goals & Concepts:**
*   **Personality-Driven Minions:** Each Minion has a unique persona, emotional state, and memory.
*   **Event-Driven Architecture:** The system relies heavily on events for communication and state changes.
*   **Agent Development Kit (ADK):** The backend leverages Google's ADK for building and managing Minion agents.
*   **V2 Architecture:** The project is currently on its V2 architecture, which emphasizes clean design and idiomatic ADK usage.

For a deep dive into the project's ultimate vision and detailed architecture, please refer to the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`. For specifics on ADK integration, consult `Project_Context_Crucible.md`.

## 2. High-Level Architecture (V2)

The system consists of two main parts: a backend powered by Python and FastAPI, and a frontend built with React and TypeScript.

```
+--------------------------------+      +---------------------------------+
|   Frontend (React, TypeScript) |----->|   Backend (Python, FastAPI)     |
|   (gemini_legion_frontend)     |      |   (gemini_legion_backend)       |
+--------------------------------+      +---------------------------------+
        |        ^                               |         ^
        | (HTTP) | (WebSocket)                    | (ADK)   | (Events)
        v        |                               v         |
+----------------+-----------------+     +-----------------+-----------------+
| UI Components, State (Zustand)   |     | API Endpoints, WebSocket Bridge |
+----------------------------------+     +----------------------------------+
                                         | Application Services (Minion, Task, Channel) |
                                         +----------------------------------+
                                         | Core Domain Logic (Emotional, Memory Engines) |
                                         +----------------------------------+
                                         | Infrastructure (ADK Adapters, DB, Event Bus) |
                                         +----------------------------------+
```

**Backend Key Components:**
*   **`main_v2.py`**: The entry point for the V2 backend application.
*   **FastAPI**: Used for creating REST APIs.
*   **Socket.IO**: Used for WebSocket communication with the frontend.
*   **ADK (`google.adk`)**: The core framework for defining Minion agents, their tools, and managing their lifecycle.
    *   `LlmAgent`: The base class for Minions. Gemini Legion uses subclasses of `LlmAgent` to integrate custom persona, emotional, and memory logic.
    *   `Runner`: Used by services to execute agent tasks.
    *   `Session.state`: Used to pass dynamic, invocation-specific data to agents.
    *   Callbacks: Key mechanism for injecting custom logic into the ADK lifecycle.
*   **Event Bus (`GeminiEventBusV2`):** Central nervous system for decoupled communication between components.
*   **Services (`MinionServiceV2`, `ChannelServiceV2`, `TaskServiceV2`):** Handle business logic.
*   **Domain Models (`core/domain/`):** Define core data structures like `Minion`, `EmotionalState`, `Message`.
*   **Persistence**: MongoDB is typically used for data persistence, and Redis for caching or distributed event bus messages (though ADK primarily uses a relational DB like PostgreSQL or SQLite for its `DatabaseSessionService`).

**Frontend Key Components:**
*   **`App.tsx`**: The main application component.
*   **React & TypeScript**: Used for building the user interface.
*   **Zustand**: For state management.
*   **`services/api/`**: Contains functions for making API calls to the backend.
*   **`hooks/useWebSocket.ts` & `store/legionStore.ts`**: Handle WebSocket connection and event processing.

## 3. Setting Up Your Development Environment

Follow these steps to get the V2 system running locally. For more detailed deployment options, see `DEPLOYMENT_V2.md` and `V2_BACKEND_VALIDATION_GUIDE.md`.

### 3.1 Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Access to a Gemini API key (or appropriate Google Cloud setup for Vertex AI).
*   MongoDB instance (running locally or accessible).
*   Redis instance (optional for local dev if `EVENT_BUS_MODE=local`, but recommended).

### 3.2 Backend Setup
1.  **Clone the repository.**
2.  **Navigate to the project root.**
3.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    # Potentially also requirements-new.txt if it's distinct for V2
    ```
5.  **Set up environment variables for the backend:**
    *   Copy `gemini_legion_backend/.env.example` to `gemini_legion_backend/.env` (if example exists, otherwise create `.env`).
    *   Edit `gemini_legion_backend/.env` with your actual values. Key variables (refer to `DEPLOYMENT_V2.md` for a more complete list):
        ```env
        GOOGLE_API_KEY=your_google_api_key_for_gemini
        # Or configure for Vertex AI if preferred (see Project_Context_Crucible.md)

        # For ADK DatabaseSessionService (if used, e.g., for persistent ADK sessions)
        # DATABASE_URL=sqlite:///./gemini_legion_adk_sessions.db
        # DATABASE_URL=postgresql://user:pass@host:port/dbname

        # For Gemini Legion's primary database (e.g., MongoDB)
        MONGODB_URL=mongodb://localhost:27017/gemini_legion_v2

        # For Event Bus (if using Redis)
        REDIS_URL=redis://localhost:6379/0
        EVENT_BUS_MODE=distributed # or 'local' for in-memory

        PORT=8000 # Or 8001 if running alongside V1 on 8000
        HOST=0.0.0.0
        LOG_LEVEL=INFO
        ```

### 3.3 Frontend Setup
1.  **Navigate to the frontend directory:**
    ```bash
    cd gemini_legion_frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Set up environment variables for the frontend:**
    *   Create a `.env` file in the `gemini_legion_frontend` directory.
    *   Add the following, adjusting the port if your V2 backend runs elsewhere:
        ```env
        VITE_API_URL=http://localhost:8000/api/v2
        VITE_WS_URL=ws://localhost:8000
        ```
        (If your V2 backend is on port 8001, use `http://localhost:8001/api/v2` and `ws://localhost:8001`)

### 3.4 Running the Application
1.  **Start the Backend (V2):**
    *   Open a terminal, navigate to the project root, activate the venv.
    *   Run: `python -m gemini_legion_backend.main_v2`
    *   Watch for any errors in the console.

2.  **Run Data Migration (Optional but Recommended for Fresh Setup):**
    *   If this is a new setup or you want to ensure V2 has necessary base data (like default channels, or data from a previous V1).
    *   Open another terminal, navigate to project root, activate venv.
    *   Run: `python migrate_to_v2.py`
    *   Answer prompts as needed.

3.  **Start the Frontend:**
    *   Open another terminal, navigate to `gemini_legion_frontend`.
    *   Run: `npm run dev`
    *   This will typically open the application in your web browser (e.g., at `http://localhost:5173` or a similar port shown in the terminal).

### 3.5 Initial Validation
1.  **Backend Health:**
    *   Open your browser or use `curl` to check the V2 health endpoint: `http://localhost:BACKEND_PORT/api/v2/health` (e.g., `http://localhost:8000/api/v2/health`).
    *   You should see a JSON response indicating the system is operational.
2.  **Frontend Loads:**
    *   Ensure the frontend loads in your browser without obvious errors.
3.  **Basic Interaction:**
    *   Try basic interactions like spawning a Minion or sending a message in a channel to see if the end-to-end flow is working.

## 4. Key Development Workflows

### 4.1 Backend Development
*   **Modifying Agents (`core/infrastructure/adk/agents/minion_agent_v2.py`):**
    *   This is where Minion behavior is defined by subclassing `LlmAgent`.
    *   Focus on using the `instruction` parameter, `tools`, `Session.state`, and ADK callbacks to integrate persona, emotional state, and memory.
*   **Adding Tools (`core/infrastructure/adk/tools/`):**
    *   Tools allow Minions to interact with external systems or perform specific actions.
    *   Tools should inherit from `google.adk.tools.BaseTool` or be simple callables.
*   **Updating Services (`core/application/services/`):**
    *   Services orchestrate actions, interact with repositories, and use the ADK `Runner` to execute agents.
*   **Defining Domain Logic (`core/domain/`):**
    *   Changes to core concepts like `EmotionalState`, `MinionPersona`, `Task` definitions happen here.
*   **API Endpoints (`api/rest/endpoints/`):**
    *   New REST API routes are added here using FastAPI.
*   **WebSocket Events (`api/websocket/event_bridge.py`):**
    *   The `WebSocketEventBridge` listens to the `GeminiEventBusV2` and relays relevant events to connected frontend clients. Adding new types of real-time updates might involve defining new events and ensuring the bridge handles them.

### 4.2 Frontend Development
*   **UI Components (`src/components/`):**
    *   Visual elements are built as React components.
*   **State Management (`src/store/`):**
    *   Zustand stores (`legionStore.ts`, `chatStore.ts`, `taskStore.ts`) manage application state.
    *   Actions in these stores often make API calls or emit WebSocket messages.
    *   WebSocket event handlers within these stores update the state based on messages from the backend.
*   **API Services (`src/services/api/`):**
    *   Functions here encapsulate HTTP requests to the backend REST API.
*   **Styling**: Tailwind CSS is used for styling.

### 4.3 Running Tests
*   **Backend Tests (`tests/v2/`):**
    *   The backend has a test suite. Use `pytest` or `python -m unittest` to run these.
    *   Example: `pytest tests/v2/`
*   **Frontend Tests:** (Details on frontend testing practices would be added here if available, e.g., using Jest/React Testing Library).

## 5. Important Considerations & Best Practices

*   **Follow the Ideal Architecture:** When implementing new features, refer to `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` to align with the project's vision.
*   **ADK Best Practices (`Project_Context_Crucible.md`):**
    *   Prefer ADK callbacks for injecting logic into the agent lifecycle.
    *   Use `Session.state` for dynamic, per-invocation context.
    *   Subclass `LlmAgent` for custom agent definitions, injecting domain objects via the constructor.
*   **Event-Driven:** Think in terms of events. If a significant action occurs, consider if an event should be emitted on the `GeminiEventBusV2`.
*   **Configuration over Code:** Use environment variables for configuration where possible.
*   **Commit Messages:** Follow standard conventions for commit messages.
*   **Branching Strategy:** (Details on branching strategy, e.g., feature branches, would be added here).

## 6. Where to Find More Information

*   **`IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`**: The complete vision and detailed design for Gemini Legion.
*   **`Project_Context_Crucible.md`**: Essential details on ADK integration, frontend structure, domain models, and ADK best practices.
*   **`DEPLOYMENT_V2.md`**: Comprehensive guide for various deployment scenarios and configurations.
*   **`V2_BACKEND_VALIDATION_GUIDE.md`**: Steps for initial backend setup and validation.
*   **ADK Documentation**: Refer to the official Google ADK documentation for specifics on ADK classes and features. (Links to relevant ADK docs could be added here if available).
*   **Code Comments & Docstrings**: Explore the existing codebase for inline documentation.

This guide should provide a solid starting point. Don't hesitate to explore the documents mentioned above and the codebase itself for deeper understanding. Welcome to the Legion!
