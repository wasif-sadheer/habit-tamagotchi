import streamlit as st
import json
import os
import time
from datetime import date, timedelta, datetime

# ── PROFESSIONAL THEME CONFIG ──
BG, CARD, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER = (
    "#0d1117", "#161b22", "#58a6ff", "#2ea043", "#c9d1d9", "#8b949e", "#30363d"
)

st.set_page_config(page_title="Life OS | Command Center", layout="wide")

# ── ADVANCED UI STYLING ──
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; white-space: pre-wrap; background-color: transparent; 
        border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px;
    }}
    .status-card {{ 
        background:{CARD}; border:1px solid {BORDER}; border-radius:15px; 
        padding:20px; margin-bottom: 20px; border-top: 4px solid {ACCENT};
    }}
    .assignment-card {{ 
        background:{CARD}; border:1px solid {BORDER}; border-radius:10px; 
        padding:15px; margin-bottom:10px; transition: 0.3s;
    }}
    .assignment-card:hover {{ border-color: {ACCENT}; }}
    .timer-display {{ 
        font-size: 70px; font-weight: 800; color: {ACCENT}; 
        font-family: 'Courier New', monospace; text-align: center; padding: 20px 0;
    }}
    .metric-val {{ font-size: 24px; font-weight: bold; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# ── DATA CORE ──
DATA_FILE = "life_os_v9_pro.json"
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

# ── TOP STATUS BAR (Global Metrics) ──
st.title("Life OS Command Center")
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""<div class='status-card'>
        <small style='color:{SUBTEXT};'>MENTAL BATTERY</small><br>
        <span class='metric-val'>{data['energy']}%</span>
    </div>""", unsafe_allow_html=True)
    st.progress(data['energy']/100)

with m2:
    xp = data["creature_xp"]
    if xp >= 100: stage, emoji = "Champion", "🏆"
    elif xp >= 60: stage, emoji = "Buddy", "🐶"
    elif xp >= 30: stage, emoji = "Sprout", "🌱"
    else: stage, emoji = "Egg", "🥚"
    st.markdown(f"""<div class='status-card' style='border-top-color:{ACCENT2}'>
        <small style='color:{SUBTEXT};'>TAMAGOTCHI STATUS</small><br>
        <span class='metric-val'>{emoji} {stage} ({xp} XP)</span>
    </div>""", unsafe_allow_html=True)

with m3:
    streak = len(data['completions'])
    st.markdown(f"""<div class='status-card' style='border-top-color:#f39c12'>
        <small style='color:{SUBTEXT};'>CURRENT STREAK</small><br>
        <span class='metric-val'>🔥 {streak} Days</span>
    </div>""", unsafe_allow_html=True)

st.write("---")

# ── MAIN NAVIGATION TABS ──
tab_focus, tab_assign, tab_habits = st.tabs(["🎯 Focus Session", "📋 Assignments", "📅 Routine & Insights"])

# --- TAB 1: FOCUS SESSION ---
with tab_focus:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("Setup Session")
        f_mode = st.selectbox("Activity Type", ["📚 Intensive Study", "💻 Dev Mode", "🧘 Meditation", "🔋 Recovery Rest"])
        f_hrs = st.number_input("Hours", 0, 12, 0)
        f_mins = st.number_input("Minutes", 0, 59, 25)
        
        if not st.session_state.timer_active:
            if st.button("🚀 Start Deep Work", use_container_width=True):
                st.session_state.timer_active = True
                st.rerun()
        else:
            if st.button("🛑 Abort Session", use_container_width=True):
                st.session_state.timer_active = False
                st.rerun()
                
    with c2:
        timer_placeholder = st.empty()
        if st.session_state.timer_active:
            total_s = (f_hrs * 3600) + (f_mins * 60)
            if total_s > 0:
                for s in range(total_s, -1, -1):
                    hh, rem = divmod(s, 3600)
                    mm, ss = divmod(rem, 60)
                    timer_placeholder.markdown(f"<div class='timer-display'>{hh:02d}:{mm:02d}:{ss:02d}</div><p style='text-align:center; color:{SUBTEXT}'>{f_mode} in progress...</p>", unsafe_allow_html=True)
                    time.sleep(1)
                
                st.session_state.timer_active = False
                if "Rest" in f_mode: data["energy"] = min(100, data["energy"] + 30)
                else: 
                    data["creature_xp"] += 10 if f_hrs > 0 else 5
                    data["energy"] = max(0, data["energy"] - 20)
                save_data(data); st.balloons(); st.rerun()
            else:
                st.warning("Please set a valid time.")
        else:
            timer_placeholder.info("Ready for a new session? Set your time on the left.")

# --- TAB 2: ASSIGNMENT VAULT ---
with tab_assign:
    st.subheader("New Assignment")
    a1, a2, a3 = st.columns([3, 2, 1])
    with a1: a_name = st.text_input("Name", placeholder="e.g. Calculus Assignment #3")
    with a2: a_date = st.date_input("Deadline", min_value=date.today())
    with a3: 
        if st.button("Add to Vault", use_container_width=True) and a_name:
            data["assignments"].append({"name": a_name, "due": str(a_date)})
            save_data(data); st.rerun()
    
    st.write("---")
    st.subheader("Active Tasks")
    if not data["assignments"]:
        st.caption("No pending assignments. Great job!")
    else:
        for i, a in enumerate(data["assignments"]):
            due_dt = datetime.strptime(a["due"], "%Y-%m-%d").date()
            days_left = (due_dt - date.today()).days
            color = "#ff4b4b" if days_left <= 2 else ACCENT
            
            with st.container():
                st.markdown(f"""
                    <div class='assignment-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <b style='font-size:18px;'>{a['name']}</b><br>
                                <small style='color:{SUBTEXT}'>Due: {a['due']}</small>
                            </div>
                            <div style='text-align:right;'>
                                <span style='color:{color}; font-weight:bold;'>{days_left} Days Left</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Mark as Completed ✅", key=f"done_{i}"):
                    data["assignments"].pop(i)
                    data["creature_xp"] += 15
                    data["energy"] = max(0, data["energy"] - 10)
                    save_data(data); st.rerun()

# --- TAB 3: ROUTINE & HEATMAP ---
with tab_habits:
    col_h, col_v = st.columns([1, 1])
    with col_h:
        st.subheader("Daily Habits")
        new_h = st.text_input("Add new habit...")
        if st.button("Add Habit") and new_h:
            data["habits"].append(new_h); save_data(data); st.rerun()
        
        done_today = data["completions"].get(today_str, [])
        for h in data["habits"]:
            c_col, d_col = st.columns([4, 1])
            with c_col:
                if st.checkbox(h, value=(h in done_today), key=f"hab_{h}"):
                    if h not in done_today:
                        data["completions"].setdefault(today_str, []).append(h)
                        data["creature_xp"] += 2
                        data["energy"] = max(0, data["energy"] - 5)
                        save_data(data); st.rerun()
            with d_col:
                if st.button("✕", key=f"del_{h}"):
                    data["habits"].remove(h); save_data(data); st.rerun()
    
    with col_v:
        st.subheader("Consistency Map")
        h_cols = st.columns(7)
        for i in range(21):
            d = date.today() - timedelta(days=i)
            active = len(data["completions"].get(str(d), [])) > 0
            with h_cols[i % 7]:
                st.markdown(f"<div style='background:{ACCENT2 if active else BORDER}; height:30px; width:100%; border-radius:4px; margin-bottom:5px; border:1px solid {BORDER}'></div>", unsafe_allow_html=True)
        st.caption("Active days are highlighted in green.")
