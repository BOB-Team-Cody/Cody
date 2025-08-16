#!/usr/bin/env python3

from analyzer import analyze_python_project

def main():
    try:
        print("Starting analysis...")
        result = analyze_python_project('sample_project')
        
        nodes = result['nodes']
        edges = result['edges']
        
        print(f"\n=== ANALYSIS RESULTS ===")
        print(f"Total nodes: {len(nodes)}")
        print(f"Total edges: {len(edges)}")
        
        # Count by type
        type_counts = {}
        dead_count = 0
        for node in nodes:
            node_type = node.get('type', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
            if node.get('dead', False):
                dead_count += 1
        
        print(f"\nDead code count: {dead_count}")
        print(f"\nType distribution:")
        for node_type, count in type_counts.items():
            print(f"  {node_type}: {count}")
        
        # Top called functions
        functions_with_calls = []
        for node in nodes:
            if node.get('type') == 'function' or node.get('type') == 'class':
                call_count = node.get('callCount', 0)
                if call_count > 0:
                    functions_with_calls.append((node['label'], call_count, node.get('type')))
        
        functions_with_calls.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nTop called functions:")
        for i, (name, count, ftype) in enumerate(functions_with_calls[:10]):
            print(f"  {i+1}. {name} ({count} calls) - {ftype}")
        
        print(f"\nDead code items:")
        dead_items = [node for node in nodes if node.get('dead', False)]
        for item in dead_items[:10]:
            print(f"  - {item['label']} ({item['type']}) in {item['file']}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
