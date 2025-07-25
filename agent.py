# agent.py
import os
from dotenv import load_dotenv
from pathlib import Path

from typing import Optional, List

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool

from tools.stock_tool import fetch_stock_data
from tools.news_tool import fetch_headlines
from tools.summary_tool import summarize_stock, summarize_stock_multiple
from tools.resolve_tool import resolve_company_name

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
openai_api_base = os.getenv("OPENAI_API_BASE")


# Tool Wrappers (with proper type hints and docstrings)
def stock_data(ticker: str) -> dict:
    """Fetch recent stock data (price, change %, volume, etc.) for a given ticker symbol (e.g., AAPL)."""
    return fetch_stock_data(ticker)

def news_fetch(
    ticker: str,
    filter_type: Optional[str] = None,
    max_results: int = 5
) -> List[dict]:
    """
    Retrieve recent news for a company by ticker.
    And filter by topic (e.g., 'Macbook', 'AI', 'M&A').
    """
    company = resolve_company_name(ticker)
    return fetch_headlines(company, filter_type, max_results)

def summarize(tickers: List[str]) -> str:
    """
    Summarize the stock data and related news for one or more ticker symbols.
    Returns a comparison if more than one ticker is given.
    """
    data_items = []
    headline_lists = []

    for t in tickers:
        data = fetch_stock_data(t)
        if "error" in data:
            return data["error"]
        headlines = fetch_headlines(t)
        data_items.append(data)
        headline_lists.append(headlines)

    if len(tickers) == 1:
        return summarize_stock(data_items[0], headline_lists[0])
    else:
        return summarize_stock_multiple(data_items, headline_lists)


# Agent builder function
def build_agent(memory):
    """Create and return an LLM agent with tools and Redis-backed memory."""

    tools = [
        Tool.from_function(
            func=stock_data,
            name="stock_data",
            description="Get stock market data for a company using its ticker symbol (e.g., AAPL)."
        ),
        Tool.from_function(
            func=news_fetch,
            name="news_fetch",
            description=(
                "Get recent news about a company. "
                "Provide the company name (e.g., 'Apple' or 'Tesla'). "
                "Filter by topic like 'Macbook', 'AI', or 'M&A'."
            )
        ),
        Tool.from_function(
            func=summarize,
            name="summarize",
            description="Summarize stock data and related news for one or more tickers (e.g., ['AAPL'], ['AAPL', 'MSFT'])."
        ),
        Tool.from_function(
        func=resolve_company_name,
        name="resolve_company_name",
        description="Given a stock ticker (like 'TSLA') or company name (like 'Tesla'), return the full company name for news search."
        )
    ]


# LLM setup
llm_kwargs = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0,
}

if openai_api_base:
    llm_kwargs["openai_api_base"] = openai_api_base

llm = ChatOpenAI(**llm_kwargs)

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    memory=memory
    max_iterations=6,
)


# CLI test block
if __name__ == "__main__":
    query = ("Give me news about Apple")
    print("=== React Agent ===")
    print(agent.run(query))
    # print("\n=== Plan-and-Execute Agent ===")
    # print(plan_and_execute_agent(query))
