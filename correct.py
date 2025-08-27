import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from PyPDF2 import PdfReader
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tempfile import NamedTemporaryFile

# Load environment variables
load_dotenv()

# Sidebar - API key input
st.sidebar.title("API Key Settings 🔐")
api_key = os.getenv("GOOGLE_API_KEY") or st.sidebar.text_input(
    "Enter your Google API Key:", type="password", key="manual_api"
)

if not api_key:
    st.sidebar.warning("🚫 GOOGLE_API_KEY not found.")
    st.sidebar.info("Get one at: https://makersuite.google.com/app/apikey")
    st.write("🔄 Waiting for API key... Enter it in the sidebar to continue.")
    st.stop()

# Set environment variable
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize Gemini
local_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    stream=True,
)

st.title("🤖 AI Document Chatbot - Powered by Gemini")

# Session State Initialization
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []  
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}

# File processing functions
def process_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def process_other_files(file):
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
        temp_file.write(file.getbuffer())
        loader = UnstructuredFileLoader(temp_file.name)
        docs = loader.load()
    os.unlink(temp_file.name)
    return docs[0].page_content

def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return text_splitter.split_text(text)

# File uploader
uploaded_file = st.file_uploader(
    "📂 Upload PDF, Word, or Text file",
    type=["pdf", "txt", "docx"],
    key=f"file_uploader_{st.session_state.current_chat_index}"
)

if uploaded_file:
    if uploaded_file.name not in st.session_state.uploaded_docs:
        with st.spinner(f"Reading {uploaded_file.name}..."):
            if uploaded_file.type == "application/pdf":
                text = process_pdf(uploaded_file)
            else:
                text = process_other_files(uploaded_file)
            
            chunks = chunk_text(text)
            st.session_state.uploaded_docs[uploaded_file.name] = {
                "text": text,
                "chunks": chunks
            }
        st.success(f"📄 Loaded {uploaded_file.name} ({len(text)} characters)")

# Document management in sidebar
with st.sidebar:
    st.header("Chat History")
    
    if st.button("Start New Chat"):
        # Save current chat first
        if st.session_state.messages or st.session_state.uploaded_docs:
            chat_data = {
                "messages": st.session_state.messages.copy(),
                "docs": st.session_state.uploaded_docs.copy()
            }
            
            if st.session_state.current_chat_index < len(st.session_state.all_chats):
                st.session_state.all_chats[st.session_state.current_chat_index] = chat_data
            else:
                st.session_state.all_chats.append(chat_data)
        
        # Start fresh chat
        st.session_state.messages = []
        st.session_state.uploaded_docs = {}
        st.session_state.current_chat_index = len(st.session_state.all_chats)
        st.rerun()

    for i, chat in enumerate(st.session_state.all_chats):
        title = chat["messages"][0]["content"][:30] + "..." if chat["messages"] else f"Chat {i+1}"
        if st.button(title, key=f"chat_{i}"):
            # Save current chat first
            if st.session_state.messages or st.session_state.uploaded_docs:
                current_chat = {
                    "messages": st.session_state.messages.copy(),
                    "docs": st.session_state.uploaded_docs.copy()
                }
                if st.session_state.current_chat_index < len(st.session_state.all_chats):
                    st.session_state.all_chats[st.session_state.current_chat_index] = current_chat
                else:
                    st.session_state.all_chats.append(current_chat)
            
            # Load selected chat
            st.session_state.current_chat_index = i
            st.session_state.messages = st.session_state.all_chats[i]["messages"].copy()
            st.session_state.uploaded_docs = st.session_state.all_chats[i]["docs"].copy()
            st.rerun()

    st.divider()
    st.header("Loaded Documents")
    
    for doc_name in st.session_state.uploaded_docs:
        if st.button(f"❌ {doc_name}", key=f"remove_{doc_name}"):
            del st.session_state.uploaded_docs[doc_name]
            st.rerun()

    if st.button("🧹 Clear All Documents"):
        st.session_state.uploaded_docs = {}
        st.rerun()

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input + document-aware responses
if prompt := st.chat_input("Ask about the documents..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare context from documents
    context = ""
    if st.session_state.uploaded_docs:
        context = "DOCUMENT CONTEXT:\n"
        for doc_name, doc_data in st.session_state.uploaded_docs.items():
            context += f"\nFrom {doc_name}:\n{doc_data['text'][:5000]}\n"  # First 5000 chars per doc

    # Generate response
    full_response = ""
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            messages = [
                HumanMessage(content=f"{context}\n\nUSER QUESTION: {prompt}")
            ]
            stream = local_llm.stream(messages)
            for chunk in stream:
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ Error: {str(e)}"
            response_placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})