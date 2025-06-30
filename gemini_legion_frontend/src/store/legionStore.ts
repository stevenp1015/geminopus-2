import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { io, Socket } from 'socket.io-client'
import toast from 'react-hot-toast'
import { minionApi, channelApi, WS_BASE_URL, API_BASE_URL } from '../services/api'
import type {
    Minion as MinionType,
    Channel as ChannelType,
    Message as MessageType,
    WebSocketTaskPayload, // Added import
    TaskEventData         // Added import
} from '../types'

export type { MinionType as Minion, ChannelType as Channel, MessageType as Message }

interface LegionState {
  // State
  minions: Record<string, MinionType>
  // channels: Record<string, ChannelType> // Moved to chatStore
  // messages: Record<string, MessageType[]> // MOVED to chatStore
  selectedMinionId: string | null
  selectedChannelId: string | null // Keep selectedChannelId if other legion parts need it, or move to chatStore
  websocket: Socket | null
  loading: boolean
  error: string | null
  
  // Actions
  setMinions: (minions: MinionType[]) => void
  addMinion: (minion: MinionType) => void
  updateMinion: (minionId: string, updates: Partial<MinionType>) => void
  removeMinion: (minionId: string) => void
  selectMinion: (minionId: string | null) => void
  
  // setChannels: (channels: ChannelType[]) => void // Moved to chatStore
  // addChannel: (channel: ChannelType) => void // Moved to chatStore
  // updateChannel: (channelId: string, updates: Partial<ChannelType>) => void // Moved to chatStore
  selectChannel: (channelId: string | null) => void // Keep if selectedChannelId remains, for UI sync
  
  // addMessage: (channelId: string, message: MessageType) => void // MOVED to chatStore
  // setMessages: (channelId: string, messages: MessageType[]) => void // MOVED to chatStore
  
  connectWebSocket: () => void
  disconnectWebSocket: () => void
  
  // API calls
  fetchMinions: () => Promise<void>
  // fetchChannels: () => Promise<void> // Moved to chatStore
  // fetchMessages: (channelId: string) => Promise<void> // MOVED to chatStore
  spawnMinion: (config: any) => Promise<void>
  sendMessage: (channelId: string, minionId: string, content: string) => Promise<void>
  sendCommanderMessage: (channelId: string, content: string) => Promise<void>
  updateMinionPersona: (minionId: string, persona: any) => Promise<void>
  updateMinionEmotionalState: (minionId: string, state: any) => Promise<void>
}

export const useLegionStore = create<LegionState>()(
  devtools(
    (set, get) => ({
      // Initial state
      minions: {},
      // channels: {}, // Moved to chatStore
      // messages: {}, // MOVED to chatStore
      selectedMinionId: null,
      selectedChannelId: null,
      websocket: null,
      loading: false,
      error: null,
      
      // Minion actions
      setMinions: (minions) => set({
        minions: minions.reduce((acc, minion) => {
          acc[minion.minion_id] = minion
          return acc
        }, {} as Record<string, MinionType>)
      }),
      
      addMinion: (minion) => {
        console.log('[LegionStore] addMinion called with:', JSON.parse(JSON.stringify(minion)));
        if (!minion || !minion.minion_id) {
          console.error('[LegionStore] addMinion: Attempted to add minion with invalid ID or undefined minion object.', minion);
          return;
        }
        if (!minion.persona) {
            console.warn('[LegionStore] addMinion: Minion object is missing persona.', JSON.parse(JSON.stringify(minion)));
        } else if (!minion.persona.name) {
            console.warn('[LegionStore] addMinion: Minion persona is missing name.', JSON.parse(JSON.stringify(minion)));
        }

        set((state) => {
          if (state.minions[minion.minion_id]) {
            console.log(`[LegionStore] addMinion: Minion ${minion.minion_id} already exists. Overwriting.`, 'Old:', state.minions[minion.minion_id], 'New:', minion);
          }
          return {
            minions: { ...state.minions, [minion.minion_id]: minion }
          };
        });
      },
      
      updateMinion: (minionId, updates) => {
        console.log('[LegionStore] updateMinion called for:', minionId, 'with updates:', JSON.parse(JSON.stringify(updates)));
        set((state) => {
          const existingMinion = state.minions[minionId];
          console.log('[LegionStore] Existing minion before update:', JSON.parse(JSON.stringify(existingMinion)));
          const updatedMinion = { ...existingMinion, ...updates };
          console.log('[LegionStore] Minion after update:', JSON.parse(JSON.stringify(updatedMinion)));
          
          // Defensive check: if persona existed and updates doesn't have it, log a warning
          if (existingMinion && existingMinion.persona && (!updates.persona && !('persona' in updates))) {
            console.warn(`[LegionStore] updateMinion for ${minionId}: Persona existed but was not in updates. Preserving old persona if updates didn't explicitly nullify it.`);
            // This logic might be too aggressive if updates *can* legitimately remove persona.
            // For now, let's see if 'updates' is the culprit.
          }
          if (updatedMinion.persona === undefined && existingMinion && existingMinion.persona !== undefined) {
            console.error(`[LegionStore] FATAL: Persona for ${minionId} became undefined after update!`, 'Existing:', existingMinion, 'Updates:', updates, 'Result:', updatedMinion);
          }

          return {
            minions: {
              ...state.minions,
              [minionId]: updatedMinion
            }
          };
        });
      },
      
      removeMinion: (minionId) => set((state) => {
        const newMinions = { ...state.minions }
        delete newMinions[minionId]
        return { minions: newMinions }
      }),
      
      selectMinion: (minionId) => set({ selectedMinionId: minionId }),
      
      // Channel actions (MOVED TO chatStore - only selectChannel might remain if needed by non-chat UI)
      // setChannels: (channels) => set({ ... }), // Moved
      // addChannel: (channel) => set((state) => ({ ... })), // Moved
      // updateChannel: (channelId, updates) => set((state) => ({ ... })), // Moved
      selectChannel: (channelId) => set({ selectedChannelId: channelId }), // Kept for now
      
      // Message actions // MOVED to chatStore
      // addMessage: (channelId, message) => set((state) => ({
      //   messages: {
      //     ...state.messages,
      //     [channelId]: [...(state.messages[channelId] || []), message]
      //   }
      // })),
      
      // setMessages: (channelId, messages) => set((state) => ({
      //   messages: { ...state.messages, [channelId]: messages }
      // })),
      
      // WebSocket management
      connectWebSocket: () => {
        const ws = io(WS_BASE_URL, { // Remove the /ws path
          transports: ['websocket'],
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
        })
        
        ws.on('connect', () => {
          console.log('WebSocket connected')
          toast.success('Connected to Legion Server')
        })
        
        ws.on('disconnect', () => {
          console.log('WebSocket disconnected')
          toast.error('Disconnected from Legion Server')
        })
        
        // Minion events
        ws.on('minion_spawned', (data: any) => {
          // Ensure data.minion is what we expect (MinionType)
          // Our backend _minion_to_dict now ensures persona is nested.
          if (data.minion && data.minion.persona) {
            get().addMinion(data.minion as MinionType); // Cast if confident about structure
            toast.success(`${data.minion.persona.name || data.minion.minion_id} has joined the Legion!`);
          } else {
            console.error('[LegionStore] minion_spawned event received malformed minion data:', data);
            toast.error('A new minion tried to join, but its data was corrupted!');
          }
        })
        
        ws.on('minion_despawned', (data: any) => {
          get().removeMinion(data.minion_id)
          toast(`${data.minion_name} has left the Legion`)
        })
        
        ws.on('minion_emotional_state_updated', (data: any) => {
          get().updateMinion(data.minion_id, { 
            emotional_state: data.emotional_state 
          })
        })
        
        ws.on('minion_status_changed', (data: any) => {
          get().updateMinion(data.minion_id, { 
            status: data.status 
          })
        })

        ws.on('minion_state_changed', (data: MinionType) => { // Assuming data is the full MinionType
          console.log('[LegionStore] WebSocket event "minion_state_changed" RECEIVED. Data:', JSON.parse(JSON.stringify(data)));
          if (data && data.minion_id) {
            // The payload is the updated minion object directly
            get().updateMinion(data.minion_id, data);
            toast.success(`State for ${data.persona?.name || data.minion_id} has been updated.`);
          } else {
            console.error('[LegionStore] minion_state_changed event received malformed data:', data);
            toast.error('Received corrupted minion state update.');
          }
        })
        
        // Message events (forward to chat store)
        ws.on('message_sent', (data: any) => {
          // Import chat store dynamically to avoid circular dependency
          import('./chatStore').then(({ useChatStore }) => {
            useChatStore.getState().handleNewMessage(data.channel_id, data.message)
          })
        })
        
        // Channel events (forward to chat store)
        ws.on('channel_created', (data: any) => {
          console.log('[LegionStore] WebSocket event "channel_created" RECEIVED. Raw Data:', JSON.parse(JSON.stringify(data)));
          if (data && data.channel && data.channel.channel_id) { // Check for channel_id specifically
            const rawChannel = data.channel;
            // Transform backend channel object to frontend Channel type
            const feChannel: ChannelType = {
              id: rawChannel.channel_id, // Map channel_id to id
              name: rawChannel.name,
              type: rawChannel.channel_type, // Assuming channel_type matches ChannelType enum
              description: rawChannel.description,
              // Map members array of objects to array of member_id strings
              members: Array.isArray(rawChannel.members) ? rawChannel.members.map((member: any) => typeof member === 'object' && member !== null && member.member_id ? member.member_id : member as string).filter((id: string) => typeof id === 'string') : [],
              created_at: rawChannel.created_at,
              created_by: rawChannel.created_by,
              metadata: rawChannel.metadata,
              unread_count: rawChannel.unread_count || 0
            };
            console.log('[LegionStore] Transformed feChannel for chatStore.addChannel:', JSON.parse(JSON.stringify(feChannel)));

            import('./chatStore').then(({ useChatStore }) => {
              useChatStore.getState().addChannel(feChannel);
            }).catch(err => {
              console.error('[LegionStore] Error importing or calling chatStore for channel_created:', err);
            });
          } else {
            console.error('[LegionStore] WebSocket event "channel_created" received with invalid or missing channel data:', data);
          }
        })
        
        ws.on('channel_updated', (data: any) => {
          import('./chatStore').then(({ useChatStore }) => {
            useChatStore.getState().handleChannelUpdate(data.channel_id, data.updates)
          })
        })
        
        ws.on('channel_member_added', (data: any) => {
          import('./chatStore').then(({ useChatStore }) => {
            const chatStore = useChatStore.getState()
            const channel = chatStore.channels[data.channel_id]
            if (channel) {
              chatStore.updateChannel(data.channel_id, {
                members: [...channel.members, data.minion_id] // Changed participants to members
              })
            }
          })
        })
        
        ws.on('channel_member_removed', (data: any) => {
          import('./chatStore').then(({ useChatStore }) => {
            const chatStore = useChatStore.getState()
            const channel = chatStore.channels[data.channel_id]
            if (channel) {
              chatStore.updateChannel(data.channel_id, {
                members: channel.members.filter((id: string) => id !== data.minion_id) // Changed participants to members, added type for id
              })
            }
          })
        })

        ws.on('channel_deleted', (data: { channel_id: string }) => {
          if (data && data.channel_id) {
            import('./chatStore').then(({ useChatStore }) => {
              useChatStore.getState().removeChannel(data.channel_id);
            });
            toast(`Channel ${data.channel_id} was deleted.`);
          } else {
            console.warn('Received channel_deleted event with missing data:', data);
          }
        });
        
        // Task events (NEW - generic handler)
        // The backend's WebSocketEventBridge emits a generic 'task_event' event.
        // The actual event type (task.created, task.status.changed, etc.) is in the payload.
        ws.on('task_event', (payload: WebSocketTaskPayload) => { // Use WebSocketTaskPayload type
          console.log('[LegionStore] WebSocket event "task_event" RECEIVED. Payload:', JSON.parse(JSON.stringify(payload)));

          if (!payload || !payload.event_type || !payload.task_id || !payload.data) {
            console.error('[LegionStore] "task_event" received with invalid structure:', payload);
            toast.error('Received corrupted task event from server.');
            return;
          }

          const taskEventData: TaskEventData = payload.data as TaskEventData; // Data from backend is TaskEventData

          import('./taskStore').then(({ useTaskStore }) => {
            useTaskStore.getState().handleTaskEvent(taskEventData, payload.event_type);
          }).catch(err => {
            console.error('[LegionStore] Error importing or calling taskStore for task_event:', err);
          });
        });

        set({ websocket: ws });
      },
      
      disconnectWebSocket: () => {
        const ws = get().websocket
        if (ws) {
          ws.disconnect()
          set({ websocket: null })
        }
      },
      
      // API calls
      fetchMinions: async () => {
        set({ loading: true, error: null })
        try {
          const minionsResult = await minionApi.list()
          console.log('[LegionStore] Minions result from minionApi.list():', minionsResult);
          console.log('[LegionStore] Is minionsResult an array?:', Array.isArray(minionsResult));
          get().setMinions(minionsResult)
        } catch (error) {
          console.error('Failed to fetch minions:', error)
          toast.error('Failed to fetch minions')
          set({ error: (error as Error).message })
        } finally {
          set({ loading: false })
        }
      },
      
      // fetchChannels: async () => { ... }, // Moved to chatStore
      
      // fetchMessages: async (channelId: string) => { // MOVED to chatStore
      //   try {
      //     const messages = await channelApi.getMessages(channelId, 100)
      //     get().setMessages(channelId, messages)
      //   } catch (error) {
      //     console.error('Failed to fetch messages:', error)
      //     toast.error('Failed to fetch messages')
      //   }
      // },
      
      spawnMinion: async (config: any) => {
        try {
          // Call the /spawn endpoint with the correct payload structure
          const response = await fetch(`${API_BASE_URL}/api/v2/minions/spawn`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: config.name,
              personality: config.base_personality || config.personality,
              quirks: config.quirks || [],
              catchphrases: config.catchphrases || [],
              expertise: config.expertise_areas || config.expertise || [],
              tools: config.allowed_tools || config.tools || []
            })
          })
          
          if (!response.ok) {
            throw new Error(`Failed to spawn minion: ${response.statusText}`)
          }
          
          const result = await response.json()
          
          // Fetch the newly created minion - REMOVED
          // const minion = await minionApi.get(result.id)
          // get().addMinion(minion) - REMOVED
          // Rely on the minion_spawned WebSocket event to add the minion to the store.
          toast.success(`Spawning ${config.name}! ${result.message}`)
        } catch (error) {
          console.error('Failed to spawn minion:', error)
          toast.error('Failed to spawn minion')
          throw error
        }
      },
      
      sendMessage: async (channelId: string, minionId: string, content: string) => {
        // Unified message sending: delegate to chatStore for consistency
        // This maintains backward compatibility while centralizing message logic
        console.log(`[LegionStore] sendMessage DELEGATING to chatStore. Channel ID: ${channelId}, Minion ID: ${minionId}, Content: "${content}"`);
        
        if (!minionId) {
          const errMsg = "Minion ID is undefined, cannot send message as minion.";
          console.error(`[LegionStore] ${errMsg}`);
          toast.error(errMsg);
          throw new Error(errMsg);
        }

        try {
          // Import and delegate to chatStore for unified message handling
          const { useChatStore } = await import('./chatStore');
          const chatStore = useChatStore.getState();
          
          // Use chatStore's sendMessage method for consistency
          await chatStore.sendMessage(channelId, minionId, content);
          
          toast.success(`Message sent by ${minionId}`);
        } catch (error) {
          console.error('[LegionStore] Error in sendMessage delegation:', error);
          if (!(error instanceof Error && error.message.startsWith("Minion ID is undefined"))) {
             toast.error(`Send failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
          }
          throw error;
        }
      },

      sendCommanderMessage: async (channelId: string, content: string) => {
        // Convenience method for Steven (the Commander) to send messages
        console.log(`[LegionStore] sendCommanderMessage delegating to chatStore. Channel: ${channelId}`);
        try {
          const { useChatStore } = await import('./chatStore');
          const chatStore = useChatStore.getState();
          
          await chatStore.sendCommanderMessage(channelId, content);
        } catch (error) {
          console.error('[LegionStore] Error in sendCommanderMessage:', error);
          throw error;
        }
      },
      
      updateMinionPersona: async (minionId: string, persona: any) => {
        try {
          const updatedPersona = await minionApi.updatePersona(minionId, persona)
          get().updateMinion(minionId, { persona: updatedPersona })
          toast.success('Persona updated!')
        } catch (error) {
          console.error('Failed to update persona:', error)
          toast.error('Failed to update persona')
          throw error
        }
      },
      
      updateMinionEmotionalState: async (minionId: string, state: any) => {
        try {
          // Use the update-emotional-state endpoint with API_BASE_URL
          const response = await fetch(`${API_BASE_URL}/api/v2/minions/${minionId}/update-emotional-state`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(state)
          })
          
          if (!response.ok) {
            throw new Error(`Failed to update emotional state: ${response.statusText}`)
          }
          
          // Fetch the updated minion to get the new state
          const minion = await minionApi.get(minionId)
          get().updateMinion(minionId, minion)
          toast.success('Emotional state updated!')
        } catch (error) {
          console.error('Failed to update emotional state:', error)
          toast.error('Failed to update emotional state')
          throw error
        }
      }
    }),
    {
      name: 'legion-store'
    }
  )
)

// Global reference for WebSocket event forwarding
declare global {
  interface Window {
    __taskStore?: any
  }
}