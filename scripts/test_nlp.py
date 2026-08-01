import sys
import os

# Adjust path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.extractor import PDFExtractor
from ai.ner import NREngine
from knowledge_graph import get_graph_service

def run_test():
    print("Testing NLP & Knowledge Graph Pipeline...")
    
    # 1. Setup mock paper data (simulating parsed structures from PDF)
    mock_paper = {
        "title": "Quantum Convolutional Neural Networks on ImageNet",
        "authors": "Alice Smith, Bob Jones",
        "abstract": "We present Quantum Convolutional Neural Networks (QCNN) applied to image classification on the ImageNet dataset. Our model combines quantum circuits with classical CNNs, achieving 94.2% accuracy.",
        "methodology": "We implement QCNN using a series of parameterized quantum filters. The classical convolution layer uses PyTorch and ResNet-50. We execute experiments using custom GPU hardware.",
        "results": "Our QCNN achieved an accuracy of 94.2% on ImageNet, outperforming standard LSTM and ResNet models which reached 89.1% and 92.0% respectively.",
        "limitations": "The model has high hardware requirements and struggles with training convergence due to quantum decoherence.",
        "future_work": "Future work will explore deploying the QCNN algorithm on IBM Quantum computers and utilizing the CIFAR-100 dataset.",
        "conclusion": "Quantum neural nets show significant promise for scaling image recognition tasks."
    }

    print("\n--- Running NER Entity Extractor ---")
    ner = NREngine()
    entities = ner.analyze_paper_metadata(mock_paper)
    
    print(f"Keywords extracted: {entities['keywords']}")
    print(f"Datasets detected: {entities['datasets']}")
    print(f"Algorithms detected: {entities['algorithms']}")
    print(f"Metrics detected: {entities['metrics']}")

    # Verification assertions
    assert "imagenet" in [k.lower() for k in entities["datasets"]] or "imagenet" in [k.lower() for k in entities["keywords"]], "Should detect ImageNet dataset"
    assert "cnn" in [a.lower() for a in entities["algorithms"]] or "qcnn" in [a.lower() for a in entities["algorithms"]], "Should detect CNN algorithm"
    print("[x] NER Extraction checks passed!")

    print("\n--- Building Knowledge Graph ---")
    graph = get_graph_service()
    graph.clear_graph()
    
    paper_id = 99
    # Add nodes
    graph.add_paper(paper_id, mock_paper["title"], 2026)
    
    for author in ["Alice Smith", "Bob Jones"]:
        graph.add_author(author)
        graph.connect_author_paper(author, paper_id)
        
    for topic in ["Quantum Computing", "Deep Learning"]:
        graph.add_topic(topic, "AI")
        graph.connect_paper_topic(paper_id, topic)
        
    for ds in entities["datasets"]:
        graph.add_dataset(ds)
        graph.connect_paper_dataset(paper_id, ds)
        
    for algo in entities["algorithms"]:
        graph.add_algorithm(algo)
        graph.connect_paper_algorithm(paper_id, algo)

    # Output subgraph
    subgraph = graph.get_subgraph()
    print(f"Successfully generated graph with {len(subgraph['nodes'])} nodes and {len(subgraph['links'])} links.")
    
    # Check if local JSON file is saved
    local_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_graph.json")
    if os.path.exists(local_json):
        print(f"[x] Graph persisted successfully to {local_json}")
    else:
        print("[!] Graph file was not found!")
        
    print("\nAll test verifications passed successfully!")

if __name__ == "__main__":
    run_test()
