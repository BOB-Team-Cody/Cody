"""
Simple static code analyzer for Python projects.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Set
from vulture import Vulture


def analyze_python_project(project_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Analyze a Python project for code structure and dead code.
    """
    project_path = Path(project_path)
    if not project_path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")
    
    print(f"Analyzing project: {project_path}")
    
    # 1. Dead code detection using vulture
    vulture = Vulture()
    python_files = list(project_path.rglob("*.py"))
    print(f"Found {len(python_files)} Python files")
    
    if python_files:
        vulture.scavenge(python_files)
        unused_code = vulture.get_unused_code()
        print(f"Vulture found {len(unused_code)} unused code items")
        
        dead_code_items = set()
        for item in unused_code:
            try:
                rel_path = Path(item.filename).relative_to(project_path)
                if hasattr(item, 'name') and item.name:
                    dead_id = f"{rel_path}:{item.name}"
                    dead_code_items.add(dead_id)
                    print(f"Dead: {dead_id}")
            except:
                pass
    
    # 2. AST analysis
    nodes = []
    edges = []
    all_call_counts = {}
    
    # First pass: count all function calls
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = _extract_call_name(node.func)
                    if func_name:
                        all_call_counts[func_name] = all_call_counts.get(func_name, 0) + 1
        except:
            continue
    
    print(f"Found {len(all_call_counts)} unique function calls")
    
    # Second pass: create nodes and edges
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            rel_path = py_file.relative_to(project_path)
            
            # Module node
            nodes.append({
                "id": str(rel_path),
                "type": "module",
                "file": str(rel_path),
                "label": rel_path.stem,
                "dead": False,
                "callCount": 0
            })
            
            # Function and class nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_id = f"{rel_path}:{node.name}"
                    is_dead = func_id in dead_code_items
                    call_count = all_call_counts.get(node.name, 0)
                    
                    nodes.append({
                        "id": func_id,
                        "type": "function",
                        "file": str(rel_path),
                        "label": node.name,
                        "dead": is_dead,
                        "callCount": call_count
                    })
                    
                elif isinstance(node, ast.ClassDef):
                    class_id = f"{rel_path}:{node.name}"
                    is_dead = class_id in dead_code_items
                    call_count = all_call_counts.get(node.name, 0)
                    
                    nodes.append({
                        "id": class_id,
                        "type": "class",
                        "file": str(rel_path),
                        "label": node.name,
                        "dead": is_dead,
                        "callCount": call_count
                    })
                    
                elif isinstance(node, ast.Call):
                    func_name = _extract_call_name(node.func)
                    if func_name:
                        edges.append({
                            "source": str(rel_path),
                            "target": f"{rel_path}:{func_name}",
                            "type": "CALLS"
                        })
                        
        except Exception as e:
            print(f"Error analyzing {py_file}: {e}")
            continue
    
    print(f"Generated {len(nodes)} nodes and {len(edges)} edges")
    
    return {
        "nodes": nodes,
        "edges": edges
    }


def _extract_call_name(node):
    """Extract function name from call node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return node.attr
    return None


if __name__ == "__main__":
    result = analyze_python_project("sample_project")
    print(f"Final result: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
