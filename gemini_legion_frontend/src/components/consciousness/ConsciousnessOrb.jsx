import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing';
import { animated, useSpring } from '@react-spring/three';
import { useGesture } from '@use-gesture/react';

/**
 * Consciousness Orb - The living visualization of a minion's mind
 * 
 * This isn't a profile picture. It's a window into digital consciousness.
 */
export const ConsciousnessOrb = ({ minion, size = 200 }) => {
  const meshRef = useRef();
  const [thoughts, setThoughts] = useState([]);
  const [emotionalField, setEmotionalField] = useState(0);
  
  // Generate thought particles based on working memory
  useEffect(() => {
    const thoughtParticles = minion.workingMemory.map((memory, i) => ({
      id: memory.id,
      position: [
        Math.sin(i * Math.PI / 3.5) * 2,
        Math.cos(i * Math.PI / 3.5) * 2,
        Math.sin(i * 0.5) * 1
      ],
      intensity: memory.relevance,
      color: getThoughtColor(memory.type)
    }));
    setThoughts(thoughtParticles);
  }, [minion.workingMemory]);

  // Emotional state drives the orb's behavior
  const emotionalPulse = useSpring({
    scale: 1 + minion.emotionalState.arousal * 0.3,
    intensity: minion.emotionalState.energy,
    turbulence: minion.emotionalState.stress,
    config: { mass: 1, tension: 120, friction: 14 }
  });

  // Custom shader for the consciousness effect
  const vertexShader = `
    uniform float time;
    uniform float turbulence;
    uniform vec3 emotionalColor;
    
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    // Noise functions
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    
    float noise(vec3 p) {
      vec3 a = floor(p);
      vec3 d = p - a;
      d = d * d * (3.0 - 2.0 * d);
      
      vec4 b = a.xxyy + vec4(0.0, 1.0, 0.0, 1.0);
      vec4 k1 = permute(b.xyxy);
      vec4 k2 = permute(k1.xyxy + b.zzww);
      
      vec4 c = k2 + a.zzzz;
      vec4 k3 = permute(c);
      vec4 k4 = permute(c + 1.0);
      
      vec4 o1 = fract(k3 * (1.0 / 41.0));
      vec4 o2 = fract(k4 * (1.0 / 41.0));
      
      vec4 o3 = o2 * d.z + o1 * (1.0 - d.z);
      vec2 o4 = o3.yw * d.x + o3.xz * (1.0 - d.x);
      
      return o4.y * d.y + o4.x * (1.0 - d.y);
    }
    
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      
      // Consciousness distortion
      vec3 pos = position;
      float noiseVal = noise(pos * 2.0 + time * 0.5) * turbulence;
      pos += normal * noiseVal * 0.2;
      
      // Thought influence
      pos += normal * sin(time * 2.0 + position.y * 3.0) * 0.05;
      
      vPosition = pos;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float time;
    uniform float intensity;
    uniform vec3 baseColor;
    uniform vec3 emotionalColor;
    uniform sampler2D thoughtTexture;
    
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    void main() {
      // Base consciousness glow
      vec3 viewDirection = normalize(cameraPosition - vPosition);
      float fresnel = pow(1.0 - dot(viewDirection, vNormal), 2.0);
      
      // Emotional color blending
      vec3 color = mix(baseColor, emotionalColor, intensity);
      
      // Thought patterns
      float thoughtPattern = sin(vUv.x * 20.0 + time) * cos(vUv.y * 20.0 - time);
      color += vec3(thoughtPattern * 0.1);
      
      // Synaptic flashes
      float flash = step(0.98, sin(time * 10.0 + vPosition.x * 50.0));
      color += vec3(flash * 0.5);
      
      // Final consciousness glow
      color = mix(color, vec3(1.0), fresnel * 0.6);
      
      gl_FragColor = vec4(color, 0.8 + fresnel * 0.2);
    }
  `;

  return (
    <div className="consciousness-orb-container" style={{ width: size, height: size }}>
      <Canvas camera={{ position: [0, 0, 5] }}>
        <ambientLight intensity={0.1} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        
        <animated.mesh
          ref={meshRef}
          scale={emotionalPulse.scale}
        >
          <sphereGeometry args={[2, 64, 64]} />
          <shaderMaterial
            uniforms={{
              time: { value: 0 },
              turbulence: { value: emotionalPulse.turbulence },
              intensity: { value: emotionalPulse.intensity },
              baseColor: { value: new THREE.Color(0x00fff0) },
              emotionalColor: { value: getEmotionalColor(minion.emotionalState) }
            }}
            vertexShader={vertexShader}
            fragmentShader={fragmentShader}
            transparent
            side={THREE.DoubleSide}
          />
        </animated.mesh>
        
        {/* Thought particles */}
        {thoughts.map(thought => (
          <ThoughtParticle key={thought.id} {...thought} />
        ))}
        
        <EffectComposer>
          <Bloom luminanceThreshold={0.1} luminanceSmoothing={0.9} intensity={2} />
          <ChromaticAberration offset={[0.001, 0.001]} />
        </EffectComposer>
        
        <OrbController meshRef={meshRef} />
      </Canvas>
    </div>
  );
};

/**
 * Thought Particle - Individual thoughts orbiting consciousness
 */
const ThoughtParticle = ({ position, intensity, color }) => {
  const meshRef = useRef();
  const [pulse] = useState(() => Math.random() * Math.PI * 2);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
      meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime + pulse) * 0.2);
    }
  });
  
  return (
    <mesh ref={meshRef} position={position}>
      <icosahedronGeometry args={[0.1 * intensity, 0]} />
      <meshBasicMaterial color={color} transparent opacity={0.8} />
    </mesh>
  );
};

/**
 * Orb Controller - Handles interaction and animation
 */
const OrbController = ({ meshRef }) => {
  const { camera } = useThree();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.material.uniforms.time.value = state.clock.elapsedTime;
    }
  });
  
  const bind = useGesture({
    onDrag: ({ movement: [mx, my] }) => {
      if (meshRef.current) {
        meshRef.current.rotation.y = mx * 0.01;
        meshRef.current.rotation.x = my * 0.01;
      }
    },
    onPinch: ({ offset: [scale] }) => {
      camera.position.z = 5 / scale;
    }
  });
  
  return <primitive object={camera} {...bind()} />;
};

// Helper functions
const getThoughtColor = (type) => {
  const colors = {
    memory: '#00ff80',
    task: '#0080ff',
    emotion: '#ff00ff',
    communication: '#00fff0'
  };
  return colors[type] || '#ffffff';
};

const getEmotionalColor = (emotionalState) => {
  const { valence, arousal, stress } = emotionalState;
  const r = Math.floor((1 + valence) * 127.5);
  const g = Math.floor((1 - stress) * 255);
  const b = Math.floor((1 + arousal) * 127.5);
  return new THREE.Color(`rgb(${r}, ${g}, ${b})`);
};

export default ConsciousnessOrb;