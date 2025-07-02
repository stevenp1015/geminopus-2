client:495 [vite] connecting...
client:618 [vite] connected.
chunk-GKJBSOWT.js?v=0e2f9e72:21551 Download the React DevTools for a better development experience: https://reactjs.org/link/react-devtools
channelApi.ts:13 [channelApi] list: Fetching channels...
socket__io-client.js?v=ab81cf54:1035 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: WebSocket is closed before the connection is established.
doClose @ socket__io-client.js?v=ab81cf54:1035
channelApi.ts:13 [channelApi] list: Fetching channels...
useWebSocket.ts:30 [useWebSocket] WebSocket instance available, attempting to set up listeners.
useWebSocket.ts:58 [useWebSocket] Registered wildcard event listener (onAny).
channelApi.ts:18 [channelApi] list: Raw response status: 200
legionStore.ts:329 [LegionStore] Minions result from minionApi.list(): Array(1)
legionStore.ts:330 [LegionStore] Is minionsResult an array?: true
channelApi.ts:23 [channelApi] list: Raw response text: {"channels":[{"id":"task_coordination","name":"Task Coordination","description":"Task assignment and coordination","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.372634"},{"id":"announcements","name":"Announcements","description":"Important system announcements","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368532"},{"id":"general","name":"General","description":"General discussion for all Minions","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368144"}],"total":3}
channelApi.ts:29 [channelApi] list: Processed data: Object
channelApi.ts:31 [channelApi] list: Returning channels: Array(3)
legionStore.ts:329 [LegionStore] Minions result from minionApi.list(): Array(1)
legionStore.ts:330 [LegionStore] Is minionsResult an array?: true
channelApi.ts:18 [channelApi] list: Raw response status: 200
useWebSocket.ts:52 [useWebSocket] WILDCARD EVENT: Name: 'connected', Data: Array(1)
legionStore.ts:162 WebSocket connected
channelApi.ts:23 [channelApi] list: Raw response text: {"channels":[{"id":"task_coordination","name":"Task Coordination","description":"Task assignment and coordination","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.372634"},{"id":"announcements","name":"Announcements","description":"Important system announcements","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368532"},{"id":"general","name":"General","description":"General discussion for all Minions","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368144"}],"total":3}
channelApi.ts:29 [channelApi] list: Processed data: Object
channelApi.ts:31 [channelApi] list: Returning channels: Array(3)
useWebSocket.ts:52 [useWebSocket] WILDCARD EVENT: Name: 'minion_spawned', Data: [{…}]
legionStore.ts:78 [LegionStore] addMinion called with: {minion_id: 'rude_boy_9be20c92', status: 'active', creation_date: '2025-07-02T15:33:48.987424', persona: {…}, emotional_state: {…}}
legionStore.ts:356 Fetch finished loading: POST "http://localhost:8000/api/v2/minions/spawn".
spawnMinion @ legionStore.ts:356
handleSubmit @ SpawnMinionModal.tsx:45
callCallback2 @ chunk-GKJBSOWT.js?v=0e2f9e72:3674
invokeGuardedCallbackDev @ chunk-GKJBSOWT.js?v=0e2f9e72:3699
invokeGuardedCallback @ chunk-GKJBSOWT.js?v=0e2f9e72:3733
invokeGuardedCallbackAndCatchFirstError @ chunk-GKJBSOWT.js?v=0e2f9e72:3736
executeDispatch @ chunk-GKJBSOWT.js?v=0e2f9e72:7014
processDispatchQueueItemsInOrder @ chunk-GKJBSOWT.js?v=0e2f9e72:7034
processDispatchQueue @ chunk-GKJBSOWT.js?v=0e2f9e72:7043
dispatchEventsForPlugins @ chunk-GKJBSOWT.js?v=0e2f9e72:7051
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:7174
batchedUpdates$1 @ chunk-GKJBSOWT.js?v=0e2f9e72:18913
batchedUpdates @ chunk-GKJBSOWT.js?v=0e2f9e72:3579
dispatchEventForPluginEventSystem @ chunk-GKJBSOWT.js?v=0e2f9e72:7173
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ chunk-GKJBSOWT.js?v=0e2f9e72:5478
dispatchEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5472
dispatchDiscreteEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5449
minionApi.ts:68 Fetch finished loading: PUT "http://localhost:8000/api/v2/minions/rude_boy_9be20c92/persona".
updatePersona @ minionApi.ts:68
handleSavePersona @ MinionDetail.tsx:46
handleSave @ MinionConfig.tsx:51
callCallback2 @ chunk-GKJBSOWT.js?v=0e2f9e72:3674
invokeGuardedCallbackDev @ chunk-GKJBSOWT.js?v=0e2f9e72:3699
invokeGuardedCallback @ chunk-GKJBSOWT.js?v=0e2f9e72:3733
invokeGuardedCallbackAndCatchFirstError @ chunk-GKJBSOWT.js?v=0e2f9e72:3736
executeDispatch @ chunk-GKJBSOWT.js?v=0e2f9e72:7014
processDispatchQueueItemsInOrder @ chunk-GKJBSOWT.js?v=0e2f9e72:7034
processDispatchQueue @ chunk-GKJBSOWT.js?v=0e2f9e72:7043
dispatchEventsForPlugins @ chunk-GKJBSOWT.js?v=0e2f9e72:7051
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:7174
batchedUpdates$1 @ chunk-GKJBSOWT.js?v=0e2f9e72:18913
batchedUpdates @ chunk-GKJBSOWT.js?v=0e2f9e72:3579
dispatchEventForPluginEventSystem @ chunk-GKJBSOWT.js?v=0e2f9e72:7173
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ chunk-GKJBSOWT.js?v=0e2f9e72:5478
dispatchEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5472
dispatchDiscreteEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5449
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: task_coordination
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel task_coordination: []
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: task_coordination
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel task_coordination: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
 [ChatInterface] Rendering. SelectedChannelId: task_coordination
 [ChatInterface] Derived channelMessages for channel task_coordination: []
 [ChatInterface] Rendering. SelectedChannelId: task_coordination
 [ChatInterface] Derived channelMessages for channel task_coordination: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
legionStore.ts:329 [LegionStore] Minions result from minionApi.list(): (2) [{…}, {…}]
legionStore.ts:330 [LegionStore] Is minionsResult an array?: true
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: task_coordination
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel task_coordination: []
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: task_coordination
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel task_coordination: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: task_coordination
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 3): (3) [{…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
minionApi.ts:13 Fetch finished loading: GET "http://localhost:8000/api/v2/minions/".
list @ minionApi.ts:13
fetchMinions @ legionStore.ts:328
(anonymous) @ CreateChannelModal.tsx:32
commitHookEffectListMount @ chunk-GKJBSOWT.js?v=0e2f9e72:16915
commitPassiveMountOnFiber @ chunk-GKJBSOWT.js?v=0e2f9e72:18156
commitPassiveMountEffects_complete @ chunk-GKJBSOWT.js?v=0e2f9e72:18129
commitPassiveMountEffects_begin @ chunk-GKJBSOWT.js?v=0e2f9e72:18119
commitPassiveMountEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:18109
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19490
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
commitRootImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19416
commitRoot @ chunk-GKJBSOWT.js?v=0e2f9e72:19277
performSyncWorkOnRoot @ chunk-GKJBSOWT.js?v=0e2f9e72:18895
flushSyncCallbacks @ chunk-GKJBSOWT.js?v=0e2f9e72:9119
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:18627
chatStore.ts:169 [ChatStore] createChannel CALLED. Name: "help", Type: "public", Members: (2) ['echo_prime', 'rude_boy_9be20c92']
channelApi.ts:58 [channelApi] create CALLED. Data: {name: 'help', channel_type: 'public', members: Array(2)}
channelApi.ts:66 [channelApi] create: Attempting to POST to create channel. Payload: {name: 'help', description: undefined, channel_type: 'public', members: Array(2)}
 [useWebSocket] WILDCARD EVENT: Name: 'channel_event', Data: [{…}]
 [useWebSocket] WILDCARD EVENT: Name: 'channel_event', Data: [{…}]
 [useWebSocket] WILDCARD EVENT: Name: 'channel_event', Data: [{…}]
 [ChatStore] addChannel CALLED. Channel object received: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …}
 [ChatStore] addChannel - Members in received channel: (3) ['api_user', 'echo_prime', 'rude_boy_9be20c92']
 [ChatStore] addChannel - Channels state AFTER update: {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}}
 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
channelApi.ts:67 Fetch finished loading: POST "http://localhost:8000/api/v2/channels/".
create @ channelApi.ts:67
createChannel @ chatStore.ts:171
handleSubmit @ CreateChannelModal.tsx:49
callCallback2 @ chunk-GKJBSOWT.js?v=0e2f9e72:3674
invokeGuardedCallbackDev @ chunk-GKJBSOWT.js?v=0e2f9e72:3699
invokeGuardedCallback @ chunk-GKJBSOWT.js?v=0e2f9e72:3733
invokeGuardedCallbackAndCatchFirstError @ chunk-GKJBSOWT.js?v=0e2f9e72:3736
executeDispatch @ chunk-GKJBSOWT.js?v=0e2f9e72:7014
processDispatchQueueItemsInOrder @ chunk-GKJBSOWT.js?v=0e2f9e72:7034
processDispatchQueue @ chunk-GKJBSOWT.js?v=0e2f9e72:7043
dispatchEventsForPlugins @ chunk-GKJBSOWT.js?v=0e2f9e72:7051
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:7174
batchedUpdates$1 @ chunk-GKJBSOWT.js?v=0e2f9e72:18913
batchedUpdates @ chunk-GKJBSOWT.js?v=0e2f9e72:3579
dispatchEventForPluginEventSystem @ chunk-GKJBSOWT.js?v=0e2f9e72:7173
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ chunk-GKJBSOWT.js?v=0e2f9e72:5478
dispatchEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5472
dispatchDiscreteEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5449
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {task_coordination: {…}, announcements: {…}, general: {…}, 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageInput.tsx:40 [MessageInput] handleSend: Preparing to call sendChatMessage. Channel ID: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4, Sender ID: COMMANDER_PRIME, Message: "i love u"
chatStore.ts:189 [ChatStore] sendMessage CALLED. Channel ID: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4, Sender ID: COMMANDER_PRIME, Content: "i love u"
channelApi.ts:102 [channelApi] sendMessage: Attempting to POST to URL: http://localhost:8000/api/v2/channels/2a9648d9-5471-4b09-9c65-2c8c9d6c7db4/messages
channelApi.ts:103 Fetch finished loading: POST "http://localhost:8000/api/v2/channels/2a9648d9-5471-4b09-9c65-2c8c9d6c7db4/messages".
sendMessage @ channelApi.ts:103
sendMessage @ chatStore.ts:192
handleSend @ MessageInput.tsx:41
handleKeyDown @ MessageInput.tsx:59
callCallback2 @ chunk-GKJBSOWT.js?v=0e2f9e72:3674
invokeGuardedCallbackDev @ chunk-GKJBSOWT.js?v=0e2f9e72:3699
invokeGuardedCallback @ chunk-GKJBSOWT.js?v=0e2f9e72:3733
invokeGuardedCallbackAndCatchFirstError @ chunk-GKJBSOWT.js?v=0e2f9e72:3736
executeDispatch @ chunk-GKJBSOWT.js?v=0e2f9e72:7014
processDispatchQueueItemsInOrder @ chunk-GKJBSOWT.js?v=0e2f9e72:7034
processDispatchQueue @ chunk-GKJBSOWT.js?v=0e2f9e72:7043
dispatchEventsForPlugins @ chunk-GKJBSOWT.js?v=0e2f9e72:7051
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:7174
batchedUpdates$1 @ chunk-GKJBSOWT.js?v=0e2f9e72:18913
batchedUpdates @ chunk-GKJBSOWT.js?v=0e2f9e72:3579
dispatchEventForPluginEventSystem @ chunk-GKJBSOWT.js?v=0e2f9e72:7173
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ chunk-GKJBSOWT.js?v=0e2f9e72:5478
dispatchEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5472
dispatchDiscreteEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5449
client:495 [vite] connecting...
client:618 [vite] connected.
chunk-GKJBSOWT.js?v=0e2f9e72:21551 Download the React DevTools for a better development experience: https://reactjs.org/link/react-devtools
channelApi.ts:13 [channelApi] list: Fetching channels...
legionStore.ts:319 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: WebSocket is closed before the connection is established.
doClose @ socket__io-client.js?v=ab81cf54:1035
close @ socket__io-client.js?v=ab81cf54:511
_onClose @ socket__io-client.js?v=ab81cf54:1609
close @ socket__io-client.js?v=ab81cf54:1556
close @ socket__io-client.js?v=ab81cf54:1581
onclose @ socket__io-client.js?v=ab81cf54:3313
_close @ socket__io-client.js?v=ab81cf54:3291
_destroy @ socket__io-client.js?v=ab81cf54:3259
destroy @ socket__io-client.js?v=ab81cf54:2745
disconnect @ socket__io-client.js?v=ab81cf54:2767
disconnectWebSocket @ legionStore.ts:319
(anonymous) @ useWebSocket.ts:16
safelyCallDestroy @ chunk-GKJBSOWT.js?v=0e2f9e72:16748
commitHookEffectListUnmount @ chunk-GKJBSOWT.js?v=0e2f9e72:16875
invokePassiveEffectUnmountInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:18363
invokeEffectsInDev @ chunk-GKJBSOWT.js?v=0e2f9e72:19701
commitDoubleInvokeEffectsInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:19682
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19503
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:19328
workLoop @ chunk-GKJBSOWT.js?v=0e2f9e72:197
flushWork @ chunk-GKJBSOWT.js?v=0e2f9e72:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=0e2f9e72:384
channelApi.ts:13 [channelApi] list: Fetching channels...
useWebSocket.ts:30 [useWebSocket] WebSocket instance available, attempting to set up listeners.
useWebSocket.ts:58 [useWebSocket] Registered wildcard event listener (onAny).
channelApi.ts:18 [channelApi] list: Raw response status: 200
channelApi.ts:18 [channelApi] list: Raw response status: 200
channelApi.ts:23 [channelApi] list: Raw response text: {"channels":[{"id":"2a9648d9-5471-4b09-9c65-2c8c9d6c7db4","name":"help","description":"","type":"public","members":["api_user","echo_prime","rude_boy_9be20c92"],"created_at":"2025-07-02T15:34:09.977597"},{"id":"task_coordination","name":"Task Coordination","description":"Task assignment and coordination","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.372634"},{"id":"announcements","name":"Announcements","description":"Important system announcements","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368532"},{"id":"general","name":"General","description":"General discussion for all Minions","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368144"}],"total":4}
legionStore.ts:329 [LegionStore] Minions result from minionApi.list(): (2) [{…}, {…}]
legionStore.ts:330 [LegionStore] Is minionsResult an array?: true
Navigated to http://localhost:5173/
channelApi.ts:23 [channelApi] list: Raw response text: {"channels":[{"id":"2a9648d9-5471-4b09-9c65-2c8c9d6c7db4","name":"help","description":"","type":"public","members":["api_user","echo_prime","rude_boy_9be20c92"],"created_at":"2025-07-02T15:34:09.977597"},{"id":"task_coordination","name":"Task Coordination","description":"Task assignment and coordination","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.372634"},{"id":"announcements","name":"Announcements","description":"Important system announcements","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368532"},{"id":"general","name":"General","description":"General discussion for all Minions","type":"public","members":["system"],"created_at":"2025-07-02T15:33:13.368144"}],"total":4}
legionStore.ts:329 [LegionStore] Minions result from minionApi.list(): (2) [{…}, {…}]
legionStore.ts:330 [LegionStore] Is minionsResult an array?: true
channelApi.ts:29 [channelApi] list: Processed data: {channels: Array(4), total: 4}
channelApi.ts:31 [channelApi] list: Returning channels: (4) [{…}, {…}, {…}, {…}]
useWebSocket.ts:52 [useWebSocket] WILDCARD EVENT: Name: 'connected', Data: [{…}]
legionStore.ts:162 WebSocket connected
channelApi.ts:29 [channelApi] list: Processed data: {channels: Array(4), total: 4}
channelApi.ts:31 [channelApi] list: Returning channels: (4) [{…}, {…}, {…}, {…}]
channelApi.ts:14 Fetch finished loading: GET "http://localhost:8000/api/v2/channels/".
list @ channelApi.ts:14
fetchChannels @ chatStore.ts:141
(anonymous) @ App.tsx:19
commitHookEffectListMount @ chunk-GKJBSOWT.js?v=0e2f9e72:16915
commitPassiveMountOnFiber @ chunk-GKJBSOWT.js?v=0e2f9e72:18156
commitPassiveMountEffects_complete @ chunk-GKJBSOWT.js?v=0e2f9e72:18129
commitPassiveMountEffects_begin @ chunk-GKJBSOWT.js?v=0e2f9e72:18119
commitPassiveMountEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:18109
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19490
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:19328
workLoop @ chunk-GKJBSOWT.js?v=0e2f9e72:197
flushWork @ chunk-GKJBSOWT.js?v=0e2f9e72:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=0e2f9e72:384
minionApi.ts:13 Fetch finished loading: GET "http://localhost:8000/api/v2/minions/".
list @ minionApi.ts:13
fetchMinions @ legionStore.ts:328
(anonymous) @ App.tsx:18
commitHookEffectListMount @ chunk-GKJBSOWT.js?v=0e2f9e72:16915
commitPassiveMountOnFiber @ chunk-GKJBSOWT.js?v=0e2f9e72:18156
commitPassiveMountEffects_complete @ chunk-GKJBSOWT.js?v=0e2f9e72:18129
commitPassiveMountEffects_begin @ chunk-GKJBSOWT.js?v=0e2f9e72:18119
commitPassiveMountEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:18109
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19490
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:19328
workLoop @ chunk-GKJBSOWT.js?v=0e2f9e72:197
flushWork @ chunk-GKJBSOWT.js?v=0e2f9e72:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=0e2f9e72:384
channelApi.ts:14 Fetch finished loading: GET "http://localhost:8000/api/v2/channels/".
list @ channelApi.ts:14
fetchChannels @ chatStore.ts:141
(anonymous) @ App.tsx:19
commitHookEffectListMount @ chunk-GKJBSOWT.js?v=0e2f9e72:16915
invokePassiveEffectMountInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:18324
invokeEffectsInDev @ chunk-GKJBSOWT.js?v=0e2f9e72:19701
commitDoubleInvokeEffectsInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:19686
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19503
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:19328
workLoop @ chunk-GKJBSOWT.js?v=0e2f9e72:197
flushWork @ chunk-GKJBSOWT.js?v=0e2f9e72:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=0e2f9e72:384
minionApi.ts:13 Fetch finished loading: GET "http://localhost:8000/api/v2/minions/".
list @ minionApi.ts:13
fetchMinions @ legionStore.ts:328
(anonymous) @ App.tsx:18
commitHookEffectListMount @ chunk-GKJBSOWT.js?v=0e2f9e72:16915
invokePassiveEffectMountInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:18324
invokeEffectsInDev @ chunk-GKJBSOWT.js?v=0e2f9e72:19701
commitDoubleInvokeEffectsInDEV @ chunk-GKJBSOWT.js?v=0e2f9e72:19686
flushPassiveEffectsImpl @ chunk-GKJBSOWT.js?v=0e2f9e72:19503
flushPassiveEffects @ chunk-GKJBSOWT.js?v=0e2f9e72:19447
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:19328
workLoop @ chunk-GKJBSOWT.js?v=0e2f9e72:197
flushWork @ chunk-GKJBSOWT.js?v=0e2f9e72:176
performWorkUntilDeadline @ chunk-GKJBSOWT.js?v=0e2f9e72:384
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageInput.tsx:40 [MessageInput] handleSend: Preparing to call sendChatMessage. Channel ID: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4, Sender ID: COMMANDER_PRIME, Message: "come back"
chatStore.ts:189 [ChatStore] sendMessage CALLED. Channel ID: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4, Sender ID: COMMANDER_PRIME, Content: "come back"
channelApi.ts:102 [channelApi] sendMessage: Attempting to POST to URL: http://localhost:8000/api/v2/channels/2a9648d9-5471-4b09-9c65-2c8c9d6c7db4/messages
channelApi.ts:103 Fetch finished loading: POST "http://localhost:8000/api/v2/channels/2a9648d9-5471-4b09-9c65-2c8c9d6c7db4/messages".
sendMessage @ channelApi.ts:103
sendMessage @ chatStore.ts:192
handleSend @ MessageInput.tsx:41
handleKeyDown @ MessageInput.tsx:59
callCallback2 @ chunk-GKJBSOWT.js?v=0e2f9e72:3674
invokeGuardedCallbackDev @ chunk-GKJBSOWT.js?v=0e2f9e72:3699
invokeGuardedCallback @ chunk-GKJBSOWT.js?v=0e2f9e72:3733
invokeGuardedCallbackAndCatchFirstError @ chunk-GKJBSOWT.js?v=0e2f9e72:3736
executeDispatch @ chunk-GKJBSOWT.js?v=0e2f9e72:7014
processDispatchQueueItemsInOrder @ chunk-GKJBSOWT.js?v=0e2f9e72:7034
processDispatchQueue @ chunk-GKJBSOWT.js?v=0e2f9e72:7043
dispatchEventsForPlugins @ chunk-GKJBSOWT.js?v=0e2f9e72:7051
(anonymous) @ chunk-GKJBSOWT.js?v=0e2f9e72:7174
batchedUpdates$1 @ chunk-GKJBSOWT.js?v=0e2f9e72:18913
batchedUpdates @ chunk-GKJBSOWT.js?v=0e2f9e72:3579
dispatchEventForPluginEventSystem @ chunk-GKJBSOWT.js?v=0e2f9e72:7173
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ chunk-GKJBSOWT.js?v=0e2f9e72:5478
dispatchEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5472
dispatchDiscreteEvent @ chunk-GKJBSOWT.js?v=0e2f9e72:5449
legionStore.ts:167 WebSocket disconnected
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChatInterface.tsx:26 [ChatInterface] Rendering. SelectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChatInterface.tsx:33 [ChatInterface] Derived channelMessages for channel 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:12 [ChannelSidebar] Store values - channels: {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}} selectedChannelId: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:21 [ChannelSidebar] currentChannels (after fallback): {2a9648d9-5471-4b09-9c65-2c8c9d6c7db4: {…}, task_coordination: {…}, announcements: {…}, general: {…}}
ChannelSidebar.tsx:24 [ChannelSidebar] allChannelsFromStore (from Object.values): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:29 [ChannelSidebar] Filtered - publicChannels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:30 [ChannelSidebar] Filtered - privateChannels: []
ChannelSidebar.tsx:31 [ChannelSidebar] Filtered - directMessages: []
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:95 [ChannelSection: Public Channels] Props channels: (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:96 [ChannelSection: Public Channels] Filtered channels for render (length 4): (4) [{…}, {…}, {…}, {…}]
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} Using key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} Using key: task_coordination
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} Using key: announcements
ChannelSidebar.tsx:127 [ChannelSection: Public Channels] Mapping channel for ChannelItem: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} Using key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: '2a9648d9-5471-4b09-9c65-2c8c9d6c7db4', name: 'help', description: '', type: 'public', members: Array(3), …} ID for key: 2a9648d9-5471-4b09-9c65-2c8c9d6c7db4
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'task_coordination', name: 'Task Coordination', description: 'Task assignment and coordination', type: 'public', members: Array(1), …} ID for key: task_coordination
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'announcements', name: 'Announcements', description: 'Important system announcements', type: 'public', members: Array(1), …} ID for key: announcements
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:52 [ChannelItem] Rendering for channel: {id: 'general', name: 'General', description: 'General discussion for all Minions', type: 'public', members: Array(1), …} ID for key: general
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Private Channels] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Private Channels] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Private Channels] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
ChannelSidebar.tsx:95 [ChannelSection: Direct Messages] Props channels: []
ChannelSidebar.tsx:96 [ChannelSection: Direct Messages] Filtered channels for render (length 0): []
ChannelSidebar.tsx:103 [ChannelSection: Direct Messages] No channels in this section (even without search).
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
MessageList.tsx:15 [MessageList] Rendering. Received messages prop: []
MessageList.tsx:16 [MessageList] Number of messages received: 0
socket__io-client.js?v=ab81cf54:1059 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: 
createSocket @ socket__io-client.js?v=ab81cf54:1059
doOpen @ socket__io-client.js?v=ab81cf54:986
open @ socket__io-client.js?v=ab81cf54:503
_open @ socket__io-client.js?v=ab81cf54:1328
_SocketWithoutUpgrade @ socket__io-client.js?v=ab81cf54:1289
SocketWithUpgrade @ socket__io-client.js?v=ab81cf54:1633
Socket @ socket__io-client.js?v=ab81cf54:1759
open @ socket__io-client.js?v=ab81cf54:3125
(anonymous) @ socket__io-client.js?v=ab81cf54:3343
socket__io-client.js?v=ab81cf54:1059 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: 
createSocket @ socket__io-client.js?v=ab81cf54:1059
doOpen @ socket__io-client.js?v=ab81cf54:986
open @ socket__io-client.js?v=ab81cf54:503
_open @ socket__io-client.js?v=ab81cf54:1328
_SocketWithoutUpgrade @ socket__io-client.js?v=ab81cf54:1289
SocketWithUpgrade @ socket__io-client.js?v=ab81cf54:1633
Socket @ socket__io-client.js?v=ab81cf54:1759
open @ socket__io-client.js?v=ab81cf54:3125
(anonymous) @ socket__io-client.js?v=ab81cf54:3343
socket__io-client.js?v=ab81cf54:1059 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: 
createSocket @ socket__io-client.js?v=ab81cf54:1059
doOpen @ socket__io-client.js?v=ab81cf54:986
open @ socket__io-client.js?v=ab81cf54:503
_open @ socket__io-client.js?v=ab81cf54:1328
_SocketWithoutUpgrade @ socket__io-client.js?v=ab81cf54:1289
SocketWithUpgrade @ socket__io-client.js?v=ab81cf54:1633
Socket @ socket__io-client.js?v=ab81cf54:1759
open @ socket__io-client.js?v=ab81cf54:3125
(anonymous) @ socket__io-client.js?v=ab81cf54:3343
 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: 
createSocket @ socket__io-client.js:1059
doOpen @ socket__io-client.js:986
open @ socket__io-client.js:503
_open @ socket__io-client.js:1328
_SocketWithoutUpgrade @ socket__io-client.js:1289
SocketWithUpgrade @ socket__io-client.js:1633
Socket @ socket__io-client.js:1759
open @ socket__io-client.js:3125
(anonymous) @ socket__io-client.js:3343
 WebSocket connection to 'ws://localhost:8000/socket.io/?EIO=4&transport=websocket' failed: 
createSocket @ socket__io-client.js:1059
doOpen @ socket__io-client.js:986
open @ socket__io-client.js:503
_open @ socket__io-client.js:1328
_SocketWithoutUpgrade @ socket__io-client.js:1289
SocketWithUpgrade @ socket__io-client.js:1633
Socket @ socket__io-client.js:1759
open @ socket__io-client.js:3125
(anonymous) @ socket__io-client.js:3343
