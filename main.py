"""
Code Weaver - FastAPI server for Python code analysis and visualization.
Provides endpoints for static code analysis, dead code detection, and graph visualization.
"""

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

from analyzer import analyze_python_project
from db_manager import get_db_manager


# Global in-memory storage (fallback when Neo4j is not available)
memory_storage = {
    "nodes": [],
    "links": [],
    "statistics": {}
}


# Pydantic models for request/response
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
    nodes: list
    links: list


# Initialize FastAPI app
app = FastAPI(
    title="Code Weaver API",
    description="Static code analysis with dead code detection and 3D visualization",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database manager
db = get_db_manager()


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    if not db.connect():
        print("Warning: Could not connect to Neo4j database")
    else:
        print("Connected to Neo4j database successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    db.close()
    print("Database connection closed")


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker container."""
    try:
        # Neo4j 연결 확인
        neo4j_status = "connected" if db.driver else "disconnected"
        
        return {
            "status": "healthy",
            "neo4j": neo4j_status,
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Code Weaver API",
        "version": "1.0.0",
        "description": "Static code analysis with dead code detection",
        "endpoints": {
            "POST /analyze": "Analyze Python project",
            "GET /graph-data": "Get visualization data",
            "GET /statistics": "Get analysis statistics",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Test database connection
    db_connected = False
    try:
        if db.driver:
            with db.driver.session() as session:
                session.run("RETURN 1")
            db_connected = True
    except Exception:
        pass
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "database_connected": db_connected,
        "service": "Code Weaver API"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_project(request: AnalyzeRequest):
    """
    Analyze a Python project for code structure and dead code.
    
    Args:
        request: Analysis request containing project path
        
    Returns:
        Analysis results and statistics
    """
    try:
        # Perform static analysis
        print(f"Starting analysis of project: {request.path}")
        analysis_result = analyze_python_project(request.path)
        
        nodes = analysis_result["nodes"]
        edges = analysis_result["edges"]
        
        print(f"Analysis complete: {len(nodes)} nodes, {len(edges)} edges")
        
        # Try to store in Neo4j, fallback to memory storage
        db_connected = db.driver is not None
        
        if db_connected:
            if not db.clear_database():
                print("Warning: Failed to clear Neo4j database, using memory storage")
                db_connected = False
            elif not db.store_analysis_results(nodes, edges):
                print("Warning: Failed to store in Neo4j, using memory storage")
                db_connected = False
        
        if not db_connected:
            # Store in memory as fallback
            print("Using memory storage for analysis results")
            memory_storage["nodes"] = []
            memory_storage["links"] = []
            
            # Convert nodes to visualization format
            for node in nodes:
                viz_node = {
                    "id": node["id"],
                    "name": node["label"],
                    "file": node["file"],
                    "type": node["type"],
                    "dead": node.get("dead", False),
                    "callCount": 0,  # Will be calculated from edges
                    "size": 3.0 if node["type"] == "class" else 1.5
                }
                memory_storage["nodes"].append(viz_node)
            
            # Convert edges and calculate call counts
            call_counts = {}
            for edge in edges:
                memory_storage["links"].append({
                    "source": edge["source"],
                    "target": edge["target"]
                })
                # Count calls to each target
                target = edge["target"]
                call_counts[target] = call_counts.get(target, 0) + 1
            
            # Update call counts in nodes
            for node in memory_storage["nodes"]:
                node["callCount"] = call_counts.get(node["id"], 0)
                # Adjust size based on call count
                base_size = 3.0 if node["type"] == "class" else 1.5
                node["size"] = base_size + (node["callCount"] * 0.2)
        
        # Get statistics
        if db_connected:
            statistics = db.get_statistics()
        else:
            # Calculate statistics from memory storage
            total_nodes = len(memory_storage["nodes"])
            total_links = len(memory_storage["links"])
            dead_count = len([n for n in memory_storage["nodes"] if n.get("dead", False)])
            
            # Most called functions
            most_called = sorted(
                [n for n in memory_storage["nodes"] if n["callCount"] > 0],
                key=lambda x: x["callCount"],
                reverse=True
            )[:10]
            
            # Type distribution
            type_counts = {}
            for node in memory_storage["nodes"]:
                node_type = node["type"]
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            statistics = {
                "total_nodes": total_nodes,
                "total_relationships": total_links,
                "dead_code_count": dead_count,
                "by_type": type_counts,
                "most_called": [{"name": n["name"], "file": n["file"], "callCount": n["callCount"]} for n in most_called]
            }
            
            memory_storage["statistics"] = statistics
        
        return AnalyzeResponse(
            success=True,
            message=f"Analysis completed successfully for {request.path}",
            nodes_count=len(nodes),
            edges_count=len(edges),
            statistics=statistics
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/graph-data", response_model=GraphDataResponse)
async def get_graph_data():
    """
    Get graph data for Three.js visualization.
    
    Returns:
        Graph data with nodes and links formatted for Three.js
    """
    try:
        graph_data = db.get_graph_data()
        
        return GraphDataResponse(
            nodes=graph_data["nodes"],
            links=graph_data["links"]
        )
        
    except Exception as e:
        print(f"Error retrieving graph data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve graph data: {str(e)}"
        )


@app.get("/statistics")
async def get_statistics():
    """
    Get analysis statistics.
    
    Returns:
        Detailed statistics about the analyzed code
    """
    try:
        statistics = db.get_statistics()
        return statistics
        
    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@app.delete("/clear")
async def clear_database():
    """
    Clear all analysis data from the database.
    
    Returns:
        Success status
    """
    try:
        if db.clear_database():
            return {"success": True, "message": "Database cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear database"
            )
            
    except Exception as e:
        print(f"Error clearing database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
