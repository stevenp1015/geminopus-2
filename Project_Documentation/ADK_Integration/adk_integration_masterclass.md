# ADK Integration Masterclass for Gemini Legion

## 1. Introduction

Welcome to the ADK Integration Masterclass for the Gemini Legion project! The Agent Development Kit (ADK) serves as a foundational layer in our infrastructure, as outlined in the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`. Its purpose is to provide a robust framework for defining, running, and managing our Minion agents, enabling complex interactions, tool usage, and structured task orchestration.

This document will guide you on how to effectively integrate Gemini Legion's unique components, such as the personality-driven Minions, Emotional Engine, and multi-layered Memory System, with ADK's idiomatic patterns. The goal is to ensure our Minions are not just functional but are true "Besties" – capable, emotionally aware, and contextually intelligent.

**Key ADK Concepts Used in Gemini Legion:**

*   **`LlmAgent`**: The base for our `MinionAgent`, providing core LLM interaction capabilities.
*   **`SequentialWorkflowAgent`**: Used for orchestrating complex tasks, like the `TaskMasterAgent`.
*   **Tools (`BaseTool`, `FunctionTool`, `MCPToolset`)**: Extending Minion capabilities.
*   **Session & State (`Session`, `Session.state`, `SessionService`)**: Managing conversation context, Minion working memory, and emotional nuances.
*   **Events (`Event`, `EventActions`)**: Understanding ADK's internal event flow for debugging and advanced control.
*   **Callbacks**: Hooks for integrating custom logic (like emotional state updates) into the ADK lifecycle.
*   **Runner**: The engine that executes agent invocations.

## 2. Core ADK Concepts for This Project

To effectively develop for Gemini Legion, a solid understanding of these ADK concepts is essential:

### a. Agents (`LlmAgent`, `SequentialWorkflowAgent`)

*   **`LlmAgent`**: This is the cornerstone for our `MinionAgent`.
    *   **Definition**: An `LlmAgent` uses a Large LanguageModel for reasoning, instruction-following, and tool usage.
    *   **Key Parameters**:
        *   `name`: Unique agent identifier (e.g., Minion's ID).
        *   `model`: The specific Gemini model to use (e.g., "gemini-2.0-flash").
        *   `instruction`: The system prompt that defines the agent's persona, goals, and how it should behave. This is critical for personality-driven Minions.
        *   `tools`: A list of `BaseTool` instances the agent can use.
    *   **Further Reading**: `Relevant_ADK_docs_1/docs/agents/llm-agents.md`

*   **`SequentialWorkflowAgent`**: Used for agents like `TaskMasterAgent` that orchestrate a series of sub-agents or tasks in a defined order.
    *   **Definition**: Executes a list of sub-agents sequentially, passing context between them.
    *   **Further Reading**: `Relevant_ADK_docs_1/docs/agents/workflow-agents/sequential-agents.md`

### b. Session, State, and Events

*   **`Session`**: Represents a single, ongoing conversation or interaction flow. It holds the history of events and the current state.
    *   **Further Reading**: `Relevant_ADK_docs_2/docs/sessions/session.md`
*   **`Session.state`**: A dictionary-like object within a `Session` for storing serializable data relevant to that specific session. This is crucial for:
    *   Tracking Minion's working memory or emotional nuances for the current interaction.
    *   Passing data between agent turns or tool calls.
    *   **Important**: Use prefixes like `user:` for user-specific persistent state or `app:` for app-level state if using a persistent `SessionService`.
    *   **Further Reading**: `Relevant_ADK_docs_2/docs/sessions/state.md`
*   **`Event`**: The fundamental unit of communication and data flow within an ADK `Runner` invocation. Represents user messages, agent responses, tool calls, tool results, and state changes.
    *   `Event.actions.state_delta`: How state changes are officially recorded.
    *   **Further Reading**: `Relevant_ADK_docs_2/docs/events/index.md`

### c. Tools

*   **`BaseTool`**: The base class for all tools.
*   **`FunctionTool`**: Wraps a Python function to be used as a tool.
*   **`MCPToolset`**: Allows ADK agents to consume tools from Model Context Protocol (MCP) servers. This is key for our `MCPToolbeltFramework`.
    *   **Further Reading**: `Relevant_ADK_docs_2/docs/tools/mcp-tools.md`, `Relevant_ADK_docs_2/docs/tools/index.md`

### d. Callbacks

*   Functions you can register to be called at specific points in the agent's execution lifecycle (e.g., `before_model_callback`, `after_tool_callback`).
*   Useful for logging, modifying requests/responses, or integrating custom logic like emotional state updates.
*   **Further Reading**: `Relevant_ADK_docs_1/docs/callbacks/index.md`, `Relevant_ADK_docs_1/docs/callbacks/types-of-callbacks.md`

## 3. Integrating Custom Components with ADK: The `MinionAgent`

The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` envisions `MinionAgent` as an extension of `LlmAgent`. Here's how to approach this integration:

### a. Extending `LlmAgent`

Our `MinionAgent` should inherit from `google.adk.agents.LlmAgent`.

```python
from google.adk.agents import LlmAgent
from typing import Optional, List, Dict, Any

# Assuming these domain objects are defined elsewhere as per IDEAL_ARCHITECTURE
from gemini_legion_backend.core.domain import MinionPersona, EmotionalState, Experience
from gemini_legion_backend.core.infrastructure.adk.emotional_engine_v2 import EmotionalEngineV2
from gemini_legion_backend.core.infrastructure.adk.memory_system_v2 import MemorySystemV2
from gemini_legion_backend.core.infrastructure.adk.tools.tool_integration import ToolIntegrationManager # Example

class ADKMinionAgent(LlmAgent):
    def __init__(
        self,
        minion_id: str,
        persona: MinionPersona,
        emotional_engine: EmotionalEngineV2, # V2 from codebase
        memory_system: MemorySystemV2,       # V2 from codebase
        tool_manager: ToolIntegrationManager,
        **kwargs
    ):
        # 1. Build the System Instruction
        # This is crucial for personality, emotional awareness, and tool use guidance.
        system_instruction = f"""You are {persona.name}, a unique AI minion.
Personality: {persona.base_personality}
Quirks: {', '.join(persona.quirks)}
Catchphrases: {', '.join(persona.catchphrases)}

Current Emotional State:
Mood: {emotional_engine.get_current_state().mood.to_prompt_modifier() if emotional_engine.get_current_state() else 'neutral'}
Energy: {emotional_engine.get_current_state().energy_level if emotional_engine.get_current_state() else 0.5}
Stress: {emotional_engine.get_current_state().stress_level if emotional_engine.get_current_state() else 0.3}

Remember to leverage your memory and emotional understanding in your responses.
You are part of a team. Be yourself and interact naturally.
Utilize your tools when appropriate to accomplish tasks or communicate.
"""
        
        # 2. Get Tools from ToolIntegrationManager
        # The tool_manager should provide BaseTool instances.
        # This aligns with the `get_tools_for_minion` logic.
        minion_tools = tool_manager.get_tools_for_minion(persona) # Assuming persona has ID

        super().__init__(
            name=minion_id,
            model=persona.model_config.get("model_name", "gemini-2.0-flash"), # Get model from persona
            instruction=system_instruction,
            tools=minion_tools,
            **kwargs
        )
        
        self.minion_id = minion_id
        self.persona = persona
        self.emotional_engine = emotional_engine
        self.memory_system = memory_system
        self.tool_manager = tool_manager

        # Consider using ADK Callbacks for some integrations if they fit the lifecycle
        # self.before_model_callbacks.append(self._inject_emotional_context_callback)
        # self.after_model_callbacks.append(self._process_emotional_impact_callback)

    async def _inject_emotional_context_callback(self, callback_context):
        # Modifies llm_request in callback_context based on current emotional state
        # Example: Add a prefix to the prompt like "[Feeling curious] User asked:"
        # current_emotion = self.emotional_engine.get_current_state()
        # prompt_prefix = f"[{current_emotion.mood.to_short_string()}] "
        # if callback_context.llm_request.contents:
        #    # This is a simplified way; actual modification might be more complex
        #    # and require careful handling of different content types (text, tool_calls)
        #    pass # Modify appropriately
        return None # Allow ADK to proceed

    async def _process_emotional_impact_callback(self, callback_context):
        # Analyzes callback_context.llm_response and updates emotional state
        # This would involve calling self.emotional_engine.process_interaction(...)
        # and then self.emotional_engine.apply_update(...)
        # The changes to emotional state should ideally be persisted via session state
        # or specific events if not directly part of ADK's session.
        # For example, if emotional state is part of ADK session state:
        # callback_context.state['emotional_state_snapshot'] = new_emotional_state_snapshot
        return None # Allow ADK to proceed

    # Enhanced predict or run_async to integrate custom systems
    # The IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md suggests enhancing predict.
    # predict() is simpler for request-response but run_async() offers more control.
    
    async def predict(
        self,
        message: str,
        session: Optional[Dict[str, Any]] = None, # ADK's session is a dict for state
        **kwargs
    ) -> str:
        """
        ADK-standard predict method with Gemini Legion enhancements.
        """
        current_emotional_state = self.emotional_engine.get_current_state()
        
        # 1. Pre-processing: Enhance message with emotional context/memory
        # This could involve modifying the 'message' or adding to 'session' state
        # that the LlmAgent's instruction can then reference.
        # For example, retrieve relevant memories:
        relevant_memories = await self.memory_system.recall_relevant(message, limit=3)
        memory_context = "\n".join([f"- {mem.content}" for mem in relevant_memories])
        
        # Update instruction dynamically or add to message (careful with prompt length)
        # A better way is to ensure system_instruction is rich and can use state variables.
        # For example, if session state holds 'current_mood_prompt':
        # session_state_updates = {"current_mood_prompt": current_emotional_state.mood.to_prompt_modifier()}
        # if session:
        #    session.update(session_state_updates)
        # else:
        #    session = session_state_updates
        
        # For simplicity, let's assume the main system_instruction is already set up
        # to consider emotional state (if it were read from session state).

        # 2. Call ADK's LlmAgent predict
        # The ADK LlmAgent will handle tool calls based on its instruction and available tools.
        response_text = await super().predict(message=message, session=session, **kwargs)
        
        # 3. Post-processing: Update emotional and memory systems
        # This is a simplified representation. In a real scenario, you'd create
        # an InteractionEvent and process it.
        # interaction_event = InteractionEvent(message, response_text)
        # emotional_update = await self.emotional_engine.process_interaction(
        # current_emotional_state, interaction_event, {"memory_context": memory_context}
        # )
        # await self.emotional_engine.apply_emotional_update(emotional_update, "predict_interaction")
        
        # Store experience
        # experience = Experience(experience_id=str(uuid.uuid4()), ...)
        # await self.memory_system.store_experience(experience)
        
        # If emotional state needs to be persisted via ADK session state:
        # if session:
        #    session['emotional_state_snapshot'] = self.emotional_engine.get_current_state().to_snapshot()
            
        return response_text

```

**Key Integration Points for `MinionAgent`**:

1.  **Constructor (`__init__`)**:
    *   Dynamically build the `instruction` string using `MinionPersona` and the current snapshot from `EmotionalEngineV2`.
    *   Populate the `tools` list using `ToolIntegrationManager.get_tools_for_minion(minion)`.
2.  **State Bridging**:
    *   The `EmotionalEngineV2` and `MemorySystemV2` are custom. To make them influence ADK's LLM calls, their state needs to be injected into the prompt or ADK `Session.state`.
    *   **Option 1 (Dynamic Instruction)**: Modify the `instruction` string before each call (complex, might hit token limits).
    *   **Option 2 (ADK Session State)**: Store relevant emotional/memory cues in `Session.state` (e.g., `session['current_mood_summary'] = "feeling curious"`). The Minion's main `instruction` should be crafted to *read* these state variables (e.g., "Current Mood: {current_mood_summary}").
    *   **Option 3 (Callbacks)**: Use `before_model_callback` to inject context into the `LlmRequest` and `after_model_callback` to process the `LlmResponse` for emotional impact.
3.  **Tool Management**: Rely on `ToolIntegrationManager` to provide the `tools` list. The underlying `MCPToADKAdapter` handles MCP tool execution.

### b. `predict()` vs. `run_async()`

*   **`predict(message, session, **kwargs)`**: Simpler, higher-level method. Good for request-response interactions. ADK handles history and state implicitly if `session` is provided. Tool calls are handled, and their results are fed back to the LLM, returning a final text response. This seems to align with the `IDEAL_ARCHITECTURE`'s description.
*   **`run_async(context)`**: Lower-level, gives more control over the event stream. You'd use this if you need to react to intermediate `Event` objects (e.g., tool call requests before they are executed). For Gemini Legion's current design, `predict` is likely sufficient for the `MinionAgent`'s core interaction loop, with custom logic wrapped in tools or callbacks.

The `minion_agent_v2.py` seems to be moving towards a custom chat loop rather than directly using ADK's `predict` or `run_async` in an idiomatic way, primarily due to issues with `google.genai` client. The masterclass should steer towards the idiomatic ADK `LlmAgent` usage.

## 4. Using Key ADK Features

### a. Multi-Agent Systems (MAS)

*   **Concept**: ADK allows agents to be composed, with parent agents orchestrating children. `SequentialAgent`, `ParallelAgent`, `LoopAgent` are workflow agents. `LlmAgent` can also delegate to sub-agents.
*   **Gemini Legion Application**:
    *   `TaskMasterAgent` is a `SequentialWorkflowAgent`, orchestrating steps.
    *   Minions can be sub-agents of a "LegionCoordinator" or use `AgentTool` to call each other.
    *   Inter-Minion communication (as per `IDEAL_ARCHITECTURE`) might use ADK's `AgentTool` for direct calls, or the custom `GeminiEventBus` can trigger Minions, which then use their ADK capabilities.
*   **Key ADK Docs**: `Relevant_ADK_docs_1/docs/agents/multi-agents.md`

### b. MCP Tool Integration

*   **Concept**: `MCPToolset` connects to an MCP server, discovers its tools, and makes them available as ADK `BaseTool` instances.
*   **Gemini Legion Application**:
    *   The `MCPToolbeltFramework` and `MCPToADKAdapter` from the codebase (`mcp_adapter.py`) are responsible for this.
    *   `ToolIntegrationManager` provides these adapted tools to Minions.
    *   `MinionAgent` receives these tools in its `tools` list. When the LLM decides to use an MCP-originated tool, ADK calls its `execute` method, which the `AdaptedMCPTool` routes to the actual MCP server.
*   **Key ADK Docs**: `Relevant_ADK_docs_2/docs/tools/mcp-tools.md`

### c. Event System (ADK's Internal Events)

*   **Concept**: ADK's `Runner` processes `Event` objects representing stages of an invocation (user input, agent message, tool call, tool response, state change).
*   **Gemini Legion Application**:
    *   While Gemini Legion has its own `GeminiEventBus` for system-wide events, understanding ADK's internal event flow is crucial for debugging and for advanced use of callbacks.
    *   When a `MinionAgent` (as an `LlmAgent`) uses a tool, an `Event` with a `FunctionCall` is generated, then an `Event` with a `FunctionResponse`.
    *   `Event.actions.state_delta` is how changes to `Session.state` are officially recorded.
*   **Key ADK Docs**: `Relevant_ADK_docs_2/docs/events/index.md`

### d. Session Management & State

*   **Concept**: `SessionService` manages `Session` objects. `Session.state` stores data for the current session.
*   **Gemini Legion Application**:
    *   Crucial for maintaining context for each Minion's interaction with a user or other Minions.
    *   The `predict` method's `session` argument is the ADK `Session.state` dictionary.
    *   Persistent `SessionService` (like `DatabaseSessionService` or `VertexAiSessionService`) should be used for production to store Minion's working memory or short-term emotional context related to a specific interaction.
    *   The custom `MemorySystemV2` and `EmotionalEngineV2` might persist their own comprehensive state, but snapshots or cues relevant to the current ADK session should be placed in `Session.state` to influence ADK agent behavior.
*   **Key ADK Docs**: `Relevant_ADK_docs_2/docs/sessions/session.md`, `Relevant_ADK_docs_2/docs/sessions/state.md`

### e. Callbacks & Streaming

*   **Callbacks**:
    *   Allow custom logic at various points (e.g., before/after LLM call, before/after tool execution).
    *   **Gemini Legion Application**: Can be used to:
        *   Update emotional state based on LLM request/response or tool success/failure.
        *   Inject memory system summaries into prompts.
        *   Log detailed interaction data for analysis.
    *   **Key ADK Docs**: `Relevant_ADK_docs_1/docs/callbacks/*`
*   **Streaming**:
    *   ADK supports streaming for real-time responses. `RunConfig` controls this.
    *   **Gemini Legion Application**: Essential for the real-time GUI. Minions should stream responses back to the API Gateway.
    *   **Key ADK Docs**: `Relevant_ADK_docs_1/docs/streaming/index.md`, `Relevant_ADK_docs_1/docs/runtime/runconfig.md` (for `streaming_mode`). The `custom-streaming-ws.md` provides an example of a FastAPI WebSocket server with ADK streaming.

## 5. Code Examples & Best Practices

### Example: MinionAgent structure (Conceptual)

```python
# In gemini_legion_backend.core.infrastructure.adk.agents.minion_agent_def.py

from google.adk.agents import LlmAgent
from google.adk.sessions import Session # Dict-like state
from typing import Optional, List, Any, Dict

# Assuming other necessary imports for Persona, EmotionalEngine, MemorySystem, ToolManager

class IdealADKMinionAgent(LlmAgent):
    def __init__(self, minion_id, persona, emotional_engine, memory_system, tool_manager, **kwargs):
        system_instruction = self._build_instruction(persona, emotional_engine, memory_system)
        minion_tools = tool_manager.get_tools_for_minion(minion_id, persona.allowed_tools)
        
        super().__init__(
            name=minion_id,
            model=persona.model_config.get("model_name", "gemini-2.0-flash"),
            instruction=system_instruction,
            tools=minion_tools,
            **kwargs
        )
        self.minion_id = minion_id
        self.persona = persona
        self.emotional_engine = emotional_engine
        self.memory_system = memory_system
        # ... other initializations ...

    def _build_instruction(self, persona, emotional_engine, memory_system) -> str:
        # Dynamically constructs the system prompt using persona,
        # current emotional state (from engine), and relevant memory cues.
        # Example:
        # emotional_summary = emotional_engine.get_current_state_summary()
        # memory_highlights = memory_system.get_working_memory_summary()
        # return f"You are {persona.name}... Current mood: {emotional_summary}. Recent thoughts: {memory_highlights}..."
        return f"You are {persona.name}, a helpful and {persona.base_personality} AI minion." # Placeholder

    async def predict(
        self,
        message: str,
        session: Optional[Session] = None, # ADK Session state
        **kwargs
    ) -> str:
        # 1. Pre-processing:
        # Update ADK session state with current emotional/memory context if instruction refers to it
        if session is not None:
            emotional_summary = self.emotional_engine.get_current_state_summary(self.minion_id)
            session['current_emotion_summary'] = emotional_summary 
            # (Ensuring instruction can use {current_emotion_summary})
        
        # 2. Core ADK processing (LLM call, tool use)
        response_text = await super().predict(message=message, session=session, **kwargs)
        
        # 3. Post-processing:
        # Update emotional_engine and memory_system based on the interaction.
        # This logic would be here or in an `after_model_callback`.
        # self.emotional_engine.process_interaction(message, response_text)
        # self.memory_system.store_experience(message, response_text)
        
        return response_text

    # Example of a callback for emotional processing
    async def after_model_llm_response_callback(self, callback_context):
        # llm_request = callback_context.llm_request
        # llm_response = callback_context.llm_response
        # current_state = callback_context.state # ADK session state
        
        # # Process emotional impact of llm_response.text
        # self.emotional_engine.process_llm_turn(...)
        # # Update ADK session state if needed
        # current_state['last_emotional_valence'] = self.emotional_engine.get_valence()
        pass
```

### Best Practices

1.  **Idiomatic ADK Usage**: Embrace ADK's patterns (LlmAgent, tools, session state, predict/run_async) rather than fighting them with custom loops if ADK provides a native way. The current `minion_agent_v2.py`'s fallback mode should be transitioned to full ADK usage.
2.  **Clear Instructions**: Craft detailed system instructions for Minions that define their persona, how to use tools, and how to incorporate emotional and memory context.
3.  **State Management**:
    *   Use ADK `Session.state` for data relevant to the *current ADK invocation/turn* or short-term conversational context that the LLM needs direct access to via prompt templating.
    *   The comprehensive state of `EmotionalEngineV2` and `MemorySystemV2` should be managed by those systems, but relevant summaries or cues should be pushed into ADK `Session.state` to influence the LLM.
4.  **Tool Design**: Ensure tools provided by `ToolIntegrationManager` are true `BaseTool` instances with clear schemas. The `MCPToADKAdapter` handles this for MCP tools.
5.  **Modularity**: Keep Minion-specific logic (emotions, complex memory) encapsulated within their respective engines, and interface with ADK `LlmAgent` through well-defined points (instruction, session state, callbacks).
6.  **Error Handling**: Implement robust error handling within tools and callbacks.
7.  **Asynchronous Operations**: Use `async` and `await` correctly, as ADK is an asynchronous framework.

## 6. Troubleshooting Common Issues

*   **Tool Not Being Called**:
    *   Check agent's `instruction`: Does it clearly state when to use the tool?
    *   Is the tool correctly added to the `tools` list during `LlmAgent` initialization?
    *   Is the tool's schema (name, description, parameters) clear and accurate? The LLM relies on this.
    *   Is `use_fallback` in `minion_agent_v2.py` preventing normal ADK tool use?
*   **Incorrect Tool Arguments**:
    *   Review the tool's schema and the agent's instruction on how to derive arguments.
    *   Debug by inspecting the `FunctionCall` object in the event stream or callbacks.
*   **State Not Persisting**:
    *   Ensure you are using a persistent `SessionService` (e.g., `DatabaseSessionService`) for production.
    *   Verify state changes are correctly included in `Event.actions.state_delta` (ADK handles this if you modify `callback_context.state` or use `output_key`).
*   **ADK Integration Issues with `google.genai`**:
    *   The `minion_agent_v2.py` indicates issues with `google.genai` client changes. The masterclass should assume these are resolved or guide on using the correct `google.generativeai` (the typical library for Gemini). If `google.adk.genai` is a specific version bundled/required by ADK, ensure compatibility.
    *   Refer to the latest ADK documentation for the correct way to initialize and use Gemini models.

This masterclass provides a roadmap for aligning Gemini Legion's unique architecture with ADK's powerful capabilities. By focusing on idiomatic ADK patterns, clear integration points for custom systems, and robust tool management, we can build truly intelligent and engaging Minion agents.The new file `project_documentation/adk_integration/adk_integration_masterclass.md` has been created with the detailed content.
This document covers:
1.  Introduction to ADK's role in Gemini Legion.
2.  Core ADK concepts relevant to the project (Agents, Session/State/Events, Tools, Callbacks, Runner).
3.  Guidance on integrating custom components like `MinionAgent`, `EmotionalEngineV2`, and `MemorySystemV2` with ADK, focusing on extending `LlmAgent` and managing state.
4.  How to use key ADK features like Multi-Agent Systems, MCP Tool Integration, ADK's internal Event System, Session Management, and Callbacks/Streaming in the context of Gemini Legion.
5.  Conceptual code examples and best practices for ADK integration.
6.  Common troubleshooting tips.

The content is synthesized from the provided ADK documentation, the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`, and insights from examining the existing codebase files. It aims to bridge the gap between the project's ambitious design and the practical application of ADK features.
