#!/usr/bin/env python3
"""
rag_query_caselaw.py
--------------------
A standalone script to query the 'caselaw_index' in Elasticsearch
and generate answers via LangChain + Ollama (gemma3:4b).
"""

import os
from typing import List
from elasticsearch import Elasticsearch
from langchain.llms import Ollama

# -------------
# Config
# -------------
ELASTIC_HOST = "http://localhost:9200"
ELASTIC_API_KEY = "LVpCU2xaVUJyYjB3VjJ1VXF2WDU6NnlKYzNVZW5RbnlTTThkRHZsZWdhUQ=="
INDEX_NAME = "caselaw_index"
OLLAMA_HOST = "http://127.0.0.1:11434"  # Where your Ollama is served
OLLAMA_MODEL = "gemma3:4b"  # Or "llama3.1:8b", etc.

# Create an Elasticsearch client
es = Elasticsearch(
    ELASTIC_HOST,
    api_key=ELASTIC_API_KEY
)

def search_legal_docs(query: str, size: int = 3) -> List[str]:
    """
    Searches the 'caselaw_index' for relevant content.
    Returns up to 'size' documents' content as a list of strings.
    """
    body = {
        "query": {
            "match": {
                "content": query
            }
        },
        "size": size
    }
    response = es.search(index=INDEX_NAME, body=body)
    hits = response["hits"]["hits"]
    return [hit["_source"]["content"] for hit in hits]

def query_ollama(query: str, context: str) -> str:
    """
    Combines the query + context into a single prompt and sends it to Ollama.
    Uses the LangChain Ollama LLM wrapper for convenience.
    """
    llm = Ollama(
        base_url=OLLAMA_HOST,
        model=OLLAMA_MODEL,
        # Additional Ollama settings if needed
    )
    # Example RAG-style prompt
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    # Run the model
    answer = llm(prompt)
    return answer

def main():
    """
    1) Prompt user for a query.
    2) Search Elasticsearch for relevant docs.
    3) Combine them into context.
    4) Ask Ollama for a final answer.
    """
    user_query = input("Enter your legal question: ")

    docs = search_legal_docs(user_query, size=3)
    if not docs:
        print("[INFO] No relevant documents found.")
        return

    # Combine top docs into a single context
    combined_context = "\n".join(docs)

    # Query Ollama
    answer = query_ollama(user_query, combined_context)
    print("\n=== RAG Chatbot Answer ===")
    print(answer)

if __name__ == "__main__":
    main()
