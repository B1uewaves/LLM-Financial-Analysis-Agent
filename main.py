from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid

from tools.vector_store import load_vector_store
from memory import get_memory
from agent import build_agent

from langchain_core.callbacks.manager import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(f"```\n{self.text}\n```")  # nice monospaced block


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
vector_store = load_vector_store(namespace="default")

# --- Set up session-scoped memory ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4()}"

if "memory" not in st.session_state:
    st.session_state.memory = get_memory(session_id=st.session_state.session_id)

if "agent" not in st.session_state:
    st.session_state.agent = build_agent(memory=st.session_state.memory)

agent = st.session_state.agent

# --- UI: user input ---
query = st.text_input("🧠 Ask a financial question:")

if query:
    thinking_box = st.empty()  # creates the live-updating UI box
    stream_handler = StreamHandler(thinking_box)

    # Run agent with the stream handler
    result = st.session_state.agent.run(query, callbacks=[stream_handler])

    st.markdown("### ✅ Final Answer")
    st.success(result)

