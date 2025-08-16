import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Edge3D } from '@/types';
import { useAppStore } from '@/hooks/useAppStore';

interface CodeEdgeProps {
  edge: Edge3D;
}

const CodeEdge: React.FC<CodeEdgeProps> = ({ edge }) => {
  const lineRef = useRef<THREE.Line>(null);
  const tubeRef = useRef<THREE.Mesh>(null);
  const arrowRef = useRef<THREE.Mesh>(null);
  const { layoutMode } = useAppStore();
  
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
  
  // Calculate tube radius based on call frequency
  const tubeRadius = React.useMemo(() => {
    const frequency = edge.frequency || 1;
    const baseRadius = 0.3;
    return baseRadius + Math.log(frequency + 1) * 0.2;
  }, [edge.frequency]);
  
  // Create tube geometry for thicker lines
  const tubeGeometry = React.useMemo(() => {
    return new THREE.TubeGeometry(curve, 20, tubeRadius, 8, false);
  }, [curve, tubeRadius]);
  
  // Create arrow geometry for direction indication - bigger in hierarchical mode
  const arrowGeometry = React.useMemo(() => {
    const isHierarchical = layoutMode === 'hierarchical';
    const sizeMultiplier = isHierarchical ? 2.5 : 1.5; // Larger arrows in hierarchical mode
    const heightMultiplier = isHierarchical ? 4 : 3;
    return new THREE.ConeGeometry(tubeRadius * sizeMultiplier, tubeRadius * heightMultiplier, 8);
  }, [tubeRadius, layoutMode]);
  
  // Calculate arrow position and rotation
  const arrowTransform = React.useMemo(() => {
    const t = 0.8; // Position arrow at 80% along the curve
    const point = curve.getPoint(t);
    const tangent = curve.getTangent(t).normalize();
    
    // Create rotation matrix to align arrow with curve direction
    const up = new THREE.Vector3(0, 1, 0);
    const axis = new THREE.Vector3().crossVectors(up, tangent).normalize();
    const angle = Math.acos(up.dot(tangent));
    
    return {
      position: point,
      rotation: new THREE.Quaternion().setFromAxisAngle(axis, angle)
    };
  }, [curve]);
  
  // Create materials
  const lineMaterial = React.useMemo(() => {
    const frequency = edge.frequency || 1;
    const lineWidth = Math.min(2 + Math.log(frequency + 1) * 2, 12); // Dynamic line width based on frequency
    
    return new THREE.LineBasicMaterial({
      color: edge.color,
      transparent: true,
      opacity: edge.opacity * 1.5,
      linewidth: lineWidth,
    });
  }, [edge.color, edge.opacity, edge.frequency]);
  
  const tubeMaterial = React.useMemo(() => {
    return new THREE.MeshBasicMaterial({
      color: edge.color,
      transparent: true,
      opacity: edge.opacity * 1.2,
    });
  }, [edge.color, edge.opacity]);
  
  const arrowMaterial = React.useMemo(() => {
    const isHierarchical = layoutMode === 'hierarchical';
    const opacityMultiplier = isHierarchical ? 2.0 : 1.5; // More opaque in hierarchical mode
    
    return new THREE.MeshBasicMaterial({
      color: edge.color,
      transparent: true,
      opacity: Math.min(edge.opacity * opacityMultiplier, 1.0),
    });
  }, [edge.color, edge.opacity, layoutMode]);
  
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
      
      {/* Direction arrow */}
      <mesh
        ref={arrowRef}
        geometry={arrowGeometry}
        material={arrowMaterial}
        position={arrowTransform.position}
        quaternion={arrowTransform.rotation}
      />
    </group>
  );
};

export default CodeEdge;