import logging
from knowledge_graph.base import BaseGraphService
from knowledge_graph.neo4j_impl import Neo4jGraphService
from knowledge_graph.networkx_impl import NetworkXGraphService

logger = logging.getLogger("researchmind")

_instance: BaseGraphService = None

def get_graph_service() -> BaseGraphService:
    """Singleton factory provider for Graph Database Services."""
    global _instance
    if _instance is not None:
        return _instance
        
    # Attempt Neo4j first
    service = Neo4jGraphService()
    if service.connect():
        _instance = service
        logger.info("Knowledge Graph is using Neo4j backend.")
    else:
        # Fall back to NetworkX
        service = NetworkXGraphService()
        service.connect()
        _instance = service
        logger.info("Knowledge Graph is using Local NetworkX (JSON) backend fallback.")
        
    return _instance
