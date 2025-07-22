# Wraps OpenAI’s ChatCompletion to generate concise summaries.
# Loads and applies your prompt templates
# Returns human‑readable text or bullet‑list summaries of input data.

# tools/summary_tool.py
# tools/summary_tool.py
from dotenv import load_dotenv
import os
from openai import OpenAI, RateLimitError
from datetime import datetime

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


def summarize(
    ticker: str,
    current_price: float,
    pct_change: str,
    trend_30d: str,
    volume: str,
    bid_ask: str,
    day_range: str,
    market_cap: str,
    pe_ratio: str,
    headlines: list[str],
    today: str = DEFAULT_TODAY,
    model: str = "gpt-4o-mini"
) -> str:
    # 1. Build the system prompt once from your template (includes examples + task)
    system_prompt = PROMPTS["summary_template"]["prompt"].template

    # 2. Build a compact user prompt with only the new data
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    user_prompt = (
        f"ticker: {ticker}\n"
        f"today: {today}\n"
        f"current_price: ${current_price:.2f}\n"
        f"pct_change: {pct_change}\n"
        f"trend_30d: {trend_30d}\n"
        f"volume: {volume}\n"
        f"bid_ask: {bid_ask}\n"
        f"day_range: {day_range}\n"
        f"market_cap: {market_cap}\n"
        f"pe_ratio: {pe_ratio}\n"
        f"headlines:\n{headlines_text}\n"
    )

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
        return "⚠️ OpenAI rate limit reached or invalid API key. Please try again later."



# Quick REPL test
if __name__ == "__main__":
    example_headlines = [
        "Apple reports record iPhone sales in Q2",
        "Analysts upgrade Apple to ‘buy’ at MajorBank",
        "Services revenue hits all‑time high"
    ]
    # Example usage with default today
    briefing = summarize(
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