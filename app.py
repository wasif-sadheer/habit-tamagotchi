import streamlit as st
import json
import os
import time
from datetime import date, timedelta

# ── PALETTE ──
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
DATA_FILE = "habit_pro_v3.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f: return json.load(f)
    return {"habits": [], "completions": {}, "creature_xp": 0, "matrix": []}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
data = st.session_state.data
today_str = str(date.today())

# ── MAIN DASHBOARD ──
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.title("Habit Tamagotchi: Life OS")
    
    # --- POWER TASK 1: LIVE FOCUS TIMER (Moved to Main for Stability) ---
    with st.expander("⏱️ DEEP WORK TIMER (Live Countdown)", expanded=False):
        t_col1, t_col2 = st.columns([1, 2])
        with t_col1:
            mins = st.number_input("Minutes", 1, 120, 25)
            start_btn = st.button("Start Focus Session")
        with t_col2:
            timer_display = st.empty()
            prog_display = st.empty()
            
            if start_btn:
                total_seconds = mins * 60
                for remaining in range(total_seconds, -1, -1):
                    m, s = divmod(remaining, 60)
                    timer_display.markdown(f"## ⏳ {m:02d}:{s:02d}")
                    prog_display.progress(1.0 - (remaining / total_seconds))
                    time.sleep(1)
                
                st.balloons()
                data["creature_xp"] += 5
                save_data(data)
                st.success("Focus Session Done! +5 XP")
                time.sleep(2)
                st.rerun()

    # --- Creature Card ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
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
        st.write("Complete habits or focus sessions to evolve.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- POWER TASK 2: PRIORITY MATRIX ---
    st.subheader("📌 High-Priority Matrix")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        new_task = st.text_input("New Urgent Task...")
        if st.button("Push to Matrix") and new_task:
            data["matrix"].append(new_task)
            save_data(data); st.rerun()
    with m_col2:
        for t in data["matrix"]:
            st.markdown(f"<div class='matrix-card'>🔥 {t}</div>", unsafe_allow_html=True)
            if st.button("Done", key=f"mat_{t}"):
                data["matrix"].remove(t)
                data["creature_xp"] += 3
                save_data(data); st.rerun()

    # --- POWER TASK 3: DAILY HABITS ---
    st.subheader("Daily Habits")
    h_input, h_add = st.columns([3, 1])
    with h_input:
        new_h = st.text_input("New Habit...", label_visibility="collapsed", key="new_habit_input")
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
            elif h in completions:
                data["completions"][today_str].remove(h)
                data["creature_xp"] = max(0, data["creature_xp"] - 2)
                save_data(data); st.rerun()
        with hc2:
            if st.button("✕", key=f"del_{h}"):
                data["habits"].remove(h); save_data(data); st.rerun()

with col_stats:
    st.subheader("Analytics")
    st.markdown(f"<div class='stat-pill'>🔥 Streak<br><b>{len(data['completions'])} Days</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-pill'>⭐ Total XP<br><b>{data['creature_xp']}</b></div>", unsafe_allow_html=True)
    st.write("---")
    st.write("📅 Weekly Activity")
    for i in range(7):
        d = date.today() - timedelta(days=i)
        count = len(data["completions"].get(str(d), []))
        color = ACCENT2 if count > 0 else BORDER
        st.markdown(f"<div style='background:{color}; height:12px; border-radius:4px; margin:3px; border:1px solid {BORDER}'></div>", unsafe_allow_html=True)
