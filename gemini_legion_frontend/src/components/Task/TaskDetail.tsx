import { useState } from 'react'
import { 
  Clock, CheckCircle, XCircle, Loader, // Removed Users, AlertCircle
  Edit, Trash, BarChart // Removed Plus, Link, Calendar
} from 'lucide-react'
import { useTaskStore } from '../../store/taskStore'
import type { Task, UpdateTaskRequestData, Minion } from '../../types' // Corrected import paths, using UpdateTaskRequestData for TaskUpdate

interface TaskDetailProps {
  task: Task
  minions: Minion[]
}

export default function TaskDetail({ task, minions }: TaskDetailProps) {
  const { updateTask, deleteTask, decomposeTask } = useTaskStore()
  const [isEditing, setIsEditing] = useState(false)
  const [editedTask, setEditedTask] = useState<Task>(task) // Ensure editedTask is of type Task

  // Modified handleUpdate to construct payload internally
  const handleUpdate = async () => {
    try {
      const payload: UpdateTaskRequestData = {
        title: editedTask.title,
        description: editedTask.description,
        priority: editedTask.priority,
        status: editedTask.status,
        progress: editedTask.progress,
        assigned_to: Array.isArray(editedTask.assigned_to) && editedTask.assigned_to.length > 0
                       ? editedTask.assigned_to[0]
                       : typeof editedTask.assigned_to === 'string'
                       ? editedTask.assigned_to
                       : null,
        // Include other fields from UpdateTaskRequestData if they are editable in this component
        // For example, if deadline, metadata, output, error_message are editable:
        // deadline: editedTask.deadline,
        // metadata: editedTask.metadata,
        // output: editedTask.output,
        // error_message: editedTask.error_message,
        // dependencies: editedTask.dependencies, // if editable
      };
      await updateTask(task.task_id, payload);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDecompose = async () => {
    try {
      if (decomposeTask) {
        await decomposeTask(task.task_id)
      } else {
        console.warn("decomposeTask function is not available on useTaskStore");
        // Optionally, show a toast to the user
        // toast.error("Task decomposition feature is currently unavailable.");
      }
    } catch (error) {
      console.error('Failed to decompose task:', error)
    }
  }

  const getStatusIcon = () => {
    switch (task.status) {
      case 'pending':
        return <Clock className="w-5 h-5" />
      case 'in_progress':
        return <Loader className="w-5 h-5 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5" />
      case 'failed':
        return <XCircle className="w-5 h-5" />
    }
  }

  const getStatusColor = () => {
    switch (task.status) {
      case 'pending':
        return 'text-yellow-400'
      case 'in_progress':
        return 'text-blue-400'
      case 'completed':
        return 'text-green-400'
      case 'failed':
        return 'text-red-400'
    }
  }

  const assignedToIds = Array.isArray(task.assigned_to)
    ? task.assigned_to
    : typeof task.assigned_to === 'string'
    ? [task.assigned_to]
    : [];

  const assignedMinions = assignedToIds.map((id: string) =>
    minions.find(m => m.minion_id === id)
  ).filter(Boolean) as Minion[];

  return (
    <div className="bg-black/30 backdrop-blur-md rounded-lg border border-legion-primary/20 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {isEditing ? (
            <input
              type="text"
              value={editedTask.title}
              onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
              className="w-full text-2xl font-bold bg-transparent border-b border-legion-primary/50
                       text-white focus:outline-none focus:border-legion-primary"
              autoFocus
            />
          ) : (
            <h2 className="text-2xl font-bold text-white">{task.title}</h2>
          )}
          <div className={`flex items-center gap-2 mt-2 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="capitalize">{task.status.replace('_', ' ')}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <Edit className="w-4 h-4 text-gray-400" />
          </button>
          <button
            onClick={() => deleteTask(task.task_id)}
            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
          >
            <Trash className="w-4 h-4 text-red-400" />
          </button>
        </div>
      </div>

      {/* Description */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Description</h3>
        {isEditing ? (
          <textarea
            value={editedTask.description}
            onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
            className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-gray-300
                     focus:border-legion-primary/50 focus:outline-none resize-none"
            rows={4}
          />
        ) : (
          <p className="text-gray-300">{task.description}</p>
        )}
      </div>

      {/* Progress */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-400">Progress</h3>
          <span className="text-legion-accent">{task.progress}%</span>
        </div>
        <div className="w-full bg-white/5 rounded-full h-3 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-legion-primary to-legion-accent transition-all duration-500"
            style={{ width: `${task.progress}%` }}
          />
        </div>
      </div>

      {/* Assigned Minions */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Assigned Minions</h3>
        <div className="space-y-2">
          {assignedMinions.length > 0 ? (
            assignedMinions.map(minion => (
              <div
                key={minion.minion_id}
                className="flex items-center gap-3 p-2 bg-white/5 rounded-lg"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-legion-primary to-legion-accent
                              flex items-center justify-center text-sm font-bold">
                  {minion.persona.name[0]}
                </div>
                <div>
                  <p className="text-white font-medium">{minion.persona.name}</p>
                  <p className="text-xs text-gray-400">{minion.persona.base_personality}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-sm">No minions assigned yet</p>
          )}
        </div>
      </div>

      {/* Subtasks */}
      {(task.subtask_ids || []).length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">
            Subtasks ({(task.subtask_ids || []).length})
          </h3>
          <div className="space-y-2">
            {/* If you want to display details of subtasks, you'd fetch them based on task.subtask_ids */}
            {/* For now, just listing IDs or a placeholder */}
            {(task.subtask_ids || []).map((subtask_id: string) => ( // Added type for subtask_id
              <div
                key={subtask_id} // Use subtask_id as key
                className="p-3 bg-white/5 rounded-lg border border-white/10"
              >
                <div className="flex items-center justify-between">
                  <p className="text-white">Subtask ID: {subtask_id}</p>
                  {/* Placeholder for actual subtask status/progress if fetched
                  <span className={`text-xs text-gray-400`}>
                    Details unavailable
                  </span>
                  */}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 pt-4 border-t border-white/10">
        {isEditing ? (
          <>
            <button
              onClick={handleUpdate} // Call without arguments
              className="btn-primary flex-1"
            >
              Save Changes
            </button>
            <button
              onClick={() => {
                setEditedTask(task)
                setIsEditing(false)
              }}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            {task.status === 'pending' && (task.subtask_ids || []).length === 0 && (
              <button
                onClick={handleDecompose}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <BarChart className="w-4 h-4" />
                Decompose Task
              </button>
            )}
            <button
              onClick={() => updateTask(task.task_id, { status: 'in_progress' })}
              className="btn-secondary flex-1"
              disabled={task.status !== 'pending'}
            >
              Start Task
            </button>
          </>
        )}
      </div>
    </div>
  )
}