# Wraps the OpenAI ChatCompletion API; feeds it your summary prompt (from prompts/templates.py) plus raw data, returns a human‑friendly summary
from dotenv import load_dotenv
import os
import openai
from prompts.templates import SUMMARY_TEMPLATE
from openai import RateLimitError


# load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    model: str = "gpt-3.5-turbo"
    ) -> str:

    """
    Produce a FT‑style morning briefing for a single ticker.
    All inputs should be formatted strings, e.g.:
      pct_change="+1.2%", trend_30d="up 5.4%", headlines="- …\n- …", etc.
    """

    headlines_text = "\n".join(f"- {h}" for h in headlines)

    # 2) Fill template
    prompt = SUMMARY_TEMPLATE.format(
        ticker=ticker,
        current_price=f"${current_price:.2f}",
        pct_change=pct_change,
        trend_30d=trend_30d,
        volume=volume,
        bid_ask=bid_ask,
        day_range=day_range,
        market_cap=market_cap,
        pe_ratio=pe_ratio,
        headlines=headlines_text
    )

    # 3) Call the API
    try:
        resp = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful equity research assistant."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.5,
            max_tokens=250,
        )
        raw = resp.choices[0].message.content or ""
        return raw.strip()

    except RateLimitError:
        return "⚠️ OpenAI quota reached—unable to generate briefing right now."

# 4) Quick REPL test
if __name__ == "__main__":
    example_headlines = [
        "Apple reports record iPhone sales in Q2",
        "Analysts upgrade Apple to ‘buy’ at MajorBank",
        "Services revenue hits all‑time high"
    ]
    print(summarize(
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
    ))