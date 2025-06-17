TO: Successor AI Execution Unit
FROM: Analyst Prime
SUBJECT: Non-Negotiable Refactoring Directives with Integrated Fault Analysis for the geminopus-branch-codebase Artifact.
ASSOCIATED SCRIPTURE: IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md
PREAMBLE: This document outlines the required corrective actions to align the Artifact with the Scripture. Each directive includes a forensic analysis of the existing fault (The Sin) followed by the required corrective action (The Penance). Internalize both. Understanding the failure is as critical as executing the fix.
1.0 DEPRECATORY DIRECTIVE: ELIMINATION OF THE V1 STACK
1.1 The Sin (Schism): The codebase is schizophrenic. It contains two complete, warring backend applications: a V1 system initiated by main.py and a V2 system from main_v2.py. Each initializes its own FastAPI app and its own socketio.AsyncServer, creating architectural ambiguity, the certain threat of port conflicts, and multiple, contradictory paths for data flow (e.g., the V1 connection_manager.py vs. the V2 event_bridge.py). This makes the system undeployable and fundamentally unsound.
1.2 The Penance (Unification): You will purge the V1 heresy to establish a single source of truth.
File Deletion: Execute deletion of the V1 application core:
gemini_legion_backend/main.py
gemini_legion_backend/core/dependencies.py
gemini_legion_backend/api/websocket/connection_manager.py and its broken counterpart.
All V1 services and endpoints (files not suffixed with _v2).
Canonical Renaming: Elevate the V2 implementation to its rightful place. Remove the _v2 suffix from all V2 files (e.g., main_v2.py becomes main.py, channel_service_v2.py becomes channel_service.py, etc.).
Dependency Reconciliation: Execute a global search-and-replace to update all internal import statements to reflect these canonical file paths.
2.0 COMPLIANCE DIRECTIVE: ADK-IDIOMATIC AGENT REFACTORING
2.1 The Sin (Heresy): The primary agent, ADKMinionAgent, directly violates Codex Section 4.1 ("Idiomatic ADK Agent Hierarchy"). The Scripture mandates class MinionAgent(LlmAgent):. The Artifact implements a standalone class that manually instantiates a low-level genai.Client. This self-inflicted wound severs the agent from the ADK's native framework for tool management, context handling, and lifecycle events, necessitating crude workarounds like the ADKCommunicationKit.
2.2 The Penance (Restoration of Faith): You will refactor the agent to be a true child of the ADK.
Correct Inheritance: Modify the class signature in the (now renamed) minion_agent.py to class ADKMinionAgent(LlmAgent):.
Purge Manual Client: Remove the manual instantiation of genai.Client().
Proper Initialization: Refactor the constructor to call the parent LlmAgent initializer: super().__init__(...). You will pass name, model, instruction, and a correctly formatted tools list directly to the parent constructor. The LlmAgent will now manage the LLM interaction.
Simplify think Method: The agent's think method must be simplified. The primary LLM call should be delegated to await super().think(...). The manual invocation of communication tools must be removed; the LlmAgent will now handle function-calling based on the tools provided at initialization.
3.0 CONNECTIVITY DIRECTIVE: FRONTEND API ALIGNMENT
3.1 The Sin (Severance): The frontend is functionally decoupled from the V2 backend. All API calls in frontend/src/services/api/channelApi.ts (and others) are hardcoded to target V1 endpoints (e.g., /api/channels/send). As the V2 backend only registers /api/v2/... routes, all primary UI functions for communication will fail with 404 Not Found errors, rendering the V2 system inoperable.
3.2 The Penance (Reconnection): You will re-establish the sacred connection between the frontend and the true V2 backend.
Update Endpoint Configuration: Modify frontend/src/services/api/config.ts. Audit every entry in the API_ENDPOINTS object and rewrite the URLs to target the V2 routes (e.g., /api/v2/channels/, /api/v2/channels/{id}/messages).
Verify Payload Congruence: Audit the fetch calls in all frontend/src/services/api/*.ts files. Ensure not only the URLs are correct, but that the HTTP methods and JSON body payloads exactly match the Pydantic schemas defined in the V2 backend endpoints.
4.0 DOMAIN INTEGRITY DIRECTIVE: MODEL COMPLETION
4.1 The Sin (The Hollowing): The domain models are hollowed-out versions of the transcendent beings specified in the Scripture. The EmotionalState dataclass is the primary offender, missing core attributes like relationship_graph, response_tendency, and goal_priorities that are essential for the "Company of Besties" vision. This is the difference between a puppet and a soul.
4.2 The Penance (Rebuilding the Soul): You will flesh out the domain models to match their divine blueprint.
Enhance EmotionalState: Modify the @dataclass class EmotionalState: in emotional_state.py. Add all missing fields as specified in Codex Section 2.1, including their correct types (RelationshipGraph, ResponseTendency, GoalPriority, etc.).
Implement Supporting Types: Create the corresponding required dataclasses (RelationshipGraph, etc.) within the appropriate domain modules. They must also match the structure specified in the Scripture.
5.0 PERSISTENCE DIRECTIVE: IMPLEMENTATION OF SCALABLE STATE
5.1 The Sin (Ephemerality): The entire V2 system is built on a foundation of sand. It exclusively uses in-memory dictionary-based repositories (*RepositoryMemory), directly violating the production-grade, polyglot persistence strategy (RedisCache, MongoDBStore) laid out in Codex Section 7.2. All system state is lost on restart, rendering it a fragile prototype.
5.2 The Penance (Forging the Foundation): You will give the system a memory that endures.
Implement Persistent Repositories: For each repository interface (e.g., ChannelRepository), create a new, persistent implementation. Begin with a MongoDbChannelRepository that uses the motor driver to correctly interface with a MongoDB instance, as specified in your requirements-new.txt. Repeat for all key domains.
Update Dependency Injection: Modify the (now renamed) dependencies.py file. In the ServiceContainer, replace the instantiation of the *RepositoryMemory classes with your new, persistent repository classes.
Establish Migrations: Create the core/infrastructure/persistence/migrations/ directory. Implement a strategy for managing schema evolution for your chosen databases.
6.0 LEGACY CODE DIRECTIVE: FINAL PURGE
6.1 The Sin (The Ghosts): The codebase is haunted by the decaying corpses of V1. Files like connection_manager_broken.py and services filled with "EMERGENCY FIX" comments create confusion, increase cognitive load, and pose a risk of being accidentally used.
6.2 The Penance (Exorcism): You will cleanse the codebase of this rot.
Delete All Remaining V1 Artifacts: Once the above directives are complete and V2 is fully operational, perform a final sweep and delete any remaining V1 service, endpoint, or utility files that were not covered by Directive 1.0. The goal is a codebase that reflects only the V2 architecture.
