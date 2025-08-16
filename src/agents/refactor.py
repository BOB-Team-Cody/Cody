"""
AI-powered refactoring agent workflow.
This module implements a code refactoring system with both AI and rule-based suggestions.
"""

import os
import ast
import uuid
from typing import List, Dict, Any
from pathlib import Path

from ..models.analysis_models import RefactorSuggestion, RefactorResult, AnalysisResult
from ..services.message_service import message_service
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class RefactoringAgent:
    """Main refactoring agent using rule-based and AI-powered analysis."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the refactoring agent."""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        logger.info("Refactoring agent initialized")
    
    def refactor_project(self, project_path: str, analysis_result: AnalysisResult, session_id: str = None) -> RefactorResult:
        """Run the complete refactoring workflow."""
        logger.info(f"Starting refactoring workflow for: {project_path}")
        
        try:
            # Helper function for progress reporting
            def report_progress(step: str, progress: int, message: str = None):
                if session_id:
                    message_service.update_progress(session_id, step, progress)
                    if message:
                        message_service.add_message(session_id, message)
            
            # Validate input
            report_progress("Validating input", 5, "🔍 Validating analysis results...")
            if not analysis_result or not analysis_result.nodes:
                logger.warning("No analysis result or nodes provided")
                if session_id:
                    message_service.add_message(session_id, "❌ No analysis data to process")
                return RefactorResult(
                    suggestions=[],
                    original_analysis=analysis_result
                )
            
            report_progress("Analyzing code structure", 15, f"📊 Found {len(analysis_result.nodes)} code elements to analyze")
            
            # Step 1: Identify issues
            report_progress("Identifying issues", 25, "🔎 Scanning for refactoring opportunities...")
            issues = self._identify_issues(analysis_result)
            logger.info(f"Identified {len(issues)} potential issues")
            
            if not issues:
                logger.info("No refactoring opportunities found")
                if session_id:
                    message_service.add_message(session_id, "✨ Code looks good! No major refactoring opportunities found")
                return RefactorResult(
                    suggestions=[],
                    original_analysis=analysis_result
                )
            
            report_progress("Found issues", 35, f"🎯 Identified {len(issues)} potential improvements")
            
            # Step 2: Generate suggestions
            report_progress("Generating suggestions", 50, "🧠 Creating detailed refactoring suggestions...")
            suggestions = []
            total_issues = len(issues)
            
            for i, issue in enumerate(issues):
                try:
                    suggestion = self._create_suggestion_for_issue(issue, project_path)
                    if suggestion:
                        suggestions.append(suggestion)
                        logger.debug(f"Created suggestion {i+1}/{len(issues)}: {suggestion.type}")
                        
                        # Report sub-progress
                        sub_progress = 50 + int((i + 1) / total_issues * 25)
                        if session_id and (i + 1) % 5 == 0:  # Report every 5 suggestions
                            message_service.add_message(session_id, f"💡 Generated {len(suggestions)} suggestions so far...")
                            message_service.update_progress(session_id, "Generating suggestions", sub_progress)
                            
                except Exception as e:
                    logger.error(f"Error creating suggestion for issue {issue}: {e}")
                    if session_id:
                        message_service.add_message(session_id, f"⚠️ Skipped problematic issue: {issue.get('element', 'unknown')}")
                    continue
            
            logger.info(f"Generated {len(suggestions)} refactoring suggestions")
            report_progress("Generated suggestions", 75, f"📝 Created {len(suggestions)} refactoring suggestions")
            
            # Step 3: Validate and rank suggestions
            report_progress("Validating suggestions", 85, "✅ Validating and ranking suggestions by confidence...")
            validated_suggestions = self._validate_suggestions(suggestions)
            logger.info(f"Validated {len(validated_suggestions)} suggestions")
            
            report_progress("Finalizing results", 95, f"🎉 Finalized {len(validated_suggestions)} high-quality suggestions")
            
            return RefactorResult(
                suggestions=validated_suggestions,
                original_analysis=analysis_result
            )
            
        except Exception as e:
            logger.error(f"Error in refactoring workflow: {e}", exc_info=True)
            if session_id:
                message_service.add_message(session_id, f"❌ Error during refactoring: {str(e)}")
                message_service.complete_session(session_id, success=False)
            return RefactorResult(
                suggestions=[],
                original_analysis=analysis_result
            )
    
    def _identify_issues(self, analysis: AnalysisResult) -> List[Dict[str, Any]]:
        """Identify potential refactoring opportunities."""
        issues = []
        
        # Issue 1: Dead code
        dead_nodes = [node for node in analysis.nodes if node.dead]
        for node in dead_nodes:
            issues.append({
                "type": "dead_code",
                "file": node.file,
                "element": node.label,
                "description": f"Dead code detected: {node.label}",
                "node": node
            })
        
        # Issue 2: High usage functions (potential for optimization)
        high_call_nodes = [node for node in analysis.nodes 
                          if node.type == "function" and node.call_count > 5]
        for node in high_call_nodes:
            issues.append({
                "type": "high_usage",
                "file": node.file,
                "element": node.label,
                "description": f"High usage function: {node.label} (called {node.call_count} times)",
                "node": node
            })
        
        # Issue 3: Unused functions (call count = 0 but not marked as dead)
        unused_nodes = [node for node in analysis.nodes 
                       if node.type == "function" and node.call_count == 0 and not node.dead]
        for node in unused_nodes:
            issues.append({
                "type": "unused_function",
                "file": node.file,
                "element": node.label,
                "description": f"Potentially unused function: {node.label}",
                "node": node
            })
        
        # Issue 4: Large modules with many functions
        module_function_count = {}
        for node in analysis.nodes:
            if node.type == "function":
                module = node.file
                module_function_count[module] = module_function_count.get(module, 0) + 1
        
        for module, count in module_function_count.items():
            if count > 10:  # Threshold for "large" module
                issues.append({
                    "type": "large_module",
                    "file": module,
                    "element": f"Module with {count} functions",
                    "description": f"Large module {module} contains {count} functions - consider splitting",
                    "function_count": count
                })
        
        return issues
    
    def _create_suggestion_for_issue(self, issue: Dict[str, Any], project_path: str) -> RefactorSuggestion:
        """Create a refactoring suggestion for a specific issue."""
        try:
            suggestion_id = str(uuid.uuid4())
            
            # Validate issue data
            required_fields = ["type", "file", "element", "description"]
            for field in required_fields:
                if field not in issue:
                    logger.error(f"Missing required field '{field}' in issue: {issue}")
                    return None
            
            # Read the actual file content
            original_code = self._read_file_content(project_path, issue["file"])
            
            # Generate suggestion based on issue type
            try:
                if issue["type"] == "dead_code":
                    suggested_code, reasoning, confidence = self._generate_dead_code_suggestion(issue, original_code)
                elif issue["type"] == "high_usage":
                    suggested_code, reasoning, confidence = self._generate_optimization_suggestion(issue, original_code)
                elif issue["type"] == "unused_function":
                    suggested_code, reasoning, confidence = self._generate_unused_function_suggestion(issue, original_code)
                elif issue["type"] == "large_module":
                    suggested_code, reasoning, confidence = self._generate_module_split_suggestion(issue, original_code)
                else:
                    logger.warning(f"Unknown issue type: {issue['type']}, using generic suggestion")
                    suggested_code, reasoning, confidence = self._generate_generic_suggestion(issue, original_code)
            except Exception as e:
                logger.error(f"Error generating suggestion for issue type {issue['type']}: {e}")
                suggested_code, reasoning, confidence = self._generate_generic_suggestion(issue, original_code)
            
            return RefactorSuggestion(
                id=suggestion_id,
                type=issue["type"],
                target_file=issue["file"],
                target_element=issue["element"],
                description=issue["description"],
                original_code=original_code[:1000],  # Limit size for demo
                suggested_code=suggested_code,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error creating refactoring suggestion: {e}")
            return None
    
    def _read_file_content(self, project_path: str, file_path: str) -> str:
        """Read file content safely."""
        try:
            # Handle both absolute and relative paths
            if Path(file_path).is_absolute():
                full_path = Path(file_path)
            else:
                full_path = Path(project_path) / file_path
            
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit content size for performance
                    return content[:2000] if len(content) > 2000 else content
            else:
                logger.warning(f"File not found: {full_path}")
                return f"# File not found: {file_path}"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"# Error reading file: {str(e)}"
    
    def _generate_dead_code_suggestion(self, issue: Dict[str, Any], original_code: str) -> tuple:
        """Generate suggestion for dead code removal."""
        suggested_code = f"# Dead code removed: {issue['element']}\n# This code was not being used anywhere in the project"
        reasoning = "This code is not being used anywhere in the project and can be safely removed to reduce complexity and maintenance burden."
        confidence = 0.9
        return suggested_code, reasoning, confidence
    
    def _generate_optimization_suggestion(self, issue: Dict[str, Any], original_code: str) -> tuple:
        """Generate optimization suggestion for high-usage functions."""
        node = issue.get("node")
        element = issue["element"]
        call_count = node.call_count if node else "many"
        
        suggested_code = f"""# Optimized version of {element}
# Consider adding memoization or caching for frequently called functions
from functools import lru_cache

@lru_cache(maxsize=128)
def {element}_optimized(*args, **kwargs):
    # Original function logic here
    # This function is called {call_count} times - caching could improve performance
    pass

# Alternative: Consider extracting complex logic into smaller functions
def {element}_helper_1():
    # First part of complex logic
    pass

def {element}_helper_2():
    # Second part of complex logic
    pass

def {element}_refactored():
    # Main function using helper functions
    result1 = {element}_helper_1()
    result2 = {element}_helper_2()
    return combine_results(result1, result2)
"""
        
        reasoning = f"This function is called {call_count} times, which suggests it's a hot path in your code. Consider adding caching, optimization, or breaking it into smaller functions for better maintainability."
        confidence = 0.7
        return suggested_code, reasoning, confidence
    
    def _generate_unused_function_suggestion(self, issue: Dict[str, Any], original_code: str) -> tuple:
        """Generate suggestion for unused functions."""
        element = issue["element"]
        
        suggested_code = f"""# Review: {element} appears to be unused
# Options:
# 1. Remove if truly unused:
#    def {element}(...):  # <- DELETE THIS FUNCTION
#        pass

# 2. If it's a utility function, consider:
#    - Adding documentation
#    - Adding tests
#    - Making it part of a utility module

# 3. If it's an API endpoint or callback, it might be used externally
#    Consider adding a comment explaining its purpose
"""
        
        reasoning = "This function has no internal callers but might be used externally or be part of an API. Review if it's truly unused or needs better documentation."
        confidence = 0.6
        return suggested_code, reasoning, confidence
    
    def _generate_module_split_suggestion(self, issue: Dict[str, Any], original_code: str) -> tuple:
        """Generate suggestion for large module splitting."""
        file_name = Path(issue["file"]).stem
        function_count = issue.get("function_count", 0)
        
        suggested_code = f"""# Module Split Suggestion for {file_name}.py
# This module has {function_count} functions - consider splitting into:

# {file_name}_core.py - Core functionality
# {file_name}_utils.py - Utility functions  
# {file_name}_helpers.py - Helper functions

# Example structure:
# from .{file_name}_core import main_functions
# from .{file_name}_utils import utility_functions
# from .{file_name}_helpers import helper_functions

# Benefits:
# - Better organization
# - Easier testing
# - Reduced coupling
# - Improved maintainability
"""
        
        reasoning = f"This module contains {function_count} functions, which makes it quite large. Splitting it into smaller, focused modules would improve maintainability and make the code easier to understand."
        confidence = 0.5
        return suggested_code, reasoning, confidence
    
    def _generate_generic_suggestion(self, issue: Dict[str, Any], original_code: str) -> tuple:
        """Generate generic refactoring suggestion."""
        suggested_code = f"""# Refactoring suggestion for: {issue['element']}
# Consider reviewing this code for:
# - Code clarity and readability
# - Function size and complexity
# - Proper naming conventions
# - Documentation and comments
# - Error handling
"""
        reasoning = "General code review and refactoring opportunity identified."
        confidence = 0.4
        return suggested_code, reasoning, confidence
    
    def _validate_suggestions(self, suggestions: List[RefactorSuggestion]) -> List[RefactorSuggestion]:
        """Validate and rank suggestions."""
        # Sort by confidence score
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Filter out low-confidence suggestions
        validated = [s for s in suggestions if s.confidence > 0.3]
        
        # Limit to top 20 suggestions to avoid overwhelming the user
        return validated[:20]


# Factory function for creating refactoring agent
def create_refactoring_agent(openai_api_key: str = None) -> RefactoringAgent:
    """Create a refactoring agent instance."""
    return RefactoringAgent(openai_api_key)