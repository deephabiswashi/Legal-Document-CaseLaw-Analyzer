from elasticsearch import Elasticsearch
from .config import settings  # Relative import

# Initialize Elasticsearch client with authentication.
es = Elasticsearch(
    settings.ELASTICSEARCH_HOST,
    api_key=settings.ELASTICSEARCH_API_KEY
)

# ======== LEGAL_DOCS INDEX FUNCTIONS (UNCHANGED) ========

def delete_existing_documents():
    """Deletes all documents from the 'legal_docs' index."""
    try:
        response = es.delete_by_query(index="legal_docs", body={"query": {"match_all": {}}})
        print("[INFO] Deleted existing documents from 'legal_docs' index:", response)
    except Exception as e:
        print("[WARN] Failed to delete documents:", e)

def index_document(text: str):
    """Indexes a piece of text into the 'legal_docs' index.
    
    Before indexing, it clears old data.
    """
    delete_existing_documents()
    doc = {"content": text}
    response = es.index(index="legal_docs", document=doc)
    return response["_id"]

def search_documents(query: str):
    """
    Searches the 'legal_docs' index by query and returns the most recent document's content.
    It sorts by _id in descending order (assuming monotonic increasing IDs).
    """
    response = es.search(
        index="legal_docs",
        body={
            "query": {
                "match": {"content": query}
            },
            "sort": [
                {"_id": {"order": "desc"}}
            ],
            "size": 1
        }
    )
    hits = response["hits"]["hits"]
    if hits:
        return [hits[0]["_source"]["content"]]
    else:
        return []

# ======== CASELAW_INDEX FUNCTIONS (NEWLY ADDED, DELETION) ========

def index_caselaw(doc_id: str, text: str):
    """Indexes a case law document into the 'caselaw_index' without deleting old data."""
    doc = {"doc_id": doc_id, "content": text}
    response = es.index(index="caselaw_index", id=doc_id, document=doc)
    return response["_id"]

def search_caselaw(query: str, size: int = 5):
    """
    Searches the 'caselaw_index' by query and returns the top matching documents.
    """
    response = es.search(
        index="caselaw_index",
        body={
            "query": {
                "match": {"content": query}
            },
            "size": size
        }
    )
    hits = response["hits"]["hits"]
    return [{"doc_id": hit["_id"], "content": hit["_source"]["content"]} for hit in hits]

def delete_caselaw_documents():
    """Deletes all documents from the 'caselaw_index'."""
    try:
        response = es.delete_by_query(index="caselaw_index", body={"query": {"match_all": {}}})
        print("[INFO] Deleted existing documents from 'caselaw_index':", response)
    except Exception as e:
        print("[WARN] Failed to delete documents from 'caselaw_index':", e)
