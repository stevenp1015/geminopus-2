# Architectural Gap Analysis: Ideal vs. Current

This document compares the current codebase against the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.

## Section 1: Core Architectural Principles
### 1.1 Domain-Driven Design
*   **Ideal:** Clear separation into Minion, Communication, Task, Tool, Session domains.
*   **Current:**
    *   `Minion Domain`: Partially implemented in `gemini_legion_backend/core/domain/minion.py`, `emotional.py`, `memory.py`. Lacks richness of ideal (e.g., full `EmotionalState`, multi-layer `MemorySystem`).
    *   `Communication Domain`: Partially present with `Channel`, `Message` in `gemini_legion_backend/core/domain/communication.py`. `InterMinionCommunicationSystem` from ideal is not present.
    *   `Task Domain`: Basic `Task` model exists. `TaskMasterAgent` and detailed orchestration not implemented.
    *   `Tool Domain`: `MCPToolbeltFramework` not implemented. Tool integration is basic.
    *   `Session Domain`: Handled by ADK's `SessionService`. Custom session domain logic minimal.
*   **Gap:** Significant. Core domain objects are placeholders or missing advanced features. The sophisticated engines (Emotional, Memory, Task Orchestration, Tool Framework) are not realized.

### 1.2 Event-Driven Architecture
*   **Ideal:** All significant state changes emit events; loose coupling via event bus; real-time GUI updates.
*   **Current:** An event bus (`GeminiEventBus`) is implemented and used by services (`MinionServiceV2`, `ChannelServiceV2`). WebSocket bridge exists for GUI updates.
*   **Gap:** Foundationally good. The *scope* of events and the richness of event data may not yet match the ideal if domain objects are incomplete. For example, granular emotional change events or memory consolidation events are not yet possible.

### 1.3 Layered Architecture
*   **Ideal:** GUI -> API Gateway -> App Services -> Core Domain -> Infrastructure.
*   **Current:** Broadly follows this. FastAPI for API Gateway, services in `application/services`, domain objects in `core/domain`, ADK adapters/persistence in `core/infrastructure`.
*   **Gap:** Layers exist, but the components within each layer (especially Domain and Application Services) are underdeveloped compared to the ideal.

## Section 2: AeroChat Emotional Engine Architecture
*   **Ideal:** Structured `EmotionalState`, `MoodVector`, `OpinionScore`. LLM as Emotional Policy Engine. Diaries as rich logs.
*   **Current:**
    *   `EmotionalState`: Simplified version in `emotional.py`. Missing `opinion_scores`, `relationship_graph`, `response_tendency`, `conversation_style`, `self_reflection_notes`, `goal_priorities`.
    *   `MoodVector`: Basic version exists. Missing secondary dimensions (`curiosity`, `creativity`, `sociability`) and `to_prompt_modifier()`.
    *   `OpinionScore`: Not implemented.
    *   `EmotionalPolicyEngine`: Not implemented.
    *   `PersonalDiary`: Not implemented.
*   **Gap:** Critical. The current emotional model is rudimentary and lacks the depth and structured components of the ideal architecture.

## Section 3: Minion Memory Architecture
*   **Ideal:** Multi-layered memory system (Working, Short-term, Episodic, Semantic, Procedural). Memory consolidation and forgetting.
*   **Current:** Basic `WorkingMemory` class exists. Other layers and `MinionMemorySystem`, `MemoryConsolidator` are not implemented.
*   **Gap:** Critical. The sophisticated, human-like memory architecture is almost entirely absent.

## Section 4: ADK Agent Design
*   **Ideal:** Idiomatic `MinionAgent(LlmAgent)` with emotional/memory integration in `think`/`predict`. Specialized agents like `TaskMasterAgent`.
*   **Current:** `ADKMinionAgent` extends `LlmAgent`. It attempts to prepare emotional/memory cues for `Session.state`, but the underlying engines are missing, and Runner invocation is problematic. Specialized agents not implemented.
*   **Gap:** Foundational `ADKMinionAgent` exists but lacks the deep integration with non-existent emotional/memory engines. The `predict()` strategy outlined in the ideal architecture is currently blocked due to reported "method not found" issues, which contradicts the `Project_Context_Crucible.md`.

## Section 5: Inter-Minion Communication Architecture
*   **Ideal:** Multi-modal system (Conversational, Structured Data, Event-Driven, RPC). Autonomous messaging. Loop safeguards.
*   **Current:** Basic channel/message system exists. Advanced layers, autonomous messaging, and safeguards are not implemented.
*   **Gap:** Significant. Current system only supports basic user-to-minion or potentially minion-to-channel broadcast.

## Section 6: Generalized MCP Toolbelt Integration Framework
*   **Ideal:** ADK-native tool architecture, dynamic discovery.
*   **Current:** Basic tool definition and passing to `LlmAgent` constructor. `MCPToolbeltFramework` not implemented.
*   **Gap:** Significant. Advanced tool management and dynamic integration are missing.

## Section 7: Transcending Prior Limitations
*   **Ideal:** Distributed intelligence, scalable state management, production-ready error handling.
*   **Current:**
    *   `DistributedIntelligence`: Not implemented. Current model is monolithic agent intelligence.
    *   `ScalableStateManagement`: `InMemorySessionService` used. Ideal specifies Redis, MongoDB, etc. This is a future scalability concern, not an immediate bug for functionality.
    *   `ResilientMinionSystem`: Basic error handling in services. Advanced resilience patterns (circuit breakers, retries) not systematically implemented.
*   **Gap:** Significant for production-readiness, but secondary to getting core agent functionality working.

---
*Analysis in progress. Detailed findings for each architectural component will be added.*
