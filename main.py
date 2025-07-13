import streamlit as st


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