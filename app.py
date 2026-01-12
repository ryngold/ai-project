import streamlit as st
from groq import Groq
import pandas as pd
import time

# ---------------------------------------------------------
# 1. PROFESSIONAL PAGE CONFIG & CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifeCompanion Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Professional Font & Clean UI */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stChatMessage[data-testid="stChatMessageAvatarUser"] { background-color: #f0f2f6; }
    .stChatMessage[data-testid="stChatMessageAvatarAssistant"] { background-color: #e8f4f9; border: 1px solid #d1e7dd; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURE GROQ CLIENT SETUP
# ---------------------------------------------------------
try:
    # This looks for the key in Streamlit Secrets (Hosted)
    groq_api_key = st.secrets["GROQ_API_KEY"]
except:
    # This acts as a fallback or allows you to paste the key locally if secrets fail
    # REPLACE THE TEXT BELOW WITH YOUR KEY IF RUNNING LOCALLY
    groq_api_key = "PASTE_YOUR_GROQ_KEY_HERE_ONLY_FOR_LOCAL_TESTING"

if groq_api_key.startswith("PASTE") or not groq_api_key:
    st.error("🚨 API Key Not Found!")
    st.info("1. On Streamlit Cloud: Go to 'Manage App' -> 'Settings' -> 'Secrets' and paste your key.")
    st.info("2. Locally: Create a .streamlit/secrets.toml file.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------------
# 3. KNOWLEDGE BASE
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination"],
    "advice": [
        "Use the 5-4-3-2-1 Grounding Technique: Acknowledge 5 things you see, 4 feel, 3 hear, 2 smell, 1 taste.",
        "Pomodoro Technique: 25 minutes intense focus, 5 minutes break. Repeat 4 cycles.",
        "Wash face twice daily with gentle cleanser. Avoid touching your face.",
        "No screens 60 mins before bed. Keep room cool.",
        "Use the '2-Minute Rule': If a task takes less than 2 minutes, do it immediately."
    ]
}
df = pd.DataFrame(data)

def get_context(query):
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return None

# ---------------------------------------------------------
# 4. PERSONA LOGIC
# ---------------------------------------------------------
personas = {
    "Emotional Buddy 💙": "You are an empathetic friend. Listen actively and validate feelings.",
    "Exam Motivator 🔥": "You are a disciplined academic coach. Use 'tough love' and focus on strategy.",
    "Adolescent Helper 🌱": "You are a wise older sibling. Provide safe, factual advice on growing up."
}

# ---------------------------------------------------------
# 5. UI & CHAT
# ---------------------------------------------------------
with st.sidebar:
    st.title("🤖 LifeCompanion Pro")
    mode = st.radio("Select Persona:", list(personas.keys()))
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.subheader(f"{mode}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare Context
    db_context = get_context(prompt)
    sys_prompt = personas[mode]
    full_prompt = f"SYSTEM: {sys_prompt}\nDATA: {db_context}\nUSER: {prompt}"

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # ✅ UPDATED MODEL NAME: The old 70b-8192 is dead. We use the new 3.3 Versatile.
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_completion_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Groq API Error: {e}")
            full_response = "Error connecting to AI."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
