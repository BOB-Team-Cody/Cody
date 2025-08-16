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
      algorithm: 'force-directed',
      nodeSpacing: 50,
      centerForce: 0.01,
      repulsionForce: 500,
      attractionForce: 0.02,
      damping: 0.95,
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

    // Convert nodes to 3D format
    const nodes3D: Node3D[] = nodes.map((node, index) => {
      const position = positions[index];
      const visualProps = this.getNodeVisualProperties(node);

      return {
        ...node,
        position: [position.x, position.y, position.z],
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
    
    // Initialize positions randomly in a sphere
    const positions = nodes.map(() => {
      const radius = Math.random() * 100 + 50;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      const position = new THREE.Vector3();
      position.setFromSphericalCoords(radius, phi, theta);
      return position;
    });

    // Create node index map for faster lookup
    const nodeIndexMap = new Map(nodes.map((node, index) => [node.id, index]));

    // Run physics simulation
    const iterations = 200;
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

      // Apply center force to prevent drift
      positions.forEach((pos, i) => {
        const centerDir = new THREE.Vector3().copy(pos).multiplyScalar(-centerForce);
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
   * Hierarchical layout - arranges nodes by type and call hierarchy
   */
  private calculateHierarchicalLayout(nodes: NodeData[], _links: LinkData[]): THREE.Vector3[] {
    const positions: THREE.Vector3[] = [];
    
    // Group nodes by type
    const modules = nodes.filter(n => n.type === 'module');
    const classes = nodes.filter(n => n.type === 'class');
    const functions = nodes.filter(n => n.type === 'function');

    let currentIndex = 0;

    // Place modules at the top level
    modules.forEach((_, i) => {
      const angle = (i / modules.length) * Math.PI * 2;
      const radius = 80;
      positions[currentIndex++] = new THREE.Vector3(
        Math.cos(angle) * radius,
        60,
        Math.sin(angle) * radius
      );
    });

    // Place classes in the middle level
    classes.forEach((_, i) => {
      const angle = (i / classes.length) * Math.PI * 2;
      const radius = 60;
      positions[currentIndex++] = new THREE.Vector3(
        Math.cos(angle) * radius,
        0,
        Math.sin(angle) * radius
      );
    });

    // Place functions at the bottom level
    functions.forEach((_, i) => {
      const angle = (i / functions.length) * Math.PI * 2;
      const radius = 40;
      positions[currentIndex++] = new THREE.Vector3(
        Math.cos(angle) * radius,
        -60,
        Math.sin(angle) * radius
      );
    });

    return positions;
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
   * Get visual properties for a node based on its data
   */
  private getNodeVisualProperties(node: NodeData): {
    color: string;
    emissive: string;
    opacity: number;
    scale: number;
  } {
    const isDead = node.dead;
    const callCount = node.callCount || 0;
    const isHighUsage = callCount > 3;

    let color: string;
    let emissive: string;
    let opacity: number;
    let scale: number;

    if (isDead) {
      // Dead code: dark red
      color = '#440000';
      emissive = '#220000';
      opacity = 0.6;
      scale = 0.8;
    } else if (isHighUsage) {
      // High usage: bright gold
      color = '#ffdd00';
      emissive = '#664400';
      opacity = 1.0;
      scale = 1.5 + Math.log(callCount) * 0.3;
    } else if (node.type === 'class') {
      // Classes: purple
      color = '#8866dd';
      emissive = '#332255';
      opacity = 0.9;
      scale = 1.3;
    } else if (callCount === 0) {
      // Unused but not dead: gray
      color = '#666666';
      emissive = '#222222';
      opacity = 0.7;
      scale = 0.9;
    } else {
      // Regular functions: blue
      color = '#4488dd';
      emissive = '#223355';
      opacity = 0.8;
      scale = 1.0 + callCount * 0.1;
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