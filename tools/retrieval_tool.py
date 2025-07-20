# tools/retrieval_tool.py
from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def init_vector_store(docs: List[Tuple[str, str]]):
    """
    docs: List of (doc_id, text) tuples
    """
    embeddings = OpenAIEmbeddings()
    # build Document objects with explicit metadata
    documents = [
        Document(page_content=text, metadata={"id": doc_id})
        for doc_id, text in docs
    ]
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def retrieve(vector_store, query: str, k: int = 5) -> List[Tuple[str, float]]:
    if vector_store is None:
        raise RuntimeError(
            "Vector store not initialized. Please run ingest_headlines_for_ticker(...) first."
        )
    results = vector_store.similarity_search_with_score(query, k=k)
    output = []
    for doc, score in results:
        # now metadata["id"] definitely exists
        doc_id = doc.metadata.get("id", "<unknown>")
        output.append((doc_id, float(score)))
    return output
