#!/usr/bin/env python3
"""
Test script for the analyzer
"""

import sys
sys.path.append('.')

from analyzer import analyze_python_project


def main():
    print("Starting analysis...")
    
    try:
        result = analyze_python_project('sample_project')
        print("Analysis completed successfully!")
        
        print(f"Nodes found: {len(result['nodes'])}")
        print(f"Edges found: {len(result['edges'])}")
        
        # Show first few nodes
        print("\nFirst 5 nodes:")
        for i, node in enumerate(result['nodes'][:5]):
            print(f"{i+1}. ID: {node['id']}")
            print(f"   Type: {node['type']}")
            print(f"   Label: {node['label']}")
            print(f"   File: {node['file']}")
            print(f"   Dead: {node.get('dead', False)}")
            print()
        
        # Show first few edges
        print("First 5 edges:")
        for i, edge in enumerate(result['edges'][:5]):
            print(f"{i+1}. {edge['source']} -> {edge['target']}")
        
        # Count dead code
        dead_nodes = [n for n in result['nodes'] if n.get('dead', False)]
        print(f"\nDead code items found: {len(dead_nodes)}")
        for node in dead_nodes:
            print(f"  - {node['id']} ({node['type']})")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
