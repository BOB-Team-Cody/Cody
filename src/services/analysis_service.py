"""Analysis service for code analysis operations."""

import ast
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from vulture import Vulture

from ..models.analysis_models import AnalysisResult, CodeNode, CodeEdge
from ..core.exceptions import AnalysisError, FileProcessingError
from ..utils.file_utils import find_python_files, is_excluded_file, safe_read_file
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class AnalysisService:
    """Service for analyzing Python code projects."""
    
    def __init__(self):
        self.dead_code_items: Set[str] = set()
        self.call_counts: Dict[str, int] = {}
    
    def analyze_project(self, project_path: str) -> AnalysisResult:
        """Analyze a Python project for code structure and dead code.
        
        Args:
            project_path: Path to the Python project
            
        Returns:
            Complete analysis result
            
        Raises:
            AnalysisError: If analysis fails
        """
        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise AnalysisError(f"Project path does not exist: {project_path}")
        
        logger.info(f"Starting analysis of project: {project_path}")
        
        try:
            # Find Python files
            python_files = find_python_files(project_path_obj)
            logger.info(f"Found {len(python_files)} Python files")
            
            if not python_files:
                logger.warning("No Python files found in project")
                return AnalysisResult(
                    nodes=[], edges=[], project_path=project_path,
                    file_count=0, dead_code_count=0
                )
            
            # Detect dead code
            self._detect_dead_code(python_files, project_path_obj)
            
            # Count function calls across all files
            self._count_function_calls(python_files)
            
            # Analyze code structure
            nodes, edges = self._analyze_code_structure(python_files, project_path_obj)
            
            result = AnalysisResult(
                nodes=nodes,
                edges=edges,
                project_path=project_path,
                file_count=len(python_files),
                dead_code_count=len(self.dead_code_items)
            )
            
            logger.info(f"Analysis complete: {len(nodes)} nodes, {len(edges)} edges")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AnalysisError(f"Analysis failed: {e}")
    
    def _detect_dead_code(self, python_files: List[Path], project_root: Path) -> None:
        """Detect dead code using vulture."""
        if not python_files:
            return
        
        logger.info("Detecting dead code with vulture...")
        
        try:
            vulture = Vulture()
            vulture.scavenge(python_files)
            unused_code = vulture.get_unused_code()
            
            logger.info(f"Vulture found {len(unused_code)} unused code items")
            
            for item in unused_code:
                try:
                    rel_path = Path(item.filename).relative_to(project_root)
                    if hasattr(item, 'name') and item.name:
                        dead_id = f"{rel_path}:{item.name}"
                        self.dead_code_items.add(dead_id)
                        logger.debug(f"Dead code detected: {dead_id}")
                except ValueError:
                    # Skip files outside project directory
                    continue
                except Exception as e:
                    logger.warning(f"Error processing dead code item: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Dead code detection failed: {e}")
            # Continue analysis without dead code detection
    
    def _count_function_calls(self, python_files: List[Path]) -> None:
        """Count function calls across all files."""
        logger.info("Counting function calls...")
        
        self.call_counts.clear()
        
        for py_file in python_files:
            try:
                content = safe_read_file(py_file)
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func_name = self._extract_call_name(node.func)
                        if func_name:
                            self.call_counts[func_name] = self.call_counts.get(func_name, 0) + 1
                            
            except Exception as e:
                logger.warning(f"Failed to count calls in {py_file}: {e}")
                continue
    
    def _analyze_code_structure(self, python_files: List[Path], project_root: Path) -> tuple[List[CodeNode], List[CodeEdge]]:
        """Analyze code structure and create nodes and edges."""
        logger.info("Analyzing code structure...")
        
        nodes = []
        edges = []
        
        for py_file in python_files:
            if is_excluded_file(py_file):
                continue
            
            try:
                file_nodes, file_edges = self._analyze_single_file(py_file, project_root)
                nodes.extend(file_nodes)
                edges.extend(file_edges)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {py_file}: {e}")
                continue
        
        return nodes, edges
    
    def _analyze_single_file(self, py_file: Path, project_root: Path) -> tuple[List[CodeNode], List[CodeEdge]]:
        """Analyze a single Python file."""
        try:
            content = safe_read_file(py_file)
            tree = ast.parse(content)
        except Exception as e:
            raise FileProcessingError(f"Failed to parse {py_file}: {e}")
        
        rel_path = py_file.relative_to(project_root)
        
        # Create module node
        nodes = [CodeNode(
            id=str(rel_path),
            type="module",
            file=str(rel_path),
            label=rel_path.stem,
            dead=False,
            call_count=0
        )]
        
        # Analyze AST nodes
        analyzer = ASTAnalyzer(
            file_path=str(rel_path),
            dead_code_items=self.dead_code_items,
            call_counts=self.call_counts
        )
        analyzer.visit(tree)
        
        nodes.extend(analyzer.nodes)
        edges = analyzer.edges
        
        return nodes, edges
    
    def _extract_call_name(self, node: ast.AST) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor to extract functions, classes, and call relationships."""
    
    def __init__(self, file_path: str, dead_code_items: Set[str], call_counts: Dict[str, int]):
        self.file_path = file_path
        self.dead_code_items = dead_code_items
        self.call_counts = call_counts
        self.nodes: List[CodeNode] = []
        self.edges: List[CodeEdge] = []
        self.current_scope: List[str] = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        self._process_function(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self._process_function(node)
    
    def _process_function(self, node: ast.FunctionDef) -> None:
        """Process function definition node."""
        func_name = node.name
        scope_name = ".".join(self.current_scope + [func_name])
        func_id = f"{self.file_path}:{scope_name}"
        
        # Check if this function is dead code
        is_dead = func_id in self.dead_code_items
        call_count = self.call_counts.get(func_name, 0)
        
        func_node = CodeNode(
            id=func_id,
            type="function",
            file=self.file_path,
            label=func_name,
            dead=is_dead,
            call_count=call_count
        )
        self.nodes.append(func_node)
        
        # Enter function scope
        self.current_scope.append(func_name)
        
        # Visit function body
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit function scope
        self.current_scope.pop()
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        class_name = node.name
        scope_name = ".".join(self.current_scope + [class_name])
        class_id = f"{self.file_path}:{scope_name}"
        
        # Check if this class is dead code
        is_dead = class_id in self.dead_code_items
        call_count = self.call_counts.get(class_name, 0)
        
        class_node = CodeNode(
            id=class_id,
            type="class",
            file=self.file_path,
            label=class_name,
            dead=is_dead,
            call_count=call_count
        )
        self.nodes.append(class_node)
        
        # Enter class scope
        self.current_scope.append(class_name)
        
        # Visit class body
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit class scope
        self.current_scope.pop()
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls."""
        func_name = self._extract_call_name(node.func)
        if func_name:
            current_func = ".".join(self.current_scope) if self.current_scope else "__module__"
            caller_id = f"{self.file_path}:{current_func}"
            callee_id = f"{self.file_path}:{func_name}"
            
            edge = CodeEdge(
                source=caller_id,
                target=callee_id,
                type="CALLS"
            )
            self.edges.append(edge)
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _extract_call_name(self, node: ast.AST) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None