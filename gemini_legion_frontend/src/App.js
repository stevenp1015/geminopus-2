import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './App.css';

// Quick and dirty but FUNCTIONAL frontend for V2
function App() {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState('general');
  const [messages, setMessages] = useState({});
  const [minions, setMinions] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  // Connect to V2 backend
  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      auth: { client_id: 'frontend-' + Date.now() }
    });

    newSocket.on('connect', () => {
      console.log('Connected to V2 backend!');
      setConnected(true);
      
      // Subscribe to general channel
      newSocket.emit('subscribe_channel', { channel_id: 'general' });
    });

    newSocket.on('message', (data) => {
      console.log('Received message:', data);
      const { channel_id, message } = data;
      
      setMessages(prev => ({
        ...prev,
        [channel_id]: [...(prev[channel_id] || []), message]
      }));
    });

    newSocket.on('minion_event', (data) => {
      console.log('Minion event:', data);
      if (data.type === 'minion_spawned') {
        loadMinions();
      }
    });

    setSocket(newSocket);

    // Load initial data
    loadChannels();
    loadMinions();

    return () => newSocket.close();
  }, []);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChannels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/channels/');
      const data = await response.json();
      setChannels(data.channels || []);
    } catch (error) {
      console.error('Failed to load channels:', error);
    }
  };

  const loadMinions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/minions/');
      const data = await response.json();
      setMinions(data.minions || []);
    } catch (error) {
      console.error('Failed to load minions:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v2/channels/${activeChannel}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: 'COMMANDER_PRIME',
          content: inputMessage
        })
      });

      if (response.ok) {
        setInputMessage('');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const spawnMinion = async () => {
    const names = ['Echo', 'Nova', 'Cipher', 'Quantum', 'Nebula', 'Flux'];
    const personalities = [
      'Enthusiastic and curious researcher',
      'Sarcastic but brilliant analyst', 
      'Cheerful chaos agent',
      'Philosophical deep thinker',
      'Hyperactive creative genius'
    ];

    const randomName = names[Math.floor(Math.random() * names.length)] + Math.floor(Math.random() * 1000);
    const randomPersonality = personalities[Math.floor(Math.random() * personalities.length)];

    try {
      const response = await fetch('http://localhost:8000/api/v2/minions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          minion_id: `minion_${Date.now()}`,
          name: randomName,
          base_personality: randomPersonality,
          personality_traits: ['curious', 'helpful', 'creative'],
          quirks: ['Uses lots of ellipses...', 'Gets excited about new topics'],
          response_style: 'medium',
          catchphrases: ['Fascinating!', 'Let me think...', 'Oh, interesting!']
        })
      });

      if (response.ok) {
        loadMinions();
      }
    } catch (error) {
      console.error('Failed to spawn minion:', error);
    }
  };

  return (
    <div className="App">
      <div className="header">
        <h1>Gemini Legion V2 - Minimal Functional UI</h1>
        <div className="status">
          {connected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>

      <div className="main-container">
        {/* Minions Panel */}
        <div className="minions-panel">
          <h2>Active Minions ({minions.length})</h2>
          <button onClick={spawnMinion} className="spawn-btn">
            Spawn New Minion
          </button>
          <div className="minions-list">
            {minions.map(minion => (
              <div key={minion.minion_id} className="minion-card">
                <div className="minion-name">{minion.name}</div>
                <div className="minion-personality">{minion.persona.base_personality}</div>
                <div className="minion-status">
                  Energy: {Math.round(minion.emotional_state.energy_level * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Panel */}
        <div className="chat-panel">
          <div className="channel-header">
            <h2>#{activeChannel}</h2>
          </div>
          
          <div className="messages-container">
            {(messages[activeChannel] || []).map((msg, index) => (
              <div key={index} className={`message ${msg.sender_id === 'COMMANDER_PRIME' ? 'commander' : 'minion'}`}>
                <div className="message-sender">{msg.sender_id}</div>
                <div className="message-content">{msg.content}</div>
                <div className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message..."
              className="message-input"
            />
            <button onClick={sendMessage} className="send-btn">Send</button>
          </div>
        </div>

        {/* Channels Panel */}
        <div className="channels-panel">
          <h2>Channels</h2>
          <div className="channels-list">
            {channels.map(channel => (
              <div
                key={channel.id}
                className={`channel-item ${channel.id === activeChannel ? 'active' : ''}`}
                onClick={() => {
                  setActiveChannel(channel.id);
                  socket?.emit('subscribe_channel', { channel_id: channel.id });
                }}
              >
                #{channel.name}
                <span className="member-count">{channel.members.length}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
