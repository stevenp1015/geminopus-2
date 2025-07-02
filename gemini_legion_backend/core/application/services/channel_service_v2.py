"""
Channel Service - Refactored with ADK Event Bus

This is the CLEAN implementation using proper event-driven architecture.
No more duplicate paths, no more custom communication systems.
"""

from typing import List, Optional, Dict, Any, Set, Callable
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import asdict
import uuid

# Event bus - THE way to communicate
from ...infrastructure.adk.events import (
    get_event_bus,
    EventType,
    Event,
    ChannelMessageEvent
)

# Domain models
from ...domain import (
    Channel,
    ChannelType,
    Message,
    MessageType,
    ChannelMember,
    ChannelRole
)

# Repositories
from ...infrastructure.persistence.repositories import (
    ChannelRepository,
    MessageRepository
)

logger = logging.getLogger(__name__)


class ChannelServiceV2:
    """
    Channel Service implemented with proper ADK event-driven architecture.
    
    Key principles:
    1. Single source of truth - Event Bus
    2. No duplicate message paths
    3. Clean separation of concerns
    4. ADK-native patterns
    """
    
    def __init__(
        self,
        channel_repository: ChannelRepository,
        message_repository: MessageRepository
    ):
        """
        Initialize the Channel service.
        
        Note: No more comm_system, no more minion_service dependency.
        Everything goes through events.
        """
        self.channel_repo = channel_repository
        self.message_repo = message_repository
        self.event_bus = get_event_bus()
        
        # Active channels cache
        self.active_channels: Dict[str, Channel] = {}
        
        # Background tasks
        self._message_persist_task: Optional[asyncio.Task] = None
        self._channel_cleanup_task: Optional[asyncio.Task] = None
        
        # Message buffer for batched persistence
        self.message_buffer: List[Message] = []
        self._buffer_lock = asyncio.Lock()
        
        # Subscribe to events we care about
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Subscribe to relevant events"""
        # We might want to listen for minion events to auto-add to channels
        self.event_bus.subscribe(EventType.MINION_SPAWNED, self._handle_minion_spawned)
    
    async def _handle_minion_spawned(self, event: Event):
        """Handle minion spawned event - add to public channels"""
        minion_id = event.data.get("minion_id")
        if not minion_id:
            return
        
        # Auto-add to public channels
        for channel in self.active_channels.values():
            if channel.channel_type == ChannelType.PUBLIC:
                try:
                    await self.add_member(channel.channel_id, minion_id, "member", "system")
                except Exception as e:
                    logger.debug(f"Could not add {minion_id} to {channel.channel_id}: {e}")
    
    async def start(self):
        """Start the service and background tasks"""
        logger.info("Starting Channel Service V2 (Event-Driven)...")
        
        # Start background tasks
        self._message_persist_task = asyncio.create_task(self._message_persist_loop())
        self._channel_cleanup_task = asyncio.create_task(self._channel_cleanup_loop())
        
        # Load active channels
        await self._load_active_channels()
        
        logger.info("Channel Service V2 started successfully")
    
    async def stop(self):
        """Stop the service and cleanup"""
        logger.info("Stopping Channel Service V2...")
        
        # Cancel background tasks
        if self._message_persist_task:
            self._message_persist_task.cancel()
        if self._channel_cleanup_task:
            self._channel_cleanup_task.cancel()
        
        # Persist any buffered messages
        await self._flush_message_buffer()
        
        # Save all active channels
        for channel in self.active_channels.values():
            await self.channel_repo.save(channel)
        
        logger.info("Channel Service V2 stopped")
    
    async def create_channel(
        self,
        channel_id: str,
        name: str,
        channel_type: str = "public",
        description: Optional[str] = None,
        creator: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new channel"""
        # Check if exists
        if channel_id in self.active_channels:
            raise ValueError(f"Channel {channel_id} already exists")
        
        # Create domain object
        channel = Channel(
            channel_id=channel_id,
            name=name,
            channel_type=ChannelType(channel_type),
            description=description or "",
            created_at=datetime.now(),
            created_by=creator or "system",
            members=[],
            metadata=metadata or {}
        )
        
        # Add creator as admin
        if creator:
            member = ChannelMember(
                member_id=creator,
                role=ChannelRole.ADMIN,
                joined_at=datetime.now()
            )
            channel.members.append(member)
        
        # Persist
        await self.channel_repo.save(channel)
        
        # Cache
        self.active_channels[channel_id] = channel
        
        # Emit event - THIS is how we notify the system
        await self.event_bus.emit(
            EventType.CHANNEL_CREATED,
            data={
                "channel_id": channel_id,
                "name": name,
                "type": channel_type,
                "creator": creator
            },
            source="channel_service"
        )
        
        logger.info(f"Created channel: {name} ({channel_id})")
        
        return self._channel_to_dict(channel)
    
    async def send_message(
        self,
        channel_id: str,
        sender_id: str,
        content: str,
        message_type: str = "chat",
        metadata: Optional[Dict[str, Any]] = None,
        parent_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a channel.
        
        THIS IS THE ONLY PLACE MESSAGES ARE CREATED AND BROADCAST.
        No more duplicate paths. Just one clean flow.
        """
        channel = self.active_channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")
        
        # Check membership for non-public channels
        if channel.channel_type != ChannelType.PUBLIC:
            if not any(m.member_id == sender_id for m in channel.members):
                raise ValueError(f"{sender_id} is not a member of {channel_id}")
        
        # Create message with proper unique ID
        message = Message(
            message_id=f"msg_{uuid.uuid4()}",  # Guaranteed unique
            channel_id=channel_id,
            sender_id=sender_id,
            content=content,
            message_type=MessageType(message_type),
            timestamp=datetime.now(),
            metadata=metadata or {},
            parent_message_id=parent_message_id
        )
        
        # Add to persistence buffer
        async with self._buffer_lock:
            self.message_buffer.append(message)
        
        # Update channel
        channel.last_activity = datetime.now()
        channel.message_count += 1
        
        # SINGLE EVENT EMISSION - This is THE way
        logger.info(f"[ChannelServiceV2] BEFORE emitting user {sender_id}'s message to bus for channel {channel_id}.")
        try:
            await self.event_bus.emit_channel_message(
                channel_id=channel_id, # Was message.channel_id, but channel_id is direct param
                sender_id=sender_id,   # Was message.sender_id, but sender_id is direct param
                content=content,       # Was message.content, but content is direct param
                source=f"channel_service:{sender_id}", # Original source
                metadata={
                    "message_id": message.message_id, # Keep this from the created message object
                    "message_type": message_type,
                    "parent_message_id": parent_message_id,
                    **(metadata or {})
                }
            )
            logger.info(f"[ChannelServiceV2] AFTER emitting user {sender_id}'s message to bus for channel {channel_id}.")
        except Exception as e_emit:
            logger.error(f"[ChannelServiceV2] ERROR during emit_channel_message for user {sender_id}'s message: {e_emit}", exc_info=True)
        
        # logger.debug(f"Message sent to {channel_id} by {sender_id} via EVENT BUS") # Original log, now covered by AFTER/ERROR
        
        return self._message_to_dict(message)
    
    async def add_member(
        self,
        channel_id: str,
        member_id: str,
        role: str = "member",
        added_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a member to a channel"""
        channel = self.active_channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")
        
        # Check if already member
        if any(m.member_id == member_id for m in channel.members):
            raise ValueError(f"{member_id} is already a member of {channel_id}")
        
        # Create member
        member = ChannelMember(
            member_id=member_id,
            role=ChannelRole(role),
            joined_at=datetime.now(),
            added_by=added_by
        )
        
        # Add to channel
        channel.members.append(member)
        channel.member_count = len(channel.members)
        channel.last_activity = datetime.now()
        
        # Save
        await self.channel_repo.save(channel)
        
        # Emit event
        await self.event_bus.emit(
            EventType.CHANNEL_MEMBER_ADDED,
            data={
                "channel_id": channel_id,
                "member_id": member_id,
                "role": role,
                "added_by": added_by
            },
            source="channel_service"
        )
        
        # Send system message
        await self.send_message(
            channel_id=channel_id,
            sender_id="system",
            content=f"{member_id} joined the channel",
            message_type="system",
            metadata={"event": "member_joined", "member_id": member_id}
        )
        
        logger.info(f"Added {member_id} to channel {channel_id}")
        
        return self._channel_to_dict(channel)
    
    async def list_channels(
        self,
        member_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        include_private: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List channels with filtering"""
        # Get from repository
        channels = await self.channel_repo.list_all(limit, offset)
        
        # Apply filters
        if channel_type:
            channels = [c for c in channels if c.channel_type.value == channel_type]
        
        if not include_private:
            channels = [c for c in channels if c.channel_type != ChannelType.PRIVATE]
        
        if member_id:
            channels = [
                c for c in channels
                if any(m.member_id == member_id for m in c.members)
            ]
        
        return [self._channel_to_dict(c) for c in channels]
    
    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel details"""
        channel = self.active_channels.get(channel_id)
        if not channel:
            channel = await self.channel_repo.get_by_id(channel_id)
            if not channel:
                return None
        
        return self._channel_to_dict(channel)
    
    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get messages from a channel"""
        # Get from repository (offset not supported yet)
        messages = await self.message_repo.get_channel_messages(
            channel_id,
            limit=limit
        )
        
        # Include buffered messages
        async with self._buffer_lock:
            buffered = [
                m for m in self.message_buffer
                if m.channel_id == channel_id
            ]
        
        # Combine and sort
        all_messages = messages + buffered
        all_messages.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit
        all_messages = all_messages[:limit]
        
        return {
            "messages": [self._message_to_dict(m) for m in all_messages],
            "total": len(all_messages),
            "has_more": len(all_messages) == limit
        }
    
    async def _message_persist_loop(self):
        """Background task to persist messages"""
        while True:
            try:
                await asyncio.sleep(5)
                await self._flush_message_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message persist loop: {e}")
    
    async def _flush_message_buffer(self):
        """Flush message buffer to repository"""
        async with self._buffer_lock:
            if not self.message_buffer:
                return
            
            messages_to_save = self.message_buffer.copy()
            self.message_buffer.clear()
        
        # Save messages
        for message in messages_to_save:
            try:
                await self.message_repo.save(message)
            except Exception as e:
                logger.error(f"Failed to persist message {message.message_id}: {e}")
        
        logger.debug(f"Persisted {len(messages_to_save)} messages")
    
    async def _channel_cleanup_loop(self):
        """Background task to clean up channels"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Clean up empty DM channels
                cutoff = datetime.now() - timedelta(days=7)
                
                for channel_id, channel in list(self.active_channels.items()):
                    if (channel.channel_type == ChannelType.DIRECT and
                        channel.message_count == 0 and
                        channel.created_at < cutoff):
                        
                        logger.info(f"Cleaning up empty DM channel {channel_id}")
                        # TODO: Implement delete_channel
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in channel cleanup loop: {e}")
    
    async def _load_active_channels(self):
        """Load active channels from repository"""
        try:
            channels = await self.channel_repo.list_active()
            
            for channel in channels:
                self.active_channels[channel.channel_id] = channel
            
            # Ensure default channels
            await self._ensure_default_channels()
            
            logger.info(f"Loaded {len(channels)} active channels")
            
        except Exception as e:
            logger.error(f"Failed to load active channels: {e}")
    
    async def _ensure_default_channels(self):
        """Ensure default channels exist"""
        default_channels = [
            {
                "channel_id": "general",
                "name": "General",
                "description": "General discussion for all Minions",
                "channel_type": "public"
            },
            {
                "channel_id": "announcements",
                "name": "Announcements",
                "description": "Important system announcements",
                "channel_type": "public"
            },
            {
                "channel_id": "task_coordination",
                "name": "Task Coordination",
                "description": "Task assignment and coordination",
                "channel_type": "public"
            }
        ]
        
        for config in default_channels:
            if config["channel_id"] not in self.active_channels:
                await self.create_channel(**config, creator="system")
    
    def _channel_to_dict(self, channel: Channel) -> Dict[str, Any]:
        """Convert channel to dict"""
        return {
            "channel_id": channel.channel_id,
            "name": channel.name,
            "channel_type": channel.channel_type.value,
            "description": channel.description,
            "created_at": channel.created_at.isoformat(),
            "created_by": channel.created_by,
            "member_count": len(channel.members),
            "message_count": channel.message_count,
            "last_activity": channel.last_activity.isoformat() if channel.last_activity else None,
            "members": [
                {
                    "member_id": m.member_id,
                    "role": m.role.value,
                    "joined_at": m.joined_at.isoformat()
                }
                for m in channel.members
            ],
            "metadata": channel.metadata
        }
    
    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert message to dict"""
        return {
            "message_id": message.message_id,
            "channel_id": message.channel_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "message_type": message.message_type.value,
            "timestamp": message.timestamp.isoformat(),
            "metadata": message.metadata,
            "parent_message_id": message.parent_message_id,
            "reactions": message.reactions,
            "edited": message.edited,
            "edited_at": message.edited_at.isoformat() if message.edited_at else None
        }
