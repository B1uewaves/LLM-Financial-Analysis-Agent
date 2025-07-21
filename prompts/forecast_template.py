from dataclasses import dataclass
from langchain_core.prompts import PromptTemplate

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
