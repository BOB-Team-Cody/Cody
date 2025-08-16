"""Database service for Neo4j operations."""

import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

from ..models.analysis_models import AnalysisResult, CodeNode, CodeEdge
from ..core.exceptions import DatabaseError
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class DatabaseService:
    """Service for database operations with Neo4j."""
    
    def __init__(self, 
                 uri: Optional[str] = None, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None):
        """Initialize database service.
        
        Args:
            uri: Neo4j database URI
            username: Database username
            password: Database password
        """
        # Read from environment variables with fallbacks
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "codycody")
        self.driver: Optional[Driver] = None
        self._connected = False
    
    def connect(self) -> bool:
        """Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            self._connected = True
            logger.info("Connected to Neo4j database successfully")
            return True
            
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            self._connected = False
            logger.info("Database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected and self.driver is not None
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check.
        
        Returns:
            Health status information
        """
        if not self.is_connected():
            return {
                "status": "disconnected",
                "database_connected": False,
                "message": "No database connection"
            }
        
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
            return {
                "status": "healthy",
                "database_connected": True,
                "message": "Database connection is healthy"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "database_connected": False,
                "message": f"Health check failed: {str(e)}"
            }
    
    def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            with self.driver.session() as session:
                # Delete all relationships first
                session.run("MATCH ()-[r]-() DELETE r")
                # Then delete all nodes
                session.run("MATCH (n) DELETE n")
                
                # Create indexes for better performance
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:Function) ON (n.id)")
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:Class) ON (n.id)")
                session.run("CREATE INDEX IF NOT EXISTS FOR (n:Module) ON (n.id)")
                
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False
    
    def store_analysis_result(self, result: AnalysisResult) -> bool:
        """Store analysis result in the database.
        
        Args:
            result: Analysis result to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            with self.driver.session() as session:
                # Store nodes
                for node in result.nodes:
                    self._create_node(session, node)
                
                # Store edges
                for edge in result.edges:
                    self._create_relationship(session, edge)
            
            logger.info(f"Stored {len(result.nodes)} nodes and {len(result.edges)} edges")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return False
    
    def _create_node(self, session, node: CodeNode) -> None:
        """Create a node in the database."""
        node_type = node.type.title()
        
        if node_type == "Function":
            query = """
            MERGE (n:Function {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type,
                n.callCount = $callCount
            """
        elif node_type == "Class":
            query = """
            MERGE (n:Class {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type,
                n.callCount = $callCount
            """
        elif node_type == "Module":
            query = """
            MERGE (n:Module {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type,
                n.callCount = $callCount
            """
        else:
            query = """
            MERGE (n:CodeElement {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type,
                n.callCount = $callCount
            """
        
        session.run(query, {
            "id": node.id,
            "label": node.label,
            "file": node.file,
            "dead": node.dead,
            "type": node.type,
            "callCount": node.call_count
        })
    
    def _create_relationship(self, session, edge: CodeEdge) -> None:
        """Create a relationship between nodes."""
        query = """
        MATCH (source {id: $source_id})
        MATCH (target {id: $target_id})
        MERGE (source)-[:CALLS]->(target)
        """
        
        session.run(query, {
            "source_id": edge.source,
            "target_id": edge.target
        })
    
    def get_graph_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve all graph data for visualization.
        
        Returns:
            Dictionary with 'nodes' and 'links' for Three.js
        """
        if not self.is_connected():
            logger.warning("Not connected to database, returning empty data")
            return {"nodes": [], "links": []}
        
        try:
            with self.driver.session() as session:
                # Get all nodes with call counts
                nodes_query = """
                MATCH (n)
                OPTIONAL MATCH (n)<-[:CALLS]-(caller)
                WITH n, COUNT(caller) as incomingCalls
                RETURN n.id as id, 
                       n.name as name, 
                       n.file as file, 
                       n.type as type,
                       n.dead as dead,
                       n.callCount as callCount,
                       incomingCalls
                ORDER BY incomingCalls DESC
                """
                
                nodes_result = session.run(nodes_query)
                nodes = []
                
                for record in nodes_result:
                    call_count = record["callCount"] or 0
                    incoming_calls = record["incomingCalls"] or 0
                    
                    node = {
                        "id": record["id"],
                        "name": record["name"],
                        "file": record["file"],
                        "type": record["type"],
                        "dead": record["dead"] if record["dead"] is not None else False,
                        "callCount": call_count,
                        # Calculate size based on call count for Three.js visualization
                        "size": max(1.0, min(10.0, call_count * 0.5 + incoming_calls * 0.3 + 1.0))
                    }
                    nodes.append(node)
                
                # Get all relationships
                links_query = """
                MATCH (source)-[:CALLS]->(target)
                RETURN source.id as source, target.id as target
                """
                
                links_result = session.run(links_query)
                links = []
                
                for record in links_result:
                    link = {
                        "source": record["source"],
                        "target": record["target"]
                    }
                    links.append(link)
                
                logger.info(f"Retrieved {len(nodes)} nodes and {len(links)} links")
                return {
                    "nodes": nodes,
                    "links": links
                }
                
        except Exception as e:
            logger.error(f"Error retrieving graph data: {e}")
            return {"nodes": [], "links": []}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with various statistics
        """
        if not self.is_connected():
            logger.warning("Not connected to database, returning empty statistics")
            return {}
        
        try:
            with self.driver.session() as session:
                stats = {}
                
                # Total counts
                result = session.run("MATCH (n) RETURN COUNT(n) as total")
                stats["total_nodes"] = result.single()["total"]
                
                result = session.run("MATCH ()-[r:CALLS]->() RETURN COUNT(r) as total")
                stats["total_relationships"] = result.single()["total"]
                
                # Counts by type
                result = session.run("""
                MATCH (n) 
                RETURN n.type as type, COUNT(n) as count
                ORDER BY count DESC
                """)
                
                type_counts = {}
                for record in result:
                    type_counts[record["type"]] = record["count"]
                stats["by_type"] = type_counts
                
                # Dead code count
                result = session.run("MATCH (n {dead: true}) RETURN COUNT(n) as dead_count")
                stats["dead_code_count"] = result.single()["dead_count"]
                
                # Most called functions
                result = session.run("""
                MATCH (n)<-[:CALLS]-(caller)
                WITH n, COUNT(caller) as callCount
                WHERE callCount > 0
                RETURN n.name as name, n.file as file, callCount
                ORDER BY callCount DESC
                LIMIT 10
                """)
                
                most_called = []
                for record in result:
                    most_called.append({
                        "name": record["name"],
                        "file": record["file"],
                        "callCount": record["callCount"]
                    })
                stats["most_called"] = most_called
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}