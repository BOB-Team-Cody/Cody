import * as THREE from 'three';
import { NodeData, LinkData, Node3D, Edge3D, LayoutConfig } from '@/types';

/**
 * 3D Visualization service for code graph
 */
export class VisualizationService {
  private _nodePositions: Map<string, THREE.Vector3> = new Map();
  private layoutConfig: LayoutConfig;

  constructor(layoutConfig?: Partial<LayoutConfig>) {
    this.layoutConfig = {
      algorithm: 'force-directed', // 기본값을 force-directed로 되돌림
      nodeSpacing: 30,
      centerForce: 0.05,
      repulsionForce: 300,
      attractionForce: 0.05,
      damping: 0.9,
      ...layoutConfig,
    };
  }

  /**
   * Convert flat graph data to 3D positioned nodes and edges
   */
  processGraphData(nodes: NodeData[], links: LinkData[]): { nodes3D: Node3D[]; edges3D: Edge3D[] } {
    console.log(`Processing graph data: ${nodes.length} nodes, ${links.length} links`);

    // Calculate positions based on layout algorithm
    const positions = this.calculateLayout(nodes, links);

    // Calculate depths for depth-based coloring
    const depths = this.layoutConfig.algorithm === 'hierarchical' 
      ? this.calculateCallDepths(nodes, links)
      : new Array(nodes.length).fill(0);
    
    // Convert nodes to 3D format
    const nodes3D: Node3D[] = nodes.map((node, index) => {
      const position = positions[index];
      const depth = depths[index];
      const visualProps = this.getNodeVisualProperties(node, depth);

      return {
        ...node,
        position: [position.x, position.y, position.z],
        depth,
        ...visualProps,
      };
    });

    // Convert links to 3D format
    const nodeIndexMap = new Map(nodes.map((node, index) => [node.id, index]));
    const edges3D: Edge3D[] = links
      .map((link) => {
        const sourceIndex = nodeIndexMap.get(link.source);
        const targetIndex = nodeIndexMap.get(link.target);

        if (sourceIndex === undefined || targetIndex === undefined) {
          console.warn(`Invalid link: ${link.source} -> ${link.target}`);
          return null;
        }

        const sourcePos = positions[sourceIndex];
        const targetPos = positions[targetIndex];

        return {
          ...link,
          points: this.generateCurvedPath(sourcePos, targetPos),
          color: this.getLinkColor(nodes[sourceIndex], nodes[targetIndex]),
          opacity: 0.6,
          frequency: link.frequency || 1, // Add frequency information for edge thickness
        };
      })
      .filter((edge): edge is Edge3D => edge !== null);

    console.log(`Processed: ${nodes3D.length} 3D nodes, ${edges3D.length} 3D edges`);
    return { nodes3D, edges3D };
  }

  /**
   * Calculate node positions based on layout algorithm
   */
  private calculateLayout(nodes: NodeData[], links: LinkData[]): THREE.Vector3[] {
    switch (this.layoutConfig.algorithm) {
      case 'sphere':
        return this.calculateSphereLayout(nodes);
      case 'force-directed':
        return this.calculateForceDirectedLayout(nodes, links);
      case 'hierarchical':
        return this.calculateHierarchicalLayout(nodes, links);
      case 'circular':
        return this.calculateCircularLayout(nodes);
      default:
        return this.calculateForceDirectedLayout(nodes, links);
    }
  }

  /**
   * Sphere layout - distributes nodes evenly on a sphere
   */
  private calculateSphereLayout(nodes: NodeData[]): THREE.Vector3[] {
    const nodeCount = nodes.length;
    const radius = Math.max(50, 20 + nodeCount * 0.8);
    const positions: THREE.Vector3[] = [];

    for (let i = 0; i < nodeCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / nodeCount);
      const theta = Math.sqrt(nodeCount * Math.PI) * phi;

      const position = new THREE.Vector3();
      position.setFromSphericalCoords(radius, phi, theta);
      positions.push(position);
    }

    return positions;
  }

  /**
   * Force-directed layout - uses physics simulation
   */
  private calculateForceDirectedLayout(nodes: NodeData[], links: LinkData[]): THREE.Vector3[] {
    const nodeCount = nodes.length;
    
    // Initialize positions randomly in a smaller, tighter sphere
    const positions = nodes.map(() => {
      const radius = Math.random() * 40 + 20; // 더 작은 초기 반경
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      const position = new THREE.Vector3();
      position.setFromSphericalCoords(radius, phi, theta);
      return position;
    });

    // Create node index map for faster lookup
    const nodeIndexMap = new Map(nodes.map((node, index) => [node.id, index]));

    // Run physics simulation with more iterations for better settling
    const iterations = 300;
    const { repulsionForce, attractionForce, damping, centerForce } = this.layoutConfig;

    for (let iter = 0; iter < iterations; iter++) {
      const forces = positions.map(() => new THREE.Vector3());

      // Calculate repulsion forces between all nodes
      for (let i = 0; i < nodeCount; i++) {
        for (let j = i + 1; j < nodeCount; j++) {
          const dir = new THREE.Vector3().subVectors(positions[i], positions[j]);
          const distance = Math.max(dir.length(), 1);
          const force = repulsionForce / (distance * distance);
          
          dir.normalize().multiplyScalar(force);
          forces[i].add(dir);
          forces[j].sub(dir);
        }
      }

      // Calculate attraction forces for connected nodes
      links.forEach((link) => {
        const sourceIndex = nodeIndexMap.get(link.source);
        const targetIndex = nodeIndexMap.get(link.target);

        if (sourceIndex !== undefined && targetIndex !== undefined) {
          const dir = new THREE.Vector3().subVectors(positions[targetIndex], positions[sourceIndex]);
          const distance = dir.length();
          const force = distance * attractionForce;

          dir.normalize().multiplyScalar(force);
          forces[sourceIndex].add(dir);
          forces[targetIndex].sub(dir);
        }
      });

      // Apply stronger center force to keep nodes closer together
      positions.forEach((pos, i) => {
        const distance = pos.length();
        const centerDir = new THREE.Vector3().copy(pos).multiplyScalar(-centerForce * (1 + distance * 0.01));
        forces[i].add(centerDir);
      });

      // Apply forces with damping
      positions.forEach((pos, i) => {
        forces[i].multiplyScalar(damping);
        pos.add(forces[i]);
      });

      // Cool down the simulation
      const cooldown = 1 - (iter / iterations) * 0.5;
      forces.forEach(force => force.multiplyScalar(cooldown));
    }

    return positions;
  }

  /**
   * Hierarchical layout - arranges nodes by call depth (left to right)
   */
  private calculateHierarchicalLayout(nodes: NodeData[], links: LinkData[]): THREE.Vector3[] {
    const positions: THREE.Vector3[] = new Array(nodes.length);
    
    // Calculate call depth for each node
    const depths = this.calculateCallDepths(nodes, links);
    const maxDepth = Math.max(...depths);
    
    // Group nodes by depth and module
    const depthGroups: Map<number, Map<string, NodeData[]>> = new Map();
    
    nodes.forEach((node, index) => {
      const depth = depths[index];
      const module = node.file || 'unknown';
      
      if (!depthGroups.has(depth)) {
        depthGroups.set(depth, new Map());
      }
      if (!depthGroups.get(depth)!.has(module)) {
        depthGroups.get(depth)!.set(module, []);
      }
      depthGroups.get(depth)!.get(module)!.push(node);
    });

    // Position nodes left to right by depth, grouped by module
    const depthSpacing = 120; // Distance between depth levels
    const moduleSpacing = 60; // Distance between modules in same depth
    const nodeSpacing = 40; // Distance between nodes in same module
    
    let nodeIndex = 0;
    for (let depth = 0; depth <= maxDepth; depth++) {
      const moduleGroups = depthGroups.get(depth);
      if (!moduleGroups) continue;
      
      const modules = Array.from(moduleGroups.keys());
      const totalModules = modules.length;
      
      modules.forEach((module, moduleIndex) => {
        const nodesInModule = moduleGroups.get(module)!;
        const totalNodes = nodesInModule.length;
        
        // Calculate module position
        const moduleY = (moduleIndex - (totalModules - 1) / 2) * moduleSpacing;
        
        nodesInModule.forEach((node, nodeIndexInModule) => {
          // Find original index
          const originalIndex = nodes.findIndex(n => n.id === node.id);
          
          // Calculate node position - Y axis for depth (top to bottom)
          const x = moduleY + (nodeIndexInModule - (totalNodes - 1) / 2) * nodeSpacing;
          const y = -(depth * depthSpacing) + (maxDepth * depthSpacing / 2); // Top to bottom layout
          const z = (Math.random() - 0.5) * 20; // Small random Z for visual depth
          
          positions[originalIndex] = new THREE.Vector3(x, y, z);
        });
      });
    }

    return positions;
  }

  /**
   * Calculate call depth for each node (0 = entry point, 1 = called by entry, etc.)
   */
  private calculateCallDepths(nodes: NodeData[], links: LinkData[]): number[] {
    const nodeIndexMap = new Map(nodes.map((node, index) => [node.id, index]));
    const depths = new Array(nodes.length).fill(-1);
    const inDegree = new Array(nodes.length).fill(0);
    const adjacencyList: number[][] = new Array(nodes.length).fill(null).map(() => []);
    
    // Build adjacency list and calculate in-degrees
    links.forEach(link => {
      const sourceIndex = nodeIndexMap.get(link.source);
      const targetIndex = nodeIndexMap.get(link.target);
      
      if (sourceIndex !== undefined && targetIndex !== undefined) {
        adjacencyList[sourceIndex].push(targetIndex);
        inDegree[targetIndex]++;
      }
    });
    
    // Find entry points (nodes with no incoming edges or main functions)
    const queue: number[] = [];
    nodes.forEach((node, index) => {
      if (inDegree[index] === 0 || node.name === 'main' || node.name.includes('main')) {
        depths[index] = 0;
        queue.push(index);
      }
    });
    
    // If no clear entry points, use nodes with lowest in-degree
    if (queue.length === 0) {
      const minInDegree = Math.min(...inDegree);
      nodes.forEach((node, index) => {
        if (inDegree[index] === minInDegree) {
          depths[index] = 0;
          queue.push(index);
        }
      });
    }
    
    // BFS to calculate depths
    while (queue.length > 0) {
      const currentIndex = queue.shift()!;
      const currentDepth = depths[currentIndex];
      
      adjacencyList[currentIndex].forEach(neighborIndex => {
        if (depths[neighborIndex] === -1 || depths[neighborIndex] > currentDepth + 1) {
          depths[neighborIndex] = currentDepth + 1;
          queue.push(neighborIndex);
        }
      });
    }
    
    // Handle isolated nodes
    depths.forEach((depth, index) => {
      if (depth === -1) {
        depths[index] = 0;
      }
    });
    
    return depths;
  }

  /**
   * Circular layout - arranges nodes in concentric circles
   */
  private calculateCircularLayout(nodes: NodeData[]): THREE.Vector3[] {
    const positions: THREE.Vector3[] = [];
    const nodeCount = nodes.length;

    // Sort nodes by call count for better visual hierarchy
    const _sortedNodes = [...nodes].sort((a, b) => (b.callCount || 0) - (a.callCount || 0));
    
    // Determine number of circles needed
    const maxNodesPerCircle = 12;
    const circleCount = Math.ceil(nodeCount / maxNodesPerCircle);
    
    let nodeIndex = 0;
    for (let circle = 0; circle < circleCount; circle++) {
      const radius = 30 + circle * 40;
      const nodesInThisCircle = Math.min(maxNodesPerCircle, nodeCount - nodeIndex);
      
      for (let i = 0; i < nodesInThisCircle; i++) {
        const angle = (i / nodesInThisCircle) * Math.PI * 2;
        const position = new THREE.Vector3(
          Math.cos(angle) * radius,
          (circle - circleCount / 2) * 20,
          Math.sin(angle) * radius
        );
        
        positions.push(position);
        nodeIndex++;
      }
    }

    return positions;
  }

  /**
   * Get module color palette
   */
  private getModuleColorPalette(module: string): { base: string; emissive: string } {
    // Create consistent color for each module using hash
    let hash = 0;
    for (let i = 0; i < module.length; i++) {
      const char = module.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    // Color palettes for different modules
    const palettes = [
      { base: '#4A90E2', emissive: '#2A5AA2' }, // Blue
      { base: '#7ED321', emissive: '#5EA321' }, // Green  
      { base: '#BD10E0', emissive: '#8D10A0' }, // Purple
      { base: '#F5A623', emissive: '#C58623' }, // Orange
      { base: '#D0021B', emissive: '#A0021B' }, // Red
      { base: '#50E3C2', emissive: '#30B392' }, // Teal
      { base: '#B8E986', emissive: '#88B956' }, // Light Green
      { base: '#9013FE', emissive: '#6013CE' }, // Deep Purple
      { base: '#FF6900', emissive: '#CF4900' }, // Deep Orange
      { base: '#FCB900', emissive: '#CC8900' }, // Yellow
    ];
    
    const paletteIndex = Math.abs(hash) % palettes.length;
    return palettes[paletteIndex];
  }

  /**
   * Get depth-based color modifier
   */
  private getDepthColorModifier(depth: number): { hue: number; saturation: number; lightness: number } {
    // Create depth-based color variations
    const depthColors = [
      { hue: 0, saturation: 0, lightness: 1.2 },     // depth 0: brighter
      { hue: 30, saturation: 0.1, lightness: 1.0 },  // depth 1: slight orange tint
      { hue: 60, saturation: 0.15, lightness: 0.9 }, // depth 2: yellow tint, dimmer
      { hue: 120, saturation: 0.2, lightness: 0.8 }, // depth 3: green tint, dimmer
      { hue: 180, saturation: 0.25, lightness: 0.7 }, // depth 4: cyan tint, dimmer
      { hue: 240, saturation: 0.3, lightness: 0.6 },  // depth 5: blue tint, dimmer
      { hue: 300, saturation: 0.35, lightness: 0.5 }, // depth 6+: purple tint, dimmest
    ];
    
    const index = Math.min(depth, depthColors.length - 1);
    return depthColors[index];
  }

  /**
   * Apply depth modifier to color
   */
  private modifyColorByDepth(baseColor: string, depth: number): string {
    const modifier = this.getDepthColorModifier(depth);
    const color = new THREE.Color(baseColor);
    
    // Convert to HSL
    const hsl = { h: 0, s: 0, l: 0 };
    color.getHSL(hsl);
    
    // Apply modifications
    hsl.h = (hsl.h + modifier.hue / 360) % 1;
    hsl.s = Math.min(hsl.s + modifier.saturation, 1);
    hsl.l = Math.min(hsl.l * modifier.lightness, 1);
    
    // Convert back to hex
    color.setHSL(hsl.h, hsl.s, hsl.l);
    return '#' + color.getHexString();
  }

  /**
   * Get visual properties for a node based on its data
   */
  private getNodeVisualProperties(node: NodeData, depth: number = 0): {
    color: string;
    emissive: string;
    opacity: number;
    scale: number;
  } {
    const isDead = node.dead;
    const callCount = node.callCount || 0;
    const isHighUsage = callCount > 3;
    const codeLength = node.lineCount || 10; // Default 10 lines if not specified
    
    // Get module-based colors
    const module = node.file || 'unknown';
    const moduleColors = this.getModuleColorPalette(module);

    let color: string;
    let emissive: string;
    let opacity: number;
    let scale: number;

    if (isDead) {
      // Dead code: dark red (override module color)
      color = '#440000';
      emissive = '#220000';
      opacity = 0.6;
      scale = 0.8;
    } else if (isHighUsage) {
      // High usage: bright gold (override module color)
      color = '#ffdd00';
      emissive = '#664400';
      opacity = 1.0;
      scale = 1.2 + Math.log(callCount) * 0.2 + Math.log(codeLength) * 0.1;
    } else {
      // Use module colors with type-based modifications and depth layering
      color = this.modifyColorByDepth(moduleColors.base, depth);
      emissive = this.modifyColorByDepth(moduleColors.emissive, depth);
      
      // Apply depth-based opacity modifier
      const depthOpacityModifier = this.getDepthColorModifier(depth).lightness;
      
      if (node.type === 'class') {
        // Classes: slightly darker and larger
        opacity = 0.9 * depthOpacityModifier;
        scale = 1.1 + Math.log(codeLength) * 0.05;
      } else if (callCount === 0) {
        // Unused: dimmed module color
        opacity = 0.5 * depthOpacityModifier;
        scale = 0.8 + Math.log(codeLength) * 0.03;
      } else {
        // Regular functions: normal module color
        opacity = 0.8 * depthOpacityModifier;
        scale = 0.9 + callCount * 0.05 + Math.log(codeLength) * 0.03;
      }
    }

    return { color, emissive, opacity, scale };
  }

  /**
   * Generate curved path between two points
   */
  private generateCurvedPath(start: THREE.Vector3, end: THREE.Vector3): [number, number, number][] {
    const midpoint = new THREE.Vector3()
      .addVectors(start, end)
      .multiplyScalar(0.5);

    // Add some randomness to the curve
    const offset = new THREE.Vector3(
      (Math.random() - 0.5) * 20,
      (Math.random() - 0.5) * 20,
      (Math.random() - 0.5) * 20
    );
    midpoint.add(offset);

    // Create bezier curve
    const curve = new THREE.QuadraticBezierCurve3(start, midpoint, end);
    const points = curve.getPoints(10);

    return points.map(p => [p.x, p.y, p.z] as [number, number, number]);
  }

  /**
   * Get link color based on source and target nodes
   */
  private getLinkColor(source: NodeData, target: NodeData): string {
    if (source.dead || target.dead) {
      return '#ff4444'; // Red for dead code connections
    }
    
    if ((source.callCount || 0) > 3 || (target.callCount || 0) > 3) {
      return '#ffaa00'; // Orange for high-usage connections
    }

    return '#00aaff'; // Default blue
  }

  /**
   * Update layout configuration
   */
  updateLayoutConfig(config: Partial<LayoutConfig>): void {
    this.layoutConfig = { ...this.layoutConfig, ...config };
  }

  /**
   * Get current layout configuration
   */
  getLayoutConfig(): LayoutConfig {
    return { ...this.layoutConfig };
  }

  /**
   * Calculate optimal camera position for viewing the graph
   */
  calculateCameraPosition(nodes3D: Node3D[]): {
    position: [number, number, number];
    target: [number, number, number];
  } {
    if (nodes3D.length === 0) {
      return {
        position: [0, 0, 120],
        target: [0, 0, 0],
      };
    }

    // Calculate bounding box
    const bounds = {
      min: new THREE.Vector3(Infinity, Infinity, Infinity),
      max: new THREE.Vector3(-Infinity, -Infinity, -Infinity),
    };

    nodes3D.forEach(node => {
      const [x, y, z] = node.position;
      bounds.min.x = Math.min(bounds.min.x, x);
      bounds.min.y = Math.min(bounds.min.y, y);
      bounds.min.z = Math.min(bounds.min.z, z);
      bounds.max.x = Math.max(bounds.max.x, x);
      bounds.max.y = Math.max(bounds.max.y, y);
      bounds.max.z = Math.max(bounds.max.z, z);
    });

    // Calculate center and size
    const center = new THREE.Vector3()
      .addVectors(bounds.min, bounds.max)
      .multiplyScalar(0.5);
    
    const size = new THREE.Vector3()
      .subVectors(bounds.max, bounds.min);
    
    const maxDimension = Math.max(size.x, size.y, size.z);
    const distance = maxDimension * 1.5 + 50;

    return {
      position: [center.x, center.y, center.z + distance],
      target: [center.x, center.y, center.z],
    };
  }
}