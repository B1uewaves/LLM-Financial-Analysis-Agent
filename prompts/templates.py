# Houses your prompt engineering:

# prompts/templates.py

from langchain import PromptTemplate

# 1. Summarize raw stock + news data
SUMMARY_TEMPLATE = PromptTemplate(
    input_variables=[
        "ticker",
        "current_price",
        "pct_change",
        "trend_30d",
        "volume",
        "bid_ask",
        "day_range",
        "market_cap",
        "pe_ratio",
        "headlines"
    ],
    template="""
You are an equity research analyst preparing a 2‑minute morning briefing.  
Produce a concise, bullet‑point summary on {ticker}, covering:

1. **Price & Movement**  
   • Current Price: {current_price} ({pct_change})  
   • 30‑Day Trend: {trend_30d}

2. **Trading Activity & Liquidity**  
   • Volume: {volume}  
   • Bid/Ask: {bid_ask}  
   • Day’s Range: {day_range}

3. **Valuation & Market Cap**  
   • Market Cap: {market_cap}  
   • P/E Ratio: {pe_ratio}

4. **Recent Drivers**  
   {headlines}

5. **Risks & Sentiment**  
   Briefly note one key risk and overall market sentiment.

6. **Outlook**  
   One‑sentence bull case and one‑sentence bear case.

Write in formal, sell‑side tone. Limit to ~150 words in total.
""".strip()
)

# 2. Compare two tickers side‑by‑side
COMPARISON_TEMPLATE = PromptTemplate(
    input_variables=["ticker_a", "data_a", "ticker_b", "data_b"],
    template="""
You are an expert investor advisor.
Compare {ticker_a} vs. {ticker_b} based on:

{ticker_a} data:  
{data_a}

{ticker_b} data:  
{data_b}

Provide:
1. A short (≤ 50 words) summary of each.  
2. Three bullet‑pointed differences.  
3. A one‑sentence recommendation.
""".strip()
)

# 3. Narrative “forecast” for next‑day trend
FORECAST_TEMPLATE = PromptTemplate(
    input_variables=["ticker", "recent_trends"],
    template="""
You are the market’s oracle.  
Given the recent trends for {ticker}:

{recent_trends}

Write a brief, narrative forecast of tomorrow’s likely price movement.  
Include one key factor driving the prediction and a disclaimer.
""".strip()
)
