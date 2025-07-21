# Drives batch ingestion of new documents (e.g. headlines) into your vector store.
# Coordinates fetching, embedding, and FAISS index rebuilding.

from typing import Tuple, List
import pickle
from tools.news_tool import fetch_headlines
from tools.retrieval_tool import init_vector_store

# directory where FAISS will persist its index + docstore
PERSIST_DIR = "vector_index"

def ingest_headlines_for_ticker(
    ticker: str,
    max_results: int = 20,
    persist: bool = True
) -> None:
    """
    1. Fetch recent headlines for a ticker
    2. Turn them into (doc_id, text) pairs
    3. Initialize or update FAISS index
    4. Optionally persist index + metadata to disk
    """
    headlines = fetch_headlines(ticker, max_results=max_results)
    # create simple unique IDs
    docs: List[Tuple[str, str]] = [
        (f"{ticker.lower()}_{i}", text)
        for i, text in enumerate(headlines)
    ]

    # build the vector store and persist it into a directory    
    vector_store = init_vector_store(docs)
    if persist:
        vector_store.save_local(PERSIST_DIR)
        print(f"[ingest] Indexed {len(docs)} docs for {ticker.upper()} → persisted in `{PERSIST_DIR}/`")
