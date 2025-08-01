from dotenv import load_dotenv
load_dotenv()

import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

BASE_DIR = "vector_index"  # Can contain subfolders per ticker or category

def get_store_path(namespace: str) -> str:
    """
    Resolve a subdirectory path for a specific ticker/company (namespace).
    """
    return os.path.join(BASE_DIR, namespace)

def load_vector_store(namespace: str) -> FAISS | None:
    """
    Load a persisted FAISS index for a specific namespace (e.g., ticker).
    Returns None if not found.
    """
    path = get_store_path(namespace)
    if not os.path.isdir(path):
        return None

    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )

def save_vector_store(store: FAISS, namespace: str) -> None:
    """
    Persist a FAISS store to disk under a specific namespace.
    """
    path = get_store_path(namespace)
    store.save_local(path)