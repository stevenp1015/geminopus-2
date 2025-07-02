// Purpose: Defines core TypeScript types and interfaces used throughout the frontend application, mirroring backend schemas.
// Data_Contract (Interface):
//   Exports: Minion, Channel, Message, Task, EmotionalState, Persona, etc.
//   (Specific interfaces for each type are defined within this file or sub-files)
// State_Management: Not applicable (defines types, doesn't manage state).
// Dependencies & Dependents: Used by virtually all components, services, and store slices.
// V2_Compliance_Check: Confirmed.

// --- Enums (mirroring backend schemas.py) ---

export enum MinionStatusEnum {
  ACTIVE = "active",
  IDLE = "idle",
  BUSY = "busy",
  ERROR = "error",
  REBOOTING = "rebooting",
}

export enum ChannelTypeEnum {
  PUBLIC = "public",
  PRIVATE = "private",
  DM = "dm",
}

export enum MessageTypeEnum {
  CHAT = "chat",
  SYSTEM = "system",
  TASK = "task",
  STATUS = "status",
}

export enum TaskStatusEnum {
  PENDING = "pending",
  ASSIGNED = "assigned",
  DECOMPOSED = "decomposed",
  IN_PROGRESS = "in_progress",
  BLOCKED = "blocked",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export enum TaskPriorityEnum {
  LOW = "low",
  NORMAL = "normal",
  HIGH = "high",
  CRITICAL = "critical",
}

export enum EntityTypeEnum {
    USER = "USER",
    MINION = "MINION",
    CONCEPT = "CONCEPT",
    TASK = "TASK",
    UNKNOWN = "UNKNOWN",
}

// --- Core Data Structures (mirroring backend schemas.py Response models) ---

export interface MinionPersona {
  name: string;
  base_personality: string;
  quirks: string[];
  catchphrases: string[];
  expertise_areas: string[];
  allowed_tools: string[];
  model_name?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface MoodVector {
  valence: number;
  arousal: number;
  dominance: number;
  curiosity: number;
  creativity: number;
  sociability: number;
}

export interface OpinionEvent {
    event_id: string;
    description: string;
    timestamp: string; // ISO datetime string
    impact_on_trust?: number | null;
    impact_on_respect?: number | null;
    impact_on_affection?: number | null;
    metadata?: Record<string, any>;
}

export interface OpinionScore {
    entity_type: EntityTypeEnum;
    trust: number;
    respect: number;
    affection: number;
    interaction_count: number;
    last_interaction_timestamp?: string | null; // ISO datetime string
    notable_events: OpinionEvent[];
    overall_sentiment: number;
}

export interface EmotionalState {
  minion_id: string;
  mood: MoodVector;
  energy_level: number;
  stress_level: number;
  opinion_scores: Record<string, OpinionScore>; // entity_id -> OpinionScore
  last_updated: string; // ISO datetime string
  state_version: number;
}

export interface Minion {
  minion_id: string;
  status: MinionStatusEnum;
  persona: MinionPersona;
  emotional_state: EmotionalState;
  creation_date: string; // ISO datetime string
}

export interface Channel {
  id: string;
  name: string;
  description?: string | null;
  type: ChannelTypeEnum;
  members: string[]; // List of minion_ids or user_ids
  created_at?: string; // ISO datetime string
}

export interface Message {
  message_id: string;
  sender: string; // minion_id or user_id (e.g., "commander")
  sender_type?: 'user' | 'minion' | 'system'; // Added to help UI distinguish
  content: string;
  timestamp: string; // ISO datetime string
  type: MessageTypeEnum;
  channel_id?: string | null;
  metadata?: Record<string, any>;
}

export interface Task {
  task_id: string;
  title: string;
  description: string;
  status: TaskStatusEnum;
  priority: TaskPriorityEnum;
  assigned_to?: string | null; // minion_id
  created_by: string;
  created_at: string; // ISO datetime string
  updated_at?: string | null; // ISO datetime string
  completed_at?: string | null; // ISO datetime string
  parent_id?: string | null;
  subtasks: string[]; // List of task_ids
  dependencies: string[]; // List of task_ids
  result?: Record<string, any> | null;
  metadata: Record<string, any>;
  progress?: number; // Optional progress field from V2 schema
  deadline?: string | null; // Optional deadline from V2 schema
}


// --- API Request/Response Wrapper Types ---

export interface MinionsListResponse {
  minions: Minion[];
  total?: number;
  active_count?: number; // As seen in minions_v2.py
}

export interface ChannelsListResponse {
  channels: Channel[];
  total?: number;
}

export interface MessagesListResponse {
  messages: Message[];
  total?: number;
  has_more: boolean;
}

export interface TasksListResponse {
  tasks: Task[];
  total?: number;
  has_more?: boolean; // Added based on V2 schema
}

export interface OperationResponse {
  status: string;
  id?: string | null;
  message?: string | null;
  timestamp?: string | null; // ISO datetime string
  data?: Record<string, any>; // For additional data like subtask_ids
}

// --- Request Payload Types (mirroring backend schemas.py Request models) ---

export interface CreateMinionRequest {
  name: string;
  personality: string; // Maps to base_personality in service/domain
  quirks: string[];
  catchphrases: string[];
  expertise: string[]; // Maps to expertise_areas in service/domain
  tools: string[];     // Maps to allowed_tools in service/domain
}

export interface CreateChannelRequest {
  name: string;
  description?: string | null;
  channel_type: ChannelTypeEnum;
  members: string[];
}

export interface SendMessageRequest {
  sender: string; // Should match the minion_id in URL path or be 'commander'/'system'
  channel_id: string; // Added this, as it's in schema and used by channel_v2 endpoint
  content: string;
}

export interface AddMemberRequest {
    minion_id: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  priority: TaskPriorityEnum;
  assigned_to?: string | null;
  dependencies?: string[];
  metadata?: Record<string, any>;
  // created_by is usually set by backend based on auth
  // tags were in V1 schema, removed in V2 CreateTaskRequest schema
}

export interface UpdateMinionPersonaRequest {
    name?: string;
    base_personality?: string;
    quirks?: string[];
    catchphrases?: string[];
    expertise_areas?: string[];
    allowed_tools?: string[];
    model_name?: string;
    temperature?: number;
    max_tokens?: number;
}

export interface UpdateEmotionalStateRequest {
    mood?: Partial<MoodVector>; // Allows partial updates to mood
    energy_level?: number;
    stress_level?: number;
    opinion_updates?: Record<string, Partial<Pick<OpinionScore, 'trust' | 'respect' | 'affection'>>>;
    // new_reflection?: { topic: string; insight: string; confidence: number }; // If reflections are updatable
}


// Memory System Types (from schemas.py)
export interface BaseMemoryEntryContents {
    content: string;
}
export interface WorkingMemoryEntryDetails extends BaseMemoryEntryContents {
    significance?: number | null;
    emotional_impact?: number | null;
}
export interface EpisodicMemoryEntryDetails extends BaseMemoryEntryContents {
    context?: Record<string, any> | null;
    emotional_state_snapshot_data?: Record<string, any> | null;
    actors?: string[] | null;
    location?: string | null;
}
export interface SemanticMemoryEntryDetails extends BaseMemoryEntryContents {
    concept_id: string;
    relations?: Array<Record<string, string>> | null;
    properties?: Record<string, any> | null;
    confidence?: number | null;
}
export interface ProceduralMemoryEntryDetails extends BaseMemoryEntryContents {
    skill_name: string;
    trigger_conditions?: string[] | null;
    action_sequence?: string[] | null;
    effectiveness_score?: number | null;
}

interface BaseMemoryEntryResponse<TDetails extends BaseMemoryEntryContents> {
    memory_id: string;
    minion_id: string;
    timestamp: string; // ISO datetime string
    details: TDetails;
}
export interface WorkingMemoryEntryResponse extends BaseMemoryEntryResponse<WorkingMemoryEntryDetails> {
    memory_type: "working";
}
export interface EpisodicMemoryEntryResponse extends BaseMemoryEntryResponse<EpisodicMemoryEntryDetails> {
    memory_type: "episodic";
}
export interface SemanticMemoryEntryResponse extends BaseMemoryEntryResponse<SemanticMemoryEntryDetails> {
    memory_type: "semantic";
}
export interface ProceduralMemoryEntryResponse extends BaseMemoryEntryResponse<ProceduralMemoryEntryDetails> {
    memory_type: "procedural";
}

export type AnyMemoryEntryResponse =
    | WorkingMemoryEntryResponse
    | EpisodicMemoryEntryResponse
    | SemanticMemoryEntryResponse
    | ProceduralMemoryEntryResponse;

export interface MemoryListResponse {
    memories: AnyMemoryEntryResponse[];
    minion_id: string;
    memory_type_filter?: string | null;
    total_returned: number;
}

// WebSocket Message Types
export interface WebSocketMessagePayload {
  type: string; // e.g., 'new_message', 'minion_status_update', 'task_update'
  channel?: string; // Optional channel context
  data: any; // The actual payload, structure depends on 'type'
  timestamp: string; // ISO datetime string
}
