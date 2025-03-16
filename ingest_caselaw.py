#!/usr/bin/env python3
"""
ingest_caselaw.py
-----------------
A standalone script to ingest case law data from the 'data/' folder
into a new Elasticsearch index named 'caselaw_index'.
"""

import os
import json
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

# ----------------------------------------------------
# 1) Configure Elasticsearch Connection
# ----------------------------------------------------
ELASTIC_HOST = "http://localhost:9200"
ELASTIC_API_KEY = "LVpCU2xaVUJyYjB3VjJ1VXF2WDU6NnlKYzNVZW5RbnlTTThkRHZsZWdhUQ=="  # Replace with your actual key
INDEX_NAME = "caselaw_index"

# Create an Elasticsearch client using your API key
es = Elasticsearch(
    ELASTIC_HOST,
    api_key=ELASTIC_API_KEY
)

def create_index_if_needed():
    """
    Creates the 'caselaw_index' in Elasticsearch if it doesn't exist already,
    with basic mappings suitable for text search.
    """
    if not es.indices.exists(index=INDEX_NAME):
        print(f"[INFO] Creating index '{INDEX_NAME}'...")
        es.indices.create(index=INDEX_NAME, body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text"}
                }
            }
        })
    else:
        print(f"[INFO] Index '{INDEX_NAME}' already exists.")

def ingest_caselaw_data(data_dir="data"):
    """
    Iterates through subfolders (e.g., '1', '2', etc.), ingesting HTML, JSON,
    and metadata files into Elasticsearch.
    """
    total_indexed = 0

    # Optionally clear the index if you want a fresh start each time:
    # es.delete_by_query(index=INDEX_NAME, body={"query": {"match_all": {}}})

    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue  # skip if it's not a directory

        # --------------------------
        # 1) Ingest HTML files
        # --------------------------
        html_dir = os.path.join(folder_path, "html")
        if os.path.exists(html_dir) and os.path.isdir(html_dir):
            for file_name in os.listdir(html_dir):
                if file_name.endswith(".html"):
                    file_path = os.path.join(html_dir, file_name)
                    with open(file_path, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "html.parser")
                        text = soup.get_text(separator="\n")
                        if text.strip():
                            doc = {"content": text}
                            es.index(index=INDEX_NAME, document=doc)
                            total_indexed += 1

        # --------------------------
        # 2) Ingest JSON files
        # --------------------------
        json_dir = os.path.join(folder_path, "json")
        if os.path.exists(json_dir) and os.path.isdir(json_dir):
            for file_name in os.listdir(json_dir):
                if file_name.endswith(".json"):
                    file_path = os.path.join(json_dir, file_name)
                    with open(file_path, "r", encoding="utf-8") as f:
                        data_content = json.load(f)
                        # If there's a 'content' field, use that; otherwise store everything
                        if isinstance(data_content, dict) and "content" in data_content:
                            text = data_content["content"]
                        else:
                            text = str(data_content)
                        if text.strip():
                            doc = {"content": text}
                            es.index(index=INDEX_NAME, document=doc)
                            total_indexed += 1

        # --------------------------
        # 3) Ingest 'metadata' files (optional)
        # --------------------------
        # If you want to parse the 'metadata' directory, do so here:
        # e.g., read .txt or .json, extract relevant fields, index them.

    print(f"[INFO] Ingested {total_indexed} documents into '{INDEX_NAME}'.")

if __name__ == "__main__":
    create_index_if_needed()
    ingest_caselaw_data("data")
