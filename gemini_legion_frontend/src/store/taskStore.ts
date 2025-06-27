import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { taskApi } from '../services/api'
import type { Task, CreateTaskData, UpdateTaskData } from '../types/task'

interface TaskState {
  tasks: Task[]
  selectedTask: Task | null
  loading: boolean
  error: string | null
  
  // Actions
  fetchTasks: () => Promise<void>
  createTask: (data: CreateTaskData) => Promise<Task>
  updateTask: (taskId: string, data: UpdateTaskData) => Promise<void>
  deleteTask: (taskId: string) => Promise<void>
  setSelectedTask: (task: Task | null) => void
  addTaskMessage: (taskId: string, message: string) => void
  updateTaskProgress: (taskId: string, progress: number) => void
  
  // Real-time updates
  // handleTaskUpdate: (task: Task) => void; // Will be replaced by handleTaskEvent
  // handleTaskDeleted: (taskId: string) => void; // Will be replaced by handleTaskEvent
  handleTaskEvent: (eventData: TaskEventData, eventType: string) => void; // Consolidated handler
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

      createTask: async (data: CreateTaskData) => {
        // API call to create task, but state update will be handled by WebSocket event
        try {
          const newTask = await taskApi.create(data);
          // Optimistic update removed, rely on WebSocket 'task.created' event via handleTaskEvent
          // set(state => ({ tasks: [...state.tasks, newTask] }));
          return newTask; // Return the created task for immediate feedback if needed
        } catch (error) {
          set({ error: (error as Error).message });
          console.error('Failed to create task via API:', error);
          toast.error(`Failed to create task: ${(error as Error).message}`);
          // throw error; // Or return undefined
          return undefined;
        }
      },

      updateTask: async (taskId: string, data: UpdateTaskData) => {
        // API call to update task, state update via WebSocket event
        try {
          const updatedTask = await taskApi.update(taskId, data);
          // Optimistic update removed
          // set(state => ({
          //   tasks: state.tasks.map(t => t.task_id === taskId ? updatedTask : t),
          //   selectedTask: state.selectedTask?.task_id === taskId ? updatedTask : state.selectedTask
          // }));
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
    }),
    {
      name: 'task-store'
    }
  )
)