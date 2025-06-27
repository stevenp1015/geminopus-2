"""
Task Service V2 - Clean Event-Driven Implementation

This service manages tasks through event-driven patterns, no more circular
dependencies with minion service, everything flows through the glorious event bus.
"""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum
from dataclasses import asdict
import json
import uuid

from ...domain import (
    Task,
    TaskStatus,
    TaskPriority,
    TaskDecomposition,
    SubTask,
    TaskAssignment
)
from ...infrastructure.persistence.repositories import TaskRepository
from ...infrastructure.adk.events import get_event_bus, EventType

logger = logging.getLogger(__name__)


class TaskOrchestrationStrategy(Enum):
    """Strategies for orchestrating task execution"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEPENDENCY = "dependency"
    ADAPTIVE = "adaptive"


class TaskServiceV2:
    """
    Task Service with proper event-driven architecture.
    
    Key principles:
    1. No direct minion service dependency
    2. All communication through events
    3. Reactive to minion events
    4. Clean separation of concerns
    """
    
    def __init__(self, task_repository: TaskRepository):
        """
        Initialize the Task service.
        
        Note: No more minion service dependency - we use events!
        """
        self.repository = task_repository
        self.event_bus = get_event_bus()
        
        # Active task monitoring
        self.active_tasks: Dict[str, Task] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Task execution queues
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.result_queue: asyncio.Queue = asyncio.Queue()
        
        # Minion availability cache (updated via events)
        self.available_minions: Dict[str, Dict[str, Any]] = {}
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()
        
        logger.info("TaskServiceV2 initialized with event-driven architecture")
    
    def _setup_event_subscriptions(self):
        """Subscribe to events we care about"""
        # Minion events for availability tracking
        self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_spawned)
        self.event_bus.subscribe(EventType.MINION_DESPAWNED, self._handle_minion_despawned)
        self.event_bus.subscribe(EventType.MINION_STATE_CHANGED, self._handle_minion_state_changed)
        
        # Task completion events from minions
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._handle_task_completed)
        self.event_bus.subscribe(EventType.TASK_FAILED, self._handle_task_failed)
    
    async def _handle_minion_spawned(self, event):
        """Track newly spawned minions"""
        minion_data = event.data
        self.available_minions[minion_data["minion_id"]] = {
            "minion_id": minion_data["minion_id"],
            "name": minion_data.get("name", "Unknown"),
            "status": "active",
            "personality": minion_data.get("personality", ""),
            "expertise_areas": minion_data.get("expertise_areas", [])
        }
        logger.info(f"Minion {minion_data['minion_id']} now available for tasks")
    
    async def _handle_minion_despawned(self, event):
        """Remove despawned minions and reassign their tasks"""
        minion_id = event.data["minion_id"]
        
        # Remove from available
        self.available_minions.pop(minion_id, None)
        
        # Check if any active tasks need reassignment
        for task in self.active_tasks.values():
            if task.assigned_to == minion_id and task.status == TaskStatus.IN_PROGRESS:
                logger.warning(f"Minion {minion_id} despawned, reassigning task {task.task_id}")
                await self.auto_assign_task(task.task_id)
    
    async def _handle_minion_state_changed(self, event):
        """Update minion availability based on state changes"""
        minion_id = event.data["minion_id"]
        if minion_id in self.available_minions:
            self.available_minions[minion_id].update(event.data)
    
    async def _handle_task_completed(self, event):
        """Handle task completion events from minions"""
        task_id = event.data.get("task_id")
        if task_id and task_id in self.active_tasks:
            await self.update_task_progress(task_id, 100, "Task completed by minion")
    
    async def _handle_task_failed(self, event):
        """Handle task failure events"""
        task_id = event.data.get("task_id")
        error = event.data.get("error", "Unknown error")
        
        if task_id and task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.now()
            await self.repository.save(task)
            
            # Emit task status change
            await self._emit_task_event(EventType.TASK_FAILED, task)
    
    async def start(self):
        """Start the service and background tasks"""
        logger.info("Starting Task Service V2...")
        
        # Start task monitoring
        self._monitor_task = asyncio.create_task(self._task_monitor_loop())
        
        # Load active tasks from repository
        await self._load_active_tasks()
        
        # Request minion list via event (minion service will respond)
        await self.event_bus.emit(
            EventType.SYSTEM_HEALTH,
            {"request": "minion_list", "source": "task_service"}
        )
        
        logger.info("Task Service V2 started successfully")
    
    async def stop(self):
        """Stop the service and cleanup"""
        logger.info("Stopping Task Service V2...")
        
        # Cancel monitoring task
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Save all active tasks
        for task in self.active_tasks.values():
            await self.repository.save(task)
        
        logger.info("Task Service V2 stopped")
    
    async def create_task(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: str = "normal",
        assigned_to: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new task - NOW WITH EVENTS"""
        try:
            # Create domain task object
            task = Task(
                task_id=task_id,
                title=title,
                description=description,
                status=TaskStatus.PENDING,
                priority=TaskPriority(priority),
                created_at=datetime.now(),
                created_by="commander",  # TODO: Get from auth context
                assigned_to=assigned_to,
                dependencies=dependencies or [],
                metadata=metadata or {}
            )
            
            # Persist to repository
            await self.repository.save(task)
            
            # Add to active tasks
            self.active_tasks[task_id] = task
            
            # Auto-decompose if complex
            if self._is_complex_task(description):
                await self.decompose_task(task_id)
            
            # Auto-assign if not assigned
            if not assigned_to:
                await self.auto_assign_task(task_id)
            
            # Emit creation event using the helper
            await self._emit_task_event(EventType.TASK_CREATED, task)
            
            logger.info(f"Created task: {title} ({task_id})")
            
            return self._task_to_dict(task) # Ensure _task_to_dict is comprehensive
            
        except Exception as e:
            logger.error(f"Failed to create task {task_id}: {e}", exc_info=True) # Added exc_info
            raise
    
    async def decompose_task(
        self,
        task_id: str,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decompose a complex task into subtasks.
        
        Now uses events to request decomposition from minions.
        """
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Find a taskmaster minion
        taskmaster = self._find_taskmaster_minion()
        if not taskmaster:
            # Fallback to simple decomposition
            return await self._simple_decomposition(task)
        
        # Request decomposition via event
        request_id = str(uuid.uuid4())
        
        await self.event_bus.emit(
            EventType.SYSTEM_HEALTH,  # Using system event for now
            data={
                "request_type": "task_decomposition",
                "request_id": request_id,
                "task_id": task_id,
                "task_title": task.title,
                "task_description": task.description,
                "task_priority": task.priority.value,
                "target_minion": taskmaster["minion_id"]
            },
            source="task_service"
        )
        
        # For now, use simple decomposition
        # In full implementation, would wait for response event
        return await self._simple_decomposition(task)
    
    async def _simple_decomposition(self, task: Task) -> Dict[str, Any]:
        """Simple fallback decomposition"""
        subtasks = [
            SubTask(
                subtask_id=f"{task.task_id}_sub_1",
                parent_task_id=task.task_id,
                title=f"Execute: {task.title}",
                description=task.description,
                status=TaskStatus.PENDING,
                complexity="medium",
                suggested_minion_type="generalist",
                dependencies=[]
            )
        ]
        
        decomposition = TaskDecomposition(
            task_id=task.task_id,
            subtasks=subtasks,
            strategy=TaskOrchestrationStrategy.SEQUENTIAL,
            created_at=datetime.now(),
            created_by="system"
        )
        
        task.decomposition = decomposition
        task.status = TaskStatus.DECOMPOSED
        
        await self.repository.save(task)
        
        return {
            "task_id": task.task_id,
            "subtask_count": len(subtasks),
            "strategy": decomposition.strategy.value,
            "subtasks": [self._subtask_to_dict(st) for st in subtasks]
        }
    
    async def auto_assign_task(
        self,
        task_id: str,
        prefer_minion_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Auto-assign task based on available minions"""
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if not self.available_minions:
            raise ValueError("No minions available for assignment")
        
        # Score minions for task suitability
        scored_minions = []
        for minion in self.available_minions.values():
            if minion.get("status") == "active":
                score = self._score_minion_for_task(minion, task, prefer_minion_type)
                scored_minions.append((score, minion))
        
        if not scored_minions:
            raise ValueError("No active minions available")
        
        # Sort by score (highest first)
        scored_minions.sort(key=lambda x: x[0], reverse=True)
        
        # Assign to best minion
        best_minion = scored_minions[0][1]
        
        # Create assignment
        assignment = TaskAssignment(
            task_id=task_id,
            minion_id=best_minion["minion_id"],
            assigned_at=datetime.now(),
            assigned_by="auto_assign",
            reason=f"Best match with score {scored_minions[0][0]}"
        )
        
        # Update task
        task.assigned_to = best_minion["minion_id"]
        task.assignment_history.append(assignment)
        task.status = TaskStatus.ASSIGNED
        
        # Save task
        await self.repository.save(task)
        
        # Emit assignment event using the helper
        await self._emit_task_event(
            EventType.TASK_ASSIGNED,
            task,
            additional_data={
                "minion_name": best_minion["name"], # Already in minion object if it's a Minion type
                "assignment_score": scored_minions[0][0]
            }
        )
        
        logger.info(f"Auto-assigned task {task_id} to {best_minion['name']}")
        
        return {
            "task_id": task_id,
            "assigned_to": best_minion["minion_id"],
            "minion_name": best_minion["name"],
            "assignment_score": scored_minions[0][0],
            "reason": assignment.reason
        }
    
    async def start_task(self, task_id: str) -> Dict[str, Any]:
        """Start task execution"""
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if not task.assigned_to:
            raise ValueError(f"Task {task_id} not assigned")
        
        # Check dependencies
        if not await self._check_dependencies_met(task):
            raise ValueError(f"Task {task_id} has unmet dependencies")
        
        # Update status
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        # Save task
        await self.repository.save(task)
        
        # Emit TASK_STATUS_CHANGED event
        await self._emit_task_event(
            EventType.TASK_STATUS_CHANGED,
            task,
            additional_data={"previous_status": TaskStatus.ASSIGNED.value} # Or whatever the previous status was
        )
        
        logger.info(f"Started task {task_id} (status changed to {task.status.value})")
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "assigned_to": task.assigned_to,
            "started_at": task.started_at.isoformat()
        }
    
    async def update_task_progress(
        self,
        task_id: str,
        progress: int,
        status_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task progress"""
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update progress
        task.progress = progress
        task.last_updated = datetime.now()
        
        # Add to execution log
        task.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "progress_update",
            "progress": progress,
            "message": status_message
        })
        
        # Check if complete
        if progress >= 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        
        # Save task
        # task.last_updated = datetime.now() # Assuming Task model has last_updated
        if not hasattr(task, 'last_updated'):
             task.last_updated = datetime.now()
        else:
            task.last_updated = datetime.now()

        # Ensure 'progress' attribute exists on the task object before updating
        if not hasattr(task, 'progress'):
            task.progress = 0 # Initialize if not present
        task.progress = progress


        current_status_before_update = task.status
        new_status = task.status

        if progress >= 100 and task.status != TaskStatus.COMPLETED:
            new_status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        # Check if task is not already in a terminal state before marking IN_PROGRESS
        elif task.status not in [TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.COMPLETED] and progress < 100:
            if task.status != TaskStatus.IN_PROGRESS : # Only change to IN_PROGRESS if it's not already
                 new_status = TaskStatus.IN_PROGRESS
        
        task.status = new_status
        await self.repository.save(task)

        if new_status == TaskStatus.COMPLETED:
            await self._emit_task_event(EventType.TASK_COMPLETED, task)
        elif new_status == TaskStatus.FAILED:
            # This case is typically handled by _handle_task_failed, which calls _emit_task_event(EventType.TASK_FAILED, task)
            # So, direct emission here might be redundant unless update_task_progress itself can determine failure.
            # For now, we assume TASK_FAILED is emitted by a more specific handler.
            pass
        elif new_status != current_status_before_update:
             await self._emit_task_event(EventType.TASK_STATUS_CHANGED, task, additional_data={"status_message": status_message, "previous_status": current_status_before_update.value if isinstance(current_status_before_update, Enum) else str(current_status_before_update)})
        else: # Just a progress update without status change
             await self._emit_task_event(EventType.TASK_PROGRESS_UPDATE, task, additional_data={"status_message": status_message})

        logger.info(f"Updated task {task_id} progress to {progress}%, status to {task.status.value}")
        
        return self._task_to_dict(task)
    
    async def _emit_task_event(self, event_type: EventType, task: Task, additional_data: Optional[Dict[str, Any]] = None):
        """Emit task-related events with comprehensive data."""
        # Ensure all relevant Task fields are included and correctly formatted
        event_data = {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if isinstance(task.status, Enum) else str(task.status),
            "priority": task.priority.value if isinstance(task.priority, Enum) else str(task.priority),
            "progress": getattr(task, 'progress', 0), # Safely get progress
            "created_at": task.created_at.isoformat(),
            "created_by": task.created_by,
            "assigned_to": task.assigned_to,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "dependencies": task.dependencies,
            "subtask_ids": getattr(task, 'subtask_ids', []), # Safely get subtask_ids
            "parent_task_id": task.parent_task_id,
            "metadata": task.metadata,
            "output": getattr(task, 'output', None), # Safely get output
            "error_message": getattr(task, 'error', None) # Safely get error, assuming 'error' attribute can exist
        }
        if hasattr(task, 'decomposition') and task.decomposition:
            event_data["decomposition"] = {
                "strategy": task.decomposition.strategy.value if isinstance(task.decomposition.strategy, Enum) else str(task.decomposition.strategy),
                "subtask_count": len(task.decomposition.subtasks),
                # "subtasks": [self._subtask_to_dict(st) for st in task.decomposition.subtasks] # Potentially too much data for an event
            }

        if additional_data:
            event_data.update(additional_data)

        await self.event_bus.emit(
            event_type,
            data=event_data, # This is the dict that will go into event.data
            source=f"task_service:{event_type.value}"
        )
        logger.info(f"Emitted {event_type.value} for task {task.task_id}")

    # Ensure methods like create_task, auto_assign_task, start_task, update_task_progress,
    # _handle_task_completed, _handle_task_failed call _emit_task_event appropriately.
    # For example, in create_task:
    # async def create_task(...):
    #     ...
    #     await self.repository.save(task)
    #     self.active_tasks[task_id] = task
    #     await self._emit_task_event(EventType.TASK_CREATED, task) # Use the helper
    #     return self._task_to_dict(task)

    # In auto_assign_task:
    # async def auto_assign_task(...):
    #     ...
    #     await self.repository.save(task)
    #     await self._emit_task_event(EventType.TASK_ASSIGNED, task, additional_data={"minion_name": best_minion["name"], "assignment_score": scored_minions[0][0]})
    #     return { ... }

    # In start_task:
    # async def start_task(...):
    #     ...
    #     await self.repository.save(task)
    #     await self._emit_task_event(EventType.TASK_STATUS_CHANGED, task, additional_data={"previous_status": "assigned"}) # Or "pending"
    #     return { ... }

    # In update_task_progress:
    # async def update_task_progress(self, task_id: str, progress: int, status_message: Optional[str] = None):
    #     task = self.active_tasks.get(task_id)
    #     if not task: raise ValueError(f"Task {task_id} not found")
    #
    #     # Add progress to task if not there, and ensure last_updated is set
    #     if not hasattr(task, 'progress'):
    #         task.progress = 0
    #     task.progress = progress
    #     # task.last_updated = datetime.now() # Assuming Task model has last_updated, or add it
    #
    #     current_status_before_update = task.status
    #     new_status = task.status
    #
    #     if progress >= 100 and task.status != TaskStatus.COMPLETED:
    #         new_status = TaskStatus.COMPLETED
    #         task.completed_at = datetime.now()
    #     elif task.status not in [TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.COMPLETED]:
    #         new_status = TaskStatus.IN_PROGRESS # Default to IN_PROGRESS if progress is < 100 and not terminal
    #
    #     task.status = new_status
    #     await self.repository.save(task)
    #
    #     if new_status == TaskStatus.COMPLETED:
    #         await self._emit_task_event(EventType.TASK_COMPLETED, task)
    #     elif new_status == TaskStatus.FAILED:
    #         await self._emit_task_event(EventType.TASK_FAILED, task)
    #     elif new_status != current_status_before_update:
    #          await self._emit_task_event(EventType.TASK_STATUS_CHANGED, task, additional_data={"status_message": status_message, "previous_status": current_status_before_update.value if isinstance(current_status_before_update, Enum) else str(current_status_before_update)})
    #     else: # Just a progress update without status change
    #          await self._emit_task_event(EventType.TASK_PROGRESS_UPDATE, task, additional_data={"status_message": status_message})
    #     return self._task_to_dict(task)
    
    def _find_taskmaster_minion(self) -> Optional[Dict[str, Any]]:
        """Find a taskmaster minion from available minions"""
        for minion in self.available_minions.values():
            if "taskmaster" in minion.get("personality", "").lower():
                return minion
            if "task" in minion.get("expertise_areas", []):
                return minion
        return None
    
    def _score_minion_for_task(
        self,
        minion: Dict[str, Any],
        task: Task,
        prefer_type: Optional[str] = None
    ) -> float:
        """Score minion suitability for task"""
        score = 50.0  # Base score
        
        # Expertise match
        task_keywords = set(task.title.lower().split() + task.description.lower().split())
        expertise_areas = set(area.lower() for area in minion.get("expertise_areas", []))
        
        matching_expertise = task_keywords.intersection(expertise_areas)
        score += len(matching_expertise) * 10
        
        # Preference match
        if prefer_type:
            if prefer_type in minion.get("personality", "").lower():
                score += 30
        
        # Priority-based scoring
        if task.priority == TaskPriority.CRITICAL:
            if "reliable" in minion.get("personality", "").lower():
                score += 15
            if "focused" in minion.get("personality", "").lower():
                score += 15
        
        return max(0, score)
    
    async def _check_dependencies_met(self, task: Task) -> bool:
        """Check if task dependencies are met"""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            dep_task = await self.repository.get_by_id(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _is_complex_task(self, description: str) -> bool:
        """Determine if task needs decomposition"""
        complexity_keywords = ["multiple", "steps", "complex", "analyze", "research", "implement", "design"]
        
        if len(description) > 200:
            return True
        
        description_lower = description.lower()
        if any(keyword in description_lower for keyword in complexity_keywords):
            return True
        
        return False
    
    async def _task_monitor_loop(self):
        """Monitor task execution"""
        while True:
            try:
                await asyncio.sleep(10)
                
                for task_id, task in list(self.active_tasks.items()):
                    try:
                        # Check task health
                        if task.status == TaskStatus.IN_PROGRESS:
                            # Check if assigned minion still exists
                            if task.assigned_to and task.assigned_to not in self.available_minions:
                                logger.warning(f"Assigned minion gone, reassigning task {task_id}")
                                await self.auto_assign_task(task_id)
                            
                            # Check timeout
                            if task.started_at:
                                elapsed = (datetime.now() - task.started_at).total_seconds()
                                if elapsed > 3600:  # 1 hour
                                    logger.warning(f"Task {task_id} timed out")
                                    task.status = TaskStatus.FAILED
                                    task.error = "Task execution timed out"
                                    await self.repository.save(task)
                                    await self._emit_task_event(EventType.TASK_FAILED, task)
                        
                        # Clean up completed tasks
                        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                            if task.completed_at:
                                elapsed = (datetime.now() - task.completed_at).total_seconds()
                                if elapsed > 300:  # 5 minutes
                                    del self.active_tasks[task_id]
                    
                    except Exception as e:
                        logger.error(f"Error monitoring task {task_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task monitor loop: {e}")
    
    async def _load_active_tasks(self):
        """Load active tasks from repository"""
        try:
            tasks = await self.repository.list_by_status([
                TaskStatus.PENDING,
                TaskStatus.ASSIGNED,
                TaskStatus.IN_PROGRESS,
                TaskStatus.DECOMPOSED
            ])
            
            for task in tasks:
                self.active_tasks[task.task_id] = task
            
            logger.info(f"Loaded {len(tasks)} active tasks")
            
        except Exception as e:
            logger.error(f"Failed to load active tasks: {e}")
    
    # Standard service methods
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        task = self.active_tasks.get(task_id)
        if not task:
            task = await self.repository.get_by_id(task_id)
        
        return self._task_to_dict(task) if task else None
    
    async def list_tasks(
        self,
        status_filter: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with filtering"""
        tasks = await self.repository.list_all(limit, offset)
        
        if status_filter:
            tasks = [t for t in tasks if t.status.value == status_filter]
        
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        
        return [self._task_to_dict(t) for t in tasks]
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert task to dict"""
        result = {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "created_by": task.created_by,
            "assigned_to": task.assigned_to,
            "dependencies": task.dependencies,
            "metadata": task.metadata
        }
        
        if task.started_at:
            result["started_at"] = task.started_at.isoformat()
        
        if task.completed_at:
            result["completed_at"] = task.completed_at.isoformat()
        
        if task.decomposition:
            result["decomposition"] = {
                "strategy": task.decomposition.strategy.value,
                "subtask_count": len(task.decomposition.subtasks),
                "subtasks": [self._subtask_to_dict(st) for st in task.decomposition.subtasks]
            }
        
        return result
    
    def _subtask_to_dict(self, subtask: SubTask) -> Dict[str, Any]:
        """Convert subtask to dict"""
        return {
            "subtask_id": subtask.subtask_id,
            "title": subtask.title,
            "status": subtask.status.value,
            "complexity": subtask.complexity,
            "suggested_minion_type": subtask.suggested_minion_type
        }
