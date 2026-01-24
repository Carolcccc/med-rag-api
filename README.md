# Healthcare RAG API

> **🚧 Work in Progress**: This is an active technical prototype focused on refining retrieval logic and exploring embedding strategies for medical-specific corpora.

## Overview

A Retrieval-Augmented Generation (RAG) pipeline designed for healthcare question-answering. The system combines multiple data sources—medical literature (PubMed/PMC), clinical guidelines, and community insights (Reddit)—to provide context-aware, evidence-based responses.

## Features

- **Multi-Source Data Ingestion**: Automated fetching of PubMed/PMC metadata, clinical guideline PDFs, and Reddit health discussions
- **Privacy-First Processing**: Built-in de-identification for sensitive healthcare text
- **High-Performance Vector Search**: FAISS-powered similarity search for efficient document retrieval
- **RESTful API**: FastAPI service with asynchronous `/ask` endpoint for real-time question-answering

## Architecture

The system follows a four-stage pipeline:

1. **Extraction**: Fetches structured medical metadata and community posts via APIs
2. **Transformation**: Normalizes heterogeneous data into unified `.txt` format with de-identification
3. **Indexing**: Generates embeddings and builds a persistent FAISS vector store
4. **Inference**: Orchestrates retriever-reader loop for LLM-based answer generation

## Project Structure

```
.
├── create_vector_db.py          # Vector database creation pipeline
├── main.py                       # FastAPI application
├── requirements.txt              # Python dependencies
└── scripts/
    ├── 01_fetch_pmc.py          # Fetch PubMed/PMC metadata
    ├── 02_fetch_guidelines.py   # Download clinical guideline PDFs
    ├── 03_fetch_reddit.py       # Extract community health posts
    └── 04_pmc_to_txt.py         # Convert JSONL to de-identified text
```

## Quick Start

### 1. Environment Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Build Vector Database

Place your source files in the `data/` directory, then initialize the FAISS index:

```bash
python create_vector_db.py
```

### 3. Run the API

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`. Visit `/docs` for interactive API documentation.

## Security & Privacy

- **Credentials**: Store Reddit and OpenAI API keys in environment variables (see `export_reddit.sh` template)
- **Data Protection**: `data/`, `faiss_index/`, and `venv/` are excluded from version control
- **De-identification**: Healthcare text is processed to remove sensitive information before indexing

## Roadmap

- [ ] **Evaluation Framework**: Integrate RAGAS for quantitative assessment of response faithfulness and relevancy
- [ ] **Advanced Chunking**: Implement semantic chunking to preserve context in complex medical documents
- [ ] **Local LLM Support**: Deploy quantized models (e.g., Llama-3) for enhanced data privacy in clinical settings
- [ ] **Extended Data Sources**: Add support for additional medical databases and knowledge bases

## License

This project is for research and educational purposes only. Please ensure compliance with data source terms of service and applicable healthcare regulations.

---

**Note**: This system is not intended for clinical decision-making. Always consult qualified healthcare professionals for medical advice.
