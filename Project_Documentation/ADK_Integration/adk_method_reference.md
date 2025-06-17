# ADK Method Reference Sheet for Gemini Legion

This document provides a quick reference to key ADK classes, methods, and design patterns relevant to the Gemini Legion project.

## I. Agents

### 1. `google.adk.agents.BaseAgent`
*   **Purpose:** The fundamental base class for all agents in ADK. Custom agents with unique, non-LLM-driven logic inherit from this.
*   **Syntax/Usage Example (Conceptual Minion Task):**
    ```python
    from google.adk.agents import BaseAgent, InvocationContext, Event
    from typing import AsyncGenerator

    class CustomMinionTaskAgent(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            # Logic for a specific, non-LLM task for a Minion
            task_data = ctx.session.state.get("current_task_data", {})
            result = f"Custom task completed for {self.name} with data: {task_data}"
            yield Event(author=self.name, content={"parts": [{"text": result}]})
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/agents/custom-agents.md`

### 2. `google.adk.agents.LlmAgent` (aliased as `Agent`)
*   **Purpose:** Core agent type for interactions driven by Large Language Models. This is the base for `MinionAgent`.
*   **Key Parameters for Initialization:**
    *   `name: str`: Unique agent name (e.g., Minion ID).
    *   `model: str`: LLM model identifier (e.g., "gemini-2.0-flash").
    *   `instruction: str`: System prompt defining persona, behavior, and tool usage. Critical for Minion personality.
    *   `tools: List[BaseTool]`: List of tools the agent can use.
    *   `output_key: Optional[str]`: If set, agent's final text response is saved to `session.state[output_key]`.
    *   `generate_content_config`: For LLM generation parameters (temperature, etc.).
*   **Syntax/Usage Example (MinionAgent Base):**
    ```python
    from google.adk.agents import LlmAgent
    # from gemini_legion_backend.core.domain import MinionPersona
    # from gemini_legion_backend.core.infrastructure.adk.emotional_engine_v2 import EmotionalEngineV2
    # from gemini_legion_backend.core.infrastructure.adk.memory_system_v2 import MemorySystemV2
    # from gemini_legion_backend.core.infrastructure.adk.tools.tool_integration import ToolIntegrationManager

    # Simplified Minion Agent structure
    class MinionAgentExample(LlmAgent):
        def __init__(self, minion_id, persona, emotional_engine, memory_system, tool_manager, **kwargs):
            system_instruction = f"You are {persona.name}, a {persona.base_personality} AI." # Simplified
            minion_tools = tool_manager.get_tools_for_minion(minion_id, persona.allowed_tools)
            
            super().__init__(
                name=minion_id,
                model=persona.model_config.get("model_name"),
                instruction=system_instruction,
                tools=minion_tools,
                output_key=f"{minion_id}_last_response", # Example output_key
                **kwargs
            )
            # Store other Gemini Legion specific engines here
            self.emotional_engine = emotional_engine
            self.memory_system = memory_system
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/agents/llm-agents.md`
    *   `Relevant_ADK_docs_2/docs/agents/llm-agents.md`

### 3. `LlmAgent.predict(message: str, session: Optional[SessionStateDict] = None, **kwargs) -> str`
*   **Purpose:** High-level method to get a response from an `LlmAgent`. Handles history and tool use implicitly.
*   **Syntax/Usage Example (Interacting with a Minion):**
    ```python
    # Assuming minion_agent is an instance of MinionAgentExample
    # session_state = {} # ADK session state dictionary
    # response = await minion_agent.predict(
    #     message="Hello Minion, how are you?", 
    #     session=session_state
    # )
    # print(f"{minion_agent.name} responded: {response}")
    # print(f"Updated session state: {session_state}")
    ```
*   **Source Reference(s):** (Implicitly covered in LlmAgent docs, behavior described in `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` for Gemini Legion)

### 4. Workflow Agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`)
*   **Purpose:** Orchestrate the execution flow of sub-agents in predefined patterns.
    *   `SequentialAgent`: Executes sub-agents one after another.
    *   `ParallelAgent`: Executes sub-agents concurrently.
    *   `LoopAgent`: Executes sub-agents in a loop until a condition is met or `max_iterations` reached.
*   **Syntax/Usage Example (TaskMasterAgent as Sequential):**
    ```python
    from google.adk.agents import SequentialAgent, LlmAgent

    # Define sub-agents for a task workflow
    # step1_agent = LlmAgent(name="TaskDecomposition", model="gemini-2.0-flash", instruction="Decompose the task: {task_description}")
    # step2_agent = LlmAgent(name="MinionAssignment", model="gemini-2.0-flash", instruction="Assign subtasks to available Minions.")
    
    # task_master_agent = SequentialAgent(
    #     name="TaskMasterPrime",
    #     sub_agents=[step1_agent, step2_agent]
    # )
    # Initial task data might be in session.state['task_description']
    # Result of step1_agent can be put into session.state via output_key for step2_agent
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/agents/workflow-agents/index.md`
    *   `Relevant_ADK_docs_1/docs/agents/workflow-agents/sequential-agents.md`
    *   (Similar docs for Parallel and Loop agents are expected)

### 5. Multi-Agent Patterns
*   **Coordinator/Dispatcher:** A central `LlmAgent` routes tasks to specialized sub-agents using LLM-driven delegation (`transfer_to_agent`) or `AgentTool`.
*   **Hierarchical Task Decomposition:** Higher-level agents break down tasks and delegate to lower-level agents.
*   **Usage Example (Conceptual Legion Coordinator):**
    ```python
    # research_minion = MinionAgentExample(...)
    # comms_minion = MinionAgentExample(...)
    
    # legion_coordinator = LlmAgent(
    #     name="LegionCommanderAI",
    #     model="gemini-2.0-flash",
    #     instruction="""Understand the user's request.
    #     If it's research, delegate to research_minion.
    #     If it's communication, delegate to comms_minion.
    #     Use transfer_to_agent(agent_name='...')""",
    #     sub_agents=[research_minion, comms_minion] # For transfer_to_agent
    # )
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/agents/multi-agents.md`

## II. Tools

### 1. `google.adk.tools.BaseTool`
*   **Purpose:** Abstract base class for all tools. Custom tools should inherit from this if `FunctionTool` is not sufficient.
*   **Key Methods to Implement:**
    *   `name: str`
    *   `description: str`
    *   `get_schema() -> Dict[str, Any]`: Returns JSON schema for tool parameters.
    *   `async execute(**kwargs) -> Dict[str, Any]`: Executes the tool logic.
*   **Source Reference(s):** (General Tool docs)
    *   `Relevant_ADK_docs_2/docs/tools/index.md`

### 2. `google.adk.tools.FunctionTool`
*   **Purpose:** Wraps a Python function or method to be used as an ADK tool. ADK automatically creates schemas from type hints and docstrings.
*   **Syntax/Usage Example (Simple Minion Utility):**
    ```python
    from google.adk.tools import FunctionTool

    # def get_minion_status(minion_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    #     """Gets the current operational status of a Minion."""
    #     # Access shared state or a Minion registry via tool_context if needed
    #     # status = ... 
    #     # return {"minion_id": minion_id, "status": status, "timestamp": datetime.now().isoformat()}
    
    # # status_tool = FunctionTool(func=get_minion_status)
    # # This tool would then be added to an LlmAgent's tools list.
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/tools/function-tools.md`

### 3. `google.adk.tools.AgentTool`
*   **Purpose:** Allows one agent to be used as a tool by another agent.
*   **Syntax/Usage Example (Minion using another Minion's skill):**
    ```python
    # from google.adk.tools import AgentTool
    # specialized_minion = MinionAgentExample(minion_id="MinionSpecialist", ...) 
    # general_minion = MinionAgentExample(
    #     minion_id="MinionGeneralist",
    #     tools=[AgentTool(agent=specialized_minion, skip_summarization=False)],
    #     instruction="If you need specialized data, call MinionSpecialist."
    # )
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/tools/function-tools.md#3-agent-as-a-tool`
    *   `Relevant_ADK_docs_1/docs/agents/multi-agents.md` (Interaction Mechanisms)

### 4. `google.adk.tools.mcp_tool.MCPToolset`
*   **Purpose:** Connects to an MCP server, discovers its tools, and adapts them into ADK `BaseTool` instances for use by an `LlmAgent`.
*   **Key Parameters for Initialization:**
    *   `connection_params: StdioServerParameters | SseServerParams`
    *   `tool_filter: Optional[List[str]]`
*   **Syntax/Usage Example (Connecting to Gemini Legion's MCP Toolbelt):**
    ```python
    # from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters
    # Assuming mcp_adapter.py provides a way to start the MCP server for Legion tools
    # mcp_toolbelt = MCPToolset(
    #     connection_params=StdioServerParameters(
    #         command='python', # Or appropriate command
    #         args=['path/to/gemini_legion_mcp_server_runner.py'] 
    #     )
    # )
    # minion_agent = MinionAgentExample(..., tools=[mcp_toolbelt, other_tool])
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/tools/mcp-tools.md`

### 5. `google.adk.tools.ToolContext`
*   **Purpose:** Passed to tool `execute` methods (if defined in signature). Provides access to session state, artifact/memory services, and allows influencing agent flow.
*   **Key Attributes/Methods:**
    *   `state: Dict[str, Any]`: Read/write access to session state.
    *   `actions: EventActions`: Set `skip_summarization`, `transfer_to_agent`, `escalate`.
    *   `save_artifact()`, `load_artifact()`, `list_artifacts()`
*   **Syntax/Usage Example (Tool modifying state):**
    ```python
    # from google.adk.tools import ToolContext
    
    # def record_interaction_tool(user_query: str, tool_context: ToolContext) -> Dict[str, Any]:
    #     """Records the user query in session state."""
    #     interactions = tool_context.state.get("session_interactions", [])
    #     interactions.append(user_query)
    #     tool_context.state["session_interactions"] = interactions # Change is captured in EventActions
    #     return {"status": "success", "recorded_interactions": len(interactions)}
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/tools/index.md#tool-context`

## III. Sessions and State

### 1. `google.adk.sessions.Session`
*   **Purpose:** Represents a single conversation thread. Contains `id`, `app_name`, `user_id`, `events` (history), and `state`.
*   **Usage:** Typically managed by a `SessionService`. Agents receive session state via `InvocationContext` or `predict` method's `session` argument.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/sessions/session.md`

### 2. `Session.state` (Dictionary-like)
*   **Purpose:** Stores serializable key-value data for the current session. Used for short-term memory, task tracking, etc.
*   **Usage Example (Accessed via context in a tool or callback):**
    ```python
    # def my_tool_or_callback(context: ToolContext): # Or CallbackContext
    #     if context.state.get("user_preference_set"):
    #         theme = context.state.get("user:theme", "default")
    #         # Apply theme
    #     context.state["last_action_timestamp"] = datetime.now().isoformat()
    ```
*   **State Prefixes:**
    *   No prefix: Session-specific.
    *   `user:`: User-specific across sessions.
    *   `app:`: App-specific across all users/sessions.
    *   `temp:`: Temporary for current turn, not persisted.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/sessions/state.md`

### 3. `google.adk.sessions.BaseSessionService`
*   **Purpose:** Abstract class for session management (CRUD operations for sessions).
*   **Key Methods:** `create_session`, `get_session`, `append_event`, `delete_session`.
*   **Implementations:** `InMemorySessionService`, `VertexAiSessionService`, `DatabaseSessionService`.
*   **Usage Example (Conceptual Setup in main application):**
    ```python
    # from google.adk.sessions import InMemorySessionService, DatabaseSessionService
    # from google.adk.runners import Runner
    
    # For local dev/testing
    # session_service = InMemorySessionService() 
    
    # For production with persistence
    # db_url = "sqlite:///./gemini_legion_sessions.db"
    # session_service = DatabaseSessionService(db_url=db_url)
    
    # runner = Runner(agent=my_minion_agent, app_name="gemini_legion", session_service=session_service)
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/sessions/session.md` (covers `SessionService`)

### 4. `SessionService.append_event(session: Session, event: Event)`
*   **Purpose:** The primary method to update a session. It appends the event to `session.events` and applies any `state_delta` from `event.actions` to `session.state`, persisting the changes.
*   **Usage:** Called by the `Runner` automatically. Direct use is rare but possible for custom event sources.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/sessions/state.md` (How State is Updated)
    *   `Relevant_ADK_docs_2/docs/events/index.md` (How Events Flow)

## IV. Events

### 1. `google.adk.events.Event`
*   **Purpose:** Fundamental unit of communication and history. Represents user messages, agent responses, tool calls/results, state changes.
*   **Key Attributes:**
    *   `author: str` ('user' or agent name)
    *   `content: Optional[google.genai.types.Content]` (text, function calls, function responses)
    *   `actions: Optional[EventActions]` (state_delta, artifact_delta, control signals)
    *   `partial: bool` (for streaming)
    *   `is_final_response() -> bool`: Helper to identify displayable final outputs.
*   **Usage Example (Iterating through Runner's output):**
    ```python
    # async for event in runner.run_async(user_id, session_id, new_message):
    #     if event.is_final_response() and event.content and event.content.parts:
    #         # Display event.content.parts[0].text to user
    #         pass
    #     if event.actions and event.actions.state_delta:
    #         # React to state changes if needed by UI
    #         pass
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/events/index.md`

### 2. `google.adk.events.EventActions`
*   **Purpose:** Carried by `Event` objects to signal side effects or control flow changes.
*   **Key Attributes:**
    *   `state_delta: Optional[Dict[str, Any]]`: Changes to be applied to `session.state`.
    *   `artifact_delta: Optional[Dict[str, Any]]`: Information about saved artifacts.
    *   `transfer_to_agent: Optional[str]`: Signals transfer to another agent.
    *   `escalate: bool`: Signals loop termination or escalation to parent.
    *   `skip_summarization: bool`: Instructs LLM to not summarize a tool's output.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/events/index.md` (Detecting Actions and Side Effects)

## V. Callbacks

### 1. Callback Registration
*   **Purpose:** Associate custom functions with an agent to run at specific lifecycle points.
*   **Usage Example (Registering a `before_model_callback`):**
    ```python
    # async def my_before_model_cb(callback_context: CallbackContext):
    #     # Logic to modify llm_request or log
    #     # callback_context.llm_request...
    #     # callback_context.state...
    #     return None # Allow LLM call to proceed
    
    # minion_agent.before_model_callbacks.append(my_before_model_cb)
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/callbacks/index.md`

### 2. Callback Types & Purpose
*   **`before_agent_callback(CallbackContext)`:** Before agent's `_run_async_impl`.
*   **`after_agent_callback(CallbackContext)`:** After agent's `_run_async_impl`.
*   **`before_model_callback(CallbackContext)`:** Before LLM call. Can return `LlmResponse` to skip LLM.
*   **`after_model_callback(CallbackContext)`:** After LLM call. Can modify `LlmResponse`.
*   **`before_tool_callback(ToolContext)`:** Before tool execution. Can return `dict` to skip tool.
*   **`after_tool_callback(ToolContext)`:** After tool execution. Can modify tool result `dict`.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/callbacks/types-of-callbacks.md`

### 3. `google.adk.agents.CallbackContext` / `google.adk.tools.ToolContext`
*   **Purpose:** Provide context to callback functions and tool `execute` methods.
*   **Key Attributes (common):** `state`, `actions`, `session`, `invocation_id`, `agent_name`.
    *   `CallbackContext`: `llm_request`, `llm_response`.
    *   `ToolContext`: `tool_name`, `tool_args`, `tool_response`, `function_call_id`.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/callbacks/index.md` (Context is Key)
    *   `Relevant_ADK_docs_2/docs/tools/index.md#tool-context`

## VI. Runtime & Streaming

### 1. `google.adk.runners.Runner`
*   **Purpose:** The engine that manages agent execution, event flow, and service interactions.
*   **Key Methods:**
    *   `run_async(user_id, session_id, new_message, run_config=None, **kwargs)`: Primary method for asynchronous agent execution, yielding `Event` objects.
    *   `run(...)`: Synchronous wrapper for `run_async`.
*   **Initialization:**
    ```python
    # runner = Runner(
    #     agent=my_minion_agent,
    #     app_name="gemini_legion",
    #     session_service=my_session_service,
    #     artifact_service=my_artifact_service, # Optional
    #     memory_service=my_memory_service     # Optional
    # )
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/runtime/index.md`

### 2. `google.adk.agents.RunConfig`
*   **Purpose:** Configures runtime behavior for an agent invocation (streaming, speech, etc.).
*   **Key Attributes:**
    *   `streaming_mode: StreamingMode` (`NONE`, `SSE`, `BIDI`)
    *   `speech_config: Optional[types.SpeechConfig]`
    *   `response_modalities: Optional[List[str]]` (e.g., `["TEXT", "AUDIO"]`)
    *   `save_input_blobs_as_artifacts: bool`
*   **Usage Example:**
    ```python
    # from google.adk.agents.run_config import RunConfig, StreamingMode
    # from google.genai import types
    
    # run_config = RunConfig(
    #     streaming_mode=StreamingMode.SSE, # For real-time GUI updates
    #     speech_config=types.SpeechConfig(language_code="en-US"),
    #     response_modalities=["TEXT", "AUDIO"]
    # )
    # async for event in runner.run_async(..., run_config=run_config):
    #     pass
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/runtime/runconfig.md`
    *   `Relevant_ADK_docs_2/docs/runtime/runconfig.md`

### 3. Streaming (`LiveRequestQueue`, `runner.run_live`)
*   **Purpose:** Enables bidirectional streaming for real-time interactions (e.g., voice conversations).
*   **Key Components:**
    *   `LiveRequestQueue`: Queue to send real-time inputs (text, audio chunks) to the agent.
    *   `runner.run_live(session, live_request_queue, run_config)`: Starts a live agent session, returning an async generator of `Event` objects.
*   **Usage Pattern (Conceptual Server-Side for WebSocket):**
    ```python
    # from google.adk.agents import LiveRequestQueue
    # live_request_queue = LiveRequestQueue()
    # live_events_stream = runner.run_live(session, live_request_queue, run_config)
    
    # async def forward_agent_events_to_client(websocket, live_events_stream):
    #     async for event in live_events_stream:
    #         # Send event to client (e.g., over WebSocket)
    #         pass 
            
    # async def receive_client_inputs(websocket, live_request_queue):
    #     async for message in websocket:
    #         # Convert message to ADK Content/Blob and send to agent
    #         # live_request_queue.send_content(...) or live_request_queue.send_realtime(...)
    #         pass
    ```
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/streaming/custom-streaming-ws.md` (provides a detailed example)
    *   `Relevant_ADK_docs_1/docs/streaming/index.md`

## VII. Artifacts & Memory

### 1. `ArtifactService` & Context Methods
*   **Purpose:** Managing binary data (files, images) associated with sessions or users.
*   **Context Methods:**
    *   `await context.save_artifact(filename: str, artifact: types.Part) -> int`: Saves artifact, returns version.
    *   `await context.load_artifact(filename: str, version: Optional[int] = None) -> Optional[types.Part]`: Loads artifact.
    *   `await context.list_artifacts() -> List[str]`: Lists artifact filenames.
*   **Namespacing:** Use `"user:filename"` for user-scoped artifacts.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_2/docs/artifacts/index.md`

### 2. `MemoryService` (Python ADK)
*   **Purpose:** Managing searchable, long-term knowledge across sessions.
*   **Key Methods (on service instance):**
    *   `await memory_service.add_session_to_memory(session: Session)`
    *   `await memory_service.search_memory(app_name: str, user_id: str, query: str) -> SearchMemoryResponse`
*   **Tool:** `google.adk.tools.load_memory` can be used by agents to query this.
*   **Implementations:** `InMemoryMemoryService`, `VertexAiRagMemoryService`.
*   **Source Reference(s):**
    *   `Relevant_ADK_docs_1/docs/sessions/memory.md`

This reference sheet should serve as a quick guide for Gemini Legion developers working with ADK. Always refer to the detailed source documents for more in-depth understanding.
The ADK Method Reference sheet has been created. It covers key classes, methods, and patterns from the ADK documentation, focusing on areas relevant to the Gemini Legion project. The content is organized by ADK concepts like Agents, Tools, Sessions/State, Events, Callbacks, Runtime/Streaming, and Artifacts/Memory. Each entry includes a name, purpose, a Python-based usage example (often tailored to Gemini Legion concepts), and source document references.
