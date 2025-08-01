#General template

# Agent Benchmark Notes

**Date:** 2025-07-25  
**Objective:** Compare performance and behavior of React vs Plan-and-Execute agents using LangChain.

---

## ✅ Agent Configurations

### 1. React Agent
- **Type:** `ZERO_SHOT_REACT_DESCRIPTION`
- **LLM:** gpt-4.1-nano via `ChatOpenAI`
- **Tools Used:** StockDataFetcher, ContextRetriever, Summarizer

### 2. Plan-and-Execute Agent
- **Type:** `OPENAI_FUNCTIONS`
- **LLM:** gpt-4.1-nano via `ChatOpenAI`
- **Tools Used:** StockDataFetcher, ContextRetriever, Summarizer

---

## 🔍 Test Queries

| Query ID | Prompt |
|----------|--------|
| Q1 | "Summarize recent performance for ticker AAPL." |
| Q2 | "Compare MSFT and AAPL in terms of recent stock performance and major news." |
| Q3 | "Fetch news about Apple's AI strategy" |

---

## 📊 Observations

| Aspect | React Agent | Plan-and-Execute Agent |
|--------|-------------|------------------------|
| **Step Clarity** | Logs every tool call step-by-step; easier to debug | Abstracts the plan; fewer logs unless explicitly added |
| **Response Accuracy (Q1–Q3)** | High, but sometimes repeats context | More concise and structured summary |
| **Error Handling (Q4)** | Tries to continue; vague fallback if ticker invalid | Detects issue more reliably; sometimes halts early |
| **Tool Usage** | Executes one tool at a time; interpretable | Sometimes chains tools more intelligently |
| **Speed** | Slightly faster (~15–20% less latency) | Slightly slower but better at multi-step |
| **Usability for Complex Tasks** | Requires careful prompt crafting | Easier for compound queries |
| **Token Efficiency** | Slightly better | Slightly more verbose internally |

---

## ✅ Conclusion

- **Best for Simple Queries:** ✅ React Agent (faster, step-wise transparent)
- **Best for Complex or Multi-Ticker Analysis:** ✅ Plan-and-Execute Agent (more robust, better reasoning)

### 📌 Decision:
> **Use Plan-and-Execute Agent** as the default, but fall back to **React** for latency-sensitive single-ticker lookups.

---

## 🔧 Next Steps

- Incorporate fallback logic between agent types.
- Log tool usage and response time for real-world queries.
- Begin integrating memory in Day 8.

