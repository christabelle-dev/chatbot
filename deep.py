import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

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
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.3,
        timeout=30,
        max_retries=2,
    )
except Exception as e:
    st.error(f"Error initializing Gemini: {str(e)}")
    st.stop()

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
        help="Paste articles, essays, reports, or any lengthy text.",
        key="input_text"
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
        use_container_width=True,
        key="generate_btn"
    )

with col2:
    st.subheader("Summary")
    
    if generate_btn and input_text.strip():
        with st.spinner("Generating summary..."):
            try:
                # Create a clear prompt for summarization
                prompt = f"""
                Please summarize the following text. {length_instructions[summary_length]}
                
                Text to summarize:
                "{input_text}"
                
                Summary:
                """
                
                # Get response from Gemini
                response = llm.invoke([HumanMessage(content=prompt)])
                summary = response.content
                
                # Display summary
                st.success("Summary generated successfully!")
                st.write(summary)
                
                # Summary word count
                summary_word_count = len(summary.split())
                st.caption(f"Summary word count: {summary_word_count}")
                
                # Add a divider and copy instructions
                st.divider()
                st.info("💡 Select the text and use Ctrl+C (Cmd+C on Mac) to copy the summary.")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("This might be due to API limitations or content restrictions. Try with a shorter text or different content.")
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
        test_response = llm.invoke([HumanMessage(content="Hello, are you connected? Respond with 'Yes, I am connected!'")])
        st.sidebar.success("✅ Connection successful!")
        st.sidebar.write(f"Response: {test_response.content}")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {str(e)}")

# Add some sample text for testing
if st.sidebar.button("Load Sample Text"):
    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. Leading AI textbooks define the field as the study of "intelligent agents": any system that perceives its environment and takes actions that maximize its chance of achieving its goals. AI applications include advanced web search engines (e.g., Google), recommendation systems (used by YouTube, Amazon and Netflix), understanding human speech (such as Siri and Alexa), self-driving cars (e.g., Tesla), automated decision-making and competing at the highest level in strategic game systems (such as chess and Go). 
    
    Artificial intelligence was founded as an academic discipline in 1956. The field went through multiple cycles of optimism followed by disappointment and loss of funding. After 2012, deep learning surpassed all previous AI techniques, leading to a vast increase in funding and interest. The various sub-fields of AI research are centered around particular goals and the use of particular tools. The traditional goals of AI research include reasoning, knowledge representation, planning, learning, natural language processing, perception, and the ability to move and manipulate objects. 
    
    Artificial intelligence has the potential to bring about numerous positive changes in society, including enhanced productivity, better healthcare, and improved access to education. However, AI also raises concerns about job displacement, algorithmic bias, and the potential for misuse. Many countries are developing strategies to promote the development of AI while addressing these ethical concerns.
    """
    st.session_state.input_text = sample_text
    st.rerun()