import streamlit as st
import json
import os
import time
from datetime import date, timedelta

# ── PALETTE (EXACT FROM ORIGINAL) ──
#
BG, CARD, CARD2, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0f1117", "#1a1d27", "#21253a", "#7c6af7", "#56c596", "#e8eaf0", "#7b7f96", "#2a2d3e"
)

st.set_page_config(page_title="Habit Tamagotchi Pro", layout="wide")

# ── PROFESSIONAL STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .main-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; padding:20px; box-shadow: 0 8px 30px rgba(0,0,0,0.4); }}
    .stat-pill {{ background:{CARD2}; border-radius:12px; padding:10px; border:1px solid {BORDER}; text-align:center; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:3px 12px; border-radius:10px; font-weight:bold; font-size:12px; }}
    </style>
    """, unsafe_allow_html=True)

# ── LOGIC & DATA ──
DATA_FILE = "habit_pro_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f: return json.load(f)
    return {"habits": [], "completions": {}, "creature_xp": 0, "focus_time": 0}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

def get_stage(xp):
    #
    if xp >= 100: return "Champion", "🏆"
    if xp >= 60: return "Buddy", "🐶"
    if xp >= 30: return "Sprout", "🌱"
    if xp >= 10: return "Hatchling", "🐣"
    return "Egg", "🥚"

if 'data' not in st.session_state: st.session_state.data = load_data()
data = st.session_state.data
today_str = str(date.today())

# ── SIDEBAR (POWER FEATURES) ──
with st.sidebar:
    st.title("⚡ Power Tools")
    
    # 1. POMODORO TIMER (Powerful Task)
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Minutes", 1, 60, 25)
    if st.button("Start Deep Work"):
        placeholder = st.empty()
        for i in range(minutes * 60, 0, -1):
            placeholder.metric("Time Remaining", f"{i//60:02d}:{i%60:02d}")
            time.sleep(1)
        st.balloons()
        data["creature_xp"] += 5 # Deep work gives more XP!
        save_data(data)
        st.success("Focus Session Complete! +5 XP")

# ── MAIN UI ──
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.title("Habit Tamagotchi Pro")
    st.caption(f"Status: Deep Work Mode Active | {today_str}")

    # 2. MULTITASKING MATRIX (Powerful Task)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    stage_name, emoji = get_stage(data["creature_xp"])
    with c1:
        st.markdown(f"<h1 style='font-size:120px; margin:0;'>{emoji}</h1>", unsafe_allow_html=True)
        st.markdown(f"<span class='badge'>{stage_name}</span>", unsafe_allow_html=True)
    with c2:
        st.write(f"**Total XP:** {data['creature_xp']}")
        st.progress(min(data["creature_xp"] / 100, 1.0))
        st.write("Keep working to evolve your pet! Each habit gives **+2 XP**, Deep Work gives **+5 XP**.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    
    # Habits Interface
    h1, h2 = st.columns([4, 1])
    with h1: new_h = st.text_input("", placeholder="Add a habit (e.g., Coding, Study)...", label_visibility="collapsed")
    with h2: 
        if st.button("Add", use_container_width=True) and new_h:
            data["habits"].append(new_h); save_data(data); st.rerun()

    # 3. HEATMAP / PROGRESS TRACKER (Powerful Task)
    st.subheader("Your Progress")
    completions = data["completions"].get(today_str, [])
    for h in data["habits"]:
        hc1, hc2 = st.columns([5, 1])
        is_done = h in completions
        with hc1:
            if st.checkbox(h, value=is_done, key=h):
                if h not in completions:
                    data["completions"].setdefault(today_str, []).append(h)
                    data["creature_xp"] += 2 #
                save_data(data); st.rerun()
        with hc2:
            if st.button("✕", key=f"del_{h}"):
                data["habits"].remove(h); save_data(data); st.rerun()

with col_stats:
    st.subheader("Analytics")
    st.markdown(f"<div class='stat-pill'>🔥 Streak<br><b>{len(data['completions'])} Days</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-pill'>🏆 All Time XP<br><b>{data['creature_xp']} Points</b></div>", unsafe_allow_html=True)
    
    # Mini Heatmap logic
    st.write("Weekly Activity")
    days = [date.today() - timedelta(days=i) for i in range(7)]
    for d in reversed(days):
        d_str = str(d)
        count = len(data["completions"].get(d_str, []))
        color = ACCENT2 if count > 0 else BORDER
        st.markdown(f"<div style='background:{color}; height:10px; border-radius:5px; margin:2px;'></div>", unsafe_allow_html=True)
