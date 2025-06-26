# Project Context Crucible

This document serves as the canonical source of truth to address key context gaps and critical knowledge areas for the Gemini Legion project. It consolidates information from existing project documentation, ADK documentation, and codebase analysis.

## ADK LlmAgent Details

### Exact LlmAgent Pydantic Schema (Key Parameters)

The Python ADK `LlmAgent` (from `google.adk.agents.LlmAgent`) is a Pydantic `BaseModel`. When creating an `LlmAgent` instance, the following key parameters are most relevant for configuration:

*   **Core Identity & Behavior:**
    *   `name: str` (Required): A unique name for the agent instance.
    *   `model: str` (Required): The identifier for the language model to be used (e.g., "gemini-2.0-flash").
    *   `instruction: str` (Required): The system prompt that defines the agent's persona, goals, constraints, and how it should behave and use tools. This can be a template string with placeholders for session state variables (e.g., "Current mood: {current_mood_cue}").
    *   `tools: List[Union[BaseTool, BaseToolset, Callable]]` (Optional): A list of tools the agent can use. These can be instances of `BaseTool` (or its subclasses like `FunctionTool`, `AgentTool`), instances of `BaseToolset` (which dynamically provide tools), or Python callables that will be auto-wrapped into `FunctionTool`s.
    *   `description: str` (Optional, but Recommended for Multi-Agent Systems): A summary of the agent's capabilities, used by other agents for delegation decisions.

*   **Generation Tuning:**
    *   `generate_content_config: Optional[google.genai.types.GenerateContentConfig]` (Optional): Allows specifying LLM generation parameters like `temperature`, `max_output_tokens`, `top_p`, `top_k`, and safety settings.

*   **Data Structuring & State Interaction:**
    *   `input_schema: Optional[Type[BaseModel]]` (Optional): A Pydantic BaseModel class defining the expected structure for input if the agent is meant to receive structured JSON.
    *   `output_schema: Optional[Type[BaseModel]]` (Optional): A Pydantic BaseModel class defining a desired JSON output structure. **Note:** Using `output_schema` typically restricts the agent's ability to use tools or transfer control.
    *   `output_key: Optional[str]` (Optional): If provided, the agent's final text response will be saved to `Session.state[output_key]`.

*   **Context Management:**
    *   `include_contents: Optional[str]` (Default: 'default'): Determines if prior conversation history (`contents`) is sent to the LLM. Can be 'none' for stateless tasks.

*   **Advanced Capabilities (Python ADK primarily noted in `Relevant_ADK_docs`):**
    *   `planner: Optional[BasePlanner]` (Optional): Assign a planner for multi-step reasoning.
    *   `code_executor: Optional[BaseCodeExecutor]` (Optional): Allow the agent to execute code blocks.

*   **Callbacks:**
    *   The `LlmAgent` constructor accepts various optional list parameters for callbacks, such as:
        *   `before_agent_callbacks: Optional[List[Callable[[CallbackContext], Awaitable[Optional[Content]]]]]`
        *   `after_agent_callbacks: Optional[List[Callable[[CallbackContext], Awaitable[Optional[Content]]]]]`
        *   `before_model_callbacks: Optional[List[Callable[[CallbackContext], Awaitable[Optional[LlmResponse]]]]]`
        *   `after_model_callbacks: Optional[List[Callable[[CallbackContext], Awaitable[Optional[LlmResponse]]]]]`
        *   `before_tool_callbacks: Optional[List[Callable[[ToolContext], Awaitable[Optional[Dict[str, Any]]]]]]`
        *   `after_tool_callbacks: Optional[List[Callable[[ToolContext], Awaitable[Optional[Dict[str, Any]]]]]]`

### How to properly store custom data (within LlmAgent or its context)?

There are two main ways to associate custom data (like Minion-specific attributes or domain engine instances) with an `LlmAgent`:

1.  **As Instance Attributes in a Subclass:**
    *   Create a custom agent class that inherits from `google.adk.agents.LlmAgent`.
    *   In your subclass's `__init__` method, accept your custom data/domain objects (e.g., `MinionPersona` instance, `EmotionalEngineV2` instance) as parameters.
    *   Store these as instance attributes (e.g., `self.persona = persona_object`, `self.emotional_engine = emotional_engine_instance`).
    *   Use these attributes within your subclass, for example, to dynamically build the `instruction` for `super().__init__()`, or within ADK callbacks attached to this agent instance.

    ```python
    # Conceptual Example:
    from google.adk.agents import LlmAgent
    # Assuming MinionPersona, EmotionalEngineV2 are defined domain classes
    
    class ADKMinionAgent(LlmAgent):
        def __init__(self, minion_id: str, persona: MinionPersona, 
                     emotional_engine: EmotionalEngineV2, tool_manager, **kwargs):
            self.minion_id = minion_id
            self.persona = persona
            self.emotional_engine = emotional_engine
            # ... other custom attributes ...
            
            system_instruction = self._build_system_instruction()
            minion_tools = tool_manager.get_tools_for_minion(persona) # Or minion_id
            
            super().__init__(
                name=minion_id,
                model=persona.model_config.get("model_name"), # Example
                instruction=system_instruction,
                tools=minion_tools,
                **kwargs
            )
        
        def _build_system_instruction(self) -> str:
            # Uses self.persona and self.emotional_engine.get_current_state()
            # to build a dynamic instruction string for the LlmAgent.
            # ...
            return "..."
            
        # Example of a callback using instance data
        async def before_model_hook(self, callback_context):
            current_emotion_summary = self.emotional_engine.get_current_state_summary()
            # Modify callback_context.llm_request based on emotion
            # ...
            return None # Proceed with modified request
    ```

2.  **In ADK `Session.state` for Dynamic/Invocation-Specific Data:**
    *   For data that needs to influence the LLM on a per-invocation basis (e.g., the Minion's mood *at the moment of the query*), use ADK `Session.state`.
    *   Before calling the agent via `ADKRunner.predict(session=...)` or `ADKRunner.run_async(context=...)`, populate the `session` dictionary (which represents `Session.state`) with the relevant cues.
    *   The agent's `instruction` string should be templated to include these state variables (e.g., `instruction="Your current mood is {current_mood_summary}. User says: {user_query}"`).
    *   Tools and callbacks can also read/write to `Session.state` via their respective context objects (`ToolContext.state`, `CallbackContext.state`).

### Best practices for extending LlmAgent with domain data (e.g., Minion persona, emotional state)?

*   **Encapsulation:** Keep domain-specific logic within your domain objects (e.g., `MinionPersona`, `EmotionalEngineV2`). The `ADKMinionAgent` subclass should *use* these objects but not replicate their internal logic.
*   **Constructor Injection:** Pass instances of domain engines/data objects to your `ADKMinionAgent` subclass's constructor.
*   **Dynamic Instruction Building:** Use data from these injected domain objects (especially static persona aspects) to dynamically construct parts of the `instruction` string passed to `super().__init__()`.
*   **State Bridging for Dynamic Data:**
    *   For dynamic data (like current emotional state) that needs to influence each LLM call:
        *   **Use `Session.state`:** Before running the agent, update `Session.state` with concise cues (e.g., `session_state['current_mood_prompt'] = self.emotional_engine.get_mood_for_prompt()`). The `LlmAgent`'s `instruction` can then reference `{current_mood_prompt}`.
        *   **Use Callbacks:** Implement `before_model_callback` to access `self.emotional_engine` (or other domain objects stored on `self`) and modify the `callback_context.llm_request` directly (e.g., prepend emotional context to the user query or system instruction).
*   **Clear Separation:** ADK `LlmAgent` handles LLM interaction, tool use, and ADK event flow. Your domain objects handle domain logic. The subclass and callbacks/state act as the bridge.
*   **Avoid Overriding Core Methods Unnecessarily:** Prefer using `instruction`, `tools`, `Session.state`, and ADK callbacks to influence behavior. Only override methods like `predict` or `_run_async_impl` if you need to fundamentally change the agent's interaction lifecycle with the ADK Runner, which should be rare if aiming for idiomatic ADK usage.

### How to properly pass domain objects to LlmAgent?

As covered above:
1.  Define your custom agent by subclassing `google.adk.agents.LlmAgent`.
2.  Add parameters to your subclass's `__init__` method to accept these domain objects.
3.  Store these objects as instance attributes (e.g., `self.persona = persona_instance`).
4.  Utilize these instance attributes:
    *   During `__init__` to configure the parent `LlmAgent` (e.g., build the `instruction`).
    *   Within ADK callbacks attached to this agent instance to access their current state and affect LLM requests/responses or `Session.state`.

## Frontend Code Structure

### Where exactly are API calls made?

*   API calls to the backend REST endpoints are primarily encapsulated as functions within the `gemini_legion_frontend/src/services/api/` directory.
*   Key files for API calls include:
    *   `gemini_legion_frontend/src/services/api/minionApi.ts` (for Minion-related operations like spawning, listing).
    *   `gemini_legion_frontend/src/services/api/channelApi.ts` (for channel and message operations).
    *   `gemini_legion_frontend/src/services/api/taskApi.ts` (for task management).
*   These API service functions are typically imported and invoked by action handlers within the Zustand state management stores (located in `gemini_legion_frontend/src/store/`), such as `legionStore.ts`, `chatStore.ts`, and `taskStore.ts`. These actions are often dispatched in response to UI interactions or other application logic.

### How is WebSocket connection handled?

*   The WebSocket (Socket.IO) connection to the backend is established and managed primarily within `gemini_legion_frontend/src/store/legionStore.ts`. This store likely contains a function such as `connectWebSocket()` that initializes the Socket.IO client and sets up connection lifecycle handlers.
*   The custom hook `gemini_legion_frontend/src/hooks/useWebSocket.ts` likely provides React components with access to the WebSocket instance (from `legionStore`) and its current connection status (e.g., connected, disconnected).
*   **Incoming WebSocket event handlers** (e.g., `socket.on('event_name_from_backend', (data) => { ... });`) are predominantly defined in `legionStore.ts`. These handlers are responsible for processing data received from the backend via WebSocket and updating the relevant Zustand stores (`legionStore`, `chatStore`, `taskStore`). UI components, being subscribed to these stores, will then re-render based on these state changes.
*   **Outgoing WebSocket messages** (e.g., subscribing to a channel) are sent from the frontend using the Socket.IO client instance, typically via methods like `socket.emit('event_name_for_backend', payload)`. These emits are also likely wrapped in actions within the Zustand stores.

### What message formats does the frontend expect (from backend via WebSocket)?

The frontend expects JSON messages from the backend over WebSocket. These messages correspond to events emitted by the backend's `GeminiEventBus` and subsequently relayed by the `WebSocketEventBridge`. The exact structure of the JSON payload depends on the specific event type. Based on the system design (and typical real-time application needs), common events and their expected payloads would include:

*   **Event: `CHANNEL_MESSAGE` (or a similar name like `new_message`)**
    *   Purpose: A new message has been posted in a channel.
    *   Expected Payload:
        ```json
        {
          "message_id": "string",    // Unique ID of the message
          "channel_id": "string",    // ID of the channel
          "sender_id": "string",     // ID of the sender (Minion ID or "USER")
          "sender_name": "string",   // Display name of the sender
          "content": "string",       // The actual message text
          "timestamp": "ISO_string_datetime", // Time of message creation
          "metadata": {              // Optional metadata
            "type": "text"           // e.g., "text", "image_url", "file_attachment"
            // ... other metadata fields ...
          }
        }
        ```

*   **Event: `MINION_SPAWNED` (or `minion_update` / `minion_status_change`)**
    *   Purpose: A new Minion has been created or an existing Minion's status/details have updated.
    *   Expected Payload:
        ```json
        {
          "minion_id": "string",
          "name": "string",
          "persona": {
            "base_personality": "string",
            "quirks": ["string", "..."],
            "catchphrases": ["string", "..."]
            // Potentially model_name, expertise_areas
          },
          "status": "string", // e.g., "active", "inactive", "processing"
          "emotional_state": { // Optional: Current emotional snapshot
            "mood": {"valence": "float", "arousal": "float", "dominance": "float"},
            "energy_level": "float",
            "stress_level": "float"
          }
          // Other relevant details like creation_date, is_active_agent
        }
        ```

*   **Event: `MINION_EMOTIONAL_CHANGE` (or `emotion_update`)**
    *   Purpose: A Minion's emotional state has changed.
    *   Expected Payload:
        ```json
        {
          "minion_id": "string",
          "emotional_state": {
            "mood": {"valence": "float", "arousal": "float", "dominance": "float"},
            "energy_level": "float",
            "stress_level": "float"
            // Potentially OpinionScore summaries if relevant to immediate UI
          }
        }
        ```

*   **Event: `TASK_STATUS_UPDATE` (or `task_update`)**
    *   Purpose: The status or progress of a task has changed.
    *   Expected Payload:
        ```json
        {
          "task_id": "string",
          "status": "string", // e.g., "PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "FAILED"
          "progress": "float", // Numeric progress (e.g., 0.0 to 1.0)
          "summary": "string", // Optional: Current step summary or result snippet
          "assigned_minion_id": "string" // Optional: ID of Minion working on it
        }
        ```

*   **Other Potential Events:** `MINION_DESPAWNED`, `CHANNEL_CREATED`, `USER_JOINED_CHANNEL`, `NOTIFICATION` (general purpose notifications), etc., each with their specific, relevant JSON payloads.

The frontend's WebSocket event handlers (primarily in `legionStore.ts`) would be structured to listen for these distinct event names and parse the corresponding payloads to update the application state in Zustand.

## Complete Domain Model Design (Ideal Architecture)

This section details the envisioned structure of key domain models as per the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.

### What should `MoodVector` contain?

The `MoodVector` is designed to represent a Minion's multi-dimensional mood. According to the Ideal Architecture (Section 2.1):

*   **Primary Dimensions:**
    *   `valence: float`: Represents the positive-negative axis of mood (e.g., -1.0 for very negative, 0.0 for neutral, 1.0 for very positive).
    *   `arousal: float`: Represents the energy level of the mood, from calm to excited (e.g., 0.0 for very calm, 1.0 for very excited).
    *   `dominance: float`: Represents the Minion's feeling of control or submissiveness in the current context (e.g., 0.0 for submissive, 1.0 for dominant).

*   **Secondary Dimensions (for nuance):**
    *   `curiosity: float`: The Minion's current level of inquisitiveness (e.g., 0.0 to 1.0).
    *   `creativity: float`: The Minion's inclination towards novel thought or expression (e.g., 0.0 to 1.0).
    *   `sociability: float`: The Minion's desire for social interaction (e.g., 0.0 to 1.0).

*   **Functionality:**
    *   It should include a method like `to_prompt_modifier(self) -> str` which translates these numerical values into a natural language phrase or set of keywords that can be injected into an LLM prompt to make the Minion's responses mood-aware (e.g., "[Feeling curious and energetic]").

The current implementation in `gemini_legion_backend/core/domain/emotional.py` includes `valence`, `arousal`, and `dominance` but is missing the secondary dimensions.

### How do `OpinionScores` work?

`OpinionScores` are central to how Minions develop and maintain relationships and judgments about other entities. Based on the Ideal Architecture (Section 2.1):

1.  **Purpose:** An `OpinionScore` object represents one Minion's specific opinion about another entity (which could be a user, another Minion, a concept, or a task).
2.  **Storage:** The main `EmotionalState` object of a Minion contains a dictionary called `opinion_scores: Dict[str, OpinionScore]`. The keys of this dictionary are the unique IDs of the entities, and the values are the `OpinionScore` objects.
3.  **Structure of `OpinionScore`:**
    *   `entity_id: str`: The unique identifier of the entity this opinion pertains to.
    *   `entity_type: EntityType`: An enum (e.g., `USER`, `MINION`, `CONCEPT`, `TASK`) specifying the type of the entity.
    *   **Core Metrics (numerical, e.g., -100 to 100):**
        *   `trust: float`
        *   `respect: float`
        *   `affection: float`
    *   **Interaction History:**
        *   `interaction_count: int`: Total number of interactions with this entity.
        *   `last_interaction: datetime`: Timestamp of the most recent interaction.
        *   `notable_events: List[OpinionEvent]`: A list of specific, significant past interactions or events that have shaped this opinion. Each `OpinionEvent` would be a structured object containing a description of the event, its timestamp, and its impact on trust, respect, and affection.
    *   **Computed Property:**
        *   `overall_sentiment: float`: A calculated property, for example, `(trust + respect + affection) / 3`.

4.  **Dynamics:** When a Minion interacts with an entity, the `EmotionalPolicyEngine` would propose updates not only to the Minion's overall `MoodVector` but also to the specific `OpinionScore` related to that entity. For instance, a positive interaction might increase `trust` and `affection` in the `OpinionScore` for that entity. `Notable_events` would be added for particularly impactful interactions.

The current domain models in `gemini_legion_backend/core/domain/` do not appear to have `OpinionScore` or `OpinionEvent` classes, nor is `opinion_scores` part of the current `EmotionalState` Pydantic model. This is a key area for development to achieve the envisioned social dynamics.

### What's the full `EmotionalState` structure?

Based on the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` (Section 2.1), the full, envisioned structure for `EmotionalState` is:

```python
# Conceptual Python dataclass representation from Ideal Architecture
class EmotionalState:
    minion_id: str                        # ID of the Minion owning this state
    mood: 'MoodVector'                    # Current multi-dimensional mood (detailed above)
    energy_level: float                   # Overall energy (0.0 to 1.0)
    stress_level: float                   # Overall stress (0.0 to 1.0)
    
    # Relational and Social Aspects
    opinion_scores: Dict[str, 'OpinionScore'] # Opinions about other entities (detailed above)
    relationship_graph: 'RelationshipGraph' # Object representing the Minion's social network graph and relationship strengths/types (e.g., friend, rival, subordinate). (Details of RelationshipGraph would need further definition but implies nodes for entities and edges for relationships with properties.)
    
    # Behavioral Modifiers (influencing response generation)
    response_tendency: 'ResponseTendency'   # Object defining current behavioral inclinations like verbosity, humor level, argumentativeness, proactivity. (Details of ResponseTendency would need further definition.)
    conversation_style: 'ConversationStyle' # Object defining nuances like formality, use of jargon/slang, emotional expressiveness in language. (Details of ConversationStyle would need further definition.)
    
    # Meta-cognitive and Goal-Oriented Aspects
    self_reflection_notes: List['ReflectionEntry'] # Structured entries from self-reflection processes, perhaps containing insights, resolved internal conflicts, or learning points. (Details of ReflectionEntry would need further definition.)
    goal_priorities: List['GoalPriority']        # List of current goals and their priority, which can be influenced by emotional state (e.g., high stress might reprioritize safety goals). (Details of GoalPriority would need definition: goal_id, priority_score, emotional_influence_factor.)
    
    # System Attributes
    last_updated: 'datetime'                # Timestamp of the last update to the emotional state
    state_version: int                    # Version number for concurrency control or history tracking
```

The current Pydantic model for `EmotionalState` in `gemini_legion_backend/core/domain/emotional.py` is much simpler, containing only `minion_id`, `mood` (a simpler `MoodVector`), `energy_level`, and `stress_level`. The ideal architecture envisions a significantly richer and more detailed structure for these domain entities.

## Original Vision Details

This section clarifies aspects of the original project vision as outlined in the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`.

### How should minions interact autonomously?

According to Section 5.2 ("Autonomous Minion-to-Minion Messaging") of the Ideal Architecture:

1.  **Autonomous Messaging Engine:** Minion autonomy in communication is driven by an `AutonomousMessagingEngine`. This engine decides if a Minion should initiate communication.
2.  **Decision Process:**
    *   **Social Appropriateness:** A `SocialReasoner` component first assesses if the current context and social dynamics make it appropriate for the Minion to speak up or reach out.
    *   **Communication Need:** The Minion (or its engine) analyzes its internal state, goals, and observations to determine if there's a genuine *need* to communicate. This need is quantified by an `urgency` level.
    *   **Urgency Threshold:** Communication is initiated only if this `urgency` surpasses a predefined `AUTONOMOUS_THRESHOLD`.
    *   **Conversation Planning:** If the threshold is met, a `ConversationPlanner` component designs the outreach. This plan includes identifying the `recipients`, the `purpose` of the communication, crafting an `initial_message`, and estimating the `expected_turns` in the conversation.
3.  **Output:** The result of this process is an `AutonomousMessage` object, which is then presumably sent through the `InterMinionCommunicationSystem`.
4.  **Influencing Factors:** A Minion's `MinionPersona`, current `EmotionalState`, and active `goal_priorities` would heavily influence the reasoning of the `SocialReasoner`, the assessment of `communication_need`, and the strategies of the `ConversationPlanner`.

This implies that Minions require a sophisticated level of self-awareness (of their state and goals) and contextual understanding to trigger and execute autonomous interactions effectively.

### What triggers emotional changes?

As per Section 2.2 ("LLM as Emotional Policy Engine") and other parts of Section 2 in the Ideal Architecture:

1.  **Interaction Events:** The primary trigger is any significant `InteractionEvent` that a Minion experiences. This includes:
    *   Receiving messages.
    *   Sending messages.
    *   Successfully using a tool.
    *   Failing to use a tool.
    *   Observing significant environmental events (if the Minion has perceptual capabilities).
2.  **Emotional Policy Engine:** This core component processes the `InteractionEvent`.
    *   It takes the Minion's `current_state` (the existing `EmotionalState` object) and the `ConversationContext` as inputs.
    *   It uses an LLM with a specialized prompt designed for emotional analysis. This prompt guides the LLM to assess the emotional impact of the interaction.
    *   The LLM's output is a proposal for structured changes to the `EmotionalState` – an `EmotionalStateUpdate` object. This might detail changes to `MoodVector`, `OpinionScores` for involved entities, `stress_level`, etc.
3.  **Validation & Application:** The `EmotionalStateUpdate` proposed by the LLM is then validated by an `EmotionalStateValidator` (to ensure changes are within reasonable bounds and consistent) before being applied to the Minion's `EmotionalState`.
4.  **Self-Reflection & Diary:**
    *   The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` also specifies `self_reflection_notes` within `EmotionalState` and a `PersonalDiary` (Section 2.3) where Minions record entries with an `emotional_snapshot`.
    *   Significant insights from self-reflection or impactful events recorded in the diary can also contribute to or document the basis for emotional shifts, likely by feeding back into the `EmotionalPolicyEngine` or by directly suggesting an `EmotionalStateUpdate`.
5.  **MinionAgent's Internal Loop:** The `MinionAgent`'s own processing loop (e.g., after its `predict` or `think` method completes) includes a step for post-processing the interaction to update its emotional state and memories (as seen in Section 4.1 and 4.3 of the Ideal Architecture).

Essentially, emotions are dynamic and reactive to the Minion's experiences, processed through a structured, LLM-augmented policy engine.

### How does memory consolidation work?

Section 3.2 ("Memory Consolidation and Forgetting") of the Ideal Architecture describes this process:

1.  **Memory Consolidator Component:** A dedicated component, `MemoryConsolidator`, is responsible for managing the memory consolidation process. This is envisioned as a periodic background task.
2.  **Multi-Layered Process:**
    *   **Promotion (Short-Term to Episodic):** Important memories from the `ShortTermMemory` layer are identified and promoted to the `EpisodicMemory` layer. `EpisodicMemory` is designed for storing specific, significant past experiences and is backed by a VectorDatabase, suggesting that the "importance" might be determined by factors like emotional salience or relevance to goals, and that these memories are stored with their embeddings for later retrieval.
    *   **Abstraction & Generalization (Episodic to Semantic):** The system analyzes recent entries in `EpisodicMemory` (e.g., memories from the last 7 days) to identify patterns, extract insights, or generalize knowledge. These abstracted pieces of information are then integrated into the `SemanticMemory` layer, which is represented by a KnowledgeGraph and ConceptEmbeddings. This step is crucial for learning and building up a more generalized understanding from specific episodes.
    *   **Forgetting:** A "forgetting curve" mechanism is applied. This means that memories (likely in episodic or even short-term layers) that are less important, infrequently accessed, or have low emotional significance will gradually decay in accessibility or be pruned from the memory system. This ensures the memory system remains efficient and relevant.

This structured consolidation process allows Minions to not just store raw experiences but to learn from them, form generalized knowledge, and maintain a manageable and relevant memory over time.

## ADK Best Practices (Consolidated)

This section consolidates ADK best practices relevant to Gemini Legion, drawn from the `Project_Documentation/ADK_Integration/adk_integration_masterclass.md` and general ADK principles.

### How to properly pass domain objects to LlmAgent?

1.  **Subclass `LlmAgent`:** Create a custom agent class (e.g., `ADKMinionAgent`) that inherits from `google.adk.agents.LlmAgent`.
2.  **Constructor Injection:** In your subclass's `__init__` method, accept instances of your domain objects (e.g., `MinionPersona`, `EmotionalEngineV2`, `MemorySystemV2`) as parameters. Store these as instance attributes (e.g., `self.persona = persona_object`).
3.  **Configure Parent `LlmAgent`:** Use the data from these injected domain objects *within your subclass's `__init__`* to dynamically construct the standard `LlmAgent` parameters (like `instruction`, `tools`, `model_name`) that are passed to `super().__init__(...)`.
    *   Example: `system_instruction = f"You are {self.persona.name}..."`
    *   Example: `minion_tools = self.tool_manager.get_tools_for_minion(self.persona)`
4.  **Dynamic Data Influence (During Invocation):**
    *   To make *dynamic* aspects of domain objects (e.g., current emotional state from `self.emotional_engine`) influence LLM calls managed by the ADK `LlmAgent` parent class, do not directly try to pass the whole engine object into the prompt. Instead:
        *   **Use `Session.state`:** Before the `ADKRunner` invokes your agent for a specific query, populate the `Session.state` dictionary with concise, prompt-friendly cues derived from your domain objects (e.g., `session_state_dict['current_mood_summary'] = self.emotional_engine.get_summary()`). Ensure your agent's main `instruction` string is templated to use these state variables (e.g., "Current mood: `{current_mood_summary}`").
        *   **Use ADK Callbacks:** Implement callbacks like `before_model_callback`. Inside the callback, you can access `self.emotional_engine` (or other domain objects stored on `self`) and use their current data to modify the `callback_context.llm_request` (e.g., by adding contextual prefixes to the prompt or augmenting system instructions dynamically).

### Whether to use callbacks or override methods (for integrating domain data/logic)?

*   **Callbacks (Preferred for Integration & Augmentation):**
    *   **Purpose:** Use callbacks to inject dynamic data from your domain objects into the ADK lifecycle, modify requests/responses, log detailed information, or react to specific events (like tool calls or model responses) without altering the fundamental execution flow managed by the ADK `LlmAgent` and `Runner`.
    *   **Examples for Gemini Legion:**
        *   `before_model_callback`: To fetch the current emotional state from `self.emotional_engine` and add it to the LLM prompt.
        *   `after_model_callback` or `after_tool_callback`: To process the LLM's response or tool output and feed it to `self.emotional_engine` for state updates, or to `self.memory_system` for experience storage.
    *   **Advantage:** Keeps your custom logic cleanly separated and leverages ADK's defined extension points. It's less prone to breaking if ADK's internal `LlmAgent` logic changes in future versions.

*   **Override Methods (For Fundamental Behavior Changes):**
    *   **Purpose:** Override methods like `predict()` (if you need to change the high-level request-response handling) or `_run_async_impl()` (if you need to completely redefine the agent's core event-yielding loop) only when your requirements cannot be met by `instruction`, `tools`, `Session.state`, and callbacks.
    *   **Consideration for Gemini Legion:** The `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` (Section 4.3) discusses a strategy for `predict()` that involves pre-processing (emotional/memory context injection) and post-processing (state updates). This can often be achieved by a combination of preparing `Session.state` before calling `super().predict()` and using `after_model_callbacks` (or handling it in the service layer after `predict()` returns). A full override might be more than needed if the goal is just context augmentation.
    *   **Caution:** Overriding core methods can make your agent deviate significantly from standard ADK behavior, potentially missing out on framework optimizations or features, and might require more maintenance if ADK internals change.
    *   **Recommendation:** For integrating domain data like emotional state or memory cues, callbacks are generally the more idiomatic and maintainable ADK approach.

### How to integrate with ADK Runner?

1.  **Centralized Runner Instance:**
    *   An instance of `google.adk.runners.Runner` should be created and managed centrally in your application, typically during startup. For Gemini Legion, this should occur in `gemini_legion_backend/core/dependencies_v2.py` within the `ServiceContainerV2`.
2.  **Runner Initialization:**
    *   The `Runner` needs to be initialized with:
        *   `agent`: The root agent of your application (this could be a dispatcher agent if you have multiple top-level agents, or the main `ADKMinionAgent` type if minions are directly invoked).
        *   `app_name: str`: A unique name for your application.
        *   `session_service: BaseSessionService`: An instance of a session service (e.g., `DatabaseSessionService` for persistence).
        *   `artifact_service: Optional[BaseArtifactService]`: (If using artifacts) An instance of an artifact service.
        *   `memory_service: Optional[BaseMemoryService]`: (If using ADK's long-term memory) An instance of a memory service.
3.  **Invocation by Application Services:**
    *   Your application services (like `MinionServiceV2`) should obtain the `Runner` instance from the service container.
    *   When a Minion needs to process an input or perform a task, the service layer should use the `Runner` to execute the Minion.
    *   **Example (Conceptual `MinionServiceV2` using `run_async`):**
        ```python
        # class MinionServiceV2:
        #     def __init__(self, runner: Runner, ...):
        #         self.runner = runner
        #
        #     async def handle_message_for_minion(self, minion_id: str, user_message: str, session_id: str, user_id: str):
        #         # ... prepare ADK session state if needed ...
        #         events_iterator = self.runner.run_async(
        #             user_id=user_id, session_id=session_id,
        #             # agent_name=minion_id, # If Runner's root_agent is a dispatcher
        #             new_message=Content(parts=[Part(text=user_message)]),
        #             # initial_state_if_new_session=prepared_session_state_dict 
        #         )
        #         async for event in events_iterator:
        #             if event.is_final_response() and event.content:
        #                 return event.content.parts[0].text
        #         return "Minion did not provide a final response."
        ```
    *   If using `predict` for simpler request-response:
        ```python
        # response_text = await self.runner.predict(
        #     message=user_message, session_id=session_id, user_id=user_id
        # )
        ```
        The `Runner` handles interaction with the `LlmAgent` subclass. `Session.state` for the specific `session_id` would be loaded by the `SessionService` configured in the `Runner`.

## Deployment Requirements (Consolidated)

### What environment variables are needed?

Based on ADK features and common cloud deployment patterns:

*   **`GOOGLE_API_KEY`**: Required if using Google AI Studio Gemini models directly and not relying on Application Default Credentials (ADC). For Vertex AI, ADC is preferred.
*   **`GOOGLE_CLOUD_PROJECT`**: Required if using Google Cloud services such as Vertex AI (for models, `VertexAiSessionService`, `VertexAiRagMemoryService`) or Google Cloud Storage (for `GcsArtifactService`).
*   **`GOOGLE_CLOUD_LOCATION`**: Required for Vertex AI services, specifying the region (e.g., `us-central1`).
*   **`GOOGLE_GENAI_USE_VERTEXAI=True`**: If you intend for ADK to use Vertex AI as the backend for Gemini model interactions (instead of Google AI Studio direct APIs).
*   **`DATABASE_URL`**: Required if using `DatabaseSessionService` for persistent session storage. The format depends on the database used (e.g., `sqlite:///./sessions.db`, `postgresql://user:password@host:port/database`).
*   **GCS Bucket Name (if using `GcsArtifactService`):** While often passed as a constructor argument to `GcsArtifactService`, this could also be configured via an environment variable that your application reads at startup to initialize the service.
*   **RAG Corpus Resource Name (if using `VertexAiRagMemoryService`):** Similar to GCS bucket, could be configured via an env var for service initialization.
*   **Application-Specific Variables:** Any other environment variables your custom tools, services, or application logic might require (e.g., API keys for third-party services your tools connect to, configuration paths for other parts of Gemini Legion).

### Database setup for persistence?

If using `DatabaseSessionService` for persistent ADK sessions:

1.  **Choose a Database:** Select a relational database compatible with SQLAlchemy. Common choices include:
    *   **PostgreSQL:** Robust, feature-rich, recommended for production.
    *   **MySQL:** Widely used, suitable for production.
    *   **SQLite:** File-based, excellent for development, testing, or very small single-instance deployments. Not generally recommended for highly concurrent or scalable production loads.
2.  **Database Server Setup:** Ensure the database server is running, configured, and accessible from where your ADK application will be deployed (network policies, firewalls).
3.  **Create Database & User:** In your chosen database server, create a dedicated database for your application (e.g., `gemini_legion_db`) and a database user with sufficient permissions on that database (e.g., `CREATE TABLE`, `SELECT`, `INSERT`, `UPDATE`, `DELETE`).
4.  **Connection String (`DATABASE_URL`):** Construct the correct SQLAlchemy connection string. Provide this string to your application via the `DATABASE_URL` environment variable. Examples:
    *   SQLite: `sqlite:///./gemini_legion_sessions.db` (creates a file named `gemini_legion_sessions.db` in the application's working directory)
    *   PostgreSQL: `postgresql://db_user:db_password@db_host:db_port/db_name`
    *   MySQL: `mysql+mysqlconnector://db_user:db_password@db_host:db_port/db_name`
5.  **Schema Creation (ADK Tables):**
    *   The ADK `DatabaseSessionService` uses SQLAlchemy ORM. Upon its first connection to the database (typically at application startup when the service is initialized), it will attempt to automatically create the necessary tables (`adk_sessions`, `adk_events`) if they do not already exist. This requires the database user (specified in `DATABASE_URL`) to have `CREATE TABLE` permissions.
    *   For production environments, especially with PostgreSQL or MySQL, it's often a best practice to manage database schema migrations explicitly using a dedicated migration tool (like Alembic for Python/SQLAlchemy projects). This gives you more control over schema changes, versioning, and rollbacks. However, for simpler setups or initial development, ADK's automatic table creation can suffice.

### Production configuration?

Key considerations for a production ADK deployment for Gemini Legion:

*   **Persistent Services:**
    *   **Session Management:** Mandatorily use `DatabaseSessionService` with a robust relational database (e.g., PostgreSQL).
    *   **Artifact Storage (if used):** Use `GcsArtifactService` with a Google Cloud Storage bucket.
    *   **Long-Term Memory (if ADK's `MemoryService` is adopted alongside custom `MemorySystemV2`):** Use a persistent implementation like `VertexAiRagMemoryService`.
    *   **Avoid `InMemory...` services entirely for production.**
*   **Scalability & Performance:**
    *   Run the FastAPI application using an ASGI server like Uvicorn, potentially managed by Gunicorn for multi-worker configurations to handle concurrent requests effectively.
    *   Design application services (like `MinionServiceV2`) to be as stateless as possible, relying on the persistent ADK services and your primary database for state. This facilitates horizontal scaling of your application instances.
    *   If running multiple instances, ensure they all connect to the same centralized database for `DatabaseSessionService`.
*   **Security:**
    *   Manage all secrets (API keys, database credentials, etc.) securely, preferably using a secret management system (e.g., Google Secret Manager, HashiCorp Vault) and injecting them as environment variables into the application runtime. Do not hardcode secrets.
    *   Secure network access to your database and other backend services.
    *   Implement robust authentication and authorization for all API endpoints exposed by FastAPI.
*   **Configuration Management:**
    *   Externalize all configurations (e.g., `RunConfig` defaults, model names, tool-specific settings, resource limits) using environment variables or dedicated configuration files. Do not hardcode these.
*   **Logging & Monitoring:**
    *   Implement comprehensive structured logging (e.g., JSON logs) throughout the application, including detailed logs from ADK callbacks for tracing agent behavior, tool usage, and errors.
    *   Integrate with a centralized logging and monitoring platform (e.g., Google Cloud Logging & Monitoring, ELK stack, Datadog) to track application health, performance metrics, error rates, and costs.
*   **Error Handling & Resilience:**
    *   Implement robust error handling within all custom agent logic, tools, and callbacks.
    *   Use try-except blocks appropriately.
    *   Consider patterns like retries with exponential backoff for transient errors when calling external services (including LLMs or tools).
    *   The `ResilientMinionSystem` concept from the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` should be implemented.
*   **`RunConfig` Defaults:**
    *   Establish sensible default `RunConfig` values for your application, especially `max_llm_calls` (to prevent unexpected costs or runaway loops) and `streaming_mode` (if real-time UI updates are standard).
*   **Resource Management:**
    *   Monitor CPU, memory, and network usage of your application instances and database. Adjust resources as needed based on load.
*   **Testing & Evaluation:**
    *   Maintain a comprehensive suite of automated tests (unit, integration, and end-to-end).
    *   Utilize ADK's evaluation framework to regularly assess the quality and behavior of your Minion agents against predefined test cases and metrics.
*   **Codebase & Dependency Management:**
    *   Keep dependencies, including `google-adk` and `google-generativeai`, up to date.
    *   Use a virtual environment and lock file (`poetry.lock` or `requirements.txt`) for reproducible builds.
