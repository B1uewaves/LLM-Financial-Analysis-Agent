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

+-------------------+
|    main.py        |  <-- Streamlit UI, entry point
+-------------------+
          |
          v
+-------------------+         +-------------------+
| stock_tool.py     |         | news_tool.py      |
| fetch_stock_data  |         | fetch_headlines   |
+-------------------+         +-------------------+
          |                           |
          +-----------+---------------+
                      |
                      v
             +-------------------+
             | ingest_tool.py    |  <-- Ingests headlines, builds vector index
             | ingest_headlines  |
             +-------------------+
                      |
                      v
             +-------------------+
             | retrieval_tool.py |  <-- Builds/queries FAISS vector store
             | init_vector_store |
             | retrieve          |
             +-------------------+
                      |
                      v
             +-------------------+
             | vector_store.py   |  <-- Loads/saves FAISS index
             | load_vector_store |
             +-------------------+
                      |
                      v
             +-------------------+
             | vector_index/     |  <-- Persisted vector data
             +-------------------+

          |
          v
+-------------------+
| summary_tool.py   |  <-- LLM summary, uses OpenAI
| summarize         |
+-------------------+
          ^
          |
+-------------------+
| prompts/          |  <-- Prompt templates (YAML, .py)
+-------------------+


Browser Tab
  |
  |-- st.session_state["session_id"] = "session-123"
  |-- st.session_state["agent"] = build_agent(memory)
  |
Streamlit Server (main.py reruns on input)
  |
  |-- get_memory("session-123") → RedisChatMessageHistory
  |
  |-- agent.run("What changed since last time?")
  |
Redis
  |
  |-- Key: "session-123"
  |-- Value: [ {user: "Show TSLA"}, {AI: "TSLA is up 5%..."} ]