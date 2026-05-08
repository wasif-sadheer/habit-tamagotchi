import streamlit as st
import json
import os
import time
from datetime import date, timedelta, datetime

# ── PALETTE (Professional Dark Theme) ──
BG, CARD, CARD2, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0f1117", "#1a1d27", "#21253a", "#7c6af7", "#56c596", "#e8eaf0", "#7b7f96", "#2a2d3e"
)

st.set_page_config(page_title="Life OS Pro", layout="wide")

# ── STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .main-card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; padding:25px; margin-bottom: 20px; }}
    .assignment-box {{ background:{CARD2}; border-left: 5px solid {ACCENT}; padding:15px; border-radius:12px; margin-bottom:10px; }}
    .timer-text {{ font-size: 65px; font-weight: bold; color: {ACCENT2}; font-family: monospace; text-align: center; }}
    .badge {{ background: linear-gradient(90deg, {ACCENT}, {ACCENT2}); color:white; padding:5px 15px; border-radius:12px; font-weight:bold; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA HANDLING ──
DATA_FILE = "life_os_final.json"
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
st.title("Life OS: Advanced Command Center 🚀")

# --- SECTION 1: ASSIGNMENT VAULT (TOP) ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.subheader("📝 Assignment Vault")
a_in, a_dt, a_btn = st.columns([3, 2, 1])
with a_in: new_a = st.text_input("Assignment Name", key="new_a")
with a_dt: new_d = st.date_input("Deadline", min_value=date.today(), key="new_d")
with a_btn:
    if st.button("Add Assignment", use_container_width=True) and new_a:
        data["assignments"].append({"name": new_a, "due": str(new_d)})
        save_data(data); st.rerun()

if data["assignments"]:
    cols = st.columns(2)
    for i, a in enumerate(data["assignments"]):
        due_dt = datetime.strptime(a["due"], "%Y-%m-%d").date()
        days_left = (due_dt - date.today()).days
        u_color = "#ff4b4b" if days_left <= 2 else ACCENT2
        with cols[i % 2]:
            st.markdown(f"""
                <div class='assignment-box' style='border-left-color: {u_color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b>{a['name']}</b>
                        <span style='color: {u_color}; font-weight: bold;'>⏳ {days_left} Days</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Mark Completed ✅", key=f"finish_{i}"):
                data["assignments"].pop(i); data["creature_xp"] += 10; data["energy"] = max(0, data["energy"] - 10)
                save_data(data); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 2: FOCUS, CREATURE & HABITS ---
c_left, c_mid, c_right = st.columns([1.5, 1, 1.2])

with c_left:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🕒 Deep Work Timer")
    energy = data.get("energy", 100)
    st.progress(energy / 100)
    st.caption(f"Mental Battery: {energy}%")
    
    mode = st.selectbox("Mode", ["📚 Study", "💻 Code", "🔋 Rest"])
    col_h, col_m = st.columns(2)
    h_v = col_h.number_input("Hr", 0, 12, 0)
    m_v = col_m.number_input("Min", 0, 59, 25)
    
    t_place = st.empty()
    if not st.session_state.timer_active:
        if st.button("🚀 Start Focus", use_container_width=True):
            st.session_state.timer_active = True; st.rerun()
    else:
        if st.button("🛑 Stop Focus", use_container_width=True):
            st.session_state.timer_active = False; st.rerun()
        
        secs = (h_v * 3600) + (m_v * 60)
        for s in range(secs, -1, -1):
            hh, rem = divmod(s, 3600)
            mm, ss = divmod(rem, 60)
            t_place.markdown(f"<div class='timer-text'>📖 {hh:02d}:{mm:02d}:{ss:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.session_state.timer_active = False
        if "Rest" in mode: data["energy"] = min(100, data["energy"] + 25)
        else: data["creature_xp"] += 5; data["energy"] = max(0, data["energy"] - 15)
        save_data(data); st.balloons(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c_mid:
    st.markdown('<div class="main-card" style="text-align:center;">', unsafe_allow_html=True)
    xp = data["creature_xp"]
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    elif xp >= 10: stage, emoji = "Hatchling", "🐣"
    else: stage, emoji = "Egg", "🥚"
    st.markdown(f"<div style='font-size:80px;'>{emoji}</div><span class='badge'>{stage}</span>", unsafe_allow_html=True)
    st.write(f"XP: {xp}/100")
    st.progress(min(xp/100, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.subheader("✅ Daily Habits")
    h_n = st.text_input("New habit", key="h_n")
    if st.button("Add", key="h_b"):
        data["habits"].append(h_n); save_data(data); st.rerun()
    
    done = data["completions"].get(today_str, [])
    for h in data["habits"]:
        if st.checkbox(h, value=(h in done), key=f"ch_{h}"):
            if h not in done:
                data["completions"].setdefault(today_str, []).append(h)
                data["creature_xp"] += 2; data["energy"] = max(0, data["energy"] - 5)
                save_data(data); st.rerun()
    
    st.write("---")
    st.subheader("📅 Activity")
    h_cls = st.columns(7)
    for i in range(21):
        d = date.today() - timedelta(days=i)
        act = len(data["completions"].get(str(d), [])) > 0
        with h_cls[i % 7]:
            st.markdown(f"<div style='background:{ACCENT2 if act else BORDER}; height:18px; width:18px; border-radius:4px; margin:2px;'></div>", unsafe_allow_html=True)
