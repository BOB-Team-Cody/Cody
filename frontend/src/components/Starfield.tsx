import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const Starfield: React.FC = () => {
  const starsRef = useRef<THREE.Points>(null);
  
  // Create star field
  const { geometry, material } = useMemo(() => {
    const starCount = 15000;
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);
    const sizes = new Float32Array(starCount);
    
    for (let i = 0; i < starCount; i++) {
      const i3 = i * 3;
      
      // Position - distribute in a large sphere
      const radius = 2000 + Math.random() * 1000;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi);
      
      // Color - various shades of blue and white
      const intensity = 0.5 + Math.random() * 0.5;
      const colorVariation = Math.random();
      
      if (colorVariation < 0.7) {
        // White stars
        colors[i3] = intensity;
        colors[i3 + 1] = intensity;
        colors[i3 + 2] = intensity;
      } else if (colorVariation < 0.9) {
        // Blue stars
        colors[i3] = intensity * 0.6;
        colors[i3 + 1] = intensity * 0.8;
        colors[i3 + 2] = intensity;
      } else {
        // Yellow/orange stars
        colors[i3] = intensity;
        colors[i3 + 1] = intensity * 0.9;
        colors[i3 + 2] = intensity * 0.6;
      }
      
      // Size variation
      sizes[i] = Math.random() * 2 + 0.5;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
      },
      vertexShader: `
        attribute float size;
        varying vec3 vColor;
        uniform float time;
        
        void main() {
          vColor = color;
          
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          
          // Add subtle twinkling by varying size
          float twinkle = sin(time * 2.0 + position.x * 0.01) * 0.3 + 0.7;
          
          gl_PointSize = size * twinkle * (300.0 / -mvPosition.z);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        
        void main() {
          // Create circular star shape
          vec2 center = gl_PointCoord - vec2(0.5);
          float dist = length(center);
          
          if (dist > 0.5) discard;
          
          // Soft glow effect
          float alpha = 1.0 - smoothstep(0.0, 0.5, dist);
          alpha = pow(alpha, 2.0);
          
          gl_FragColor = vec4(vColor, alpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      vertexColors: true,
    });
    
    return { geometry, material };
  }, []);
  
  // Animation
  useFrame((state) => {
    if (starsRef.current && material.uniforms) {
      // Update time uniform for twinkling
      material.uniforms.time.value = state.clock.getElapsedTime();
      
      // Subtle rotation
      starsRef.current.rotation.y += 0.0001;
      starsRef.current.rotation.x += 0.00005;
    }
  });
  
  return (
    <points
      ref={starsRef}
      geometry={geometry}
      material={material}
    />
  );
};

export default Starfield;