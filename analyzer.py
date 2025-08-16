"""
Static code analyzer for Python projects.
Uses AST for parsing and vulture for dead code detection.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from vulture import Vulture

class CodeAnalyzer:
    """Main analyzer for Python projects."""
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.dead_code_items = set()

    def analyze_project(self, project_path: str) -> Dict[str, List[Dict[str, Any]]]:
        project_path = Path(project_path)
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Dead code detection
        self._detect_dead_code(project_path)
        # AST analysis
        self._analyze_code_structure(project_path)

        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

    def _detect_dead_code(self, project_path: Path) -> None:
        """Detect dead code using vulture."""
        vulture = Vulture()
        python_files = list(project_path.rglob("*.py"))
        if not python_files:
            return
        vulture.scavenge(python_files)
        unused_code = vulture.get_unused_code()
        for item in unused_code:
            try:
                rel_path = Path(item.filename).relative_to(project_path)
            except ValueError:
                abs_path = Path(item.filename).resolve()
                abs_project = project_path.resolve()
                rel_path = abs_path.relative_to(abs_project)
            if hasattr(item, 'name') and item.name:
                dead_id = f"{rel_path}:{item.name}"
                self.dead_code_items.add(dead_id)
            else:
                dead_id = f"{rel_path}:line_{item.first_lineno}"
                self.dead_code_items.add(dead_id)

    def _analyze_code_structure(self, project_path: Path) -> None:
        python_files = list(project_path.rglob("*.py"))
        all_call_counts = {}
        for py_file in python_files:
            try:
                analyzer = self._get_file_analyzer(py_file, project_path)
                if analyzer:
                    for func_name, count in analyzer.call_counts.items():
                        all_call_counts[func_name] = all_call_counts.get(func_name, 0) + count
            except Exception as e:
                continue
        for py_file in python_files:
            try:
                self._analyze_file(py_file, project_path, all_call_counts)
            except Exception as e:
                continue

    def _get_file_analyzer(self, file_path: Path, project_root: Path) -> 'ASTAnalyzer':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        rel_path = file_path.relative_to(project_root)
        analyzer = ASTAnalyzer(str(rel_path), self.dead_code_items)
        analyzer.visit(tree)
        return analyzer

    def _analyze_file(self, file_path: Path, project_root: Path, all_call_counts: Dict[str, int]) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        rel_path = file_path.relative_to(project_root)
        module_id = str(rel_path)
        self.nodes.append({
            "id": module_id,
            "type": "module",
            "file": str(rel_path),
            "label": rel_path.stem,
            "dead": False,
            "callCount": 0
        })
        analyzer = ASTAnalyzer(str(rel_path), self.dead_code_items)
        analyzer.global_call_counts = all_call_counts
        analyzer.visit(tree)
        self.nodes.extend(analyzer.nodes)
        self.edges.extend(analyzer.edges)


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
    
    dead_code_items = set()
    if python_files:
        vulture.scavenge(python_files)
        unused_code = vulture.get_unused_code()
        print(f"Vulture found {len(unused_code)} unused code items")
        
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
    
    # First pass: count all function calls across all files
    print("First pass: counting function calls...")
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
        except Exception as e:
            print(f"Error in first pass for {py_file}: {e}")
            continue
    
    print(f"Found {len(all_call_counts)} unique function calls")
    
    # Second pass: create nodes and edges
    print("Second pass: creating nodes and edges...")
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

class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor to extract functions, classes, and call relationships."""
    
    def __init__(self, file_path: str, dead_code_items: Set[str]):
        self.file_path = file_path
        self.dead_code_items = dead_code_items
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.current_scope: List[str] = []
        self.function_calls: List[Tuple[str, str]] = []
        self.call_counts: Dict[str, int] = {}  # 함수별 호출 횟수
        self.imports: Dict[str, str] = {}  # import 매핑
        self.global_call_counts: Dict[str, int] = {}  # 전역 호출 횟수
        
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = alias.name
            
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from ... import ... statements."""
        if node.module:
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                self.imports[name] = f"{node.module}.{alias.name}"
                # Import 관계 엣지 추가
                source_id = f"{self.file_path}"
                target_id = f"{node.module}.py:{alias.name}"
                self.edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "IMPORTS"
                })

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        func_name = node.name
        scope_name = ".".join(self.current_scope + [func_name])
        func_id = f"{self.file_path}:{scope_name}"
        
        # Check if this function is dead code
        is_dead = func_id in self.dead_code_items
        
        # 호출 횟수 계산 (전역 호출 횟수 사용)
        call_count = self.global_call_counts.get(func_name, 0)
        
        self.nodes.append({
            "id": func_id,
            "type": "function",
            "file": self.file_path,
            "label": func_name,
            "dead": is_dead,
            "callCount": call_count
        })
        
        # Enter function scope
        self.current_scope.append(func_name)
        
        # Visit function body to find calls
        for stmt in node.body:
            self.visit(stmt)
            
        # Exit function scope
        self.current_scope.pop()
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self.visit_FunctionDef(node)  # Treat same as regular function
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        class_name = node.name
        scope_name = ".".join(self.current_scope + [class_name])
        class_id = f"{self.file_path}:{scope_name}"
        
        # Check if this class is dead code
        is_dead = class_id in self.dead_code_items
        
        # 클래스 호출 횟수 (인스턴스 생성 횟수)
        call_count = self.global_call_counts.get(class_name, 0)
        
        self.nodes.append({
            "id": class_id,
            "type": "class",
            "file": self.file_path,
            "label": class_name,
            "dead": is_dead,
            "callCount": call_count
        })
        
        # Enter class scope
        self.current_scope.append(class_name)
        
        # Visit class body
        for stmt in node.body:
            self.visit(stmt)
            
        # Exit class scope
        self.current_scope.pop()
        
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls."""
        # Extract function name from call
        func_name = self._extract_call_name(node.func)
        if func_name:
            # 호출 횟수 증가
            self.call_counts[func_name] = self.call_counts.get(func_name, 0) + 1
            
            # Record the call for later processing
            current_func = ".".join(self.current_scope) if self.current_scope else "__module__"
            caller_id = f"{self.file_path}:{current_func}"
            
            # 호출 대상 해결 시도
            if func_name in self.imports:
                # Import된 함수인 경우
                imported_path = self.imports[func_name]
                if "." in imported_path:
                    module_name, func_name_resolved = imported_path.rsplit(".", 1)
                    callee_id = f"{module_name}.py:{func_name_resolved}"
                else:
                    callee_id = f"{imported_path}.py:{func_name}"
            else:
                # 같은 모듈의 함수인 경우
                callee_id = f"{self.file_path}:{func_name}"
            
            self.edges.append({
                "source": caller_id,
                "target": callee_id,
                "type": "CALLS"
            })
        
        # Continue visiting child nodes
        self.generic_visit(node)
        
    def _extract_call_name(self, node: ast.AST) -> str:
        """Extract function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For method calls like obj.method()
            return node.attr
        elif isinstance(node, ast.Call):
            # For chained calls
            return self._extract_call_name(node.func)
        return ""


def analyze_python_project(project_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Main entry point for analyzing a Python project.
    
    Args:
        project_path: Path to the Python project root
        
    Returns:
        Dictionary with 'nodes' and 'edges' lists
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_project(project_path)


if __name__ == "__main__":
    # Test the analyzer
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <project_path>")
        sys.exit(1)
        
    project_path = sys.argv[1]
    result = analyze_python_project(project_path)
    
    print("Analysis Results:")
    print(f"Nodes: {len(result['nodes'])}")
    print(f"Edges: {len(result['edges'])}")
    
    # Pretty print results
    print("\nNodes:")
    for node in result['nodes'][:5]:  # Show first 5
        print(f"  {node}")
        
    print("\nEdges:")
    for edge in result['edges'][:5]:  # Show first 5
        print(f"  {edge}")
