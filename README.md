# LLM LangChain Stock & News Agent

## Overview  
A lightweight Streamlit app + LangChain agent that fetches real‑time stock data (via yfinance), summarizes news with OpenAI, and provides basic price forecasts.

## Features  
- ✅ Live stock quotes & charts  
- 🧠 LLM‑powered company news summaries  
- 🔮 ML‑based short‑term price forecasts  
- ☁️ Deployable to Hugging Face Spaces

## Project Structure  
```text
project/
├── agent.py
├── main.py
├── tools/
│   ├── stock_tool.py
│   ├── summary_tool.py
│   └── forecast_tool.py
├── prompts/
│   └── templates.py
├── requirements.txt
├── .env.example
├── .huggingface.yaml
└── README.md