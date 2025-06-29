import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import toast from 'react-hot-toast' // Added import for toast
import { taskApi } from '../services/api'
import type {
    Task,
    CreateTaskRequestData, // Changed from CreateTaskData
    UpdateTaskRequestData, // Changed from UpdateTaskData
    TaskEventData          // Added import
} from '../types' // Corrected import path

interface TaskState {
  tasks: Task[]
  selectedTask: Task | null
  loading: boolean
  error: string | null
  
  // Actions
  fetchTasks: () => Promise<void>
  createTask: (data: CreateTaskRequestData) => Promise<Task | undefined> // Adjusted return type
  updateTask: (taskId: string, data: UpdateTaskRequestData) => Promise<void> // Adjusted type
  deleteTask: (taskId: string) => Promise<void>
  setSelectedTask: (task: Task | null) => void
  addTaskMessage: (taskId: string, message: string) => void // Consider if this is still needed with full event updates
  updateTaskProgress: (taskId: string, progress: number) => void // Consider if this is still needed
  decomposeTask?: (taskId: string) => Promise<void>; // Added for TaskDetail.tsx
  
  // Real-time updates
  handleTaskEvent: (eventData: TaskEventData, eventType: string) => void;
}

export const useTaskStore = create<TaskState>()(
  devtools(
    (set, get) => ({
      tasks: [],
      selectedTask: null,
      loading: false,
      error: null,

      fetchTasks: async () => {
        set({ loading: true, error: null });
        try {
          const tasks = await taskApi.list();
          set({ tasks, loading: false });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
          console.error('Failed to fetch tasks:', error);
        }
      },

      createTask: async (data: CreateTaskRequestData) => { // Use CreateTaskRequestData
        // API call to create task, but state update will be handled by WebSocket event
        try {
          const newTask = await taskApi.create(data); // taskApi.create will also need to expect CreateTaskRequestData
          // Optimistic update removed, rely on WebSocket 'task.created' event via handleTaskEvent
          return newTask; // Return the created task for immediate feedback if needed
        } catch (error) {
          set({ error: (error as Error).message });
          console.error('Failed to create task via API:', error);
          toast.error(`Failed to create task: ${(error as Error).message}`);
          return undefined;
        }
      },

      updateTask: async (taskId: string, data: UpdateTaskRequestData) => { // Use UpdateTaskRequestData
        // API call to update task, state update via WebSocket event
        try {
          await taskApi.update(taskId, data); // taskApi.update will also need to expect UpdateTaskRequestData
          // Optimistic update removed
        } catch (error) {
          set({ error: (error as Error).message });
          console.error(`Failed to update task ${taskId} via API:`, error);
          toast.error(`Failed to update task: ${(error as Error).message}`);
          throw error;
        }
      },

      deleteTask: async (taskId: string) => {
        // API call to delete task, state update via WebSocket event
        try {
          await taskApi.delete(taskId);
          // Optimistic update removed
          // set(state => ({
          //   tasks: state.tasks.filter(t => t.task_id !== taskId),
          //   selectedTask: state.selectedTask?.task_id === taskId ? null : state.selectedTask
          // }));
        } catch (error) {
          set({ error: (error as Error).message });
          console.error(`Failed to delete task ${taskId} via API:`, error);
          toast.error(`Failed to delete task: ${(error as Error).message}`);
          throw error;
        }
      },

      setSelectedTask: (task: Task | null) => {
        set({ selectedTask: task });
      },

      // These might be deprecated if all updates come via handleTaskEvent
      addTaskMessage: (taskId: string, message: string) => {
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.task_id === taskId) {
              return {
                ...t,
                execution_log: [...(t.execution_log || []), {
                  timestamp: new Date().toISOString(),
                  message,
                  level: 'info'
                }]
              };
            }
            return t;
          })
        }));
      },

      updateTaskProgress: (taskId: string, progress: number) => {
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.task_id === taskId) {
              return {
                ...t,
                progress,
                status: progress >= 100 ? 'completed' : t.status // Simple status update based on progress
              };
            }
            return t;
          })
        }));
      },

      // Consolidated real-time event handler
      handleTaskEvent: (eventData: TaskEventData, eventType: string) => {
        set(state => {
          let newTasks = [...state.tasks];
          let newSelectedTask = state.selectedTask;
          const taskIndex = state.tasks.findIndex(t => t.task_id === eventData.task_id);

          if (eventType === 'task.deleted') {
            newTasks = state.tasks.filter(t => t.task_id !== eventData.task_id);
            if (state.selectedTask?.task_id === eventData.task_id) {
              newSelectedTask = null;
            }
            toast.info(`Task '${eventData.title || eventData.task_id}' was deleted.`);
          } else {
            // Covers created, updated, status_changed, assigned, completed, failed, etc.
            // We treat all as updates or additions. The eventData should be the full new state of the task.
            const updatedTaskData = eventData; // Assuming eventData is the complete Task object

            if (taskIndex > -1) { // Task exists, update it
              newTasks[taskIndex] = { ...newTasks[taskIndex], ...updatedTaskData };
            } else { // New task
              newTasks.push(updatedTaskData);
            }

            if (state.selectedTask?.task_id === eventData.task_id) {
              newSelectedTask = { ...state.selectedTask, ...updatedTaskData };
            }
            // Avoid too many toasts if not desired for every update type
            if (eventType === 'task.created' || eventType === 'task.completed' || eventType === 'task.failed' || eventType === 'task.assigned') {
                 toast.info(`Task '${updatedTaskData.title}' ${eventType.split('.')[1]}.`);
            } else if (eventType === 'task.status.changed' || eventType === 'task.progress.update' ) {
                // Potentially less verbose toast or just log for these frequent updates
                console.log(`Task '${updatedTaskData.title}' updated: ${eventType}`);
            }
          }

          // Optional: Sort tasks, e.g., by creation date or priority
          // newTasks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
          return {
            tasks: newTasks,
            selectedTask: newSelectedTask,
            error: null // Clear previous errors on new data
          };
        });
        console.log(`[TaskStore] Handled WebSocket event type '${eventType}' for task ${eventData.task_id}. New status: ${eventData.status}`);
      },

      decomposeTask: async (taskId: string) => {
        console.log(`[TaskStore] decomposeTask called for task ID: ${taskId}`);
        toast.info(`Task decomposition requested for ${taskId}. (Not yet fully implemented)`);
        // try {
        //   // TODO: Implement API call if backend supports task decomposition
        //   // const updatedTask = await taskApi.decompose(taskId);
        //   // set(state => ({
        //   //   tasks: state.tasks.map(t => t.task_id === taskId ? { ...t, ...updatedTask, status: 'decomposed' } : t),
        //   //   selectedTask: state.selectedTask?.task_id === taskId ? { ...state.selectedTask, ...updatedTask, status: 'decomposed' } : state.selectedTask
        //   // }));
        //   // toast.success(`Task ${taskId} decomposition initiated.`);
        // } catch (error) {
        //   console.error(`Failed to decompose task ${taskId}:`, error);
        //   toast.error(`Failed to decompose task ${taskId}: ${(error as Error).message}`);
        //   set({ error: (error as Error).message });
        // }
      }
    }),
    {
      name: 'task-store'
    }
  )
)