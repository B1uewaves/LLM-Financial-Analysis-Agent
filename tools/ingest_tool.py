from typing import Tuple, List
from tools.headline_utils import fetch_headlines_raw
from tools.retrieval_tool import init_vector_store, merge_vector_stores
from tools.vector_store import load_vector_store, save_vector_store

def ingest_headlines_for_ticker(
    ticker: str,
    max_results: int = 100,
    persist: bool = True
) -> None:
    """
    Ingest and vectorize news headlines for a specific ticker.
    Saves the index under vector_index/{ticker}/
    """
    headlines = fetch_headlines_raw(ticker, max_results=max_results)

    docs = []
    for i, article in enumerate(headlines):
        title = article.get("title", "").strip()
        if not title:
            continue

        doc = {
            "id": f"{ticker.lower()}_{i}",
            "title": (article.get("title") or "").strip(),
            "description": (article.get("description") or "").strip(),
            "url": (article.get("url") or "").strip(),
            "published_at": (article.get("published_at") or "").strip()
        }
        docs.append(doc)

    if not docs:
        print(f"[ingest] No headlines found for {ticker.upper()}")
        return

    new_store = init_vector_store(docs)
    existing_store = load_vector_store(namespace=ticker)

    combined_store = merge_vector_stores(existing_store, new_store) if existing_store else new_store

    if persist:
        save_vector_store(combined_store, namespace=ticker)
        print(f"[ingest] Indexed {len(docs)} headlines for {ticker.upper()} → vector_index/{ticker}/")

if __name__ == "__main__":
    # Example: test ingesting Apple headlines
    from sys import argv

    ticker = argv[1] if len(argv) > 1 else "AAPL"
    print(f"[Test] Ingesting headlines for {ticker}...")
    ingest_headlines_for_ticker(ticker)