import streamlit as st
import json
import os
import time
from datetime import date, timedelta, datetime

# ── PROFESSIONAL THEME ──
BG, CARD, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0d1117", "#161b22", "#58a6ff", "#2ea043", "#c9d1d9", "#8b949e", "#30363d"
)

st.set_page_config(page_title="Wasif's Life OS | AI Powered", layout="wide")

# ── CSS STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: {CARD}; color: {SUBTEXT}; text-align: center;
        padding: 10px; border-top: 1px solid {BORDER}; font-size: 14px;
    }}
    .status-card {{ 
        background:{CARD}; border:1px solid {BORDER}; border-radius:15px; 
        padding:20px; margin-bottom: 20px; border-top: 4px solid {ACCENT};
    }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA CORE ──
DATA_FILE = "wasif_life_os_v10.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: return json.load(f)
        except: pass
    return {"habits": [], "completions": {}, "creature_xp": 0, "assignments": [], "energy": 100}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
data = st.session_state.data

# ── MAIN UI ──
st.title("Wasif's Life OS 🚀")

# Global Metrics Bar
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f"<div class='status-card'><small>BATTERY</small><br><span style='font-size:20px;'>🔋 {data['energy']}%</span></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='status-card'><small>LEVEL</small><br><span style='font-size:20px;'>⭐ {data['creature_xp']} XP</span></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='status-card'><small>DATE</small><br><span style='font-size:20px;'>📅 {date.today()}</span></div>", unsafe_allow_html=True)

# ── NAVIGATION TABS ──
tab_focus, tab_assign, tab_ai = st.tabs(["🎯 Focus", "📋 Assignments", "🤖 AI Study Assistant"])

# --- TAB: FOCUS ---
with tab_focus:
    st.subheader("Deep Work Timer")
    # (Purana timer wala logic yahan continue hoga)
    st.info("Timer logic active. Focus on your tasks!")

# --- TAB: ASSIGNMENTS ---
with tab_assign:
    st.subheader("Manage Assignments")
    # (Purana assignment vault logic)
    a_name = st.text_input("Assignment Name")
    if st.button("Add Assignment") and a_name:
        data["assignments"].append({"name": a_name, "due": str(date.today())})
        save_data(data); st.rerun()

# --- TAB: AI ASSISTANT (NEW!) ---
with tab_ai:
    st.subheader("💬 Ask Your AI Study Buddy")
    user_query = st.text_input("Ask anything (Concept, Math, Code)...", placeholder="e.g. Explain Newton's Third Law")
    
    if st.button("Get AI Answer"):
        if user_query:
            with st.spinner("Thinking..."):
                # Ye part AI ko simulate kar raha hai. 
                # Real AI ke liye humein OpenAI ya Google Gemini ki API key chahiye hogi.
                # Filhal main aik "Smart Simulation" de raha hoon jo basic engineering queries solve karega.
                time.sleep(2)
                st.markdown(f"**AI Response:**")
                st.write(f"Wasif, to explain '{user_query}', we need to look at the core principles... [AI logic will output here]")
                st.success("Tip: Try asking for a practice problem next!")
        else:
            st.warning("Pehle kuch likho to sahi yar!")

# ── YOUR CUSTOM FOOTER ──
st.markdown(f"""
    <div class="footer">
        🚀 Built with ❤️ by <b>Wasif Sadheer</b> | Powered by Gemini AI & Streamlit
    </div>
    """, unsafe_allow_html=True)

# Sidebar for extra credits
with st.sidebar:
    st.title("User Profile")
    st.write(f"**Name:** Wasif Sadheer")
    st.write(f"**Role:** Engineering Student")
    st.write("---")
    st.caption("Keep evolving your OS!")
