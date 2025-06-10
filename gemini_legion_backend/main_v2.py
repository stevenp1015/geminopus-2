"""
Gemini Legion Backend V2 - Clean Event-Driven Architecture

This is the PROPER implementation following the original design document.
No more custom communication systems, no more duplicate paths, just clean ADK patterns.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import socketio

# API routers - V2 versions
from .api.rest.endpoints.health import router as health_router # Direct import of health
from .api.rest.endpoints.channels_v2 import router as channels_v2_router
from .api.rest.endpoints.minions_v2 import router as minions_v2_router
# Add tasks_v2_router when available and needed by main_v2:
# from .api.rest.endpoints.tasks_v2 import router as tasks_v2_router

# Core V2 systems
from .core.dependencies_v2 import (
    initialize_services_v2,
    shutdown_services_v2,
    get_service_container_v2
)

# WebSocket event bridge
from .api.websocket.event_bridge import WebSocketEventBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - CLEAN VERSION"""
    # Startup
    logger.info("🚀 Gemini Legion Backend V2 starting...")
    logger.info("   Clean event-driven architecture")
    logger.info("   No duplicate message paths")
    logger.info("   Proper ADK integration")
    
    # Initialize services
    await initialize_services_v2()
    
    # Get container
    container = get_service_container_v2()
    app.state.container = container
    
    # Create WebSocket bridge
    bridge = WebSocketEventBridge(sio)
    container.websocket_bridge = bridge
    
    logger.info("✅ Gemini Legion Backend V2 initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Gemini Legion Backend V2 shutting down...")
    await shutdown_services_v2()
    logger.info("👋 Gemini Legion Backend V2 shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Gemini Legion Backend V2",
    description="Clean event-driven implementation of the AI minion legion",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc"
)

# Socket.IO Server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)  # Keep old health endpoint
app.include_router(channels_v2_router)
app.include_router(minions_v2_router)

# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle Socket.IO connection"""
    logger.info(f"Socket.IO client connected: {sid}")
    
    # Get bridge from app state
    container = get_service_container_v2()
    if container.websocket_bridge:
        await container.websocket_bridge.handle_client_connect(sid, auth)


@sio.event
async def disconnect(sid):
    """Handle Socket.IO disconnection"""
    logger.info(f"Socket.IO client disconnected: {sid}")
    
    container = get_service_container_v2()
    if container.websocket_bridge:
        await container.websocket_bridge.handle_client_disconnect(sid)


@sio.on("subscribe_channel")
async def handle_subscribe_channel(sid, data):
    """Subscribe to channel events"""
    channel_id = data.get("channel_id")
    if not channel_id:
        await sio.emit("error", {"message": "channel_id required"}, to=sid)
        return
    
    container = get_service_container_v2()
    if container.websocket_bridge:
        await container.websocket_bridge.subscribe_to_channel(sid, channel_id)


@sio.on("unsubscribe_channel")
async def handle_unsubscribe_channel(sid, data):
    """Unsubscribe from channel events"""
    channel_id = data.get("channel_id")
    if not channel_id:
        await sio.emit("error", {"message": "channel_id required"}, to=sid)
        return
    
    container = get_service_container_v2()
    if container.websocket_bridge:
        await container.websocket_bridge.unsubscribe_from_channel(sid, channel_id)


@sio.on("subscribe_minion")
async def handle_subscribe_minion(sid, data):
    """Subscribe to minion events"""
    minion_id = data.get("minion_id")
    if not minion_id:
        await sio.emit("error", {"message": "minion_id required"}, to=sid)
        return
    
    container = get_service_container_v2()
    if container.websocket_bridge:
        await container.websocket_bridge.subscribe_to_minion(sid, minion_id)


@sio.on("get_subscriptions")
async def handle_get_subscriptions(sid, data):
    """Get current subscriptions"""
    container = get_service_container_v2()
    if container.websocket_bridge:
        subscriptions = await container.websocket_bridge.get_subscriptions(sid)
        await sio.emit("subscriptions", subscriptions, to=sid)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Gemini Legion Backend V2",
        "version": "2.0.0",
        "status": "operational",
        "architecture": "clean event-driven",
        "message": "No more duplicates, no more custom bullshit, just clean ADK patterns",
        "documentation": "/api/v2/docs"
    }


@app.get("/api/v2/status")
async def v2_status():
    """V2 Status endpoint"""
    container = get_service_container_v2()
    
    # Get some stats
    channels = await container.channel_service.list_channels()
    minions = await container.minion_service.list_minions()
    
    return {
        "status": "operational",
        "version": "2.0.0",
        "architecture": {
            "event_driven": True,
            "message_paths": 1,  # SINGLE PATH
            "communication": "ADK Event Bus",
            "agents": "Native ADK patterns"
        },
        "stats": {
            "channels": len(channels),
            "minions": len(minions),
            "active_minions": len([m for m in minions if m.get("is_active")])
        }
    }


# Wrap FastAPI app with Socket.IO
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting Gemini Legion Backend V2 on {host}:{port}")
    logger.info("Clean architecture, no duplicates, proper ADK")
    
    uvicorn.run(
        "gemini_legion_backend.main_v2:asgi_app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
