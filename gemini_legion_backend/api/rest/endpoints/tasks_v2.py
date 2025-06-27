```python
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
import logging
import uuid

from ..schemas import CreateTaskRequest, TaskResponse, TasksListResponse
from ....core.dependencies_v2 import get_task_service_v2
from ....core.application.services.task_service_v2 import TaskServiceV2
from ....core.domain.task import TaskStatus as DomainTaskStatus # For potential mapping
from ....core.domain.task import TaskPriority as DomainTaskPriority # For potential mapping

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/tasks", tags=["Tasks V2"])

def _convert_service_task_to_response(task_data: Optional[Dict[str, Any]]) -> Optional[TaskResponse]:
    """Helper to convert service layer task dict to API response model."""
    if not task_data:
        return None

    # Ensure all required fields for TaskResponse are present or have defaults
    # This mapping needs to be robust, especially for enums and optional fields.
    response_data = {
        "task_id": task_data.get("task_id"),
        "title": task_data.get("title"),
        "description": task_data.get("description"),
        "status": task_data.get("status"), # Assumes service returns string value of TaskStatusAPI
        "priority": task_data.get("priority"), # Assumes service returns string value of TaskPriorityAPI
        "progress": task_data.get("progress", 0),
        "created_at": task_data.get("created_at"),
        "created_by": task_data.get("created_by"),
        "assigned_to": task_data.get("assigned_to"),
        "started_at": task_data.get("started_at"),
        "completed_at": task_data.get("completed_at"),
        "deadline": task_data.get("deadline"),
        "dependencies": task_data.get("dependencies", []),
        "metadata": task_data.get("metadata", {}),
        # Ensure other fields from TaskResponse schema are handled if present in task_data
        # "output": task_data.get("output"),
        # "error_message": task_data.get("error_message"),
        # "subtask_ids": task_data.get("subtask_ids", []),
        # "parent_task_id": task_data.get("parent_task_id"),
        # "decomposition": task_data.get("decomposition"),
    }
    # Filter out None values for optional fields if not desired in response,
    # though Pydantic handles this by not including them if Optional and None.
    return TaskResponse(**response_data)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    request: CreateTaskRequest,
    task_service: TaskServiceV2 = Depends(get_task_service_v2)
):
    try:
        task_id = f"task_{uuid.uuid4().hex}"
        logger.info(f"API: Received request to create task: {request.title} with id {task_id}")

        # The TaskServiceV2.create_task method expects priority as a string.
        # The CreateTaskRequest schema uses TaskPriorityAPI enum, which provides .value
        task_data_from_service = await task_service.create_task(
            task_id=task_id,
            title=request.title,
            description=request.description,
            priority=request.priority.value,
            assigned_to=request.assigned_to,
            dependencies=request.dependencies,
            metadata=request.metadata
            # created_by will be set by service, or could pass authenticated user ID here
        )
        if not task_data_from_service:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task service created no data.")

        response_obj = _convert_service_task_to_response(task_data_from_service)
        if not response_obj:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to convert task data to API response.")
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
        # Assuming task_service.list_tasks returns a list of dicts
        # The service's _task_to_dict should align with TaskResponse or this conversion needs to be more robust
        converted_tasks = [_convert_service_task_to_response(t) for t in tasks_data_list if t]

        # TaskServiceV2.list_tasks currently returns List[Dict[str, Any]].
        # For proper pagination, it should ideally return a structure like {'tasks': [...], 'total': X}
        # For now, total is based on the returned list length for the current page.
        return TasksListResponse(
            tasks=converted_tasks,
            total=len(converted_tasks)
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
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to convert task data to API response.")
        return response_obj
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"API: Error getting task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving task")

# TODO: Add PUT for updates, DELETE for task removal, and other specific operations
# For example:
# @router.put("/{task_id}/assign/{minion_id}", response_model=TaskResponse)
# async def assign_task_to_minion_endpoint(task_id: str, minion_id: str, task_service: TaskServiceV2 = Depends(get_task_service_v2)): ...

# @router.put("/{task_id}/status", response_model=TaskResponse)
# async def update_task_status_endpoint(task_id: str, new_status: TaskStatusAPI, task_service: TaskServiceV2 = Depends(get_task_service_v2)): ...

```
