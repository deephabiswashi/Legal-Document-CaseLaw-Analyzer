# Legal Document & Case Law Analyzer

A robust, **two-index** system for uploading, OCRing, and querying legal documents—plus ingesting and searching case law data. This project uses **FastAPI**, **Elasticsearch**, **LangChain**, and **Ollama** to provide an end-to-end solution for scanning PDFs, extracting text, and performing intelligent queries on contracts and case law.

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [Project Structure](#project-structure)  
4. [Installation & Setup](#installation--setup)  
5. [Running the Application](#running-the-application)  
6. [Endpoints](#endpoints)  
7. [Using the Frontend](#using-the-frontend)  
8. [Additional Scripts](#additional-scripts)  
9. [Tech Stack](#tech-stack)  
10. [License](#license)

---

## Project Overview
This repository contains a **Legal Document & Case Law Analyzer** that uses:
- **OCR** (via Tesseract & pdf2image) to extract text from uploaded PDFs or images.
- **Elasticsearch** to index and query text.
- **LangChain** + **Ollama** (e.g., `gemma3:4b` model) to provide a Retrieval-Augmented Generation (RAG) approach for answering queries.

It supports **two indexes**:
1. **`legal_docs`** for uploaded documents via the main UI.  
2. **`caselaw_index`** for separately ingested case law data (HTML/JSON files).

A modern, two-panel UI (using **HTML/CSS/JS**) allows users to:
- Upload and query documents in the **UI-based** index.
- Ingest and query **case law** in a separate index.

---

## Key Features
1. **OCR & Indexing**  
   - Upload PDFs or images → The system runs OCR → Text is indexed in Elasticsearch.

2. **UI-based Document Analyzer**  
   - `/upload` and `/query` endpoints manage the **`legal_docs`** index.  
   - Perfect for scanning and querying typical legal documents.

3. **Case Law Analyzer**  
   - `/ingest-caselaw` endpoint to read subfolders of `data/` (HTML/JSON) and index them into **`caselaw_index`**.  
   - `/query-caselaw` to retrieve and answer queries about previously ingested case law.

4. **LangChain + Ollama**  
   - Queries are answered by a Llama-based model (e.g., `gemma3:4b`) using a RAG approach.  
   - Integrates with `langchain_integration.py` to manage the model prompt and retrieve context from Elasticsearch.

5. **Modern Two-Panel UI**  
   - Left panel: UI-based uploads & queries.  
   - Right panel: Case law ingestion & queries.

---

## Project Structure
```
Legal Doc Chatbot/
├─ backend/
│  ├─ __init__.py
│  ├─ app.py                 # Main FastAPI application
│  ├─ config.py              # Configuration (e.g., OLLAMA_HOST, ES credentials)
│  ├─ es_client.py           # Elasticsearch client for both indexes
│  ├─ langchain_integration.py # RAG logic with Ollama (gemma3:4b)
│  ├─ ocr.py                 # OCR logic using Tesseract/pdf2image
├─ data/                     # Subfolders (1, 2, 3...) containing HTML/JSON case law
├─ env1/                     # Python virtual environment (not tracked)
├─ frontend/
│  ├─ index.html             # Two-panel UI
│  ├─ script.js              # Frontend logic calling FastAPI endpoints
│  ├─ styles.css             # Modern styling
├─ ingest_caselaw.py         # (Optional) Standalone script for ingesting case law
├─ rag_query_caselaw.py      # (Optional) Standalone script for querying case law
├─ requirements.txt          # Python dependencies
└─ .env                      # Environment variables (Elasticsearch credentials, etc.)
```

---

## Installation & Setup
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/YourUser/Legal-Document-CaseLaw-Analyzer.git
   cd Legal-Document-CaseLaw-Analyzer
   ```

2. **Create & Activate a Virtual Environment**  
   ```bash
   python3 -m venv env1
   source env1/bin/activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install External Tools**  
   - **Tesseract** (for OCR):  
     - macOS: `brew install tesseract poppler ghostscript`  
     - Ubuntu: `sudo apt-get install tesseract-ocr poppler-utils ghostscript`  
   - **Ollama** for local LLM inference. E.g., `gemma3:4b` or `llama3.1:8b`.

5. **Configure Environment**  
   - Create or edit `.env` with credentials (Elasticsearch host & API key, Ollama host, etc.).
   
6. **Elasticsearch & Kibana**  
   - Run them via Docker or local installation:
     ```bash
     docker run -p 9200:9200 -p 5601:5601 docker.elastic.co/elasticsearch/elasticsearch:8.17.3
     ```

---

## Running the Application
1. **Start Ollama** in a separate terminal:
   ```bash
   ollama serve
   ```
2. **Launch FastAPI**:
   ```bash
   uvicorn backend.app:app --reload
   ```
3. **Open the UI**:
   - In your browser, navigate to `http://127.0.0.1:8000`.

---

## Endpoints
- `POST /upload` - Upload a PDF/image, run OCR, and index into `legal_docs`.
- `POST /query` - Query the `legal_docs` index, then generate an answer using Gemma model.
- `POST /ingest-caselaw` - Ingest case law into `caselaw_index`.
- `POST /query-caselaw` - Search `caselaw_index` for relevant documents, pass them to the Gemma model for an answer.

---

## Tech Stack
- **FastAPI** (HTTP server & endpoints)  
- **Elasticsearch** (Index & retrieve documents)  
- **LangChain** + **Ollama** (RAG approach using `gemma3:4b`)  
- **pdf2image** + **Tesseract** (OCR for PDF/image uploads)  
- **HTML/CSS/JS** (Two-column modern UI)  

---

## License
This project is licensed under the **MIT License**.

---

**Enjoy analyzing and querying your legal documents and case law with a modern UI and robust backend!**

