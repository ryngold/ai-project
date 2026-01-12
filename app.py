import streamlit as st
import google.generativeai as genai
import pandas as pd
import datetime

# ---------------------------------------------------------
# 1. PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="LifeCompanion AI", page_icon="🧠", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f0f2f6; 
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURE CONNECTION (Hosting & Local)
# ---------------------------------------------------------
try:
    # This works when hosted on Streamlit Cloud
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # This works on your computer. 
    # REPLACE THE TEXT BELOW WITH YOUR ACTUAL KEY
    api_key = "PASTE_YOUR_AIza_KEY_HERE"

if api_key == "PASTE_YOUR_AIza_KEY_HERE":
    st.error("⚠️ API Key Missing! Please paste your key in line 28 of the code.")
    st.stop()

genai.configure(api_key=api_key)

# ---------------------------------------------------------
# 3. KNOWLEDGE BASE
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination"],
    "advice": [
        "Grounding: Name 5 things you see, 4 feel, 3 hear, 2 smell, 1 taste.",
        "Pomodoro: 25 min work, 5 min break. Repeat 4 times.",
        "Hygiene: Wash face 2x daily. Change pillowcases.",
        "Sleep: No screens 1hr before bed. Keep room cool.",
        "2-Minute Rule: If it takes <2 mins, do it now."
    ]
}
df = pd.DataFrame(data)

def get_context(query):
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return "No specific database record."

# ---------------------------------------------------------
# 4. UI & LOGIC
# ---------------------------------------------------------
st.sidebar.title("🤖 Companion AI")
mode = st.sidebar.selectbox("Choose Persona:", ["Emotional Buddy 💙", "Exam Motivator 🔥", "Adolescent Helper 🌱"])

# Extra Features
extra_context = ""
if "Exam" in mode:
    exam_date = st.sidebar.date_input("Exam Date", datetime.date.today())
    days = (exam_date - datetime.date.today()).days
    if days > 0:
        st.sidebar.info(f"{days} days left!")
        extra_context = f"User has an exam in {days} days. Be urgent."

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.title(mode)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Prepare Prompt
    db_info = get_context(prompt)
    sys_prompt = f"You are a helpful AI in {mode} mode."
    
    full_prompt = f"""
    SYSTEM: {sys_prompt}
    CONTEXT: {extra_context}
    DATA: {db_info}
    USER: {prompt}
    """

    # Generate Response
    with st.chat_message("assistant"):
        try:
            # ✅ UPDATED TO A MODEL FROM YOUR LIST
            model = genai.GenerativeModel("gemini-2.0-flash") 
            
            response = model.generate_content(full_prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Connection Error: {e}")

