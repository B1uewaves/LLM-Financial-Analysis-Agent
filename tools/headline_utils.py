from typing import List, Dict
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = os.getenv("NEWS_API_BASE")

def fetch_headlines_raw(ticker: str, max_results: int = 100) -> List[Dict]:
    params = {
        "q": f'"{ticker}"',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_results,
        "apiKey": API_KEY,
    }

    try:
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json().get("articles", [])
    except Exception as e:
        return []