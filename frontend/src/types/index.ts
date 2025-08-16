// API Types
export interface AnalyzeRequest {
  path: string;
}

export interface AnalyzeResponse {
  success: boolean;
  message: string;
  nodes_count: number;
  edges_count: number;
  statistics: Statistics;
}

export interface GraphDataResponse {
  nodes: NodeData[];
  links: LinkData[];
}

export interface NodeData {
  id: string;
  name: string;
  file: string;
  type: 'function' | 'class' | 'module';
  dead: boolean;
  callCount: number;
  size: number;
  lineCount?: number; // Added for code length information
  sourceCode?: string; // Added for actual source code from Neo4j
  className?: string; // Added for class name
}

export interface LinkData {
  source: string;
  target: string;
  frequency?: number; // Added for call frequency information
}

export interface Statistics {
  total_nodes: number;
  total_relationships: number;
  dead_code_count: number;
  by_type: Record<string, number>;
  most_called: {
    name: string;
    file: string;
    callCount: number;
  }[];
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database_connected: boolean;
  service: string;
  database_status?: string;
}

// 3D Visualization Types
export interface Node3D extends NodeData {
  position: [number, number, number];
  color: string;
  emissive: string;
  opacity: number;
  scale: number;
  depth?: number; // Added for hierarchical layout depth information
}

export interface Edge3D extends LinkData {
  points: [number, number, number][];
  color: string;
  opacity: number;
  frequency?: number; // Added for call frequency visualization
}

// UI State Types
export interface AppState {
  // Analysis state
  isAnalyzing: boolean;
  analysisResult: AnalyzeResponse | null;
  graphData: GraphDataResponse | null;
  statistics: Statistics | null;
  
  // UI state
  sidebarOpen: boolean;
  activeTab: 'analysis' | 'hierarchy' | 'code' | 'stats' | 'refactoring'; // Added 'hierarchy' and 'refactoring' tabs
  selectedNode: NodeData | null;
  
  // 3D state
  cameraPosition: [number, number, number];
  cameraTarget: [number, number, number];
  autoRotate: boolean;
  layoutMode: 'force-directed' | 'hierarchical'; // Added layout mode
  
  // Connection state
  apiConnected: boolean;
  lastError: string | null;
}

// Component Props Types
export interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  analysisResult: AnalyzeResponse | null;
  selectedNode: NodeData | null;
  statistics: Statistics | null;
  onAnalyze: (path: string) => void;
  isAnalyzing: boolean;
}

export interface Canvas3DProps {
  graphData: GraphDataResponse | null;
  onNodeClick: (node: NodeData) => void;
  onNodeHover: (node: NodeData | null) => void;
  selectedNode: NodeData | null;
  autoRotate: boolean;
}

export interface ControlsProps {
  onRefresh: () => void;
  onClear: () => void;
  onToggleAutoRotate: () => void;
  autoRotate: boolean;
  isLoading: boolean;
}

// Theme and styling types
export interface Theme {
  colors: {
    background: string;
    surface: string;
    primary: string;
    secondary: string;
    accent: string;
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    status: {
      success: string;
      warning: string;
      error: string;
      info: string;
    };
    code: {
      function: string;
      class: string;
      module: string;
      dead: string;
      highUsage: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
  };
}

// Error types
export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

// Animation types
export interface AnimationConfig {
  duration: number;
  easing: string;
  delay?: number;
}

// Layout types
export type LayoutAlgorithm = 'sphere' | 'force-directed' | 'hierarchical' | 'circular';

export interface LayoutConfig {
  algorithm: LayoutAlgorithm;
  nodeSpacing: number;
  centerForce: number;
  repulsionForce: number;
  attractionForce: number;
  damping: number;
}

// Filter types
export interface FilterConfig {
  showDeadCode: boolean;
  showUnusedCode: boolean;
  minCallCount: number;
  filePattern: string;
  nodeTypes: ('function' | 'class' | 'module')[];
}