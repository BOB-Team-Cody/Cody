"""Analysis controller for handling API requests."""

from typing import Dict, Any
from fastapi import HTTPException, status

from ..models.api_models import AnalyzeRequest, AnalyzeResponse, GraphDataResponse
from ..services.analysis_service import AnalysisService
from ..services.database_service import DatabaseService
from ..core.exceptions import AnalysisError, DatabaseError
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class AnalysisController:
    """Controller for analysis operations."""
    
    def __init__(self, analysis_service: AnalysisService, database_service: DatabaseService):
        self.analysis_service = analysis_service
        self.database_service = database_service
        self.memory_storage = {
            "nodes": [],
            "links": [],
            "statistics": {}
        }
    
    async def analyze_project(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """Handle project analysis request.
        
        Args:
            request: Analysis request
            
        Returns:
            Analysis response
            
        Raises:
            HTTPException: If analysis fails
        """
        try:
            logger.info(f"Starting analysis of project: {request.path}")
            
            # Perform analysis
            result = self.analysis_service.analyze_project(request.path)
            
            # Try to store in database, fallback to memory
            db_connected = self.database_service.is_connected()
            
            if db_connected:
                # Clear and store in database
                if not self.database_service.clear_database():
                    logger.warning("Failed to clear database, using memory storage")
                    db_connected = False
                elif not self.database_service.store_analysis_result(result):
                    logger.warning("Failed to store in database, using memory storage")
                    db_connected = False
            
            if not db_connected:
                # Store in memory as fallback
                logger.info("Using memory storage for analysis results")
                self._store_in_memory(result)
            
            # Get statistics
            if db_connected:
                statistics = self.database_service.get_statistics()
            else:
                statistics = result.statistics
                self.memory_storage["statistics"] = statistics
            
            return AnalyzeResponse(
                success=True,
                message=f"Analysis completed successfully for {request.path}",
                nodes_count=len(result.nodes),
                edges_count=len(result.edges),
                statistics=statistics
            )
            
        except AnalysisError as e:
            logger.error(f"Analysis error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(e)}"
            )
    
    async def get_graph_data(self) -> GraphDataResponse:
        """Get graph data for visualization.
        
        Returns:
            Graph data response
            
        Raises:
            HTTPException: If data retrieval fails
        """
        try:
            if self.database_service.is_connected():
                graph_data = self.database_service.get_graph_data()
            else:
                # Use memory storage
                graph_data = {
                    "nodes": self.memory_storage["nodes"],
                    "links": self.memory_storage["links"]
                }
            
            return GraphDataResponse(
                nodes=graph_data["nodes"],
                links=graph_data["links"]
            )
            
        except Exception as e:
            logger.error(f"Error retrieving graph data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve graph data: {str(e)}"
            )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics.
        
        Returns:
            Statistics data
            
        Raises:
            HTTPException: If statistics retrieval fails
        """
        try:
            if self.database_service.is_connected():
                statistics = self.database_service.get_statistics()
            else:
                # Use memory storage
                statistics = self.memory_storage.get("statistics", {})
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve statistics: {str(e)}"
            )
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all analysis data.
        
        Returns:
            Success status
            
        Raises:
            HTTPException: If clearing fails
        """
        try:
            if self.database_service.is_connected():
                if self.database_service.clear_database():
                    return {"success": True, "message": "Database cleared successfully"}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to clear database"
                    )
            else:
                # Clear memory storage
                self.memory_storage = {
                    "nodes": [],
                    "links": [],
                    "statistics": {}
                }
                return {"success": True, "message": "Memory storage cleared successfully"}
                
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to clear data: {str(e)}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check.
        
        Returns:
            Health status
        """
        db_health = self.database_service.health_check()
        
        overall_status = "healthy" if db_health.get("database_connected", False) else "degraded"
        
        return {
            "status": overall_status,
            "database_connected": db_health.get("database_connected", False),
            "service": "Code Weaver API",
            "database_status": db_health.get("status", "unknown")
        }
    
    def _store_in_memory(self, result) -> None:
        """Store analysis result in memory."""
        self.memory_storage["nodes"] = []
        self.memory_storage["links"] = []
        
        # Convert nodes to visualization format
        for node in result.nodes:
            viz_node = {
                "id": node.id,
                "name": node.label,
                "file": node.file,
                "type": node.type,
                "dead": node.dead,
                "callCount": node.call_count,
                "className": node.class_name,
                "size": 3.0 if node.type == "class" else (1.5 + node.call_count * 0.2)
            }
            self.memory_storage["nodes"].append(viz_node)
        
        # Convert edges
        call_counts = {}
        for edge in result.edges:
            self.memory_storage["links"].append({
                "source": edge.source,
                "target": edge.target
            })
            # Count calls to each target
            target = edge.target
            call_counts[target] = call_counts.get(target, 0) + 1
        
        # Update call counts in nodes
        for node in self.memory_storage["nodes"]:
            actual_calls = call_counts.get(node["id"], 0)
            if actual_calls > 0:
                node["callCount"] = max(node["callCount"], actual_calls)
            # Adjust size based on actual call count
            base_size = 3.0 if node["type"] == "class" else 1.5
            node["size"] = base_size + (node["callCount"] * 0.2)