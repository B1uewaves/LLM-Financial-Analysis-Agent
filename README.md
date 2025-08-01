#####
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

streamlit run main.py

docker-compose down
docker-compose up --build -d

http://localhost:8501

scp -i llm.pem -r * ubuntu@13.51.206.118:~/llm-agent
ssh -i llm.pem ubuntu@13.51.206.118

then on ec2: 
cd ~/llm-agent
docker compose down        # stop old container
docker compose up --build  # rebuild with new code

docker system prune -a -f --volumes
df -h




http://13.51.206.118:8501


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

Layer 1: Data Ingestion
  ↳ ingest_tool.py         → Handles embedding + indexing

Layer 2: Vector Store Manager (ISOLATED HERE) ✅
  ↳ vector_store.py        → Load, retrieve, save, inspect (generic interface)

Layer 3: Applications
  ↳ summary_tool.py        → Uses retrieve() + summarize()
  ↳ headline_tool.py       → Uses retrieve() + prints titles/snippets


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