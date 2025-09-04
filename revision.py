import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json
import re

# Set up the page
st.set_page_config(
    page_title="AI Revision Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False

# App title and description
st.title("📚 AI Revision Buddy")
st.markdown("""
Welcome to your AI Revision Buddy! I can help you:
- Explain any school topic in simple language
- Generate practice questions to test your knowledge
""")

# Sidebar for API key input and instructions
with st.sidebar:
    st.header("Setup Instructions")
    st.markdown("""
    1. Get a Google AI API key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    2. Enter your API key below
    3. Type a topic you want to learn about
    4. Click 'Explain Topic' or 'Generate Quiz'
    """)
    
    api_key = st.text_input("Enter your Google AI API key:", type="password")
    if api_key:
        google_genai.configure(api_key=api_key)

    st.divider()
    st.markdown("### Examples to try:")
    st.markdown("- Newton's Laws of Motion")
    st.markdown("- Photosynthesis")
    st.markdown("- French Revolution")
    st.markdown("- Quadratic Equations")

# Function to get AI explanation using Gemini
def get_explanation(topic):
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Explain the topic '{topic}' in simple language appropriate for a 13-year-old student.
        Provide a clear, concise explanation with 1-2 examples if relevant.
        Keep it to about 150 words.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error getting explanation: {str(e)}")
        return None

# Function to generate quiz questions using Gemini
def generate_quiz(topic):
    try:
        # Initialize the model
        local_llm = ChatGoogleGenerativeAI(
    model ="gemini-2.0-flash-exp")
        

        prompt = f"""
        Generate a short quiz with 5 questions about '{topic}' for a 13-year-old student.
        For each question, provide:
        1. The question
        2. Four multiple choice options (A, B, C, D)
        3. The correct answer (just the letter)
        
        Format your response as a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "question": "question text",
                    "options": {{
                        "A": "option A",
                        "B": "option B",
                        "C": "option C",
                        "D": "option D"
                    }},
                    "correct_answer": "A"
                }}
            ]
        }}
        """
        
        response = local_llm.generate_content(prompt)
        content = response.text.strip()
        
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            st.error("Could not parse quiz questions from the response.")
            return None
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return None

# Main app interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Learn a New Topic")
    topic = st.text_input("Enter a topic you want to learn about:", 
                         placeholder="e.g., Newton's Laws, Photosynthesis, French Revolution")
    
    if st.button("Explain Topic") and topic:
        with st.spinner("Generating explanation..."):
            explanation = get_explanation(topic)
            if explanation:
                st.session_state.topic = topic
                st.session_state.explanation = explanation
                st.success("Explanation generated!")
    
    if st.session_state.explanation:
        st.subheader(f"Explanation: {st.session_state.topic}")
        st.write(st.session_state.explanation)
        
        if st.button("Generate Quiz Based on This Explanation"):
            with st.spinner("Creating quiz questions..."):
                quiz_data = generate_quiz(st.session_state.topic)
                if quiz_data and 'questions' in quiz_data:
                    st.session_state.questions = quiz_data['questions']
                    st.session_state.quiz_generated = True
                    st.session_state.answers = {}
                    st.session_state.score = 0
                    st.rerun()

with col2:
    if st.session_state.quiz_generated and st.session_state.questions:
        st.header(f"Quiz: {st.session_state.topic}")
        st.info("Answer the questions below. Click 'Submit Answers' when you're done!")
        
        for i, q in enumerate(st.session_state.questions):
            st.subheader(f"Question {i+1}")
            st.write(q['question'])
            
            options = q['options']
            answer_key = f"q_{i}"
            st.session_state.answers[answer_key] = st.radio(
                "Select your answer:",
                options=["A", "B", "C", "D"],
                key=answer_key,
                horizontal=True
            )
            
            st.write("---")
        
        if st.button("Submit Answers"):
            score = 0
            for i, q in enumerate(st.session_state.questions):
                answer_key = f"q_{i}"
                if st.session_state.answers[answer_key] == q['correct_answer']:
                    score += 1
            
            st.session_state.score = score
            st.success(f"You scored {score} out of {len(st.session_state.questions)}!")
            
            # Show correct answers
            st.subheader("Review:")
            for i, q in enumerate(st.session_state.questions):
                answer_key = f"q_{i}"
                user_answer = st.session_state.answers[answer_key]
                is_correct = user_answer == q['correct_answer']
                
                st.write(f"Question {i+1}: Your answer was {user_answer} - {'✅ Correct!' if is_correct else '❌ Incorrect'}")
                if not is_correct:
                    st.write(f"Correct answer is {q['correct_answer']}: {q['options'][q['correct_answer']]}")
            
            if score == len(st.session_state.questions):
                st.balloons()
    else:
        st.header("Practice Quiz")
        st.info("Enter a topic and generate an explanation first. Then you can create a quiz to test your knowledge!")

# Footer
st.divider()
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f1f1f1;
    color: black;
    text-align: center;
    padding: 10px;
}
</style>
<div class="footer">
    <p>Built with ❤️ for students | AI Revision Buddy v1.0 | Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)