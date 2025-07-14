# Pulls the latest headlines via NewsAPI (or another news source)

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # read NEWSAPI_KEY from .env

API_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_headlines(ticker: str, max_results: int = 5) -> list[str]:
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
    titles = []
    for a in articles:
        title = a.get("title", "").strip()
        # skip non-English leftovers or too‑long titles
        if not title or len(title) > 120:
            continue
        titles.append(title)
        if len(titles) >= max_results:
            break

    return titles
