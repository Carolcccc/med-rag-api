# Healthcare RAG API

Small local RAG (Retrieval-Augmented Generation) demo focused on healthcare data ingestion and question-answering. This repository contains scripts to fetch medical text (PMC metadata), optional guideline PDFs, and Reddit posts; preprocessing and de-identification helpers; a small pipeline to chunk/embed documents into a FAISS vectorstore; and a FastAPI service that answers queries using a retriever + LLM.

WARNING: This repository may handle sensitive data. Do NOT commit secrets (API keys, client secrets). Use the provided `export_reddit.sh` or environment variables (and add them to your local `.gitignore`) rather than committing credentials.

## Contents
- `create_vector_db.py` — chunk, embed and save FAISS vector store from `.txt` files found under `data/`.
- `main.py` — FastAPI app exposing `/ask` endpoint (loads local FAISS vectorstore and uses OpenAI or Hugging Face LLM fallback).
- `scripts/` — data collection & preprocessing helpers:
  - `01_fetch_pmc.py` — fetch PubMed/PMC metadata using Entrez
  - `02_fetch_guidelines.py` — download guideline PDFs and extract text (requires PDF URLs)
  - `03_fetch_reddit.py` — fetch Reddit posts with PRAW (requires credentials)
  - `04_pmc_to_txt.py` — convert PMC JSONL to `.txt` files with simple de-id
  - `README.md` — notes about the scripts
- `data/` — (ignored) raw and processed files
- `faiss_index/` — (ignored) generated FAISS index
- `export_reddit.sh` — template (ignored) to set Reddit credentials locally

## Quick start (local)
1. Create a Python virtualenv and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Prepare data: place `.txt` files under `data/` (or run scripts in `scripts/` to fetch data).

3. Build the vector database:
```bash
python create_vector_db.py
```

4. Start the API (ensure `faiss_index/` exists):
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

5. Test `/ask`:
```bash
curl -X POST http://127.0.0.1:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"What is Myocardial Infarction (MI)？"}'
```

## Reddit credentials
- Put your Reddit `client_id`, `client_secret` and `user_agent` in `export_reddit.sh` (template provided). Do NOT commit that file. Use `source ./export_reddit.sh` to load in your shell.

## Security & GitHub
- `export_reddit.sh`, `data/`, `faiss_index/`, and `venv/` are already in `.gitignore`. Double-check before pushing. If a secret was accidentally committed, reset the secret in the provider (e.g. Reddit dev console) and remove it from git history.

