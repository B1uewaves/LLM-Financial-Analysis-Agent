# Houses your prompt engineering:

# prompts/templates.py

from langchain_core.prompts import PromptTemplate

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
        "headlines",
        "today"
    ],
    template="""
You are a sell-side equity analyst preparing a short institutional briefing on {ticker}.  
Write in a clear, neutral, and data-driven tone suitable for executive readers.  
Use approximately **150 words** to concisely summarize current performance, key metrics, and recent news.  
Do **not cut off any sentence**.  
Follow the six-section structure below and ensure **all six sections are completed** before ending.  
Use markdown format for output. 

# Briefing on {ticker}
**Date:** {today}

1. **Price & Movement**  
• Price: {current_price} ({pct_change})  
• 30-Day Trend: {trend_30d}  
• Comment on price momentum, sector-relative performance, or technical strength.

2. **Trading Activity & Liquidity**  
• Volume: {volume}  
• Bid/Ask: {bid_ask}  
• Day Range: {day_range}  
• Note any significant deviation from average volume or notable spread behavior.

3. **Valuation & Market Cap**  
• Market Cap: {market_cap}  
• P/E Ratio: {pe_ratio}  
• Compare briefly to sector average or historical norm if relevant.

4. **Recent Drivers**  
{headlines}  
• Attribute analyst upgrades or company news to specific, credible sources (e.g. JPMorgan, Goldman Sachs, Bloomberg, Reuters).
5. **Risks & Sentiment**  
• State one specific forward risk.  
• Summarize investor sentiment (e.g. constructive, cautious, mixed).

6. **Outlook**  
• **Bull Case:** Identify a credible upside catalyst.  
• **Bear Case:** Point to a plausible downside risk to revenue, margins, or valuation.

Return only the formatted briefing in markdown.
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
