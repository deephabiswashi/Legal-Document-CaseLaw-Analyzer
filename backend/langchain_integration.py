import time
import requests
from .config import settings  # Ensure settings.OLLAMA_HOST is correctly configured

def query_gemma(query: str, context_documents: list) -> str:
    """
    Send a legal query to the Ollama Gemma3:4b model, using retrieved context documents.
    Implements a retry mechanism for connection errors and increases the timeout.
    """
    context = "\n".join(context_documents) if context_documents else "No context provided."
    prompt = f"Legal Query: {query}\n\nRelevant Documents:\n{context}\n\nAnswer:"

    payload = {
        "model": "gemma3:4b",  # Updated model name
        "prompt": prompt,
        "max_tokens": 500,     # Allows a more complete answer
        "stream": False        # Ensures we get the full response at once
    }
    
    url = f"{settings.OLLAMA_HOST}/api/generate"
    max_retries = 3
    timeout_val = 120  # Increase timeout to 30 seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=timeout_val)
            response.raise_for_status()  # Raises an HTTPError if status is not 200
            data = response.json()
            return data.get("response", "No answer generated")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                return f"Connection failed after {max_retries} attempts: {str(e)}"
