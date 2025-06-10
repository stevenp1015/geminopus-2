"""
Channel API Endpoints V2 - Clean Implementation

These endpoints use the refactored channel service with proper event-driven architecture.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..schemas import (
    CreateChannelRequest,
    SendMessageRequest,
    ChannelResponse,
    ChannelTypeEnum,
    ChannelsListResponse,
    MessageResponse,
    MessagesListResponse,
    OperationResponse,
    MessageTypeEnum,
    AddMemberRequest
)
from ....core.dependencies_v2 import get_channel_service_v2
from ....core.application.services.channel_service_v2 import ChannelServiceV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/channels", tags=["channels-v2"])


def convert_channel_to_response(channel_data: dict) -> ChannelResponse:
    """Convert channel data to API response format"""
    channel_type = ChannelTypeEnum.PRIVATE if channel_data.get("channel_type") == "private" else ChannelTypeEnum.PUBLIC
    
    member_ids = []
    if "members" in channel_data:
        members_data = channel_data["members"]
        if members_data and isinstance(members_data[0], dict):
            member_ids = [member["member_id"] for member in members_data]
        else:
            member_ids = members_data
    
    return ChannelResponse(
        id=channel_data["channel_id"],
        name=channel_data["name"],
        description=channel_data.get("description"),
        type=channel_type,
        members=member_ids,
        created_at=channel_data["created_at"]
    )


def convert_message_to_response(message_data: dict) -> MessageResponse:
    """Convert message data to API response format"""
    # Map message types
    message_type = MessageTypeEnum.CHAT
    if message_data.get("message_type") == "system":
        message_type = MessageTypeEnum.SYSTEM
    elif message_data.get("message_type") == "task":
        message_type = MessageTypeEnum.TASK
    
    return MessageResponse(
        message_id=message_data["message_id"],
        sender=message_data["sender_id"],
        content=message_data["content"],
        timestamp=message_data["timestamp"],
        type=message_type,
        channel_id=message_data["channel_id"],
        metadata=message_data.get("metadata", {})
    )


@router.get("/", response_model=ChannelsListResponse)
async def list_channels(
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> ChannelsListResponse:
    """List all channels"""
    try:
        channels_data = await channel_service.list_channels()
        channels = [convert_channel_to_response(ch) for ch in channels_data]
        
        return ChannelsListResponse(
            channels=channels,
            total=len(channels)
        )
    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        raise HTTPException(status_code=500, detail="Error listing channels")


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> ChannelResponse:
    """Get a specific channel"""
    try:
        channel_data = await channel_service.get_channel(channel_id)
        
        if not channel_data:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        return convert_channel_to_response(channel_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving channel")


@router.post("/", response_model=ChannelResponse)
async def create_channel(
    request: CreateChannelRequest,
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> ChannelResponse:
    """Create a new channel"""
    try:
        import uuid
        channel_id = str(uuid.uuid4())
        
        channel_data = await channel_service.create_channel(
            channel_id=channel_id,
            name=request.name,
            channel_type=request.channel_type.value,
            description=request.description,
            creator="api_user"  # TODO: Get from auth
        )
        
        # Add initial members if specified
        if request.members:
            for member_id in request.members:
                try:
                    await channel_service.add_member(
                        channel_id=channel_id,
                        member_id=member_id,
                        role="member",
                        added_by="api_user"
                    )
                except ValueError as e:
                    logger.warning(f"Could not add member {member_id}: {e}")
        
        # Get updated channel
        final_channel = await channel_service.get_channel(channel_id)
        
        return convert_channel_to_response(final_channel)
        
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{channel_id}/members", response_model=OperationResponse)
async def add_channel_member(
    channel_id: str,
    request: AddMemberRequest,
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> OperationResponse:
    """Add a member to a channel"""
    try:
        await channel_service.add_member(
            channel_id=channel_id,
            member_id=request.minion_id,
            role="member",
            added_by="api_user"
        )
        
        return OperationResponse(
            status="success",
            id=channel_id,
            message=f"Added {request.minion_id} to channel",
            timestamp=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding member: {e}")
        raise HTTPException(status_code=500, detail="Error adding member")


@router.get("/{channel_id}/messages", response_model=MessagesListResponse)
async def get_channel_messages(
    channel_id: str,
    limit: int = 50,
    offset: int = 0,
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> MessagesListResponse:
    """Get messages from a channel"""
    try:
        result = await channel_service.get_channel_messages(
            channel_id=channel_id,
            limit=limit,
            offset=offset
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        messages = [convert_message_to_response(msg) for msg in result["messages"]]
        
        return MessagesListResponse(
            messages=messages,
            total=result["total"],
            has_more=result["has_more"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving messages")


@router.post("/{channel_id}/messages", response_model=MessageResponse)
async def send_message(
    channel_id: str,
    request: SendMessageRequest,
    channel_service: ChannelServiceV2 = Depends(get_channel_service_v2)
) -> MessageResponse:
    """
    Send a message to a channel.
    
    This is THE endpoint for sending messages. Clean, simple, no duplicates.
    """
    try:
        # Determine message type
        message_type = "chat"
        if request.sender == "system":
            message_type = "system"
        elif "[TASK]" in request.content:
            message_type = "task"
        
        # Send through the service
        message_data = await channel_service.send_message(
            channel_id=channel_id,
            sender_id=request.sender,
            content=request.content,
            message_type=message_type
        )
        
        logger.info(f"Message sent to {channel_id} from {request.sender} via V2 API")
        
        return convert_message_to_response(message_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Error sending message")


@router.get("/test", response_model=Dict[str, Any])
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify V2 API is working"""
    return {
        "status": "ok",
        "version": "v2",
        "message": "Clean event-driven architecture",
        "timestamp": datetime.now().isoformat()
    }
