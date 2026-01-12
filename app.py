import streamlit as st
import google.generativeai as genai
import pandas as pd
import datetime

# ---------------------------------------------------------
# 1. PAGE SETUP & STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="LifeCompanion AI", page_icon="🧠", layout="wide")

# Custom CSS for better chat bubbles
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f0f2f6; 
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURE API CONNECTION (Hosting Friendly)
# ---------------------------------------------------------
# This logic works for BOTH Local (your PC) and Streamlit Cloud
try:
    # Try loading from Streamlit Cloud Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # FALLBACK: If running locally, you can paste your key here temporarily
    # DO NOT commit your key to GitHub if you use this method.
    api_key = "PASTE_YOUR_AIza_KEY_HERE"

if api_key == "PASTE_YOUR_AIza_KEY_HERE":
    st.error("⚠️ API Key Missing. Please set it in Streamlit Secrets or line 36.")
    st.stop()

genai.configure(api_key=api_key)

# ---------------------------------------------------------
# 3. KNOWLEDGE BASE
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination", "motivation"],
    "advice": [
        "Use the 5-4-3-2-1 Grounding Technique to calm down.",
        "Try the Pomodoro Technique: 25 minutes work, 5 minutes break.",
        "Wash your face twice daily and avoid touching it.",
        "Avoid screens 1 hour before bed for better melatonin production.",
        "Use the '2-Minute Rule': If it takes <2 mins, do it now.",
        "Action creates motivation, not the other way around. Just start."
    ]
}
df = pd.DataFrame(data)

def get_context(query):
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return "No specific database record."

# ---------------------------------------------------------
# 4. SIDEBAR & FEATURE LOGIC
# ---------------------------------------------------------
st.sidebar.title("🤖 AI Companion")
mode = st.sidebar.selectbox("Choose Persona:", ["Emotional Buddy 💙", "Exam Motivator 🔥", "Adolescent Helper 🌱"])

# Dynamic Sidebar Features based on Persona
extra_context = ""

if "Exam" in mode:
    st.sidebar.subheader("📅 Exam Planner")
    exam_date = st.sidebar.date_input("When is your exam?", datetime.date.today())
    days_left = (exam_date - datetime.date.today()).days
    
    if days_left < 0:
        st.sidebar.error("Exam date has passed!")
    else:
        st.sidebar.info(f"Time remaining: {days_left} days")
        extra_context = f"IMPORTANT: The user has an exam in {days_left} days. Use this urgency in your response."

elif "Emotional" in mode:
    st.sidebar.subheader("🌡️ Mood Check")
    stress_level = st.sidebar.slider("Stress Level (1-10)", 1, 10, 5)
    extra_context = f"The user's current stress level is {stress_level}/10. Adjust your tone accordingly."

# Clear Chat Button
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# ---------------------------------------------------------
# 5. MAIN CHAT INTERFACE
# ---------------------------------------------------------
st.title(f"{mode}")
st.caption("Powered by Gemini 1.5 Flash")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Type here..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build Prompt (RAG + Features)
    db_info = get_context(prompt)
    
    if "Emotional" in mode:
        sys_prompt = "You are an empathetic friend. Validate feelings deeply."
    elif "Exam" in mode:
        sys_prompt = "You are a strict academic coach. Push for productivity."
    else:
        sys_prompt = "You are a wise older sibling. Give factual advice."

    full_prompt = f"""
    SYSTEM ROLE: {sys_prompt}
    USER CONTEXT: {extra_context}
    DATABASE INFO: {db_info}
    USER MESSAGE: {prompt}
    """

    # 3. AI Response
    with st.chat_message("assistant"):
        try:
            # Using the NEW model name that works
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Connection Error: {e}")
