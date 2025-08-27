import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
import os
from langchain_core.messages import HumanMessage

load_dotenv()

st.sidebar.title("Api Key Setting")
api_key = os.getenv("GOOGLE_API_KEY") or st.sidebar.text_input(
    "Enter your Google Api Key:", type="password", key="manual_api"
)

if not api_key: 
    st.sidebar.warning("GOOGLE_API_KEY not found.")
    st.sidebar.info("Get one at: https://makersuite.google.com/app/apikey")
    st.sidebar.write("Waiting for API key... Enter it in the sidebar to continue.")
    st.stop()
    
os.environ["GOOGLE_API_KEY"] = api_key
    
local_llm = ChatGoogleGenerativeAI(
    model ="gemini-2.0-flash-exp",
    google_api_key=api_key,
    temperature=0.7,
    max_tokens=None,
    timeout=20,
    max_retries=2,
    stream=True,
)

st.title("🤖 AI Support Chatbot - Powered by Gemini")

if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chatt_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []


def save_current_chat():
    if st.session_state.messages:
        if len(st.session_state.all_chats) <=st.session_state.current_chat_index:
         st.session_state.all_chats.append(st.session_state.messages)
        else:
            st.session_state.all_chats[st.session_state.current_chat_index] = st.session_state.messages

with st.sidebar:
    st.header("🗂 Chat History")

    # Start New Chat
    if st.button("➕ Start New Chat"):
        save_current_chat()
        st.session_state.messages = []
        st.session_state.current_chat_index = len(st.session_state.all_chats)
        st.rerun()

    # List all previous chats
    for i, chat in enumerate(st.session_state.all_chats):
        # Show first message as title, fallback to "Chat X"
        title = chat[0]["content"][:15] + "..." if chat else f"Chat {i+1}"

        # 👇 define cols INSIDE the loop
        cols = st.columns([4, 1])  

        # Open chat button
        with cols[0]:
            if st.button(title, key=f"chat_{i}"):
                save_current_chat()
                st.session_state.current_chat_index = i
                st.session_state.messages = chat
                st.rerun()

        # Delete chat button
        with cols[1]:
            if st.button("❌", key=f"delete_{i}"):
                del st.session_state.all_chats[i]

                # If you delete the active chat → reset to empty
                if i == st.session_state.current_chat_index:
                    st.session_state.messages = []

                # Adjust current_chat_index so it doesn't break
                st.session_state.current_chat_index = min(
                    st.session_state.current_chat_index,
                    len(st.session_state.all_chats) - 1
                )
                st.rerun()
