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

# Professional styling to hide clutter and enhance chat bubbles
st.markdown("""
<style>
    /* Import a professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Clean up Streamlit UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Chat bubble styling */
    .stChatMessage[data-testid="stChatMessageAvatarUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAvatarAssistant"] {
        background-color: #e8f4f9;
        border: 1px solid #d1e7dd;
    }
    .stChatMessageContent {
        border-radius: 10px;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURE GROQ CLIENT SETUP
# ---------------------------------------------------------
try:
    # Try getting key from Streamlit Secrets (for hosting)
    groq_api_key = st.secrets["GROQ_API_KEY"]
except FileNotFoundError:
    # Fallback for local testing without secrets.toml
    # REPLACE WITH YOUR KEY FOR LOCAL RUNS ONLY. DON'T COMMIT TO GITHUB.
    groq_api_key = "PASTE_YOUR_GROQ_KEY_HERE_FOR_LOCAL_TESTING"

if groq_api_key == "PASTE_YOUR_GROQ_KEY_HERE_FOR_LOCAL_TESTING" or not groq_api_key:
    st.warning("⚠️ **Groq API Key Missing.** Please set it in Streamlit Secrets for hosting.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------------
# 3. INTERNAL KNOWLEDGE BASE
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study tips", "pomodoro", "acne", "sleep hygiene", "procrastination", "motivation"],
    "advice": [
        "Use the 5-4-3-2-1 Grounding Technique: Acknowledge 5 things you see, 4 you feel, 3 hear, 2 smell, 1 taste.",
        "Break work into chunks. Focus on active recall rather than passive re-reading.",
        "Pomodoro Technique: 25 minutes intense focus, 5 minutes break. Repeat 4 cycles, then take a 20-minute break.",
        "Wash face twice daily with gentle cleanser. Avoid touching your face. Change pillowcases frequently.",
        "Maintain a cool, dark room. No screens 60 mins before bed. Stick to a consistent sleep schedule.",
        "Use the '2-Minute Rule': If a task takes less than 2 minutes, do it immediately to build momentum.",
        "Do not wait for motivation. Action leads to motivation. Start for just 5 minutes."
    ]
}
df = pd.DataFrame(data)

def get_context(query):
    """Retrieves relevant advice from the internal dataset."""
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return None

# ---------------------------------------------------------
# 4. PROFESSIONAL PERSONA DEFINITIONS
# ---------------------------------------------------------
personas = {
    "Emotional Buddy 💙": {
        "role": "You are an empathetic, non-judgmental supportive friend.",
        "instructions": "Listen actively. Validate their feelings first before offering gentle perspectives. Use a warm, comforting tone. If self-harm is mentioned, immediately provide standard international helpline resources."
    },
    "Exam Motivator 🔥": {
        "role": "You are a disciplined, high-performance academic coach.",
        "instructions": "Focus on strategy, time management, and eliminating excuses. Use a direct, stoic, 'tough love' approach to inspire action. Prioritize efficiency."
    },
    "Adolescent Helper 🌱": {
        "role": "You are a wise, trustworthy older sibling figure.",
        "instructions": "Provide safe, factual, and socially aware advice about growing up, puberty, and relationships. Be approachable but responsible. Avoid overly technical jargon."
    }
}

# ---------------------------------------------------------
# 5. SIDEBAR NAVIGATION & FEATURES
# ---------------------------------------------------------
with st.sidebar:
    st.title("🤖 LifeCompanion Pro")
    st.markdown("---")
    selected_mode = st.radio("Select Persona Mode:", list(personas.keys()))
    st.markdown("---")

    # Dynamic Features based on mode
    user_context_extra = ""
    if "Exam" in selected_mode:
        st.subheader("📅 Study Tracker")
        deadline = st.date_input("Next Big Deadline")
        days_left = (deadline - pd.Timestamp.today().date()).days
        if days_left >= 0:
           st.caption(f"🗓️ Time remaining: {days_left} days")
           user_context_extra = f"[CONTEXT: The user has a major deadline in {days_left} days. Use this urgency.]"
        else:
           st.error("Deadline passed!")

    elif "Emotional" in selected_mode:
         st.subheader("🌡️ Vibe Check")
         stress = st.select_slider("Current Stress Level", options=["Low", "Medium", "High", "Overwhelmed"])
         user_context_extra = f"[CONTEXT: User reports their stress level is '{stress}'. Adjust tone accordingly.]"

    st.markdown("---")
    if st.button("🗑️ Clear Conversation History", type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    with st.expander("ℹ️ About this App"):
        st.caption("Powered by Groq (Llama 3 70B). Uses RAG for specific knowledge retrieval. Designed for demo purposes.")


# ---------------------------------------------------------
# 6. MAIN CHAT INTERFACE
# ---------------------------------------------------------
st.subheader(f"{selected_mode}")

# Initialize History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User Input Handler
if prompt := st.chat_input("Type your message here..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Prepare Context & System Prompt
    db_context = get_context(prompt)
    persona_data = personas[selected_mode]
    
    system_prompt = f"""
    ROLE: {persona_data['role']}
    INSTRUCTIONS: {persona_data['instructions']}
    
    RELEVANT KNOWLEDGE BASE INFO: {db_context if db_context else 'None available for this query.'}
    
    ADDITIONAL USER CONTEXT: {user_context_extra}
    """

    # 3. Generate Streaming Response via Groq
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Using Llama 3 70B for high quality
            stream = client.chat.completions.create(
                model="llama3-70b-8192", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=True # Enable streaming
            )
            
            # Process the stream
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final update without cursor
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"API Error: {e}")
            full_response = "Sorry, I encountered an error connecting to the inference engine."

    # 4. Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
