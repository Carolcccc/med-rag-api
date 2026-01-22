**Healthcare RAG API**

**🚧 Project Status: Work in Progress (WIP)**
This repository is a technical prototype currently undergoing active development. The primary focus is on refining retrieval logic and exploring diverse embedding strategies for specialized medical-specific corpora.

**Overview**
This project implements a small-scale Retrieval-Augmented Generation (RAG) pipeline focused on healthcare data ingestion and question-answering. By integrating medical literature (PMC metadata), clinical guidelines, and community-driven insights (Reddit), the system provides context-aware responses grounded in verified data sources.

**🚀 Key Features**
Multi-Source Ingestion: Automated scripts for fetching PubMed/PMC metadata and clinical guideline PDFs.

Privacy-First Data Handling: Implements de-identification helpers to process sensitive healthcare text before indexing.

Efficient Vector Search: Utilizes FAISS for high-performance similarity search and document retrieval.

Asynchronous API: A FastAPI service exposing an /ask endpoint for real-time retriever-LLM orchestration.

**🛠️ System Architecture**
Extraction: Fetches structured medical metadata and unstructured community posts via APIs.

Transformation: Normalizes heterogeneous data sources into a unified .txt format with de-identification logic.

Indexing: Chunks documents and generates embeddings to build a persistent FAISS vector store.

Inference: Orchestrates the retriever-reader loop to generate evidence-based answers using LLMs.

**📂 Repository Structure**
create_vector_db.py: Pipeline to chunk, embed, and save the FAISS vector store.

main.py: FastAPI application for the retrieval and generation service.

scripts/: Modular data engineering helpers:

01_fetch_pmc.py: Fetch metadata using Entrez.

02_fetch_guidelines.py: Download and extract text from guideline PDFs.

03_fetch_reddit.py: Extract community posts via PRAW.

04_pmc_to_txt.py: Convert JSONL to de-identified text files.

**⚡ Quick Start**
Environment Setup:

Bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Database Construction: Place source files in data/ and initialize the FAISS store:

Bash
python create_vector_db.py
API Deployment:

Bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000

**🔒 Security & Privacy**
Credential Management: Reddit and OpenAI keys should be managed via environment variables or the export_reddit.sh template.

Exclusion Rules: Local data/, faiss_index/, and venv/ are strictly excluded from version control via .gitignore.

**🗺️ Future Roadmap**
Evaluation Framework: Integrate RAGAS to quantitatively evaluate the faithfulness and relevancy of generated responses.

Advanced Chunking: Experiment with semantic chunking to better preserve the context of complex medical guidelines.

Quantized LLM Support: Research local deployment of quantized LLMs (e.g., Llama-3) to ensure data privacy in clinical settings.
