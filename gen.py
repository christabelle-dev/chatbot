import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="📝",
    layout="wide"
)

# Sidebar for API key and settings
st.sidebar.title("🔐 API Key & Settings")
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
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=api_key,
    temperature=0.3,
    timeout=None,
    max_retries=2,
)

# App title and description
st.title("📝 AI Text Summarizer")
st.markdown("Paste your text below and get an AI-powered summary using Google's Gemini model.")

# Settings in sidebar
st.sidebar.header("Summary Settings")
summary_length = st.sidebar.selectbox(
    "Summary Length:",
    options=["Short", "Medium", "Detailed"],
    index=1
)

# Map summary length to instructions
length_instructions = {
    "Short": "Provide a very concise summary (2-3 sentences).",
    "Medium": "Provide a balanced summary (1 paragraph).",
    "Detailed": "Provide a comprehensive summary (multiple paragraphs)."
}

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Text")
    input_text = st.text_area(
        "Paste your text here:",
        height=400,
        placeholder="Enter the text you want to summarize...",
        help="Paste articles, essays, reports, or any lengthy text."
    )
    
    # Word count
    if input_text:
        word_count = len(input_text.split())
        st.caption(f"Word count: {word_count}")
    
    # Generate button
    generate_btn = st.button(
        "Generate Summary",
        type="primary",
        disabled=not input_text.strip(),
        use_container_width=True
    )

with col2:
    st.subheader("Summary")
    
    if generate_btn and input_text.strip():
        with st.spinner("Generating summary..."):
            try:
                # Create prompt with instructions
                system_message = SystemMessage(content="You are a helpful assistant that creates clear, accurate summaries of text. Follow the user's instructions carefully.")
                human_message = HumanMessage(content=f"""
                Please summarize the following text. {length_instructions[summary_length]}
                
                Text to summarize:
                {input_text}
                """)
                
                # Get response from Gemini
                response = llm.invoke([system_message, human_message])
                summary = response.content
                
                # Display summary
                st.success("Summary generated successfully!")
                st.write(summary)
                
                # Summary word count
                summary_word_count = len(summary.split())
                st.caption(f"Summary word count: {summary_word_count}")
                
                # Copy to clipboard button
                st.button(
                    "Copy Summary to Clipboard",
                    on_click=lambda: st.write("📋 Summary copied to clipboard!"),
                    help="Note: This is a visual indication. Use keyboard shortcuts to actually copy."
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Enter text and click 'Generate Summary' to see the result here.")
        st.write("---")
        st.caption("Example usage:")
        st.caption("- Summarize long articles for quick reading")
        st.caption("- Condense research papers to key findings")
        st.caption("- Create briefs from lengthy reports")

# Footer
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info(
    "This tool uses Google's Gemini AI to generate summaries of text. "
    "Your API key is only used for the current session and is not stored."
)

# Test connection in sidebar
if st.sidebar.button("Test Connection"):
    try:
        test_response = llm.invoke([HumanMessage(content="Hello, are you connected?")])
        st.sidebar.success("✅ Connection successful!")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {str(e)}")