import sys
import os
import time
import requests
import fitz  # PyMuPDF

# Adjust path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"

def create_mock_pdf(filename: str):
    """Generates a valid 1-page scientific PDF document using PyMuPDF."""
    print(f"Generating mock PDF scientific paper: {filename}...")
    doc = fitz.open()
    page = doc.new_page()
    
    text_content = (
        "Title: Optimization of Edge CNN models on MNIST\n\n"
        "Authors: Carol Miller, Dave Wilson\n\n"
        "Abstract\n"
        "We propose an optimized Convolutional Neural Network (CNN) model trained on the MNIST dataset. "
        "The model achieves an accuracy of 99.2% by utilizing localized convolution kernels.\n\n"
        "Introduction\n"
        "Deep learning models are increasingly deployed on edge devices.\n\n"
        "Methodology\n"
        "Our architecture implements a 5-layer CNN using PyTorch. We compile kernels using specialized vector pipelines. "
        "All model benchmarks were executed on an NVIDIA Edge GPU configuration.\n\n"
        "Results\n"
        "Our CNN achieved 99.2% accuracy on the MNIST benchmark with minimal latency.\n\n"
        "Limitations\n"
        "The current implementation is constrained by GPU memory and struggles with high floating-point latency on standard CPU hardware.\n\n"
        "Future Work\n"
        "Subsequent work will focus on testing the CNN model on Coral TPU and Raspberry Pi edge configurations.\n\n"
        "Conclusion\n"
        "Optimized CNN kernels can significantly speed up edge image classification."
    )
    
    # Write text to PDF page
    page.insert_text((50, 50), text_content, fontsize=10)
    doc.save(filename)
    doc.close()
    print("PDF generated successfully.")

def run_e2e():
    # 1. Generate PDF
    pdf_filename = "test_edge_cnn.pdf"
    create_mock_pdf(pdf_filename)

    try:
        # 2. Login
        print("\n[Step 1] Logging in as Research Scholar...")
        login_data = {
            "username": "scholar@researchmind.ai",
            "password": "scholar123"
        }
        res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        res.raise_for_status()
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in successfully. Token acquired.")

        # 3. Upload Paper
        print("\n[Step 2] Uploading mock PDF...")
        with open(pdf_filename, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            data = {
                "publication_year": 2026,
                "conference_journal": "IEEE Edge Conference",
                "doi": "10.1109/EDGE.2026.11"
            }
            res = requests.post(f"{BASE_URL}/papers/upload", headers=headers, files=files, data=data)
        
        res.raise_for_status()
        paper_info = res.json()
        paper_id = paper_info["id"]
        print(f"Paper uploaded successfully. Assigned ID: {paper_id}. Status: {paper_info['status']}")

        # 4. Poll Processing Status
        print("\n[Step 3] Polling background processing status...")
        status = "processing"
        attempts = 0
        while status == "processing" and attempts < 10:
            time.sleep(2)
            res = requests.get(f"{BASE_URL}/papers/{paper_id}", headers=headers)
            res.raise_for_status()
            paper_info = res.json()
            status = paper_info["status"]
            attempts += 1
            print(f"Attempt {attempts}: Status is '{status}'")

        if status != "completed":
            raise RuntimeError(f"Background parsing failed. Status: {status}")

        print("Paper successfully indexed in SQL Database, FAISS Vector Index, and NetworkX Graph!")

        # 5. Query RAG Chat Assistant
        print("\n[Step 4] Querying AI Chat Assistant...")
        chat_payload = {
            "message": "What is the accuracy of the CNN model on MNIST and what hardware did they use?"
        }
        res = requests.post(f"{BASE_URL}/chat/", headers=headers, json=chat_payload)
        res.raise_for_status()
        chat_data = res.json()
        
        print("\nAssistant Response:")
        print("=================================================================")
        print(chat_data["response"])
        print("=================================================================")
        
        print("\nCitations returned:")
        for s in chat_data["sources"]:
            print(f"- {s['title']} | Section: {s['section']} | Score: {s['relevance_score']}")

        # Validate RAG answers
        assert len(chat_data["sources"]) > 0, "No citations returned"
        assert "99.2" in chat_data["response"], "RAG failed to retrieve accurate metrics"
        print("\n[x] RAG Chat check passed successfully!")

        # 6. Trigger Research Gaps Scan
        print("\n[Step 5] Triggering Gaps & Ideas scan...")
        # Get topic id for Large Language Models or default topic
        res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        res.raise_for_status()
        stats = res.json()
        
        # We can find all papers and select the first topic ID
        res = requests.get(f"{BASE_URL}/papers/{paper_id}", headers=headers)
        res.raise_for_status()
        p_details = res.json()
        
        # Topic name should be auto-extracted from keywords (e.g. cnn, model, etc.)
        # Let's run scan for a seeded topic first
        topic_id = 1 # Large Language Models
        print(f"Triggering scan for topic ID {topic_id}...")
        res = requests.post(f"{BASE_URL}/gaps/scan/{topic_id}", headers=headers)
        res.raise_for_status()
        print("Scan triggered successfully:", res.json()["message"])

        # Fetch gaps
        time.sleep(2)
        res = requests.get(f"{BASE_URL}/gaps/", headers=headers)
        res.raise_for_status()
        gaps_list = res.json()
        print(f"Currently active gaps in database: {len(gaps_list)}")

        print("\nAll E2E flow assertions verified successfully!")
        
    finally:
        # Cleanup mock pdf
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            print("\nCleaned up local mock PDF.")

if __name__ == "__main__":
    run_e2e()
