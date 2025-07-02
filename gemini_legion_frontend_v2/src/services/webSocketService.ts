// Purpose: Manages the global WebSocket connection, event subscriptions, and dispatches actions to stores.
// Data_Contract (Interface):
//   Methods:
//     connect(url: string): void
//     disconnect(): void
//     subscribeToMinionUpdates(minionId: string, storeActions: MinionStoreActions): () => void // Returns unsubscribe function
//     subscribeToChannelMessages(channelId: string, storeActions: ChannelStoreActions): () => void // Placeholder
//     // ... other specific event subscriptions
//   Internal: Uses useWebSocket hook for actual connection management.
// State_Management: Manages connection status internally via useWebSocket. Does not hold application data.
// Dependencies & Dependents: Imports useWebSocket, store actions (e.g., from useMinionStore), relevant types. Used by root component (App.tsx or main.tsx) to initialize.
// V2_Compliance_Check: Confirmed.

import { Minion } from '../types';
import { useMinionStore } from '../store/minionStore'; // Assuming Zustand store actions are part of the hook return

// Define a type for the actions we need from useMinionStore
// This makes the webSocketService more testable and less coupled to the exact store implementation.
type MinionStoreActions = {
  addMinion: (minion: Minion) => void;
  removeMinion: (minionId: string) => void;
  updateMinion: (minionData: Partial<Minion> & { minion_id: string }) => void;
};

class WebSocketService {
  private socket: ReturnType<typeof import('../hooks/useWebSocket').default> | null = null;
  private minionStoreActions: MinionStoreActions | null = null;

  // Dynamically import useWebSocket to allow for server-side rendering or testing environments
  // where window/document might not be available immediately.
  private async getWebSocketHook() {
    if (typeof window !== 'undefined') {
      const { default: useWebSocket } = await import('../hooks/useWebSocket');
      return useWebSocket;
    }
    return null;
  }

  public async connect(url: string, minionActions: MinionStoreActions) {
    this.minionStoreActions = minionActions;
    const useWebSocketHook = await this.getWebSocketHook();

    if (!useWebSocketHook) {
      console.warn('WebSocket hook could not be loaded (likely SSR environment). WebSocketService will not connect.');
      return;
    }

    if (this.socket && this.socket.isConnected) {
      console.warn('WebSocketService: Already connected.');
      return;
    }

    // The useWebSocket hook itself needs to be called within a React component's context.
    // This service is a class, not a React component.
    // A common pattern is to initialize the hook in App.tsx and pass the socket instance or methods to this service.
    // For this exercise, we'll simulate the hook's direct usage here, assuming it's adapted or this service is used differently.
    // Let's adjust the approach: this service will manage subscriptions and event handling,
    // but the actual useWebSocket hook instance should be created in a React component (e.g., App.tsx)
    // and its `subscribe` and `unsubscribe` methods passed to this service or used by this service.

    console.error("WebSocketService.connect needs to be refactored. `useWebSocket` is a hook and cannot be called directly in a class. The hook should be used in a React component (e.g., App.tsx), and its `subscribe`/`unsubscribe` methods should be leveraged by this service or passed to it.");
    // This is a placeholder to indicate the connection logic needs proper React context.
    // In a real app, App.tsx would instantiate useWebSocket and this service would be called with the socket instance or its methods.
  }

  // This method would be called from App.tsx after useWebSocket is initialized
  public initializeHandlers(
    socketSubscriber: (event: string, callback: (data: any) => void) => void,
    socketUnsubscriber: (event: string, callback: (data: any) => void) => void
    ) {
    if (!this.minionStoreActions) {
      console.error("MinionStore actions not set in WebSocketService.");
      return;
    }
    const actions = this.minionStoreActions;

    // Minion Event Handlers
    const handleMinionSpawned = (data: { minion: Minion }) => {
      console.log('WS Event: minion_spawned', data);
      if (data && data.minion) actions.addMinion(data.minion);
    };
    const handleMinionDespawned = (data: { minion_id: string }) => {
      console.log('WS Event: minion_despawned', data);
      if (data && data.minion_id) actions.removeMinion(data.minion_id);
    };
    // Generic handler for various minion updates
    const handleMinionUpdated = (data: Partial<Minion> & { minion_id: string }) => {
        console.log('WS Event: minion_updated (or similar like minion_state_changed, minion_emotional_state_updated, minion_persona_updated)', data);
        if (data && data.minion_id) {
            // The backend might send the full minion object or partial updates.
            // The store's updateMinion action is designed to handle partial updates.
            actions.updateMinion(data);
        }
    };

    // Subscribe to specific backend events
    // These event names must match what the backend's WebSocketEventBridge emits.
    socketSubscriber('minion_spawned', handleMinionSpawned);
    socketSubscriber('minion_despawned', handleMinionDespawned);

    // Assuming backend emits a generic 'minion_updated' or specific ones
    // that can all be handled by the same updateMinion logic.
    // Based on event_bridge.py, specific events are emitted:
    socketSubscriber('minion_state_changed', handleMinionUpdated); // This might carry the full minion object
    socketSubscriber('minion_emotional_state_updated', handleMinionUpdated); // This carries { minion_id, emotional_state }
    socketSubscriber('minion_persona_updated', handleMinionUpdated); // This carries { minion_id, persona }
    socketSubscriber('minion_status_changed', handleMinionUpdated); // This carries { minion_id, status }

    // TODO: Add subscriptions for channel events, task events etc.

    // Return an unsubscribe function for cleanup
    return () => {
      socketUnsubscriber('minion_spawned', handleMinionSpawned);
      socketUnsubscriber('minion_despawned', handleMinionDespawned);
      socketUnsubscriber('minion_state_changed', handleMinionUpdated);
      socketUnsubscriber('minion_emotional_state_updated', handleMinionUpdated);
      socketUnsubscriber('minion_persona_updated', handleMinionUpdated);
      socketUnsubscriber('minion_status_changed', handleMinionUpdated);
      // TODO: Unsubscribe other events
    };
  }

  public disconnect() {
    // Disconnection is handled by the useWebSocket hook when its host component unmounts.
    // This service itself doesn't directly control the socket.disconnect() from useWebSocket.
    console.log('WebSocketService: Disconnect called. Actual disconnection managed by useWebSocket hook instance.');
    this.socket = null;
    this.minionStoreActions = null;
  }

  // Example of sending a command (if needed by this service, though often done via components)
  // public sendCommand(command: string, params: any) {
  //   if (this.socket && this.socket.isConnected) {
  //     this.socket.sendMessage(command, params);
  //   } else {
  //     console.warn('WebSocketService: Not connected. Command not sent:', command);
  //   }
  // }
}

// Singleton instance
const webSocketService = new WebSocketService();
export default webSocketService;

// HOW TO USE THIS SERVICE:
// In App.tsx (or a top-level component):
//
// import useWebSocket from './hooks/useWebSocket';
// import webSocketService from './services/webSocketService';
// import { useMinionStore } from './store/minionStore';
//
// function App() {
//   const { addMinion, removeMinion, updateMinion } = useMinionStore.getState(); // Or subscribe to actions
//
//   // Initialize the useWebSocket hook here
//   const { subscribe, unsubscribe, isConnected, sendMessage } = useWebSocket({
//     url: 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket', // Replace with your actual WS URL
//     onMessage: (type, data) => {
//       console.log('Generic WS Message in App:', type, data);
//       // Generic messages can be handled here or by specific subscriptions via webSocketService
//     },
//     onOpen: () => console.log('App: WebSocket Connected'),
//     onClose: () => console.log('App: WebSocket Disconnected'),
//     onError: (err) => console.error('App: WebSocket Error', err),
//   });
//
//   useEffect(() => {
//     if (isConnected) {
//       // Pass the hook's subscribe/unsubscribe methods to the service
//       const cleanupSubscribers = webSocketService.initializeHandlers(
//         subscribe,
//         unsubscribe,
//         // Pass minion store actions
//         // Note: Directly passing store actions like this can work but consider a more decoupled approach
//         // if the service needs to be independent of Zustand's exact hook structure.
//         // For this example, we'll assume useMinionStore provides these actions.
//         { addMinion, removeMinion, updateMinion }
//       );
//       return cleanupSubscribers; // Cleanup on unmount
//     }
//   }, [isConnected, subscribe, unsubscribe, addMinion, removeMinion, updateMinion]);
//
//   // ... rest of App component
// }
