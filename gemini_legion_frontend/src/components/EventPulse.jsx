import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing';

// The Neural Event Visualization - Where Events Become Art
const EventPulse = ({ events = [] }) => {
  const networkRef = useRef();
  const [neurons, setNeurons] = useState([]);
  const [connections, setConnections] = useState([]);
  
  // Initialize neural network
  useEffect(() => {
    const nodeCount = 50;
    const newNeurons = [];
    
    // Create neurons in 3D space
    for (let i = 0; i < nodeCount; i++) {
      newNeurons.push({
        id: i,
        position: [
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 10
        ],
        energy: Math.random(),
        type: ['channel', 'minion', 'task', 'system'][Math.floor(Math.random() * 4)]
      });
    }
    
    // Create connections
    const newConnections = [];
    for (let i = 0; i < nodeCount * 2; i++) {
      const from = Math.floor(Math.random() * nodeCount);
      const to = Math.floor(Math.random() * nodeCount);
      if (from !== to) {
        newConnections.push({ from, to, strength: Math.random() });
      }
    }
    
    setNeurons(newNeurons);
    setConnections(newConnections);
  }, []);
  
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 15], fov: 60 }}>
        <color attach="background" args={['#0a0e1a']} />
        <fog attach="fog" args={['#0a0e1a', 5, 30]} />
        
        <ambientLight intensity={0.1} />
        <pointLight position={[10, 10, 10]} intensity={0.5} color="#00fff0" />
        
        <NeuralNetwork neurons={neurons} connections={connections} events={events} />
        
        <EffectComposer>
          <Bloom 
            intensity={1.5}
            luminanceThreshold={0.2}
            luminanceSmoothing={0.9}
          />
          <ChromaticAberration offset={[0.001, 0.001]} />
        </EffectComposer>
      </Canvas>
      
      <EventLegend />
    </div>
  );
};

// The actual neural network mesh
const NeuralNetwork = ({ neurons, connections, events }) => {
  const meshRef = useRef();
  const pulseRefs = useRef([]);
  const time = useRef(0);
  
  useFrame((state, delta) => {
    time.current += delta;
    
    // Rotate the entire network slowly
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.1;
      meshRef.current.rotation.x = Math.sin(time.current * 0.2) * 0.1;
    }
    
    // Animate pulses along connections
    pulseRefs.current.forEach((pulse, i) => {
      if (pulse) {
        const progress = (time.current * 0.5 + i * 0.1) % 1;
        const connection = connections[i % connections.length];
        if (connection && neurons[connection.from] && neurons[connection.to]) {
          const from = neurons[connection.from].position;
          const to = neurons[connection.to].position;
          
          pulse.position.x = from[0] + (to[0] - from[0]) * progress;
          pulse.position.y = from[1] + (to[1] - from[1]) * progress;
          pulse.position.z = from[2] + (to[2] - from[2]) * progress;
          
          // Pulse size based on event activity
          const eventBoost = events.length > 0 ? 1.5 : 1;
          pulse.scale.setScalar((Math.sin(progress * Math.PI) * 0.3 + 0.1) * eventBoost);
        }
      }
    });
  });
  
  return (
    <group ref={meshRef}>
      {/* Render neurons */}
      {neurons.map((neuron, i) => (
        <Neuron key={i} {...neuron} />
      ))}
      
      {/* Render connections */}
      {connections.map((connection, i) => (
        <Connection 
          key={i}
          from={neurons[connection.from]}
          to={neurons[connection.to]}
          strength={connection.strength}
        />
      ))}
      
      {/* Render pulses */}
      {connections.slice(0, 20).map((_, i) => (
        <mesh key={i} ref={el => pulseRefs.current[i] = el}>
          <sphereGeometry args={[0.1, 8, 8]} />
          <meshBasicMaterial color="#00fff0" />
        </mesh>
      ))}
    </group>
  );
};

// Individual neuron component
const Neuron = ({ position, energy, type }) => {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  const colors = {
    channel: '#00fff0',
    minion: '#8000ff',
    task: '#ff00ff',
    system: '#00ff80'
  };
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      // Pulsing based on energy
      const scale = 0.2 + energy * 0.3 + (hovered ? 0.2 : 0) + 
                    Math.sin(state.clock.elapsedTime * 2 + position[0]) * 0.05;
      meshRef.current.scale.setScalar(scale);
      
      // Slight rotation
      meshRef.current.rotation.x += delta * energy;
      meshRef.current.rotation.y += delta * energy * 0.5;
    }
  });
  
  return (
    <mesh
      ref={meshRef}
      position={position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <icosahedronGeometry args={[1, 0]} />
      <meshPhongMaterial 
        color={colors[type] || '#ffffff'}
        emissive={colors[type] || '#ffffff'}
        emissiveIntensity={energy * 0.5}
        wireframe={hovered}
      />
    </mesh>
  );
};

// Connection lines between neurons
const Connection = ({ from, to, strength }) => {
  if (!from || !to) return null;
  
  const points = [
    new THREE.Vector3(...from.position),
    new THREE.Vector3(...to.position)
  ];
  
  const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
  
  return (
    <line>
      <bufferGeometry attach="geometry" {...lineGeometry} />
      <lineBasicMaterial 
        attach="material" 
        color="#00fff0"
        opacity={strength * 0.3}
        transparent
      />
    </line>
  );
};

// Event type legend
const EventLegend = () => (
  <div style={{
    position: 'absolute',
    bottom: '20px',
    left: '20px',
    background: 'rgba(10, 14, 26, 0.8)',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #00fff0',
    fontFamily: 'monospace',
    fontSize: '12px'
  }}>
    <div style={{ marginBottom: '10px', color: '#00fff0', fontWeight: 'bold' }}>
      NEURAL EVENT TYPES
    </div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      <div><span style={{ color: '#00fff0' }}>●</span> Channel Events</div>
      <div><span style={{ color: '#8000ff' }}>●</span> Minion Activity</div>
      <div><span style={{ color: '#ff00ff' }}>●</span> Task Processing</div>
      <div><span style={{ color: '#00ff80' }}>●</span> System Health</div>
    </div>
  </div>
);

export default EventPulse;
