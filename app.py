import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
# PASTE YOUR API KEY HERE DIRECTLY FOR TESTING (OR USE ENV VARIABLES)
GOOGLE_API_KEY = "AIzaSyDFyUUooNioOTLasBsWAJKX7SouVNubNmE"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="Companion AI", layout="wide")

# ---------------------------------------------------------
# 2. DATA LOADING (THE ML PART)
# ---------------------------------------------------------
@st.cache_data # This keeps the data in memory so it doesn't reload every click
def load_data():
    try:
        # Assuming your CSV has columns like 'Questions' and 'Answers'
        df = pd.read_csv("knowledge_base.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame() # Return empty if no file found

df = load_data()

def retrieve_knowledge(user_query):
    """
    Simple Search: Looks for keywords in the dataset to give the AI context.
    """
    if df.empty:
        return "No specific dataset knowledge available."
    
    # Check if user query matches any keywords in the CSV
    # We take the top result that matches
    results = df[df.iloc[:, 0].str.contains(user_query, case=False, na=False)]
    
    if not results.empty:
        # Return the Answer from the first matching row
        return f"Relevant specific info from database: {results.iloc[0, 1]}"
    return "No specific database match."

# ---------------------------------------------------------
# 3. PERSONA DEFINITIONS
# ---------------------------------------------------------
personas = {
    "Emotional Buddy": "You are an empathetic friend. Prioritize listening and validating feelings. Use a warm, comforting tone.",
    "Exam Motivator": "You are a strict but encouraging coach. Focus on discipline, time management (Pomodoro), and study strategies.",
    "Adolescent Helper": "You are a wise older sibling. Give safe, non-judgmental advice on puberty, social life, and growing up for men and women."
}

# ---------------------------------------------------------
# 4. USER INTERFACE (FRONTEND)
# ---------------------------------------------------------


# Sidebar for Navigation
st.sidebar.title("🤖 AI Companion")
page = st.sidebar.radio("Navigate to:", ["Home", "Emotional Buddy", "Exam Motivator", "Adolescent Helper"])

if page == "Home":
    st.title("Welcome to Your AI Support System")
    st.info("Select a mode from the sidebar to begin.")
    st.markdown("""
    * **Emotional Buddy:** For when you need to vent.
    * **Exam Motivator:** For when you need to study.
    * **Adolescent Helper:** For growing up questions.
    """)

else:
    st.header(f"{page} Mode")
    
    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # Display Chat History
    for role, text in st.session_state.history:
        with st.chat_message(role):
            st.write(text)

    # User Input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # 1. Display User Message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.history.append(("user", user_input))

        # 2. Retrieve Context from Kaggle Data
        context_data = retrieve_knowledge(user_input)

        # 3. Construct the Prompt for Gemini
        system_instruction = personas[page]
        full_prompt = f"""
        System Role: {system_instruction}
        
        Background Knowledge from Dataset: {context_data}
        
        User Question: {user_input}
        """

        # 4. Generate and Display AI Response
        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(full_prompt)
                ai_reply = response.text
            except Exception as e:
                ai_reply = "I'm having trouble connecting to the brain right now."

        with st.chat_message("assistant"):
            st.write(ai_reply)
        st.session_state.history.append(("assistant", ai_reply))