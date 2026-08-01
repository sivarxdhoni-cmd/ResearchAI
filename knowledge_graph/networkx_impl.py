import os
import json
import logging
from typing import Dict, Any, List
import networkx as nx
from backend.app.core.config import settings
from knowledge_graph.base import BaseGraphService

logger = logging.getLogger("researchmind")

class NetworkXGraphService(BaseGraphService):
    def __init__(self):
        self.db_path = os.path.join(settings.BASE_DIR, "knowledge_graph.json")
        self.graph = nx.MultiDiGraph()

    def connect(self) -> bool:
        """Loads graph from JSON file if it exists, otherwise creates empty graph."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Reconstruct graph from JSON serialization
                for node in data.get("nodes", []):
                    self.graph.add_node(
                        node["id"], 
                        label=node["label"], 
                        type=node["type"], 
                        **node.get("properties", {})
                    )
                for edge in data.get("edges", []):
                    self.graph.add_edge(
                        edge["source"], 
                        edge["target"], 
                        type=edge["type"]
                    )
                logger.info(f"Loaded local NetworkX graph from: {self.db_path} ({len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges).")
            else:
                self.graph = nx.MultiDiGraph()
                self._save()
                logger.info(f"Initialized new NetworkX graph database at: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize NetworkX graph fallback: {e}")
            return False

    def close(self) -> None:
        self._save()

    def _save(self) -> None:
        """Serializes current graph to JSON file."""
        try:
            nodes = []
            for n_id, data in self.graph.nodes(data=True):
                # Copy properties and separate core tags
                properties = data.copy()
                label = properties.pop("label", n_id)
                ntype = properties.pop("type", "Unknown")
                nodes.append({
                    "id": n_id,
                    "label": label,
                    "type": ntype,
                    "properties": properties
                })
                
            edges = []
            for u, v, key, data in self.graph.edges(keys=True, data=True):
                edges.append({
                    "source": u,
                    "target": v,
                    "type": data.get("type", "RELATED_TO")
                })
                
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"nodes": nodes, "edges": edges}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving NetworkX graph file: {e}")

    def add_paper(self, paper_id: int, title: str, year: int) -> None:
        uid = f"paper_{paper_id}"
        self.graph.add_node(uid, label=title, type="Paper", year=year)
        self._save()

    def add_author(self, name: str) -> None:
        self.graph.add_node(name, label=name, type="Author")
        self._save()

    def add_topic(self, name: str, category: str = None) -> None:
        self.graph.add_node(name, label=name, type="Topic", category=category or "General")
        self._save()

    def add_dataset(self, name: str) -> None:
        self.graph.add_node(name, label=name, type="Dataset")
        self._save()

    def add_algorithm(self, name: str) -> None:
        self.graph.add_node(name, label=name, type="Algorithm")
        self._save()

    def add_research_gap(self, gap_id: int, description: str, score: float) -> None:
        uid = f"gap_{gap_id}"
        short_desc = description[:37] + "..." if len(description) > 40 else description
        self.graph.add_node(uid, label=short_desc, type="ResearchGap", description=description, score=score)
        self._save()

    def connect_author_paper(self, author_name: str, paper_id: int) -> None:
        paper_uid = f"paper_{paper_id}"
        if author_name in self.graph.nodes and paper_uid in self.graph.nodes:
            self.graph.add_edge(author_name, paper_uid, type="AUTHORED")
            self._save()

    def connect_paper_topic(self, paper_id: int, topic_name: str) -> None:
        paper_uid = f"paper_{paper_id}"
        if paper_uid in self.graph.nodes and topic_name in self.graph.nodes:
            self.graph.add_edge(paper_uid, topic_name, type="COVERS")
            self._save()

    def connect_paper_dataset(self, paper_id: int, dataset_name: str) -> None:
        paper_uid = f"paper_{paper_id}"
        if paper_uid in self.graph.nodes and dataset_name in self.graph.nodes:
            self.graph.add_edge(paper_uid, dataset_name, type="USES_DATASET")
            self._save()

    def connect_paper_algorithm(self, paper_id: int, algorithm_name: str) -> None:
        paper_uid = f"paper_{paper_id}"
        if paper_uid in self.graph.nodes and algorithm_name in self.graph.nodes:
            self.graph.add_edge(paper_uid, algorithm_name, type="USES_ALGORITHM")
            self._save()

    def connect_gap_topic(self, gap_id: int, topic_name: str) -> None:
        gap_uid = f"gap_{gap_id}"
        if gap_uid in self.graph.nodes and topic_name in self.graph.nodes:
            self.graph.add_edge(gap_uid, topic_name, type="GAP_IN")
            self._save()

    def connect_paper_gap(self, paper_id: int, gap_id: int) -> None:
        paper_uid = f"paper_{paper_id}"
        gap_uid = f"gap_{gap_id}"
        if paper_uid in self.graph.nodes and gap_uid in self.graph.nodes:
            self.graph.add_edge(paper_uid, gap_uid, type="IDENTIFIES_GAP")
            self._save()

    def clear_graph(self) -> None:
        self.graph.clear()
        self._save()

    def get_subgraph(self, center_node_type: str = None, center_node_value: str = None) -> Dict[str, Any]:
        """Formats the NetworkX nodes and edges directly for D3.js visualization."""
        nodes = []
        for n_id, data in self.graph.nodes(data=True):
            props = data.copy()
            label = props.pop("label", n_id)
            ntype = props.pop("type", "Unknown")
            
            # Shorten labels for display
            display_label = label
            if len(display_label) > 40:
                display_label = display_label[:37] + "..."
                
            nodes.append({
                "id": n_id,
                "label": display_label,
                "type": ntype,
                "properties": props
            })
            
        links = []
        for u, v, data in self.graph.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "type": data.get("type", "RELATED_TO")
            })
            
        return {
            "nodes": nodes,
            "links": links
        }
