# Frontend Integration Guide for V2 Architecture

## Overview

The frontend needs updates to work with the new clean event-driven backend. No more duplicate messages, no more confusion, just clean real-time updates.

## Key Changes

### 1. WebSocket Events Structure

#### Old (Broken) Events:
```javascript
// Multiple events for the same message - GROSS
socket.on('message_sent', ...)
socket.on('channel_message', ...)
socket.on('minion_message', ...)
```

#### New (Clean) Events:
```javascript
// Single event types, single source of truth
socket.on('message', (data) => {
  // data = {
  //   type: 'message',
  //   channel_id: 'general',
  //   message: {
  //     message_id: 'msg_uuid',  // ALWAYS UNIQUE
  //     sender_id: 'minion_id',
  //     content: 'Hello world',
  //     timestamp: '2024-01-01T00:00:00Z',
  //     message_type: 'chat',
  //     metadata: {}
  //   }
  // }
})

socket.on('channel_event', (data) => {
  // data = {
  //   type: 'channel_created|channel_updated|channel_deleted',
  //   channel_id: 'channel_id',
  //   data: {...},
  //   timestamp: '2024-01-01T00:00:00Z'
  // }
})

socket.on('minion_event', (data) => {
  // data = {
  //   type: 'minion_spawned|minion_despawned|minion_state_changed',
  //   minion_id: 'minion_id',
  //   data: {...},
  //   timestamp: '2024-01-01T00:00:00Z'
  // }
})
```

### 2. API Endpoints

All endpoints now use `/api/v2/` prefix:

```javascript
// Old
POST /api/channels/{channel_id}/send
GET /api/channels/

// New
POST /api/v2/channels/{channel_id}/messages
GET /api/v2/channels/
```

### 3. Message Deduplication

The frontend should use `message_id` as the key:

```javascript
// MessageList.tsx
const MessageList = ({ messages }) => {
  // No more duplicate keys!
  return (
    <div>
      {messages.map(msg => (
        <Message key={msg.message_id} {...msg} />
      ))}
    </div>
  )
}
```

## Implementation Steps

### Step 1: Update WebSocket Connection

```typescript
// src/services/websocket.ts
import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null
  private messageHandlers: Map<string, Set<Function>> = new Map()

  connect() {
    this.socket = io('http://localhost:8000', {
      auth: {
        client_id: 'frontend-' + Date.now()
      }
    })

    this.setupEventHandlers()
  }

  private setupEventHandlers() {
    if (!this.socket) return

    // Single handler for messages
    this.socket.on('message', (data) => {
      this.emit('message', data)
    })

    // Channel events
    this.socket.on('channel_event', (data) => {
      this.emit('channel_event', data)
    })

    // Minion events
    this.socket.on('minion_event', (data) => {
      this.emit('minion_event', data)
    })
  }

  subscribeToChannel(channelId: string) {
    this.socket?.emit('subscribe_channel', { channel_id: channelId })
  }

  unsubscribeFromChannel(channelId: string) {
    this.socket?.emit('unsubscribe_channel', { channel_id: channelId })
  }

  on(event: string, handler: Function) {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, new Set())
    }
    this.messageHandlers.get(event)?.add(handler)
  }

  off(event: string, handler: Function) {
    this.messageHandlers.get(event)?.delete(handler)
  }

  private emit(event: string, data: any) {
    this.messageHandlers.get(event)?.forEach(handler => handler(data))
  }
}

export const wsService = new WebSocketService()
```

### Step 2: Update API Service

```typescript
// src/services/api.ts
const API_BASE = 'http://localhost:8000/api/v2'

export const api = {
  // Channels
  async listChannels() {
    const res = await fetch(`${API_BASE}/channels/`)
    return res.json()
  },

  async createChannel(data: CreateChannelRequest) {
    const res = await fetch(`${API_BASE}/channels/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return res.json()
  },

  async sendMessage(channelId: string, content: string, sender: string = 'COMMANDER_PRIME') {
    const res = await fetch(`${API_BASE}/channels/${channelId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender, content })
    })
    return res.json()
  },

  // Minions
  async listMinions() {
    const res = await fetch(`${API_BASE}/minions/`)
    return res.json()
  },

  async spawnMinion(data: CreateMinionRequest) {
    const res = await fetch(`${API_BASE}/minions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return res.json()
  }
}
```

### Step 3: Update React Components

```typescript
// src/hooks/useChannel.ts
import { useState, useEffect } from 'react'
import { wsService } from '../services/websocket'
import { api } from '../services/api'

export const useChannel = (channelId: string) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load initial messages
    const loadMessages = async () => {
      try {
        const data = await api.getChannelMessages(channelId)
        setMessages(data.messages)
      } finally {
        setLoading(false)
      }
    }

    loadMessages()

    // Subscribe to new messages
    const handleMessage = (data: any) => {
      if (data.channel_id === channelId) {
        setMessages(prev => {
          // Check for duplicates by message_id
          const exists = prev.some(m => m.message_id === data.message.message_id)
          if (exists) return prev
          
          return [...prev, data.message]
        })
      }
    }

    wsService.on('message', handleMessage)
    wsService.subscribeToChannel(channelId)

    return () => {
      wsService.off('message', handleMessage)
      wsService.unsubscribeFromChannel(channelId)
    }
  }, [channelId])

  const sendMessage = async (content: string) => {
    await api.sendMessage(channelId, content)
    // No need to manually add - will come through WebSocket
  }

  return { messages, loading, sendMessage }
}
```

### Step 4: Update Store (if using Redux/Zustand)

```typescript
// src/store/chatStore.ts
import { create } from 'zustand'
import { wsService } from '../services/websocket'

interface ChatStore {
  messages: Map<string, Message[]>  // channelId -> messages
  addMessage: (channelId: string, message: Message) => void
  setMessages: (channelId: string, messages: Message[]) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: new Map(),

  addMessage: (channelId, message) => set((state) => {
    const channelMessages = state.messages.get(channelId) || []
    
    // Prevent duplicates
    if (channelMessages.some(m => m.message_id === message.message_id)) {
      return state
    }

    const newMessages = new Map(state.messages)
    newMessages.set(channelId, [...channelMessages, message])
    
    return { messages: newMessages }
  }),

  setMessages: (channelId, messages) => set((state) => {
    const newMessages = new Map(state.messages)
    newMessages.set(channelId, messages)
    return { messages: newMessages }
  })
}))

// Set up WebSocket listeners
wsService.on('message', (data) => {
  useChatStore.getState().addMessage(data.channel_id, data.message)
})
```

## Testing the Integration

### 1. No More Duplicates Test

```typescript
// Open console and run:
wsService.subscribeToChannel('general')

// Send a message
await api.sendMessage('general', 'Test message')

// Should see EXACTLY ONE message in the UI
// Check console for any duplicate key warnings
```

### 2. Real-time Updates Test

```typescript
// Open two browser windows
// Both subscribe to same channel
// Send message from one
// Should appear in both WITHOUT duplicates
```

### 3. Minion Response Test

```typescript
// Send a message that triggers minion response
await api.sendMessage('general', 'Hello minions!')

// Should see:
// 1. Your message (once)
// 2. Minion responses (once each)
// 3. No placeholder text like "ADK integration needs work"
```

## Deployment Considerations

### Environment Variables

```typescript
// .env.production
VITE_API_URL=https://api.geminilegion.com/api/v2
VITE_WS_URL=wss://api.geminilegion.com
```

### CORS Configuration

Make sure backend allows your frontend origin:

```python
# backend/main_v2.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://geminilegion.com",
        "https://www.geminilegion.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rollback Plan

If shit goes wrong, you can run both V1 and V2 side by side:

1. Keep V1 on port 8000
2. Run V2 on port 8001
3. Use feature flag to switch between them:

```typescript
const API_VERSION = process.env.VITE_API_VERSION || 'v2'
const API_BASE = API_VERSION === 'v2' 
  ? 'http://localhost:8001/api/v2'
  : 'http://localhost:8000/api'
```

## Success Metrics

- ✅ No duplicate messages
- ✅ No console errors about duplicate keys
- ✅ Minions respond with actual content
- ✅ Real-time updates work smoothly
- ✅ Single WebSocket connection per client
- ✅ Clean message flow from backend to frontend

That's it! Your frontend is now talking to a backend that doesn't suck.
