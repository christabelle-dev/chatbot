import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load .env if available
load_dotenv()

# Sidebar - API key input
st.sidebar.title("🔐 API Key Settings")
api_key = os.getenv("GOOGLE_API_KEY") or st.sidebar.text_input(
    "Enter your Google API Key:", type="password", key="manual_api"
)

if not api_key:
    st.sidebar.warning("🚫 GOOGLE_API_KEY not found.")
    st.sidebar.info("Get one at: https://makersuite.google.com/app/apikey")
    st.stop()

# Set env variable
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=api_key,
    temperature=0.9,
    stream=True,
)

st.title("😂 AI Joke Generator - Advanced Edition")

# --- Session State Initialization ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []  # list of chats (each is list of jokes)
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0
if "jokes" not in st.session_state:
    st.session_state.jokes = []  # current jokes in active session

# --- Save current jokes into history ---
def save_current_chat():
    if st.session_state.jokes:
        if len(st.session_state.all_chats) <= st.session_state.current_chat_index:
            st.session_state.all_chats.append(st.session_state.jokes)
        else:
            st.session_state.all_chats[st.session_state.current_chat_index] = st.session_state.jokes

# --- Sidebar: Manage Joke Sessions ---
with st.sidebar:
    st.header("🗂 Joke History")

    # Start New Session
    if st.button("➕ Start New Session"):
        save_current_chat()
        st.session_state.jokes = []
        st.session_state.current_chat_index = len(st.session_state.all_chats)
        st.rerun()

    # List previous sessions
    for i, chat in enumerate(st.session_state.all_chats):
        # Use first joke as session title, fallback to "Session X"
        title = chat[0]["content"][:15] + "..." if chat else f"Session {i+1}"

        cols = st.columns([4, 1])

        # Open session button
        with cols[0]:
            if st.button(title, key=f"chat_{i}"):
                save_current_chat()
                st.session_state.current_chat_index = i
                st.session_state.jokes = chat
                st.rerun()

        # Delete session button
        with cols[1]:
            if st.button("❌", key=f"delete_{i}"):
                del st.session_state.all_chats[i]
                if i == st.session_state.current_chat_index:
                    st.session_state.jokes = []
                st.session_state.current_chat_index = min(
                    st.session_state.current_chat_index,
                    len(st.session_state.all_chats) - 1
                )
                st.rerun()

    st.divider()

    if st.button("Test Connection"):
        try:
            test_response = llm.invoke([HumanMessage(content="Tell me a short joke")])
            st.success("✅ Connection successful!")
            st.write(f"Sample joke: {test_response.content}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

    if st.button("Check API Key"):
        st.success("✅ Google API Key is set." if api_key else "❌ API Key not set.")

# --- Main Interface ---
topic = st.text_input("🎭 Enter a topic for your joke:", "")

if st.button("🤣 Generate Joke") and topic:
    st.write(f"**Topic:** {topic}")
    full_response = ""
    with st.spinner("Generating joke..."):
        stream = llm.stream([HumanMessage(content=f"Tell me a funny joke about {topic}")])
        for chunk in stream:
            full_response += chunk.content
            st.markdown(full_response + "▌")
        st.markdown(full_response)

    st.session_state.jokes.append({"role": "assistant", "content": full_response})

# --- Display Joke History for Current Session ---
st.subheader("📜 Current Session Jokes")
for joke in st.session_state.jokes:
    with st.chat_message("assistant"):
        st.markdown(joke["content"])
