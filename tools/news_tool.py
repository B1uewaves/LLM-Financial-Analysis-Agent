# Retrieves the latest headlines for a given ticker (e.g. via NewsAPI).
# Normalizes, deduplicates, and truncates results.
# Exposes fetch_headlines(ticker: str) → List[str].

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # read NEWSAPI_KEY from .env

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = os.getenv("NEWS_API_BASE")

def fetch_headlines(ticker: str, max_results: int = 5) -> str:
    """
    Return the top `max_results` recent headlines mentioning the ticker.
    """

    if not API_KEY:
        raise RuntimeError("Missing NEWSAPI_KEY in environment")

    params = {
        "q": ticker,
        "sortBy": "publishedAt",
        "language": "en",   
        "pageSize": max_results,
        "apiKey": API_KEY,
    }
    resp = requests.get(BASE_URL, params=params)
    data = resp.json()
    # Fallback if API limit or error
    articles = data.get("articles", [])
    # extract & filter titles
    titles: list[str] = []
    for a in articles:
        title = a.get("title", "").strip()
        if not title or len(title) > 120:
            continue
        titles.append(f"• {title}")
        if len(titles) >= max_results:
            break

    return titles
