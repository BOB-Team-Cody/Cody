"""
LangGraph-based code refactoring agent.

This module implements a multi-step code refactoring workflow using LangGraph,
which analyzes code from Neo4j database and provides intelligent refactoring suggestions.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from ..services.database_service import DatabaseService
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class RefactoringState:
    """State object for the refactoring workflow."""
    function_id: str
    source_code: str
    function_name: str
    file_path: str
    context_functions: List[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]] = None
    refactoring_suggestions: Optional[List[Dict[str, Any]]] = None
    refactored_code: Optional[str] = None
    validation_result: Optional[Dict[str, Any]] = None
    current_step: str = ""
    llm_responses: List[str] = None
    
    def __post_init__(self):
        if self.llm_responses is None:
            self.llm_responses = []


class CodeRefactoringAgent:
    """LangGraph-based code refactoring agent."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize the refactoring agent.
        
        Args:
            database_service: Service for database operations
        """
        self.database_service = database_service
        self.llm = self._initialize_llm()
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the LLM."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=api_key,
            streaming=True
        )
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for code refactoring."""
        workflow = StateGraph(Dict[str, Any])
        
        # Add nodes
        workflow.add_node("analyze_code", self._analyze_code_node)
        workflow.add_node("generate_suggestions", self._generate_suggestions_node)
        workflow.add_node("refactor_code", self._refactor_code_node)
        workflow.add_node("validate_refactoring", self._validate_refactoring_node)
        
        # Add edges
        workflow.add_edge(START, "analyze_code")
        workflow.add_edge("analyze_code", "generate_suggestions")
        workflow.add_edge("generate_suggestions", "refactor_code")
        workflow.add_edge("refactor_code", "validate_refactoring")
        workflow.add_edge("validate_refactoring", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _analyze_code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the target code and its context."""
        logger.info(f"Analyzing code for function: {state['function_name']}")
        
        state["current_step"] = "analyze_code"
        
        # Create analysis prompt
        context_info = ""
        if state["context_functions"]:
            context_info = "\n".join([
                f"- {func['name']} (calls: {func.get('callCount', 0)}, dead: {func.get('dead', False)})"
                for func in state["context_functions"][:10]  # Limit context
            ])
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code analyst specializing in Python code quality and maintainability.
            Analyze the provided function and its context to identify areas for improvement.
            
            Focus on:
            1. Code complexity and readability
            2. Naming conventions
            3. Function length and single responsibility
            4. Potential performance issues
            5. Code duplication or patterns
            6. Error handling
            7. Documentation quality
            
            Provide a detailed analysis explaining what you found and what could be improved.
            Be specific and actionable in your recommendations."""),
            ("human", """Analyze this Python function:

Function Name: {function_name}
File Path: {file_path}
Source Code:
```python
{source_code}
```

Context (related functions in the same file):
{context_info}

Please provide a comprehensive analysis of this function, highlighting specific issues and improvement opportunities.""")
        ])
        
        try:
            messages = analysis_prompt.format_messages(
                function_name=state["function_name"],
                file_path=state["file_path"],
                source_code=state["source_code"],
                context_info=context_info or "No related functions found."
            )
            
            response = await self.llm.ainvoke(messages)
            analysis_content = response.content
            
            # Store the LLM response
            state["llm_responses"].append(analysis_content)
            
            # Try to extract structured data for internal use
            try:
                import json
                # Look for JSON in the response
                if "{" in analysis_content and "}" in analysis_content:
                    json_start = analysis_content.find("{")
                    json_end = analysis_content.rfind("}") + 1
                    json_part = analysis_content[json_start:json_end]
                    analysis_result = json.loads(json_part)
                else:
                    # Fallback to text analysis
                    analysis_result = {
                        "analysis": analysis_content,
                        "issues": []
                    }
            except (json.JSONDecodeError, ValueError):
                # Fallback to text analysis
                analysis_result = {
                    "analysis": analysis_content,
                    "issues": []
                }
            
            state["analysis_result"] = analysis_result
            
        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            error_message = f"Error during code analysis: {str(e)}"
            state["analysis_result"] = {"error": error_message}
            state["llm_responses"].append(error_message)
        
        return state
    
    async def _generate_suggestions_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate refactoring suggestions based on analysis."""
        logger.info(f"Generating refactoring suggestions for: {state['function_name']}")
        
        state["current_step"] = "generate_suggestions"
        
        suggestions_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code refactoring consultant.
            Based on the code analysis, generate specific, actionable refactoring suggestions.
            
            Each suggestion should include:
            1. Type of refactoring (extract method, rename, simplify, etc.)
            2. Priority (high, medium, low)
            3. Description of the improvement
            4. Specific code changes needed
            5. Benefits of the change
            
            Be detailed and explain your reasoning for each suggestion."""),
            ("human", """Based on this analysis of function '{function_name}':

Analysis Result:
{analysis_result}

Original Code:
```python
{source_code}
```

Generate specific refactoring suggestions with detailed explanations for each improvement.""")
        ])
        
        try:
            analysis_text = str(state["analysis_result"]) if state["analysis_result"] else "No analysis available"
            
            messages = suggestions_prompt.format_messages(
                function_name=state["function_name"],
                analysis_result=analysis_text,
                source_code=state["source_code"]
            )
            
            response = await self.llm.ainvoke(messages)
            suggestions_content = response.content
            
            # Store the LLM response
            state["llm_responses"].append(suggestions_content)
            
            # Try to extract structured suggestions for internal use
            try:
                import json
                import re
                
                # Look for JSON array in the response
                json_match = re.search(r'\[.*\]', suggestions_content, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                    if not isinstance(suggestions, list):
                        suggestions = [suggestions]
                else:
                    # Fallback to text suggestions
                    suggestions = [{
                        "type": "general",
                        "priority": "medium",
                        "description": suggestions_content,
                        "changes": "See description",
                        "benefits": "Improved code quality"
                    }]
            except (json.JSONDecodeError, ValueError):
                # Fallback to text suggestions
                suggestions = [{
                    "type": "general",
                    "priority": "medium",
                    "description": suggestions_content,
                    "changes": "See description",
                    "benefits": "Improved code quality"
                }]
            
            state["refactoring_suggestions"] = suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            error_message = f"Error generating refactoring suggestions: {str(e)}"
            state["refactoring_suggestions"] = []
            state["llm_responses"].append(error_message)
        
        return state
    
    async def _refactor_code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply refactoring suggestions to generate improved code."""
        logger.info(f"Refactoring code for: {state['function_name']}")
        
        state["current_step"] = "refactor_code"
        
        refactoring_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Python developer performing code refactoring.
            Apply the suggested improvements to the original code.
            
            Guidelines:
            1. Maintain the same functionality
            2. Improve readability and maintainability
            3. Follow Python best practices and PEP 8
            4. Add proper documentation and type hints
            5. Ensure the refactored code is production-ready
            
            Explain your refactoring decisions and then provide the complete refactored code."""),
            ("human", """Refactor this Python function based on the analysis and suggestions:

Original Code:
```python
{source_code}
```

Analysis and Suggestions:
{suggestions}

Please explain your refactoring approach and then provide the complete improved function:""")
        ])
        
        try:
            suggestions_text = ""
            if state["refactoring_suggestions"]:
                for i, suggestion in enumerate(state["refactoring_suggestions"], 1):
                    suggestions_text += f"{i}. {suggestion.get('type', 'Unknown')}: {suggestion.get('description', 'No description')}\n"
            else:
                suggestions_text = "No specific suggestions available. Apply general best practices."
            
            messages = refactoring_prompt.format_messages(
                source_code=state["source_code"],
                suggestions=suggestions_text
            )
            
            response = await self.llm.ainvoke(messages)
            refactoring_content = response.content
            
            # Store the LLM response
            state["llm_responses"].append(refactoring_content)
            
            # Extract code from response (remove markdown formatting if present)
            refactored_code = refactoring_content
            if "```python" in refactored_code:
                code_blocks = refactored_code.split("```python")
                if len(code_blocks) > 1:
                    refactored_code = code_blocks[1].split("```")[0].strip()
            elif "```" in refactored_code:
                code_blocks = refactored_code.split("```")
                if len(code_blocks) >= 3:
                    refactored_code = code_blocks[1].strip()
            
            state["refactored_code"] = refactored_code
            
        except Exception as e:
            logger.error(f"Error refactoring code: {e}")
            error_message = f"Error during code refactoring: {str(e)}"
            state["refactored_code"] = state["source_code"]  # Fallback to original
            state["llm_responses"].append(error_message)
        
        return state
    
    async def _validate_refactoring_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the refactored code and provide final assessment."""
        logger.info(f"Validating refactored code for: {state['function_name']}")
        
        state["current_step"] = "validate_refactoring"
        
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code quality validator.
            Compare the original and refactored code to assess improvements.
            
            Evaluate:
            1. Syntax correctness
            2. Functionality preservation
            3. Code quality improvements
            4. Readability enhancements
            5. Potential issues or regressions
            
            Provide a detailed assessment explaining the validation results and overall quality improvements."""),
            ("human", """Validate this refactoring:

Original Code:
```python
{original_code}
```

Refactored Code:
```python
{refactored_code}
```

Please provide a comprehensive validation assessment of the refactoring quality and improvements.""")
        ])
        
        try:
            messages = validation_prompt.format_messages(
                original_code=state["source_code"],
                refactored_code=state["refactored_code"] or "No refactored code available"
            )
            
            response = await self.llm.ainvoke(messages)
            validation_content = response.content
            
            # Store the LLM response
            state["llm_responses"].append(validation_content)
            
            # Try to extract structured validation for internal use
            try:
                import json
                import re
                
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', validation_content, re.DOTALL)
                if json_match:
                    validation_result = json.loads(json_match.group())
                else:
                    validation_result = {
                        "validation": validation_content,
                        "quality_score": 8
                    }
            except (json.JSONDecodeError, ValueError):
                validation_result = {
                    "validation": validation_content,
                    "quality_score": 8
                }
            
            state["validation_result"] = validation_result
            
        except Exception as e:
            logger.error(f"Error validating refactoring: {e}")
            error_message = f"Error during validation: {str(e)}"
            state["validation_result"] = {"error": error_message}
            state["llm_responses"].append(error_message)
        
        return state
    
    async def refactor_function(self, function_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Refactor a function using the LangGraph workflow.
        
        Args:
            function_id: ID of the function to refactor
            
        Yields:
            Streaming updates from the workflow execution
        """
        try:
            # Get function data from database
            function_data = self.database_service.get_function_by_id(function_id)
            if not function_data:
                yield {
                    "error": f"Function with ID '{function_id}' not found",
                    "step": "initialization"
                }
                return
            
            # Get related functions for context
            context_functions = self.database_service.search_functions_by_file(
                function_data["file"]
            )
            
            # Initialize state
            initial_state = {
                "function_id": function_id,
                "source_code": function_data["sourceCode"] or "",
                "function_name": function_data["name"],
                "file_path": function_data["file"],
                "context_functions": context_functions,
                "analysis_result": None,
                "refactoring_suggestions": None,
                "refactored_code": None,
                "validation_result": None,
                "current_step": "",
                "llm_responses": []
            }
            
            # Configure workflow
            config = {
                "configurable": {"thread_id": f"refactor_{function_id}"}
            }
            
            # Track previous response count to detect new LLM responses
            previous_response_count = 0
            
            # Stream workflow execution
            async for chunk in self.workflow.astream(initial_state, config, stream_mode="updates"):
                for node_name, node_state in chunk.items():
                    if node_name != "__end__":
                        # Check for new LLM responses
                        if ("llm_responses" in node_state and 
                            len(node_state["llm_responses"]) > previous_response_count):
                            
                            # Yield new LLM responses
                            for i in range(previous_response_count, len(node_state["llm_responses"])):
                                yield {
                                    "step": node_state["current_step"],
                                    "content": node_state["llm_responses"][i],
                                    "node": node_name,
                                    "type": "llm_response"
                                }
                            
                            previous_response_count = len(node_state["llm_responses"])
                        
                        # Yield specific results when workflow completes
                        if node_name == "validate_refactoring":
                            yield {
                                "step": "workflow_complete",
                                "type": "final_result",
                                "result": {
                                    "function_name": node_state["function_name"],
                                    "file_path": node_state["file_path"],
                                    "original_code": node_state["source_code"],
                                    "refactored_code": node_state["refactored_code"],
                                    "suggestions": node_state["refactoring_suggestions"],
                                    "analysis": node_state["analysis_result"],
                                    "validation": node_state["validation_result"],
                                    "llm_responses": node_state["llm_responses"]
                                }
                            }
            
        except Exception as e:
            logger.error(f"Error in refactoring workflow: {e}")
            yield {
                "error": str(e),
                "step": "workflow_error",
                "type": "error"
            }
