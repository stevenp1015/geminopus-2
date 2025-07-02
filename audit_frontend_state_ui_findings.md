# Frontend State and UI Rendering Audit

This document analyzes frontend Zustand stores and their interaction with WebSocket events and UI components, particularly concerning the display of newly spawned minions.

## Zustand Stores Overview

*   **`legionStore.ts`:** Manages overall Legion state, including the list of `minions`, WebSocket connection status, and probably handles `MINION_SPAWNED`, `MINION_DESPAWNED`, `MINION_EMOTIONAL_CHANGE` events.
*   **`chatStore.ts`:** Manages chat channels and messages. Handles `CHANNEL_MESSAGE` events.
*   **`taskStore.ts`:** Manages tasks. Handles `TASK_STATUS_UPDATE` events.

## Minion Spawning Flow and UI Update

**Scenario:** User spawns a new minion. Why might it not appear in the UI?

1.  **API Call & Backend Processing:**
    *   `legionStore.spawnMinion` action calls `minionApi.spawnMinion`.
    *   Backend `MinionServiceV2.spawn_minion` successfully creates the minion, saves it, starts the agent, and emits `MINION_SPAWNED` event via `GeminiEventBus`.
    *   `WebSocketEventBridge` picks up this event and sends it to connected clients.

2.  **Frontend WebSocket Event Handling (`legionStore.ts`):**
    *   The `legionStore` should have a Socket.IO event listener:
        ```typescript
        // Conceptual listener in legionStore.ts
        socket.on('MINION_SPAWNED', (data: { minion: MinionType }) => {
          // Add the new minion to the store's minions array
          set((state) => ({
            minions: [...state.minions, data.minion],
          }));
        });
        ```
    *   **Potential Issues Here:**
        *   **Event Name Mismatch:** Is the frontend listening for the exact event name string that the backend's `WebSocketEventBridge` is emitting? (e.g., "MINION_SPAWNED" vs "minion_spawned").
        *   **Data Payload Mismatch:** Does the structure of `data.minion` received from WebSocket exactly match the `MinionType` expected by the store and UI components? (The `audit_data_flow_types_findings.md` suggests this is likely okay).
        *   **Store Update Logic:** Is the logic for adding the new minion to the `minions` array correct? (e.g., avoiding duplicates if events are somehow re-processed, ensuring immutability for state updates).
        *   **WebSocket Connection:** Is the WebSocket connection active and healthy when the event is emitted? `legionStore` likely manages this.

3.  **UI Component Subscription (`LegionDashboard.tsx`, `MinionCard.tsx`):**
    *   UI components that display the list of minions (e.g., `LegionDashboard.tsx`) should be subscribed to the `minions` array in `legionStore`.
        ```typescript
        // Conceptual usage in a React component
        import { useLegionStore } from '@/store'; // Or specific store import

        const LegionDashboard = () => {
          const minions = useLegionStore((state) => state.minions);
          // Render MinionCard for each minion in the 'minions' array
          return (
            <div>
              {minions.map(minion => <MinionCard key={minion.minion_id} minion={minion} />)}
            </div>
          );
        };
        ```
    *   **Potential Issues Here:**
        *   **Incorrect Subscription:** Is the component correctly selecting the `minions` state from the store?
        *   **Re-render Not Triggered:** Is Zustand correctly triggering a re-render of the component when the `minions` array changes? (Usually reliable, but worth checking if complex selectors are used).
        *   **Filtering/Display Logic:** Is there any client-side filtering or conditional rendering logic that might inadvertently hide the new minion?
        *   **`key` Prop:** Ensure `MinionCard` components have a stable and unique `key` (e.g., `minion.minion_id`) when mapping, for efficient rendering.

## Specific Investigation Points for "Newly Spawned Minion Not Appearing":

1.  **Verify WebSocket Event Reception:**
    *   Use browser developer tools (Network tab) to inspect WebSocket traffic. Confirm that the `MINION_SPAWNED` event is received by the frontend when a minion is spawned on the backend.
    *   Check the exact payload of the received WebSocket message.

2.  **Debug `legionStore` Event Handler:**
    *   Place `console.log` statements inside the `socket.on('MINION_SPAWNED', ...)` handler in `legionStore.ts` to see if it fires and what data it receives.
    *   Log the state of the `minions` array before and after the update.

3.  **Inspect UI Component Props:**
    *   Use React Developer Tools to inspect the props of `LegionDashboard` (or equivalent component) and verify that its `minions` prop updates correctly after the WebSocket event is processed by the store.
    *   Check if `MinionCard` components are being rendered for new minions.

4.  **Check for Client-Side Errors:**
    *   Look for any JavaScript errors in the browser console that might occur during event handling or UI rendering.

5.  **State Initialization and Hydration (Less Likely for this specific issue, but possible):**
    *   If there's any complex state hydration logic (e.g., from localStorage), ensure it doesn't interfere with real-time updates.

## General Frontend State Health:

*   **Immutability:** Ensure all Zustand state updates are performed immutably (e.g., creating new arrays/objects instead of modifying existing ones directly). This is crucial for Zustand to detect changes and trigger re-renders.
*   **Selectors:** Use efficient selectors for accessing store state in components. Overly complex selectors can sometimes cause performance issues or unexpected behavior.
*   **WebSocket Lifecycle Management:** `legionStore` should robustly handle WebSocket connection, disconnection, and reconnection events, ensuring event listeners are correctly re-established if the connection drops and comes back.

---
*Audit in progress. Will further investigate specific store implementations and UI component code by reading `legionStore.ts`, relevant UI components, and `WebSocketEventBridge.py`.*
