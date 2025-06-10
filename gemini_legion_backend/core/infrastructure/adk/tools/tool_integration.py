"""
Tool Integration Manager for Gemini Legion

This module provides centralized management of all tools available
to Minions, including MCP tools and communication capabilities.
"""

from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from google.adk.tools import BaseTool

from .communication_capability import CommunicationCapability, SendMessageTool, SubscribeChannelTool, AutonomousCommunicationTool
from .mcp import (
    MCPToolRegistry,
    ToolPermissionManager,
    create_filesystem_tools,
    create_computer_use_tools,
    create_web_automation_tools
)
from ...messaging.communication_system import InterMinionCommunicationSystem
from ...messaging.safeguards import CommunicationSafeguards
from ....domain import Minion


logger = logging.getLogger(__name__)


class ToolIntegrationManager:
    """
    Centralized manager for all Minion tools
    
    This class handles tool registration, permission management,
    and tool distribution to Minions based on their roles and permissions.
    """
    
    def __init__(
        self,
        comm_system: Optional[InterMinionCommunicationSystem] = None,
        safeguards: Optional[CommunicationSafeguards] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the tool integration manager
        
        Args:
            comm_system: Communication system for messaging tools
            safeguards: Communication safeguards
            config: Configuration for tools
        """
        self.comm_system = comm_system
        self.safeguards = safeguards
        self.config = config or {}
        
        # Initialize registries
        self.mcp_registry = MCPToolRegistry()
        self.permission_manager = ToolPermissionManager()
        
        # Tool collections by category
        self.web_tools: List[BaseTool] = []
        self.analysis_tools: List[BaseTool] = []
        self.custom_tools: Dict[str, BaseTool] = {}
        
        # Initialize default tools
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize default tool sets"""
        # Filesystem tools
        fs_config = {
            "allowed_paths": self.config.get("allowed_paths", [
                "./data",
                "./diaries",
                "./outputs"
            ]),
            "diary_path": self.config.get("diary_path", "./diaries")
        }
        
        # Ensure directories exist
        for path in fs_config["allowed_paths"]:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        self.filesystem_tools = create_filesystem_tools(fs_config)
        
        # Computer use tools
        self.computer_tools = create_computer_use_tools()
        
        # Web automation tools
        self.web_tools = create_web_automation_tools()
        
        # Register all tools
        for tool in self.filesystem_tools:
            self.mcp_registry.register_tool(type(tool))
        
        for tool in self.computer_tools:
            self.mcp_registry.register_tool(type(tool))
            
        for tool in self.web_tools:
            self.mcp_registry.register_tool(type(tool))
        
        logger.info(
            f"Initialized tools: {len(self.filesystem_tools)} filesystem, "
            f"{len(self.computer_tools)} computer use, {len(self.web_tools)} web automation"
        )
    
    def create_communication_capability(self, minion: Minion) -> Optional[CommunicationCapability]:
        """
        Create communication capability for a Minion
        
        Args:
            minion: The Minion to create capability for
            
        Returns:
            CommunicationCapability if comm system available, None otherwise
        """
        if not self.comm_system or not self.safeguards:
            logger.warning(
                f"Cannot create communication capability for {minion.minion_id}: "
                "Communication system not available"
            )
            return None
        
        return CommunicationCapability(
            minion=minion,
            comm_system=self.comm_system,
            safeguards=self.safeguards
        )
    
    def get_tools_for_minion(self, minion: Minion) -> List[BaseTool]:
        """
        Get all tools available to a specific Minion
        
        Args:
            minion: The Minion requesting tools
            
        Returns:
            List of Tool instances the Minion can use
        """
        tools = []
        
        # Get allowed tool names from persona
        allowed_tools = minion.persona.allowed_tools
        
        # Grant permissions for allowed tools
        for tool_name in allowed_tools:
            self.permission_manager.grant_permission(minion.minion_id, tool_name)
        
        # Collect tools from registry and communication capability
        comm_capability_instance: Optional[CommunicationCapability] = None # Lazily initialize

        for tool_name in allowed_tools:
            # Attempt to get from MCP registry first
            tool_instance: Optional[BaseTool] = self.mcp_registry.create_tool_instance(tool_name)
            
            if not tool_instance:
                # Not in MCP registry, explicitly check if it's a known communication tool
                if comm_capability_instance is None: # Create if not already done for this minion call
                    # Ensure comm_system and safeguards are available before attempting to create CommunicationCapability
                    if self.comm_system and self.safeguards:
                        comm_capability_instance = self.create_communication_capability(minion)
                    else:
                        logger.error( # Changed to error as this is a critical setup issue
                            f"Cannot create CommunicationCapability for {minion.minion_id} due to missing comm_system or safeguards. "
                            "Relevant communication tools will be unavailable."
                        )
                
                if comm_capability_instance: # Proceed only if comm_capability_instance was successfully created
                    if tool_name == SendMessageTool.name and hasattr(comm_capability_instance, 'send_tool'):
                        tool_instance = comm_capability_instance.send_tool
                    elif tool_name == SubscribeChannelTool.name and hasattr(comm_capability_instance, 'subscribe_tool'):
                        tool_instance = comm_capability_instance.subscribe_tool
                    elif tool_name == AutonomousCommunicationTool.name and hasattr(comm_capability_instance, 'autonomous_tool'):
                        tool_instance = comm_capability_instance.autonomous_tool
            
            if tool_instance:
                # Tool instance acquired (either MCP or Communication Tool)
                # Permission should have been granted by the loop at line 146-148.
                # The wrap_tool method itself might re-check or rely on the prior grant.
                wrapped_tool = self.permission_manager.wrap_tool(
                    tool_instance, minion.minion_id
                )
                tools.append(wrapped_tool)
            else:
                # If tool_instance is still None after all checks (MCP registry and specific communication tool checks)
                logger.warning(
                    f"Tool '{tool_name}' requested by Minion '{minion.minion_id}' was not found in the MCP tool registry "
                    f"nor is it a recognized, available communication tool. This tool will not be provided."
                )
        
        logger.info(f"Provided {len(tools)} tools to {minion.minion_id} (Allowed: {len(allowed_tools)} - '{', '.join(allowed_tools)}'). Provided tools: {[tool.name for tool in tools] if tools else 'None'}")
        
        return tools
    
    def register_custom_tool(self, tool: BaseTool, category: Optional[str] = None):
        """
        Register a custom tool
        
        Args:
            tool: Tool instance to register
            category: Optional category for organization
        """
        self.mcp_registry.register_tool(type(tool))
        
        if category == "filesystem":
            self.filesystem_tools.append(tool)
        elif category == "web":
            self.web_tools.append(tool)
        elif category == "analysis":
            self.analysis_tools.append(tool)
        else:
            self.custom_tools[tool.name] = tool
        
        logger.info(f"Registered custom tool: {tool.name} (category: {category})")
    
    def set_minion_permissions(self, minion_id: str, tool_names: List[str]):
        """
        Set tool permissions for a Minion
        
        Args:
            minion_id: ID of the Minion
            tool_names: List of tool names to grant access to
        """
        # Revoke all current permissions
        current_permissions = self.permission_manager.permissions.get(minion_id, [])
        for tool_name in current_permissions:
            self.permission_manager.revoke_permission(minion_id, tool_name)
        
        # Grant new permissions
        for tool_name in tool_names:
            self.permission_manager.grant_permission(minion_id, tool_name)
        
        logger.info(f"Updated permissions for {minion_id}: {tool_names}")
    
    def get_tool_presets(self) -> Dict[str, List[str]]:
        """
        Get predefined tool sets for different Minion roles
        
        Returns:
            Dictionary mapping role names to tool lists
        """
        return {
            "taskmaster": [
                "send_message",
                "subscribe_channel",
                "consider_autonomous_communication",
                "read_file",
                "write_file",
                "list_directory",
                "computer_screenshot",
                "web_navigate",
                "web_extract_text"
            ],
            "scout": [
                "send_message",
                "subscribe_channel",
                "read_file",
                "list_directory",
                "diary_tool",
                "web_navigate",
                "web_search",
                "web_extract_text",
                "web_screenshot"
            ],
            "analyst": [
                "send_message",
                "subscribe_channel",
                "read_file",
                "write_file",
                "diary_tool",
                "computer_screenshot",
                "web_navigate",
                "web_extract_text",
                "web_execute_script"
            ],
            "scribe": [
                "send_message",
                "subscribe_channel",
                "read_file",
                "write_file",
                "list_directory",
                "diary_tool",
                "computer_type",
                "computer_key"
            ],
            "researcher": [
                "send_message",
                "subscribe_channel",
                "consider_autonomous_communication",
                "read_file",
                "diary_tool",
                "web_navigate",
                "web_search",
                "web_extract_text",
                "web_screenshot",
                "web_execute_script"
            ],
            "automator": [
                "send_message",
                "subscribe_channel",
                "computer_screenshot",
                "computer_click",
                "computer_type",
                "computer_key",
                "computer_scroll",
                "computer_wait",
                "web_navigate",
                "web_click",
                "web_fill",
                "web_wait_for_element"
            ]
        }
    
    def apply_role_preset(self, minion: Minion, role: str):
        """
        Apply a predefined tool set based on role
        
        Args:
            minion: The Minion to configure
            role: Role name
        """
        presets = self.get_tool_presets()
        
        if role not in presets:
            logger.warning(f"Unknown role: {role}")
            return
        
        tool_names = presets[role]
        self.set_minion_permissions(minion.minion_id, tool_names)
        
        # Update persona allowed tools
        minion.persona.allowed_tools = tool_names
        
        logger.info(f"Applied {role} preset to {minion.minion_id}")


# Singleton instance
_tool_manager: Optional[ToolIntegrationManager] = None


def get_tool_manager(
    comm_system: Optional[InterMinionCommunicationSystem] = None,
    safeguards: Optional[CommunicationSafeguards] = None,
    config: Optional[Dict[str, Any]] = None
) -> ToolIntegrationManager:
    """
    Get or create the singleton tool manager
    
    Args:
        comm_system: Communication system
        safeguards: Communication safeguards  
        config: Tool configuration
        
    Returns:
        ToolIntegrationManager instance
    """
    global _tool_manager
    
    if _tool_manager is None:
        _tool_manager = ToolIntegrationManager(comm_system, safeguards, config)
    
    return _tool_manager
