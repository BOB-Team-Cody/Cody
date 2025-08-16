import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';
import Scene3D from './Scene3D';
import LoadingScreen from './LoadingScreen';

interface ComparisonData {
  original: {
    nodes: any[];
    links: any[];
    statistics: any;
  };
  refactored: {
    nodes: any[];
    links: any[];
    statistics: any;
  };
  differences: {
    nodes_removed: number;
    dead_code_removed: number;
    complexity_reduction: {
      before: number;
      after: number;
      improvement: number;
    };
    improvements: string[];
  };
}

interface RefactorComparisonProps {
  comparisonData: ComparisonData | null;
  loading: boolean;
}

const RefactorComparison: React.FC<RefactorComparisonProps> = ({
  comparisonData,
  loading
}) => {
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'split' | 'overlay' | 'toggle'>('split');
  const [showOriginal, setShowOriginal] = useState(true);

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <LoadingScreen message="Generating refactoring comparison..." />
      </div>
    );
  }

  if (!comparisonData) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-400">
        <div className="text-center">
          <div className="text-xl mb-2">No comparison data available</div>
          <div className="text-sm">Run refactoring analysis to see comparison</div>
        </div>
      </div>
    );
  }

  const { original, refactored, differences } = comparisonData;

  return (
    <div className="w-full h-full flex flex-col">
      {/* Controls */}
      <div className="flex-shrink-0 p-4 bg-space-800 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Refactoring Comparison</h2>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-400">View Mode:</label>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as any)}
              className="bg-space-700 text-white px-3 py-1 rounded border border-gray-600 focus:border-cyber-blue focus:outline-none"
            >
              <option value="split">Split View</option>
              <option value="overlay">Overlay</option>
              <option value="toggle">Toggle</option>
            </select>
            
            {viewMode === 'toggle' && (
              <button
                onClick={() => setShowOriginal(!showOriginal)}
                className="px-3 py-1 bg-cyber-blue text-white rounded hover:bg-cyber-blue-dark transition-colors"
              >
                {showOriginal ? 'Show Refactored' : 'Show Original'}
              </button>
            )}
          </div>
        </div>

        {/* Statistics Comparison */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="glassmorphism p-3 rounded">
            <div className="text-gray-400 mb-1">Nodes Removed</div>
            <div className="text-green-400 text-xl font-bold">
              {differences.nodes_removed}
            </div>
          </div>
          
          <div className="glassmorphism p-3 rounded">
            <div className="text-gray-400 mb-1">Dead Code Removed</div>
            <div className="text-green-400 text-xl font-bold">
              {differences.dead_code_removed}
            </div>
          </div>
          
          <div className="glassmorphism p-3 rounded">
            <div className="text-gray-400 mb-1">Complexity Reduction</div>
            <div className="text-green-400 text-xl font-bold">
              {differences.complexity_reduction.improvement}
            </div>
          </div>
        </div>

        {/* Improvements List */}
        <div className="mt-4">
          <div className="text-sm text-gray-400 mb-2">Key Improvements:</div>
          <div className="flex flex-wrap gap-2">
            {differences.improvements.map((improvement, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-green-600 bg-opacity-20 text-green-400 rounded text-xs border border-green-600 border-opacity-30"
              >
                {improvement}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* 3D Visualization */}
      <div className="flex-1 relative">
        {viewMode === 'split' && (
          <div className="w-full h-full flex">
            {/* Original */}
            <div className="w-1/2 h-full relative border-r border-gray-700">
              <div className="absolute top-4 left-4 z-10 glassmorphism px-3 py-1 rounded text-sm text-white">
                Original ({original.statistics.total_nodes} nodes)
              </div>
              <Canvas
                camera={{
                  position: [0, 0, 120],
                  fov: 75,
                  near: 0.1,
                  far: 2000,
                }}
                gl={{
                  antialias: true,
                  alpha: true,
                  powerPreference: 'high-performance',
                }}
                dpr={Math.min(window.devicePixelRatio, 2)}
              >
                <Suspense fallback={<LoadingScreen message="Loading original..." />}>
                  <Scene3D
                    graphData={original}
                    selectedNode={selectedNode}
                    onNodeClick={setSelectedNode}
                    autoRotate={false}
                  />
                </Suspense>
              </Canvas>
            </div>

            {/* Refactored */}
            <div className="w-1/2 h-full relative">
              <div className="absolute top-4 left-4 z-10 glassmorphism px-3 py-1 rounded text-sm text-white">
                Refactored ({refactored.statistics.total_nodes} nodes)
              </div>
              <Canvas
                camera={{
                  position: [0, 0, 120],
                  fov: 75,
                  near: 0.1,
                  far: 2000,
                }}
                gl={{
                  antialias: true,
                  alpha: true,
                  powerPreference: 'high-performance',
                }}
                dpr={Math.min(window.devicePixelRatio, 2)}
              >
                <Suspense fallback={<LoadingScreen message="Loading refactored..." />}>
                  <Scene3D
                    graphData={refactored}
                    selectedNode={selectedNode}
                    onNodeClick={setSelectedNode}
                    autoRotate={false}
                  />
                </Suspense>
              </Canvas>
            </div>
          </div>
        )}

        {viewMode === 'overlay' && (
          <div className="w-full h-full relative">
            <div className="absolute top-4 left-4 z-10 glassmorphism px-3 py-1 rounded text-sm text-white">
              Overlay Comparison
            </div>
            <Canvas
              camera={{
                position: [0, 0, 120],
                fov: 75,
                near: 0.1,
                far: 2000,
              }}
              gl={{
                antialias: true,
                alpha: true,
                powerPreference: 'high-performance',
              }}
              dpr={Math.min(window.devicePixelRatio, 2)}
            >
              <Suspense fallback={<LoadingScreen message="Loading overlay..." />}>
                <OverlayScene
                  originalData={original}
                  refactoredData={refactored}
                  selectedNode={selectedNode}
                  onNodeClick={setSelectedNode}
                />
              </Suspense>
            </Canvas>
          </div>
        )}

        {viewMode === 'toggle' && (
          <div className="w-full h-full relative">
            <div className="absolute top-4 left-4 z-10 glassmorphism px-3 py-1 rounded text-sm text-white">
              {showOriginal 
                ? `Original (${original.statistics.total_nodes} nodes)` 
                : `Refactored (${refactored.statistics.total_nodes} nodes)`
              }
            </div>
            <Canvas
              camera={{
                position: [0, 0, 120],
                fov: 75,
                near: 0.1,
                far: 2000,
              }}
              gl={{
                antialias: true,
                alpha: true,
                powerPreference: 'high-performance',
              }}
              dpr={Math.min(window.devicePixelRatio, 2)}
            >
              <Suspense fallback={<LoadingScreen message="Loading..." />}>
                <Scene3D
                  graphData={showOriginal ? original : refactored}
                  selectedNode={selectedNode}
                  onNodeClick={setSelectedNode}
                  autoRotate={false}
                />
              </Suspense>
            </Canvas>
          </div>
        )}
      </div>
    </div>
  );
};

// Overlay scene component for showing both original and refactored with different colors
const OverlayScene: React.FC<{
  originalData: any;
  refactoredData: any;
  selectedNode: any;
  onNodeClick: (node: any) => void;
}> = ({ originalData, refactoredData, selectedNode, onNodeClick }) => {
  // Create combined data with different materials for original vs refactored
  const combinedData = {
    nodes: [
      ...originalData.nodes.map((node: any) => ({
        ...node,
        id: `original_${node.id}`,
        material: 'original',
        opacity: 0.6
      })),
      ...refactoredData.nodes.map((node: any) => ({
        ...node,
        id: `refactored_${node.id}`,
        material: 'refactored',
        opacity: 0.8
      }))
    ],
    links: [
      ...originalData.links.map((link: any) => ({
        ...link,
        source: `original_${link.source}`,
        target: `original_${link.target}`,
        material: 'original'
      })),
      ...refactoredData.links.map((link: any) => ({
        ...link,
        source: `refactored_${link.source}`,
        target: `refactored_${link.target}`,
        material: 'refactored'
      }))
    ]
  };

  return (
    <Scene3D
      graphData={combinedData}
      selectedNode={selectedNode}
      onNodeClick={onNodeClick}
      autoRotate={false}
    />
  );
};

export default RefactorComparison;