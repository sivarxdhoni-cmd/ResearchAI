from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class BaseGraphService(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """Establishes connection to the graph database backend."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes connection."""
        pass

    @abstractmethod
    def add_paper(self, paper_id: int, title: str, year: int) -> None:
        """Adds a Paper node to the graph."""
        pass

    @abstractmethod
    def add_author(self, name: str) -> None:
        """Adds an Author node to the graph."""
        pass

    @abstractmethod
    def add_topic(self, name: str, category: str = None) -> None:
        """Adds a Topic node to the graph."""
        pass

    @abstractmethod
    def add_dataset(self, name: str) -> None:
        """Adds a Dataset node."""
        pass

    @abstractmethod
    def add_algorithm(self, name: str) -> None:
        """Adds an Algorithm node."""
        pass

    @abstractmethod
    def add_research_gap(self, gap_id: int, description: str, score: float) -> None:
        """Adds a Research Gap node."""
        pass

    @abstractmethod
    def connect_author_paper(self, author_name: str, paper_id: int) -> None:
        """Creates relationship: (Author)-[:AUTHORED]->(Paper)."""
        pass

    @abstractmethod
    def connect_paper_topic(self, paper_id: int, topic_name: str) -> None:
        """Creates relationship: (Paper)-[:COVERS]->(Topic)."""
        pass

    @abstractmethod
    def connect_paper_dataset(self, paper_id: int, dataset_name: str) -> None:
        """Creates relationship: (Paper)-[:USES_DATASET]->(Dataset)."""
        pass

    @abstractmethod
    def connect_paper_algorithm(self, paper_id: int, algorithm_name: str) -> None:
        """Creates relationship: (Paper)-[:USES_ALGORITHM]->(Algorithm)."""
        pass

    @abstractmethod
    def connect_gap_topic(self, gap_id: int, topic_name: str) -> None:
        """Creates relationship: (ResearchGap)-[:GAP_IN]->(Topic)."""
        pass

    @abstractmethod
    def connect_paper_gap(self, paper_id: int, gap_id: int) -> None:
        """Creates relationship: (Paper)-[:IDENTIFIES_GAP]->(ResearchGap)."""
        pass

    @abstractmethod
    def get_subgraph(self, center_node_type: str = None, center_node_value: str = None) -> Dict[str, Any]:
        """Retrieves nodes and edges for visualization in the React frontend.
        Returns a dict format: {'nodes': [{'id': '...', 'label': '...', 'type': '...'}], 'links': [{'source': '...', 'target': '...', 'type': '...'}]}
        """
        pass

    @abstractmethod
    def clear_graph(self) -> None:
        """Deletes all nodes and relationships in the graph."""
        pass
