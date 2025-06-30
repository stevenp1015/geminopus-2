"""
Minion API Endpoints V2 - Clean Implementation

These endpoints use the refactored minion service with proper event-driven architecture.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..schemas import (
    CreateMinionRequest,
    MinionResponse,
    MinionsListResponse,
    OperationResponse,
    UpdateEmotionalStateRequest,
    UpdateMinionPersonaRequest, # Added schema import
    MinionStatusEnum
)
from ....core.dependencies_v2 import get_minion_service_v2
from ....core.application.services.minion_service_v2 import MinionServiceV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/minions", tags=["minions-v2"])


def convert_minion_to_response(minion_data: Dict[str, Any]) -> MinionResponse:
    """Convert minion data to API response format"""
    try:
        # Get persona safely
        persona_dict = minion_data.get("persona", {})
        
        # Get status safely
        status_str = minion_data.get("status", "idle")
        # Map service status to API enum
        status_map = {
            "operational": "active",
            "healthy": "active",
            "idle": "idle",
            "busy": "busy",
            "error": "error"
        }
        status_enum = status_map.get(status_str, "idle")
        
        # Build persona response
        persona_response = {
            "name": minion_data.get("name", persona_dict.get("name", "Unknown")),  # Get name from minion_data first
            "base_personality": persona_dict.get("base_personality", "Unknown"),
            "quirks": persona_dict.get("quirks", []),
            "catchphrases": persona_dict.get("catchphrases", []),
            "expertise_areas": persona_dict.get("expertise_areas", []),
            "allowed_tools": persona_dict.get("allowed_tools", []),
            "model_name": persona_dict.get("model_name", "gemini-2.5-flash"), # Changed default model
            "temperature": persona_dict.get("temperature", 0.7),
            "max_tokens": persona_dict.get("max_tokens", 4096)
        }
        
        # Build emotional state response
        raw_emotional_state = minion_data.get("emotional_state", {})
        mood_data = raw_emotional_state.get("mood", {})
        
        emotional_state_response = {
            "minion_id": minion_data.get("minion_id", ""),
            "mood": {
                "valence": mood_data.get("valence", 0.0),
                "arousal": mood_data.get("arousal", 0.5),
                "dominance": mood_data.get("dominance", 0.5),
                "curiosity": mood_data.get("curiosity", 0.5),
                "creativity": mood_data.get("creativity", 0.5),
                "sociability": mood_data.get("sociability", 0.5)
            },
            "energy_level": raw_emotional_state.get("energy_level", 0.8),
            "stress_level": raw_emotional_state.get("stress_level", 0.2),
            "opinion_scores": {},  # Empty for now
            "last_updated": raw_emotional_state.get("last_updated", datetime.now().isoformat()),
            "state_version": raw_emotional_state.get("state_version", 1)
        }
        
        return MinionResponse(
            minion_id=minion_data.get("minion_id", ""),
            status=status_enum,
            creation_date=minion_data.get("created_at", datetime.now().isoformat()),
            persona=persona_response,
            emotional_state=emotional_state_response
        )
    except Exception as e:
        logger.error(f"Error converting minion data: {e}", exc_info=True)
        raise


@router.get("/", response_model=MinionsListResponse)
async def list_minions(
    status: Optional[str] = None,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> MinionsListResponse:
    """List all minions"""
    try:
        minions_data = await minion_service.list_minions(status_filter=status)
        minions = [convert_minion_to_response(m) for m in minions_data]
        
        return MinionsListResponse(
            minions=minions,
            total=len(minions),
            active_count=len([m for m in minions if m.status == MinionStatusEnum.ACTIVE])
        )
    except Exception as e:
        logger.error(f"Error listing minions: {e}")
        raise HTTPException(status_code=500, detail="Error listing minions")


@router.get("/{minion_id}", response_model=MinionResponse)
async def get_minion(
    minion_id: str,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
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


@router.post("/spawn", response_model=MinionResponse)
async def spawn_minion(
    request: CreateMinionRequest,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> MinionResponse:
    """Spawn a new minion"""
    try:
        import uuid
        import re
        
        # Generate minion_id
        minion_id = str(uuid.uuid4())
        
        # Create a valid agent name from the minion name
        # Replace spaces and special chars with underscores, ensure it starts with a letter
        agent_name = re.sub(r'[^a-zA-Z0-9_]', '_', request.name)
        if not agent_name[0].isalpha():
            agent_name = f"minion_{agent_name}"
        # Make it unique by appending part of the UUID
        agent_name = f"{agent_name}_{minion_id.split('-')[0]}"
        
        minion_data = await minion_service.spawn_minion(
            minion_id=agent_name,  # Use valid agent name instead of UUID
            name=request.name,
            base_personality=request.personality,  # Map 'personality' to 'base_personality'
            quirks=request.quirks,
            catchphrases=request.catchphrases,
            expertise_areas=request.expertise,  # Map 'expertise' to 'expertise_areas'
            allowed_tools=request.tools # Pass the tools from the request
        )
        
        # Override the minion_id in the response to use the UUID
        minion_data["minion_id"] = minion_id
        
        return convert_minion_to_response(minion_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error spawning minion: {e}")
        raise HTTPException(status_code=500, detail="Error spawning minion")


@router.delete("/{minion_id}", response_model=OperationResponse)
async def despawn_minion(
    minion_id: str,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> OperationResponse:
    """Despawn a minion"""
    try:
        await minion_service.despawn_minion(minion_id)
        
        return OperationResponse(
            status="despawned",
            id=minion_id,
            message=f"Minion {minion_id} despawned successfully",
            timestamp=datetime.now().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error despawning minion: {e}")
        raise HTTPException(status_code=500, detail="Error despawning minion")


@router.post("/{minion_id}/emotional-state", response_model=MinionResponse)
async def update_emotional_state(
    minion_id: str,
    request: UpdateEmotionalStateRequest,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> MinionResponse:
    """Update a minion's emotional state"""
    try:
        mood_delta = None
        if request.mood_changes:
            mood_delta = {
                "valence": request.mood_changes.get("valence", 0),
                "arousal": request.mood_changes.get("arousal", 0),
                "dominance": request.mood_changes.get("dominance", 0)
            }
        
        minion_data = await minion_service.update_emotional_state(
            minion_id=minion_id,
            mood_delta=mood_delta,
            energy_delta=request.energy_change,
            stress_delta=request.stress_change
        )
        
        return convert_minion_to_response(minion_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating emotional state: {e}")
        raise HTTPException(status_code=500, detail="Error updating emotional state")


@router.put("/{minion_id}/persona", response_model=MinionResponse)
async def update_minion_persona_endpoint(
    minion_id: str,
    request: UpdateMinionPersonaRequest,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> MinionResponse:
    """Update a minion's persona details."""
    try:
        # Pass only the fields that are set in the request using model_dump(exclude_unset=True)
        persona_data_to_update = request.model_dump(exclude_unset=True)
        if not persona_data_to_update:
            raise HTTPException(status_code=400, detail="No persona data provided for update.")

        updated_minion_data = await minion_service.update_minion_persona(
            minion_id=minion_id,
            persona_data=persona_data_to_update
        )
        if not updated_minion_data:
            # This case should ideally be caught by ValueError in service if minion not found
            raise HTTPException(status_code=404, detail=f"Minion {minion_id} not found or update failed.")

        return convert_minion_to_response(updated_minion_data)
    except ValueError as e: # Handles minion not found from service
        logger.warning(f"Failed to update persona for minion {minion_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException: # Re-raise existing HTTPExceptions (like the 400 above)
        raise
    except Exception as e:
        logger.error(f"Error updating persona for minion {minion_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error updating persona for minion {minion_id}")


@router.get("/test", response_model=Dict[str, Any])
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify V2 API is working"""
    return {
        "status": "ok",
        "version": "v2",
        "message": "Clean minion service with ADK agents",
        "timestamp": datetime.now().isoformat()
    }
