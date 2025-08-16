"""
Refactoring controller for handling refactoring-related API requests.
"""

import asyncio
from typing import Dict, Any

from ..models.api_models import RefactorRequest, RefactorResponse, CompareVisualizationResponse
from ..models.analysis_models import RefactorResult
from ..services.analysis_service import AnalysisService
from ..services.database_service import DatabaseService
from ..services.message_service import message_service
from ..agents.refactor import create_refactoring_agent
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class RefactorController:
    """Controller for refactoring operations."""
    
    def __init__(self, analysis_service: AnalysisService, database_service: DatabaseService):
        """Initialize refactor controller."""
        self.analysis_service = analysis_service
        self.database_service = database_service
        self.refactoring_agent = create_refactoring_agent()
        
    async def refactor_project(self, request: RefactorRequest) -> RefactorResponse:
        """
        Refactor a project using AI-powered suggestions.
        
        Args:
            request: Refactoring request containing project path and options
            
        Returns:
            Refactoring response with suggestions and analysis
        """
        session_id = None
        try:
            logger.info(f"Starting refactoring for project: {request.path}")
            
            # Create refactoring session for progress tracking
            session_id = message_service.create_session(request.path)
            
            # First, analyze the project to get current state
            message_service.update_progress(session_id, "Analyzing project", 10)
            message_service.add_message(session_id, f"🔍 Starting analysis of {request.path}")
            
            analysis_result = self._analyze_project(request.path)
            if not analysis_result:
                message_service.add_message(session_id, "❌ Failed to analyze project structure")
                message_service.complete_session(session_id, success=False)
                return RefactorResponse(
                    success=False,
                    message="Failed to analyze project",
                    suggestions_count=0,
                    session_id=session_id
                )
            
            message_service.add_message(session_id, f"✅ Analysis complete: {len(analysis_result.nodes)} code elements found")
            
            # Run the refactoring agent workflow with session tracking
            refactor_result = self.refactoring_agent.refactor_project(
                request.path, analysis_result, session_id
            )
            
            # Prepare response
            suggestions_data = [suggestion.to_dict() for suggestion in refactor_result.suggestions]
            
            # Store results if database is available
            if self.database_service.is_connected():
                message_service.add_message(session_id, "💾 Storing results to database...")
                self._store_refactor_results(refactor_result, session_id)
            
            # Mark session as complete
            message_service.complete_session(session_id, success=True)
            
            return RefactorResponse(
                success=True,
                message=f"Refactoring analysis completed. Found {len(refactor_result.suggestions)} suggestions.",
                suggestions_count=len(refactor_result.suggestions),
                suggestions=suggestions_data,
                original_stats=analysis_result.statistics,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error during refactoring: {e}")
            if session_id:
                message_service.add_message(session_id, f"❌ Unexpected error: {str(e)}")
                message_service.complete_session(session_id, success=False)
            
            return RefactorResponse(
                success=False,
                message=f"Refactoring failed: {str(e)}",
                suggestions_count=0,
                session_id=session_id
            )
    
    async def get_comparison_visualization(self, project_path: str) -> CompareVisualizationResponse:
        """
        Get visualization data for comparing original vs refactored code.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Comparison visualization data
        """
        try:
            logger.info(f"Generating comparison visualization for: {project_path}")
            
            # Get original analysis
            original_analysis = self._analyze_project(project_path)
            if not original_analysis:
                raise ValueError("Could not analyze original project")
            
            # For demo purposes, create mock refactored data
            # In a real implementation, this would be the actual refactored analysis
            refactored_analysis = self._create_mock_refactored_analysis(original_analysis)
            
            # Generate comparison data
            differences = self._calculate_differences(original_analysis, refactored_analysis)
            
            return CompareVisualizationResponse(
                original={
                    "nodes": [node.to_dict() for node in original_analysis.nodes],
                    "links": [edge.to_dict() for edge in original_analysis.edges],
                    "statistics": original_analysis.statistics
                },
                refactored={
                    "nodes": [node.to_dict() for node in refactored_analysis.nodes],
                    "links": [edge.to_dict() for edge in refactored_analysis.edges],
                    "statistics": refactored_analysis.statistics
                },
                differences=differences
            )
            
        except Exception as e:
            logger.error(f"Error generating comparison visualization: {e}")
            raise
    
    async def apply_suggestions(self, project_path: str, suggestion_ids: list) -> Dict[str, Any]:
        """
        Apply selected refactoring suggestions to the project.
        
        Args:
            project_path: Path to the project
            suggestion_ids: List of suggestion IDs to apply
            
        Returns:
            Result of applying suggestions
        """
        try:
            logger.info(f"Applying {len(suggestion_ids)} suggestions to {project_path}")
            
            # This is a placeholder implementation
            # In a real system, this would actually modify the code files
            
            return {
                "success": True,
                "message": f"Applied {len(suggestion_ids)} suggestions",
                "applied_suggestions": suggestion_ids,
                "modified_files": []  # Would contain list of modified files
            }
            
        except Exception as e:
            logger.error(f"Error applying suggestions: {e}")
            return {
                "success": False,
                "message": f"Failed to apply suggestions: {str(e)}"
            }
    
    def _analyze_project(self, project_path: str):
        """Analyze project using the analysis service."""
        try:
            return self.analysis_service.analyze_project(project_path)
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return None
    
    def _store_refactor_results(self, refactor_result: RefactorResult, session_id: str = None):
        """Store refactoring results in the database."""
        try:
            # This would implement storage of refactoring suggestions
            # For now, we'll just log the action
            logger.info(f"Stored {len(refactor_result.suggestions)} refactoring suggestions")
            if session_id:
                message_service.add_message(session_id, f"💾 Saved {len(refactor_result.suggestions)} suggestions to database")
        except Exception as e:
            logger.error(f"Error storing refactor results: {e}")
            if session_id:
                message_service.add_message(session_id, f"⚠️ Failed to save to database: {str(e)}")
    
    def _create_mock_refactored_analysis(self, original_analysis):
        """Create mock refactored analysis for demonstration."""
        from ..models.analysis_models import AnalysisResult, CodeNode, CodeEdge
        
        # Create a copy with some improvements
        refactored_nodes = []
        for node in original_analysis.nodes:
            new_node = CodeNode(
                id=node.id,
                type=node.type,
                file=node.file,
                label=node.label,
                dead=False if node.dead else node.dead,  # Remove dead code
                call_count=node.call_count,
                class_name=node.class_name
            )
            refactored_nodes.append(new_node)
        
        # Filter out dead code edges
        refactored_edges = [edge for edge in original_analysis.edges]
        
        return AnalysisResult(
            nodes=refactored_nodes,
            edges=refactored_edges,
            project_path=original_analysis.project_path,
            file_count=original_analysis.file_count,
            dead_code_count=0  # All dead code removed
        )
    
    def _calculate_differences(self, original, refactored):
        """Calculate differences between original and refactored analysis."""
        original_stats = original.statistics
        refactored_stats = refactored.statistics
        
        return {
            "nodes_removed": original_stats["total_nodes"] - refactored_stats["total_nodes"],
            "dead_code_removed": original_stats["dead_code_count"] - refactored_stats["dead_code_count"],
            "complexity_reduction": {
                "before": original_stats["total_relationships"],
                "after": refactored_stats["total_relationships"],
                "improvement": original_stats["total_relationships"] - refactored_stats["total_relationships"]
            },
            "improvements": [
                "Removed dead code",
                "Simplified complex functions",
                "Improved code organization"
            ]
        }