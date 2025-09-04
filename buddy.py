import streamlit as st
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

st.set_page_config(
    page_title="AI Revision Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


if "all_chats" not in st.session_state:
    st.session_state.all_chats = []  
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []  


def save_current_chat():
    if st.session_state.messages:
        if len(st.session_state.all_chats) <= st.session_state.current_chat_index:
            st.session_state.all_chats.append(st.session_state.messages)
        else:
            st.session_state.all_chats[st.session_state.current_chat_index] = st.session_state.messages


with st.sidebar:
    st.header("⚙️ Settings")

    # API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ API key not found.")
    else:
        st.success("✅ API key loaded.")

    subject = st.selectbox(
        "Choose a subject:",
        ["Mathematics", "Chemistry", "Literature", "Agriculture", "Commerce", "English", "Biology", "Physics", "French"]
    )

    difficulty = st.slider("Difficulty level:", 1, 5, 2)
    st.caption("1 = Very easy, 5 = Advanced")

    st.divider()
    st.header("History")

    # Start New Chat
    if st.button("💥Your Chats"):
        save_current_chat()
        st.session_state.messages = []
        st.session_state.current_chat_index = len(st.session_state.all_chats)
        st.rerun()

    # List all previous chats
    for i, chat in enumerate(st.session_state.all_chats):
        # Show first message as title, fallback to "Chat X"
        title = chat[0]["content"][:15] + "..." if chat else f"Chat {i+1}"

        if st.button(title, key=f"chat_{i}"):
            save_current_chat()
            st.session_state.current_chat_index = i
            st.session_state.messages = chat
            st.rerun()

st.title("📘 AI Revision Buddy")
st.write("Pick a **subject** and type a topic. Save your chats, revisit them anytime!")

topic = st.text_input(f"Enter your {subject} topic:")
task = st.selectbox("What do you want?", ["📖 Simple Explanation", "📝 Sample Exam Questions", "🎯 Mini Quiz"])


if api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 google_api_key=api_key,
                                 temperature=0.8,
                                 max_tokens=None,
                                 max_retries=2
)

if st.button("Generate") and topic:
    with st.spinner("Thinking..."):
        if task == "📖 Simple Explanation":
            prompt = f"Explain '{topic}' in {subject} using simple language. Difficulty level: {difficulty}."
        elif task == "📝 Sample Exam Questions":
            prompt = f"Create 10 exam-style questions with answers on '{topic}' in {subject}. Difficulty level: {difficulty}."
        elif task == "🎯 Mini Quiz":
            prompt = f"Make a short quiz (5 multiple-choice questions with options + answers) on '{topic}' in {subject}. Difficulty level: {difficulty}."

        response = llm.invoke([HumanMessage(content=prompt)])

        # Save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response.content})

st.subheader(f"💬 Chat {st.session_state.current_chat_index + 1}")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Buddy:** {msg['content']}")

st.divider()
st.caption("💡 Tip: Save each topic as a chat to quickly compare explanations and quizzes later.")

