import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Tuple

from tools.vector_store import load_vector_store
from tools.retrieval_tool import retrieve
from tools.ingest_tool import ingest_headlines_for_ticker
from tools.resolve_tool import resolve_company_name
from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

# Use a lightweight model for fast keyword extraction
llm_keyword = ChatOpenAI(temperature=0, model="gpt-4.1-nano")

def contains_all_keywords(text: str, keywords: List[str]) -> bool:
    """
    Check if all keywords are present in the given text (case-insensitive).
    """
    text_lower = text.lower()
    return all(keyword.lower() in text_lower for keyword in keywords)

def extract_keywords_from_query(query: str, ticker: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Use LLM to extract primary and secondary keywords from a *cleaned* query.
    Replaces ticker-only or vague queries with resolved company names *before* prompting the LLM.
    """
    query = query.strip()
    resolved = resolve_company_name(ticker) if ticker else None

    # Case 1: Vague query
    if not query or query.lower() in {"news", "company", "company news"}:
        query = resolved or "financial news"
        print(f"[Fallback] Replaced vague query with: {query}")

    # Case 2: Ticker symbol used directly
    elif ticker and query.upper() == ticker.upper():
        query = resolved
        print(f"[Fallback] Replaced ticker symbol with resolved name: {query}")

    # Case 3: Query is missing resolved company name
    elif ticker and resolved and resolved.lower() not in query.lower():
        query = f"{resolved} {query}"
        print(f"[Enhancement] Added company name to query: {query}")

    # === Now safe to pass to LLM ===
    prompt = ChatPromptTemplate.from_template("""
You are an advanced keyword extraction system helping a financial news search agent.

Your job is to extract:

1. **Primary keywords**: Specific named entities, products, technologies, or COMPOUND NOUN PHRASES (e.g., "AI chip", "carbon emission policy", "Apple") that MUST appear in the news title or description. These are essential concepts the article is fundamentally about.

2. **Secondary keywords**: Supporting terms, time references, or general actions (e.g., "launch", "development", "strategy") that are useful context but not required.

Avoid generic terms like “news” or “report.” Extract compound concepts exactly as they appear (e.g., "AI chip" not "AI" and "chip").

Return a JSON object with two arrays.

---

**Example 1**

Query: "Apple AI chip development"

Output:
{{
  "primary_keywords": ["Apple", "AI chip"],
  "secondary_keywords": ["development"]
}}

---

**Now extract keywords for this query**:

Query: {query}
""")

    try:
        chain = prompt | llm_keyword
        response = chain.invoke({"query": query})
        print("[Keyword Extraction] Raw LLM response:", response.content.strip())
        return eval(response.content.strip())
    except Exception as e:
        print(f"[Keyword Extractor] Error: {e}")
        return {"primary_keywords": [], "secondary_keywords": []}



# Global in-memory relevance cache
relevance_cache = {}

def judge_relevance_cached(title: str, description: str, topic: str, threshold: float = 0.4) -> bool:
    """
    Check whether a headline is relevant to a topic using LLM (cached).
    """
    key = (title, description, topic)
    if key in relevance_cache:
        return relevance_cache[key]

    # Call LLM
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain

    llm = ChatOpenAI(temperature=0)
    prompt = PromptTemplate(
        input_variables=["title", "description", "filter_topic"],
        template="""
Decide if the following article is directly relevant to the company's business **in the area of {filter_topic}**.

Relevant examples include:
- developer tools, APIs, and SDKs
- App Store policy or commissions
- developer relations or platform changes
- strategic direction, legal disputes, or regulations affecting the App Store
- app approval/rejection controversies

Title: {title}

Description: {description}

Respond ONLY with a float between 0 and 1. Be strict: 
0 = not clearly about {filter_topic}, 1 = directly about it.
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "title": title,
        "description": description,
        "filter_topic": topic
    }).strip()

    try:
        score = float(response)
        is_relevant = score >= threshold
    except ValueError:
        print(f"[judge_relevance_cached] Failed to parse response: {response}")
        is_relevant = False

    relevance_cache[key] = is_relevant
    return is_relevant

# === Revised Headline Retriever using Vector Store ===
from typing import Optional, List, Dict, Tuple
from langchain.schema import Document

def fetch_headlines(
    ticker: str,
    query: str,
    max_results: int = 5,
    auto_ingest: bool = True,
    is_relevant: bool = True
) -> List[Dict]:
    """
    Retrieve relevant headlines for a company from its FAISS vector store.
    Applies primary keyword filtering and optional LLM-based filtering.
    """
    if not query or not query.strip() or query.lower().strip() in {"company news", "news", "general"}:
        return [{"error": "Query too vague — please use a descriptive topic like 'Apple AI strategy'."}]

    # 🔍 Step 1: Extract primary/secondary keywords
    keyword_info = extract_keywords_from_query(query, ticker=ticker)

    resolved_name = resolve_company_name(ticker)
    primary_keywords = keyword_info.get("primary_keywords", []) or [resolved_name]
    if not primary_keywords:
    # Fallback to at least include ticker name
        primary_keywords = [ticker]
        print(f"[Fallback] Using ticker as primary keyword: {ticker}")

    secondary_query = " ".join(keyword_info.get("secondary_keywords", [])) or query

    print(f"[Keyword Extraction] Primary: {primary_keywords} | Secondary Query: '{secondary_query}'")


    # Step 2: Load or ingest vector store
    vector_store = load_vector_store(ticker)
    if not vector_store and auto_ingest:
        ingest_headlines_for_ticker(ticker, max_results=100)
        vector_store = load_vector_store(ticker)

    if not vector_store:
        return [{"error": f"No vector index found for '{ticker}' — please run ingestion first."}]

    # Step 3: Vector search using secondary query
    try:
        raw_results: List[Tuple[Document, float]] = retrieve(vector_store, query=secondary_query, k=10)
    except Exception as e:
        return [{"error": f"Vector search failed: {str(e)}"}]

    # Step 4: Filter by primary keywords + LLM
    filtered = []
    for doc, score in raw_results:
        meta = doc.metadata or {}
        title = meta.get("title", doc.page_content.strip())
        desc = meta.get("description", "")
        url = meta.get("url", "N/A")
        published = meta.get("published_at", "N/A")

        # 🧠 Hard filter: primary keywords
        if not contains_all_keywords(f"{title} {desc}", primary_keywords):
            print(f"[Filtered: Missing Primary Keywords] {title}")
            continue

        # 🤖 Optional LLM Relevance Check
        llm_relevance = True
        if is_relevant:
            llm_relevance = judge_relevance_cached(title, desc, topic=query)

        # 🔍 Logging
        print(f"\n[Headline Check] Title: {title}")
        print(f"→ Score: {score:.2f} | Primary Match: ✅ | LLM Relevance: {llm_relevance}")
        print(f"→ Description: {desc}")
        print(f"→ URL: {url} | Published At: {published}")

        if not llm_relevance:
            print(f"[Rejected by LLM] {title}")
            continue

        filtered.append({
            "title": title,
            "description": desc or f"Similarity Score: {score:.2f}",
            "url": url,
            "published_at": published,
        })

        if len(filtered) >= max_results:
            break

    return filtered
