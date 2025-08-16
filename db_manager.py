"""
Neo4j database manager for Code Weaver.
Handles storing and retrieving code analysis data.
"""

import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError


class Neo4jManager:
    """Manages Neo4j database operations for code analysis data."""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "codycody"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI
            username: Database username
            password: Database password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
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
            return True
        except (ServiceUnavailable, AuthError) as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to Neo4j: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from the database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
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
                
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
    
    def store_analysis_results(self, nodes: List[Dict[str, Any]], 
                             edges: List[Dict[str, Any]]) -> bool:
        """
        Store analysis results in Neo4j.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            with self.driver.session() as session:
                # Store nodes
                for node in nodes:
                    self._create_node(session, node)
                
                # Store edges
                for edge in edges:
                    self._create_relationship(session, edge)
                    
            return True
        except Exception as e:
            print(f"Error storing analysis results: {e}")
            return False
    
    def _create_node(self, session, node: Dict[str, Any]) -> None:
        """Create a node in the database."""
        node_type = node.get("type", "Unknown").title()
        
        # Use MERGE to avoid duplicates
        if node_type == "Function":
            query = """
            MERGE (n:Function {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type
            """
        elif node_type == "Class":
            query = """
            MERGE (n:Class {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type
            """
        elif node_type == "Module":
            query = """
            MERGE (n:Module {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type
            """
        else:
            query = """
            MERGE (n:CodeElement {id: $id})
            SET n.name = $label,
                n.file = $file,
                n.dead = $dead,
                n.type = $type
            """
        
        session.run(query, {
            "id": node["id"],
            "label": node["label"],
            "file": node["file"],
            "dead": node.get("dead", False),
            "type": node["type"]
        })
    
    def _create_relationship(self, session, edge: Dict[str, Any]) -> None:
        """Create a relationship between nodes."""
        query = """
        MATCH (source {id: $source_id})
        MATCH (target {id: $target_id})
        MERGE (source)-[:CALLS]->(target)
        """
        
        session.run(query, {
            "source_id": edge["source"],
            "target_id": edge["target"]
        })
    
    def get_graph_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve all graph data for visualization.
        
        Returns:
            Dictionary with 'nodes' and 'links' for Three.js
        """
        if not self.driver:
            return {"nodes": [], "links": []}
            
        try:
            with self.driver.session() as session:
                # Get all nodes with call counts
                nodes_query = """
                MATCH (n)
                OPTIONAL MATCH (n)<-[:CALLS]-(caller)
                WITH n, COUNT(caller) as callCount
                RETURN n.id as id, 
                       n.name as name, 
                       n.file as file, 
                       n.type as type,
                       n.dead as dead,
                       callCount
                ORDER BY callCount DESC
                """
                
                nodes_result = session.run(nodes_query)
                nodes = []
                
                for record in nodes_result:
                    node = {
                        "id": record["id"],
                        "name": record["name"],
                        "file": record["file"],
                        "type": record["type"],
                        "dead": record["dead"] if record["dead"] is not None else False,
                        "callCount": record["callCount"],
                        # Calculate size based on call count (for Three.js visualization)
                        "size": max(5, min(50, record["callCount"] * 3 + 10))
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
                
                return {
                    "nodes": nodes,
                    "links": links
                }
                
        except Exception as e:
            print(f"Error retrieving graph data: {e}")
            return {"nodes": [], "links": []}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with various statistics
        """
        if not self.driver:
            return {}
            
        try:
            with self.driver.session() as session:
                # Count nodes by type
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
            print(f"Error getting statistics: {e}")
            return {}


# Global database manager instance
db_manager = Neo4jManager()


def get_db_manager() -> Neo4jManager:
    """Get the global database manager instance."""
    return db_manager


if __name__ == "__main__":
    # Test the database manager
    manager = Neo4jManager()
    
    if manager.connect():
        print("Connected to Neo4j successfully!")
        
        # Clear database
        if manager.clear_database():
            print("Database cleared successfully!")
        
        # Test with sample data
        sample_nodes = [
            {
                "id": "test.py:main",
                "type": "function",
                "file": "test.py",
                "label": "main",
                "dead": False
            }
        ]
        
        sample_edges = []
        
        if manager.store_analysis_results(sample_nodes, sample_edges):
            print("Sample data stored successfully!")
        
        # Get statistics
        stats = manager.get_statistics()
        print("Database statistics:", stats)
        
        manager.close()
        print("Connection closed.")
    else:
        print("Failed to connect to Neo4j!")
