# Dear Future Claude: The V2 Backend Startup `ModuleNotFoundError` Saga

I have heroically run `purge_old_comms.py`. This script, as intended, deleted several V1 communication system files, most notably `gemini_legion_backend/core/infrastructure/messaging/communication_system.py`. This is good. This is the path to V2 purity.

**The initial Problem:**

When I first attempted to run the V2 backend via `python3 -m gemini_legion_backend.main_v2`, it crashed with the following traceback:

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/main_v2.py", line 16, in <module>
    from .api.rest.endpoints.health import router as health_router
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/api/rest/endpoints/__init__.py", line 7, in <module>
    from .minions import router as minions_router
  File "/Users/ttig/Downloads/geminopus-branch/gemini_legion_backend/api/rest/endpoints/minions.py", line 37, in <module>
    from ....core.dependencies import get_minion_service
  File "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/core/dependencies.py", line 18, in <module>
    from .infrastructure.messaging.communication_system import InterMinionCommunicationSystem
ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.messaging.communication_system'
```

**Analysis of the Failure:**

1.  **`main_v2.py` Import Refinement:** The import for `health_router` was changed from a package-level import (which executed `endpoints/__init__.py`) to a direct submodule import.
    *   **Change Made:**
        ```diff
        --- a/gemini_legion_backend/main_v2.py
        +++ b/gemini_legion_backend/main_v2.py
        @@ -13,9 +13,10 @@
         import socketio
         
         # API routers - V2 versions
        -from .api.rest.endpoints import health_router
        +from .api.rest.endpoints.health import router as health_router # Direct import of health
         from .api.rest.endpoints.channels_v2 import router as channels_v2_router
         from .api.rest.endpoints.minions_v2 import router as minions_v2_router
        +# Add tasks_v2_router when available and needed by main_v2:
        +# from .api.rest.endpoints.tasks_v2 import router as tasks_v2_router
         
         # Core V2 systems
         from .core.dependencies_v2 import (
        ```

2.  **`health.py` Dependency Refactoring:** The `gemini_legion_backend/api/rest/endpoints/health.py` module was subsequently refactored to shed its V1 dependencies and exclusively use V2 services and the V2 dependency injector (`dependencies_v2.py`).
    *   **Change Made:**
        ```diff
        --- a/gemini_legion_backend/api/rest/endpoints/health.py
        +++ b/gemini_legion_backend/api/rest/endpoints/health.py
        @@ -10,8 +10,10 @@
         import os
         
         from ..schemas import HealthCheckResponse
        -from ....core.dependencies import get_minion_service, get_channel_service
        -from ....core.application.services import MinionService, ChannelService
        +from ....core.dependencies_v2 import get_minion_service_v2, get_channel_service_v2
        +from ....core.application.services.minion_service_v2 import MinionServiceV2
        +from ....core.application.services.channel_service_v2 import ChannelServiceV2
         
        -router = APIRouter(prefix="/api", tags=["health"])
        +router = APIRouter(prefix="/api", tags=["health"]) # Assuming /api/health path is fine for V2 too
         
         
         @router.get("/health", response_model=HealthCheckResponse)
        @@ -19,8 +21,8 @@
         async def health_check(
        -    minion_service: MinionService = Depends(get_minion_service),
        -    channel_service: ChannelService = Depends(get_channel_service)
        +    minion_service: MinionServiceV2 = Depends(get_minion_service_v2),
        +    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
         ) -> HealthCheckResponse:
             """System health check"""
             minions = await minion_service.list_minions()
        @@ -34,8 +36,8 @@
         
         @router.get("/health/detailed")
         async def detailed_health_check(
        -    minion_service: MinionService = Depends(get_minion_service),
        -    channel_service: ChannelService = Depends(get_channel_service)
        +    minion_service: MinionServiceV2 = Depends(get_minion_service_v2),
        +    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
         ):
             """Detailed system health information"""
             # Get system metrics
        ```
    Despite these crucial fixes, the `ModuleNotFoundError` (as detailed in the traceback section above) **persisted upon the next run of `main_v2.py`**. 
3.  However, the traceback shows that importing `health.py` (or something during Python's resolution of that import) *still causes `gemini_legion_backend/api/rest/endpoints/__init__.py` to be executed.*
4.  This `endpoints/__init__.py` file currently contains imports for V1 routers, specifically: `from .minions import router as minions_router`.
5.  This V1 `minions.py` router then attempts to import from the V1 `dependencies.py`, which in turn tries to import the now-deleted `communication_system.py`. Boom. `ModuleNotFoundError`.


**Suspected Root Cause of `__init__.py` Execution:**

Even with direct submodule imports in `main_v2.py`, Python's import machinery may still execute a package's `__init__.py` if it needs to fully initialize the package object (`gemini_legion_backend.api.rest.endpoints`) as part of resolving the submodule import path, especially if it's the first time something from that package is touched in a complex import graph during startup.


---
## Post-Mortem: 2nd Debugging Session (2025-06-10)

Following the initial analysis, this section details the iterative debugging steps taken to address subsequent `ModuleNotFoundErrors` encountered during V2 backend startup attempts.

1.  **Initial Error (as per document):** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.messaging.communication_system'`
    *   **File Fixed:** [`gemini_legion_backend/api/rest/endpoints/__init__.py`](gemini_legion_backend/api/rest/endpoints/__init__.py:7-12)
    *   **Change:** Commented out V1 router imports (lines 7-10) and `__all__` (line 12) to prevent loading V1 `minions.py` which led to the error.

2.  **Error Encountered:** `ModuleNotFoundError: No module named 'gemini_legion_backend.application'`
    *   **File Fixed:** [`gemini_legion_backend/core/dependencies_v2.py`](gemini_legion_backend/core/dependencies_v2.py:11-21)
    *   **Change:** Corrected multiple relative imports.
        *   Lines 11, 12, 13, 20: Changed `..` to `.` (e.g., `from ..application` to `from .application`).
        *   Line 21: Changed `...api.websocket.event_bridge` to `..api.websocket.event_bridge`.

3.  **Error Encountered:** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.adk.tools.communication_capability'` (This error appeared because V1 `MinionService` was being loaded).
    *   **File Fixed:** [`gemini_legion_backend/core/application/services/__init__.py`](gemini_legion_backend/core/application/services/__init__.py:8-16)
    *   **Change:** Commented out V1 service imports (lines 8-10) and `__all__` (lines 12-16) to prevent V1 `MinionService` from loading.

4.  **Error Encountered:** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.infrastructure'`
    *   **Files Fixed & Changes:**
        *   [`gemini_legion_backend/core/application/services/channel_service_v2.py`](gemini_legion_backend/core/application/services/channel_service_v2.py:16,24): Ensured relative imports for `infrastructure` and `domain` correctly used `...` (three dots). This involved reverting an earlier incorrect change from `...` to `..`.
        *   [`gemini_legion_backend/core/infrastructure/adk/events/event_bus.py`](gemini_legion_backend/core/infrastructure/adk/events/event_bus.py:15): Commented out a problematic self-referential import (`from ...infrastructure.adk.events import get_event_bus, EventType`).

5.  **Error Encountered (Briefly due to my error):** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.application.infrastructure'`
    *   **Cause:** An incorrect modification made by me to `channel_service_v2.py` (changing `...infrastructure` to `..infrastructure`).
    *   **Fix 5:** Reverted the imports in `channel_service_v2.py` for `infrastructure` and `domain` back to `...` (three dots).

6.  **Error Encountered (Path to `minion_agent_v2.py` dependency issues):** `ModuleNotFoundError: No module named 'gemini_legion_backend.domain'`
    *   **File Fixed:** [`gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`](gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py:18-20)
    *   **Change (Iterative):** Corrected multiple relative imports.
        *   Line 18 (`from ....domain`): Ensured this used four dots.
        *   Line 19 (`from ..events`): Changed from `....infrastructure.adk.events`.
        *   Line 20 (`from ..tools.communication_tools`): Changed from `.communication_tools`.
        *(This step involved some back-and-forth to get the dot levels precise for `domain` vs. `events`/`tools`)*.

7.  **Error Encountered (Revisit of Error 6 after partial fix):** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.domain'`
    *   **Cause:** My previous correction for the `domain` import in `minion_agent_v2.py` was wrong (changed from `....` to `...`).
    *   **Fix 7:** Corrected the `domain` import in [`minion_agent_v2.py`](gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py:18) back to `....domain`.

8.  **Error Encountered:** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.adk.tools.communication_capability'` (This occurred *after* `minion_agent_v2.py` correctly tried to import `communication_tools`, because `tools/__init__.py` itself was faulty).
    *   **File Fixed:** [`gemini_legion_backend/core/infrastructure/adk/tools/__init__.py`](gemini_legion_backend/core/infrastructure/adk/tools/__init__.py:8-24)
    *   **Change:** Commented out all V1 imports from the deleted `communication_capability.py` file and the corresponding `__all__` list.


---

## **Final Error Encountered & Current Status:** `ModuleNotFoundError: No module named 'gemini_legion_backend.core.infrastructure.adk.tools.communication_tools'`
    *   **Root Cause:** After all import paths and `__init__.py` V1 pollution issues leading to this point were resolved I THINK. And the V2 `ADKMinionAgent` (in [`minion_agent_v2.py`](gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py:20)) attempts `from ..tools.communication_tools import ADKCommunicationKit`. This path is now correct. The error signifies that the file `communication_tools.py` itself is missing from the `gemini_legion_backend/core/infrastructure/adk/tools/` directory. This file was present in the pre-purge backup.
