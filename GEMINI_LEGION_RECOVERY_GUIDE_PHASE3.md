# Gemini Legion - Step-by-Step Recovery and Enhancement Guide - PHASE 3

## Phase 3: System Robustness & Completeness

### Major Task 3.1: Task Domain Full Integration (Backend)

**Context for this major task:**
The IADD specifies a Task Domain for managing task lifecycle, decomposition, and orchestration. While domain models (`Task`, `SubTask`, etc. in `domain/task.py`) and a service (`application/services/task_service_v2.py`) exist, they are not fully integrated into the main application flow or exposed via the V2 API. This task will wire up the `TaskServiceV2`, create API endpoints, and ensure task-related events are properly handled.

---
**Step 3.1.1: Integrate `TaskServiceV2` into the Dependency Injection Container**

**Objective:**
*   Make `TaskServiceV2` available throughout the application via the central service container.

**File(s) to Modify:**
*   `gemini_legion_backend/core/dependencies_v2.py`

**Context & Reasoning:**
*   The `ServiceContainerV2` in `dependencies_v2.py` is responsible for instantiating and providing access to all core services. `TaskServiceV2` needs to be part of this to be used by API endpoints and potentially other services (though direct inter-service calls are minimized in favor of events).
*   The `TaskServiceV2` depends on `TaskRepository`. The existing `TaskRepositoryMemory` will be used.

**Detailed Instructions:**

*   **In `gemini_legion_backend/core/dependencies_v2.py`:**
    *   Import `TaskServiceV2`.
    *   In the `ServiceContainerV2.__init__` method, ensure `TaskRepositoryMemory` is instantiated (it should already be there) and then instantiate `TaskServiceV2`, passing the repository.
    *   Add `TaskServiceV2` to the `start_all` and `stop_all` methods of the container.
    *   Add a getter method `get_task_service()` to the container.
    *   Add a FastAPI dependency provider function `get_task_service_v2()`.

    ```python
    # In gemini_legion_backend/core/dependencies_v2.py
    # ... other imports ...
    from .application.services.task_service_v2 import TaskServiceV2 # Add this if not present
    from .infrastructure.persistence.repositories.memory import (
        ChannelRepositoryMemory,
        MessageRepositoryMemory,
        MinionRepositoryMemory,
        TaskRepositoryMemory # Ensure this is imported and used
    )
    from google.adk.sessions import InMemorySessionService # Ensure this is imported
    from gemini_legion_backend.api.websocket.event_bridge import WebSocketEventBridge # Ensure this is imported
    from typing import Optional # Ensure Optional is imported
    import os # Ensure os is imported
    import logging # Ensure logging is imported
    logger = logging.getLogger(__name__) # Ensure logger is defined


    class ServiceContainerV2:
        def __init__(self):
            # Repositories
            self.channel_repo = ChannelRepositoryMemory()
            self.message_repo = MessageRepositoryMemory()
            self.minion_repo = MinionRepositoryMemory()
            self.task_repo = TaskRepositoryMemory() # Ensure this line exists and is correct

            self.event_bus = get_event_bus() # Ensure get_event_bus is imported from .infrastructure.adk.events
            self.session_service = InMemorySessionService()

            self.channel_service = ChannelServiceV2(
                channel_repository=self.channel_repo,
                message_repository=self.message_repo
            )

            self.minion_service = MinionServiceV2(
                minion_repository=self.minion_repo,
                api_key=os.getenv("GEMINI_API_KEY"),
                session_service=self.session_service
            )

            # Add TaskServiceV2 instantiation
            self.task_service = TaskServiceV2(
                task_repository=self.task_repo
            )

            self.websocket_bridge: Optional[WebSocketEventBridge] = None
            logger.info("ServiceContainerV2 initialized with clean architecture, including TaskServiceV2.")

        async def start_all(self):
            logger.info("Starting all services...")
            await self.channel_service.start()
            await self.minion_service.start()
            await self.task_service.start() # Start TaskServiceV2
            logger.info("All services started")

        async def stop_all(self):
            logger.info("Stopping all services...")
            # Stop in reverse order of start, or as appropriate
            await self.task_service.stop()
            await self.minion_service.stop()
            await self.channel_service.stop()
            logger.info("All services stopped")

        def get_channel_service(self) -> ChannelServiceV2: # Ensure ChannelServiceV2 is imported
            return self.channel_service

        def get_minion_service(self) -> MinionServiceV2: # Ensure MinionServiceV2 is imported
            return self.minion_service

        def get_event_bus(self): # Consider adding return type hint if EventBus class is defined
            return self.event_bus

        def get_task_service(self) -> TaskServiceV2: # Add this getter
            """Get task service"""
            return self.task_service

    # Global container instance
    _container: Optional[ServiceContainerV2] = None

    async def initialize_services_v2():
        global _container
        if _container is not None:
            logger.warning("Services already initialized")
            return
        logger.info("Initializing services with clean architecture...")
        _container = ServiceContainerV2()
        await _container.start_all()
        logger.info("Services initialized successfully")

    async def shutdown_services_v2():
        global _container
        if _container is None:
            logger.warning("No services to shutdown")
            return
        logger.info("Shutting down services...")
        await _container.stop_all()
        _container = None
        logger.info("Services shutdown complete")

    def get_service_container_v2() -> ServiceContainerV2:
        global _container
        if _container is None:
            raise RuntimeError("Services not initialized. Call initialize_services_v2() first.")
        return _container

    # FastAPI dependency providers
    def get_channel_service_v2() -> ChannelServiceV2:
        return get_service_container_v2().get_channel_service()

    def get_minion_service_v2() -> MinionServiceV2:
        return get_service_container_v2().get_minion_service()

    def get_event_bus_dep(): # Consider adding return type hint
        return get_service_container_v2().get_event_bus()

    def get_task_service_v2() -> TaskServiceV2: # Add this provider
        """FastAPI dependency for task service"""
        return get_service_container_v2().get_task_service()
    ```

    *   **Explanation of Changes:**
        *   Imported `TaskServiceV2` and ensured other necessary imports like `Optional`, `os`, `logging`, `InMemorySessionService`, `WebSocketEventBridge`, and `get_event_bus` are present.
        *   Ensured `TaskRepositoryMemory` is instantiated and passed to `TaskServiceV2`.
        *   Added `self.task_service.start()` and `self.task_service.stop()` calls.
        *   Added `get_task_service()` method and `get_task_service_v2()` FastAPI dependency provider.

**Verification:**
1.  Restart the backend server: `python3 -m gemini_legion_backend.main_v2`.
2.  Check logs for:
    *   "ServiceContainerV2 initialized with clean architecture, including TaskServiceV2."
    *   During startup: "Starting Task Service V2..." and "Task Service V2 started successfully."
    *   During shutdown (e.g., Ctrl+C): "Stopping Task Service V2..." and "Task Service V2 stopped."
3.  The server should start and stop without errors related to `TaskServiceV2` initialization or lifecycle.

**Potential Pitfalls:**
*   Incorrect import paths.
*   `TaskServiceV2` missing `start()` or `stop()` async methods (the provided `task_service_v2.py` has them).
*   Forgetting to add the service to `start_all` and `stop_all`.

**State of the System After This Step:**
*   `TaskServiceV2` is correctly initialized as part of the application lifecycle.
*   It is now available for use by other components, primarily API endpoints, via dependency injection.

---
**Step 3.1.2: Create Basic Task API Endpoints (Router and Schemas)**

**Objective:**
*   Create a new FastAPI router (`tasks_v2.py`) for task-related V2 endpoints.
*   Define basic Pydantic schemas for task creation requests and responses.
*   Implement initial GET (list tasks, get task by ID) and POST (create task) endpoints.

**File(s) to Modify/Create:**
*   `gemini_legion_backend/api/rest/schemas.py` (or create `gemini_legion_backend/api/rest/task_schemas.py` and import appropriately)
*   Create `gemini_legion_backend/api/rest/endpoints/tasks_v2.py`
*   `gemini_legion_backend/main_v2.py` (to include the new router)

**Context & Reasoning:**
*   To interact with the `TaskServiceV2`, API endpoints are needed. This aligns with the IADD's layered architecture.
*   Pydantic schemas ensure data validation and serialization for API requests/responses.

**Detailed Instructions:**

1.  **Define Task Schemas in `gemini_legion_backend/api/rest/schemas.py`:**
    *   Add or ensure the following Pydantic models are present and correctly defined.

    ```python
    # In gemini_legion_backend/api/rest/schemas.py
    from pydantic import BaseModel, Field
    from typing import List, Optional, Dict, Any
    from datetime import datetime
    from enum import Enum as PyEnum

    # API-specific Enums (can map to domain enums in the service or endpoint)
    class TaskStatusAPI(str, PyEnum):
        PENDING = "pending"
        ASSIGNED = "assigned"
        DECOMPOSED = "decomposed"
        IN_PROGRESS = "in_progress"
        BLOCKED = "blocked"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    class TaskPriorityAPI(str, PyEnum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class CreateTaskRequest(BaseModel):
        title: str = Field(..., min_length=1, max_length=255)
        description: str = Field(...)
        priority: TaskPriorityAPI = TaskPriorityAPI.MEDIUM
        assigned_to: Optional[str] = None
        dependencies: Optional[List[str]] = Field(default_factory=list)
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
        # deadline: Optional[datetime] = None # Consider adding later

    class TaskResponse(BaseModel):
        task_id: str
        title: str
        description: str
        status: TaskStatusAPI
        priority: TaskPriorityAPI
        progress: Optional[int] = Field(default=0, ge=0, le=100)
        created_at: datetime
        created_by: Optional[str] = None
        assigned_to: Optional[str] = None # Or List[str] if multiple assignees
        started_at: Optional[datetime] = None
        completed_at: Optional[datetime] = None
        deadline: Optional[datetime] = None
        dependencies: List[str] = Field(default_factory=list)
        metadata: Dict[str, Any] = Field(default_factory=dict)
        # output: Optional[str] = None
        # error_message: Optional[str] = None
        # subtask_ids: Optional[List[str]] = Field(default_factory=list)
        # parent_task_id: Optional[str] = None
        # decomposition: Optional[Dict[str, Any]] = None # Simplified for now

    class TasksListResponse(BaseModel):
        tasks: List[TaskResponse]
        total: int
        # Add limit, offset if you implement pagination in the response
    ```

2.  **Create `gemini_legion_backend/api/rest/endpoints/tasks_v2.py`:**
    *   Implement the router with initial endpoints for creating and listing tasks.

    ```python
    # Create file: gemini_legion_backend/api/rest/endpoints/tasks_v2.py
    from fastapi import APIRouter, HTTPException, Depends, status
    from typing import List, Optional, Dict, Any
    import logging
    import uuid

    from ..schemas import CreateTaskRequest, TaskResponse, TasksListResponse
    from ....core.dependencies_v2 import get_task_service_v2
    from ....core.application.services.task_service_v2 import TaskServiceV2

    logger = logging.getLogger(__name__)
    router = APIRouter(prefix="/api/v2/tasks", tags=["Tasks V2"])

    def _convert_service_task_to_response(task_data: Optional[Dict[str, Any]]) -> Optional[TaskResponse]:
        if not task_data:
            return None

        # Ensure all required fields for TaskResponse are present or have defaults
        response_data = {
            "task_id": task_data.get("task_id"),
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "status": task_data.get("status"),
            "priority": task_data.get("priority"),
            "progress": task_data.get("progress", 0),
            "created_at": task_data.get("created_at"),
            "created_by": task_data.get("created_by"),
            "assigned_to": task_data.get("assigned_to"),
            "started_at": task_data.get("started_at"),
            "completed_at": task_data.get("completed_at"),
            "deadline": task_data.get("deadline"),
            "dependencies": task_data.get("dependencies", []),
            "metadata": task_data.get("metadata", {}),
        }
        # Filter out None values for optional fields if TaskResponse doesn't want them
        # response_data = {k: v for k, v in response_data.items() if v is not None or k in TaskResponse.__fields__}
        return TaskResponse(**response_data)


    @router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    async def create_task_endpoint(
        request: CreateTaskRequest,
        task_service: TaskServiceV2 = Depends(get_task_service_v2)
    ):
        try:
            task_id = f"task_{uuid.uuid4().hex}"
            logger.info(f"API: Received request to create task: {request.title} with id {task_id}")
            task_data_from_service = await task_service.create_task(
                task_id=task_id,
                title=request.title,
                description=request.description,
                priority=request.priority.value,
                assigned_to=request.assigned_to,
                dependencies=request.dependencies,
                metadata=request.metadata
            )
            if not task_data_from_service:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task service created no data.")

            response_obj = _convert_service_task_to_response(task_data_from_service)
            if not response_obj:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to convert task data to response.")
            return response_obj
        except ValueError as e:
            logger.warning(f"API: Value error creating task '{request.title}': {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"API: Error creating task '{request.title}': {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error creating task")

    @router.get("/", response_model=TasksListResponse)
    async def list_tasks_endpoint(
        status_filter: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        task_service: TaskServiceV2 = Depends(get_task_service_v2)
    ):
        try:
            tasks_data_list = await task_service.list_tasks(
                status_filter=status_filter,
                assigned_to=assigned_to,
                limit=limit,
                offset=offset
            )
            converted_tasks = [_convert_service_task_to_response(t) for t in tasks_data_list if t]
            # This assumes task_service.list_tasks returns a list. If it returns a dict with 'tasks' and 'total':
            # total_count = tasks_data_list.get('total', len(converted_tasks))
            # tasks_to_convert = tasks_data_list.get('tasks', converted_tasks)
            return TasksListResponse(
                tasks=converted_tasks,
                total=len(converted_tasks) # Adjust if service provides total count
            )
        except Exception as e:
            logger.error(f"API: Error listing tasks: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing tasks")

    @router.get("/{task_id}", response_model=TaskResponse)
    async def get_task_endpoint(
        task_id: str,
        task_service: TaskServiceV2 = Depends(get_task_service_v2)
    ):
        try:
            task_data = await task_service.get_task(task_id)
            if not task_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID '{task_id}' not found")
            response_obj = _convert_service_task_to_response(task_data)
            if not response_obj:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to convert task data to response.")
            return response_obj
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API: Error getting task {task_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving task")
    ```

3.  **Include the Task Router in `gemini_legion_backend/main_v2.py`:**

    ```python
    # In gemini_legion_backend/main_v2.py
    # ... other imports ...
    from .api.rest.endpoints.health import router as health_router
    from .api.rest.endpoints.channels_v2 import router as channels_v2_router
    from .api.rest.endpoints.minions_v2 import router as minions_v2_router
    from .api.rest.endpoints.tasks_v2 import router as tasks_v2_router # Add this import

    # ... (app = FastAPI(...) and sio setup) ...

    # Include routers
    app.include_router(health_router)
    app.include_router(channels_v2_router)
    app.include_router(minions_v2_router)
    app.include_router(tasks_v2_router) # Add this line

    # ... (rest of main_v2.py)
    ```

**Verification:**
1.  Restart backend. Check API docs at `/api/v2/docs`.
2.  **Expected Outcome:** "Tasks V2" section with POST `/tasks/`, GET `/tasks/`, GET `/tasks/{task_id}`.
3.  Use Postman: POST a task, GET list, GET specific task. Check for 201/200 responses and correct data.
4.  Logs should be clean or show informative messages.

**Potential Pitfalls:**
*   Schema mismatches between `TaskResponse` and `TaskServiceV2` dict output.
*   Forgetting to include `tasks_v2_router` in `main_v2.py`.

**State of the System After This Step:**
*   Basic REST API for task CRUD is functional. System can manage tasks via HTTP.

---
**Step 3.1.3: Ensure Task Events are Emitted by `TaskServiceV2` and Bridged to WebSocket**

**Objective:**
*   Verify `TaskServiceV2` emits events for task changes (create, assign, status update).
*   Ensure `WebSocketEventBridge` forwards these to clients.

**File(s) to Modify:**
*   `gemini_legion_backend/core/infrastructure/adk/events.py` (Verify `EventType` for tasks)
*   `gemini_legion_backend/core/application/services/task_service_v2.py` (Refine event emission)
*   `gemini_legion_backend/api/websocket/event_bridge.py` (Add handlers for task events)

**Context & Reasoning:**
*   EDA for real-time UI (IADD). Frontend needs task event awareness.

**Detailed Instructions:**

1.  **Define/Verify Task EventTypes in `gemini_legion_backend/core/infrastructure/adk/events.py`:**
    ```python
    # In gemini_legion_backend/core/infrastructure/adk/events.py
    from enum import Enum

    class EventType(Enum):
        # ... MINION_* and CHANNEL_* types ...
        MINION_ERROR = "minion.error"

        TASK_CREATED = "task.created"
        TASK_UPDATED = "task.updated"
        TASK_STATUS_CHANGED = "task.status.changed"
        TASK_ASSIGNED = "task.assigned"
        TASK_DECOMPOSED = "task.decomposed"
        TASK_PROGRESS_UPDATE = "task.progress.update"
        TASK_COMPLETED = "task.completed"
        TASK_FAILED = "task.failed"
        TASK_CANCELLED = "task.cancelled"
        TASK_DELETED = "task.deleted"

        SYSTEM_HEALTH = "system.health"
        # ... other system events ...
    ```

2.  **Refine Event Emission in `gemini_legion_backend/core/application/services/task_service_v2.py`:**
    *   Use the `_emit_task_event` helper consistently. Ensure its data payload is comprehensive.
    *   Make sure domain `Task` model has `progress`, `output`, `error`, `subtask_ids` attributes or handle them safely with `getattr`.

    ```python
    # In gemini_legion_backend/core/application/services/task_service_v2.py
    from ....core.infrastructure.adk.events import EventType, Event # Ensure Event is imported
    from ....core.domain.task import Task, TaskStatus, TaskPriority, TaskDecomposition, SubTask, TaskAssignment # Ensure all domain parts are imported
    from enum import Enum as PyEnum # To help with .value for domain enums

    async def _emit_task_event(self, event_type: EventType, task: Task, additional_data: Optional[Dict[str, Any]] = None):
        """Emit task-related events with comprehensive data."""
        event_data = {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if isinstance(task.status, PyEnum) else str(task.status),
            "priority": task.priority.value if isinstance(task.priority, PyEnum) else str(task.priority),
            "progress": getattr(task, 'progress', 0),
            "created_at": task.created_at.isoformat(),
            "created_by": task.created_by,
            "assigned_to": task.assigned_to,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "dependencies": task.dependencies,
            "subtask_ids": getattr(task, 'subtask_ids', []),
            "parent_task_id": task.parent_task_id,
            "metadata": task.metadata,
            "output": getattr(task, 'output', None),
            "error_message": getattr(task, 'error', None)
        }
        if hasattr(task, 'decomposition') and task.decomposition:
            event_data["decomposition"] = {
                "strategy": task.decomposition.strategy.value if isinstance(task.decomposition.strategy, PyEnum) else str(task.decomposition.strategy),
                "subtask_count": len(task.decomposition.subtasks),
            }

        if additional_data:
            event_data.update(additional_data)

        await self.event_bus.emit(
            event_type,
            data=event_data, # This is the dict that will go into event.data
            source=f"task_service:{event_type.value}"
        )
        logger.info(f"Emitted {event_type.value} for task {task.task_id}")

    # In create_task:
    # async def create_task(...):
    #     ...
    #     await self.repository.save(task)
    #     self.active_tasks[task_id] = task
    #     await self._emit_task_event(EventType.TASK_CREATED, task)
    #     return self._task_to_dict(task) # Ensure this returns a dict

    # In auto_assign_task:
    # async def auto_assign_task(...):
    #     ...
    #     await self.repository.save(task)
    #     await self._emit_task_event(EventType.TASK_ASSIGNED, task, additional_data={"minion_name": best_minion["name"], "assignment_score": scored_minions[0][0]})
    #     return { ... } # Ensure this returns a dict

    # In start_task:
    # async def start_task(...):
    #     ...
    #     await self.repository.save(task)
    #     await self._emit_task_event(EventType.TASK_STATUS_CHANGED, task, additional_data={"previous_status": "assigned"}) # Or "pending"
    #     return { ... } # Ensure this returns a dict

    # In update_task_progress:
    # async def update_task_progress(self, task_id: str, progress: int, status_message: Optional[str] = None):
    #     task = self.active_tasks.get(task_id)
    #     if not task: raise ValueError(f"Task {task_id} not found")
    #
    #     # Ensure 'progress' attribute exists or add it dynamically for this operation
    #     # This is a workaround if the domain model doesn't have it yet.
    #     # It's better to add 'progress: int = 0' to the Task domain model.
    #     setattr(task, 'progress', progress)
    #     # setattr(task, 'last_updated', datetime.now()) # Assuming Task model has last_updated
    #
    #     current_status_before_update = task.status
    #     new_status = task.status
    #
    #     if progress >= 100 and task.status != TaskStatus.COMPLETED:
    #         new_status = TaskStatus.COMPLETED
    #         task.completed_at = datetime.now()
    #     elif task.status not in [TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.COMPLETED]:
    #         new_status = TaskStatus.IN_PROGRESS
    #
    #     task.status = new_status
    #     await self.repository.save(task)
    #
    #     if new_status == TaskStatus.COMPLETED:
    #         await self._emit_task_event(EventType.TASK_COMPLETED, task)
    #     elif new_status == TaskStatus.FAILED: # This condition might be set elsewhere
    #         await self._emit_task_event(EventType.TASK_FAILED, task)
    #     elif new_status != current_status_before_update:
    #          await self._emit_task_event(EventType.TASK_STATUS_CHANGED, task, additional_data={"status_message": status_message, "previous_status": current_status_before_update.value})
    #     else: # Just a progress update without status change
    #          await self._emit_task_event(EventType.TASK_PROGRESS_UPDATE, task, additional_data={"status_message": status_message})
    #     return self._task_to_dict(task)

    # Ensure _task_to_dict also includes all these fields for consistency in API responses.
    ```

3.  **Add Handlers to `WebSocketEventBridge` in `gemini_legion_backend/api/websocket/event_bridge.py`:**
    ```python
    # In gemini_legion_backend/api/websocket/event_bridge.py
    from ....core.infrastructure.adk.events import Event, EventType # Ensure Event is imported

    class WebSocketEventBridge:
        def _setup_event_subscriptions(self):
            # ... (existing channel and minion subscriptions) ...

            task_event_types = [
                EventType.TASK_CREATED, EventType.TASK_UPDATED, EventType.TASK_STATUS_CHANGED,
                EventType.TASK_ASSIGNED, EventType.TASK_DECOMPOSED, EventType.TASK_PROGRESS_UPDATE,
                EventType.TASK_COMPLETED, EventType.TASK_FAILED, EventType.TASK_CANCELLED,
                EventType.TASK_DELETED
            ]
            for event_type in task_event_types:
                if hasattr(event_type, 'value'): # Check if it's a valid enum member
                    self.event_bus.subscribe(event_type, self._handle_task_event)

            logger.info("WebSocketEventBridge subscribed to all relevant events, including detailed task events")

        async def _handle_task_event(self, event: Event):
            task_id = event.data.get("task_id")
            if not task_id:
                logger.warning(f"Task event received without task_id: {event.type.value if isinstance(event.type, Enum) else event.type}, data: {event.data}")
                return

            ws_event_name = "task_event"

            payload = {
                "event_type": event.type.value if isinstance(event.type, Enum) else str(event.type),
                "task_id": task_id,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }

            await self.sio.emit(ws_event_name, payload)
            logger.debug(f"Broadcast {payload['event_type']} (as {ws_event_name}) for task {task_id}. Data keys: {list(event.data.keys())}")
    ```

**Verification:**
1.  Restart backend. Connect WebSocket client. Use API to create/update tasks.
2.  **Expected Outcome:** Logs show `TaskServiceV2` emitting events. WebSocket client receives `task_event` with `event_type` and full task data in `payload.data`.

**Potential Pitfalls:**
*   Missing `EventType` members. Payload structure mismatch for frontend.

**State of the System After This Step:**
*   Task state changes are propagated via event bus and WebSockets.

---

### Major Task 3.2: Frontend Real-time Update Enhancements

**Context for this major task:**
Backend emits `task_event`. Frontend `taskStore.ts` needs to process these for real-time UI.

---
**Step 3.2.1: Define/Update Frontend Task Types**

**Objective:**
*   Ensure frontend TypeScript types for `Task` (and related) in `gemini_legion_frontend/src/types/index.ts` match backend event payloads.

**File(s) to Modify:**
*   `gemini_legion_frontend/src/types/index.ts` (or `types/task.ts`)

**Context & Reasoning:**
*   Accurate types for handling backend data in Zustand and React.

**Detailed Instructions:**

*   **In `gemini_legion_frontend/src/types/index.ts` (or `types/task.ts`):**
    *   Review and update `Task`, `TaskDecompositionFE`, `SubTask`, `TaskEventData`, `WebSocketTaskPayload`.

    ```typescript
    // In gemini_legion_frontend/src/types/index.ts or types/task.ts

    export type TaskStatus = 'pending' | 'assigned' | 'decomposed' | 'in_progress' | 'blocked' | 'completed' | 'failed' | 'cancelled';
    export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

    export interface ExecutionLogEntry {
      timestamp: string;
      message: string;
      level: 'info' | 'warning' | 'error' | 'debug';
    }

    export interface SubTask {
        subtask_id: string;
        parent_task_id: string;
        title: string;
        description: string;
        status: TaskStatus;
        complexity: string;
        suggested_minion_type?: string;
        dependencies: string[];
    }

    export interface TaskDecompositionFE {
        strategy: string;
        subtask_count: number;
        // subtasks?: SubTask[]; // Keep this optional or ensure backend sends it if needed
    }

    export interface Task {
      task_id: string;
      title: string;
      description: string;
      status: TaskStatus;
      priority: TaskPriority;
      progress?: number;
      created_at: string;
      created_by?: string;
      assigned_to?: string | string[] | null;
      started_at?: string | null;
      completed_at?: string | null;
      deadline?: string | null;
      dependencies?: string[];
      subtask_ids?: string[];
      parent_task_id?: string | null;
      metadata?: Record<string, any>;
      output?: string | null;
      error_message?: string | null;
      artifacts?: string[];
      assignment_history?: any[];
      execution_log?: ExecutionLogEntry[];
      decomposition?: TaskDecompositionFE | null;
    }

    // For API POST to /api/v2/tasks/
    export interface CreateTaskRequestData { // Renamed from CreateTaskData to avoid conflict if used elsewhere
        title: string;
        description: string;
        priority?: TaskPriority; // Should match TaskPriorityAPI from backend schemas.py
        assigned_to?: string;
        dependencies?: string[];
        metadata?: Record<string, any>;
    }

    // For API PUT /api/v2/tasks/{task_id}
    export interface UpdateTaskRequestData extends Partial<CreateTaskRequestData> {
        status?: TaskStatus;
        progress?: number;
        assigned_to?: string | string[]; // Or just string if API expects one
        output?: string;
        error_message?: string;
        title?: string;
    }

    // Interface for the data within WebSocket 'task_event' payload.data
    // This should mirror the fields sent by backend's _emit_task_event
    export interface TaskEventData {
      task_id: string;
      title: string;
      description: string;
      status: TaskStatus;
      priority: TaskPriority;
      progress?: number;
      created_at: string;
      created_by?: string;
      assigned_to?: string | string[] | null;
      started_at?: string | null;
      completed_at?: string | null;
      deadline?: string | null;
      dependencies?: string[];
      subtask_ids?: string[];
      parent_task_id?: string | null;
      metadata?: Record<string, any>;
      output?: string | null;
      error_message?: string | null;
      // Fields specific to certain events, if any, from additional_data in _emit_task_event
      minion_name?: string;
      assignment_score?: number;
      status_message?: string;
      previous_status?: string;
      decomposition?: TaskDecompositionFE | null;
    }

    export interface WebSocketTaskPayload {
        event_type: string; // e.g., "task.created", "task.status.changed"
        task_id: string;    // Redundant with data.task_id but often useful
        data: TaskEventData;
        timestamp: string;
    }
    ```

**Verification:**
1.  Compare frontend types with backend `_emit_task_event` payload in `TaskServiceV2`.
2.  Ensure all fields match.

**Potential Pitfalls:**
*   Naming/type mismatches between backend payload and frontend types.

**State of the System After This Step:**
*   Frontend Task types are aligned with backend WebSocket event payloads.

---
**Step 3.2.2: Implement Task Event Handlers in Zustand Stores**

**Objective:**
*   Add/Update WebSocket event listener in `legionStore.ts` for `task_event`.
*   Dispatch these events to `useTaskStore` using `TaskEventData`.

**File(s) to Modify:**
*   `gemini_legion_frontend/src/store/legionStore.ts`
*   `gemini_legion_frontend/src/store/taskStore.ts`

**Context & Reasoning:**
*   Backend emits `task_event`. `legionStore` (manages WS) delegates to `taskStore`.

**Detailed Instructions:**

1.  **Verify/Update Handlers in `gemini_legion_frontend/src/store/taskStore.ts`:**
    ```typescript
    // In gemini_legion_frontend/src/store/taskStore.ts
    import type { Task, CreateTaskData, UpdateTaskData, TaskEventData } from '../types'; // Ensure TaskEventData

    interface TaskState {
      tasks: Task[];
      selectedTask: Task | null;
      loading: boolean;
      error: string | null;

      fetchTasks: () => Promise<void>;
      createTask: (data: CreateTaskData) => Promise<Task | undefined>; // Can return undefined on error
      updateTask: (taskId: string, data: UpdateTaskData) => Promise<void>;
      deleteTask: (taskId: string) => Promise<void>;
      setSelectedTask: (task: Task | null) => void;

      // Real-time update handlers
      handleTaskEvent: (eventData: TaskEventData, eventType: string) => void; // Consolidated handler
    }

    export const useTaskStore = create<TaskState>()(
      devtools(
        (set, get) => ({
          tasks: [],
          selectedTask: null,
          loading: false,
          error: null,

          fetchTasks: async () => { /* ... as before ... */ },
          createTask: async (data: CreateTaskData) => { /* ... as before, ensure it returns Task or undefined ... */
            try {
              const newTask = await taskApi.create(data); // Assuming taskApi.create returns the created task
              // No set((state) => ({ tasks: [...state.tasks, newTask] })) here, rely on WebSocket
              return newTask;
            } catch (error) {
              set({ error: (error as Error).message });
              toast.error(`Failed to create task: ${(error as Error).message}`);
              // throw error; // Or return undefined
              return undefined;
            }
          },
          updateTask: async (taskId, data) => { /* ... as before, remove direct state update, rely on WS ... */ },
          deleteTask: async (taskId) => { /* ... as before, remove direct state update, rely on WS ... */ },
          setSelectedTask: (task) => set({ selectedTask: task }),

          handleTaskEvent: (eventData: TaskEventData, eventType: string) => {
            set(state => {
              let newTasks = [...state.tasks];
              let newSelectedTask = state.selectedTask;

              if (eventType === 'task.deleted') {
                newTasks = state.tasks.filter(t => t.task_id !== eventData.task_id);
                if (state.selectedTask?.task_id === eventData.task_id) {
                  newSelectedTask = null;
                }
                toast.info(`Task '${eventData.title || eventData.task_id}' was deleted.`);
              } else { // Covers created, updated, status_changed, assigned, etc.
                const taskIndex = state.tasks.findIndex(t => t.task_id === eventData.task_id);
                const updatedTaskData = { ...state.tasks[taskIndex] || {}, ...eventData }; // Merge with existing if present

                if (taskIndex > -1) {
                  newTasks[taskIndex] = updatedTaskData;
                } else {
                  newTasks.push(updatedTaskData); // Add if new
                }
                if (state.selectedTask?.task_id === eventData.task_id) {
                  newSelectedTask = updatedTaskData;
                }
                toast.info(`Task '${eventData.title}' event: ${eventType.split('.')[1]}`);
              }

              // Optional: Sort tasks, e.g., by creation date or priority
              // newTasks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
              return {
                tasks: newTasks,
                selectedTask: newSelectedTask,
                error: null // Clear previous errors on new data
              };
            });
            console.log(`[TaskStore] Handled event type '${eventType}' for task ${eventData.task_id}. Status: ${eventData.status}`);
          },
        }),
        { name: 'task-store' }
      )
    );
    ```

2.  **Update Task Event Listener in `gemini_legion_frontend/src/store/legionStore.ts`:**
    ```typescript
    // In gemini_legion_frontend/src/store/legionStore.ts
    import type { Task, WebSocketTaskPayload, Minion as MinionType, Channel as ChannelType, Message as MessageType } from '../types'; // Ensure WebSocketTaskPayload

    // ... inside connectWebSocket method ...
            ws.on('task_event', (payload: WebSocketTaskPayload) => { // Use WebSocketTaskPayload type
              console.log('[LegionStore] WebSocket event "task_event" RECEIVED. Payload:', JSON.parse(JSON.stringify(payload)));

              if (!payload || !payload.event_type || !payload.task_id || !payload.data) {
                console.error('[LegionStore] "task_event" received with invalid structure:', payload);
                toast.error('Received corrupted task event from server.');
                return;
              }

              const taskEventData: TaskEventData = payload.data; // Data from backend is TaskEventData

              import('./taskStore').then(({ useTaskStore }) => {
                useTaskStore.getState().handleTaskEvent(taskEventData, payload.event_type);
              }).catch(err => {
                console.error('[LegionStore] Error importing or calling taskStore for task_event:', err);
              });
            });

            // ... (rest of connectWebSocket)
    ```

**Verification:**
1.  Restart backend & frontend. Open task UI. Use API tool to manipulate tasks.
2.  **Expected Outcome:** UI updates tasks in real-time. Console logs show `task_event` processing. `taskStore` state is accurate.

**Potential Pitfalls:**
*   Payload mismatch between `WebSocketTaskPayload.data` and `TaskEventData` / `TaskStore.handleTaskEvent`.
*   Incorrect event type routing in `legionStore`.

**State of the System After This Step:**
*   `taskStore` is reactive to backend task events. UI shows real-time task updates.

---
**Step 3.2.3: Verify and Enhance Minion and Channel Real-time UI Updates**

**Objective:**
*   Confirm existing WebSocket handlers in `legionStore.ts` for minion/channel events correctly update stores.
*   Identify and implement any missing common event handlers.

**File(s) to Modify:**
*   `gemini_legion_frontend/src/store/legionStore.ts`
*   `gemini_legion_frontend/src/store/chatStore.ts`

**Context & Reasoning:**
*   Ensuring all core entities update in real-time for UI consistency.

**Detailed Instructions:**

1.  **Review Event Handlers in `gemini_legion_frontend/src/store/legionStore.ts`:**
    *   **Minion Events:**
        *   `minion_spawned`: `get().addMinion(data.minion as MinionType)` - `data.minion` should come from backend's `_minion_to_dict`. Ensure types match.
        *   `minion_despawned`: `get().removeMinion(data.minion_id)`. Correct.
        *   `minion_emotional_state_updated`: `get().updateMinion(data.minion_id, { emotional_state: data.emotional_state })`. Verify `data.emotional_state` structure (from `_emotional_state_to_dict`).
        *   `minion_status_changed`: `get().updateMinion(data.minion_id, { status: data.status })`. Verify `data.status` mapping.
        *   **NEW: Add `minion_error` handler:**
            ```typescript
            ws.on('minion_error', (data: { minion_id: string, error_message: string, details?: string, context?: any }) => {
                console.error(`[LegionStore] Minion Error Event for ${data.minion_id}: ${data.error_message}`, data);
                toast.error(`Minion ${data.minion_id} reported an error: ${data.error_message}`);
                // Optionally, update minion status in store to 'error'
                // get().updateMinion(data.minion_id, { status: 'error' });
            });
            ```

    *   **Channel Events (forwarded to `chatStore`):**
        *   `message_sent`: Forwards to `chatStore.getState().handleNewMessage(data.channel_id, data.message)`. Check `data.message` structure.
        *   `channel_created`: Forwards to `chatStore.getState().addChannel(feChannel)`. The transformation logic for `feChannel` needs to be robust, especially for `members`.
        *   `channel_updated`, `channel_member_added`, `channel_member_removed`, `channel_deleted`: Check forwarding logic and corresponding `chatStore` actions.

2.  **Verify `chatStore.ts` Handlers:**
    *   Ensure `handleNewMessage`, `addChannel`, `updateChannel`, `removeChannel` correctly update the state.

**Verification:**
1.  Restart backend & frontend. Trigger minion/channel events (spawn, send messages, create channels, simulate minion errors if possible).
2.  **Expected Outcome:** UI updates in real-time for all these events. Stores are accurate.

**Potential Pitfalls:**
*   Payload mismatches between backend events and frontend types/handlers.
*   Incorrect state merging in Zustand actions.

**State of the System After This Step:**
*   Frontend provides a more comprehensive real-time view of minion, channel, and task states.

---

### Major Task 3.3: Production Readiness Basics

**Context for this major task:**
IADD Section 7.3 envisions `ResilientMinionSystem`. Handoff V6 Task 015 calls for "proper error handling" and "retry logic." Focus on foundational improvements.

---
**Step 3.3.1: Enhance Error Handling in `MinionServiceV2` for `runner.predict()`**

**Objective:**
*   Improve error handling around `runner.predict()` for better logs, error event emission, and graceful failure.

**File(s) to Modify:**
*   `gemini_legion_backend/core/application/services/minion_service_v2.py`
*   `gemini_legion_backend/core/infrastructure/adk/events.py`

**Context & Reasoning:**
*   `runner.predict()` is critical. Failures need robust handling.

**Detailed Instructions:**

1.  **Ensure `MINION_ERROR` EventType in `gemini_legion_backend/core/infrastructure/adk/events.py`:**
    *   (Already added in Step 3.1.3. Verify.)

2.  **Expand `try...except` in `_handle_channel_message` in `gemini_legion_backend/core/application/services/minion_service_v2.py`:**
    *   (The code from Step 2.2.2 already includes a try-except block for `runner.predict`. This step confirms and refines it for error event emission.)

    ```python
    # In gemini_legion_backend/core/application/services/minion_service_v2.py
    # ... (inside _handle_channel_message, within the loop)
                    response_text = None
                    try:
                        response_text = await runner.predict(
                            message=content,
                            session_id=current_session_id,
                            user_id=sender_id,
                            session_state=session_state_for_predict
                        )
                    except Exception as e:
                        logger.error(f"ADK Runner predict call failed for minion {minion_id} (session {current_session_id}). Error: {str(e)}", exc_info=True)
                        await self.event_bus.emit(
                            EventType.MINION_ERROR,
                            data={
                                "minion_id": minion_id,
                                "error_message": f"Failed to generate response: {str(e)}",
                                "details": "Error during ADK Runner predict call.",
                                "context": { "channel_id": channel_id, "original_message_content": content[:100] }
                            },
                            source="minion_service:predict_failure"
                        )
                        try:
                            error_notify_content = f"Apologies, I ({agent_instance.persona.name if agent_instance else minion_id}) encountered an issue and couldn't process that request."
                            await self.event_bus.emit_channel_message(
                                channel_id=channel_id,
                                sender_id=minion_id, # Or "system"
                                content=error_notify_content,
                                source="minion_service:predict_error_notification",
                                metadata={"is_error_message": True}
                            )
                        except Exception as notify_err:
                            logger.error(f"Failed to send error notification to channel {channel_id} for minion {minion_id}: {notify_err}")
                        # response_text remains None

                    if response_text:
                        # ... (success logic as established in 2.2.2) ...
                    else:
                        logger.warning(f"Minion {minion_id} generated no response or failed to predict for channel {channel_id} to message: '{content[:30]}...'")
    ```

**Verification:**
1.  Restart backend. Simulate `predict()` failure.
2.  **Expected Outcome:** Error logged; `MINION_ERROR` emitted; user-facing error message in channel. System stable.

**Potential Pitfalls:**
*   `MINION_ERROR` handling in `WebSocketEventBridge` and frontend store might be needed if UI should react to these errors.

**State of the System After This Step:**
*   More robust error handling for `runner.predict()`.

---
**Step 3.3.2: Implement Basic Retry Mechanism (Illustrative for Backend Service)**

**Objective:**
*   Illustrate adding simple retry for a hypothetical critical external call in a backend service.

**File(s) to Modify:**
*   (Hypothetical) e.g., a new file or an existing service if it makes external calls.

**Context & Reasoning:**
*   External services can fail transiently. Retries improve resilience. (ADK Runner handles LLM call retries).

**Detailed Instructions (Conceptual - No direct file to change in current structure without adding a new hypothetical external call):**
*   Provide a Python example of a retry decorator or helper function.
    ```python
    # Conceptual retry decorator (e.g., in a utils.py)
    import asyncio
    import time
    import logging
    from functools import wraps

    logger = logging.getLogger(__name__)

    def retry(exceptions=(Exception,), tries=3, delay=1, backoff=2):
        def deco_retry(f):
            @wraps(f)
            async def f_retry(*args, **kwargs):
                mtries, mdelay = tries, delay
                while mtries > 1:
                    try:
                        return await f(*args, **kwargs)
                    except exceptions as e:
                        msg = f"Retrying in {mdelay} seconds... ({mtries-1} tries remaining). Error: {e}"
                        logger.warning(msg)
                        await asyncio.sleep(mdelay)
                        mtries -= 1
                        mdelay *= backoff
                return await f(*args, **kwargs) # Last attempt
            return f_retry
        return deco_retry

    # Example usage:
    # @retry(exceptions=(ExternalServiceError,), tries=3)
    # async def call_flaky_service():
    #     # ... logic to call external service ...
    #     pass
    ```
*   **Explanation:** This demonstrates a basic exponential backoff retry pattern. For production, a library like `tenacity` is recommended.

**Verification (Conceptual):**
1.  If applied, mock the external service to fail transiently.
2.  **Expected Outcome:** Operation succeeds after retries. Logs show attempts.

**Potential Pitfalls:**
*   Retrying non-idempotent operations. Retry storms.

**State of the System After This Step:**
*   A pattern for basic retry logic is available for future external integrations.

---
**Step 3.3.3: Implement/Enhance Basic Health Check Endpoint**

**Objective:**
*   Ensure `/health` endpoint in `health.py` is robust, checking critical components like services and event bus.

**File(s) to Modify:**
*   `gemini_legion_backend/api/rest/endpoints/health.py`

**Context & Reasoning:**
*   Health checks are vital for monitoring and automated recovery.

**Detailed Instructions:**

*   **Enhance `gemini_legion_backend/api/rest/endpoints/health.py`:**
    ```python
    # In gemini_legion_backend/api/rest/endpoints/health.py
    from fastapi import APIRouter, Depends, HTTPException, status as http_status
    from typing import Dict, Any, List
    import logging
    # Adjust relative import path based on your project structure
    from ....core.dependencies_v2 import get_service_container_v2, ServiceContainerV2

    logger = logging.getLogger(__name__)
    # Ensure router is defined if not already, or that this is part of an existing router
    router = APIRouter(tags=["Health"]) # If defining new, else use existing from health.py

    @router.get("/health", response_model=Dict[str, Any])
    async def health_check(container: ServiceContainerV2 = Depends(get_service_container_v2)):
        healthy_components: Dict[str, str] = {}
        component_errors: List[str] = []
        overall_status = "healthy"

        healthy_components["api_server"] = "ok"

        # Check Event Bus
        try:
            if container.event_bus and hasattr(container.event_bus, 'subscriptions'): # Simple check
                healthy_components["event_bus"] = "ok"
            else:
                healthy_components["event_bus"] = "error: not available"
                component_errors.append("Event Bus unavailable")
        except Exception as e:
            healthy_components["event_bus"] = f"error: {str(e)}"
            component_errors.append(f"Event Bus check failed: {str(e)}")

        # Check ADK Session Service
        try:
            if container.session_service and hasattr(container.session_service, 'get_session'):
                 healthy_components["adk_session_service"] = "ok"
            else:
                healthy_components["adk_session_service"] = "error: not available"
                component_errors.append("ADK Session Service unavailable")
        except Exception as e:
            healthy_components["adk_session_service"] = f"error: {str(e)}"
            component_errors.append(f"ADK Session Service check failed: {str(e)}")

        # Check Minion Service
        try:
            if container.minion_service and hasattr(container.minion_service, 'list_minions'):
                # You could add a light check, e.g., await container.minion_service.list_minions(limit=1)
                healthy_components["minion_service"] = "ok"
            else:
                healthy_components["minion_service"] = "error: not available"
                component_errors.append("Minion Service unavailable")
        except Exception as e:
            healthy_components["minion_service"] = f"error: {str(e)}"
            component_errors.append(f"Minion Service check failed: {str(e)}")

        # Check Task Service
        try:
            if container.task_service and hasattr(container.task_service, 'list_tasks'):
                healthy_components["task_service"] = "ok"
            else:
                healthy_components["task_service"] = "error: not available"
                component_errors.append("Task Service unavailable")
        except Exception as e:
            healthy_components["task_service"] = f"error: {str(e)}"
            component_errors.append(f"Task Service check failed: {str(e)}")

        if component_errors:
            overall_status = "unhealthy"
            logger.error(f"Health check failed. Errors: {component_errors}")
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": overall_status, "components": healthy_components, "errors": component_errors}
            )

        return {"status": overall_status, "components": healthy_components}
    ```
    *   **Note:** Ensure the `health_router` is included in `main_v2.py` correctly (`app.include_router(health_router)`).

**Verification:**
1.  Restart backend. Access `/health`.
2.  **Expected Outcome:** JSON with `"status": "healthy"` and component statuses. If a service fails init, should show "unhealthy" and 503.

**Potential Pitfalls:**
*   Health checks too slow. Incorrect assessment of health.

**State of the System After This Step:**
*   More informative `/health` endpoint for basic operational monitoring.

---

This completes the guide for Phase 3.
