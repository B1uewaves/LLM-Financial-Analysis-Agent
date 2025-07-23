# agent.py
import os
from dotenv import load_dotenv

# 1) Load and verify environment
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not set!"

# 2) Imports for LangChain and tools
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType

from tools.stock_tool    import fetch_stock_data
from tools.news_tool     import fetch_headlines
from tools.summary_tool  import summarize_stock, summarize_stock_multiple

import ast
import re

# 1) Instantiate the LLM wrapper
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE"),  # Optional custom endpoint
    temperature=0,
)

# 2) Safe wrapper for stock tool to handle errors gracefully

def stock_data_tool(raw_input: str) -> str:
    """
    Normalize the LLM's raw action input so only the ticker symbol is passed
    to fetch_stock_data, then return either data dict or error string.
    """
    # Extract ticker if provided as ticker='AAPL' or with extra whitespace/quotes
    if "=" in raw_input:
        _, rhs = raw_input.split("=", 1)
        raw_input = rhs
    ticker = raw_input.strip().strip('"\' ')

    # Fetch data
    data = fetch_stock_data(ticker)
    if "error" in data:
        return data["error"]
    return data

# 3) Define other tool wrappers if needed
#    The news_tool returns a list of headlines directly, so no wrapper.
#    The summarize_stock tool expects two inputs; we'll wrap below.


def summarize_wrapper(raw_input: str) -> str:
    """
    raw_input example:
      'AAPL stock data dict, AAPL news headlines, MSFT stock data dict, MSFT news headlines'

    This wrapper will:
      1) extract ['AAPL','MSFT']
      2) fetch data & headlines for each
      3) call summarize_stock() if 1 ticker, else summarize_stock_multiple()
    """
    # 1) find tickers (assumes tickers are 1–5 uppercase letters)
    tickers = re.findall(r"\b[A-Z]{1,5}\b", raw_input)
    # dedupe while preserving order
    seen = set(); tickers = [t for t in tickers if not (t in seen or seen.add(t))]

    if not tickers:
        return "Error: no valid tickers found in input."

    # 2) fetch data & headlines
    data_items     = []
    headline_lists = []
    for tkr in tickers:
        data = fetch_stock_data(tkr)
        if "error" in data:
            return data["error"]
        data_items.append(data)

        headlines = fetch_headlines(tkr)
        headline_lists.append(headlines)

    # 3) delegate to the proper summarizer
    if len(tickers) == 1:
        return summarize_stock(data_items[0], headline_lists[0])
    else:
        return summarize_stock_multiple(data_items, headline_lists)

# Register your tools
tools = [
    Tool("stock_data", fetch_stock_data, "Given a ticker, returns a dict of stock metrics."),
    Tool("news_fetch", fetch_headlines,  "Given a ticker, returns a list of recent headlines."),
    Tool("summarize",  summarize_wrapper, "Given the agent’s Action Input string, fetches data & headlines and returns a summary or comparison."),
]

# 5) Initialize React-style agent
react_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=6,
)

# 6) Optional: DIY Plan-and-Execute wrapper using LLMChain (if desired)
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

# Planner chain
planner_prompt = PromptTemplate(
    input_variables=["task"],
    template="""
You are an expert planner. Break down the following request into an ordered JSON list of steps.

Request: {task}

Respond ONLY with a JSON array, e.g. ["step1", "step2", ...].
""",
)
planner_chain = LLMChain(llm=llm, prompt=planner_prompt)

# Plan-and-execute function

def plan_and_execute_agent(query: str) -> str:
    # 1) Plan
    plan_json = planner_chain.run(task=query)
    try:
        steps = json.loads(plan_json)
    except json.JSONDecodeError:
        return react_agent.run(query)

    # 2) Execute
    outputs = []
    for step in steps:
        outputs.append(react_agent.run(step))

    # 3) Return combined
    return "\n\n".join(outputs)

# 7) CLI test block
if __name__ == "__main__":
    query = "Compare AAPL vs MSFT stock performance and news."
    print("=== React Agent ===")
    print(react_agent.run(query))
    # print("\n=== Plan-and-Execute Agent ===")
    # print(plan_and_execute_agent(query))
