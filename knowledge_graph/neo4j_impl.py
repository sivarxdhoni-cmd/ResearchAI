import logging
from typing import Dict, Any, List
from neo4j import GraphDatabase, Driver
from backend.app.core.config import settings
from knowledge_graph.base import BaseGraphService

logger = logging.getLogger("researchmind")

class Neo4jGraphService(BaseGraphService):
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.driver: Driver = None

    def connect(self) -> bool:
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j database.")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j database: {e}")
            self.driver = None
            return False

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            logger.info("Neo4j database connection closed.")

    def _execute(self, query: str, parameters: Dict[str, Any] = None) -> Any:
        if not self.driver:
            raise RuntimeError("Neo4j driver is not connected.")
        with self.driver.session() as session:
            return session.run(query, parameters)

    def add_paper(self, paper_id: int, title: str, year: int) -> None:
        query = """
        MERGE (p:Paper {uid: $uid})
        SET p.title = $title, p.year = $year
        """
        self._execute(query, {"uid": f"paper_{paper_id}", "title": title, "year": year})

    def add_author(self, name: str) -> None:
        query = "MERGE (a:Author {uid: $name, name: $name})"
        self._execute(query, {"name": name})

    def add_topic(self, name: str, category: str = None) -> None:
        query = """
        MERGE (t:Topic {uid: $name})
        SET t.name = $name, t.category = $category
        """
        self._execute(query, {"name": name, "category": category or "General"})

    def add_dataset(self, name: str) -> None:
        query = "MERGE (d:Dataset {uid: $name, name: $name})"
        self._execute(query, {"name": name})

    def add_algorithm(self, name: str) -> None:
        query = "MERGE (al:Algorithm {uid: $name, name: $name})"
        self._execute(query, {"name": name})

    def add_research_gap(self, gap_id: int, description: str, score: float) -> None:
        query = """
        MERGE (g:ResearchGap {uid: $uid})
        SET g.description = $description, g.score = $score
        """
        self._execute(query, {"uid": f"gap_{gap_id}", "description": description, "score": score})

    def connect_author_paper(self, author_name: str, paper_id: int) -> None:
        query = """
        MATCH (a:Author {uid: $author_name})
        MATCH (p:Paper {uid: $paper_uid})
        MERGE (a)-[:AUTHORED]->(p)
        """
        self._execute(query, {"author_name": author_name, "paper_uid": f"paper_{paper_id}"})

    def connect_paper_topic(self, paper_id: int, topic_name: str) -> None:
        query = """
        MATCH (p:Paper {uid: $paper_uid})
        MATCH (t:Topic {uid: $topic_name})
        MERGE (p)-[:COVERS]->(t)
        """
        self._execute(query, {"paper_uid": f"paper_{paper_id}", "topic_name": topic_name})

    def connect_paper_dataset(self, paper_id: int, dataset_name: str) -> None:
        query = """
        MATCH (p:Paper {uid: $paper_uid})
        MATCH (d:Dataset {uid: $dataset_name})
        MERGE (p)-[:USES_DATASET]->(d)
        """
        self._execute(query, {"paper_uid": f"paper_{paper_id}", "dataset_name": dataset_name})

    def connect_paper_algorithm(self, paper_id: int, algorithm_name: str) -> None:
        query = """
        MATCH (p:Paper {uid: $paper_uid})
        MATCH (al:Algorithm {uid: $algorithm_name})
        MERGE (p)-[:USES_ALGORITHM]->(al)
        """
        self._execute(query, {"paper_uid": f"paper_{paper_id}", "algorithm_name": algorithm_name})

    def connect_gap_topic(self, gap_id: int, topic_name: str) -> None:
        query = """
        MATCH (g:ResearchGap {uid: $gap_uid})
        MATCH (t:Topic {uid: $topic_name})
        MERGE (g)-[:GAP_IN]->(t)
        """
        self._execute(query, {"gap_uid": f"gap_{gap_id}", "topic_name": topic_name})

    def connect_paper_gap(self, paper_id: int, gap_id: int) -> None:
        query = """
        MATCH (p:Paper {uid: $paper_uid})
        MATCH (g:ResearchGap {uid: $gap_uid})
        MERGE (p)-[:IDENTIFIES_GAP]->(g)
        """
        self._execute(query, {"paper_uid": f"paper_{paper_id}", "gap_uid": f"gap_{gap_id}"})

    def clear_graph(self) -> None:
        query = "MATCH (n) DETACH DELETE n"
        self._execute(query)

    def get_subgraph(self, center_node_type: str = None, center_node_value: str = None) -> Dict[str, Any]:
        """Queries database and builds structured format for UI representation."""
        # Simple full retrieval with limits
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 300
        """
        result = self._execute(query)
        
        nodes_dict = {}
        links = []
        
        for record in result:
            n = record.get("n")
            r = record.get("r")
            m = record.get("m")
            
            if n:
                n_id = n.get("uid")
                labels = list(n.labels)
                label_type = labels[0] if labels else "Unknown"
                
                # Fetch naming attributes
                name_val = n.get("title") or n.get("name") or n.get("description") or n_id
                if len(name_val) > 40:
                    name_val = name_val[:37] + "..."
                    
                nodes_dict[n_id] = {
                    "id": n_id,
                    "label": name_val,
                    "type": label_type,
                    "properties": dict(n)
                }
                
            if m:
                m_id = m.get("uid")
                labels = list(m.labels)
                label_type = labels[0] if labels else "Unknown"
                
                name_val = m.get("title") or m.get("name") or m.get("description") or m_id
                if len(name_val) > 40:
                    name_val = name_val[:37] + "..."
                    
                nodes_dict[m_id] = {
                    "id": m_id,
                    "label": name_val,
                    "type": label_type,
                    "properties": dict(m)
                }
                
            if r and n and m:
                links.append({
                    "source": n.get("uid"),
                    "target": m.get("uid"),
                    "type": r.type
                })
                
        return {
            "nodes": list(nodes_dict.values()),
            "links": links
        }
