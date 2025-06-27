#!/usr/bin/env python3
"""
Direct test of minion response capability.
Tests if minions use real Gemini or fallback responses.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_legion_backend.core.dependencies_v2 import initialize_services_v2
from gemini_legion_backend.core.infrastructure.adk.events import get_event_bus

async def test_direct_minion_response():
    """Test minion responses directly through the service"""
    
    # Initialize services
    print("Initializing services...")
    container = await initialize_services_v2()
    minion_service = container.minion_service
    channel_service = container.channel_service
    event_bus = get_event_bus()
    
    print(f"\nActive minions: {len(minion_service.minions)}")
    for minion_id, minion in minion_service.minions.items():
        print(f"  - {minion_id}: {minion.persona.name}")
    
    # Check if we have any agents
    if minion_service.agents:
        print(f"\nActive agents: {len(minion_service.agents)}")
        
        # Get first agent
        first_agent_id = list(minion_service.agents.keys())[0]
        agent = minion_service.agents[first_agent_id]
        print(f"\nTesting agent: {first_agent_id}")
        
        # Try to get agent to respond
        print("\nAttempting direct agent interaction...")
        
        # Check if agent has communication tools
        if hasattr(agent, 'tools') and agent.tools:
            print(f"Agent has {len(agent.tools)} tools available")
        
        # Try using the agent's think method
        try:
            print("\nCalling agent.think() with test prompt...")
            response = await agent.think("Tell me a joke about AI!")
            print(f"Agent response: {response}")
            
            # Check if it's a fallback response
            if "ADK integration needs work" in str(response):
                print("\n❌ FALLBACK RESPONSE - Minions not using real Gemini!")
            else:
                print("\n✅ REAL GEMINI RESPONSE - Minions are thinking!")
                
        except Exception as e:
            print(f"Error calling think: {e}")
            print(f"Error type: {type(e)}")
    
    else:
        print("\n⚠️  No active agents found!")
    
    # Shutdown
    await container.shutdown()

if __name__ == "__main__":
    print("=== Direct Minion Response Test ===\n")
    asyncio.run(test_direct_minion_response())
    print("\n=== Test Complete ===")
