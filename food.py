import streamlit as st
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

if "all_chats" not in st.session_state:
    st.session_state.all_chats = []  # list of all chat sessions
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0  # track active chat
if "messages" not in st.session_state:
    st.session_state.messages = []  # store messages for current chat

def save_current_chat():
    """Save the messages into the correct chat slot."""
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

    category = st.selectbox(
        "Choose a food category:",
        ["Fruits", "Vegetables", "Grains", "Proteins", "Dairy", "Snacks", "Beverages"]
    )

    goal_level = st.slider("Health Goal (1=Basic, 5=Strict/Advanced):", 1, 5, 2)
    st.caption("Example: 1 = General wellness, 5 = Strict diet/fitness goals")

    st.divider()
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

        if st.button(title, key=f"chat_{i}"):
            save_current_chat()
            st.session_state.current_chat_index = i
            st.session_state.messages = chat
            st.rerun()


st.title("🥗 Nutritional and Food Advisor")
st.write("Ask me about foods, nutrition tips, or meal plans😉. Chats anytime!🥰")

topic = st.text_input(f"What would you like to know about {category}?")
task = st.selectbox(
    "What do you want?",
    ["🍎 Nutrition Facts", "🥗 Meal Plan Suggestion", "❓ Quiz on Healthy Eating"]
)


if api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature = 0.8)

# Generate Response
if st.button("Generate") and topic:
    with st.spinner("Thinking..."):
        if task == "🍎 Nutrition Facts":
            prompt = f"Give detailed nutritional facts and health benefits of {topic} in {category}. Goal level: {goal_level}."
        elif task == "🥗 Meal Plan Suggestion":
            prompt = f"Suggest a one-day meal plan using foods from {category}, focusing on {topic}. Goal level: {goal_level}."
        elif task == "❓ Quiz on Healthy Eating":
            prompt = f"Create a short nutrition quiz (3 questions with answers) about {topic} in {category}. Goal level: {goal_level}."

        response = llm.invoke([HumanMessage(content=prompt)])

        # Save conversation
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response.content})

# Show Chat
st.subheader(f"💬 Chat {st.session_state.current_chat_index + 1}")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Advisor:** {msg['content']}")

st.divider()
st.caption("💡 Tip: Use different categories to compare diets and nutrition advice!")
