from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from pydantic import BaseModel
from typing import List, Optional
from bs4 import BeautifulSoup

from .config import settings
from .ocr import extract_text_from_image
from .es_client import (
    index_document,
    search_documents,
    index_caselaw,  # ✅ Fixed function name
    search_caselaw
)
from .langchain_integration import query_gemma  # Your existing function for Gemma model

app = FastAPI(title="Legal Document Analyzer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the /frontend directory as /static
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_index():
    """Returns the main frontend page."""
    return FileResponse("frontend/index.html")

# -------------------------------------------------------------------------
# 1) Existing UI-based endpoints (unchanged)
# -------------------------------------------------------------------------

def process_file(contents: bytes, filename: str):
    try:
        extracted_text = extract_text_from_image(contents, filename)
        if not extracted_text.strip():
            raise ValueError("No text extracted from document.")
        doc_id = index_document(extracted_text)
        print(f"Document '{filename}' processed and indexed with id: {doc_id}")
    except Exception as e:
        print(f"Document processing failed for '{filename}': {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    contents = await file.read()
    background_tasks.add_task(process_file, contents, file.filename)
    return JSONResponse({"message": "Upload successful! Extracting text..."})

class LegalQueryRequest(BaseModel):
    query: str
    context_documents: Optional[List[str]] = []

@app.post("/query")
async def legal_query(request: LegalQueryRequest):
    """
    Existing UI-based query endpoint: uses 'legal_docs' index + Gemma model.
    """
    if not request.context_documents:
        es_results = search_documents(request.query)
        if not es_results:
            return JSONResponse({"query": request.query, "answer": "No relevant documents found."})
        request.context_documents = es_results

    answer = query_gemma(request.query, request.context_documents)
    return JSONResponse({"query": request.query, "answer": answer})

@app.post("/ingest-data")
def ingest_data():
    """
    Ingests data from the 'data/' folder into 'legal_docs' index (existing).
    """
    data_dir = "data"
    total_indexed = 0

    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # HTML
        html_dir = os.path.join(folder_path, "html")
        if os.path.exists(html_dir):
            for file_name in os.listdir(html_dir):
                if file_name.endswith(".html"):
                    with open(os.path.join(html_dir, file_name), "r", encoding="utf-8") as f:
                        text = BeautifulSoup(f, "html.parser").get_text(separator="\n")
                        index_document(text)
                        total_indexed += 1

        # JSON
        json_dir = os.path.join(folder_path, "json")
        if os.path.exists(json_dir):
            for file_name in os.listdir(json_dir):
                if file_name.endswith(".json"):
                    with open(os.path.join(json_dir, file_name), "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                        text = data_content.get("content", str(data_content))
                        index_document(text)
                        total_indexed += 1

    return JSONResponse({"message": f"Ingested {total_indexed} documents into Elasticsearch."})

# -------------------------------------------------------------------------
# 2) NEW: Endpoints for 'caselaw_index'
# -------------------------------------------------------------------------

@app.post("/ingest-caselaw")
def ingest_caselaw_data():
    """
    Ingests HTML and JSON files from the 'data/' directory into 'caselaw_index'.
    """
    data_dir = "data"
    total_indexed = 0

    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # HTML
        html_dir = os.path.join(folder_path, "html")
        if os.path.exists(html_dir):
            for file_name in os.listdir(html_dir):
                if file_name.endswith(".html"):
                    with open(os.path.join(html_dir, file_name), "r", encoding="utf-8") as f:
                        text = BeautifulSoup(f, "html.parser").get_text(separator="\n")
                        index_caselaw(folder_name, text)  # ✅ Fix: Ensure doc_id is passed
                        total_indexed += 1

        # JSON
        json_dir = os.path.join(folder_path, "json")
        if os.path.exists(json_dir):
            for file_name in os.listdir(json_dir):
                if file_name.endswith(".json"):
                    with open(os.path.join(json_dir, file_name), "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                        text = data_content.get("content", str(data_content))
                        index_caselaw(file_name, text)  # ✅ Fix: Ensure doc_id is passed
                        total_indexed += 1

    return JSONResponse({"message": f"Ingested {total_indexed} documents into 'caselaw_index'."})

class CaselawQueryRequest(BaseModel):
    query: str
    size: int = 3  # Default number of docs to retrieve

@app.post("/query-caselaw")
def query_caselaw(request: CaselawQueryRequest):
    """
    Query 'caselaw_index' for relevant docs, then call gemma-based RAG approach.
    """
    docs = search_caselaw(request.query, size=request.size)
    
    if not docs:
        return JSONResponse({"query": request.query, "answer": "No relevant case law found."})

    # Combine docs for a RAG-style context
    combined_context = "\n".join([doc["content"] for doc in docs])
    answer = query_gemma(request.query, [combined_context])

    return JSONResponse({"query": request.query, "answer": answer})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
