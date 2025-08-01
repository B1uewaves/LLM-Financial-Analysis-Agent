# tools/summary_tool.py
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List

from openai import OpenAI, RateLimitError
from tools.vector_store import load_vector_store
from tools.resolve_tool import resolve_company_name
from tools.retrieval_tool import retrieve
from prompts.templates import PROMPTS
from tools.news_tool import extract_keywords_from_query, contains_all_keywords

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

DEFAULT_TODAY = datetime.today().strftime("%B %d, %Y")

def get_relevant_headlines(ticker: str, query: str = "", k: int = 5) -> List[str]:
    store = load_vector_store(ticker)
    if not store:
        return ["(No vector index found — please run ingestion first.)"]

    # ✅ Always resolve company name
    resolved = resolve_company_name(ticker)

    # ✅ Improve default query if needed
    query = query.strip()
    if not query or query.lower() in {"", "company", "news", "company news", ticker.lower()}:
        print(f"[Fallback] No clear query. Using resolved name: {resolved}")
        query = resolved

    # ✅ Keyword extraction from enhanced query
    keyword_info = extract_keywords_from_query(query, ticker=ticker)
    primary_keywords = keyword_info.get("primary_keywords", []) or [resolved]
    secondary_query = " ".join(keyword_info.get("secondary_keywords", [])) or query

    # ✅ Search vector store
    results = retrieve(store, query=secondary_query, k=k * 2)
    headlines = []

    for doc, score in results:
        title = doc.page_content
        url = doc.metadata.get("url", "")
        published = doc.metadata.get("published_at", "")
        description = doc.metadata.get("description", "")
        combined_text = f"{title} {description}"

        if not contains_all_keywords(combined_text, primary_keywords):
            continue

        line = f"{title} ({published})\n{url}" if url else title
        headlines.append(line)

        if len(headlines) >= k:
            break

    return headlines if headlines else ["(No relevant headlines found.)"]


def summarize_stock(
    data: dict,
    query: str = "",
    today: str = DEFAULT_TODAY,
    model: str = "gpt-4.1-nano"
) -> str:
    """
    Summarize the stock data and retrieve headlines using FAISS based on filter_type.
    """
    headlines = get_relevant_headlines(data["ticker"], query)

    # 1. Load prompt
    system_prompt = PROMPTS["summary_template"]["prompt"].template

    # 2. Format input
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    user_prompt = (
        f"ticker: {data.get('ticker')} ({data.get('name')})\n"
        f"date: {today}\n"
        f"current_price: ${float(data.get('current_price')):.2f}\n"
        f"pct_change: {data.get('pct_change')}\n"
        f"trend_30d: {data.get('trend_30d')}\n"
        f"volume: {data.get('volume')}\n"
        f"bid_ask: {data.get('bid_ask')}\n"
        f"day_range: {data.get('day_range')}\n"
        f"market_cap: {data.get('market_cap')}\n"
        f"pe_ratio: {data.get('pe_ratio')}\n"
        f"headlines:\n{headlines_text}\n"
    )

    # 3. LLM call
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=640,
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return "⚠️ OpenAI rate limit or API error."

def summarize_stock_multiple(
    data_items: List[Dict],
    query: str = ""
) -> str:
    """
    Summarizes multiple stocks by retrieving FAISS-based headlines for each and comparing.
    """
    individual_summaries = []
    for d in data_items:
        headlines = get_relevant_headlines(d["ticker"], query)
        summary = summarize_stock(d, query=query)
        individual_summaries.append(f"• {d['ticker']}: {summary}")

    # Comparison prompt
    prompt = (
        "You are a financial analyst. Here are individual summaries:\n"
        + "\n".join(individual_summaries)
        + "\n\nNow compare and contrast their performance, trends, and key drivers "
          "in a concise (≤150 words) analysis."
    )

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=640,
    )
    return resp.choices[0].message.content.strip()

# Test
# if __name__ == "__main__":
    # summary = summarize_stock({
    #     "ticker": "AAPL",
    #     "name": "Apple Inc.",
    #     "current_price": 210.00,
    #     "pct_change": "+1.15%",
    #     "trend_30d": "up 5.4%",
    #     "volume": "48M (avg 37M)",
    #     "bid_ask": "$209.95/$210.05",
    #     "day_range": "$208.50–$211.50",
    #     "market_cap": "$3.3T",
    #     "pe_ratio": "27.8×"
    # }, filter_type="macbook")

    # print(summary)