# tools/vector_store.py
from dotenv import load_dotenv
load_dotenv()

import os
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS


PERSIST_DIR = "vector_index"

def load_vector_store():
    """
    Load a persisted FAISS index (and its doc IDs).
    Returns None if no index is found.
    """
    if not os.path.isdir(PERSIST_DIR):
        return None

    embeddings = OpenAIEmbeddings()
    # note: positional args only—first the folder, then embeddings
    return FAISS.load_local(
        PERSIST_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )