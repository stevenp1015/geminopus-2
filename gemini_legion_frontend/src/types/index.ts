// Core domain types for Gemini Legion

// Minion-related types
export interface MinionPersona {
  minion_id: string
  name: string
  base_personality: string
  quirks: string[]
  catchphrases: string[]
  allowed_tools: string[]
  expertise_areas: string[]
  model_name: string
  temperature?: number
  max_tokens?: number
}

export interface MoodVector {
  valence: number      // -1.0 to 1.0 (positive-negative)
  arousal: number      // 0.0 to 1.0 (calm-excited)
  dominance: number    // 0.0 to 1.0 (submissive-dominant)
  curiosity: number    // 0.0 to 1.0
  creativity: number   // 0.0 to 1.0
  sociability: number  // 0.0 to 1.0
}

export interface OpinionScore {
  entity_id: string
  entity_type: 'USER' | 'MINION' | 'CONCEPT' | 'TASK'
  trust: number        // -100 to 100
  respect: number      // -100 to 100
  affection: number    // -100 to 100
  interaction_count: number
  last_interaction: string | null
  notable_events: any[]
  overall_sentiment: number
}

export interface EmotionalState {
  minion_id: string
  mood: MoodVector
  energy_level: number     // 0.0 to 1.0
  stress_level: number     // 0.0 to 1.0
  opinion_scores: Record<string, OpinionScore>
  last_updated: string
  state_version: number
}

export interface Minion {
  minion_id: string
  persona: MinionPersona
  emotional_state: EmotionalState
  creation_date: string // Changed from spawn_time to align with backend
  status: 'active' | 'idle' | 'busy' | 'error' | 'rebooting'
  current_task?: Task
  memory_stats?: {
    working_memory_items: number
    episodic_memories: number
    semantic_concepts: number
  }
}

// Communication types
export type ChannelType = 'public' | 'private' | 'dm'
export type MessagePriority = 'low' | 'normal' | 'high' | 'urgent'

export interface Channel {
  id: string // Changed from channel_id to align with backend API response
  name: string
  type: ChannelType
  description?: string
  members: string[] // Changed from participants to align with backend ChannelResponse
  created_at: string
  created_by: string
  metadata?: Record<string, any>
  unread_count?: number
}

export interface Message {
  message_id: string
  channel_id: string
  sender_id: string
  sender_type: 'minion' | 'user' | 'system'
  type: 'CHAT' | 'SYSTEM' | 'TASK' | 'STATUS' | 'EMOTIONAL' // Added to align with backend MessageTypeEnum + observed 'EMOTIONAL'
  content: string
  timestamp: string
  priority?: MessagePriority
  metadata?: {
    emotional_state?: EmotionalState
    personality_hint?: string
    emotional_impact?: number
    [key: string]: any
  }
}

// Task types
export type TaskStatus = 'pending' | 'assigned' | 'decomposed' | 'in_progress' | 'blocked' | 'completed' | 'failed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

// This ExecutionLogEntry is a common pattern, add if not present
export interface ExecutionLogEntry {
  timestamp: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'debug'; // Or more specific types
}

export interface SubTask { // Define if not already present from backend domain
    subtask_id: string;
    parent_task_id: string;
    title: string;
    description: string;
    status: TaskStatus;
    complexity: string;
    suggested_minion_type?: string;
    dependencies: string[];
}

export interface TaskDecompositionFE { // Renamed to avoid conflict if backend also has TaskDecomposition
    strategy: string; // e.g., "sequential", "parallel"
    subtask_count: number;
    // subtasks?: SubTask[]; // Optional if not always sent
}

export interface Task {
  task_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  progress?: number;
  created_at: string; // ISO date string
  created_by?: string;
  assigned_to?: string | string[] | null; // Can be null
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
  assignment_history?: any[]; // Define more strictly if needed
  execution_log?: ExecutionLogEntry[]; // For logs/updates during task execution
  decomposition?: TaskDecompositionFE | null; // Use frontend specific type
}

// For API POST to /api/v2/tasks/
export interface CreateTaskRequestData { // Renamed from CreateTaskData to avoid conflict if used elsewhere
    title: string;
    description: string;
    priority?: TaskPriority; // Should match TaskPriorityAPI from backend schemas.py
    assigned_to?: string | null; // Allow null
    dependencies?: string[];
    metadata?: Record<string, any>;
}

// For API PUT /api/v2/tasks/{task_id}
export interface UpdateTaskRequestData extends Partial<CreateTaskRequestData> {
    status?: TaskStatus;
    progress?: number;
    assigned_to?: string | null; // Aligned with CreateTaskRequestData and typical single assignee
    output?: string;
    error_message?: string;
    title?: string;
}

// Interface for the data within WebSocket 'task_event' payload.data
// This should mirror the fields sent by backend's _emit_task_event
export interface TaskEventData extends Task {
    // It already includes all fields from Task.
    // Add any additional fields specific to the event payload if any.
    // For example, if 'status_message' or 'previous_status' are sent for specific events:
    status_message?: string;
    previous_status?: string;
    minion_name?: string;
    assignment_score?: number;
    // decomposition is already in Task, so it's inherited
}

export interface WebSocketTaskPayload {
    event_type: string; // e.g., "task.created", "task.status.changed"
    task_id: string;    // Redundant with data.task_id but often useful
    data: TaskEventData;
    timestamp: string;
}

// Memory and diary types
export interface DiaryEntry {
  entry_id: string
  minion_id: string
  timestamp: string
  entry_type: 'reflection' | 'interaction' | 'observation' | 'emotion'
  content: string
  emotional_snapshot?: EmotionalState
  metadata?: Record<string, any>
  embeddings?: number[]
}

export interface Memory {
  memory_id: string
  minion_id: string
  memory_type: 'working' | 'short_term' | 'episodic' | 'semantic' | 'procedural'
  content: string
  context?: Record<string, any>
  timestamp: string
  significance: number
  emotional_impact?: number
  decay_rate?: number
  access_count: number
  last_accessed?: string
  embeddings?: number[]
}

// User types
export interface User {
  id: string
  name: string
  role: 'commander' | 'observer'
  selected_minion_id?: string
  preferences?: {
    theme?: 'dark' | 'light'
    notifications?: boolean
  }
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// WebSocket types
export interface WebSocketMessage {
  type: 'minion_update' | 'message' | 'channel_update' | 'task_update' | 'emotional_update' | 'system'
  event: string
  data: any
  timestamp: string
  minion_id?: string
}

export interface WebSocketCommand {
  command: 'subscribe' | 'unsubscribe' | 'send_message' | 'update_status'
  params: Record<string, any>
}

// Store types
export interface LegionStore {
  // State
  minions: Record<string, Minion>
  channels: Record<string, Channel>
  messages: Message[]
  tasks: Record<string, Task>
  selectedMinionId: string | null
  selectedChannelId: string | null
  currentUser: User | null
  wsConnected: boolean
  
  // Actions
  setMinions: (minions: Minion[]) => void
  updateMinion: (minion: Minion) => void
  selectMinion: (minionId: string | null) => void
  
  setChannels: (channels: Channel[]) => void
  updateChannel: (channel: Channel) => void
  selectChannel: (channelId: string | null) => void
  createChannel: (channel: Partial<Channel>) => Promise<void>
  
  addMessage: (message: Message) => void
  sendMessage: (message: Partial<Message>) => Promise<void>
  
  setTasks: (tasks: Task[]) => void
  updateTask: (task: Task) => void
  createTask: (task: Partial<Task>) => Promise<void>
  
  setCurrentUser: (user: User | null) => void
  setWsConnected: (connected: boolean) => void
  
  // Async actions
  fetchMinions: () => Promise<void>
  fetchChannels: () => Promise<void>
  fetchMessages: (channelId: string) => Promise<void>
  spawnMinion: (config: Partial<MinionPersona>) => Promise<void>
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}