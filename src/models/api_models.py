"""API request/response models."""

from pydantic import BaseModel, validator
from pathlib import Path
from typing import Dict, Any, List


class AnalyzeRequest(BaseModel):
    """Request model for code analysis."""
    path: str
    
    @validator('path')
    def validate_path(cls, v):
        """Validate that the path exists and is a directory."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Path does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return str(path.absolute())


class AnalyzeResponse(BaseModel):
    """Response model for code analysis."""
    success: bool
    message: str
    nodes_count: int = 0
    edges_count: int = 0
    statistics: Dict[str, Any] = {}


class GraphDataResponse(BaseModel):
    """Response model for graph data."""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]


class NodeData(BaseModel):
    """Model for individual node data."""
    id: str
    name: str
    file: str
    type: str
    dead: bool
    call_count: int
    size: float


class LinkData(BaseModel):
    """Model for individual link data."""
    source: str
    target: str