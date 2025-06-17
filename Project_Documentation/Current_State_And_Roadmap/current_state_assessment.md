# Gemini Legion: Current State Assessment & Unfucking Roadmap

## 1. Introduction

This document provides an assessment of the current state of the Gemini Legion project, drawing from existing documentation, issue trackers, and a preliminary code scan. Its primary purpose is to identify key issues, deviations from the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`, and to outline a prioritized roadmap for recovery and alignment. The goal is to guide development efforts towards a stable, robust, and ADK-idiomatic system.

## 2. Summary of Current Issues

The Gemini Legion codebase, while having made strides towards a V2 architecture, currently faces several critical challenges that hinder its functionality, maintainability, and alignment with its original vision.

### Key Architectural Deviations & Major Issues:

1.  **Dual V1/V2 Backend Stacks (Partially Addressed):**
    *   **Issue:** The codebase historically contained two parallel backend applications (`main.py` vs. `main_v2.py`).
    *   **Status:** `purge_old_comms.py` aimed to remove V1 components. `main_v2.py` is the current entry point. The directive in `fuckups_introduced_in_v2.md` is to rename V2 components (e.g., `main_v2.py` to `main.py`) after full V1 purge.
    *   **Deviation:** The ideal architecture implies a single, coherent V2 system.

2.  **Non-Idiomatic ADK Agent Implementation:**
    *   **Issue:** `ADKMinionAgent` in `minion_agent_v2.py` primarily uses a manual `genai.Client()` (and was experiencing issues with its initialization) and operates in a fallback mode that doesn't fully leverage ADK `LlmAgent` capabilities. This impacts native tool use, context handling, and lifecycle management via ADK.
    *   **Deviation:** The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` (Section 4.1) specifies `MinionAgent(LlmAgent)`, implying full use of ADK's agent model. The `adk_integration_masterclass.md` provides guidance on this.

3.  **Broken Frontend-Backend API Connectivity:**
    *   **Issue:** Frontend API calls in `gemini_legion_frontend/src/services/api/*` likely target V1 endpoints (e.g., `/api/minions/`) while the V2 backend serves routes under `/api/v2/...`. This will cause 404 errors.
    *   **Deviation:** A functional system requires aligned API paths.

4.  **Incomplete Domain Models:**
    *   **Issue:** Core domain models, particularly `EmotionalState`, are missing attributes (e.g., `relationship_graph`, `response_tendency`) specified in the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.
    *   **Deviation:** The richness of the Minion personalities and interactions depends on these complete domain models.

5.  **Ephemeral Persistence for Domain Objects:**
    *   **Issue:** The V2 backend currently uses in-memory dictionary-based repositories (`MinionRepositoryMemory`, `ChannelRepositoryMemory`, etc.) for its core domain objects. All this application state is lost on restart.
    *   **Deviation:** The ideal architecture (Section 7.2) calls for scalable, persistent state management (e.g., MongoDB, Redis). While `settings.py` defines a `DATABASE_URL` for SQLite, this is not currently used by the main domain repositories.

6.  **Custom Event Bus vs. ADK Events:**
    *   **Issue:** The backend uses a custom `GeminiEventBus` for inter-service communication and frontend updates. This is distinct from ADK's internal `Event` stream used by an ADK `Runner` during an agent invocation.
    *   **Deviation:** While not a direct contradiction, the roles and interactions between these two event systems need to be clear. The custom `GeminiEventBus` is suitable for application-level events. ADK events are for the agent execution lifecycle.

7.  **ADK `SessionService` and `Runner` Not Explicitly Managed:**
    *   **Issue:** The central service initialization in `dependencies_v2.py` does not explicitly set up or provide an ADK `SessionService` or `Runner` instances for use by `MinionServiceV2`.
    *   **Deviation:** Idiomatic ADK usage typically involves a shared, configured `Runner` and `SessionService` (ideally persistent) to manage agent invocations and conversational state.

### Specific Code-Level & Functionality Issues:

*   **`google.genai` Client Instability:** `ADKMinionAgent` has faced significant issues with `google.genai.Client` initialization (`configure`, `GenerativeModel` attributes), suggesting problems with library versions or usage. While the user upgraded `google-generativeai`, this remains a sensitive area.
*   **Pydantic Schema Misalignment:** `convert_minion_to_response` in `endpoints/minions_v2.py` was noted as potentially misaligned with Pydantic response schemas.
*   **Incomplete Features (based on TODOs):**
    *   Auth for channel creation and task creation.
    *   Channel deletion.
    *   Full task lifecycle eventing (`TASK_STARTED`, `TASK_PROGRESS`).
    *   Various frontend UI enhancements and full WebSocket event handling.

## 3. The Ultimate Unfucking Roadmap

This roadmap prioritizes establishing a stable V2 foundation, then aligning with ADK best practices and the ideal architecture.

### Phase 1: Stabilize V2 Core & Frontend-Backend Connectivity (Critical)

1.  **Action:** Ensure `ADKMinionAgent` robustly initializes and uses the `google.generativeai` client.
    *   **Why:** This is fundamental for Minions to have any LLM capabilities. Eliminate the fallback mode.
    *   **Files:** `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`, `gemini_legion_backend/core/application/services/minion_service_v2.py`.
    *   **Priority:** Critical

2.  **Action:** Correct all frontend API call paths and payloads.
    *   **Why:** Enable basic frontend-backend interaction.
    *   **Files:** `gemini_legion_frontend/src/services/api/config.ts`, and all files in `gemini_legion_frontend/src/services/api/`.
    *   **Priority:** Critical

3.  **Action:** Resolve critical Pydantic schema misalignments in API responses (e.g., `convert_minion_to_response`).
    *   **Why:** Ensure frontend receives data in the expected format.
    *   **Files:** `gemini_legion_backend/api/rest/endpoints/minions_v2.py`, related `schemas.py`.
    *   **Priority:** High

4.  **Action:** Complete V1 Code Purge & V2 Renaming.
    *   **Why:** Eliminate confusion and establish V2 as the sole system, as per `fuckups_introduced_in_v2.md`.
    *   **Files:** Multiple, involves deleting old files and renaming V2 files (e.g., `main_v2.py` to `main.py`). Update all import paths.
    *   **Priority:** High

### Phase 2: True ADK Integration for Minions (High)

1.  **Action:** Refactor `ADKMinionAgent` to be a proper subclass of `google.adk.agents.LlmAgent`.
    *   **Why:** To leverage ADK's native capabilities for instruction processing, tool management, and context handling.
    *   **Files:** `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`.
    *   **Reference:** `adk_integration_masterclass.md`.

2.  **Action:** Initialize and use a persistent ADK `SessionService` (e.g., `DatabaseSessionService` with SQLite from `settings.database_url`).
    *   **Why:** To enable ADK-managed conversational state and history for Minions, crucial for context and tool use.
    *   **Files:** `gemini_legion_backend/core/dependencies_v2.py`. The service should be added to `ServiceContainerV2`.

3.  **Action:** Implement ADK `Runner` usage within `MinionServiceV2`.
    *   **Why:** `MinionServiceV2` should use a `Runner` instance (configured with the `SessionService`) to execute `ADKMinionAgent.predict()` or `ADKMinionAgent.run_async()` for handling messages or tasks.
    *   **Files:** `gemini_legion_backend/core/application/services/minion_service_v2.py`.

4.  **Action:** Integrate `EmotionalEngineV2` and `MemorySystemV2` with `ADKMinionAgent` via ADK `Session.state` or Callbacks.
    *   **Why:** To allow Minion's emotional state and memory to influence LLM interactions in an ADK-idiomatic way.
    *   **Files:** `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`.
    *   **Reference:** `adk_integration_masterclass.md`.

### Phase 3: Implement Persistent Storage for Domain Objects (High)

1.  **Action:** Implement persistent repositories (e.g., MongoDB or PostgreSQL using SQLAlchemy, based on `requirements-new.txt` and team preference) for core domain objects (`Minion`, `Channel`, `Message`, `Task`).
    *   **Why:** Ensure data persistence beyond application restarts, as per `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.
    *   **Files:** Create new repository implementations in `gemini_legion_backend/core/infrastructure/persistence/repositories/`. Update `gemini_legion_backend/core/dependencies_v2.py` to use them.
    *   **Priority:** High

2.  **Action:** Develop a data migration strategy from current in-memory/SQLite (if ADK uses it separately) to the new persistent stores if needed.
    *   **Why:** Preserve any existing important data.
    *   **Files:** New migration scripts.
    *   **Priority:** Medium (after persistent repos are chosen)

### Phase 4: Complete Domain Models & Address TODOs (Medium)

1.  **Action:** Flesh out all domain models (`EmotionalState`, `MinionPersona`, etc.) to match the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.
    *   **Why:** Enable the full richness of the envisioned Minion personalities and system capabilities.
    *   **Files:** `gemini_legion_backend/core/domain/*.py`.
    *   **Priority:** Medium

2.  **Action:** Systematically review and address `TODO` comments throughout the codebase.
    *   **Why:** Fix known small issues and complete unfinished features (e.g., auth, full task eventing).
    *   **Files:** Various, identified by `grep`.
    *   **Priority:** Medium (can be done incrementally)

### Phase 5: Enhancements & Robustness (Medium to Low)

1.  **Action:** Implement comprehensive test coverage (unit, integration) for V2 backend components.
    *   **Why:** Ensure stability and prevent regressions.
    *   **Priority:** Medium

2.  **Action:** Refine frontend WebSocket event handling for clarity and completeness.
    *   **Why:** Improve frontend stability and real-time updates.
    *   **Files:** `gemini_legion_frontend/src/store/legionStore.ts`, `gemini_legion_frontend/src/hooks/useWebSocket.ts`.
    *   **Priority:** Medium

3.  **Action:** Implement remaining UI features based on `UI_DESIGN_OPUS_VISION.md`.
    *   **Why:** Achieve the full user experience vision.
    *   **Files:** `gemini_legion_frontend/src/components/`.
    *   **Priority:** Medium to Low (can be phased)

4.  **Action:** Address other items from "Tier 3: Medium Priority" and "Tier 4: Low Priority" of `GEMINI_LEGION_PRIORITIZED_RECOVERY_PLAN.md` as time permits (e.g., performance optimization, advanced logging, full API documentation).
    *   **Why:** Long-term health and scalability of the system.
    *   **Priority:** Low

This roadmap aims to first stabilize the V2 system, then deeply integrate ADK as intended, followed by implementing full data persistence and completing features. The `fuckups_introduced_in_v2.md` document provides a strong, if aggressive, set of initial steps that align with Phases 1 and 2 of this roadmap.
The Current State Assessment and Unfucking Roadmap document has been created. It synthesizes information from various provided documents (`fuckups_introduced_in_v2.md`, `UNFUCK_PLAN.md`, `V2_SITREP_AND_UNFUCKENING_TRACKER.md`, etc.) and the codebase analysis (including `grep` for TODOs) to:
1.  Summarize current major issues and architectural deviations from the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.
2.  Provide a prioritized, step-by-step roadmap to address these issues, focusing on stabilizing V2, achieving proper ADK integration, implementing persistence, and completing domain models.

The document is saved at `project_documentation/current_state_and_roadmap/current_state_assessment.md`.
