#####
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

streamlit run main.py

python -m tools.summary_tool 

# LangChain Stock & News Agent

## Overview
A lightweight Streamlit app + LangChain agent that fetches real‑time stock data (via yfinance), summarizes news with OpenAI, and provides basic price forecasts.

## Features
- ✅ Live stock quotes & charts
- 🧠 LLM‑powered company news summaries
- 🔮 ML‑based short‑term price forecasts
- ☁️ Deployable to Hugging Face Spaces

## Project Structure
```text
project/
├── agent.py
├── main.py
├── tools/
│   ├── stock_tool.py   
│   ├── summary_tool.py
│   ├── news_tool.py
│   └── forecast_tool.py
├── prompts/
│   └── templates.py
├── requirements.txt
├── .env.example
├── .huggingface.yaml
└── README.md
```

## Getting Started
1. Clone the repo
2. Create & activate your virtualenv
3. Copy `.env.example` → `.env` and fill in your API keys
4. `pip install -r requirements.txt`
5. `streamlit run main.py`

## Day 1 Goals
- Scaffold repo & folders
- Init virtualenv & install deps
- Write README outline

## agentic Ai(plan, execute, report, finish)
Build stock_tool.py with a get_stock_info(ticker) function
Return from get_stock_info: company name, current price, historical price chart, and key metrics
Test get_stock_info in the console using a dummy ticker

## 
Your finance‑analysis agent is a lightweight, LLM‑driven assistant that lets you ask plain‑English questions about any stock ticker and get back:

Real‑time data: pulls current price, company name, and 30‑day history via yfinance.

News context: fetches the latest headlines from NewsAPI.

Smart summaries: uses an LLM (via LangChain) to turn raw prices and headlines into concise, easy‑to‑read insights.

Natural comparisons: compares two tickers side‑by‑side on performance, news sentiment, and key metrics.

Narrative “forecasts”: prompts the LLM to produce short‑term trend predictions in prose, complete with caveats.

All the “smarts” live in a LangChain agent that decides which data‑fetch tool to call, in what order, and how to compose the final answer—so you get a conversational, AI‑powered finance helper without writing heavy ML code.