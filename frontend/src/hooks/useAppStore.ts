import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { AppState, NodeData, AnalyzeResponse, GraphDataResponse, Statistics } from '@/types';

interface AppActions {
  // Analysis actions
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  setAnalysisResult: (result: AnalyzeResponse | null) => void;
  setGraphData: (data: GraphDataResponse | null) => void;
  setStatistics: (stats: Statistics | null) => void;
  
  // UI actions
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setActiveTab: (tab: 'analysis' | 'hierarchy' | 'code' | 'stats' | 'refactor') => void;
  setSelectedNode: (node: NodeData | null) => void;
  
  // 3D actions
  setCameraPosition: (position: [number, number, number]) => void;
  setCameraTarget: (target: [number, number, number]) => void;
  setAutoRotate: (autoRotate: boolean) => void;
  toggleAutoRotate: () => void;
  setLayoutMode: (mode: 'force-directed' | 'hierarchical') => void;
  toggleLayoutMode: () => void;
  
  // Connection actions
  setApiConnected: (connected: boolean) => void;
  setLastError: (error: string | null) => void;

  // Refactoring actions
  setComparisonData: (data: any) => void;
  setShowComparison: (show: boolean) => void;
  setCurrentProjectPath: (path: string) => void;
  addToast: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  
  // Reset actions
  resetAnalysisState: () => void;
  resetUIState: () => void;
  resetAll: () => void;
}

type AppStore = AppState & AppActions;

const initialState: AppState = {
  // Analysis state
  isAnalyzing: false,
  analysisResult: null,
  graphData: null,
  statistics: null,
  
  // UI state
  sidebarOpen: true,
  activeTab: 'analysis',
  selectedNode: null,
  
  // 3D state
  cameraPosition: [0, 0, 120],
  cameraTarget: [0, 0, 0],
  autoRotate: false,
  layoutMode: 'force-directed',
  
  // Connection state
  apiConnected: false,
  lastError: null,

  // Refactoring state
  comparisonData: null,
  showComparison: false,
  currentProjectPath: '',
  toasts: [],
};

export const useAppStore = create<AppStore>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      // Analysis actions
      setIsAnalyzing: (isAnalyzing) => 
        set({ isAnalyzing }, false, 'setIsAnalyzing'),
      
      setAnalysisResult: (analysisResult) =>
        set({ analysisResult }, false, 'setAnalysisResult'),
      
      setGraphData: (graphData) =>
        set({ graphData }, false, 'setGraphData'),
      
      setStatistics: (statistics) =>
        set({ statistics }, false, 'setStatistics'),
      
      // UI actions
      setSidebarOpen: (sidebarOpen) =>
        set({ sidebarOpen }, false, 'setSidebarOpen'),
      
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen }), false, 'toggleSidebar'),
      
      setActiveTab: (activeTab) =>
        set({ activeTab }, false, 'setActiveTab'),
      
      setSelectedNode: (selectedNode) => {
        set({ selectedNode }, false, 'setSelectedNode');
        
        // Auto-switch to analysis tab when a node is selected
        if (selectedNode && get().activeTab !== 'analysis') {
          set({ activeTab: 'analysis' }, false, 'autoSwitchToAnalysis');
        }
      },
      
      // 3D actions
      setCameraPosition: (cameraPosition) =>
        set({ cameraPosition }, false, 'setCameraPosition'),
      
      setCameraTarget: (cameraTarget) =>
        set({ cameraTarget }, false, 'setCameraTarget'),
      
      setAutoRotate: (autoRotate) =>
        set({ autoRotate }, false, 'setAutoRotate'),
      
      toggleAutoRotate: () =>
        set((state) => ({ autoRotate: !state.autoRotate }), false, 'toggleAutoRotate'),
      
      setLayoutMode: (layoutMode) =>
        set({ layoutMode }, false, 'setLayoutMode'),
      
      toggleLayoutMode: () =>
        set((state) => ({ 
          layoutMode: state.layoutMode === 'force-directed' ? 'hierarchical' : 'force-directed' 
        }), false, 'toggleLayoutMode'),
      
      // Connection actions
      setApiConnected: (apiConnected) =>
        set({ apiConnected }, false, 'setApiConnected'),
      
      setLastError: (lastError) =>
        set({ lastError }, false, 'setLastError'),

      // Refactoring actions
      setComparisonData: (comparisonData) =>
        set({ comparisonData }, false, 'setComparisonData'),

      setShowComparison: (showComparison) =>
        set({ showComparison }, false, 'setShowComparison'),

      setCurrentProjectPath: (currentProjectPath) =>
        set({ currentProjectPath }, false, 'setCurrentProjectPath'),

      addToast: (message, type) =>
        set((state) => ({
          toasts: [...state.toasts, { id: Date.now(), message, type }]
        }), false, 'addToast'),
      
      // Reset actions
      resetAnalysisState: () =>
        set(
          {
            isAnalyzing: false,
            analysisResult: null,
            graphData: null,
            statistics: null,
            selectedNode: null,
          },
          false,
          'resetAnalysisState'
        ),
      
      resetUIState: () =>
        set(
          {
            sidebarOpen: true,
            activeTab: 'analysis',
            selectedNode: null,
          },
          false,
          'resetUIState'
        ),
      
      resetAll: () =>
        set(
          { ...initialState },
          false,
          'resetAll'
        ),
    }),
    {
      name: 'code-weaver-store',
      // Only persist UI preferences, not analysis data
      partialize: (state: any) => ({
        sidebarOpen: state.sidebarOpen,
        activeTab: state.activeTab,
        autoRotate: state.autoRotate,
        layoutMode: state.layoutMode,
      }),
    }
  )
);

// Selectors for computed values
export const useAnalysisStats = () => useAppStore((state) => {
  if (!state.analysisResult || !state.graphData) {
    return null;
  }
  
  const { nodes_count, edges_count } = state.analysisResult;
  const deadCodeCount = state.graphData.nodes.filter(n => n.dead).length;
  const highUsageCount = state.graphData.nodes.filter(n => (n.callCount || 0) > 3).length;
  const unusedCount = state.graphData.nodes.filter(n => (n.callCount || 0) === 0 && !n.dead).length;
  
  return {
    totalNodes: nodes_count,
    totalEdges: edges_count,
    deadCodeCount,
    highUsageCount,
    unusedCount,
    analysisComplete: true,
  };
});

export const useGraphMetrics = () => useAppStore((state) => {
  if (!state.graphData) {
    return null;
  }
  
  const nodes = state.graphData.nodes;
  const links = state.graphData.links;
  
  // Calculate node type distribution
  const typeDistribution = nodes.reduce((acc, node) => {
    acc[node.type] = (acc[node.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  // Calculate connectivity metrics
  const connectivityMap = new Map<string, number>();
  links.forEach(link => {
    connectivityMap.set(link.target, (connectivityMap.get(link.target) || 0) + 1);
  });
  
  const isolatedNodes = nodes.filter(node => !connectivityMap.has(node.id)).length;
  const hubNodes = nodes.filter(node => (connectivityMap.get(node.id) || 0) > 3).length;
  
  return {
    typeDistribution,
    isolatedNodes,
    hubNodes,
    averageConnectivity: links.length / nodes.length,
    networkDensity: (2 * links.length) / (nodes.length * (nodes.length - 1)),
  };
});

// Action creators for complex operations
export const useAppActions = () => {
  const store = useAppStore();
  
  return {
    // Start analysis workflow
    startAnalysis: async (_projectPath: string) => {
      store.setIsAnalyzing(true);
      store.setLastError(null);
      store.resetAnalysisState();
    },
    
    // Complete analysis workflow
    completeAnalysis: (
      analysisResult: AnalyzeResponse,
      graphData: GraphDataResponse,
      statistics: Statistics
    ) => {
      store.setAnalysisResult(analysisResult);
      store.setGraphData(graphData);
      store.setStatistics(statistics);
      store.setIsAnalyzing(false);
      store.setActiveTab('analysis');
    },
    
    // Handle analysis error
    handleAnalysisError: (error: string) => {
      store.setIsAnalyzing(false);
      store.setLastError(error);
    },
    
    // Focus on node (updates camera and selection)
    focusOnNode: (node: NodeData) => {
      store.setSelectedNode(node);
      // Camera focusing will be handled by the 3D component
    },
    
    // Clear selection and reset camera
    clearSelection: () => {
      store.setSelectedNode(null);
      store.setCameraPosition([0, 0, 120]);
      store.setCameraTarget([0, 0, 0]);
    },
  };
};