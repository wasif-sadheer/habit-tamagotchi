import streamlit as st
import json
import os
import time
from datetime import date, timedelta

# ── PALETTE (EXACT) ──
BG, CARD, CARD2, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0f1117", "#1a1d27", "#21253a", "#7c6af7", "#56c596", "#e8eaf0", "#7b7f96", "#2a2d3e"
)

st.set_page_config(page_title="Habit Tamagotchi Life OS", layout="wide")

# ── STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .main-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; padding:20px; margin-bottom: 20px; }}
    .stat-pill {{ background:{CARD2}; border-radius:12px; padding:10px; border:1px solid {BORDER}; text-align:center; }}
    .matrix-card {{ background:{CARD2}; border-left: 5px solid {ACCENT}; padding:10px; border-radius:10px; margin-bottom:10px; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:3px 12px; border-radius:10px; font-weight:bold; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA HANDLING ──
DATA_FILE = "habit_pro_v2.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f: return json.load(f)
    return {"habits": [], "completions": {}, "creature_xp": 0, "matrix": []}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
data = st.session_state.data
today_str = str(date.today())

# ── SIDEBAR (TIMER FIX) ──
with st.sidebar:
    st.title("⚡ Study Tools")
    st.subheader("⏱️ Focus Timer")
    focus_mins = st.number_input("Set Minutes", 1, 120, 25)
    
    if st.button("Start Deep Work"):
        st.session_state.timer_running = True
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        for percent in range(100):
            time.sleep((focus_mins * 60) / 100)
            prog_bar.progress(percent + 1)
            status_text.text(f"Focusing... {percent+1}%")
        
        st.success("Session Done! +5 XP")
        data["creature_xp"] += 5
        save_data(data)
        st.session_state.timer_running = False
        st.rerun()

# ── MAIN DASHBOARD ──
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.title("Habit Tamagotchi: Life OS")
    
    # 1. Creature Card
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    # Evolution Stage Logic
    xp = data["creature_xp"]
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    elif xp >= 10: stage, emoji = "Hatchling", "🐣"
    else: stage, emoji = "Egg", "🥚"
    
    with c1:
        st.markdown(f"<h1 style='font-size:100px; text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
        st.markdown(f"<center><span class='badge'>{stage}</span></center>", unsafe_allow_html=True)
    with c2:
        st.write(f"**XP Progression:** {xp}/100")
        st.progress(min(xp/100, 1.0))
        st.info("Tip: Multi-tasking generates bonus XP. Use the Matrix for high-priority tasks.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. PRIORITY MATRIX (The New Power Feature)
    st.subheader("📌 University Priority Matrix")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        new_task = st.text_input("Add High Priority Task (Urgent)")
        if st.button("Push to Matrix") and new_task:
            data["matrix"].append(new_task)
            save_data(data); st.rerun()
    
    with m_col2:
        for t in data["matrix"]:
            st.markdown(f"<div class='matrix-card'>🔥 {t}</div>", unsafe_allow_html=True)
            if st.button("Done", key=t):
                data["matrix"].remove(t)
                data["creature_xp"] += 3
                save_data(data); st.rerun()

    # 3. HABITS
    st.subheader("Daily Habits")
    h_input, h_add = st.columns([3, 1])
    with h_input:
        new_h = st.text_input("New Habit...", label_visibility="collapsed")
    with h_add:
        if st.button("Add Habit", use_container_width=True) and new_h:
            data["habits"].append(new_h); save_data(data); st.rerun()
            
    completions = data["completions"].get(today_str, [])
    for h in data["habits"]:
        hc1, hc2 = st.columns([5, 1])
        with hc1:
            if st.checkbox(h, value=(h in completions), key=f"h_{h}"):
                if h not in completions:
                    data["completions"].setdefault(today_str, []).append(h)
                    data["creature_xp"] += 2
                    save_data(data); st.rerun()
        with hc2:
            if st.button("✕", key=f"del_{h}"):
                data["habits"].remove(h); save_data(data); st.rerun()

with col_stats:
    st.subheader("Analytics")
    st.markdown(f"<div class='stat-pill'>🔥 Daily Streak<br><b>{len(data['completions'])} Days</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-pill'>⭐ Total XP<br><b>{data['creature_xp']}</b></div>", unsafe_allow_html=True)
    
    st.write("---")
    st.write("📅 Weekly Activity")
    # Heatmap logic
    for i in range(7):
        d = date.today() - timedelta(days=i)
        count = len(data["completions"].get(str(d), []))
        color = ACCENT2 if count > 0 else BORDER
        st.markdown(f"<div style='background:{color}; height:12px; border-radius:4px; margin:3px; border:1px solid {BORDER}'></div>", unsafe_allow_html=True)
