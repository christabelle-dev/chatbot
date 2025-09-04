import streamlit as st
from dotenv import load_dotenv
import os

# ---- LLM ----
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# ---- Session State Setup ----
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  # {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"
if "messages" not in st.session_state:
    st.session_state.messages = []  # stores current conversation

# ---- Sidebar ----
st.sidebar.title("⚙️ Settings")

# API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.sidebar.error("❌ API key not found. Add it to your .env file.")
else:
    st.sidebar.success("✅ API key loaded.")

# Subject Selector
subject = st.sidebar.selectbox(
    "Choose a subject:",
    ["Mathematics", "Chemistry", "Literature", "Agriculture", "Commerce", "English", "Biology", "Physics"]
)

# Difficulty Slider
difficulty = st.sidebar.slider("Difficulty level:", 1, 5, 2)
st.sidebar.caption("1 = Very easy, 5 = Advanced")

st.sidebar.divider()

# ---- Chat Management ----
st.sidebar.subheader("💬 Chat History")

# Save current chat
chat_name = st.sidebar.text_input("Save current chat as:", value=st.session_state.current_chat)
if st.sidebar.button("💾 Save Chat"):
    if chat_name.strip():
        st.session_state.all_chats[chat_name] = st.session_state.messages.copy()
        st.session_state.current_chat = chat_name
        st.sidebar.success(f"Chat saved as '{chat_name}'")

# Load previous chat
if st.session_state.all_chats:
    selected_chat = st.sidebar.selectbox("Load a previous chat:", list(st.session_state.all_chats.keys()))
    if st.sidebar.button("📂 Load Chat"):
        st.session_state.current_chat = selected_chat
        st.session_state.messages = st.session_state.all_chats[selected_chat].copy()
        st.sidebar.info(f"Loaded chat: {selected_chat}")

# ---- App Title ----
st.title("📘 AI Revision Buddy")
st.write("Pick a **subject** and type a topic. Save your chats, revisit them anytime!")

# ---- User Input ----
topic = st.text_input(f"Enter your {subject} topic:")
task = st.selectbox("What do you want?", ["📖 Simple Explanation", "📝 Sample Exam Questions", "🎯 Mini Quiz"])

# ---- LLM Setup ----
if api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# ---- Chat Interaction ----
if st.button("Generate") and topic:
    with st.spinner("Thinking..."):
        if task == "📖 Simple Explanation":
            prompt = f"Explain '{topic}' in {subject} using simple language. Difficulty level: {difficulty}."
        elif task == "📝 Sample Exam Questions":
            prompt = f"Create 5 exam-style questions with answers on '{topic}' in {subject}. Difficulty level: {difficulty}."
        elif task == "🎯 Mini Quiz":
            prompt = f"Make a short quiz (3 multiple-choice questions with options + answers) on '{topic}' in {subject}. Difficulty level: {difficulty}."

        response = llm.invoke([HumanMessage(content=prompt)])

        # Save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response.content})

# ---- Display Chat ----
st.subheader(f"💬 Chat: {st.session_state.current_chat}")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Buddy:** {msg['content']}")

# ---- Footer ----
st.divider()
st.caption("💡 Tip: Save each topic as a chat to quickly compare explanations and quizzes later.")
