"""Data models for code analysis results."""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class CodeNode:
    """Represents a code element (function, class, module)."""
    id: str
    type: str
    file: str
    label: str
    dead: bool
    call_count: int
    class_name: Optional[str] = None
    source_code: Optional[str] = None
    class_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "file": self.file,
            "label": self.label,
            "dead": self.dead,
            "callCount": self.call_count,
            "sourceCode": self.source_code
        }


@dataclass
class CodeEdge:
    """Represents a relationship between code elements."""
    source: str
    target: str
    type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type
        }


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    nodes: List[CodeNode]
    edges: List[CodeEdge]
    project_path: str
    file_count: int
    dead_code_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "project_path": self.project_path,
            "file_count": self.file_count,
            "dead_code_count": self.dead_code_count
        }
    
    @property
    def statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        type_counts = {}
        for node in self.nodes:
            type_counts[node.type] = type_counts.get(node.type, 0) + 1
        
        # Most called functions
        functions_with_calls = [
            node for node in self.nodes 
            if node.type == "function" and node.call_count > 0
        ]
        most_called = sorted(
            functions_with_calls,
            key=lambda x: x.call_count,
            reverse=True
        )[:10]
        
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.edges),
            "dead_code_count": self.dead_code_count,
            "by_type": type_counts,
            "most_called": [
                {
                    "name": node.label,
                    "file": node.file,
                    "callCount": node.call_count
                }
                for node in most_called
            ]
        }