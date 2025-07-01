"""
Dependencies V2 - Clean Event-Driven Architecture

This sets up the proper dependencies using the refactored services.
"""

from typing import Optional
import logging
import os

# ADK imports
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

from .application.services.channel_service_v2 import ChannelServiceV2
from .application.services.minion_service_v2 import MinionServiceV2
from .application.services.task_service_v2 import TaskServiceV2 # Add this
# Import abstract repository interfaces (if needed for type hinting elsewhere, but not for instantiation here)
# from .infrastructure.persistence.repositories import (
#     ChannelRepository,
#     MessageRepository,
#     MinionRepository,
#     TaskRepository
# )
# Import concrete in-memory repository implementations
from .infrastructure.persistence.repositories.memory import (
    ChannelRepositoryMemory,
    MessageRepositoryMemory,
    MinionRepositoryMemory,
    TaskRepositoryMemory
)
from .infrastructure.adk.events import get_event_bus
from gemini_legion_backend.api.websocket.event_bridge import WebSocketEventBridge

logger = logging.getLogger(__name__)


class ServiceContainerV2:
    """
    Container for all services in the clean architecture.
    
    No circular dependencies, everything flows through events.
    """
    
    def __init__(self):
        # Repositories
        self.channel_repo = ChannelRepositoryMemory()
        self.message_repo = MessageRepositoryMemory()
        self.minion_repo = MinionRepositoryMemory()
        # self.memory_repo = MemoryRepository()  # Doesn't exist, removed by future Claude
        self.task_repo = TaskRepositoryMemory()
        
        # Event bus - THE communication backbone
        self.event_bus = get_event_bus()
        
        # ADK Runner setup - SHARED instance for all agents
        # For now, use in-memory session service (can switch to DatabaseSessionService for production)
        self.session_service = InMemorySessionService()
        
        # Note: Runner will be initialized with agents as they're created
        # For now, we'll pass the session service to MinionServiceV2
        
        # Services - Note NO circular dependencies!
        self.channel_service = ChannelServiceV2(
            channel_repository=self.channel_repo,
            message_repository=self.message_repo
        )
        
        self.minion_service = MinionServiceV2(
            minion_repository=self.minion_repo,
            api_key=os.getenv("GOOGLE_API_KEY"),
            session_service=self.session_service  # Pass session service for Runner usage
        )

        # Add TaskServiceV2 instantiation
        self.task_service = TaskServiceV2(
            task_repository=self.task_repo
        )
        
        # WebSocket bridge will be set up in main.py with sio instance
        self.websocket_bridge: Optional[WebSocketEventBridge] = None
        
        logger.info("ServiceContainerV2 initialized with clean architecture, including TaskServiceV2.")
    
    async def start_all(self):
        """Start all services"""
        logger.info("Starting all services...")
        
        # Start services
        await self.channel_service.start()
        await self.minion_service.start()
        await self.task_service.start() # Start TaskServiceV2
        
        logger.info("All services started")
    
    async def stop_all(self):
        """Stop all services"""
        logger.info("Stopping all services...")
        
        # Stop services in reverse order
        await self.task_service.stop() # Stop TaskServiceV2
        await self.minion_service.stop()
        await self.channel_service.stop()
        
        logger.info("All services stopped")
    
    def get_channel_service(self) -> ChannelServiceV2:
        """Get channel service"""
        return self.channel_service
    
    def get_minion_service(self) -> MinionServiceV2:
        """Get minion service"""
        return self.minion_service
    
    def get_event_bus(self): # Consider adding return type hint if EventBus class is defined
        """Get event bus"""
        return self.event_bus

    def get_task_service(self) -> TaskServiceV2: # Add this getter
        """Get task service"""
        return self.task_service


# Global container instance
_container: Optional[ServiceContainerV2] = None


async def initialize_services_v2():
    """Initialize all services"""
    global _container
    
    if _container is not None:
        logger.warning("Services already initialized")
        return
    
    logger.info("Initializing services with clean architecture...")
    
    # Create container
    _container = ServiceContainerV2()
    
    # Start all services
    await _container.start_all()
    
    logger.info("Services initialized successfully")


async def shutdown_services_v2():
    """Shutdown all services"""
    global _container
    
    if _container is None:
        logger.warning("No services to shutdown")
        return
    
    logger.info("Shutting down services...")
    
    # Stop all services
    await _container.stop_all()
    
    # Clear container
    _container = None
    
    logger.info("Services shutdown complete")


def get_service_container_v2() -> ServiceContainerV2:
    """Get the service container"""
    global _container
    
    if _container is None:
        raise RuntimeError("Services not initialized. Call initialize_services_v2() first.")
    
    return _container


# Dependency injection functions for FastAPI
def get_channel_service_v2() -> ChannelServiceV2:
    """FastAPI dependency for channel service"""
    return get_service_container_v2().get_channel_service()


def get_minion_service_v2() -> MinionServiceV2:
    """FastAPI dependency for minion service"""
    return get_service_container_v2().get_minion_service()


def get_event_bus_dep(): # Consider adding return type hint
    """FastAPI dependency for event bus"""
    return get_service_container_v2().get_event_bus()

def get_task_service_v2() -> TaskServiceV2: # Add this provider
    """FastAPI dependency for task service"""
    return get_service_container_v2().get_task_service()
