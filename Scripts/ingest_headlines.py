#!/usr/bin/env python3
"""
scripts/ingest_headlines.py

Fetch latest headlines for a list of tickers, embed them, and rebuild/save the FAISS index.
"""
import os
from tools.news_tool import fetch_headlines
from tools.retrieval_tool import init_vector_store

# Define your list of top tickers (or load from a config/YAML)
def load_tickers():
    return [
        "AAPL","MSFT","GOOGL","AMZN","TSLA",
        "NVDA","META","BRK.B","JPM","JNJ",
        "V","WMT","PG","UNH","MA",
        "DIS","HD","BAC","XOM","PFE"
    ]


def main():
    # 1) Collect docs: (doc_id, text) tuples
    docs = []
    for ticker in load_tickers():
        headlines = fetch_headlines(ticker)
        for idx, headline in enumerate(headlines):
            doc_id = f"{ticker}_{idx}"
            docs.append((doc_id, headline))

    # 2) Build a fresh FAISS vector store
    vector_store = init_vector_store(docs)

    # 3) Persist to disk
    index_path = os.environ.get("FAISS_INDEX_PATH", "faiss_index")
    os.makedirs(index_path, exist_ok=True)
    vector_store.save_local(index_path)

    print(f"[Ingest] Indexed {len(docs)} documents to '{index_path}'")


if __name__ == "__main__":
    main()
