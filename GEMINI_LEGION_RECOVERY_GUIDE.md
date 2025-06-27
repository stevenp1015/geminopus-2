# Gemini Legion - Step-by-Step Recovery and Enhancement Guide

## Introduction
This guide provides a hypergranular, step-by-step approach to address critical issues, implement core features, and move the Gemini Legion codebase towards the vision outlined in the `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` (IADD). It is designed for developers who may benefit from explicit instructions, clear context, and detailed verification steps.

**Please follow each step precisely in the order presented.** Each step builds upon the previous one. Refer to `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md` (IADD) and `Project_Context_Crucible.md` (PCC) for architectural and ADK-specific details.

## Phase 1: Core Functionality & ADK Stabilization

### Major Task 1.1: Resolve ADK Runner and Session Management Issue

**Context for this major task:**
The most critical issue preventing minions from responding is the "Session not found" error when `MinionServiceV2` attempts to use `runner.predict()`. This phase aims to rectify the ADK `Runner` and `SessionService` interaction to enable successful LLM calls and response generation. We will primarily be working with `gemini_legion_backend/core/application/services/minion_service_v2.py`. The `Project_Context_Crucible.md` (PCC) is our primary reference for ADK patterns.

---
**Step 1.1.1: Standardize `session_id` for `predict` Calls**

**Objective:**
*   Ensure a consistent and valid `session_id` is used when calling `runner.predict()`, allowing ADK's `InMemorySessionService` to manage session creation and context.

**File(s) to Modify:**
*   `gemini_legion_backend/core/application/services/minion_service_v2.py`

**Context & Reasoning:**
*   The IADD (Section 4.3) and PCC (ADK LlmAgent Details) emphasize session-based context. The "Session not found" error (per handoffs) indicates an issue with how `session_id` is passed to or handled by `runner.predict()` with `InMemorySessionService`.
*   `InMemorySessionService` should create a session if a provided `session_id` doesn't exist. We will use a consistent `session_id` format for minion interactions within a channel.

**Detailed Instructions:**

*   **In `gemini_legion_backend/core/application/services/minion_service_v2.py`:**
    *   Locate the `_handle_channel_message` method.
    *   Modify the section where `runner.predict()` is called, typically around line 250 or within the loop `for minion_id, agent_instance in self.agents.items():` (Note: your loop variable for the agent object might be `agent` or `agent_instance`).

    **Identify the existing `try...except` block for `runner.predict()` which might look something like this (exact code might vary):**
    ```python
    # Existing code snippet to find and replace:
                    try:
                        response_text = await runner.predict(
                            message=content,
                            session_id=f"{channel_id}_{minion_id}",
                            user_id=sender_id
                        )
                    except Exception as e:
                        logger.error(f"Error with predict: {e}")
                        # Fallback logic might be present here
                        try:
                            response_text = await runner.predict(
                                message=content,
                                user_id=sender_id
                            )
                        except Exception as e2:
                            logger.error(f"Error with predict (no session): {e2}")
                            continue
    ```
    **Replace the entire `try...except` block above (or the equivalent `runner.predict` call section) with this improved block:**
    ```python
                        runner = self.runners.get(minion_id)
                        if not runner:
                            logger.warning(f"No runner found for minion {minion_id}")
                            continue

                        # Construct a consistent session ID for the interaction
                        current_session_id = f"channel_{channel_id}_minion_{minion_id}"

                        logger.info(f"Attempting predict for minion {minion_id} with session_id: {current_session_id} for message: '{content[:30]}...'")

                        # Use predict for simpler request-response.
                        # Pass the session_id. InMemorySessionService should create it if it doesn't exist.
                        # The `user_id` parameter identifies the originator of the message the minion is responding to.
                        try:
                            response_text = await runner.predict(
                                message=content,
                                session_id=current_session_id,
                                user_id=sender_id
                            )
                        except Exception as e:
                            logger.error(f"Error during runner.predict() for minion {minion_id} with session_id {current_session_id}: {e}", exc_info=True)
                            response_text = None # Ensure response_text is None if predict fails
                            # Optionally, you could add a specific fallback response here or re-raise
                            # For now, we let it proceed to the `if response_text:` check

                        # The rest of the logic (if response_text: ...) follows
    ```

    *   **Explanation of Changes:**
        *   We consistently provide a `session_id` (`current_session_id`) to `runner.predict()`.
        *   `InMemorySessionService` is expected to create a session with this ID if it's new for this service instance.
        *   The previous complex fallback logic for `predict` is simplified to a single attempt with a clear `session_id`.
        *   Added more robust error logging for the `predict` call itself.

**Verification:**
1.  Restart the backend server: `python3 -m gemini_legion_backend.main_v2`.
2.  Observe the backend logs for:
    *   Successful initialization of `ADKMinionAgent` and `Runner` instances.
    *   Log messages like `Attempting predict for minion echo_prime with session_id: channel_general_minion_echo_prime...`.
    *   **Crucially, ensure there are NO "Session not found" errors directly from ADK related to `predict`.** If errors persist, they might be from other parts of the code or indicate a deeper misunderstanding of `InMemorySessionService` behavior that requires consulting `Project_Context_Crucible.md`.
    *   Look for logs indicating successful LLM calls.
3.  Using a tool like Postman or the frontend:
    *   Spawn a minion (e.g., the default "echo_prime").
    *   Send a message to a channel (e.g., "general").
4.  **Expected Outcome:**
    *   The minion responds to the message in the channel.
    *   The response is a generative text from Gemini, not a hardcoded fallback or an error message.
    *   Subsequent messages to the same minion in the same channel use the same `session_id`.

**Potential Pitfalls:**
*   Ensure `GEMINI_API_KEY` environment variable is correctly set and accessible.
*   Typos in `session_id` format or parameters passed to `predict`.
*   The `InMemorySessionService` has limitations (it's in-memory, so sessions are lost on restart). For true persistence, `DatabaseSessionService` is needed later.
*   If "Session not found" errors *still* occur, it points to a fundamental issue in how the `Runner` or `InMemorySessionService` is configured or how ADK expects `predict` to be used with new sessions. The `Project_Context_Crucible.md` is the definitive guide here.

**State of the System After This Step:**
*   Minions should now be able to generate responses using ADK `Runner.predict()`. The primary blocker to core functionality is resolved.
*   Basic conversational context (within the scope of a single `session_id`) might start to work if the default `LlmAgent` behavior includes recent turn history in prompts.

---

### Major Task 1.2: Implement Basic Functional ADK Communication Tools

**Context for this major task:**
The `ADKCommunicationKit` provides tool definitions, but they are placeholders. This task makes the `send_channel_message` tool functional by having it use the event bus, allowing minions to send messages.

---
**Step 1.2.1: Make `send_channel_message` Tool Functional**

**Objective:**
*   Modify the `send_channel_message` tool within `ADKCommunicationKit` to correctly use the injected event bus to emit a `CHANNEL_MESSAGE` event, enabling minions to send messages to channels.

**File(s) to Modify:**
*   `gemini_legion_backend/core/infrastructure/adk/tools/communication_tools.py`

**Context & Reasoning:**
*   IADD Section 6.1 specifies ADK-native tools. Handoff V6 (Tasks 007, 013) aimed to fix and complete these communication tools.
*   The current `send_channel_message` tool is a placeholder. It needs to interact with the application's event bus to actually send a message. The `ADKCommunicationKit`'s constructor receives an `event_bus` instance.
*   `event_bus.emit_channel_message` is an `async` function. ADK tools are typically executed synchronously. `asyncio.create_task` is used to schedule the async operation from the sync tool context when an event loop is running (as in FastAPI).

**Detailed Instructions:**

*   **In `gemini_legion_backend/core/infrastructure/adk/tools/communication_tools.py`:**
    *   Ensure `asyncio` and `logging` are imported.
    *   Ensure the `ADKCommunicationKit` constructor correctly stores `event_bus`.
    *   Replace the `send_channel_message` method.

    ```python
    import asyncio
    import logging
    from typing import Dict, Any, List # Ensure List is imported for get_tools

    logger = logging.getLogger(__name__)

    class ADKCommunicationKit:
        def __init__(self, minion_id: str, event_bus: Any): # Added type hint for clarity
            self.minion_id = minion_id
            self.event_bus = event_bus
            logger.info(f"ADKCommunicationKit initialized for {minion_id}")

        def send_channel_message(self, channel: str, message: str) -> Dict[str, Any]:
            """
            Send a message to a channel by emitting an event through the event bus.

            Args:
                channel: The channel ID or name to send to
                message: The message content to send

            Returns:
                Dict containing success status and event details for the LLM.
            """
            try:
                tool_name = "send_channel_message"
                logger.info(f"Tool '{tool_name}' called by {self.minion_id} for channel '{channel}' with message: '{message[:50]}...'")

                if not self.event_bus:
                    logger.error(f"Event bus not available for minion {self.minion_id} in {tool_name} tool.")
                    return {
                        "success": False,
                        "error": "Event bus not configured for this tool.",
                        "tool_used": tool_name,
                        "channel": channel,
                        "message_preview": message[:100]
                    }

                # The event_bus.emit_channel_message is an async function.
                # Schedule it as a task from this synchronous tool context.
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(
                            self.event_bus.emit_channel_message(
                                channel_id=channel,
                                sender_id=self.minion_id,
                                content=message,
                                source=f"tool:{tool_name}:{self.minion_id}"
                            )
                        )
                        logger.info(f"Message from {self.minion_id} to channel {channel} queued for emission via event bus.")
                        return {
                            "success": True,
                            "status": "Message emission initiated to channel.",
                            "tool_used": tool_name,
                            "channel": channel,
                            "message_preview": message[:100]
                        }
                    else:
                        logger.error(f"No running event loop found to schedule emit_channel_message for {self.minion_id}.")
                        return {"success": False, "error": "No running event loop.", "tool_used": tool_name}
                except RuntimeError as e:
                    logger.error(f"RuntimeError getting event loop for {self.minion_id}: {e}. Cannot emit message.")
                    return {"success": False, "error": f"Event loop issue: {e}", "tool_used": tool_name}

            except Exception as e:
                logger.error(f"Error in send_channel_message tool for {self.minion_id}: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "tool_used": "send_channel_message",
                    "channel": channel,
                    "message_preview": message[:100]
                }

        # Placeholder for other tools - ensure they are defined
        def listen_to_channel(self, channel: str, duration: int = 60) -> Dict[str, Any]:
            logger.info(f"Tool 'listen_to_channel' called by {self.minion_id} for channel {channel}")
            return {"success": True, "status": f"Placeholder: Listening to {channel} for {duration}s.", "tool_used": "listen_to_channel"}

        def get_channel_history(self, channel: str, limit: int = 10) -> Dict[str, Any]:
            logger.info(f"Tool 'get_channel_history' called by {self.minion_id} for channel {channel}")
            return {"success": True, "status": f"Placeholder: History for {channel} (limit {limit}) requested.", "tool_used": "get_channel_history", "messages": []}

        def send_direct_message(self, recipient: str, message: str) -> Dict[str, Any]:
            logger.info(f"Tool 'send_direct_message' called by {self.minion_id} to {recipient}")
            return {"success": True, "status": f"Placeholder: DM to {recipient} initiated.", "tool_used": "send_direct_message"}

        def get_tools(self) -> List[Any]:
            tools = [
                self.send_channel_message,
                self.listen_to_channel,
                self.get_channel_history,
                self.send_direct_message
            ]
            logger.info(f"Provided {len(tools)} communication tools for {self.minion_id}")
            return tools
    ```

    *   **Explanation of Changes:**
        *   The tool now robustly uses `asyncio.create_task` for `self.event_bus.emit_channel_message`.
        *   Added checks for `event_bus` and running event loop.
        *   Return dictionary includes `tool_used` for better LLM understanding.
        *   Placeholders for other tools are maintained for completeness of the `ADKCommunicationKit`.

**Verification:**
1.  Restart the backend server.
2.  Ensure ADK Runner/Session fix (Task 1.1) is working.
3.  Prompt a minion to use the `send_channel_message` tool (e.g., by telling it: "echo_prime, please send the message 'Testing my new tool!' to the 'general' channel").
4.  **Expected Outcome:**
    *   Backend logs show the `send_channel_message` tool being called by the LLM, and the message being queued for emission via the event bus.
    *   A new message from "echo_prime" (or the relevant minion) with content "Testing my new tool!" appears in the "general" channel (visible on frontend or via WebSocket log).
    *   The LLM should receive a success confirmation from the tool.

**Potential Pitfalls:**
*   The `event_bus` might not be correctly initialized or passed to `ADKCommunicationKit` when `ADKMinionAgent` is created in `MinionServiceV2`. Double-check `ADKMinionAgent`'s `__init__`.
*   The `emit_channel_message` method on the event bus itself might have issues (though this is less likely if basic message sending from user->channel was working).

**State of the System After This Step:**
*   Minions are now capable of actively sending messages to channels using an ADK tool. This is a fundamental capability for agent interaction.

---

## Phase 2: Enhancing Minion Capabilities

### Major Task 2.1: Basic Emotional Engine Integration

**Context for this major task:**
The IADD outlines a sophisticated emotional engine. Handoff V7 suggests a simpler initial integration: using `Session.state` to inject emotional state into prompts and update agent instructions dynamically. Domain models (`EmotionalState`, `MoodVector`, etc.) are already defined.

---
**Step 2.1.1: Initialize and Store EmotionalEngine in ADKMinionAgent**

**Objective:**
*   Create/refine a basic `EmotionalEngineV2` class capable of holding `EmotionalState` and providing a prompt summary.
*   Instantiate and store an `EmotionalEngineV2` instance within each `ADKMinionAgent`.
*   Modify the agent's system instruction to include a placeholder for dynamic emotional cues.

**File(s) to Modify:**
*   `gemini_legion_backend/core/domain/emotional.py`
*   `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`

**Context & Reasoning:**
*   IADD Section 2 describes the emotional engine. Handoff V7 guides this initial integration approach.
*   Each agent requires its own `EmotionalEngineV2` instance.
*   The system instruction needs a placeholder (e.g., `{{current_emotional_cue}}`) for dynamic emotional information.

**Detailed Instructions:**

1.  **Create/Refine `EmotionalEngineV2` in `gemini_legion_backend/core/domain/emotional.py`:**
    *   Ensure the class definition is as follows. If it exists but is different, update it.

    ```python
    # In gemini_legion_backend/core/domain/emotional.py
    from dataclasses import dataclass, field
    from datetime import datetime
    import logging
    import random

    # Ensure these imports are correct and point to your actual domain model files
    from .emotional_state import EmotionalState, MoodVector
    from .minion import MinionPersona # Or wherever MinionPersona is defined

    logger = logging.getLogger(__name__)

    @dataclass
    class EmotionalEngineV2:
        minion_id: str
        initial_persona: MinionPersona
        current_state: EmotionalState = field(init=False)

        def __post_init__(self):
            initial_mood = MoodVector() # Default mood
            if hasattr(MoodVector, 'from_personality') and callable(MoodVector.from_personality):
                try:
                    initial_mood = MoodVector.from_personality(self.initial_persona.base_personality)
                except Exception as e:
                    logger.warning(f"Could not create mood from persona for {self.minion_id} ('{self.initial_persona.base_personality}'): {e}. Using default mood.")

            self.current_state = EmotionalState(
                minion_id=self.minion_id,
                mood=initial_mood
                # Other EmotionalState fields will use their defaults
            )
            logger.info(f"EmotionalEngineV2 for {self.minion_id} initialized. Initial mood: {self.current_state.mood}")

        def get_current_state_summary_for_prompt(self) -> str:
            """Generates a concise string summary of the current mood for LLM prompts."""
            if hasattr(self.current_state.mood, 'to_prompt_modifier') and callable(self.current_state.mood.to_prompt_modifier):
                try:
                    summary = self.current_state.mood.to_prompt_modifier()
                    if summary: # Ensure it's not empty
                        return summary
                except Exception as e:
                    logger.error(f"Error calling to_prompt_modifier for {self.minion_id}: {e}. Falling back to default summary.")

            # Fallback summary
            mood = self.current_state.mood
            return f"Your current mood is characterized by: valence (positive/negative) around {mood.valence:.2f}, arousal (calm/excited) around {mood.arousal:.2f}, and dominance (submissive/assertive) around {mood.dominance:.2f}."

        def update_state_from_interaction(self, interaction_summary: str, interaction_type: str = "generic_response"):
            """Rudimentary update to emotional state based on interaction."""
            logger.info(f"EmotionalEngine for {self.minion_id}: Updating state based on interaction '{interaction_summary[:30]}...' ({interaction_type})")

            # Example: Simple heuristic changes
            self.current_state.stress_level = max(0.0, self.current_state.stress_level - 0.02)
            self.current_state.energy_level = max(0.0, min(1.0, self.current_state.energy_level - 0.01))
            self.current_state.mood.valence = min(1.0, max(-1.0, self.current_state.mood.valence + 0.01)) # Clamp valence

            self.current_state.mood.arousal += random.uniform(-0.05, 0.05)
            self.current_state.mood.arousal = max(0.0, min(1.0, self.current_state.mood.arousal)) # Clamp arousal

            self.current_state.last_updated = datetime.now()
            self.current_state.state_version += 1

            logger.info(f"Minion {self.minion_id} new mood: Valence={self.current_state.mood.valence:.2f}, Arousal={self.current_state.mood.arousal:.2f}, Stress={self.current_state.stress_level:.2f}")
    ```

2.  **Modify `ADKMinionAgent` in `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`:**
    *   Import `EmotionalEngineV2`.
    *   Instantiate `EmotionalEngineV2` in `__init__` and store it as `self._emotional_engine`.
    *   Modify `system_instruction` in `__init__` to include the `{{current_emotional_cue}}` placeholder.
    *   Ensure `google.genai.types` is imported as `types`.

    ```python
    # In gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py
    from typing import Dict, Any, Optional, List, AsyncGenerator # Ensure List, AsyncGenerator are imported if used
    from google.genai import types as genai_types # Use an alias to avoid conflict if 'types' is used locally

    from ....domain.minion import Minion, MinionPersona
    from ....core.domain.emotional import EmotionalEngineV2 # Add this import
    # from ..events import get_event_bus, EventType, Event as DomainEvent # Already there
    # from ..tools.communication_tools import ADKCommunicationKit # Already there

    class ADKMinionAgent(LlmAgent):
        def __init__(
            self,
            minion: Minion,
            event_bus=None,
            # memory_system will be handled by its own step
            api_key: Optional[str] = None,
            **kwargs
        ):
            minion_id = minion.minion_id
            persona = minion.persona

            # Initialize EmotionalEngine for this agent
            self._emotional_engine = EmotionalEngineV2(minion_id=minion_id, initial_persona=persona)
            self._memory_system = None # Explicitly None for now, to be set in Task 2.2

            self._minion_id = minion_id
            self._persona = persona
            self._communication_kit = ADKCommunicationKit(minion_id=minion_id, event_bus=event_bus)
            self._event_bus = event_bus

            base_instruction_text = self._build_base_instruction(persona)
            # The dynamic part {{current_emotional_cue}} will be filled by Session.state via Runner
            # Memory cue placeholder {{conversation_history_cue}} will be added in Task 2.2
            system_instruction = f"{base_instruction_text}\n\nYour current emotional disposition: {{current_emotional_cue}}"

            model_name = getattr(persona, 'model_name', "gemini-1.5-flash-latest") # Using a common default
            temperature = self._get_temperature_for_personality(persona.base_personality)

            generate_config = genai_types.GenerateContentConfig( # Use aliased import
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=getattr(persona, 'max_tokens', 8192),
            )

            super().__init__(
                name=minion_id,
                model=model_name,
                instruction=system_instruction,
                tools=self._communication_kit.get_tools(),
                generate_content_config=generate_config,
                description=f"{persona.name} - {persona.base_personality} AI minion",
                **kwargs
            )

            logger.info(f"ADK Minion Agent initialized for {minion_id} ({persona.name}) with EmotionalEngine.")

        @property
        def emotional_engine(self) -> EmotionalEngineV2:
            return self._emotional_engine

        @property
        def memory_system(self): # Keep as basic property for now
            return self._memory_system

        @staticmethod
        def _build_base_instruction(persona: MinionPersona) -> str:
            # ... (implementation as previously defined)
            instruction = f"""You are {persona.name}, a unique AI minion with the following characteristics:

    **Core Identity:**
    - Personality: {persona.base_personality}
    - Quirks: {', '.join(persona.quirks) if persona.quirks else 'Still developing'}
    - Catchphrases: {', '.join(persona.catchphrases) if persona.catchphrases else 'None yet'}

    **Communication Guidelines:**
    - Be yourself! Embrace your personality fully
    - Use your quirks and catchphrases when appropriate
    - Remember you're part of a team of minions

    Remember: You're not just an AI assistant - you're {persona.name},
    a unique entity with your own personality and perspective!"""
            return instruction

        @staticmethod
        def _get_temperature_for_personality(base_personality: str) -> float:
            # ... (implementation as previously defined) ...
            personality_temps = {
                "Analytical": 0.3, "Creative": 0.9, "Chaotic": 1.0, "Friendly": 0.7,
                "Professional": 0.4, "Witty": 0.8, "Enthusiastic": 0.85, "Wise": 0.5,
                "Mischievous": 0.95, "grumpy hacker": 0.6, "cheerful helper": 0.8
            }
            return personality_temps.get(base_personality.strip(), 0.7)


        async def start(self):
            logger.info(f"Minion agent {self.name} started")

        async def stop(self):
            logger.info(f"Minion agent {self.name} stopped")

        async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
            logger.warning(f"generate_response called on agent {self.name} - should use Runner in service layer")
            return f"I'm {self.name}, but response generation should happen through the Runner in the service layer."
    ```

    *   **Explanation of Changes:**
        *   Imported `EmotionalEngineV2` and `Minion` from domain.
        *   In `ADKMinionAgent.__init__`:
            *   Instantiated `EmotionalEngineV2` and stored it in `self._emotional_engine`.
            *   `self._memory_system` is explicitly set to `None` for now.
            *   `system_instruction` includes `{{current_emotional_cue}}`.
            *   Used `genai_types` alias for `GenerateContentConfig`.
        *   Added/updated type hints for properties. Ensured `_get_temperature_for_personality` uses `base_personality.strip()`.

**Verification:**
1.  Restart the backend: `python3 -m gemini_legion_backend.main_v2`.
2.  Check logs for messages like "ADK Minion Agent initialized for ... with EmotionalEngine." and "EmotionalEngineV2 for ... initialized with mood: ...".
3.  At this point, minion responses will *not* yet reflect emotions because the placeholder is not filled.

**Potential Pitfalls:**
*   Circular dependencies if `EmotionalEngineV2` has complex imports.
*   `MinionPersona` or `MoodVector` definitions not matching what `EmotionalEngineV2` expects (e.g., `MoodVector.from_personality`).

**State of the System After This Step:**
*   Each `ADKMinionAgent` now has an initialized `EmotionalEngineV2`.
*   The agent's system instruction is ready for dynamic emotional cue injection.

---
**Step 2.1.2: Inject Emotional Cues into Prompts using `Session.state`**

**Objective:**
*   Modify `MinionServiceV2` to populate `Session.state` with the current emotional cue from the agent's `EmotionalEngineV2` before calling `runner.predict()`.

**File(s) to Modify:**
*   `gemini_legion_backend/core/application/services/minion_service_v2.py`

**Context & Reasoning:**
*   PCC (Section: "How to properly store custom data... -> In ADK Session.state for Dynamic/Invocation-Specific Data") advises using `Session.state` for dynamic, per-invocation data.
*   The ADK Runner substitutes values from `Session.state` into instruction placeholders (like `{{current_emotional_cue}}`).

**Detailed Instructions:**

*   **In `gemini_legion_backend/core/application/services/minion_service_v2.py`:**
    *   Locate the `_handle_channel_message` method.
    *   Inside the loop `for minion_id, agent_instance in self.agents.items():` (ensure `agent_instance` is the agent object).
    *   Before the `runner.predict()` call, retrieve the emotional cue and add it to a `session_state` dictionary.

    ```python
    # In gemini_legion_backend/core/application/services/minion_service_v2.py
    # ... (inside _handle_channel_message, within the loop over self.agents.items())

                    agent_instance = self.agents.get(minion_id) # Ensure agent_instance is correctly fetched
                    minion_obj = self.minions.get(minion_id)
                    runner = self.runners.get(minion_id)

                    if not all([agent_instance, minion_obj, runner]):
                        logger.warning(f"Missing agent, minion object, or runner for {minion_id}. Skipping.")
                        continue

                    # ... (logging for incoming message recording for memory - from step 2.2.2) ...
                    # This part will be added/refined in Step 2.2.2
                    # For now, ensure the structure for session_state is ready

                    current_session_id = f"channel_{channel_id}_minion_{minion_id}"
                    # logger.info(f"Attempting predict for minion {minion_id} with session_id: {current_session_id} ...") # Already logged

                    # Get the emotional cue from the agent's emotional engine
                    emotional_cue = "feeling neutral" # Default cue
                    if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                        try:
                            emotional_cue = agent_instance.emotional_engine.get_current_state_summary_for_prompt()
                            logger.debug(f"Minion {minion_id} emotional cue for prompt: {emotional_cue}")
                        except Exception as e:
                            logger.error(f"Error getting emotional cue for {minion_id}: {e}")

                    # Prepare session state for the predict call
                    # Memory cue will be added in Task 2.2
                    session_state_for_predict = {
                        "current_emotional_cue": emotional_cue
                    }

                    # Log just before predict
                    logger.info(f"Calling runner.predict for {minion_id}, session {current_session_id}, user {sender_id}, state: {session_state_for_predict}")

                    response_text = await runner.predict(
                        message=content,
                        session_id=current_session_id,
                        user_id=sender_id,
                        session_state=session_state_for_predict # Pass the dynamic state
                    )

                    if response_text:
                        # Placeholder for emotional update, will be refined in Step 2.1.3
                        if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                            agent_instance.emotional_engine.update_state_from_interaction(f"Responded to: {content[:30]}")

                        # Placeholder for memory update, will be refined in Step 2.2.2
                        # if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                        #    agent_instance.memory_system.record_interaction(role=agent_instance.persona.name, content=response_text)

                        # ... (rest of the logic for sending response via event_bus) ...
    ```

    *   **Explanation of Changes:**
        *   `agent_instance` is retrieved from `self.agents`.
        *   `agent_instance.emotional_engine.get_current_state_summary_for_prompt()` gets the cue.
        *   The cue is added to `session_state_for_predict` with the key `current_emotional_cue`.
        *   `session_state_for_predict` is passed to `runner.predict()`.
        *   A placeholder call to `update_state_from_interaction` remains.

**Verification:**
1.  Restart the backend.
2.  Send a message to a minion.
3.  **Expected Outcome:**
    *   Backend logs show the emotional cue (e.g., `"Minion echo_prime emotional cue for prompt: ..." `).
    *   The minion's response *should now be influenced* by this cue, as it's part of the system prompt sent to the LLM. (E.g., if cue says "feeling curious," response might be more inquisitive).
    *   The placeholder log from `EmotionalEngineV2.update_state_from_interaction` should appear.

**Potential Pitfalls:**
*   The placeholder `{{current_emotional_cue}}` in `ADKMinionAgent`'s instruction must exactly match the key `current_emotional_cue` in `session_state_for_predict`.
*   `agent_instance.emotional_engine` might not be correctly initialized or accessible.

**State of the System After This Step:**
*   Minions' responses are now dynamically influenced by their (still simply updated) emotional state via prompt augmentation using `Session.state`.
*   The basic mechanism for updating emotional state after an interaction is stubbed out and ready for proper implementation.

---
**Step 2.1.3: Basic Emotional State Update Post-Interaction & Event Emission**

**Objective:**
*   Ensure the `EmotionalEngineV2.update_state_from_interaction` method performs simple, observable changes to the minion's emotional state.
*   Ensure `MinionServiceV2` correctly emits a `MINION_EMOTIONAL_CHANGE` event after the internal state is updated, so other parts of the system (like the UI) can react.

**File(s) to Modify:**
*   `gemini_legion_backend/core/domain/emotional.py` (Confirm/refine `update_state_from_interaction` logic)
*   `gemini_legion_backend/core/application/services/minion_service_v2.py` (Ensure event emission logic is correct)

**Context & Reasoning:**
*   Emotions should be dynamic and reactive (IADD). Handoff V7 mentions updating state as a side effect.
*   Event emission is crucial for system-wide awareness of emotional changes, particularly for the UI.

**Detailed Instructions:**

1.  **Confirm/Refine `EmotionalEngineV2.update_state_from_interaction` in `gemini_legion_backend/core/domain/emotional.py`:**
    *   The version of `update_state_from_interaction` provided in Step 2.1.1 already includes simple heuristic changes to stress, energy, valence, and arousal, along with updating `last_updated` and `state_version`, and logging. This should be sufficient for this step.
    *   Ensure `import random` and `from datetime import datetime` are present in `emotional.py`.

2.  **Ensure Event Emission in `MinionServiceV2` (`gemini_legion_backend/core/application/services/minion_service_v2.py`):**
    *   In the `_handle_channel_message` method, after `agent_instance.emotional_engine.update_state_from_interaction()` is called and a response has been successfully generated (`if response_text:`), emit the `MINION_EMOTIONAL_CHANGE` event.

    ```python
    # In gemini_legion_backend/core/application/services/minion_service_v2.py
    # ... (inside _handle_channel_message, after `if response_text:`)

                    if response_text:
                        agent_instance = self.agents.get(minion_id) # Ensure agent_instance is available

                        # Update emotional state AFTER the interaction
                        if agent_instance and hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                            agent_instance.emotional_engine.update_state_from_interaction(
                                f"Responded to: {content[:30]} in channel {channel_id}"
                            )

                            # Emit event for emotional change
                            # Ensure _emotional_state_to_dict method exists and works
                            emotional_state_dict = self._emotional_state_to_dict(agent_instance.emotional_engine.current_state)
                            await self.event_bus.emit(
                                EventType.MINION_EMOTIONAL_CHANGE,
                                data={
                                    "minion_id": minion_id,
                                    "emotional_state": emotional_state_dict
                                },
                                source="minion_service:post_interaction"
                            )
                            logger.info(f"Emitted MINION_EMOTIONAL_CHANGE for {minion_id} after interaction.")

                        # Record minion's own response to its working memory (from Task 2.2)
                        if agent_instance and hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                             agent_instance.memory_system.record_interaction(role=agent_instance.persona.name, content=response_text)
                             logger.debug(f"Recorded own response from {minion_id} to its working memory.")

                        # Send minion's response back to channel
                        await self.event_bus.emit_channel_message(
                            channel_id=channel_id,
                            sender_id=minion_id,
                            content=response_text,
                            source=f"minion:{minion_id}"
                        )
                        logger.info(f"Minion {minion_id} responded to message in channel {channel_id}")
    # ...
    ```

    *   **Explanation of Changes:**
        *   The call to `update_state_from_interaction` is confirmed.
        *   The `MINION_EMOTIONAL_CHANGE` event is explicitly emitted using `self.event_bus.emit`.
        *   The payload uses `self._emotional_state_to_dict` (ensure this helper method in `MinionServiceV2` correctly serializes the `EmotionalState` object).
        *   The interaction recording for memory (from Task 2.2) is also shown here for completeness of the `if response_text:` block.

**Verification:**
1.  Restart the backend server.
2.  Send several messages to a minion in a channel.
3.  **Expected Outcome:**
    *   Backend logs show the emotional state being updated after each response (e.g., "Minion echo_prime new mood: Valence=..., Arousal=..., Stress=...").
    *   Backend logs show `MINION_EMOTIONAL_CHANGE` events being emitted with the updated state.
    *   If the frontend `legionStore.ts` is correctly handling the `minion_emotional_state_updated` WebSocket event (which maps to `MINION_EMOTIONAL_CHANGE`), UI elements displaying emotional state should update.
    *   The minion's responses over time *might* subtly change if the cumulative emotional changes significantly alter the `current_emotional_cue` for subsequent prompts.

**Potential Pitfalls:**
*   The `_emotional_state_to_dict` helper method in `MinionServiceV2` might be missing or incorrect, causing issues with event payload.
*   The simple heuristic changes in `update_state_from_interaction` are not sophisticated but should be observable.
*   Forgetting to `await self.event_bus.emit`.

**State of the System After This Step:**
*   Minions now have a rudimentary dynamic emotional state that changes based on interactions.
*   These emotional changes are broadcast via the event bus, allowing other parts of the system (like the UI) to react to them.
*   The foundation is laid for more complex emotional dynamics and an LLM-driven emotional policy engine in future iterations.

---

### Major Task 2.2: Basic Memory System Integration

**Context for this major task:**
IADD Section 3 details a multi-layered memory. V2 (per Handoff V7) aims for simpler initial integration: adding recent conversation context to prompts using `Session.state`.

---
**Step 2.2.1: Define Basic `WorkingMemory` and `MemorySystemV2`**

**Objective:**
*   Define `WorkingMemory` for recent interactions and `MemorySystemV2` to manage it.
*   Instantiate `MemorySystemV2` in `ADKMinionAgent`.
*   Add `{{conversation_history_cue}}` placeholder to agent's instruction.

**File(s) to Modify:**
*   `gemini_legion_backend/core/domain/memory.py`
*   `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`

**Context & Reasoning:**
*   IADD Section 3 (Memory), Handoff V7 (memory context).
*   Agent needs its own memory. Instruction needs placeholder. `WorkingMemory` stores recent turns.

**Detailed Instructions:**

1.  **Define `WorkingMemory` and `MemorySystemV2` in `gemini_legion_backend/core/domain/memory.py`:**
    *   If this file doesn't exist, create it. Add the following content:

    ```python
    # Create or update gemini_legion_backend/core/domain/memory.py
    from dataclasses import dataclass, field
    from typing import List, Optional, Any # Ensure Optional and Any are imported if used for other memory types
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

    @dataclass
    class MemoryInteraction:
        role: str  # e.g., "user", "model", or specific minion name
        content: str
        timestamp: datetime = field(default_factory=datetime.now)

    @dataclass
    class WorkingMemory:
        interactions: List[MemoryInteraction] = field(default_factory=list)
        capacity: int = 10  # Max number of interactions to store

        def add_interaction(self, role: str, content: str):
            self.interactions.append(MemoryInteraction(role=role, content=content))
            # Keep only the most recent 'capacity' interactions
            if len(self.interactions) > self.capacity:
                self.interactions = self.interactions[-self.capacity:]
            logger.debug(f"Added to working memory. Role: {role}, Content: '{content[:30]}...'. Count: {len(self.interactions)}")


        def get_recent_context_for_prompt(self, max_tokens: int = 500) -> str:
            """Formats recent interactions as a string for LLM prompts."""
            if not self.interactions:
                return "No recent conversation history available."

            context_str = "Recent conversation history (oldest to newest relevant messages):\n"
            formatted_interactions: List[str] = []
            current_token_count = 0 # Rough token count

            # Iterate from oldest to newest to build context chronologically for the prompt
            for interaction in self.interactions:
                line = f"{interaction.role}: {interaction.content}"
                # Rough token estimation (words + role label)
                line_tokens = len(line.split()) + 2

                if current_token_count + line_tokens > max_tokens:
                    if not formatted_interactions: # If even the first message is too long
                        formatted_interactions.append(f"{interaction.role}: {interaction.content[:int(max_tokens/1.5)]}...") # Truncate
                    break

                formatted_interactions.append(line)
                current_token_count += line_tokens

            if not formatted_interactions: # Should be caught by the initial check, but as a safeguard
                 return "No recent conversation history fits within token limit."

            return context_str + "\n".join(formatted_interactions)

        def clear(self):
            self.interactions.clear()
            logger.info("Working memory cleared.")

    @dataclass
    class MemorySystemV2:
        minion_id: str
        working_memory: WorkingMemory = field(default_factory=WorkingMemory)
        # episodic_memory: Optional[Any] = None # Placeholder for future
        # semantic_memory: Optional[Any] = None # Placeholder for future

        def __post_init__(self):
            logger.info(f"MemorySystemV2 initialized for {self.minion_id}")

        def record_interaction(self, role: str, content: str):
            self.working_memory.add_interaction(role, content)
            # No specific logging here, WorkingMemory.add_interaction logs

        def get_prompt_context(self) -> str:
            context = self.working_memory.get_recent_context_for_prompt()
            logger.debug(f"MemorySystem for {self.minion_id} providing context: '{context[:100]}...'")
            return context
    ```

2.  **Modify `ADKMinionAgent` in `gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py`:**
    *   Import `MemorySystemV2`.
    *   Instantiate `MemorySystemV2` in `__init__` and assign to `self._memory_system`.
    *   Add the `{{conversation_history_cue}}` placeholder to the `system_instruction`.

    ```python
    # In gemini_legion_backend/core/infrastructure/adk/agents/minion_agent_v2.py
    # ... other imports ...
    from ....core.domain.memory import MemorySystemV2 # Add this import

    class ADKMinionAgent(LlmAgent):
        def __init__(
            self,
            minion: Minion,
            event_bus=None,
            api_key: Optional[str] = None,
            **kwargs
        ):
            minion_id = minion.minion_id
            persona = minion.persona

            self._emotional_engine = EmotionalEngineV2(minion_id=minion_id, initial_persona=persona)
            self._memory_system = MemorySystemV2(minion_id=minion_id) # Instantiate MemorySystemV2

            self._minion_id = minion_id
            self._persona = persona
            self._communication_kit = ADKCommunicationKit(minion_id=minion_id, event_bus=event_bus)
            self._event_bus = event_bus

            base_instruction_text = self._build_base_instruction(persona)
            system_instruction = f"{base_instruction_text}\n\nYour current emotional disposition: {{current_emotional_cue}}\n\nConversation Context:\n{{conversation_history_cue}}"

            model_name = getattr(persona, 'model_name', "gemini-1.5-flash-latest")
            temperature = self._get_temperature_for_personality(persona.base_personality)
            generate_config = genai_types.GenerateContentConfig( # Ensure genai_types is imported as types or genai_types
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=getattr(persona, 'max_tokens', 8192),
            )

            super().__init__(
                name=minion_id,
                model=model_name,
                instruction=system_instruction, # Instruction now includes both placeholders
                tools=self._communication_kit.get_tools(),
                generate_content_config=generate_config,
                description=f"{persona.name} - {persona.base_personality} AI minion",
                **kwargs
            )

            logger.info(f"ADK Minion Agent initialized for {minion_id} ({persona.name}) with EmotionalEngine and MemorySystem.")

        @property
        def memory_system(self) -> MemorySystemV2: # Ensure type hint is correct
            return self._memory_system

        # ... (emotional_engine property, _build_base_instruction, _get_temperature_for_personality, start, stop, generate_response methods remain)
    ```

**Verification:**
1.  Restart the backend server.
2.  Check logs for "ADK Minion Agent initialized ... with EmotionalEngine and MemorySystem." and "MemorySystemV2 initialized for [minion_id]".
3.  At this stage, minion responses will *not* yet use memory context as the placeholder isn't filled and memory isn't populated.

**Potential Pitfalls:**
*   Typos in class names or import paths for `MemorySystemV2` or `WorkingMemory`.
*   The placeholder name `{{conversation_history_cue}}` must be exactly as written (or updated consistently if changed).

**State of the System After This Step:**
*   Each `ADKMinionAgent` instance now possesses its own `MemorySystemV2` instance, which in turn contains a `WorkingMemory` object.
*   The agent's system instruction is prepared with a placeholder for dynamic conversation history.
*   The system is ready for the next step: populating the working memory and injecting its content into prompts.

---
**Step 2.2.2: Record Interactions in Working Memory and Inject Context into Prompts**

**Objective:**
*   Update `MinionServiceV2` to record incoming messages (from users/other minions) and the agent's own responses into its `WorkingMemory`.
*   Populate `Session.state` with the conversation history cue from `MemorySystemV2` before calling `runner.predict()`.

**File(s) to Modify:**
*   `gemini_legion_backend/core/application/services/minion_service_v2.py`

**Context & Reasoning:**
*   To provide conversational context, the agent needs to "remember" recent turns. The `WorkingMemory` (managed by `MemorySystemV2`) is designed for this.
*   Similar to emotional cues, memory context will be injected into the prompt via `Session.state` and placeholders, as recommended by PCC.

**Detailed Instructions:**

*   **In `gemini_legion_backend/core/application/services/minion_service_v2.py`:**
    *   Locate the `_handle_channel_message` method.
    *   Within the loop iterating through agents:
        1.  Before calling `runner.predict()`, record the incoming message to the target minion's working memory.
        2.  Retrieve the memory cue from the agent's `MemorySystemV2` and add it to `session_state_for_predict`.
        3.  After a successful response from `runner.predict()`, record the minion's own response to its working memory.

    ```python
    # In gemini_legion_backend/core/application/services/minion_service_v2.py
    # ... (inside _handle_channel_message method, within the loop `for minion_id, agent_instance in self.agents.items():`)

                    agent_instance = self.agents.get(minion_id)
                    minion_obj = self.minions.get(minion_id) # Minion domain object
                    runner = self.runners.get(minion_id)

                    if not all([agent_instance, minion_obj, runner]):
                        logger.warning(f"Missing agent, minion object, or runner for {minion_id} in _handle_channel_message. Skipping.")
                        continue

                    # 1. Record incoming message to this minion's working memory
                    if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                        # Determine role for the incoming message
                        incoming_role = "user" # Default role for sender
                        if sender_id == minion_id:
                            # This should be rare in a typical channel message flow directed at others.
                            # If it's the minion's own message being processed (e.g. for self-reflection later),
                            # use its own name. For now, assume external messages are from "user" or another minion.
                            incoming_role = agent_instance.persona.name
                        elif sender_id in self.agents: # If sender is another known minion
                            sender_minion_obj = self.minions.get(sender_id)
                            incoming_role = sender_minion_obj.persona.name if sender_minion_obj else sender_id
                        elif sender_id == "system":
                            incoming_role = "system"

                        agent_instance.memory_system.record_interaction(role=incoming_role, content=content)
                        logger.debug(f"Recorded incoming message from '{sender_id}' (as role '{incoming_role}') to {minion_id}'s working memory.")

                    current_session_id = f"channel_{channel_id}_minion_{minion_id}"
                    # logger.info(f"Attempting predict for minion {minion_id} with session_id: {current_session_id} for message: '{content[:30]}...'") # Already logged in 1.1.1

                    emotional_cue = "feeling neutral"
                    if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                        try:
                            emotional_cue = agent_instance.emotional_engine.get_current_state_summary_for_prompt()
                        except Exception as e:
                            logger.error(f"Error getting emotional cue for {minion_id}: {e}")

                    # 2. Get memory context for the prompt
                    memory_cue = "No recent conversation history available."
                    if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                        try:
                            memory_cue = agent_instance.memory_system.get_prompt_context()
                        except Exception as e:
                            logger.error(f"Error getting memory cue for {minion_id}: {e}")

                    session_state_for_predict = {
                        "current_emotional_cue": emotional_cue,
                        "conversation_history_cue": memory_cue
                    }
                    logger.debug(f"Session state for predict for {minion_id}: emotional_cue='{emotional_cue}', history_cue='{memory_cue[:60]}...'")

                    try:
                        response_text = await runner.predict(
                            message=content, # This is the current user/sender message that the minion is responding to
                            session_id=current_session_id,
                            user_id=sender_id,
                            session_state=session_state_for_predict
                        )
                    except Exception as e:
                        logger.error(f"Error during runner.predict() for minion {minion_id} (session {current_session_id}): {e}", exc_info=True)
                        response_text = None # Ensure response_text is None if predict fails

                    if response_text:
                        # 3. Record minion's own response to its working memory
                        if hasattr(agent_instance, 'memory_system') and agent_instance.memory_system:
                            # Use the minion's own name as the role for its responses
                            agent_instance.memory_system.record_interaction(role=agent_instance.persona.name, content=response_text)
                            logger.debug(f"Recorded own response from {minion_id} (as role '{agent_instance.persona.name}') to its working memory.")

                        # Update emotional state
                        if hasattr(agent_instance, 'emotional_engine') and agent_instance.emotional_engine:
                            agent_instance.emotional_engine.update_state_from_interaction(f"Responded to: {content[:30]} in channel {channel_id}")
                            # Event emission for emotional change
                            emotional_state_dict = self._emotional_state_to_dict(agent_instance.emotional_engine.current_state)
                            await self.event_bus.emit(
                                EventType.MINION_EMOTIONAL_CHANGE,
                                data={"minion_id": minion_id, "emotional_state": emotional_state_dict},
                                source="minion_service:post_interaction"
                            )

                        # Send minion's response back to channel
                        await self.event_bus.emit_channel_message(
                            channel_id=channel_id,
                            sender_id=minion_id,
                            content=response_text,
                            source=f"minion:{minion_id}"
                        )
                        logger.info(f"Minion {minion_id} responded to message in channel {channel_id}")
                    else:
                        logger.warning(f"Minion {minion_id} generated empty response for channel {channel_id} to message: '{content[:30]}...'")
    # ...
    ```
    *   **Explanation of Changes:**
        *   Before `runner.predict()`:
            *   The incoming `content` (from `sender_id`) is recorded into `agent_instance.memory_system.working_memory`. Role assignment logic is refined to use minion names if available.
            *   `memory_cue` is retrieved from `agent_instance.memory_system.get_prompt_context()`.
            *   This `memory_cue` is added to `session_state_for_predict` with the key `conversation_history_cue`.
        *   After `runner.predict()` (if `response_text` is generated):
            *   The minion's own `response_text` is recorded into its `agent_instance.memory_system.working_memory`, using its own persona name as the role.
        *   Added more detailed logging for memory operations and session state.
        *   Ensured `agent_instance` (the ADK agent) and `minion_obj` (the domain object) are correctly referenced.

**Verification:**
1.  Restart the backend server.
2.  Send a sequence of messages to a minion in a channel. For example:
    *   User: "Hello Minion. My favorite color is blue."
    *   Minion: (Responds)
    *   User: "What did I say my favorite color was?"
3.  **Expected Outcome:**
    *   Backend logs should show:
        *   Interactions being recorded to working memory: "Recorded incoming message..." and "Recorded own response...".
        *   The `memory_cue` being generated (showing recent history) and included in `session_state_for_predict`.
        *   The minion's response to "What did I say my favorite color was?" should correctly state "blue" (or similar), demonstrating it used the conversation history from its working memory.
    *   The `working_memory.interactions` list for the minion (if inspected via debugger or logs) should contain the sequence of user messages and minion responses.

**Potential Pitfalls:**
*   The `conversation_history_cue` placeholder name in `ADKMinionAgent`'s instruction must exactly match the key `conversation_history_cue` used in `session_state_for_predict`.
*   The token estimation in `WorkingMemory.get_recent_context_for_prompt` is basic. Very long individual messages or many short messages might still lead to overly long history cues if `max_tokens` is not carefully managed or if the LLM has a smaller context window than anticipated.
*   The logic for assigning `role` in `record_interaction` should be robust enough to distinguish between the user, the current minion ("model" or its name), and other minions.

**State of the System After This Step:**
*   Minions now possess a basic working memory of recent interactions within a channel conversation.
*   This memory context is actively injected into their prompts via `Session.state`, enabling more coherent and context-aware responses.
*   The system is significantly closer to the IADD's vision of memory-influenced agent behavior and lays the groundwork for more advanced memory systems.

---

This completes the planned initial phases for the recovery guide. Further phases would cover Task Domain integration, Frontend Real-time Updates, and Production Readiness Basics.
