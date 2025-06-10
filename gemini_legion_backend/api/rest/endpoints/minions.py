"""
Minion-related API endpoints

Handles creation, management, and interaction with Minions.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid # Added for generating memory_id

from ..schemas import (
    CreateMinionRequest,
    MinionResponse,
    MinionsListResponse,
    OperationResponse,
    RebootMinionRequest,
    MoodVectorResponse,
    OpinionScoreResponse,
    OpinionEventResponse, # Added for OpinionScoreResponse
    EntityTypeEnum, # Added for OpinionScoreResponse
    EmotionalStateResponse,
    MinionPersonaResponse, # Added for nested persona
    MinionStatusEnum,
    SendMessageRequest,
    UpdateMinionPersonaRequest,
    UpdateEmotionalStateRequest, # Added for the endpoint
    # Memory Schemas
    MemoryListResponse,
    AnyMemoryEntryResponse,
    WorkingMemoryEntryResponse,
    EpisodicMemoryEntryResponse,
    WorkingMemoryEntryDetails,
    EpisodicMemoryEntryDetails
)
from ....core.dependencies import get_minion_service
from ....core.application.services import MinionService
from ....core.domain import MinionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/minions", tags=["minions"])


def convert_minion_to_response(minion_data: Dict[str, Any]) -> MinionResponse:
    """Convert a minion data dict (from service layer) to API response format - SIMPLIFIED FOR DEBUGGING"""
    logger.debug(f"Attempting SIMPLIFIED conversion for minion_data: {minion_data.get('minion_id')}")
    try:
        # Get persona name safely
        persona_dict = minion_data.get("persona", {})
        persona_name = persona_dict.get("name", f"Unknown_{minion_data.get('minion_id', 'NoID')}")
        base_personality = persona_dict.get("base_personality", "Undefined")

        # Get status safely
        status_str = minion_data.get("status", MinionStatusEnum.ERROR.value)
        try:
            current_status_enum = MinionStatusEnum(status_str)
        except ValueError:
            logger.warning(f"Invalid status '{status_str}' for minion {minion_data.get('minion_id')}, defaulting to ERROR.")
            current_status_enum = MinionStatusEnum.ERROR

        # Restore full MinionPersonaResponse construction
        # persona_dict is already defined above as minion_data.get("persona", {})
        persona_response = MinionPersonaResponse(
            name=persona_dict.get("name", "Unknown Name"),
            base_personality=persona_dict.get("base_personality", "Unknown Personality"),
            quirks=persona_dict.get("quirks", []),
            catchphrases=persona_dict.get("catchphrases", []),
            expertise_areas=persona_dict.get("expertise_areas", []),
            allowed_tools=persona_dict.get("allowed_tools", []),
            model_name=persona_dict.get("model_name", "unknown"), # Ensure schema default matches if different
            temperature=persona_dict.get("temperature", 0.7), # Ensure schema default matches
            max_tokens=persona_dict.get("max_tokens", 4096)    # Ensure schema default matches
        )

        # Restore EmotionalStateResponse - Stage 1 (simple fields, empty opinions)
        raw_emotional_state = minion_data.get("emotional_state") # This is a dict from service
        emotional_state_response_stage1: EmotionalStateResponse

        if raw_emotional_state:
            mood_data = raw_emotional_state.get("mood", {})
            mood_response = MoodVectorResponse(
                valence=mood_data.get("valence", 0.0),
                arousal=mood_data.get("arousal", 0.5),
                dominance=mood_data.get("dominance", 0.3),
                curiosity=mood_data.get("curiosity", 0.7),
                creativity=mood_data.get("creativity", 0.6),
                sociability=mood_data.get("sociability", 0.6)
            )
            emotional_state_response_stage1 = EmotionalStateResponse(
                minion_id=minion_data.get("minion_id", "unknown_id_emo_stage1"),
                mood=mood_response,
                energy_level=raw_emotional_state.get("energy_level", 0.8),
                stress_level=raw_emotional_state.get("stress_level", 0.2),
                opinion_scores={ # RESTORING OPINION SCORES DICT, but notable_events still empty
                    entity_id: OpinionScoreResponse(
                        entity_type=EntityTypeEnum(opinion_data.get("entity_type", "UNKNOWN")) if opinion_data.get("entity_type") else EntityTypeEnum.UNKNOWN,
                        trust=opinion_data.get("trust", 0.0),
                        respect=opinion_data.get("respect", 0.0),
                        affection=opinion_data.get("affection", 0.0),
                        interaction_count=opinion_data.get("interaction_count", 0),
                        last_interaction_timestamp=datetime.fromisoformat(ts) if (ts := opinion_data.get("last_interaction_timestamp")) else None,
                        notable_events=[ # NOW RESTORING NOTABLE_EVENTS
                            OpinionEventResponse(
                                event_id=event_data.get("event_id", str(uuid.uuid4())), # Ensure uuid is imported if not already
                                description=event_data.get("description", "Unknown event"),
                                timestamp=datetime.fromisoformat(ets) if (ets := event_data.get("timestamp")) else datetime.now(), # Handle timestamp conversion
                                impact_on_trust=event_data.get("impact_on_trust"),
                                impact_on_respect=event_data.get("impact_on_respect"),
                                impact_on_affection=event_data.get("impact_on_affection"),
                                metadata=event_data.get("metadata", {})
                            )
                            for event_data in opinion_data.get("notable_events", []) if isinstance(event_data, dict)
                        ],
                        overall_sentiment=opinion_data.get("overall_sentiment", 0.0)
                    )
                    for entity_id, opinion_data in raw_emotional_state.get("opinion_scores", {}).items()
                },
                last_updated=raw_emotional_state.get("last_updated", datetime.now().isoformat()),
                state_version=raw_emotional_state.get("state_version", 1)
            )
        else:
            # Fallback if emotional_state is entirely missing from minion_data
            logger.warning(f"Emotional state missing for minion {minion_data.get('minion_id')} during opinion_scores restore. Using default emotional response.")
            default_mood = MoodVectorResponse(valence=0, arousal=0.5, dominance=0.3, curiosity=0.7, creativity=0.6, sociability=0.6)
            emotional_state_response_stage1 = EmotionalStateResponse( # Renaming to current stage variable
                minion_id=minion_data.get("minion_id", "unknown_id_emo_default_ops"),
                mood=default_mood,
                energy_level=0.8,
                stress_level=0.2,
                opinion_scores={}, # Still empty in this fallback
                last_updated=datetime.now().isoformat(),
                state_version=1
            )

        response = MinionResponse(
            minion_id=minion_data.get("minion_id", "unknown_id_main_fallback"),
            status=current_status_enum,
            creation_date=minion_data.get("creation_date", datetime.now().isoformat()),
            persona=persona_response, # Use the more fully constructed persona_response
            emotional_state=emotional_state_response_stage1 # Variable name was emotional_state_response_stage1
        )
        logger.info(f"Successfully converted (DIAGNOSTIC STAGE 4 - FULLY RESTORED notable_events) minion: {response.minion_id}")
        return response
    except Exception as e:
        logger.error(f"!!! CRITICAL ERROR IN SIMPLIFIED convert_minion_to_response for {minion_data.get('minion_id')} !!! Error: {e}", exc_info=True)
        # Fallback to ensure *something* returns if possible, or let it raise
        # This specific fallback might fail if MinionResponse schema has non-optional complex types not provided here.
        # Defaulting to raise to see the error clearly.
        raise



@router.get("/", response_model=MinionsListResponse)
async def list_minions(
    minion_service: MinionService = Depends(get_minion_service)
) -> MinionsListResponse:
    """List all active minions"""
    try:
        minions_data = await minion_service.list_minions()
        
        minions = [convert_minion_to_response(minion) for minion in minions_data]
        
        return MinionsListResponse(
            minions=minions,
            total=len(minions)
        )
    except Exception as e:
        logger.error(f"Error listing minions: {e}")
        raise HTTPException(status_code=500, detail="Error listing minions")


@router.get("/{minion_id}", response_model=MinionResponse)
async def get_minion(
    minion_id: str,
    minion_service: MinionService = Depends(get_minion_service)
) -> MinionResponse:
    """Get a specific minion"""
    try:
        minion_data = await minion_service.get_minion(minion_id)
        
        if not minion_data:
            raise HTTPException(status_code=404, detail="Minion not found")
        
        return convert_minion_to_response(minion_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting minion {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving minion")


@router.post("/spawn", response_model=OperationResponse)
async def spawn_minion(
    request: CreateMinionRequest,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Spawn a new minion"""
    try:
        spawn_result = await minion_service.spawn_minion(
            name=request.name,
            personality=request.personality,
            quirks=request.quirks,
            catchphrases=request.catchphrases,
            expertise=request.expertise,
            tools=request.tools
            # minion_id is now optional in the service and will be generated if not passed
        )
        
        # Assuming spawn_result is a dict that includes the minion_id
        minion_id_from_service = spawn_result.get("minion_id", "UNKNOWN_ID_FROM_SERVICE")
        
        logger.info(f"Spawned minion: {minion_id_from_service} - {request.name}")
        
        return OperationResponse(
            status="spawned",
            id=minion_id_from_service, # Use the ID from the service's response
            message=f"Minion '{request.name}' spawned successfully!   . .   .",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error spawning minion: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/spawn-specialized", response_model=OperationResponse)
async def spawn_specialized_minion(
    minion_type: str,
    name: str,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Spawn a specialized minion (taskmaster, scout, analyst)"""
    try:
        minion_id = await minion_service.spawn_specialized_minion(
            minion_type=minion_type,
            name=name
        )
        
        logger.info(f"Spawned specialized {minion_type}: {minion_id} - {name}")
        
        return OperationResponse(
            status="spawned",
            id=minion_id,
            message=f"Specialized {minion_type} '{name}' spawned successfully! Ready to serve!",
            timestamp=datetime.now().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error spawning specialized minion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{minion_id}", response_model=OperationResponse)
async def despawn_minion(
    minion_id: str,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Despawn a minion"""
    try:
        success = await minion_service.despawn_minion(minion_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Minion not found")
        
        return OperationResponse(
            status="despawned",
            id=minion_id,
            message=f"Minion despawned. Their service will be remembered.  .   .",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error despawning minion {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error despawning minion")


@router.get("/{minion_id}/emotional-state", response_model=EmotionalStateResponse)
async def get_emotional_state(
    minion_id: str,
    minion_service: MinionService = Depends(get_minion_service)
) -> EmotionalStateResponse:
    """Get a minion's current emotional state"""
    try:
        emotional_state = await minion_service.get_emotional_state(minion_id)
        
        if not emotional_state:
            raise HTTPException(status_code=404, detail="Minion not found")
        
        # Convert to response format
        mood = emotional_state.get("mood", {})
        mood_response = MoodVectorResponse(
            valence=mood.get("valence", 0.0),
            arousal=mood.get("arousal", 0.5),
            dominance=mood.get("dominance", 0.3),
            curiosity=mood.get("curiosity", 0.7),
            creativity=mood.get("creativity", 0.6),
            sociability=mood.get("sociability", 0.6)
        )
        
        # Convert opinion scores
        opinion_scores = {}
        for entity_id, opinion in emotional_state.get("opinion_scores", {}).items():
            opinion_scores[entity_id] = OpinionScoreResponse(
                trust=opinion.get("trust", 0.0),
                respect=opinion.get("respect", 0.0),
                affection=opinion.get("affection", 0.0),
                overall_sentiment=opinion.get("overall_sentiment", 0.0)
            )
        
        return EmotionalStateResponse(
            minion_id=minion_id,
            mood=mood_response,
            energy_level=emotional_state.get("energy_level", 0.8),
            stress_level=emotional_state.get("stress_level", 0.2),
            opinion_scores=opinion_scores,
            last_updated=emotional_state.get("last_updated", datetime.now().isoformat()),
            state_version=emotional_state.get("state_version", 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting emotional state for {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving emotional state")


@router.post("/{minion_id}/update-emotional-state")
async def update_emotional_state(
    minion_id: str,
    request: UpdateEmotionalStateRequest, # Changed from updates: Dict[str, Any]
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Update a minion's emotional state using a structured request."""
    try:
        # Pass only the fields that were actually set in the request
        update_payload = request.dict(exclude_unset=True)
        if not update_payload:
            # Return a success if no actual updates were provided, or a 400 if that's preferred.
            # For now, treating as a no-op success.
            return OperationResponse(
                status="no_op",
                id=minion_id,
                message="No emotional state changes provided.",
                timestamp=datetime.now().isoformat()
            )

        success = await minion_service.update_emotional_state(minion_id, update_payload)
        
        if not success:
            raise HTTPException(status_code=404, detail="Minion not found")
        
        return OperationResponse(
            status="updated",
            id=minion_id,
            message="Emotional state updated successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emotional state for {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating emotional state")


@router.put("/{minion_id}/persona", response_model=MinionPersonaResponse)
async def update_minion_persona(
    minion_id: str,
    request: UpdateMinionPersonaRequest,
    minion_service: MinionService = Depends(get_minion_service)
) -> MinionPersonaResponse:
    """Update a minion's persona details."""
    try:
        updated_persona_data = await minion_service.update_minion_persona(minion_id, request)
        if not updated_persona_data:
            raise HTTPException(status_code=404, detail="Minion not found or persona update failed")
        
        # The service should return data that can be directly used by MinionPersonaResponse
        # Assuming updated_persona_data is a dict matching MinionPersonaResponse fields
        return MinionPersonaResponse(**updated_persona_data)
        
    except HTTPException:
        raise
    except ValueError as ve: # Catch specific validation or logic errors from service
        logger.error(f"ValueError updating persona for {minion_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating persona for {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating minion persona")


@router.get("/{minion_id}/memories", response_model=MemoryListResponse)
async def get_minion_memories_endpoint(
    minion_id: str,
    memory_type: Optional[str] = Query(None, enum=["working", "episodic", "semantic", "procedural"]),
    limit: int = Query(10, ge=1, le=100),
    minion_service: MinionService = Depends(get_minion_service)
) -> MemoryListResponse:
    """Get memories for a specific minion, with optional type filtering."""
    try:
        service_memories_data = await minion_service.get_minion_memories(
            minion_id=minion_id,
            memory_type=memory_type, # Pass along the type filter
            limit=limit
        )
        
        if service_memories_data is None: # Service might return None if minion not found/not active
             raise HTTPException(status_code=404, detail=f"Minion {minion_id} not found or no memories accessible.")

        response_memories: List[AnyMemoryEntryResponse] = []
        for mem_data in service_memories_data:
            converted_mem = convert_service_memory_to_response(minion_id, mem_data)
            if converted_mem:
                response_memories.append(converted_mem)
        
        return MemoryListResponse(
            memories=response_memories,
            minion_id=minion_id,
            memory_type_filter=memory_type,
            total_returned=len(response_memories)
        )
    except ValueError as ve: # Catch errors from convert_service_memory_to_response or service layer
        logger.error(f"ValueError retrieving memories for {minion_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memories for {minion_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving memories for minion {minion_id}")


@router.post("/{minion_id}/send-message")
async def send_minion_message(
    minion_id: str,
    request: SendMessageRequest,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Have a minion send a message to a channel"""
    try:
        success = await minion_service.send_message(
            minion_id=minion_id,             # This comes from the URL path parameter
            channel_id=request.channel_id, # Corrected: Use channel_id from SendMessageRequest
            content=request.content        # Corrected: Use content from SendMessageRequest
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Minion not found or unable to send")
        
        return OperationResponse(
            status="sent",
            id=minion_id,
            message=f"Message sent to channel '{request.channel_id}'", # Corrected: use request.channel_id
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message from {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error sending message")


@router.post("/{minion_id}/assign-task")
async def assign_task_to_minion(
    minion_id: str,
    task_id: str,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Assign a task to a minion"""
    try:
        success = await minion_service.assign_task(minion_id, task_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Minion not found or task assignment failed"
            )
        
        return OperationResponse(
            status="assigned",
            id=task_id,
            message=f"Task assigned to minion {minion_id}",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning task to {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error assigning task")


@router.post("/{minion_id}/complete-task")
async def complete_minion_task(
    minion_id: str,
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
    minion_service: MinionService = Depends(get_minion_service)
) -> OperationResponse:
    """Mark a task as completed by a minion"""
    try:
        success = await minion_service.complete_task(minion_id, task_id, result)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Minion not found or task completion failed"
            )
        
        return OperationResponse(
            status="completed",
            id=task_id,
            message=f"Task completed by minion {minion_id}!",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task for {minion_id}: {e}")
        raise HTTPException(status_code=500, detail="Error completing task")