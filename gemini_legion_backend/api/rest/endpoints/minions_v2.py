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
    UpdateEmotionalStateRequest
)
from ....core.dependencies_v2 import get_minion_service_v2
from ....core.application.services.minion_service_v2 import MinionServiceV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/minions", tags=["minions-v2"])


def convert_minion_to_response(minion_data: dict) -> MinionResponse:
    """Convert minion data to API response format"""
    return MinionResponse(
        id=minion_data["minion_id"],
        name=minion_data["name"],
        status=minion_data["status"],
        created_at=minion_data["created_at"],
        persona={
            "base_personality": minion_data["persona"]["base_personality"],
            "traits": minion_data["persona"]["personality_traits"],
            "quirks": minion_data["persona"]["quirks"],
            "response_style": minion_data["persona"]["response_length"],
            "catchphrases": minion_data["persona"]["catchphrases"],
            "expertise": minion_data["persona"]["expertise_areas"]
        },
        emotional_state={
            "mood": minion_data["emotional_state"]["mood"],
            "energy": minion_data["emotional_state"]["energy_level"],
            "stress": minion_data["emotional_state"]["stress_level"]
        },
        is_active=minion_data.get("is_active", False)
    )


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
            active_count=len([m for m in minions if m.is_active])
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


@router.post("/", response_model=MinionResponse)
async def spawn_minion(
    request: CreateMinionRequest,
    minion_service: MinionServiceV2 = Depends(get_minion_service_v2)
) -> MinionResponse:
    """Spawn a new minion"""
    try:
        import uuid
        minion_id = request.minion_id or str(uuid.uuid4())
        
        minion_data = await minion_service.spawn_minion(
            minion_id=minion_id,
            name=request.name,
            base_personality=request.base_personality,
            personality_traits=request.personality_traits,
            quirks=request.quirks,
            response_length=request.response_style or "medium",
            catchphrases=request.catchphrases,
            expertise_areas=request.expertise_areas,
            model_name=request.model or "gemini-2.0-flash-exp"
        )
        
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


@router.get("/test", response_model=Dict[str, Any])
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint to verify V2 API is working"""
    return {
        "status": "ok",
        "version": "v2",
        "message": "Clean minion service with ADK agents",
        "timestamp": datetime.now().isoformat()
    }
