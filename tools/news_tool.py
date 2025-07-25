import os
from dotenv import load_dotenv
from pathlib import Path
import requests
from datetime import datetime
from typing import Optional, cast

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = cast(str, os.getenv("NEWS_API_BASE"))

if not API_KEY:
    raise RuntimeError("Missing NEWSAPI_KEY in environment")

# Map shorthand to full filter phrases and keywords for manual filtering
FILTER_MAP = {
    "M&A": {
        "phrase": "mergers and acquisitions",
        "keywords": ["merger", "acquisition", "deal", "acquire", "acquisition"],
    },
    "Earnings": {
        "phrase": "earnings",
        "keywords": ["earnings", "earnings report", "earning"],
    },
    # add more filter configs here
}

# === LLM classifier to judge final relevance ===
llm = ChatOpenAI(temperature=0)
relevance_prompt = PromptTemplate(
    input_variables=["title", "description", "filter_topic"],
    template="""
decide if it is directly relevant to Apple Inc.'s business **in the area of {filter_topic}** — for example, new MacBook releases, pricing changes, sales trends, chip upgrades, or strategic decisions involving MacBooks.

Title: {title}

Description: {description}

Respond with only "Yes" or "No".
"""
)

relevance_chain = LLMChain(llm=llm, prompt=relevance_prompt)

def judge_article_relevance(article: dict, filter_topic: str) -> bool:
    """
    Uses LLM to determine if a news article is directly relevant to Apple’s business/products/strategy.
    """
    response = relevance_chain.run({
        "title": article.get("title", ""),
        "description": article.get("description", ""),
        "filter_topic": filter_topic
    })
    return response.strip().lower().startswith("yes")

# === Main news fetcher ===    
def fetch_headlines(
    ticker: str,
    filter_type: Optional[str] = None,
    max_results: int = 5,
) -> list[dict]:
    """
    Retrieve up to `max_results` news articles for a company (by name or ticker).
    Filters articles using keywords and LLM-based relevance checking.
    """
    # Validate dates
    params = {
        "q": f'"{ticker}"',
        "language": "en",
        "sortBy": "publishedAt",
        # fetch more to allow manual filtering
        "pageSize": max_results * 10,
        "apiKey": API_KEY,
    }


    # Fetch articles
    try:
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
    except Exception as e:
        return [{"error": f"Failed to fetch headlines: {e}"}]

    # Determine keywords for filtering
    if filter_type and filter_type in FILTER_MAP:
        cfg = FILTER_MAP[filter_type]
        keywords = cfg["keywords"]
    elif filter_type:
        # use raw filter_type as keyword
        keywords = [filter_type.lower()]
    else:
        keywords = None

    # Step 1: Keyword filtering
    keyword_filtered = []
    for art in articles:
        text = (art.get("title", "") + " " + art.get("description", "")).lower()
        if keywords and not any(kw in text for kw in keywords):
            continue
        keyword_filtered.append(art)

    # Step 2: LLM relevance filtering
    final_results = []
    seen = set()
    for art in keyword_filtered:
        if not judge_article_relevance(art, filter_type):
            continue

        url = art.get("url")
        if not url or url in seen:
            continue

        seen.add(url)
        title = art.get("title", "").strip()
        desc = art.get("description", "").strip()
        pub = art.get("publishedAt", "")

        if len(title) > 120:
            title = title[:117] + "..."
        if len(desc) > 300:
            desc = desc[:297] + "..."

        final_results.append({
            "title": title,
            "description": desc,
            "url": url,
            "published_at": pub,
        })

        if len(final_results) >= max_results:
            break

    return final_results