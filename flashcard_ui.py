#!/usr/bin/env python3
"""
🧠 Big Five (OCEAN) Personality Assessment — Streamlit Flashcard UI
Run with: streamlit run flashcard_ui.py
"""

import json
import os
import math
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from scoring import calculate_scores
from ai_results import generate_radar_chart_base64, generate_results

# ─── Helpers ──────────────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> str:
    """Convert #RRGGBB to 'R,G,B' string for rgba() usage."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🧠 Big Five Assessment",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Category & Scale Config ─────────────────────────────────────────────────

CATEGORY_CONFIG = {
    "EXT": {"name": "Extraversion",        "emoji": "🎉", "gradient": "linear-gradient(135deg, #E94560, #FF6B6B)", "color": "#E94560"},
    "AGR": {"name": "Agreeableness",       "emoji": "🤝", "gradient": "linear-gradient(135deg, #0F3460, #3B82F6)", "color": "#3B82F6"},
    "CSN": {"name": "Conscientiousness",   "emoji": "🎯", "gradient": "linear-gradient(135deg, #059669, #16C79A)", "color": "#16C79A"},
    "EST": {"name": "Emotional Stability", "emoji": "🧘", "gradient": "linear-gradient(135deg, #7C3AED, #A78BFA)", "color": "#8B5CF6"},
    "OPN": {"name": "Openness",            "emoji": "🌌", "gradient": "linear-gradient(135deg, #EA580C, #F97316)", "color": "#F97316"},
}

SCALE_OPTIONS = {
    1: {"label": "Very Low",  "emoji": "😴", "color": "#EF4444"},
    2: {"label": "Low",       "emoji": "😕", "color": "#F97316"},
    3: {"label": "Moderate",  "emoji": "😐", "color": "#EAB308"},
    4: {"label": "High",      "emoji": "😊", "color": "#22C55E"},
    5: {"label": "Very High", "emoji": "🔥", "color": "#3B82F6"},
}

# ─── Inject Custom CSS ───────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ─── Global ─── */
.stApp {
    background: linear-gradient(180deg, #0a0a1a 0%, #0f0f2e 50%, #0a0a1a 100%) !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, header, footer, .stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

/* ─── Header ─── */
.main-header {
    text-align: center;
    padding: 1.5rem 1rem 0.75rem;
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60A5FA, #A78BFA, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #64748B;
    font-size: 0.85rem;
    margin-top: 0.2rem;
}

/* ─── Progress ─── */
.progress-section {
    max-width: 600px;
    margin: 0 auto 1.25rem;
    padding: 0 0.5rem;
}
.progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.progress-info .counter { color: #94A3B8; font-size: 0.85rem; font-weight: 500; }
.progress-info .pct { color: #60A5FA; font-size: 0.85rem; font-weight: 700; }
.progress-track {
    width: 100%; height: 8px;
    background: #1E293B;
    border-radius: 99px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899);
    transition: width 0.4s ease;
    box-shadow: 0 0 12px rgba(59,130,246,0.4);
}

/* ─── Category Badges ─── */
.cat-badges {
    display: flex;
    justify-content: center;
    gap: 0.4rem;
    margin-top: 0.6rem;
    flex-wrap: wrap;
}
.cat-badge {
    background: #1E293B;
    border: 1px solid #2D3748;
    border-radius: 99px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    color: #94A3B8;
    font-weight: 600;
    transition: all 0.2s;
}
.cat-badge.active {
    border-color: var(--active-color);
    color: var(--active-color);
    background: rgba(59, 130, 246, 0.1);
    box-shadow: 0 0 8px rgba(59,130,246,0.15);
}

/* ─── Flashcard ─── */
.flashcard {
    max-width: 620px;
    margin: 0 auto;
    background: linear-gradient(145deg, #12122a, #1a1a3e);
    border: 1px solid #2D2D5C;
    border-radius: 24px;
    padding: 2rem 1.75rem 1.75rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(59,130,246,0.05);
}
.flashcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--cat-gradient);
}
.cat-pill {
    display: inline-block;
    padding: 0.35rem 1.1rem;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #FFF;
    background: var(--cat-gradient);
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.q-id { color: #4B5563; font-size: 0.78rem; font-weight: 500; margin-bottom: 0.75rem; }
.q-text {
    font-size: 1.45rem;
    font-weight: 700;
    color: #F1F5F9;
    line-height: 1.4;
    margin-bottom: 1.5rem;
    padding: 0 0.5rem;
}
.scale-label {
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ─── Visual Response Display ─── */
.response-visual {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.rv-item {
    width: 72px;
    text-align: center;
}
.rv-circle {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    background: #1E1E3A;
    border: 2px solid #2D2D5C;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.25rem;
    transition: all 0.2s;
}
.rv-circle.selected {
    border-color: var(--sel-color);
    background: var(--sel-bg);
    box-shadow: 0 0 20px var(--sel-glow);
    transform: scale(1.08);
}
.rv-circle .emoji { font-size: 1.4rem; }
.rv-circle .val { font-size: 0.85rem; font-weight: 700; color: #64748B; }
.rv-circle.selected .val { color: #FFF; }
.rv-label { font-size: 0.6rem; color: #4B5563; font-weight: 500; }

/* ─── Status Pill ─── */
.status-pill {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.3rem 0.85rem;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-pill.answered { background: rgba(34,197,94,0.1); color: #22C55E; border: 1px solid rgba(34,197,94,0.2); }
.status-pill.pending { background: rgba(100,116,139,0.1); color: #64748B; border: 1px solid rgba(100,116,139,0.2); }

/* ─── Streamlit Button Overrides ─── */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.15s ease !important;
    font-size: 0.9rem !important;
}

/* ─── Summary Card ─── */
.summary-card {
    max-width: 600px;
    margin: 0.75rem auto;
    background: linear-gradient(145deg, #12122a, #1a1a3e);
    border: 1px solid #2D2D5C;
    border-radius: 20px;
    padding: 1.25rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.2s;
}
.summary-card:hover {
    border-color: var(--s-color);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.summary-icon {
    font-size: 1.8rem;
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--s-gradient);
    flex-shrink: 0;
}
.summary-info h3 { margin: 0; font-size: 1rem; color: #F1F5F9; font-weight: 700; }
.summary-info p { margin: 0.1rem 0 0; color: #64748B; font-size: 0.82rem; }
.summary-bar-track {
    width: 100%; height: 6px;
    background: #1E293B; border-radius: 99px;
    margin-top: 0.4rem; overflow: hidden;
}
.summary-bar-fill { height: 100%; border-radius: 99px; background: var(--s-gradient); }

/* ─── Results Page ─── */
.results-header {
    text-align: center;
    padding: 1.5rem 0;
}
.results-header .big-emoji { font-size: 3.5rem; display: block; margin-bottom: 0.5rem; }
.results-header h2 {
    color: #F1F5F9; font-weight: 800;
    font-size: 1.6rem; margin: 0 0 0.25rem;
}
.results-header p { color: #64748B; font-size: 0.9rem; margin: 0; }

.scores-overview {
    max-width: 620px;
    margin: 0 auto 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
}
.score-chip {
    background: linear-gradient(145deg, #12122a, #1a1a3e);
    border: 1px solid #2D2D5C;
    border-radius: 16px;
    padding: 1rem 0.5rem;
    text-align: center;
    transition: all 0.2s;
}
.score-chip:hover { border-color: var(--chip-color); transform: translateY(-2px); }
.score-chip .chip-emoji { font-size: 1.5rem; }
.score-chip .chip-name { font-size: 0.7rem; color: #94A3B8; font-weight: 600; margin: 0.3rem 0 0.15rem; }
.score-chip .chip-pct { font-size: 1.25rem; color: #F1F5F9; font-weight: 800; }
.score-chip .chip-level { font-size: 0.65rem; color: var(--chip-color); font-weight: 600; }

.radar-container {
    max-width: 500px;
    margin: 0 auto 1.5rem;
    text-align: center;
}
.radar-container img {
    width: 100%;
    max-width: 450px;
    border-radius: 20px;
    border: 1px solid #2D2D5C;
}

.result-section {
    max-width: 620px;
    margin: 1rem auto;
    background: linear-gradient(145deg, #12122a, #1a1a3e);
    border: 1px solid #2D2D5C;
    border-radius: 20px;
    padding: 1.5rem 1.75rem;
    position: relative;
    overflow: hidden;
}
.result-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--section-gradient);
}
.result-section .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}
.result-section .section-header .sec-emoji { font-size: 1.4rem; }
.result-section .section-header h3 {
    margin: 0; font-size: 1.05rem;
    color: #F1F5F9; font-weight: 700;
}
.result-section .section-body {
    color: #CBD5E1;
    font-size: 0.92rem;
    line-height: 1.7;
}

.flag-banner {
    max-width: 620px;
    margin: 1rem auto;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    color: #FCA5A5;
    font-size: 0.85rem;
    line-height: 1.6;
}

.overall-badge {
    max-width: 280px;
    margin: 1rem auto;
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 2px solid #3B82F6;
    border-radius: 20px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(59,130,246,0.15);
}
.overall-badge .ob-label { color: #94A3B8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.overall-badge .ob-pct { color: #F1F5F9; font-size: 2.5rem; font-weight: 800; margin: 0.25rem 0; }
.overall-badge .ob-level { color: #60A5FA; font-size: 1rem; font-weight: 700; }

/* ─── Responsive ─── */
@media (max-width: 480px) {
    .main-header h1 { font-size: 1.35rem; }
    .q-text { font-size: 1.1rem; }
    .rv-item { width: 56px; }
    .rv-circle { width: 50px; height: 50px; border-radius: 12px; }
    .rv-circle .emoji { font-size: 1.1rem; }
    .rv-circle .val { font-size: 0.75rem; }
    .flashcard { padding: 1.25rem 1rem; border-radius: 18px; }
    .scores-overview { grid-template-columns: repeat(3, 1fr); }
    .result-section { padding: 1.25rem 1rem; }
}
</style>
""", unsafe_allow_html=True)


# ─── Load Data ────────────────────────────────────────────────────────────────

@st.cache_data
def load_questions():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    q_path = os.path.join(script_dir, "question.txt")
    with open(q_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]

questions = load_questions()
total = len(questions)

# ─── Session State ────────────────────────────────────────────────────────────

if "idx" not in st.session_state:
    st.session_state.idx = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "finished" not in st.session_state:
    st.session_state.finished = False
if "ai_results" not in st.session_state:
    st.session_state.ai_results = None
if "scores" not in st.session_state:
    st.session_state.scores = None

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <div style="display:inline-block; background:rgba(59,130,246,0.1); color:#3B82F6; padding:4px 12px; border-radius:99px; font-size:0.7rem; font-weight:700; margin-bottom:8px; border:1px solid rgba(59,130,246,0.2); text-transform:uppercase; letter-spacing:0.5px;">
        🤖 AI-Powered Personality Detector
    </div>
    <h1>🧠 Big Five Personality Assessment</h1>
    <p>50 questions · Powered by <b>Gemini 2.5 Flash</b></p>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESULTS SCREEN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if st.session_state.finished:
    # ── Compute scores (once) ─────────────────────────────────────────────
    if st.session_state.scores is None:
        st.session_state.scores = calculate_scores(
            st.session_state.responses, questions
        )
    scores = st.session_state.scores
    cat_scores = scores["category_scores"]
    answered = len(st.session_state.responses)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="results-header">
        <span class="big-emoji">🎊</span>
        <h2>Assessment Complete!</h2>
        <p>You answered <strong style="color:#60A5FA">{answered}</strong> of
           <strong style="color:#60A5FA">{total}</strong> questions</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Overall Badge ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="overall-badge">
        <div class="ob-label">Overall Personality Score</div>
        <div class="ob-pct">{scores['overall_pct']}%</div>
        <div class="ob-level">{scores['overall_level']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Chips ───────────────────────────────────────────────────────
    chips_html = ""
    for k in ["EXT", "AGR", "CSN", "EST", "OPN"]:
        cfg = CATEGORY_CONFIG[k]
        s = cat_scores[k]
        chips_html += f"""
        <div class="score-chip" style="--chip-color:{cfg['color']};">
            <div class="chip-emoji">{cfg['emoji']}</div>
            <div class="chip-name">{cfg['name'][:3].upper()}</div>
            <div class="chip-pct">{s['pct']}%</div>
            <div class="chip-level">{s['level']}</div>
        </div>"""

    st.markdown(f'<div class="scores-overview">{chips_html}</div>', unsafe_allow_html=True)

    # ── Radar Chart ───────────────────────────────────────────────────────
    radar_b64 = generate_radar_chart_base64(cat_scores)
    st.markdown(f"""
    <div class="radar-container">
        <img src="data:image/png;base64,{radar_b64}" alt="Personality Radar Chart" />
    </div>
    """, unsafe_allow_html=True)

    # ── Flags (if any) ────────────────────────────────────────────────────
    if scores["flags"]:
        flags_html = "<br>".join(scores["flags"])
        st.markdown(f"""
        <div class="flag-banner">
            <strong>⚠️ Unusual Patterns Detected</strong><br><br>
            {flags_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Gemini AI Explanations (auto-generated) ─────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    import os
    # Priority: 1. Streamlit Secrets (Cloud), 2. .env (Local)
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        st.error("❌ GEMINI_API_KEY not found. Please set it in .env (local) or Streamlit Secrets (cloud).")
        st.stop()

    # Auto-generate results on first load
    if st.session_state.ai_results is None:
        with st.spinner("🧠 Deadpool is analysing your personality... hold tight!"):
            st.session_state.ai_results = generate_results(GEMINI_API_KEY, scores)

    ai = st.session_state.ai_results

    if "error" in ai:
        st.error(f"❌ {ai['error']}")
    else:
        # Section A — Spider Chart Explained
        st.markdown(f"""
        <div class="result-section" style="--section-gradient: linear-gradient(90deg, #3B82F6, #8B5CF6);">
            <div class="section-header">
                <span class="sec-emoji">🕸️</span>
                <h3>Your Spider Chart — Decoded</h3>
            </div>
            <div class="section-body">{ai.get('a', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Section B — Overall Personality
        st.markdown(f"""
        <div class="result-section" style="--section-gradient: linear-gradient(90deg, #EC4899, #F97316);">
            <div class="section-header">
                <span class="sec-emoji">🧬</span>
                <h3>Who Are You, Really?</h3>
            </div>
            <div class="section-body">{ai.get('b', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Section C — Category Breakdown
        st.markdown(f"""
        <div class="result-section" style="--section-gradient: linear-gradient(90deg, #16C79A, #3B82F6);">
            <div class="section-header">
                <span class="sec-emoji">📊</span>
                <h3>Category Breakdown — The Simple Truth</h3>
            </div>
            <div class="section-body">{ai.get('c', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Section D — Unusual Patterns
        st.markdown(f"""
        <div class="result-section" style="--section-gradient: linear-gradient(90deg, #EF4444, #F97316);">
            <div class="section-header">
                <span class="sec-emoji">🔍</span>
                <h3>Honesty Check</h3>
            </div>
            <div class="section-body">{ai.get('d', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Restart Button ────────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔄  Restart Assessment", use_container_width=True):
            st.session_state.idx = 0
            st.session_state.responses = {}
            st.session_state.finished = False
            st.session_state.scores = None
            st.session_state.ai_results = None
            st.rerun()
    st.stop()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ASSESSMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx = st.session_state.idx
q = questions[idx]
cat_key = q["category"]
cat = CATEGORY_CONFIG[cat_key]
answered_count = len(st.session_state.responses)
pct_val = math.floor((answered_count / total) * 100)

# ── Progress Bar ──────────────────────────────────────────────────────────────

badges_html = ""
for k, c in CATEGORY_CONFIG.items():
    active_cls = "active" if k == cat_key else ""
    badges_html += f'<span class="cat-badge {active_cls}" style="--active-color:{c["color"]}">{c["emoji"]} {c["name"][:3].upper()}</span>'

st.markdown(f"""
<div class="progress-section">
    <div class="progress-info">
        <span class="counter">📋 Question {idx + 1} of {total}</span>
        <span class="pct">{pct_val}% complete</span>
    </div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{pct_val}%;"></div>
    </div>
    <div class="cat-badges">{badges_html}</div>
</div>
""", unsafe_allow_html=True)

# ── Flashcard ─────────────────────────────────────────────────────────────────

selected = st.session_state.responses.get(q["id"])

# Visual response display (non-clickable, just shows state)
rv_html = ""
for val in range(1, 6):
    opt = SCALE_OPTIONS[val]
    is_selected = val == selected
    sel_cls = "selected" if is_selected else ""
    sel_style = ""
    if is_selected:
        rgb = hex_to_rgb(opt["color"])
        sel_style = f'--sel-color:{opt["color"]}; --sel-bg:rgba({rgb},0.18); --sel-glow:rgba({rgb},0.25);'

    rv_html += f"""
    <div class="rv-item">
        <div class="rv-circle {sel_cls}" style="{sel_style}">
            <span class="emoji">{opt["emoji"]}</span>
            <span class="val">{val}</span>
        </div>
        <span class="rv-label">{opt["label"]}</span>
    </div>"""

# Status pill
if selected:
    s_opt = SCALE_OPTIONS[selected]
    status_html = f'<span class="status-pill answered">✅ {s_opt["emoji"]} {s_opt["label"]}</span>'
else:
    status_html = '<span class="status-pill pending">⏳ Pick a response below</span>'

st.markdown(f"""
<div class="flashcard" style="--cat-gradient:{cat['gradient']};">
    <div class="cat-pill">{cat['emoji']}  {cat['name']}</div>
    <div class="q-id">#{q['id']}</div>
    <div class="q-text">"{q['text']}"</div>
    <div class="scale-label">How much does this describe you?</div>
    <div class="response-visual">{rv_html}</div>
    {status_html}
</div>
""", unsafe_allow_html=True)

# ── Clickable Streamlit Response Buttons ──────────────────────────────────────

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

cols = st.columns(5)
for i, val in enumerate(range(1, 6)):
    opt = SCALE_OPTIONS[val]
    with cols[i]:
        btn_label = f"✅ {val}" if selected == val else f"{opt['emoji']} {val}"
        if st.button(btn_label, key=f"resp_{val}", use_container_width=True):
            st.session_state.responses[q["id"]] = val
            st.rerun()

# ── Navigation Buttons ───────────────────────────────────────────────────────

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

nav_l, nav_m, nav_r = st.columns([1, 1, 1])

with nav_l:
    if idx > 0:
        if st.button("⬅️ Previous", key="nav_prev", use_container_width=True):
            st.session_state.idx -= 1
            st.rerun()

with nav_r:
    if idx < total - 1:
        if st.button("Next ➡️", key="nav_next", use_container_width=True):
            st.session_state.idx += 1
            st.rerun()
    else:
        if st.button("🏁 Finish", key="nav_finish", use_container_width=True):
            st.session_state.finished = True
            st.rerun()
