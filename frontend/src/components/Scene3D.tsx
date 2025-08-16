import React, { useRef, useMemo, useEffect, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { GraphDataResponse, NodeData } from '@/types';
import { VisualizationService } from '@/services/visualization';
import { useAppStore } from '@/hooks/useAppStore';
import CodeNode from './CodeNode';
import CodeEdge from './CodeEdge';
import Starfield from './Starfield';

interface Scene3DProps {
  graphData: GraphDataResponse | null;
  selectedNode: NodeData | null;
  onNodeClick: (node: NodeData) => void;
  autoRotate: boolean;
}

const Scene3D: React.FC<Scene3DProps> = ({
  graphData,
  selectedNode,
  onNodeClick,
  autoRotate,
}) => {
  const controlsRef = useRef<any>();
  const groupRef = useRef<THREE.Group>(null);
  const { camera } = useThree();
  const { layoutMode } = useAppStore();
  
  // Animation state for layout transitions
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [previousNodes3D, setPreviousNodes3D] = useState<any[]>([]);
  const [transitionProgress, setTransitionProgress] = useState(0);
  
  // Visualization service instance with layout mode
  const visualizationService = useMemo(() => {
    return new VisualizationService({ algorithm: layoutMode });
  }, [layoutMode]);
  
  // Process graph data into 3D format
  const { nodes3D, edges3D } = useMemo(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
      return { nodes3D: [], edges3D: [] };
    }
    
    console.log(`Processing graph data for 3D visualization with ${layoutMode} layout...`);
    return visualizationService.processGraphData(graphData.nodes, graphData.links || []);
  }, [graphData, visualizationService, layoutMode]);

  // Handle layout transitions with animation
  useEffect(() => {
    if (nodes3D.length > 0 && previousNodes3D.length > 0) {
      // Start transition animation
      setIsTransitioning(true);
      setTransitionProgress(0);
      
      let startTime: number | null = null;
      const animationDuration = 1500; // 1.5 seconds
      
      const animate = (time: number) => {
        if (startTime === null) startTime = time;
        const elapsed = time - startTime;
        const progress = Math.min(elapsed / animationDuration, 1);
        
        // Easing function (ease-out-cubic)
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        setTransitionProgress(easedProgress);
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setIsTransitioning(false);
          setPreviousNodes3D([]); // Clear previous positions
        }
      };
      
      requestAnimationFrame(animate);
    } else if (nodes3D.length > 0) {
      // Store current positions for future transitions
      setPreviousNodes3D([...nodes3D]);
    }
  }, [nodes3D]);

  // Calculate interpolated positions during transition
  const displayNodes3D = useMemo(() => {
    if (!isTransitioning || previousNodes3D.length === 0) {
      return nodes3D;
    }
    
    return nodes3D.map((node, index) => {
      const prevNode = previousNodes3D.find(p => p.id === node.id);
      if (!prevNode) return node;
      
      // Interpolate position
      const newPos = new THREE.Vector3(...node.position);
      const oldPos = new THREE.Vector3(...prevNode.position);
      const lerpedPos = oldPos.lerp(newPos, transitionProgress);
      
      return {
        ...node,
        position: [lerpedPos.x, lerpedPos.y, lerpedPos.z] as [number, number, number]
      };
    });
  }, [nodes3D, previousNodes3D, isTransitioning, transitionProgress]);
  
  // Calculate optimal camera position when data changes
  useEffect(() => {
    if (displayNodes3D.length > 0 && controlsRef.current) {
      const { position, target } = visualizationService.calculateCameraPosition(displayNodes3D);
      
      // Smoothly animate camera to optimal position
      const controls = controlsRef.current;
      const startPos = camera.position.clone();
      const startTarget = controls.target.clone();
      const targetPos = new THREE.Vector3(...position);
      const targetLookAt = new THREE.Vector3(...target);
      
      let progress = 0;
      const animate = () => {
        progress += 0.02;
        if (progress <= 1) {
          camera.position.lerpVectors(startPos, targetPos, progress);
          controls.target.lerpVectors(startTarget, targetLookAt, progress);
          controls.update();
          requestAnimationFrame(animate);
        }
      };
      
      // Delay animation to ensure scene is ready
      setTimeout(animate, 100);
    }
  }, [displayNodes3D, camera, visualizationService]);
  
  // Handle node selection
  useEffect(() => {
    if (selectedNode && controlsRef.current) {
      const selectedNode3D = displayNodes3D.find(n => n.id === selectedNode.id);
      if (selectedNode3D) {
        const targetPos = new THREE.Vector3(...selectedNode3D.position);
        const offset = new THREE.Vector3(0, 0, 50);
        targetPos.add(offset);
        
        // Animate camera to selected node
        const controls = controlsRef.current;
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const targetLookAt = new THREE.Vector3(...selectedNode3D.position);
        
        let progress = 0;
        const animate = () => {
          progress += 0.03;
          if (progress <= 1) {
            const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
            camera.position.lerpVectors(startPos, targetPos, eased);
            controls.target.lerpVectors(startTarget, targetLookAt, eased);
            controls.update();
            requestAnimationFrame(animate);
          }
        };
        animate();
      }
    }
  }, [selectedNode, displayNodes3D, camera]);
  
  // Auto-rotation animation
  useFrame((_state, delta) => {
    if (autoRotate && groupRef.current) {
      groupRef.current.rotation.y += delta * 0.1;
    }
  });
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (!controlsRef.current) return;
      
      const controls = controlsRef.current;
      
      switch (event.code) {
        case 'KeyR':
          if (!event.ctrlKey && !event.metaKey) {
            // Reset camera
            event.preventDefault();
            controls.reset();
          }
          break;
        case 'Space':
          // Toggle auto-rotate (handled by parent)
          event.preventDefault();
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);
  
  if (!graphData || displayNodes3D.length === 0) {
    return (
      <>
        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.05}
          minDistance={20}
          maxDistance={500}
          autoRotate={false}
        />
        
        <Starfield />
        
        <ambientLight intensity={0.3} />
        <directionalLight position={[50, 50, 50]} intensity={0.8} />
        
        <Html center>
          <div className="text-center text-gray-400 p-8 glassmorphism rounded-lg">
            <div className="text-6xl mb-4">🌌</div>
            <div className="text-xl font-semibold mb-2">Welcome to Code Weaver</div>
            <div className="text-sm">
              Analyze a Python project to see your code in 3D space
            </div>
          </div>
        </Html>
      </>
    );
  }
  
  return (
    <>
      {/* Camera Controls */}
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={500}
        autoRotate={false}
        mouseButtons={{
          LEFT: THREE.MOUSE.ROTATE,
          MIDDLE: THREE.MOUSE.DOLLY,
          RIGHT: THREE.MOUSE.PAN,
        }}
      />
      
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[50, 50, 50]}
        intensity={0.8}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <pointLight position={[-50, 30, 50]} intensity={0.6} color="#4080ff" />
      <pointLight position={[50, -30, -50]} intensity={0.4} color="#ff8040" />
      
      {/* Background */}
      <Starfield />
      
      {/* Main content group */}
      <group ref={groupRef}>
        {/* Render nodes */}
        {displayNodes3D.map((node) => (
          <CodeNode
            key={node.id}
            node={node}
            isSelected={selectedNode?.id === node.id}
            onClick={onNodeClick}
          />
        ))}
        
        {/* Render edges */}
        {edges3D.map((edge, index) => (
          <CodeEdge
            key={`${edge.source}-${edge.target}-${index}`}
            edge={edge}
          />
        ))}
      </group>
      
      {/* Performance monitoring */}
      {process.env.NODE_ENV === 'development' && (
        <Html position={[-100, 80, 0]}>
          <div className="text-xs text-gray-500 bg-black bg-opacity-50 p-2 rounded">
            <div>Nodes: {displayNodes3D.length}</div>
            <div>Edges: {edges3D.length}</div>
            <div>Layout: {layoutMode}</div>
            <div>Selected: {selectedNode?.name || 'None'}</div>
            {isTransitioning && (
              <div className="text-cyber-blue">Transitioning...</div>
            )}
          </div>
        </Html>
      )}
    </>
  );
};

export default Scene3D;