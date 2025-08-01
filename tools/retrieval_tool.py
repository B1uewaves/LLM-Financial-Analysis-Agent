# tools/retrieval_tool.py
from typing import List, Dict, Tuple
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from tools.vector_store import load_vector_store

def init_vector_store(docs: List[Dict]):
    """
    docs: List of dicts, each containing:
    - title (str)
    - description (str)
    - url (optional)
    - published_at (optional)
    """
    embeddings = OpenAIEmbeddings()
    # build Document objects with explicit metadata
    documents = [
        Document(
            page_content=doc["title"],
            metadata={
                "id": doc.get("id", doc["title"]),
                "description": doc.get("description", ""),
                "url": doc.get("url", ""),
                "published_at": doc.get("published_at", "")
            }
        )
        for doc in docs
    ]
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def retrieve(vector_store: FAISS, query: str, k: int = 5) -> List[Tuple[str, float]]:
    """
    Retrieves top-k relevant headline texts and their similarity scores
    for a given query (e.g., 'Macbook') using the vector store for the ticker.
    
    Args:
        ticker (str): Ticker name used as namespace (e.g., 'AAPL')
        query (str): Query string to match against stored headlines
        k (int): Number of top results to return

    Returns:
        List of (headline, similarity_score)
    """
    if vector_store is None:
        raise RuntimeError("Vector store is None — please load it before calling `retrieve()`.")
    
    return vector_store.similarity_search_with_score(query, k=k)


def merge_vector_stores(store1: FAISS, store2: FAISS) -> FAISS:
    """
    Merges two FAISS vector stores in place.
    Appending new headlines for the same or different tickers
    Keeping one unified FAISS index across sessions
    Returns the combined store.
    """
    store1.merge_from(store2)
    return store1
