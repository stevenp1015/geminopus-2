"""
WebSocket handler for real-time communication

Manages WebSocket connections and real-time updates.
Fixed version that eliminates duplicate methods and syntax errors.
"""

from typing import Dict, Set, Optional, List, Callable
import asyncio
import logging
import socketio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions"""
    
    def __init__(self):
        self.sio: Optional[socketio.AsyncServer] = None
        
        # Active connections: sid -> {"client_id": str}
        self.active_connections: Dict[str, Dict] = {}

        # Channel subscriptions: channel_id -> Set[sid]
        self.channel_subscriptions: Dict[str, Set[str]] = {}
        
        # Client subscriptions: sid -> Set[channel_id] (tracks what a specific SID is subscribed to)
        self.sid_to_channel_subscriptions: Dict[str, Set[str]] = {}
        
        # Minion subscriptions: minion_id -> Set[sid]
        self.minion_subscriptions: Dict[str, Set[str]] = {}
        
        # Service container (set during app startup)
        self.services: Optional['ServiceContainer'] = None

    def set_sio_instance(self, sio_server: socketio.AsyncServer):
        """Set the Socket.IO instance for event emission"""
        self.sio = sio_server
        logger.info("Socket.IO server instance set in ConnectionManager")
    
    def set_services(self, services: 'ServiceContainer'):
        """Set the service container for event broadcasting"""
        self.services = services
        logger.info("Services connected to WebSocket manager")

    async def handle_connect(self, sid: str, client_id: str):
        """Handle Socket.IO client connection"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for handle_connect")
            return

        self.active_connections[sid] = {"client_id": client_id}
        self.sid_to_channel_subscriptions[sid] = set()
        
        logger.info(f"Client {client_id} (SID: {sid}) connected. Total: {len(self.active_connections)}")
        
        # Send connection confirmation
        try:
            await self.sio.emit(
                'connection_established',
                {"client_id": client_id, "sid": sid, "timestamp": datetime.now().isoformat()},
                room=sid
            )
        except Exception as e:
            logger.error(f"Failed to send connection confirmation to {sid}: {e}")

    async def handle_disconnect(self, sid: str):
        """Handle Socket.IO client disconnection"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for handle_disconnect")
            return

        client_info = self.active_connections.pop(sid, None)
        client_id = client_info.get("client_id", "Unknown") if client_info else "Unknown"

        # Unsubscribe from all channels this SID was part of
        if sid in self.sid_to_channel_subscriptions:
            for channel_id in list(self.sid_to_channel_subscriptions[sid]):
                if channel_id in self.channel_subscriptions:
                    self.channel_subscriptions[channel_id].discard(sid)
                    if not self.channel_subscriptions[channel_id]:
                        del self.channel_subscriptions[channel_id]
                try:
                    await self.sio.leave_room(sid, channel_id)
                except Exception as e:
                    logger.error(f"Error leaving room {channel_id} for sid {sid}: {e}")
            del self.sid_to_channel_subscriptions[sid]
        
        # Remove from minion subscriptions
        sids_to_remove_from_minions = []
        for minion_id, sids in self.minion_subscriptions.items():
            if sid in sids:
                sids.discard(sid)
                if not sids:
                    sids_to_remove_from_minions.append(minion_id)
        
        for minion_id in sids_to_remove_from_minions:
            del self.minion_subscriptions[minion_id]
            try:
                await self.sio.leave_room(sid, f"minion_{minion_id}")
            except Exception as e:
                logger.error(f"Error leaving minion room for {minion_id}, sid {sid}: {e}")

        logger.info(f"Client {client_id} (SID: {sid}) disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, sid: str, message_payload: dict):
        """Send a message to a specific client by SID"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for send_personal_message")
            return
        if sid in self.active_connections:
            event_name = message_payload.pop("type", "personal_message")
            try:
                await self.sio.emit(event_name, message_payload, room=sid)
            except Exception as e:
                logger.error(f"Error sending personal message to SID {sid}: {e}")
    
    async def broadcast_to_channel(self, channel_id: str, message_payload: dict, exclude_sid: Optional[str] = None):
        """Broadcast a message to all clients subscribed to a channel using Socket.IO"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for broadcast_to_channel")
            return
        
        if channel_id not in self.channel_subscriptions or not self.channel_subscriptions[channel_id]:
            logger.debug(f"No SIDs subscribed to channel {channel_id}, not broadcasting.")
            return
        
        event_name = message_payload.pop("type", "channel_message")
        try:
            await self.sio.emit(event_name, message_payload, room=channel_id, skip_sid=exclude_sid)
        except Exception as e:
            logger.error(f"Error broadcasting to channel {channel_id}: {e}")
    
    async def broadcast_to_all(self, message_payload: dict):
        """Broadcast a message to all connected clients using Socket.IO"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for broadcast_to_all")
            return
        
        event_name = message_payload.pop("type", "global_broadcast")
        try:
            await self.sio.emit(event_name, message_payload)
        except Exception as e:
            logger.error(f"Error in broadcast_to_all: {e}")
    
    async def subscribe_to_channel(self, sid: str, channel_id: str):
        """Subscribe a client (by SID) to a channel using Socket.IO rooms"""
        if not self.sio:
            logger.error("SIO server not initialized for subscribe_to_channel")
            return
        if sid not in self.active_connections:
            logger.warning(f"subscribe_to_channel: SID {sid} not found in active_connections.")
            return

        try:
            await self.sio.enter_room(sid, channel_id)
            
            if channel_id not in self.channel_subscriptions:
                self.channel_subscriptions[channel_id] = set()
            self.channel_subscriptions[channel_id].add(sid)
            
            if sid not in self.sid_to_channel_subscriptions:
                self.sid_to_channel_subscriptions[sid] = set()
            self.sid_to_channel_subscriptions[sid].add(channel_id)
            
            client_info = self.active_connections.get(sid, {})
            logger.info(f"Client {client_info.get('client_id', sid)} (SID: {sid}) subscribed to channel {channel_id}")
            
            await self.sio.emit('subscription_confirmed', {
                "type": "channel", 
                "id": channel_id, 
                "timestamp": datetime.now().isoformat()
            }, room=sid)
        except Exception as e:
            logger.error(f"Error subscribing SID {sid} to channel {channel_id}: {e}")

    async def unsubscribe_from_channel(self, sid: str, channel_id: str):
        """Unsubscribe a client (by SID) from a channel using Socket.IO rooms"""
        if not self.sio:
            logger.error("SIO server not initialized for unsubscribe_from_channel")
            return
        if sid not in self.active_connections:
            logger.warning(f"unsubscribe_from_channel: SID {sid} not found in active_connections.")
            return

        try:
            await self.sio.leave_room(sid, channel_id)
            
            if channel_id in self.channel_subscriptions:
                self.channel_subscriptions[channel_id].discard(sid)
                if not self.channel_subscriptions[channel_id]:
                    del self.channel_subscriptions[channel_id]
            
            if sid in self.sid_to_channel_subscriptions:
                self.sid_to_channel_subscriptions[sid].discard(channel_id)

            client_info = self.active_connections.get(sid, {})
            logger.info(f"Client {client_info.get('client_id', sid)} (SID: {sid}) unsubscribed from channel {channel_id}")

            await self.sio.emit('unsubscription_confirmed', {
                "type": "channel", 
                "id": channel_id, 
                "timestamp": datetime.now().isoformat()
            }, room=sid)
        except Exception as e:
            logger.error(f"Error unsubscribing SID {sid} from channel {channel_id}: {e}")

    async def subscribe_to_minion(self, sid: str, minion_id: str):
        """Subscribe a client (by SID) to minion updates using Socket.IO rooms"""
        if not self.sio:
            logger.error("SIO server not initialized for subscribe_to_minion")
            return
        if sid not in self.active_connections:
            logger.warning(f"subscribe_to_minion: SID {sid} not found in active_connections.")
            return

        try:
            minion_room = f"minion_{minion_id}"
            await self.sio.enter_room(sid, minion_room)
            
            if minion_id not in self.minion_subscriptions:
                self.minion_subscriptions[minion_id] = set()
            self.minion_subscriptions[minion_id].add(sid)
            
            client_info = self.active_connections.get(sid, {})
            logger.info(f"Client {client_info.get('client_id', sid)} (SID: {sid}) subscribed to minion {minion_id}")

            await self.sio.emit('subscription_confirmed', {
                "type": "minion", 
                "id": minion_id, 
                "timestamp": datetime.now().isoformat()
            }, room=sid)
        except Exception as e:
            logger.error(f"Error subscribing SID {sid} to minion {minion_id}: {e}")

    async def unsubscribe_from_minion(self, sid: str, minion_id: str):
        """Unsubscribe a client (by SID) from minion updates using Socket.IO rooms"""
        if not self.sio:
            logger.error("SIO server not initialized for unsubscribe_from_minion")
            return
        if sid not in self.active_connections:
            logger.warning(f"unsubscribe_from_minion: SID {sid} not found in active_connections.")
            return

        try:
            minion_room = f"minion_{minion_id}"
            await self.sio.leave_room(sid, minion_room)

            if minion_id in self.minion_subscriptions:
                self.minion_subscriptions[minion_id].discard(sid)
                if not self.minion_subscriptions[minion_id]:
                    del self.minion_subscriptions[minion_id]
            
            client_info = self.active_connections.get(sid, {})
            logger.info(f"Client {client_info.get('client_id', sid)} (SID: {sid}) unsubscribed from minion {minion_id}")

            await self.sio.emit('unsubscription_confirmed', {
                "type": "minion", 
                "id": minion_id, 
                "timestamp": datetime.now().isoformat()
            }, room=sid)
        except Exception as e:
            logger.error(f"Error unsubscribing SID {sid} from minion {minion_id}: {e}")

    async def broadcast_minion_update(self, minion_id: str, update_type: str, data: dict):
        """Broadcast updates about a specific minion using Socket.IO"""
        if not self.sio:
            logger.error("SIO server not initialized in ConnectionManager for broadcast_minion_update")
            return
        
        minion_room = f"minion_{minion_id}"
        if not self.minion_subscriptions.get(minion_id):
            logger.debug(f"No SIDs subscribed to minion {minion_id}, not broadcasting update.")
            return

        payload = {
            "minion_id": minion_id,
            "update_type": update_type,
            **data
        }
        try:
            await self.sio.emit('minion_update', payload, room=minion_room)
        except Exception as e:
            logger.error(f"Error broadcasting minion update for {minion_id} to room {minion_room}: {e}")
    
    async def handle_sio_command(self, event_name: str, sid: str, params: Optional[Dict]):
        """Handle a Socket.IO command from a client by SID"""
        if not self.sio:
            logger.error(f"SIO server not initialized for handle_sio_command: {event_name}")
            return
        if sid not in self.active_connections:
            logger.warning(f"handle_sio_command: SID {sid} not found for event {event_name}")
            return

        client_info = self.active_connections.get(sid, {})
        client_id_for_log = client_info.get('client_id', sid)

        try:
            if event_name == "ping":
                await self.sio.emit('pong', {"timestamp": datetime.now().isoformat()}, room=sid)
            
            elif event_name == "subscribe_channel":
                channel_id = params.get("channel_id") if params else None
                if channel_id:
                    await self.subscribe_to_channel(sid, channel_id)
                else:
                    await self.sio.emit('command_error', {
                        "command": event_name, 
                        "message": "channel_id missing"
                    }, room=sid)
            
            elif event_name == "unsubscribe_channel":
                channel_id = params.get("channel_id") if params else None
                if channel_id:
                    await self.unsubscribe_from_channel(sid, channel_id)
                else:
                    await self.sio.emit('command_error', {
                        "command": event_name, 
                        "message": "channel_id missing"
                    }, room=sid)

            elif event_name == "subscribe_minion":
                minion_id = params.get("minion_id") if params else None
                if minion_id:
                    await self.subscribe_to_minion(sid, minion_id)
                else:
                    await self.sio.emit('command_error', {
                        "command": event_name, 
                        "message": "minion_id missing"
                    }, room=sid)

            elif event_name == "unsubscribe_minion":
                minion_id = params.get("minion_id") if params else None
                if minion_id:
                    await self.unsubscribe_from_minion(sid, minion_id)
                else:
                    await self.sio.emit('command_error', {
                        "command": event_name, 
                        "message": "minion_id missing"
                    }, room=sid)
            
            elif event_name == "get_subscriptions":
                channels = list(self.sid_to_channel_subscriptions.get(sid, set()))
                minions_subscribed = [
                    m_id for m_id, sids_in_room in self.minion_subscriptions.items() 
                    if sid in sids_in_room
                ]
                await self.sio.emit('subscriptions_list', {
                    "channels": channels,
                    "minions": minions_subscribed,
                    "timestamp": datetime.now().isoformat()
                }, room=sid)
            
            else:
                logger.warning(f"Unknown SIO command: {event_name} from Client {client_id_for_log} (SID: {sid})")
                await self.sio.emit('command_error', {
                    "command": event_name, 
                    "message": "Unknown command"
                }, room=sid)
        
        except Exception as e:
            logger.error(f"Error handling SIO command {event_name} from Client {client_id_for_log} (SID: {sid}): {e}")
            try:
                await self.sio.emit('command_error', {
                    "command": event_name, 
                    "message": "Error processing command"
                }, room=sid)
            except Exception as emit_e:
                logger.error(f"Failed to send command_error for {event_name} to SID {sid}: {emit_e}")

    async def broadcast_service_event(self, event_name_from_service: str, event_data: dict):
        """
        THE MISSING METHOD THAT CAUSED YOUR SPAWNING CHAOS
        
        Broadcast a service event to relevant Socket.IO clients/rooms.
        This is the method that your minion spawning was desperately trying to call.
        """
        if not self.sio:
            logger.error(f"SIO server not initialized for broadcast_service_event: {event_name_from_service}")
            return

        try:
            target_event_name = event_name_from_service
            target_room = None
            custom_payload = event_data.copy()

            if event_name_from_service == "minion_spawned":
                # Broadcast to all clients - new minion has joined the Legion
                logger.info(f"Broadcasting minion_spawned event: {event_data}")
                
            elif event_name_from_service == "minion_despawned":
                # Broadcast to all clients - minion has left the Legion
                logger.info(f"Broadcasting minion_despawned event: {event_data}")
                
            elif event_name_from_service == "minion_emotional_state_updated":
                minion_id = event_data.get("minion_id")
                if minion_id:
                    target_room = f"minion_{minion_id}"
                    logger.info(f"Broadcasting emotional state update for minion {minion_id}")
                else:
                    logger.warning("minion_emotional_state_updated event missing minion_id for room targeting")
                    return
            
            elif event_name_from_service == "minion_status_changed":
                minion_id = event_data.get("minion_id")
                if minion_id:
                    target_room = f"minion_{minion_id}"
                    logger.info(f"Broadcasting status change for minion {minion_id}: {event_data.get('status')}")
                else:
                    logger.warning("minion_status_changed event missing minion_id for room targeting")
                    # Fall through to global broadcast
            
            elif event_name_from_service == "minion_persona_updated":
                minion_id = event_data.get("minion_id")
                if minion_id:
                    target_room = f"minion_{minion_id}"
                    logger.info(f"Broadcasting persona update for minion {minion_id}")
                else:
                    logger.warning("minion_persona_updated event missing minion_id for room targeting, not broadcasting.")
                    return # Explicitly do nothing if no target
            
            elif event_name_from_service == "minion_updated":
                # Payload for "minion_updated" is {"minion": minion_data_dict}, minion_data_dict contains "minion_id"
                minion_data = event_data.get("minion")
                extracted_minion_id = None
                if isinstance(minion_data, dict):
                    extracted_minion_id = minion_data.get("minion_id")
                
                if extracted_minion_id:
                    target_room = f"minion_{extracted_minion_id}"
                    logger.info(f"Broadcasting 'minion_updated' event for minion {extracted_minion_id} to room {target_room}")
                else:
                    logger.warning(
                        f"For 'minion_updated' event, 'minion_id' was not found in the expected nested structure "
                        f"event_data['minion']['minion_id']. Event data: {str(event_data)[:250]}. Not broadcasting."
                    )
                    return # Explicitly do nothing if no target_room can be determined
            
            elif event_name_from_service == "message_sent":
                channel_id = event_data.get("channel_id")
                if channel_id:
                    target_room = channel_id
                    logger.info(f"Broadcasting message to channel {channel_id}")
                else:
                    logger.warning(f"message_sent event missing channel_id: {custom_payload}")
                    return
            
            elif event_name_from_service == "channel_created":
                logger.info(f"Broadcasting channel_created event: {event_data}")
                
            elif event_name_from_service == "channel_updated":
                logger.info(f"Broadcasting channel_updated event: {event_data}")
                
            elif event_name_from_service == "channel_member_added":
                logger.info(f"Broadcasting channel_member_added event: {event_data}")
                
            elif event_name_from_service == "channel_member_removed":
                logger.info(f"Broadcasting channel_member_removed event: {event_data}")
                
            elif event_name_from_service == "channel_deleted":
                logger.info(f"Broadcasting channel_deleted event: {event_data}")
                
            # Task events
            elif event_name_from_service in [
                "task_created", "task_updated", "task_assigned", 
                "task_status_changed", "task_completed"
            ]:
                logger.info(f"Broadcasting task event {event_name_from_service}: {event_data}")
                
            else:
                logger.warning(f"Unhandled service event type: {event_name_from_service}. Broadcasting to all.")
            
            # Execute the broadcast
            if target_room:
                await self.sio.emit(target_event_name, custom_payload, room=target_room)
                logger.debug(f"Event {target_event_name} sent to room {target_room}")
            else:
                await self.sio.emit(target_event_name, custom_payload)
                logger.debug(f"Event {target_event_name} sent to all clients")
                
        except Exception as e:
            logger.error(f"Error broadcasting service event {event_name_from_service} via Socket.IO: {e}")


# Global connection manager instance
connection_manager = ConnectionManager()
