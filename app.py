import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="LifeCompanion AI", page_icon="🧠", layout="wide")

# --- 2. SECURE API CONNECTION ---
# This line tries to get the key from Streamlit's secure storage
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    # If the key is missing, show this helpful error on the screen
    st.error("🚨 API Key Missing")
    st.info("To fix this, you need to set up your 'secrets.toml' file (if local) or 'Secrets' in settings (if hosted).")
    st.stop() # Stop the app here so it doesn't crash

# Configure Gemini with the secure key
genai.configure(api_key=api_key)

# --- 3. KNOWLEDGE BASE (DATASET) ---
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination"],
    "advice": [
        "Grounding: Name 5 things you see, 4 you feel, 3 you hear, 2 smell, 1 taste.",
        "Pomodoro: 25 min work, 5 min break. Repeat 4 times.",
        "Hygiene: Wash face 2x daily. Change pillowcases often.",
        "Sleep: No screens 1hr before bed. Keep room cool.",
        "2-Minute Rule: If it takes <2 mins, do it now."
    ]
}
df = pd.DataFrame(data)

def get_rag_response(query):
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return None

# --- 4. PERSONA LOGIC ---
personas = {
    "Emotional Buddy 💙": "You are a supportive, empathetic friend. Validate feelings.",
    "Exam Coach 🔥": "You are a strict academic coach. Focus on discipline and deadlines.",
    "Big Sibling 🌱": "You are a wise older sibling. Give safe, factual advice on growing up."
}

# --- 5. THE UI ---
st.sidebar.title("🤖 AI Companion")
mode = st.sidebar.radio("Select Persona:", list(personas.keys()))

st.title(mode)
st.caption("Secure Streamlit App • Powered by Gemini")

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

    # Logic
    context = get_rag_response(prompt)
    system_instruction = personas[mode]
    final_prompt = f"System: {system_instruction}\nDatabase Info: {context}\nUser: {prompt}"

    # Generate
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(final_prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"API Error: {e}")
