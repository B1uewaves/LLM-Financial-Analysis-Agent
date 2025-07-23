# Wraps OpenAI’s ChatCompletion to generate concise summaries.
# Loads and applies your prompt templates
# Returns human‑readable text or bullet‑list summaries of input data.

# tools/summary_tool.py
from dotenv import load_dotenv
import os
from openai import OpenAI, RateLimitError
from datetime import datetime
from typing import Dict, List
from prompts.templates import PROMPTS

# Load environment variables
load_dotenv()

# Instantiate OpenAI client (reads API key from OPENAI_API_KEY and base URL from OPENAI_API_BASE)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Default date string
DEFAULT_TODAY = datetime.today().strftime("%B %d, %Y")


def summarize_stock(
    data: dict,
    headlines: list[str],
    today: str = DEFAULT_TODAY,
    model: str = "gpt-4o-mini"
) -> str:
    """
    data: {
      'ticker': str,
      'name': str,
      'current_price': float or str,
      'pct_change': str,
      'trend_30d': str,
      'volume': str,
      'bid_ask': str,
      'day_range': str,
      'market_cap': str,
      'pe_ratio': str
    }
    headlines: list of latest news headlines
    """
    # 1. Load system prompt from templates
    system_prompt = PROMPTS["summary_template"]["prompt"].template

    # 2. Format headlines
    headlines_text = "\n".join(f"- {h}" for h in headlines)

    # 3. Build user prompt with data fields
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

    # 4. Call OpenAI chat completion
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=640,
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return (
            "⚠️ OpenAI rate limit reached or invalid API key. "
            "Please try again later."
        )

#Multi summary
def summarize_stock_multiple(
    data_items: List[Dict],
    headline_lists: List[List[str]]
) -> str:
    """
    data_items: [ {ticker, name, current_price, pct_change, …}, … ]
    headline_lists:  parallel list of lists of strings
    """
    # Build a comparison prompt

    prompt_sections = []
    for d, h in zip(data_items, headline_lists):
        # Build one section per ticker
        section = f"""
    == {d['ticker']} ({d['name']}) ==
    • Price: ${d['current_price']} ({d['pct_change']:+.2f}%)
    • 30‑day trend: {d['trend_30d']:+.2f}%

    Headlines:
    {''.join(f"- {headline}\n" for headline in h)}
    """
        prompt_sections.append(section)


    prompt = (
        "You are a financial analyst. Compare the performance of the following tickers:\n"
        + "\n".join(prompt_sections)
        + "\nProvide a concise (≤150 words) compare‑and‑contrast focusing on drivers and outlook."
    )

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=640,
    )
    return resp.choices[0].message.content.strip()

def summarize_stock_multiple(
    data_items: List[Dict],
    headline_lists: List[List[str]]
) -> str:
    # 1) Generate individual summaries
    individual_summaries = []
    for d, h in zip(data_items, headline_lists):
        text = summarize_stock(d, h)
        individual_summaries.append(f"• {d['ticker']}: {text}")

    # 2) Build a compare prompt
    prompt = (
        "You are a financial analyst. Here are individual summaries:\n"
        + "\n".join(individual_summaries)
        + "\n\nNow compare and contrast their performance, trends, and key drivers "
          "in a concise (≤150 words) analysis."
    )

    # 3) Call the LLM
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=640,
    )
    return resp.choices[0].message.content.strip()

# Quick REPL test
if __name__ == "__main__":
    example_headlines = [
        "Apple reports record iPhone sales in Q2",
        "Analysts upgrade Apple to ‘buy’ at MajorBank",
        "Services revenue hits all‑time high"
    ]
    # Example usage with default today
    briefing = summarize_stock(
        ticker="AAPL",
        current_price=210.00,
        pct_change="+1.15%",
        trend_30d="up 5.4%",
        volume="48M (avg 37M)",
        bid_ask="$209.95/$210.05",
        day_range="$208.50–$211.50",
        market_cap="$3.3T",
        pe_ratio="27.8×",
        headlines=example_headlines
    )
    print(briefing)