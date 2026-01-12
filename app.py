import streamlit as st
import google.generativeai as genai
import pandas as pd
import time

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifeCompanion AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner look
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f1f1f1;
        border-radius: 10px;
        padding: 10px;
    }
    h1 {
        color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API SETUP (Cloud & Local Compatible)
# ---------------------------------------------------------
# This allows the app to work on Streamlit Cloud (using Secrets) 
# OR on your local computer if you replace the text below.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # REPLACE THIS WITH YOUR ACTUAL KEY FOR LOCAL TESTING
    api_key = "PASTE_YOUR_GEMINI_KEY_HERE"

if api_key == "PASTE_YOUR_GEMINI_KEY_HERE":
    st.warning("⚠️ **Setup Required:** Please add your Google API Key in the code (line 39) or Streamlit Secrets.")
    st.stop()
else:
    genai.configure(api_key=api_key)

# ---------------------------------------------------------
# 3. INTERNAL DATASET (The Knowledge Base)
# ---------------------------------------------------------
# We embed the data directly so the app works without needing external CSV files.
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination", "motivation"],
    "advice": [
        "Use the 5-4-3-2-1 Grounding Technique: Acknowledge 5 things you see, 4 you feel, 3 you hear, 2 you smell, and 1 you taste.",
        "Try the Pomodoro Technique: 25 minutes of focus, 5 minutes break. Repeat 4 times.",
        "Wash face twice daily with gentle cleanser. Avoid touching your face. Drink 3L of water daily.",
        "No screens 1 hour before bed. Keep the room cool (around 18°C/65°F).",
        "Use the '2-Minute Rule': If a task takes less than 2 minutes, do it right now.",
        "Motivation follows action. Don't wait to feel like it; start for just 5 minutes and momentum will build."
    ]
}
df = pd.DataFrame(data)

def get_context(query):
    """Checks the internal dataset for matching keywords."""
    for index, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return "No specific database record found."

# ---------------------------------------------------------
# 4. PERSONAS
# ---------------------------------------------------------
personas = {
    "Emotional Buddy": {
        "role": "You are an empathetic friend. Listen actively, validate feelings, and offer comfort.",
        "icon": "💙",
        "intro": "I'm here to listen. No judgment, just support."
    },
    "Exam Motivator": {
        "role": "You are a strict but fair coach. Focus on discipline, schedules, and 'tough love'.",
        "icon": "🔥",
        "intro": "Stop scrolling and start studying. What is your deadline?"
    },
    "Adolescent Helper": {
        "role": "You are a wise older sibling. Give factual, safe advice about growing up and social dynamics.",
        "icon": "🌱",
        "intro": "Growing up is weird. Ask me anything about health, friends, or changes."
    }
}

# ---------------------------------------------------------
# 5. APP INTERFACE
# ---------------------------------------------------------
st.sidebar.header("🤖 Companion Modes")
selected_mode = st.sidebar.radio("Choose Persona:", list(personas.keys()))

st.sidebar.markdown("---")
st.sidebar.info("💡 **Try asking about:**\n- Anxiety\n- Study Tips\n- Sleep")

# Main Content
persona = personas[selected_mode]
st.title(f"{persona['icon']} {selected_mode}")
st.markdown(f"*{persona['intro']}*")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear history if persona changes
if "last_persona" not in st.session_state:
    st.session_state.last_persona = selected_mode
if st.session_state.last_persona != selected_mode:
    st.session_state.messages = []
    st.session_state.last_persona = selected_mode

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if user_input := st.chat_input("Type your message..."):
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get Context & Response
    dataset_info = get_context(user_input)
    
    system_prompt = f"""
    ROLE: {persona['role']}
    KNOWLEDGE BASE: {dataset_info}
    USER MESSAGE: {user_input}
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            with st.spinner("Thinking..."):
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(system_prompt)
                
                # Streaming effect
                for chunk in response.text.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        except Exception as e:
            st.error("Connection Error. Please check your API Key.")
            full_response = "Error connecting to AI."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
