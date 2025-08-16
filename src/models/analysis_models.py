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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "file": self.file,
            "label": self.label,
            "dead": self.dead,
            "callCount": self.call_count,
            "className": self.class_name
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


@dataclass
class RefactorSuggestion:
    """Represents a refactoring suggestion."""
    id: str
    type: str  # 'extract_method', 'rename', 'remove_dead_code', 'simplify', etc.
    target_file: str
    target_element: str
    description: str
    original_code: str
    suggested_code: str
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "target_file": self.target_file,
            "target_element": self.target_element,
            "description": self.description,
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


@dataclass
class RefactorResult:
    """Complete refactoring result."""
    suggestions: List[RefactorSuggestion]
    original_analysis: AnalysisResult
    refactored_analysis: Optional[AnalysisResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions],
            "original_analysis": self.original_analysis.to_dict(),
            "refactored_analysis": self.refactored_analysis.to_dict() if self.refactored_analysis else None
        }


@dataclass
class RefactoringSession:
    """Represents a refactoring session with progress tracking."""
    id: str
    project_path: str
    status: str  # 'running', 'completed', 'failed'
    start_time: str
    end_time: Optional[str] = None
    current_step: str = ""
    progress_percentage: int = 0
    messages: List[str] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "project_path": self.project_path,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "current_step": self.current_step,
            "progress_percentage": self.progress_percentage,
            "messages": self.messages
        }


@dataclass
class SourceCodeSnapshot:
    """Represents a snapshot of source code for version tracking."""
    id: str
    file_path: str
    content: str
    hash: str
    timestamp: str
    version: str = "original"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "content": self.content,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "version": self.version
        }