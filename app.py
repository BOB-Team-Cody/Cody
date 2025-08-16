"""
Code Weaver - Main FastAPI application.
Modern layered architecture with dependency injection.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.responses import JSONResponse

from src.models.api_models import AnalyzeRequest, AnalyzeResponse, GraphDataResponse
from src.services.analysis_service import AnalysisService
from src.services.database_service import DatabaseService
from src.controllers.analysis_controller import AnalysisController
from src.utils.logging_utils import setup_logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger(__name__)

# Global services - will be initialized in lifespan
analysis_service: AnalysisService = None
database_service: DatabaseService = None
analysis_controller: AnalysisController = None
refactoring_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global analysis_service, database_service, analysis_controller, refactoring_agent
    
    # Startup
    logger.info("Starting Code Weaver API...")
    
    # Initialize services
    analysis_service = AnalysisService()
    database_service = DatabaseService()
    
    # Try to connect to database
    if not database_service.connect():
        logger.warning("Could not connect to Neo4j database - using memory storage")
    else:
        logger.info("Connected to Neo4j database successfully")
    
    # Initialize controller
    analysis_controller = AnalysisController(analysis_service, database_service)
    
    # Initialize refactoring agent
    try:
        from src.agents.refactoring_agent import CodeRefactoringAgent
        refactoring_agent = CodeRefactoringAgent(database_service)
        logger.info("Code refactoring agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize refactoring agent: {e}")
        refactoring_agent = None
    
    logger.info("Code Weaver API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Code Weaver API...")
    if database_service:
        database_service.disconnect()
    logger.info("Code Weaver API shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Code Weaver API",
    description="Static code analysis with dead code detection and 3D visualization",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS from environment
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount frontend build files (production only)
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=frontend_dist), name="static")


# Dependency injection
def get_analysis_controller() -> AnalysisController:
    """Dependency injection for analysis controller."""
    if analysis_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized"
        )
    return analysis_controller


# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Code Weaver API",
        "version": "2.0.0",
        "description": "Static code analysis with dead code detection and 3D visualization",
        "architecture": "Layered architecture with dependency injection",
        "endpoints": {
            "POST /analyze": "Analyze Python project",
            "GET /graph-data": "Get visualization data",
            "GET /statistics": "Get analysis statistics",
            "GET /health": "Health check",
            "DELETE /clear": "Clear analysis data",
            "GET /functions/search/{function_name}": "Search functions by name",
            "GET /functions/id/{function_id}": "Get function by ID",
            "GET /functions/file/{file_path}": "Get functions by file",
            "GET /refactor/{function_id}": "Refactor function with LangGraph agent",
            "GET /docs": "API documentation"
        }
    }


@app.get("/health")
async def health_check(controller: AnalysisController = Depends(get_analysis_controller)):
    """Health check endpoint."""
    return await controller.health_check()


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_project(
    request: AnalyzeRequest,
    controller: AnalysisController = Depends(get_analysis_controller)
):
    """
    Analyze a Python project for code structure and dead code.
    
    Args:
        request: Analysis request containing project path
        
    Returns:
        Analysis results and statistics
    """
    return await controller.analyze_project(request)


@app.get("/graph-data", response_model=GraphDataResponse)
async def get_graph_data(controller: AnalysisController = Depends(get_analysis_controller)):
    """
    Get graph data for Three.js visualization.
    
    Returns:
        Graph data with nodes and links formatted for Three.js
    """
    return await controller.get_graph_data()


@app.get("/statistics")
async def get_statistics(controller: AnalysisController = Depends(get_analysis_controller)):
    """
    Get analysis statistics.
    
    Returns:
        Detailed statistics about the analyzed code
    """
    return await controller.get_statistics()


@app.delete("/clear")
async def clear_data(controller: AnalysisController = Depends(get_analysis_controller)):
    """
    Clear all analysis data.
    
    Returns:
        Success status
    """
    return await controller.clear_database()


@app.get("/functions/search/{function_name}")
async def search_functions(
    function_name: str,
    controller: AnalysisController = Depends(get_analysis_controller)
):
    """
    Search for functions by name pattern.
    
    Args:
        function_name: Name or pattern to search for
        
    Returns:
        List of matching functions with their source code
    """
    return await controller.search_functions_by_name(function_name)


@app.get("/functions/id/{function_id:path}")
async def get_function_by_id(
    function_id: str,
    controller: AnalysisController = Depends(get_analysis_controller)
):
    """
    Get a specific function by its ID.
    
    Args:
        function_id: The function ID to search for
        
    Returns:
        Function data with source code
    """
    return await controller.get_function_by_id(function_id)


@app.get("/functions/file/{file_path:path}")
async def get_functions_by_file(
    file_path: str,
    controller: AnalysisController = Depends(get_analysis_controller)
):
    """
    Get all functions in a specific file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of functions in the file with their source code
    """
    return await controller.search_functions_by_file(file_path)


@app.get("/refactor")
async def refactor_function(function_id: str):
    """
    Refactor a function using LangGraph-based agent.
    
    Args:
        function_id: The function ID to refactor (as query parameter)
        
    Returns:
        Streaming response with refactoring progress and results
    """
    if refactoring_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Refactoring agent not available. Check OPENAI_API_KEY environment variable."
        )
    
    async def generate_refactoring_stream():
        """Generator for streaming refactoring updates."""
        import json
        
        try:
            async for update in refactoring_agent.refactor_function(function_id):
                # Format as Server-Sent Events
                data = json.dumps(update, ensure_ascii=False)
                yield f"data: {data}\n\n"
                
        except Exception as e:
            logger.error(f"Error in refactoring stream: {e}")
            error_data = json.dumps({
                "error": str(e),
                "step": "stream_error",
                "type": "error"
            })
            yield f"data: {error_data}\n\n"
        
        # Signal end of stream
        yield f"data: {json.dumps({'step': 'stream_end', 'type': 'end'})}\n\n"
    
    return StreamingResponse(
        generate_refactoring_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )


@app.get("/frontend")
async def serve_frontend():
    """Serve the frontend application (production build)."""
    frontend_index = Path(__file__).parent / "frontend" / "dist" / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    else:
        return {
            "message": "Frontend not built",
            "instruction": "Run 'npm run build' in the frontend directory",
            "development": "For development, run 'npm run dev' in frontend directory on port 3000"
        }


# Legacy compatibility endpoint
@app.get("/docs-legacy")
async def legacy_docs():
    """Legacy API documentation reference."""
    return {
        "message": "This is Code Weaver API v2.0 with improved architecture",
        "changes": [
            "Layered architecture with separation of concerns",
            "Dependency injection for better testability",
            "Improved error handling and logging",
            "Better memory management and fallback mechanisms",
            "Enhanced data models with validation"
        ],
        "migration": "All existing endpoints remain compatible",
        "new_features": [
            "Better dead code detection",
            "Improved performance",
            "Enhanced visualization data",
            "More detailed statistics"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )