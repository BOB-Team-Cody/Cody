import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { Node3D, NodeData } from '@/types';

interface CodeNodeProps {
  node: Node3D;
  isSelected: boolean;
  onClick: (node: NodeData) => void;
}

const CodeNode: React.FC<CodeNodeProps> = ({ node, isSelected, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  
  // Create geometry based on node type
  const geometry = React.useMemo(() => {
    const scale = node.scale || 1;
    
    switch (node.type) {
      case 'class':
        return new THREE.BoxGeometry(scale * 2, scale * 2, scale * 2);
      case 'function':
        return new THREE.SphereGeometry(scale * 1.2, 16, 12);
      case 'module':
        return new THREE.CylinderGeometry(scale * 1, scale * 1.2, scale * 0.8, 8);
      default:
        return new THREE.TetrahedronGeometry(scale * 1.5);
    }
  }, [node.type, node.scale]);
  
  // Create material based on node properties
  const material = React.useMemo(() => {
    const baseColor = new THREE.Color(node.color);
    const emissiveColor = new THREE.Color(node.emissive);
    
    return new THREE.MeshPhongMaterial({
      color: baseColor,
      emissive: emissiveColor,
      transparent: true,
      opacity: node.opacity,
      shininess: 100,
    });
  }, [node.color, node.emissive, node.opacity]);
  
  // Animation frame
  useFrame((state) => {
    if (!meshRef.current) return;
    
    const mesh = meshRef.current;
    const time = state.clock.getElapsedTime();
    
    // Gentle floating animation
    if (node.type === 'class') {
      mesh.rotation.y += 0.01;
    } else {
      mesh.rotation.x = Math.sin(time * 0.5 + node.position[0] * 0.01) * 0.1;
      mesh.rotation.z = Math.cos(time * 0.3 + node.position[2] * 0.01) * 0.1;
    }
    
    // Pulsing effect for selected nodes
    if (isSelected) {
      const pulse = 1 + Math.sin(time * 4) * 0.1;
      mesh.scale.setScalar(pulse);
    } else if (hovered) {
      const hover = 1 + Math.sin(time * 6) * 0.05;
      mesh.scale.setScalar(hover);
    } else {
      mesh.scale.setScalar(1);
    }
    
    // Update material for selection/hover
    if (material instanceof THREE.MeshPhongMaterial) {
      if (isSelected) {
        material.emissive.setHex(0xffffff);
        material.emissiveIntensity = 0.3;
      } else if (hovered) {
        material.emissive.setHex(0x666666);
        material.emissiveIntensity = 0.2;
      } else {
        material.emissive.set(node.emissive);
        material.emissiveIntensity = 0.1;
      }
    }
  });
  
  // Handle click
  const handleClick = (event: any) => {
    event.stopPropagation();
    onClick(node);
  };
  
  // Handle hover
  const handlePointerOver = (event: any) => {
    event.stopPropagation();
    setHovered(true);
    document.body.style.cursor = 'pointer';
  };
  
  const handlePointerOut = (event: any) => {
    event.stopPropagation();
    setHovered(false);
    document.body.style.cursor = 'default';
  };
  
  // Label component
  const NodeLabel = () => {
    let labelClass = 'node-label';
    
    if (node.dead) {
      labelClass += ' dead-code';
    } else if ((node.callCount || 0) > 3) {
      labelClass += ' high-usage';
    } else if (node.type === 'class') {
      labelClass += ' class-type';
    } else if ((node.callCount || 0) === 0) {
      labelClass += ' unused';
    }
    
    return (
      <div className={labelClass}>
        {node.name}
        {node.callCount > 0 && (
          <span className="ml-1 text-xs opacity-75">
            ({node.callCount})
          </span>
        )}
      </div>
    );
  };
  
  return (
    <group position={node.position}>
      {/* Main mesh */}
      <mesh
        ref={meshRef}
        geometry={geometry}
        material={material}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        castShadow
        receiveShadow
      />
      
      {/* Node label */}
      <Html
        position={[0, (node.scale || 1) * 2.5, 0]}
        center
        distanceFactor={15}
        occlude
      >
        <NodeLabel />
      </Html>
      
      {/* Selection indicator */}
      {isSelected && (
        <mesh position={[0, 0, 0]}>
          <ringGeometry args={[(node.scale || 1) * 2.5, (node.scale || 1) * 3, 32]} />
          <meshBasicMaterial
            color="#ffffff"
            transparent
            opacity={0.6}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      
      {/* Dead code indicator */}
      {node.dead && (
        <Html
          position={[0, -(node.scale || 1) * 2, 0]}
          center
          distanceFactor={20}
        >
          <div className="text-red-400 text-lg animate-pulse">💀</div>
        </Html>
      )}
      
      {/* High usage indicator */}
      {(node.callCount || 0) > 5 && (
        <Html
          position={[0, -(node.scale || 1) * 2, 0]}
          center
          distanceFactor={20}
        >
          <div className="text-yellow-400 text-lg animate-bounce">🔥</div>
        </Html>
      )}
    </group>
  );
};

export default CodeNode;