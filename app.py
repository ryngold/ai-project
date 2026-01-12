import streamlit as st
from groq import Groq
import pandas as pd
import datetime

# ---------------------------------------------------------
# 1. PROFESSIONAL PAGE CONFIG & MODERN CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="MindMate Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Colorful, Professional UI
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Gradient Background for Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E3192 0%, #1BFFFF 100%);
        color: white;
    }
    
    /* Clean Main Chat Area */
    .stApp {
        background-color: #ffffff;
    }

    /* Chat Bubbles */
    .stChatMessage[data-testid="stChatMessageAvatarUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAvatarAssistant"] {
        background-color: #eef2ff;
        border-left: 5px solid #4f46e5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Header Styling */
    h1 {
        color: #4f46e5;
        font-weight: 700;
    }
    h3 {
        color: #333;
    }
    
    /* Button Styling */
    .stButton button {
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURE CLIENT SETUP
# ---------------------------------------------------------
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except:
    # Fallback for local testing (Do not commit actual key to GitHub)
    groq_api_key = "PASTE_KEY_HERE_FOR_LOCAL_ONLY"

if groq_api_key.startswith("PASTE") or not groq_api_key:
    st.error("🚨 **System Halted:** API Key is missing.")
    st.info("Please go to Streamlit Cloud -> Settings -> Secrets and add your GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------------
# 3. KNOWLEDGE BASE (RAG SYSTEM)
# ---------------------------------------------------------
data = {
    "topic": ["anxiety", "study tips", "acne", "sleep", "procrastination", "motivation", "friendship"],
    "advice": [
        "**5-4-3-2-1 Grounding:** Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
        "**Pomodoro Technique:** 25 mins focus, 5 mins break. After 4 cycles, take a long break.",
        "**Skincare:** Wash face twice daily. Change pillowcases often. Don't touch your face!",
        "**Sleep Hygiene:** No blue light 1 hour before bed. Keep room cool (18°C/65°F).",
        "**2-Minute Rule:** If a task takes <2 mins, do it NOW. Momentum builds motivation.",
        "Action leads to motivation, not the other way around. Just start for 5 minutes.",
        "True friends respect boundaries. If you feel drained, it's okay to take space."
    ]
}
df = pd.DataFrame(data)

def get_rag_context(query):
    """Finds best advice from the database."""
    for i, row in df.iterrows():
        if row['topic'] in query.lower():
            return row['advice']
    return None

# ---------------------------------------------------------
# 4. PERSONAS & SIDEBAR FEATURES
# ---------------------------------------------------------
personas = {
    "Emotional Buddy 💙": {
        "role": "You are a warm, empathetic therapist friend.",
        "tone": "Use soothing language. Validate feelings. Never judge.",
        "color": "#e3f2fd"
    },
    "Exam Motivator 🔥": {
        "role": "You are a high-energy, strict performance coach.",
        "tone": "Be direct. Use 'tough love'. Focus on discipline and deadlines.",
        "color": "#fff3e0"
    },
    "Adolescent Helper 🌱": {
        "role": "You are a cool, wise older sibling.",
        "tone": "Be casual but responsible. Use emojis. Avoid being 'cringe'.",
        "color": "#e8f5e9"
    }
}

# SIDEBAR DESIGN
with st.sidebar:
    st.title("🧠 MindMate Pro")
    st.markdown("*Your AI Companion for Life*")
    st.divider()
    
    # 1. Mode Selection
    selected_mode = st.radio("Choose Your Companion:", list(personas.keys()))
    
    # 2. Dynamic Tools
    extra_context = ""
    st.divider()
    
    if "Exam" in selected_mode:
        st.subheader("📅 Exam Countdown")
        exam_date = st.date_input("Next Exam Date", datetime.date.today())
        days_left = (exam_date - datetime.date.today()).days
        if days_left >= 0:
            st.metric("Days Remaining", f"{days_left} Days")
            if days_left < 3:
                st.warning("⚠️ Crunch time! Focus is critical.")
                extra_context = f"[CRITICAL: User has an exam in {days_left} days. BE URGENT.]"
            else:
                extra_context = f"[CONTEXT: Exam is in {days_left} days. Help them plan.]"
    
    elif "Emotional" in selected_mode:
        st.subheader("🌡️ Emotional Check-in")
        mood = st.select_slider("How are you feeling?", options=["😞", "😐", "🙂", "🤩"])
        extra_context = f"[CONTEXT: User mood is {mood}. Adjust empathy accordingly.]"

    # 3. Utility Buttons
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", help="Wipe chat history"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        with st.expander("📚 Topics"):
            st.write(df['topic'].tolist())

# ---------------------------------------------------------
# 5. MAIN CHAT INTERFACE
# ---------------------------------------------------------
current_persona = personas[selected_mode]

# Header
st.title(f"{selected_mode}")
st.caption(f"Powered by Groq Llama 3 • {current_persona['role']}")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcoming starting message
    welcome_msg = f"Hello! I'm your {selected_mode.split()[0]} Buddy. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display Chat
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User Input & Processing
if prompt := st.chat_input("Type your message..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Build the "Brain" (Prompt Engineering)
    db_advice = get_rag_context(prompt)
    
    system_instruction = f"""
    ROLE: {current_persona['role']}
    TONE: {current_persona['tone']}
    
    USER SITUATION: {extra_context}
    
    KNOWLEDGE BASE (Use if relevant): {db_advice if db_advice else "No specific database entry."}
    
    INSTRUCTION: Keep responses concise, helpful, and human-like. 
    """

    # 3. Generate Response (Streaming)
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Using the NEW STABLE MODEL
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Connection Error: {e}")
            full_response = "I'm having trouble connecting right now. Please try again."

    # 4. Save History
    st.session_state.messages.append({"role": "assistant", "content": full_response})
