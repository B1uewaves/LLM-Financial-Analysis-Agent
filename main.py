from dotenv import load_dotenv
load_dotenv() 

import streamlit as st
from tools.vector_store import load_vector_store

# → Page config
st.set_page_config(
    page_title="LLM Financial Analysis Agent",
    layout="wide",
)

# → Header
st.title("📊 LLM Financial Analysis Agent")
st.markdown(
    """
    Fetch real‑time stock quotes, get LLM‑powered news summaries, and see lightweight ML forecasts — 
    all in one Streamlit app.
    """
)

# Load your RAG index once at startup
vector_store = load_vector_store()
