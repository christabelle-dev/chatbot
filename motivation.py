import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Load .env if available ---
load_dotenv()

# --- Sidebar: API key input ---
st.sidebar.title("🔐 API Key Settings")
api_key = os.getenv("GOOGLE_API_KEY") or st.sidebar.text_input(
    "Enter your Google API Key:", type="password", key="manual_api"
)

if not api_key:
    st.sidebar.warning("🚫 GOOGLE_API_KEY not found.")
    st.sidebar.info("Get one at: https://makersuite.google.com/app/apikey")
    st.stop()

os.environ["GOOGLE_API_KEY"] = api_key

# --- Initialize Gemini ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=api_key,
    temperature=0.9,
    stream=True,
)

st.title("✨ AI Motivational Quote Generator - Multi-Session Edition")

# --- Session State Initialization ---
if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = []  # list of sessions, each session is list of quotes
if "current_session_index" not in st.session_state:
    st.session_state.current_session_index = 0
if "quotes" not in st.session_state:
    st.session_state.quotes = []  # current active session quotes

# --- Save current session ---
def save_current_session():
    if st.session_state.quotes:
        if len(st.session_state.all_sessions) <= st.session_state.current_session_index:
            st.session_state.all_sessions.append(st.session_state.quotes)
        else:
            st.session_state.all_sessions[st.session_state.current_session_index] = st.session_state.quotes

# --- Sidebar: Manage Sessions ---
with st.sidebar:
    st.header("🗂 Quote Sessions")

    # Start New Session
    if st.button("➕ Start New Session"):
        save_current_session()
        st.session_state.quotes = []
        st.session_state.current_session_index = len(st.session_state.all_sessions)
        st.rerun()

    # List previous sessions
    for i, session in enumerate(st.session_state.all_sessions):
        title = session[0]["content"][:15] + "..." if session else f"Session {i+1}"
        cols = st.columns([4, 1])
        with cols[0]:
            if st.button(title, key=f"session_{i}"):
                save_current_session()
                st.session_state.current_session_index = i
                st.session_state.quotes = session
                st.rerun()
        with cols[1]:
            if st.button("❌", key=f"del_session_{i}"):
                del st.session_state.all_sessions[i]
                if i == st.session_state.current_session_index:
                    st.session_state.quotes = []
                st.session_state.current_session_index = min(
                    st.session_state.current_session_index,
                    len(st.session_state.all_sessions) - 1
                )
                st.rerun()

    st.divider()
    if st.button("Test Connection"):
        try:
            test_response = llm.invoke([HumanMessage(content="Give me a short motivational quote about optimism")])
            st.success("✅ Connection successful!")
            st.write(f"Sample quote: {test_response.content}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

    if st.button("Check API Key"):
        st.success("✅ Google API Key is set." if api_key else "❌ API Key not set.")

# --- Main Interface ---
st.subheader("🎯 Choose a theme")
themes = ["Success", "Perseverance", "Happiness", "Fitness", "Study", "Courage", "Gratitude", "Mindfulness"]
col1, col2 = st.columns([2, 3])
with col1:
    theme = st.selectbox("Pick a theme:", themes)
with col2:
    custom_theme = st.text_input("Or type a custom theme (optional)")

active_theme = custom_theme.strip() if custom_theme.strip() else theme

gen_cols = st.columns([2, 2, 2])
with gen_cols[0]:
    gen_clicked = st.button("🌟 Generate Quote")
with gen_cols[1]:
    gen_again_clicked = st.button("🔁 Generate Another Quote")
with gen_cols[2]:
    clear_session_clicked = st.button("🗑️ Clear Current Session")

# Clear current session
if clear_session_clicked:
    st.session_state.quotes = []
    st.success("Cleared current session quotes.")

# --- Generate Quote Function ---
def generate_quote(theme_text: str) -> str:
    full = ""
    prompt = (
        f"You are a motivational quotes generator. "
        f"Create a concise, inspiring quote about: {theme_text}. "
        f"1–50 sentences max, positive, practical, original."
    )
    with st.spinner("Generating quote..."):
        stream = llm.stream([HumanMessage(content=prompt)])
        placeholder = st.empty()
        for chunk in stream:
            full += chunk.content
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)
    return full.strip()

# Handle generation
if (gen_clicked or gen_again_clicked) and active_theme:
    quote_text = generate_quote(active_theme)
    if quote_text:
        st.session_state.quotes.append({"theme": active_theme, "content": quote_text})
elif (gen_clicked or gen_again_clicked) and not active_theme:
    st.warning("Please choose or enter a theme first.")

st.divider()

# --- Display Current Session Quotes ---
st.subheader("📜 Current Session Quotes")
if not st.session_state.quotes:
    st.info("No quotes in this session yet. Generate one!")
else:
    for i, q in enumerate(reversed(st.session_state.quotes)):
        idx = len(st.session_state.quotes) - 1 - i
        with st.container(border=True):
            top = st.columns([6, 1])
            with top[0]:
                st.markdown(f"**Theme:** {q['theme']}")
            with top[1]:
                if st.button("❌ Delete", key=f"del_quote_{idx}"):
                    del st.session_state.quotes[idx]
                    st.rerun()
            st.write(q["content"])
