# agent.py
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List, Union

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.tools import StructuredTool

from tools.stock_tool import fetch_stock_data
from tools.news_tool import fetch_headlines
from tools.summary_tool import summarize_stock, summarize_stock_multiple
from tools.resolve_tool import resolve_company_name
from memory import get_memory
from pydantic import BaseModel, Field

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
openai_api_base = os.getenv("OPENAI_API_BASE")

# Tool Wrappers
def stock_data(ticker: str) -> dict:
    """Fetch stock market data for a ticker symbol (e.g., AAPL)."""
    return fetch_stock_data(ticker)

def news_fetch(ticker: str, query: str, max_results: int = 5) -> List[dict]:
    """
    Fetch recent vector-based headlines about a company.
    Example: ticker="AAPL", query="AI chip development"
    """
    company = resolve_company_name(ticker)
    return fetch_headlines(company, query=query, max_results=max_results)

def summarize(tickers: Union[str, List[str]], query: Optional[str] = "") -> str:
    """
    Summarize stock and news data for VALID tickers like AAPL or MSFT.
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    data_items = []
    for ticker in tickers:
        data = fetch_stock_data(ticker)
        if "error" in data:
            return data["error"]
        data_items.append(data)

    if len(data_items) == 1:
        return summarize_stock(data_items[0], query=query)
    else:
        return summarize_stock_multiple(data_items, query=query)

class NewsFetchInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol (e.g., AAPL)")
    query: str = Field(..., description="The topic to search for, like 'AI chip development'")

class SummarizeInput(BaseModel):
    tickers: Union[str, List[str]] = Field(..., description="One or more stock tickers like AAPL or MSFT.")
    query: Optional[str] = Field("", description="Optional news topic to summarize, like 'AI chip development'.")

# Agent builder
def build_agent(memory):
    tools = [
        Tool.from_function(
            func=stock_data,
            name="stock_data",
            description="Get stock market data using a ticker (e.g., AAPL)."
        ),
        StructuredTool.from_function(
            func=news_fetch,
            name="news_fetch",
            description="Get recent news about a company. You must provide a stock ticker (e.g., AAPL) and a topic or area of focus (e.g., 'AI chip development', 'Siri strategy').",
            args_schema=NewsFetchInput,
            return_direct=False

        ),
        StructuredTool.from_function(
            func=summarize,
            name="summarize",
            description="Summarize one or more stocks using filtered headlines and financial metrics. You can specify a topic like 'AI chip development'.",
            args_schema=SummarizeInput,
            return_direct=False
        ),

        Tool.from_function(
            func=resolve_company_name,
            name="resolve_company_name",
            description="Resolve a stock ticker or company name to the full company name."
        )
    ]

    llm_args = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0,
    }
    if openai_api_base:
        llm_args["openai_api_base"] = openai_api_base

    llm = ChatOpenAI(**llm_args, streaming=True)

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
        max_iterations=6
    )

# CLI test
if __name__ == "__main__":
    memory = get_memory(session_id="cli-test-session")
    agent = build_agent(memory)
    print(agent.run("Summarize ticker AAPL"))
