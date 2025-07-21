from dataclasses import dataclass
from langchain_core.prompts import PromptTemplate

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