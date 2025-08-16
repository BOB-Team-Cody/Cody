import React, { useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';
import { useAppStore } from '@/hooks/useAppStore';
import { useApiStatus } from '@/hooks/useApi';
import Sidebar from '@/components/Sidebar';
import Scene3D from '@/components/Scene3D';
import LoadingScreen from '@/components/LoadingScreen';
import ToastContainer from '@/components/ToastContainer';
import ConnectionStatus from '@/components/ConnectionStatus';
import Controls from '@/components/Controls';
import { ErrorBoundary } from '@/components/ErrorBoundary';

const App: React.FC = () => {
  const {
    sidebarOpen,
    toggleSidebar,
    selectedNode,
    setSelectedNode,
    graphData,
    autoRotate,
    lastError,
    setLastError,
  } = useAppStore();

  const { connected: apiConnected, loading: apiLoading } = useApiStatus();

  // Clear errors after 5 seconds
  useEffect(() => {
    if (lastError) {
      const timer = setTimeout(() => {
        setLastError(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [lastError, setLastError]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (event.code) {
        case 'KeyS':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            toggleSidebar();
          }
          break;
        case 'Escape':
          if (selectedNode) {
            setSelectedNode(null);
          }
          break;
        case 'KeyR':
          if (!event.ctrlKey && !event.metaKey) {
            // Reset camera view (handled by Scene3D)
            event.preventDefault();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [toggleSidebar, selectedNode, setSelectedNode]);

  return (
    <ErrorBoundary>
      <div className="w-full h-full relative overflow-hidden bg-space-900">
        {/* 3D Canvas */}
        <div className="absolute inset-0">
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
            <Suspense fallback={<LoadingScreen message="Loading 3D scene..." />}>
              <Scene3D
                graphData={graphData}
                selectedNode={selectedNode}
                onNodeClick={setSelectedNode}
                autoRotate={autoRotate}
              />
            </Suspense>
          </Canvas>
        </div>

        {/* Sidebar */}
        <Sidebar />

        {/* Sidebar Toggle Button */}
        <button
          onClick={toggleSidebar}
          className={`
            fixed top-1/2 transform -translate-y-1/2 z-20
            glassmorphism p-3 rounded-r-lg transition-all duration-300
            text-white hover:text-cyber-blue focus-ring
            ${sidebarOpen ? 'left-96' : 'left-0'}
          `}
          title={sidebarOpen ? 'Close sidebar (Ctrl+S)' : 'Open sidebar (Ctrl+S)'}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {sidebarOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 5l7 7-7 7M5 5l7 7-7 7"
              />
            )}
          </svg>
        </button>

        {/* Bottom Controls */}
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-10">
          <Controls />
        </div>

        {/* Connection Status */}
        <div className="fixed top-4 right-4 z-30">
          <ConnectionStatus
            connected={apiConnected}
            loading={apiLoading}
          />
        </div>

        {/* Toast Notifications */}
        <ToastContainer />

        {/* Keyboard Shortcuts Help */}
        <div className="fixed bottom-4 right-4 z-10">
          <div className="glassmorphism p-3 rounded-lg text-xs text-gray-400 max-w-xs opacity-75">
            <div className="font-semibold mb-1">Keyboard Shortcuts:</div>
            <div>Ctrl+S: Toggle sidebar</div>
            <div>Esc: Clear selection</div>
            <div>R: Reset camera</div>
            <div>Space: Toggle auto-rotate</div>
          </div>
        </div>

        {/* Loading overlay */}
        {apiLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <LoadingScreen message="Connecting to API..." />
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default App;