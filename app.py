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
    .main-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; padding:25px; margin-bottom: 20px; text-align: center; }}
    .stat-pill {{ background:{CARD2}; border-radius:12px; padding:15px; border:1px solid {BORDER}; text-align:center; }}
    .matrix-card {{ background:{CARD2}; border-left: 5px solid {ACCENT}; padding:10px; border-radius:10px; margin-bottom:10px; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:5px 15px; border-radius:12px; font-weight:bold; }}
    .timer-text {{ font-size: 50px; font-weight: bold; color: {ACCENT2}; font-family: monospace; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA HANDLING ──
DATA_FILE = "habit_pro_v4.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: return json.load(f)
        except: pass
    return {"habits": [], "completions": {}, "creature_xp": 0, "matrix": []}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'timer_active' not in st.session_state: st.session_state.timer_active = False

data = st.session_state.data
today_str = str(date.today())

# ── MAIN DASHBOARD ──
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.title("Habit Tamagotchi: Life OS 🚀")
    
    # --- POWER TASK 1: PRO TIMER (HOURS & MINS) + ACTIVITY SELECTION ---
    with st.expander("🕒 PRO FOCUS SESSION (Deep Work, Meditation, Study)", expanded=True):
        t_col1, t_col2 = st.columns([1, 1])
        
        with t_col1:
            activity = st.selectbox("Select Activity", ["📚 Studying", "🧘 Meditation", "💻 Coding", "🔋 Rest"])
            h_timer = st.number_input("Hours", 0, 12, 0)
            m_timer = st.number_input("Minutes", 0, 59, 25)
            
            if not st.session_state.timer_active:
                if st.button("🚀 Start Session", use_container_width=True):
                    st.session_state.timer_active = True
                    st.rerun()
            else:
                if st.button("🛑 Stop & Reset", use_container_width=True):
                    st.session_state.timer_active = False
                    st.rerun()

        with t_col2:
            timer_box = st.empty()
            if st.session_state.timer_active:
                total_secs = (h_timer * 3600) + (m_timer * 60)
                if total_secs == 0:
                    st.warning("Please set a time!")
                    st.session_state.timer_active = False
                else:
                    try:
                        # Activity Visual
                        visual_emoji = "📖" if "Study" in activity else "🧘" if "Meditation" in activity else "👨‍💻" if "Coding" in activity else "😴"
                        
                        for remaining in range(total_secs, -1, -1):
                            hrs, rem = divmod(remaining, 3600)
                            mins, secs = divmod(rem, 60)
                            timer_box.markdown(f"""
                                <div style='text-align:center;'>
                                    <div style='font-size:80px;'>{visual_emoji}</div>
                                    <div class='timer-text'>{hrs:02d}:{mins:02d}:{secs:02d}</div>
                                    <p style='color:{SUBTEXT};'>{activity} in progress...</p>
                                </div>
                            """, unsafe_allow_html=True)
                            time.sleep(1)
                        
                        st.session_state.timer_active = False
                        data["creature_xp"] += 10 if h_timer > 0 else 5 # Long sessions = More XP
                        save_data(data)
                        st.balloons()
                        st.success(f"Session Complete! {activity} XP added.")
                        time.sleep(2)
                        st.rerun()
                    except:
                        st.session_state.timer_active = False
            else:
                timer_box.info("Choose your activity and time to start evolving.")

    # --- Creature Card (Evolution Logic) ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    xp = data["creature_xp"]
    #
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    elif xp >= 10: stage, emoji = "Hatchling", "🐣"
    else: stage, emoji = "Egg", "🥚"
    
    st.markdown(f"<div style='font-size:100px;'>{emoji}</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='badge'>{stage}</span>", unsafe_allow_html=True)
    st.write(f"**XP Progress:** {xp}/100")
    st.progress(min(xp/100, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

    # --- POWER TASK 2: PRIORITY MATRIX ---
    st.subheader("📌 Urgent Matrix")
    m_in, m_btn = st.columns([3, 1])
    with m_in: new_task = st.text_input("Critical assignment or task...", key="matrix_in")
    with m_btn: 
        if st.button("Add Task", use_container_width=True) and new_task:
            data["matrix"].append(new_task); save_data(data); st.rerun()
    
    for t in data["matrix"]:
        mc1, mc2 = st.columns([5, 1])
        with mc1: st.markdown(f"<div class='matrix-card'>⚡ {t}</div>", unsafe_allow_html=True)
        with mc2: 
            if st.button("Done", key=f"mat_{t}"):
                data["matrix"].remove(t); data["creature_xp"] += 3; save_data(data); st.rerun()

    # --- POWER TASK 3: DAILY HABITS ---
    st.subheader("Daily Habits")
    h_in, h_add = st.columns([3, 1])
    with h_in: new_h = st.text_input("New habit...", label_visibility="collapsed", key="h_in")
    with h_add:
        if st.button("Add", key="add_h_btn", use_container_width=True) and new_h:
            data["habits"].append(new_h); save_data(data); st.rerun()
            
    completions = data["completions"].get(today_str, [])
    for h in data["habits"]:
        hc1, hc2 = st.columns([5, 1])
        with hc1:
            if st.checkbox(h, value=(h in completions), key=f"h_{h}"):
                if h not in completions:
                    data["completions"].setdefault(today_str, []).append(h)
                    data["creature_xp"] += 2; save_data(data); st.rerun()
            elif h in completions:
                data["completions"][today_str].remove(h)
                data["creature_xp"] = max(0, data["creature_xp"] - 2); save_data(data); st.rerun()
        with hc2:
            if st.button("✕", key=f"del_{h}"):
                data["habits"].remove(h); save_data(data); st.rerun()

with col_stats:
    st.subheader("Insights")
    st.markdown(f"<div class='stat-pill'>🔥 Daily Streak<br><b>{len(data['completions'])} Days</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-pill'>⭐ Total XP<br><b>{data['creature_xp']}</b></div>", unsafe_allow_html=True)
    st.write("---")
    st.write("📅 GitHub-Style Heatmap")
    # Heatmap visualization
    cols = st.columns(7)
    for i in range(21): # Last 3 weeks
        d = date.today() - timedelta(days=i)
        active = len(data["completions"].get(str(d), [])) > 0
        color = ACCENT2 if active else BORDER
        with cols[i % 7]:
            st.markdown(f"<div style='background:{color}; height:20px; width:20px; border-radius:4px; margin:2px;'></div>", unsafe_allow_html=True)
