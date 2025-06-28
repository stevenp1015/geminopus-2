from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
import logging
import uuid

from ..schemas import CreateTaskRequest, TaskResponse, TasksListResponse
from ....core.dependencies_v2 import get_task_service_v2
from ....core.application.services.task_service_v2 import TaskServiceV2
# from ....core.domain.task import TaskStatus as DomainTaskStatus # For potential mapping - removed as per guide
# from ....core.domain.task import TaskPriority as DomainTaskPriority # For potential mapping - removed as per guide

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/tasks", tags=["Tasks V2"])

def _convert_service_task_to_response(task_data: Optional[Dict[str, Any]]) -> Optional[TaskResponse]:
    """Helper to convert service layer task dict to API response model."""
    if not task_data:
        return None

    # Ensure all required fields for TaskResponse are present or have defaults
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
    }
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
