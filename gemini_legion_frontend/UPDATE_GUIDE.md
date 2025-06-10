# Gemini Legion V2 - Frontend Update Guide

This document outlines the necessary changes to integrate the Gemini Legion frontend with the new V2 backend architecture. The V2 backend utilizes an event-driven system with a central event bus and updated API endpoints, aiming for a cleaner and more robust communication flow.

## 1. Core Architectural Changes to Understand

Before diving into specific frontend modifications, it's crucial to understand the V2 backend's philosophical shifts:

*   **Event-Driven Core:** Most real-time updates will now flow through a central `EventBus`. The frontend will receive these via a WebSocket bridge (`EventBridge`). This means a more standardized event structure.
*   **ADK-Native Agents:** The new `minion_agent_v2.py` aims for a more idiomatic use of Google's ADK, which might affect the nature of responses and interactions.
*   **Deprecated V1 Communication:** The old `InterMinionCommunicationSystem` and `CommunicationCapability.py` (from V1) are being phased out. Frontend logic relying on their specific behaviors or event types must be updated.

## 2. WebSocket Integration Overhaul

The existing WebSocket connection and event handling logic need a significant update.

### 2.1 Connection Endpoint
*   **Verify URL:** The WebSocket connection URL may have changed. Confirm the correct endpoint, likely now served via `main_v2.py` and connected through the `EventBridge`.
*   **Authentication:** Ensure any existing authentication tokens or handshake procedures are compatible with the V2 WebSocket setup.

### 2.2 Unified Event Handling
*   **New Event Structure:** V2 events from the `EventBus` will likely have a consistent wrapper structure. Expect something like:
    ```json
    {
      "event_type": "module.action.v2", // e.g., "channel.message.v2", "minion.status.v2"
      "payload": { /* event-specific data */ },
      "timestamp": "YYYY-MM-DDTHH:mm:ss.sssZ",
      "source_service": "service_name", // e.g., "ChannelServiceV2"
      "event_id": "unique-event-id"
    }
    ```
*   **Centralized Listener:** Instead of multiple `socket.on('specific_event', ...)` listeners for V1, consider a primary `socket.on('event', (event_data) => { ... })` listener. Inside this, use a `switch` statement on `event_data.event_type` to route to specific handlers.
    ```typescript
    // Conceptual V2 WebSocket event handler in the frontend
    socket.on('event', (event) => {
      logger.debug('V2 WebSocket event received:', event);
      switch (event.event_type) {
        case 'channel.message.v2':
          const messagePayload = event.payload; // Assuming payload contains the message object
          store.dispatch(chatActions.addMessage(messagePayload.message)); // Adapt to your store
          break;
        case 'minion.status.v2':
          const statusPayload = event.payload; // Assuming minion_id and status are in payload
          store.dispatch(legionActions.updateMinionStatus(statusPayload));
          break;
        case 'minion.spawned.v2':
          // Handle new minion appearing
          break;
        case 'minion.despawned.v2':
          // Handle minion removal
          break;
        // Add cases for all relevant V2 events (tasks, emotional updates, etc.)
        default:
          logger.warn(`Received unhandled V2 WebSocket event type: ${event.event_type}`);
      }
    });
    ```

### 2.3 State Management Integration
*   Update your frontend state management (Zustand, Redux, etc.) actions and reducers/slices to process the new V2 event payloads correctly. Ensure data structures in your store align with V2 domain models.

## 3. API Endpoint Migration to `/api/v2/`

All HTTP REST API calls must be transitioned from V1 endpoints to their V2 counterparts.

### 3.1 Identifying V2 Endpoints
*   **Source of Truth:** The `main_v2.py` file and the `*_v2.py` files within `gemini_legion_backend/api/rest/endpoints/` (e.g., `channels_v2.py`, `minions_v2.py`) define the new V2 API routes, request methods, and expected request/response schemas.
*   **Prefix:** Expect most, if not all, V2 API endpoints to be prefixed with `/api/v2/`.

### 3.2 Updating API Client / Service Functions
*   Locate all API call definitions in your frontend (e.g., in `src/services/api/` or similar).
*   Change base URLs and paths to point to V2. Example:
    ```typescript
    // Before (V1)
    // const fetchMinions = () => apiClient.get('/api/minions');
    // const postMessageToChannel = (channelId, data) => apiClient.post(`/api/channels/${channelId}/send`, data);

    // After (V2)
    // const fetchMinionsV2 = () => apiClient.get('/api/v2/minions');
    // const postMessageToChannelV2 = (channelId, data) => apiClient.post(`/api/v2/channels/${channelId}/messages`, data); // Example path change
    ```
*   **Request/Response Schemas:** V2 endpoints will use Pydantic schemas defined in or referenced by the `*_v2.py` backend files. Ensure your frontend's TypeScript interfaces for request bodies and expected responses match these V2 schemas. Pay close attention to field names, data types, and optional/required properties.

### 3.3 Authentication and Headers
*   Verify that authentication mechanisms (e.g., token headers) are still compatible and correctly implemented for `/api/v2/` calls.

## 4. Adapting to V2 Data Structures

The domain models in V2 might have evolved. Ensure your frontend interfaces and components correctly reflect these.

*   **Minion Data:** `MinionPersona`, `EmotionalState`, `MinionStatus` structures from V2 should be mirrored in frontend types.
*   **Channel & Message Data:** Check for any changes in how channels, members, and messages are represented.
*   **Task Data (Future):** When the Task service is refactored to V2, its data structures will also need frontend adaptation.

## 5. Removing Obsolete V1 Code

*   Once V2 integration is stable, systematically remove all frontend code related to V1 API calls and V1 WebSocket event handling to prevent confusion and dead code.
*   This includes old service functions, V1-specific state management logic, and UI components that might have been tied to V1 data structures.

## 6. Testing the V2 Integration

*   **Comprehensive UI Testing:** Test all user flows that involve fetching data, posting data, or receiving real-time updates.
*   **WebSocket Event Verification:** Use browser developer tools to inspect incoming V2 WebSocket messages and ensure they are correctly parsed and reflected in the UI and application state.
*   **API Call Verification:** Monitor network requests to confirm they are targeting V2 endpoints with correct payloads, and that responses are handled appropriately.
*   **Error Handling:** Test how the frontend handles potential errors from V2 API calls or unexpected WebSocket events.

This guide provides a roadmap for the frontend transition. Success depends on careful cross-referencing with the V2 backend's actual implementation details, particularly the API endpoint definitions in `main_v2.py`, the `*_v2.py` service and endpoint files, and the event definitions related to the new `EventBus`.

Good luck, and may your frontend integrate flawlessly with the glorious V2 backend!