import streamlit as st
import json
import os
import time
from datetime import date, timedelta, datetime

# ── PALETTE ──
BG, CARD, CARD2, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0f1117", "#1a1d27", "#21253a", "#7c6af7", "#56c596", "#e8eaf0", "#7b7f96", "#2a2d3e"
)

st.set_page_config(page_title="Tamagotchi Life OS Pro", layout="wide")

# ── STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .main-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; padding:25px; margin-bottom: 20px; text-align: center; }}
    .battery-box {{ background:{CARD2}; border-radius:15px; padding:10px; border:1px solid {BORDER}; margin-top:10px; }}
    .timer-text {{ font-size: 50px; font-weight: bold; color: {ACCENT2}; font-family: monospace; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:5px 15px; border-radius:12px; font-weight:bold; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA HANDLING ──
DATA_FILE = "habit_pro_v8.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: return json.load(f)
        except: pass
    return {"habits": [], "completions": {}, "creature_xp": 0, "assignments": [], "energy": 100}

def save_data(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'timer_active' not in st.session_state: st.session_state.timer_active = False

data = st.session_state.data
today_str = str(date.today())

# ── MAIN DASHBOARD ──
col_left, col_mid, col_right = st.columns([1.2, 2, 1.2])

with col_left:
    st.subheader("🔋 Mental Battery")
    # Energy Logic: Habits take energy, Rest restores it.
    energy = data.get("energy", 100)
    bar_color = ACCENT2 if energy > 50 else "#ff4b4b"
    st.progress(energy / 100)
    st.write(f"Current Energy: **{energy}%**")
    st.caption("Tasks consume energy. Use 'Rest' in Timer to recharge!")
    
    st.write("---")
    st.subheader("📝 Assignments")
    for i, a in enumerate(data.get("assignments", [])):
        due_date = datetime.strptime(a["due"], "%Y-%m-%d").date()
        days_left = (due_date - date.today()).days
        st.markdown(f"<div style='padding:10px; background:{CARD2}; border-radius:10px; margin-bottom:5px; border-left:4px solid {ACCENT if days_left > 2 else '#ff4b4b'}'><b>{a['name']}</b><br><small>{days_left} days left</small></div>", unsafe_allow_html=True)

with col_mid:
    st.title("Life OS: Advanced Analytics")
    
    # --- PRO TIMER WITH ENERGY DYNAMICS ---
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        activity = st.selectbox("Focus Mode", ["📚 Intensive Study", "💻 Coding", "🧘 Meditation", "🔋 Deep Rest"])
        col_h, col_m = st.columns(2)
        h_t = col_h.number_input("Hr", 0, 12, 0)
        m_t = col_m.number_input("Min", 0, 59, 25)
        
        t_box = st.empty()
        if not st.session_state.timer_active:
            if st.button("🚀 Start Session", use_container_width=True):
                st.session_state.timer_active = True
                st.rerun()
        else:
            total_secs = (h_t * 3600) + (m_t * 60)
            if st.button("🛑 Stop"):
                st.session_state.timer_active = False
                st.rerun()
            
            # Timer Loop
            for r in range(total_secs, -1, -1):
                hh, rem = divmod(r, 3600)
                mm, ss = divmod(rem, 60)
                t_box.markdown(f"<div class='timer-text'>{hh:02d}:{mm:02d}:{ss:02d}</div>", unsafe_allow_html=True)
                time.sleep(1)
            
            # Session Completion Logic
            st.session_state.timer_active = False
            if "Rest" in activity:
                data["energy"] = min(100, data["energy"] + 20)
            else:
                data["energy"] = max(0, data["energy"] - 15)
                data["creature_xp"] += 5
            
            save_data(data)
            st.balloons()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Creature Card ---
    xp = data["creature_xp"]
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    elif xp >= 10: stage, emoji = "Hatchling", "🐣"
    else: stage, emoji = "Egg", "🥚"
    
    st.markdown(f"<div class='main-card'><div style='font-size:80px;'>{emoji}</div><span class='badge'>{stage}</span><br><br>XP: {xp}/100</div>", unsafe_allow_html=True)

with col_right:
    st.subheader("📊 Performance")
    st.markdown(f"<div class='stat-pill'>🔥 Streak<br><b>{len(data['completions'])} Days</b></div>", unsafe_allow_html=True)
    
    st.write("---")
    st.write("📅 Weekly Focus")
    cols = st.columns(7)
    for i in range(21):
        d = date.today() - timedelta(days=i)
        active = len(data["completions"].get(str(d), [])) > 0
        with cols[i % 7]:
            st.markdown(f"<div style='background:{ACCENT2 if active else BORDER}; height:20px; width:20px; border-radius:4px; margin:2px;'></div>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("✅ Quick Habits")
    new_h = st.text_input("New Habit", label_visibility="collapsed")
    if st.button("Add") and new_h:
        data["habits"].append(new_h); save_data(data); st.rerun()
    
    for h in data["habits"]:
        if st.checkbox(h, key=f"c_{h}"):
            # Logic: Habit gives XP but costs a bit of energy
            if h not in data["completions"].get(today_str, []):
                data["completions"].setdefault(today_str, []).append(h)
                data["creature_xp"] += 2
                data["energy"] = max(0, data["energy"] - 5)
                save_data(data); st.rerun()
