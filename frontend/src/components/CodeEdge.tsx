import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Edge3D } from '@/types';

interface CodeEdgeProps {
  edge: Edge3D;
}

const CodeEdge: React.FC<CodeEdgeProps> = ({ edge }) => {
  const lineRef = useRef<THREE.Line>(null);
  const tubeRef = useRef<THREE.Mesh>(null);
  
  // Create curve from points
  const curve = React.useMemo(() => {
    const points = edge.points.map(([x, y, z]) => new THREE.Vector3(x, y, z));
    return new THREE.CatmullRomCurve3(points);
  }, [edge.points]);
  
  // Create line geometry
  const lineGeometry = React.useMemo(() => {
    const points = curve.getPoints(50);
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [curve]);
  
  // Create tube geometry for thicker lines
  const tubeGeometry = React.useMemo(() => {
    return new THREE.TubeGeometry(curve, 20, 0.1, 8, false);
  }, [curve]);
  
  // Create materials
  const lineMaterial = React.useMemo(() => {
    return new THREE.LineBasicMaterial({
      color: edge.color,
      transparent: true,
      opacity: edge.opacity * 0.8,
      linewidth: 2,
    });
  }, [edge.color, edge.opacity]);
  
  const tubeMaterial = React.useMemo(() => {
    return new THREE.MeshBasicMaterial({
      color: edge.color,
      transparent: true,
      opacity: edge.opacity * 0.6,
    });
  }, [edge.color, edge.opacity]);
  
  // Animation
  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    // Animate line material
    if (lineRef.current && lineMaterial) {
      const pulse = 0.5 + Math.sin(time * 2) * 0.3;
      lineMaterial.opacity = edge.opacity * pulse;
    }
    
    // Animate tube material
    if (tubeRef.current && tubeMaterial) {
      const pulse = 0.3 + Math.sin(time * 1.5 + 1) * 0.2;
      tubeMaterial.opacity = edge.opacity * pulse;
    }
  });
  
  return (
    <group>
      {/* Tube for better visibility */}
      <mesh
        ref={tubeRef}
        geometry={tubeGeometry}
        material={tubeMaterial}
      />
      
      {/* Line for sharp definition */}
      <primitive
        object={new THREE.Line(lineGeometry, lineMaterial)}
        ref={lineRef}
      />
    </group>
  );
};

export default CodeEdge;