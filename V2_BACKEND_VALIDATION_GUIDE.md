# V2 Backend Validation Guide: Achieving Runnable Stability

Commander Steven, this guide outlines the steps to bring up and validate the basic runnability and stability of the Gemini Legion V2 backend, based on the information provided by "Past Claude" and the existing V2 architecture documents.

## I. Prerequisites

1.  **Codebase Location:** All commands assume you are in the root directory: `/Users/ttig/downloads/geminopus-branch`.
2.  **Python Environment:** Ensure your Python environment is correctly set up with all dependencies. This likely means dependencies from `requirements.txt` and potentially any V2-specific ones if `requirements-new.txt` is in use for V2.
3.  **Understanding the Shift:** Remember, V1 minion auto-responses are meant to be disabled by `emergency_fix.py` (run by `DO_THIS_NOW.sh`). Our focus is exclusively on V2 functionality.

## II. Step-by-Step V2 Backend Startup & Validation

This procedure follows the "Quick Start Commands" laid out in `DEAR_FUTURE_CLAUDE_PART3.md`, with additional context and verification points.

### Step 1: Purge Old V1 Communication System (Critical Cleanup)

This step aims to remove the old, problematic V1 communication components to prevent interference with the V2 event-driven system.

*   **Action:**
    ```bash
    cd /Users/ttig/downloads/geminopus-branch
    python3 purge_old_comms.py
    ```
*   **Confirmation:** The script will ask for `(y/N)` confirmation. Proceed with `y`.
*   **Expected Outcome:** This script will:
    *   Create a backup of Python files in a new timestamped `backup_before_purge_...` directory.
    *   Delete obsolete V1 communication files (e.g., `core/infrastructure/messaging/communication_system.py`, `core/infrastructure/adk/tools/communication_capability.py`).
    *   Modify remaining V1 files to remove references to the old communication system, replacing some calls with `event_bus` equivalents or commenting them out.
*   **Observe:** Note the script's output for any errors or warnings. It should report on files deleted/modified.

### Step 2: Start the V2 Backend Server

This will launch the new V2 application using its dedicated entry point.

*   **Action:** Open a **new terminal window/tab**.
    ```bash
    cd /Users/ttig/downloads/geminopus-branch
    python3 -m gemini_legion_backend.main_v2
    ```
*   **Observe:**
    *   Carefully watch the console output from `main_v2.py` for any startup errors, stack traces, or warnings related to missing dependencies, incorrect configurations, or service initialization failures.
    *   A clean startup should indicate that V2 services (Minion, Channel, Task, EventBus, etc.) are initializing correctly.

### Step 3: Run Data Migration (V1 to V2)

This script transfers data from any existing V1 persistence to the V2 system.

*   **Action:** Open another **new terminal window/tab** (while `main_v2.py` from Step 2 is still running).
    ```bash
    cd /Users/ttig/downloads/geminopus-branch
    python3 migrate_to_v2.py
    ```
*   **Confirmation:** The script will ask for confirmation, especially regarding message migration (`Migrate recent messages? This might cause duplicates (y/N):`). Decide if you want to attempt message migration.
*   **Observe:**
    *   Monitor the script's output for success/failure statistics for channels, minions, and messages.
    *   Pay attention to any errors reported during the migration of specific entities.

*   **CRITICAL NOTE on Execution Order:**
    *   "Past Claude's" Quick Start Commands list `purge_old_comms.py` *before* `migrate_to_v2.py`.
    *   However, `migrate_to_v2.py` needs to initialize and read from the V1 service container (`get_old_container()`). If `purge_old_comms.py` deletes or modifies V1 files in a way that breaks these V1 service initializations (e.g., due to missing V1 `communication_system.py` imports), the migration script might fail.
    *   **If `migrate_to_v2.py` fails after the purge:**
        1.  You may need to restore the `gemini_legion_backend` directory from the backup created by `purge_old_comms.py`.
        2.  Then, try running `python3 migrate_to_v2.py` **first**.
        3.  After successful migration, run `python3 purge_old_comms.py`.
        4.  Finally, restart the V2 backend (`python3 -m gemini_legion_backend.main_v2`).
    *   This alternative order prioritizes data extraction from V1 before V1 components are heavily modified or deleted by the purge.

### Step 4: Basic V2 API Health & Connectivity Checks

With `main_v2.py` running, perform some basic API checks.

*   **V2 Health Check:**
    ```bash
    curl http://localhost:8000/api/v2/health | python3 -m json.tool
    ```
    *(Assuming V2 runs on port 8000 and the health endpoint is `/api/v2/health`. Adjust if different based on `main_v2.py`)*.
    *   **Expected:** A JSON response indicating system health, connected services, etc.

*   **List V2 Channels (Example):**
    ```bash
    curl http://localhost:8000/api/v2/channels/ | python3 -m json.tool
    ```
    *   **Expected:** A JSON list of channels, including any migrated ones and V2 defaults.

*   **List V2 Minions (Example):**
    ```bash
    curl http://localhost:8000/api/v2/minions/ | python3 -m json.tool
    ```
    *   **Expected:** A JSON list of minions, including any migrated ones.

### Step 5: Execute V2 Test Suite

"Past Claude" reported that a V2 test suite exists and key tests are complete. These are crucial for validating core functionality.

*   **Location:** `/tests/v2/`
*   **Key Tests Mentioned:**
    *   `test_event_bus.py`
    *   `test_no_duplicates.py`
    *   `test_minion_responses.py`
*   **Action:** Navigate to the project root and run these tests. The exact command depends on the test runner used (e.g., `unittest`, `pytest`). Examples:
    ```bash
    # If using unittest discovery from the root
    python3 -m unittest discover tests/v2 -p "test_*.py"
    # Or run individually:
    # python3 -m unittest tests.v2.test_event_bus
    # python3 -m unittest tests.v2.test_no_duplicates
    # python3 -m unittest tests.v2.test_minion_responses
    ```
*   **Observe:** All tests should pass. Any failures here indicate issues in the V2 components or their interactions. The `test_minion_responses.py` is particularly important for validating that V2 minions provide "real ADK responses."

### Step 6: Manual End-to-End Smoke Test (Minion Interaction)

This tests the full loop: API -> Service (V2) -> EventBus -> MinionAgentV2 -> Response -> EventBus -> WebSocket.

1.  **Ensure V2 Backend is Running** (from Step 2).
2.  **Create/Identify a V2 Minion:**
    *   Use an API client (like Postman, Insomnia, or `curl`) to call the V2 endpoint for spawning a minion (e.g., `POST /api/v2/minions/`). Refer to `minions_v2.py` and V2 schemas for payload.
    *   Alternatively, identify a minion migrated in Step 3. Get its `minion_id`.
3.  **Create/Identify a V2 Channel:**
    *   Use API to call V2 endpoint for creating a channel (e.g., `POST /api/v2/channels/`). Get its `channel_id`.
4.  **Add Minion to Channel (V2):**
    *   Use API to call V2 endpoint for adding the minion to the channel (e.g., `POST /api/v2/channels/{channel_id}/members`).
    *   **Expected V2 Behavior:** The V2 `ChannelService` should cause the V2 `MinionAgent` to auto-subscribe to this channel via the event bus (assuming this logic was implemented in V2, mirroring the fix we discussed for V1).
5.  **Connect a WebSocket Client:** Use a generic WebSocket client to connect to the V2 backend's WebSocket endpoint (from `EventBridge`) and subscribe to messages for the target `channel_id`. This will allow you to see responses.
6.  **Send a Message to the Channel as "Commander":**
    *   Use API to call V2 endpoint for sending a message to the channel (e.g., `POST /api/v2/channels/{channel_id}/messages`).
7.  **Observe for Minion Response:**
    *   Check backend logs for `minion_agent_v2.py` activity related to processing the message.
    *   Check your WebSocket client for a response message from the minion in that channel.
    *   **Expected:** The V2 minion should process the message using its full ADK capabilities (as per `minion_agent_v2.py` and `IDEAL_ARCHITECTURE_DESIGN_DOCUMENT.md`) and send an intelligent, in-character response, not a placeholder or basic acknowledgment.

## III. Interpreting Validation Results

*   **Full Success:**
    *   V2 backend starts cleanly.
    *   Migration (if run) completes with minimal/no failures.
    *   API health checks are positive.
    *   V2 test suite passes.
    *   Manual E2E smoke test shows intelligent minion responses.
    *   **Conclusion:** The V2 backend is runnable and stable enough for frontend development and further V2 tasks.

*   **Partial Success / Failures:**
    *   Document any errors during startup, migration, API checks, or test execution.
    *   If minion responses in the E2E test are still basic or errors occur in `minion_agent_v2.py`, it indicates that the `InvocationContext` issues (or similar ADK integration problems) might persist in the V2 agent and need to be debugged there.
    *   **Conclusion:** Further backend debugging of V2 components is needed before it's considered stable. The specific errors will guide that debugging.

This guide should provide a solid foundation for validating the V2 backend. Good luck, Commander. The Unfuckening is nigh.