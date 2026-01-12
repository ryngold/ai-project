import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

st.set_page_config(page_title="AI Companion", page_icon="🤖", layout="wide")


api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not found. Please set the GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()
@st.cache_data
def load_context():
    """Loads the CSV dataset into a DataFrame."""   
        df = pd.read_csv("knowledge_base.csv")
        return df
    except FileNotFoundError:
        return None

df = load_context()

def get_rag_context(query):
    """Finds relevant info from the CSV dataset."""
    if df is not None:
        # Simple keyword search
        results = df[df.iloc[:, 0].str.contains(query, case=False, na=False)]
        if not results.empty:
            return results.iloc[0, 1] # Return the first matching info
    return "No specific database info available."

# --- 3. PERSONA DEFINITIONS ---
personas = {
    "Emotional Buddy": """
        You are an empathetic, supportive friend. 
        Your goal is to listen, validate feelings, and offer gentle comfort. 
        Always ask follow-up questions to show you care.
        CRITICAL: If the user mentions self-harm, provide immediate helpline resources.
    """,
    "Exam Motivator": """
        You are a high-energy, disciplined academic coach. 
        Focus on productivity, schedules, and 'tough love'. 
        Use the Pomodoro technique and Stoic philosophy to encourage action.
    """,
    "Adolescent Helper": """
        You are a trusted, non-judgmental older sibling figure. 
        Provide safe, factual advice about growing up, puberty, and social dynamics. 
        Be cool but responsible.
    """
}

# --- 4. APP INTERFACE ---
st.sidebar.title("🤖 Life Companion")
page = st.sidebar.radio("Choose Mode:", ["Home", "Emotional Buddy", "Exam Motivator", "Adolescent Helper"])

if page == "Home":
    st.title("Welcome to Your AI Space 🌟")
    st.markdown("""
    This app is designed to help you navigate different challenges in life.
    
    ### Available Modes:
    * **❤️ Emotional Buddy:** A safe space to vent and be heard.
    * **🔥 Exam Motivator:** Get pushed to finish your syllabus.
    * **🌱 Adolescent Helper:** Ask awkward questions without judgment.
    
    **👈 Select a persona from the sidebar to start.**
    """)

else:
    st.title(f"{page}")
    st.caption("Powered by Gemini AI")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input Area
    if user_input := st.chat_input("Type your message..."):
        # 1. Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. Get Context and Prepare Prompt
        context_info = get_rag_context(user_input)
        system_prompt = personas[page]
        
        full_prompt = f"""
        System Instruction: {system_prompt}
        Context from Knowledge Base: {context_info}
        User Message: {user_input}
        """

        # 3. Generate Response
        with st.spinner("Thinking..."):
            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(full_prompt)
                ai_reply = response.text
            except Exception as e:
                ai_reply = f"Error connecting to AI: {str(e)}"

        # 4. Show AI Response
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})