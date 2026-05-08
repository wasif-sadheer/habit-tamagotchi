import streamlit as st
import json
import os
import time
from datetime import date, timedelta, datetime

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
    .assignment-card {{ background:{CARD2}; border-left: 5px solid {ACCENT}; padding:15px; border-radius:10px; margin-bottom:10px; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:5px 15px; border-radius:12px; font-weight:bold; }}
    .timer-text {{ font-size: 60px; font-weight: bold; color: {ACCENT2}; font-family: monospace; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA HANDLING ──
DATA_FILE = "habit_pro_v7.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: return json.load(f)
        except: pass
    return {"habits": [], "completions": {}, "creature_xp": 0, "matrix": [], "assignments": []}

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
    
    # --- POWER TASK 1: ASSIGNMENT VAULT (DEADLINES) ---
    with st.expander("📝 UNIVERSITY ASSIGNMENT VAULT", expanded=True):
        a_col1, a_col2 = st.columns([2, 1])
        with a_col1:
            a_name = st.text_input("Assignment Name (e.g., Programming Project)")
        with a_col2:
            a_date = st.date_input("Due Date", min_value=date.today())
        
        if st.button("Add to Vault", use_container_width=True) and a_name:
            data["assignments"].append({"name": a_name, "due": str(a_date)})
            save_data(data); st.rerun()
            
        st.write("")
        for i, a in enumerate(data["assignments"]):
            due_date = datetime.strptime(a["due"], "%Y-%m-%d").date()
            days_left = (due_date - date.today()).days
            # Color logic: Red if less than 3 days
            urgency_color = "#ff4b4b" if days_left <= 2 else ACCENT2
            
            st.markdown(f"""
                <div class='assignment-card' style='border-left-color: {urgency_color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='text-align: left;'>
                            <b style='font-size: 18px;'>{a['name']}</b><br>
                            <span style='color: {SUBTEXT}; font-size: 13px;'>Deadline: {a['due']}</span>
                        </div>
                        <div style='text-align: right;'>
                            <span style='color: {urgency_color}; font-weight: bold;'>⏳ {days_left} Days Left</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Mark Finished (+10 XP) ✅", key=f"assign_{i}"):
                data["assignments"].pop(i)
                data["creature_xp"] += 10
                save_data(data); st.rerun()

    # --- POWER TASK 2: FOCUS TIMER (PRO VERSION) ---
    with st.expander("🕒 FOCUS SESSION (Deep Work)"):
        t_col1, t_col2 = st.columns([1, 1])
        with t_col1:
            activity = st.selectbox("Current Activity", ["📚 Studying", "🧘 Meditation", "💻 Coding", "🔋 Rest"])
            h_timer = st.number_input("Hours", 0, 12, 0)
            m_timer = st.number_input("Minutes", 0, 59, 25)
            
            if not st.session_state.timer_active:
                if st.button("🚀 Start Focus", use_container_width=True):
                    st.session_state.timer_active = True; st.rerun()
            else:
                if st.button("🛑 Stop & Reset", use_container_width=True):
                    st.session_state.timer_active = False; st.rerun()

        with t_col2:
            timer_box = st.empty()
            if st.session_state.timer_active:
                total_secs = (h_timer * 3600) + (m_timer * 60)
                if total_secs > 0:
                    try:
                        # Simple visual matching your request
                        icon = "📖" if "Study" in activity else "🧘" if "Meditation" in activity else "💻"
                        for remaining in range(total_secs, -1, -1):
                            hrs, rem = divmod(remaining, 3600)
                            mins, secs = divmod(rem, 60)
                            timer_box.markdown(f"""
                                <div style='text-align:center;'>
                                    <div style='font-size:70px;'>{icon}</div>
                                    <div class='timer-text'>{hrs:02d}:{mins:02d}:{secs:02d}</div>
                                    <p style='color:{SUBTEXT};'>{activity} Session Active</p>
                                </div>
                            """, unsafe_allow_html=True)
                            time.sleep(1)
                        st.session_state.timer_active = False
                        data["creature_xp"] += 5
                        save_data(data); st.balloons(); st.rerun()
                    except: st.session_state.timer_active = False
            else:
                timer_box.info("Set your session time to begin.")

    # --- Creature Evolution Card ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    xp = data["creature_xp"]
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    elif xp >= 10: stage, emoji = "Hatchling", "🐣"
    else: stage, emoji = "Egg", "🥚"
    
    st.markdown(f"<div style='font-size:100px;'>{emoji}</div><br><span class='badge'>{stage}</span>", unsafe_allow_html=True)
    st.write(f"**Total XP:** {xp}/100")
    st.progress(min(xp/100, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

    # --- DAILY HABITS ---
    st.subheader("Daily Habits")
    h_in, h_add = st.columns([3, 1])
    with h_in: new_h = st.text_input("Add daily habit...", label_visibility="collapsed", key="h_in")
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
    st.markdown(f"<div class='stat-pill'>⭐ All-time XP<br><b>{data['creature_xp']}</b></div>", unsafe_allow_html=True)
    st.write("---")
    st.write("📅 Weekly Performance")
    cols = st.columns(7)
    for i in range(21): # Last 3 weeks heatmap
        d = date.today() - timedelta(days=i)
        active = len(data["completions"].get(str(d), [])) > 0
        color = ACCENT2 if active else BORDER
        with cols[i % 7]:
            st.markdown(f"<div style='background:{color}; height:20px; width:20px; border-radius:4px; margin:2px; border:1px solid {BORDER};'></div>", unsafe_allow_html=True)
