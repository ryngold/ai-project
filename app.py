import streamlit as st
from groq import Groq
import pandas as pd
import datetime
import random

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="MindMate Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. ADVANCED PROFESSIONAL CSS (Glassmorphism)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* GLASSMORPHISM CARDS */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }

    /* CUSTOM CHAT BUBBLES */
    .stChatMessage[data-testid="stChatMessageAvatarUser"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stChatMessage[data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, rgba(46, 49, 146, 0.1) 0%, rgba(27, 255, 255, 0.1) 100%);
        border: 1px solid var(--primary-color);
        border-left: 5px solid var(--primary-color);
    }

    /* GRADIENT HEADER TEXT */
    .gradient-text {
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SECURE SETUP
# ---------------------------------------------------------
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except:
    groq_api_key = "PASTE_KEY_HERE_FOR_LOCAL_ONLY"

if groq_api_key.startswith("PASTE") or not groq_api_key:
    st.error("🚨 API Key Missing. Please set it in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------------
# 4. KNOWLEDGE BASE & UTILS
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study", "acne", "sleep", "procrastination", "motivation", "social"],
    "advice": [
        "🌿 **Grounding:** Name 5 things you see, 4 feel, 3 hear, 2 smell, 1 taste.",
        "🍅 **Pomodoro:** 25m Focus / 5m Break. Repeat 4x.",
        "💧 **Skin:** Wash face 2x daily. Don't touch!",
        "🌙 **Sleep:** No screens 1hr before bed. Cool room.",
        "🚀 **2-Min Rule:** If it takes <2 mins, do it NOW.",
        "🔥 **Momentum:** Action creates motivation. Just start.",
        "🤝 **Boundaries:** It is okay to say no to protect your peace."
    ]
}
df = pd.DataFrame(data)

def get_rag_context(query):
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return None

def convert_chat_to_text(messages):
    """Converts chat history to a downloadable text string."""
    chat_text = "--- MINDMATE PRO CHAT LOG ---\n\n"
    for msg in messages:
        role = "USER" if msg["role"] == "user" else "AI"
        chat_text += f"{role}: {msg['content']}\n\n"
    return chat_text

# ---------------------------------------------------------
# 5. SIDEBAR DASHBOARD
# ---------------------------------------------------------
personas = {
    "Emotional Buddy": {"icon": "💙", "role": "Empathetic Therapist", "tone": "Warm, validating, soothing."},
    "Exam Motivator": {"icon": "🔥", "role": "Strict Coach", "tone": "Direct, urgent, disciplined."},
    "Adolescent Helper": {"icon": "🌱", "role": "Wise Sibling", "tone": "Casual, safe, non-judgmental."}
}

with st.sidebar:
    st.title(f"🧠 MindMate Pro")
    st.caption("Your AI Life Companion")
    st.markdown("---")
    
    # 1. PERSONA SELECTOR
    mode_name = st.selectbox("Choose Persona", list(personas.keys()))
    current_persona = personas[mode_name]
    
    st.markdown("---")

    # 2. DYNAMIC TOOLS
    extra_context = ""
    if "Exam" in mode_name:
        st.subheader("📅 Exam Countdown")
        exam_date = st.date_input("Target Date", datetime.date.today())
        days = (exam_date - datetime.date.today()).days
        if days >= 0:
            st.metric("Days Remaining", f"{days}", delta=f"-1 Day")
            extra_context = f"[URGENT: Exam in {days} days]"
        else:
            st.error("Date passed!")
            
    elif "Emotional" in mode_name:
        st.subheader("🌡️ Vibe Check")
        mood = st.select_slider("Current Mood", ["😞", "😐", "🙂", "🤩"])
        st.write(f"Tracking: **{mood}**")
        extra_context = f"[MOOD: {mood}]"

    st.markdown("---")

    # 3. FEATURE: DAILY WISDOM CARD
    st.subheader("💡 Daily Wisdom")
    if "daily_tip" not in st.session_state:
        st.session_state.daily_tip = random.choice(df['advice'].tolist())
    st.info(st.session_state.daily_tip)

    # 4. DOWNLOAD CHAT
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.markdown("---")
        chat_str = convert_chat_to_text(st.session_state.messages)
        st.download_button(
            label="📥 Download Chat",
            data=chat_str,
            file_name="mindmate_chat.txt",
            mime="text/plain"
        )
    
    # Clear Button
    if st.button("🗑️ Reset All", type="primary"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 6. MAIN INTERFACE
# ---------------------------------------------------------
# Header Area
col1, col2 = st.columns([1, 5])
with col1:
    st.title(current_persona["icon"])
with col2:
    st.markdown(f"<h1 style='padding-top:10px;'>{mode_name}</h1>", unsafe_allow_html=True)
    st.caption(f"Identity: {current_persona['role']} • Powered by Llama 3")

# Initialize History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome Message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"Hello! I'm your **{mode_name}**. How can I support you right now?"
    })

# Render Chat
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input Area
if prompt := st.chat_input("Type here..."):
    # User Msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # RAG & Prompt
    db_advice = get_rag_context(prompt)
    sys_msg = f"""
    ROLE: {current_persona['role']} ({current_persona['tone']})
    USER CONTEXT: {extra_context}
    KNOWLEDGE BASE: {db_advice}
    """

    # AI Response
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Connection error. Please check API Key."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
