"""
WebSocket Event Bridge - Clean ADK Event Bus to WebSocket Bridge

This subscribes to the event bus and broadcasts relevant events to WebSocket clients.
No more custom routing, no more duplicate paths.
"""

import logging
import json
from typing import Dict, Set, Optional, Any, List
from datetime import datetime

from gemini_legion_backend.core.infrastructure.adk.events import (
    get_event_bus,
    EventType,
    Event
)

logger = logging.getLogger(__name__)


class WebSocketEventBridge:
    """
    Bridge between ADK Event Bus and WebSocket clients.
    
    This is the ONLY place where events get sent to the frontend.
    Clean, simple, no duplicates.
    """
    
    def __init__(self, sio):
        """
        Initialize the bridge.
        
        Args:
            sio: Socket.IO server instance
        """
        self.sio = sio
        self.event_bus = get_event_bus()
        
        # Track client subscriptions
        self.channel_subscriptions: Dict[str, Set[str]] = {}  # channel_id -> set of sids
        self.minion_subscriptions: Dict[str, Set[str]] = {}   # minion_id -> set of sids
        
        # Subscribe to all events we want to forward
        self._setup_event_subscriptions()
        
        logger.info("WebSocketEventBridge initialized - Single path from events to WebSocket")
    
    def _setup_event_subscriptions(self):
        """Subscribe to events that should be forwarded to WebSocket"""
        # Channel events
        self.event_bus.subscribe(EventType.CHANNEL_MESSAGE, self._handle_channel_message)
        self.event_bus.subscribe(EventType.CHANNEL_CREATED, self._handle_channel_event)
        self.event_bus.subscribe(EventType.CHANNEL_UPDATED, self._handle_channel_event)
        self.event_bus.subscribe(EventType.CHANNEL_DELETED, self._handle_channel_event)
        self.event_bus.subscribe(EventType.CHANNEL_MEMBER_ADDED, self._handle_channel_event)
        self.event_bus.subscribe(EventType.CHANNEL_MEMBER_REMOVED, self._handle_channel_event)
        
        # Minion events
        self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_event)
        self.event_bus.subscribe(EventType.MINION_DESPAWNED, self._handle_minion_event)
        self.event_bus.subscribe(EventType.MINION_STATE_CHANGED, self._handle_minion_event)
        self.event_bus.subscribe(EventType.MINION_EMOTIONAL_CHANGE, self._handle_minion_event)
        self.event_bus.subscribe(EventType.MINION_ERROR, self._handle_minion_event) # Added from 3.3.1

        # Task events
        task_event_types = [
            EventType.TASK_CREATED, EventType.TASK_UPDATED, EventType.TASK_STATUS_CHANGED,
            EventType.TASK_ASSIGNED, EventType.TASK_DECOMPOSED, EventType.TASK_PROGRESS_UPDATE,
            EventType.TASK_COMPLETED, EventType.TASK_FAILED, EventType.TASK_CANCELLED,
            EventType.TASK_DELETED
        ]
        for event_type in task_event_types:
            if hasattr(event_type, 'value'): # Check if it's a valid enum member
                self.event_bus.subscribe(event_type, self._handle_task_event)

        logger.info("WebSocketEventBridge subscribed to all relevant events, including detailed task events")

    async def _handle_task_event(self, event: Event): # Ensure 'Event' type hint is correct
        """Handle generic task events and broadcast them."""
        task_id = event.data.get("task_id")
        if not task_id:
            logger.warning(f"Task event received without task_id: {event.type.value if isinstance(event.type, Enum) else event.type}, data: {event.data}")
            return
        
        ws_event_name = "task_event" # Unified event name for frontend

        payload = {
            "event_type": event.type.value if isinstance(event.type, Enum) else str(event.type),
            "task_id": task_id,
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        }

        await self.sio.emit(ws_event_name, payload)
        logger.debug(f"Broadcast {payload['event_type']} (as {ws_event_name}) for task {task_id}. Data keys: {list(event.data.keys())}")

    async def _handle_channel_message(self, event: Event):
        """Handle channel message events"""
        channel_id = event.data.get("channel_id")
        if not channel_id:
            return
        
        # Get subscribed clients for this channel
        subscribers = self.channel_subscriptions.get(channel_id, set())
        
        if not subscribers:
            logger.debug(f"No WebSocket subscribers for channel {channel_id}")
            return
        
        # Format message for WebSocket (matching frontend Message interface)
        sender_id = event.data.get("sender_id")
        
        # Determine sender_type based on sender_id
        sender_type = "user"  # Default
        if sender_id == "system":
            sender_type = "system"
        elif sender_id and sender_id != "commander":
            sender_type = "minion"  # Assume non-system, non-commander senders are minions
        
        # Map message_type to frontend type enum
        message_type = event.metadata.get("message_type", "chat")
        frontend_type = "CHAT"  # Default
        if message_type == "system":
            frontend_type = "SYSTEM"
        elif message_type == "task":
            frontend_type = "TASK"
        
        ws_message = {
            "type": "message",
            "channel_id": channel_id,
            "message": {
                "message_id": event.data.get("message_id"),
                "channel_id": channel_id,  # Frontend expects this in message object too
                "sender_id": sender_id,
                "sender_type": sender_type,  # Required by frontend
                "type": frontend_type,       # Required by frontend  
                "content": event.data.get("content"),
                "timestamp": event.data.get("timestamp"),
                "metadata": event.metadata
            }
        }
        
        # Emit to all subscribers
        for sid in subscribers:
            await self.sio.emit("message_sent", ws_message, to=sid)
        
        logger.debug(f"Broadcast message to {len(subscribers)} clients for channel {channel_id}")
    
    async def _handle_channel_event(self, event: Event):
        """Handle non-message channel events"""
        channel_id = event.data.get("channel_id")
        if not channel_id:
            return
        
        # Get event type name for WebSocket
        event_name = event.type.value.replace("channel.", "channel_")
        
        # Format for WebSocket
        ws_event = {
            "type": event_name,
            "channel_id": channel_id,
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        }
        
        # Broadcast to all connected clients (channel events are global)
        await self.sio.emit("channel_event", ws_event)
        
        logger.debug(f"Broadcast {event_name} to all clients")
    
    async def _handle_minion_event(self, event: Event):
        """Handle minion events"""
        event_name = event.type.value.replace("minion.", "minion_")
        minion_id_for_routing = None
        ws_payload = {"type": event_name, "timestamp": event.timestamp.isoformat()}

        if event.type == EventType.MINION_SPAWNED or event.type == EventType.MINION_STATE_CHANGED:
            # These events have data = {"minion": {...full_minion_object...}}
            minion_data_obj = event.data.get("minion")
            if minion_data_obj and isinstance(minion_data_obj, dict):
                minion_id_for_routing = minion_data_obj.get("minion_id")
                ws_payload["minion_id"] = minion_id_for_routing
                ws_payload["minion"] = minion_data_obj # Pass the whole minion object for spawn/state change
            else:
                logger.warning(f"Malformed {event.type.value} data: 'minion' object missing or not a dict. Data: {event.data}")
                return
        elif event.data and "minion_id" in event.data:
            # For other events like MINION_DESPAWNED, MINION_EMOTIONAL_CHANGE, MINION_ERROR
            # where event.data is flat, e.g., {"minion_id": "id", "name": "name"} or {"minion_id": "id", "emotional_state": {...}}
            minion_id_for_routing = event.data.get("minion_id")
            ws_payload["minion_id"] = minion_id_for_routing
            # Spread other keys from event.data into the ws_payload
            # Example: for emotional_change, this adds "emotional_state": {...} to ws_payload
            # For despawned, this adds "name": "name"
            for key, value in event.data.items():
                if key not in ws_payload: # Avoid overwriting minion_id if it was already set differently
                    ws_payload[key] = value
        else:
            logger.warning(f"Minion event {event.type.value} received without 'minion_id' or 'minion' object in data. Data: {event.data}")
            return

        if not minion_id_for_routing:
            logger.warning(f"Could not determine minion_id for routing minion event {event.type.value}. Data: {event.data}")
            return
        
        # Get subscribers for this minion
        subscribers = self.minion_subscriptions.get(minion_id_for_routing, set())
        
        # Emit specific event names instead of generic "minion_event"
        specific_event_name = event.type.value.replace("minion.", "minion_")
        
        # Broadcast spawn/despawn events to all clients, others only to subscribers
        if event.type in [EventType.MINION_SPAWNED, EventType.MINION_DESPAWNED]:
            await self.sio.emit(specific_event_name, ws_payload)  # Emit specific event name
            logger.debug(f"Broadcast {specific_event_name} to all clients")
        else:
            # Only to subscribers
            for sid in subscribers:
                await self.sio.emit(specific_event_name, ws_payload, to=sid)
            logger.debug(f"Broadcast {specific_event_name} to {len(subscribers)} subscribers")
        
        logger.debug(f"Emitted {specific_event_name} for minion {minion_id_for_routing}")
    
    async def handle_client_connect(self, sid: str, auth: Optional[Dict[str, Any]] = None):
        """Handle new WebSocket client connection"""
        logger.info(f"WebSocket client connected: {sid}")
        
        # Send initial connection confirmation
        await self.sio.emit("connected", {
            "status": "connected",
            "sid": sid,
            "timestamp": datetime.now().isoformat()
        }, to=sid)
    
    async def handle_client_disconnect(self, sid: str):
        """Handle WebSocket client disconnection"""
        # Remove from all subscriptions
        for channel_subs in self.channel_subscriptions.values():
            channel_subs.discard(sid)
        
        for minion_subs in self.minion_subscriptions.values():
            minion_subs.discard(sid)
        
        logger.info(f"WebSocket client disconnected: {sid}")
    
    async def subscribe_to_channel(self, sid: str, channel_id: str):
        """Subscribe a client to channel events"""
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        
        self.channel_subscriptions[channel_id].add(sid)
        
        await self.sio.emit("subscribed", {
            "type": "channel",
            "id": channel_id,
            "status": "subscribed"
        }, to=sid)
        
        logger.info(f"Client {sid} subscribed to channel {channel_id}")
    
    async def unsubscribe_from_channel(self, sid: str, channel_id: str):
        """Unsubscribe a client from channel events"""
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(sid)
        
        await self.sio.emit("unsubscribed", {
            "type": "channel",
            "id": channel_id,
            "status": "unsubscribed"
        }, to=sid)
        
        logger.info(f"Client {sid} unsubscribed from channel {channel_id}")
    
    async def subscribe_to_minion(self, sid: str, minion_id: str):
        """Subscribe a client to minion events"""
        if minion_id not in self.minion_subscriptions:
            self.minion_subscriptions[minion_id] = set()
        
        self.minion_subscriptions[minion_id].add(sid)
        
        await self.sio.emit("subscribed", {
            "type": "minion",
            "id": minion_id,
            "status": "subscribed"
        }, to=sid)
        
        logger.info(f"Client {sid} subscribed to minion {minion_id}")
    
    async def unsubscribe_from_minion(self, sid: str, minion_id: str):
        """Unsubscribe a client from minion events"""
        if minion_id in self.minion_subscriptions:
            self.minion_subscriptions[minion_id].discard(sid)
        
        await self.sio.emit("unsubscribed", {
            "type": "minion",
            "id": minion_id,
            "status": "unsubscribed"
        }, to=sid)
        
        logger.info(f"Client {sid} unsubscribed from minion {minion_id}")
    
    async def get_subscriptions(self, sid: str) -> Dict[str, List[str]]:
        """Get all subscriptions for a client"""
        subscriptions = {
            "channels": [],
            "minions": []
        }
        
        # Find all channel subscriptions
        for channel_id, subs in self.channel_subscriptions.items():
            if sid in subs:
                subscriptions["channels"].append(channel_id)
        
        # Find all minion subscriptions
        for minion_id, subs in self.minion_subscriptions.items():
            if sid in subs:
                subscriptions["minions"].append(minion_id)
        
        return subscriptions
