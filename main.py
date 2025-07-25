from dotenv import load_dotenv
load_dotenv() 

import streamlit as st
from tools.vector_store import load_vector_store

from agent import build_agent  # 👈 import this function
from memory import get_memory
import uuid

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

# --- Set up session-scoped memory ---
# Create session ID once
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4()}"

# Create memory once
if "memory" not in st.session_state:
    st.session_state.memory = get_memory(session_id=st.session_state.session_id)

# Build agent once
if "agent" not in st.session_state:
    st.session_state.agent = build_agent(memory=st.session_state.memory)

memory = get_memory(session_id=st.session_state.session_id)
# Create agent using the shared logic
agent = build_agent(memory)