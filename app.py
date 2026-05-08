import streamlit as st
import json
import os
from datetime import date, timedelta

# ── PALETTE (EXACT FROM habit_tamagotchi.py) ──
#
BG          = "#0f1117"
CARD        = "#1a1d27"
CARD2       = "#21253a"
ACCENT      = "#7c6af7"
ACCENT2     = "#56c596"
DANGER      = "#ff6b6b"
TEXT        = "#e8eaf0"
SUBTEXT     = "#7b7f96"
BORDER      = "#2a2d3e"

st.set_page_config(page_title="Habit Tamagotchi", layout="centered")

# ── CUSTOM CSS (TO MATCH PYQT UI) ──
#
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    
    .creature-card {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .stat-pill {{
        background-color: {CARD2};
        border-radius: 14px;
        padding: 10px;
        border: 1px solid {BORDER};
        margin-bottom: 8px;
    }}
    .habit-row {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 10px;
    }}
    .badge {{
        background: linear-gradient(90deg, {ACCENT}, {ACCENT2});
        color: white;
        padding: 2px 12px;
        border-radius: 11px;
        font-size: 12px;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# ── LOGIC (EXACT FROM habit_tamagotchi.py) ──
DATA_FILE = "habit_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"habits": [], "completions": {}, "creature_xp": 0}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def get_stage(xp):
    #
    STAGES = [
        {"name": "Egg",       "min_xp": 0,   "emoji": "🥚"},
        {"name": "Hatchling", "min_xp": 10,  "emoji": "🐣"},
        {"name": "Sprout",    "min_xp": 30,  "emoji": "🌱"},
        {"name": "Buddy",     "min_xp": 60,  "emoji": "🐶"},
        {"name": "Champion",  "min_xp": 100, "emoji": "🏆"},
    ]
    current = STAGES[0]
    for s in STAGES:
        if xp >= s["min_xp"]: current = s
    return current

def calc_streak(data):
    #
    habits = data["habits"]
    if not habits: return 0
    streak = 0
    d = date.today()
    while True:
        done = data["completions"].get(str(d), [])
        if all(h in done for h in habits):
            streak += 1
            d -= timedelta(days=1)
        else: break
    return streak

# --- State Management ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today_str = str(date.today())

# ── UI HEADER ──
st.title("Habit Tamagotchi")
st.caption(f"📅 {today_str}")

# ── CREATURE SECTION (Matching CreatureWidget & Stats) ──
#
with st.container():
    st.markdown('<div class="creature-card">', unsafe_allow_html=True)
    
    stage = get_stage(data["creature_xp"])
    col_img, col_stats = st.columns([1, 1.5])
    
    with col_img:
        st.markdown(f"<h1 style='font-size: 100px; text-align: center; margin: 0;'>{stage['emoji']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'><span class='badge'>{stage['name']}</span></div>", unsafe_allow_html=True)

    with col_stats:
        xp = data["creature_xp"]
        st.write(f"**XP:** {xp}")
        st.progress(min(xp / 100, 1.0))
        
        # Stat Pills
        done_count = len(data["completions"].get(today_str, []))
        total_count = len(data["habits"])
        streak = calc_streak(data)
        
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(f"<div class='stat-pill'><small style='color:{SUBTEXT}'>🔥 STREAK</small><br><b>{streak} Days</b></div>", unsafe_allow_html=True)
        with s2:
            st.markdown(f"<div class='stat-pill'><small style='color:{SUBTEXT}'>✅ TODAY</small><br><b>{done_count}/{total_count}</b></div>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

st.write("") # Spacer

# ── ADD HABIT ──
#
c_in, c_btn = st.columns([4, 1])
with c_in:
    new_h = st.text_input("", placeholder="＋ Add a new habit...", label_visibility="collapsed")
with c_btn:
    if st.button("Add", use_container_width=True) and new_h:
        if new_h not in data["habits"]:
            data["habits"].append(new_h)
            save_data(data)
            st.rerun()

st.markdown(f"<p style='color: {SUBTEXT}; font-size: 11px; font-weight: bold; letter-spacing: 1.5px;'>TODAY'S HABITS</p>", unsafe_allow_html=True)

# ── HABIT LIST (Matching HabitRow) ──
#
completions = data["completions"].get(today_str, [])

for h in data["habits"]:
    is_done = h in completions
    
    # Custom container for the row
    col_check, col_del = st.columns([5, 1])
    
    with col_check:
        # Checkbox handles XP (+2 per habit)
        if st.checkbox(h, value=is_done, key=f"cb_{h}"):
            if h not in completions:
                data["completions"].setdefault(today_str, []).append(h)
                data["creature_xp"] += 2
                save_data(data)
                st.rerun()
        else:
            if h in completions:
                data["completions"][today_str].remove(h)
                data["creature_xp"] = max(0, data["creature_xp"] - 2)
                save_data(data)
                st.rerun()

    with col_del:
        if st.button("✕", key=f"del_{h}", help="Delete"):
            data["habits"].remove(h)
            if today_str in data["completions"] and h in data["completions"][today_str]:
                data["completions"][today_str].remove(h)
            save_data(data)
            st.rerun()