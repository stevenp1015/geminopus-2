/**
 * API Configuration
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  // Health
  health: '/health',
  
  // Minions
  minions: {
    list: '/api/v2/minions/',
    get: (id: string) => `/api/v2/minions/${id}`,
    create: '/api/v2/minions/',
    updateState: (id: string) => `/api/v2/minions/${id}/state`,
    updatePersona: (id: string) => `/api/v2/minions/${id}/persona`,
    delete: (id: string) => `/api/v2/minions/${id}`,
    diaryEntries: (id: string) => `/api/v2/minions/${id}/diary`,
    memories: (id: string) => `/api/v2/minions/${id}/memories`,
  },
  
  // Channels
  channels: {
    list: '/api/v2/channels/',
    get: (id: string) => `/api/v2/channels/${id}`,
    create: '/api/v2/channels/',
    messages: (id: string) => `/api/v2/channels/${id}/messages`,
    sendMessage: (id: string) => `/api/v2/channels/${id}/messages`,
    members: (id: string) => `/api/v2/channels/${id}/members`,
    addMember: (id: string) => `/api/v2/channels/${id}/members`,
    removeMember: (id: string, minionId: string) => `/api/v2/channels/${id}/members/${minionId}`,
  },
  
  // Tasks
  tasks: {
    list: '/api/v2/tasks/',
    get: (id: string) => `/api/v2/tasks/${id}`,
    create: '/api/v2/tasks/',
    update: (id: string) => `/api/v2/tasks/${id}`,
    updateStatus: (id: string) => `/api/v2/tasks/${id}/status`,
    assign: (id: string) => `/api/v2/tasks/${id}/assign`,
    delete: (id: string) => `/api/v2/tasks/${id}`,
    subtasks: (id: string) => `/api/v2/tasks/${id}/subtasks`,
  },
  
  // Tools
  tools: {
    list: '/api/v2/tools/',
    get: (id: string) => `/api/v2/tools/${id}`,
    execute: (id: string) => `/api/v2/tools/${id}/execute`,
  },
} as const

// Request headers
export const getHeaders = (token?: string) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}

// Generic API error class
export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`${status}: ${statusText}`)
    this.name = 'APIError'
  }
}

// Generic API response handler
export async function handleAPIResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new APIError(response.status, response.statusText, errorData)
  }
  
  return response.json()
}