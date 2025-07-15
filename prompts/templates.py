# Houses your prompt engineering:

# prompts/templates.py

from langchain import PromptTemplate

# 1. Summarize raw stock + news data
SUMMARY_TEMPLATE = PromptTemplate(
    input_variables=["ticker", "price_data", "headlines"],
    template="""
You are a financial analyst.
Given the following information for {ticker}:

• Recent price history (last 30 days):  
{price_data}

• Top 5 news headlines:  
{headlines}

Write a concise summary (≤ 100 words) covering:
- Key price trend  
- Most important news  
- Overall outlook

Use bullet points.
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
