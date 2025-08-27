import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ChatMessage, HumanMessage

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for chat history
with st.sidebar:
    st.title("Chat History")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    # Display chat history
    st.subheader("Previous Conversations")
    for i, message in enumerate(st.session_state.chat_history):
        if st.button(f"Conversation {i+1}", key=f"conv_{i}"):
            st.session_state.messages = message
            st.rerun()

# Main chat interface
st.title("💬 Gemini Chatbot")
st.caption("Powered by Google Gemini 2.0 Flash")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get API key and initialize LLM
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("Please set the GOOGLE_API_KEY environment variable")
        st.stop()
    
    try:
        local_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.7,
            timeout=None,
            max_retries=2
        )

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert chat history to LangChain format
                chat_history = []
                for msg in st.session_state.messages[:-1]:  # Exclude the latest user message
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    else:
                        chat_history.append(ChatMessage(role="assistant", content=msg["content"]))
                
                # Get response from LLM
                response = local_llm.invoke(chat_history + [HumanMessage(content=prompt)])
                
                # Display response
                st.markdown(response.content)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error. Please try again."})

# Save current conversation to history
if len(st.session_state.messages) > 0 and st.sidebar.button("Save Conversation"):
    st.session_state.chat_history.append(st.session_state.messages.copy())
    st.sidebar.success("Conversation saved!")
