<CONSOLE>
Navigated to http://localhost:5173/
client:495 [vite] connecting...
client:618 [vite] connected.
legionStore.ts:274 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: WebSocket is closed before the connection is established.
doClose @ socket__io-client.js?v=104a2088:1035
close @ socket__io-client.js?v=104a2088:511
_onClose @ socket__io-client.js?v=104a2088:1609
close @ socket__io-client.js?v=104a2088:1556
close @ socket__io-client.js?v=104a2088:1581
onclose @ socket__io-client.js?v=104a2088:3313
_close @ socket__io-client.js?v=104a2088:3291
_destroy @ socket__io-client.js?v=104a2088:3259
destroy @ socket__io-client.js?v=104a2088:2745
disconnect @ socket__io-client.js?v=104a2088:2767
disconnectWebSocket @ legionStore.ts:274
(anonymous) @ useWebSocket.ts:14
safelyCallDestroy @ chunk-GKJBSOWT.js?v=104a2088:16748
commitHookEffectListUnmount @ chunk-GKJBSOWT.js?v=104a2088:16875
invokePassiveEffectUnmountInDEV @ chunk-GKJBSOWT.js?v=104a2088:18363
invokeEffectsInDev @ chunk-GKJBSOWT.js?v=104a2088:19701
commitDoubleInvokeEffectsInDEV @ chunk-GKJBSOWT.js?v=104a2088:19682
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=104a2088:19503
flushPassiveEffects @ chunk-GKJBSOWT.js?v=104a2088:19447
(anonymous) @ chunk-GKJBSOWT.js?v=104a2088:19328
workLoop @ chunk-GKJBSOWT.js?v=104a2088:197
flushWork @ chunk-GKJBSOWT.js?v=104a2088:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=104a2088:384Understand this warning
8Fetch finished loading: GET "<URL>".
legionStore.ts:284 [LegionStore] Minions result from minionApi.list(): []
legionStore.ts:285 [LegionStore] Is minionsResult an array?: true
legionStore.ts:284 [LegionStore] Minions result from minionApi.list(): []
legionStore.ts:285 [LegionStore] Is minionsResult an array?: true
legionStore.ts:130 WebSocket connected
Navigated to http://localhost:5173/
</CONSOLE>
    ---

<TERMINAL>
(.venv) (.venv) ttig@WIIP-Mac05 geminopus-branch % python -m gemini_legion_backend.main
/Users/ttig/Downloads/geminopus-branch/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:373: UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
  warnings.warn(message, UserWarning)
2025-06-01 22:30:45,747 - __main__ - INFO - Starting Gemini Legion Backend on 0.0.0.0:8000
INFO:     Will watch for changes in these directories: ['/Users/ttig/Downloads/geminopus-branch']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [84861] using WatchFiles
/Users/ttig/Downloads/geminopus-branch/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:373: UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
  warnings.warn(message, UserWarning)
2025-06-01 22:30:54,597 - watchfiles.main - INFO - 2 changes detected
INFO:     Started server process [84869]
INFO:     Waiting for application startup.
2025-06-01 22:30:54,728 - gemini_legion_backend.main - INFO - 🚀 Gemini Legion Backend starting...
2025-06-01 22:30:54,728 - gemini_legion_backend.core.dependencies - INFO - Initializing service container...
2025-06-01 22:30:54,729 - gemini_legion_backend.core.infrastructure.adk.tools.tool_integration - INFO - Initialized tools: 4 filesystem, 6 computer use, 8 web automation
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.minion_service - INFO - Starting Minion Service...
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.minion_service - INFO - Minion Service started successfully
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.task_service - INFO - Starting Task Service...
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.task_service - INFO - Loaded 0 active tasks
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.task_service - INFO - Task Service started successfully
2025-06-01 22:30:54,730 - gemini_legion_backend.core.application.services.channel_service - INFO - Starting Channel Service...
2025-06-01 22:30:54,731 - gemini_legion_backend.core.application.services.channel_service - INFO - Created channel: General (general)
2025-06-01 22:30:54,731 - gemini_legion_backend.core.application.services.channel_service - INFO - Created channel: Announcements (announcements)
2025-06-01 22:30:54,732 - gemini_legion_backend.core.application.services.channel_service - INFO - Created channel: Task Coordination (task_coordination)
2025-06-01 22:30:54,732 - gemini_legion_backend.core.application.services.channel_service - INFO - Loaded 0 active channels
2025-06-01 22:30:54,732 - gemini_legion_backend.core.application.services.channel_service - INFO - Channel Service started successfully
2025-06-01 22:30:54,732 - gemini_legion_backend.core.dependencies - INFO - Service container initialized successfully
2025-06-01 22:30:54,732 - gemini_legion_backend.api.websocket.connection_manager - INFO - Socket.IO server instance set in ConnectionManager
2025-06-01 22:30:54,732 - gemini_legion_backend.api.websocket.connection_manager - INFO - Services connected to WebSocket manager
2025-06-01 22:30:54,733 - gemini_legion_backend.main - INFO - ✅ Gemini Legion Backend initialized
INFO:     Application startup complete.
INFO:     ('127.0.0.1', 60104) - "WebSocket /socket.io/?EIO=4&transport=websocket" [accepted]
INFO:     connection open
INFO:     127.0.0.1:60107 - "OPTIONS /api/minions HTTP/1.1" 200 OK
INFO:     127.0.0.1:60108 - "OPTIONS /api/channels HTTP/1.1" 200 OK
INFO:     127.0.0.1:60110 - "OPTIONS /api/minions HTTP/1.1" 200 OK
INFO:     127.0.0.1:60107 - "GET /api/minions HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60112 - "OPTIONS /api/channels HTTP/1.1" 200 OK
INFO:     127.0.0.1:60115 - "GET /api/channels HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60107 - "GET /api/minions HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60115 - "GET /api/channels HTTP/1.1" 307 Temporary Redirect
INFO:     ('127.0.0.1', 60116) - "WebSocket /socket.io/?EIO=4&transport=websocket" [accepted]
INFO:     connection open
INFO:     connection closed
INFO:     127.0.0.1:60115 - "OPTIONS /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60107 - "OPTIONS /api/channels/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60112 - "OPTIONS /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60110 - "OPTIONS /api/channels/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60108 - "GET /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60115 - "GET /api/channels/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60108 - "GET /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60115 - "GET /api/channels/ HTTP/1.1" 200 OK
2025-06-01 22:31:22,726 - gemini_legion_backend.main - INFO - Socket.IO client connected: cBIB0ZwWoQ4a85JbAAAC
2025-06-01 22:31:22,727 - gemini_legion_backend.api.websocket.connection_manager - INFO - Client cBIB0ZwWoQ4a85JbAAAC (SID: cBIB0ZwWoQ4a85JbAAAC) connected. Total: 1
2025-06-01 22:31:31,556 - gemini_legion_backend.main - INFO - Socket.IO client disconnected: cBIB0ZwWoQ4a85JbAAAC
2025-06-01 22:31:31,556 - gemini_legion_backend.api.websocket.connection_manager - INFO - Client cBIB0ZwWoQ4a85JbAAAC (SID: cBIB0ZwWoQ4a85JbAAAC) disconnected. Total connections: 0
INFO:     connection closed
INFO:     127.0.0.1:60573 - "GET /api/minions HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60575 - "GET /api/minions HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60573 - "GET /api/channels HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:60573 - "GET /api/channels HTTP/1.1" 307 Temporary Redirect
INFO:     ('127.0.0.1', 60577) - "WebSocket /socket.io/?EIO=4&transport=websocket" [accepted]
INFO:     connection open
INFO:     127.0.0.1:60573 - "GET /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60575 - "GET /api/channels/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60573 - "GET /api/minions/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60575 - "GET /api/channels/ HTTP/1.1" 200 OK
2025-06-01 22:31:32,021 - gemini_legion_backend.main - INFO - Socket.IO client connected: gb3nSX5Pr8BwSLfUAAAE
2025-06-01 22:31:32,021 - gemini_legion_backend.api.websocket.connection_manager - INFO - Client gb3nSX5Pr8BwSLfUAAAE (SID: gb3nSX5Pr8BwSLfUAAAE) connected. Total: 1


</TERMINAL>