import streamlit as st
import json
import re
import os
from openai import OpenAI

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SimGroupAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIORITIES = [
    "Price & Value",
    "Product Features & Functionality",
    "Design & Aesthetics",
    "Ease of Use & UX",
    "Brand Trust & Credibility",
    "Privacy & Data Security",
    "Performance & Quality",
    "Sustainability & Ethics",
    "Health & Safety",
    "Innovation & Novelty",
    "Social Status & Prestige",
    "Convenience & Speed",
    "Customer Support",
    "Accessibility & Inclusivity",
    "Environmental Impact",
    "Community & Social Impact",
    "Family-Friendliness",
    "Durability & Reliability",
]

# ─────────────────────────────────────────────
# CSS — Dark GA-inspired
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
    }

    /* ── Base ── */
    .stApp {
        background: #1c1c1e;
        color: #e8eaed;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #28282b !important;
        border-right: 1px solid #3c3c3f;
        display: block !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #bdc1c6 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e8eaed !important;
    }
    /* Hide the collapse arrow inside sidebar — sidebar stays permanently open */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    /* ── Top nav bar ── */
    .ga-topbar {
        background: #28282b;
        border-bottom: 1px solid #3c3c3f;
        padding: 0 24px;
        margin: -1rem -1rem 28px -1rem;
        display: flex;
        align-items: center;
        height: 56px;
        gap: 16px;
    }
    .ga-logo {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #e8eaed;
        letter-spacing: -0.2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .ga-logo-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #1a73e8;
        display: inline-block;
    }
    .ga-property {
        font-size: 0.78rem;
        color: #9aa0a6;
        border-left: 1px solid #3c3c3f;
        padding-left: 14px;
        letter-spacing: 0.2px;
    }

    /* ── Cards ── */
    .ga-card {
        background: #28282b;
        border: 1px solid #3c3c3f;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .ga-card-title {
        font-size: 0.72rem;
        font-weight: 500;
        color: #9aa0a6;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ga-metric-value {
        font-size: 2.4rem;
        font-weight: 400;
        color: #e8eaed;
        line-height: 1;
        font-family: 'Google Sans', 'Roboto', sans-serif;
    }
    .ga-metric-sub {
        font-size: 0.78rem;
        color: #9aa0a6;
        margin-top: 6px;
    }

    /* ── Summary scorecard row ── */
    .ga-scorecard-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .ga-scorecard {
        background: #28282b;
        border: 1px solid #3c3c3f;
        border-radius: 8px;
        padding: 16px 20px;
        flex: 1;
        min-width: 140px;
    }
    .ga-scorecard-label {
        font-size: 0.72rem;
        color: #9aa0a6;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        margin-bottom: 6px;
    }
    .ga-scorecard-value {
        font-size: 2rem;
        font-weight: 400;
        color: #e8eaed;
        font-family: 'Google Sans', 'Roboto', sans-serif;
        line-height: 1;
    }
    .ga-scorecard-delta {
        font-size: 0.75rem;
        margin-top: 4px;
    }
    .delta-green { color: #34a853; }
    .delta-yellow { color: #fbbc04; }
    .delta-red { color: #ea4335; }

    /* ── Progress bars ── */
    .ga-bar-row {
        margin-bottom: 10px;
    }
    .ga-bar-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        color: #bdc1c6;
        margin-bottom: 4px;
    }
    .ga-bar-track {
        background: #3c3c3f;
        border-radius: 3px;
        height: 5px;
        overflow: hidden;
    }
    .ga-bar-fill {
        height: 100%;
        border-radius: 3px;
        background: #1a73e8;
    }
    .ga-bar-fill-warn {
        background: #fbbc04;
    }
    .ga-bar-fill-danger {
        background: #ea4335;
    }
    .ga-bar-fill-green {
        background: #34a853;
    }

    /* ── Table-like rows (findings) ── */
    .ga-finding-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #3c3c3f;
        font-size: 0.84rem;
        color: #bdc1c6;
        line-height: 1.45;
    }
    .ga-finding-row:last-child { border-bottom: none; }
    .ga-finding-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        margin-top: 6px;
        flex-shrink: 0;
    }
    .dot-red { background: #ea4335; }
    .dot-green { background: #34a853; }
    .dot-yellow { background: #fbbc04; }

    /* ── Chip / badge ── */
    .ga-chip {
        display: inline-flex;
        align-items: center;
        background: #35363a;
        border: 1px solid #5f6368;
        border-radius: 16px;
        padding: 3px 10px;
        font-size: 0.72rem;
        color: #bdc1c6;
        margin: 2px;
        gap: 4px;
    }
    .ga-chip-blue {
        background: #1a3a5c;
        border-color: #1a73e8;
        color: #8ab4f8;
    }
    .ga-chip-green {
        background: #1e3a2a;
        border-color: #34a853;
        color: #81c995;
    }
    .ga-chip-red {
        background: #3a1e1e;
        border-color: #ea4335;
        color: #f28b82;
    }
    .ga-chip-yellow {
        background: #3a3010;
        border-color: #fbbc04;
        color: #fdd663;
    }

    /* ── Verdict badge ── */
    .verdict-badge {
        display: inline-block;
        border-radius: 4px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    .verdict-green { background: #1e3a2a; color: #81c995; border: 1px solid #34a853; }
    .verdict-yellow { background: #3a3010; color: #fdd663; border: 1px solid #fbbc04; }
    .verdict-orange { background: #3a2810; color: #ffb74d; border: 1px solid #f57c00; }
    .verdict-red { background: #3a1e1e; color: #f28b82; border: 1px solid #ea4335; }

    /* ── Honesty badge ── */
    .honesty-chip {
        font-size: 0.68rem;
        padding: 2px 7px;
        border-radius: 10px;
        font-weight: 500;
        margin-left: 6px;
        vertical-align: middle;
    }
    .hc-high { background: #1e3a2a; color: #81c995; }
    .hc-mid  { background: #3a3010; color: #fdd663; }
    .hc-low  { background: #3a1e1e; color: #f28b82; }

    /* ── Transcript bubbles ── */
    .tx-bubble {
        padding: 10px 14px;
        border-radius: 6px;
        margin: 5px 0;
        background: #28282b;
        border: 1px solid #3c3c3f;
        font-size: 0.87rem;
        line-height: 1.55;
        color: #bdc1c6;
    }
    .tx-bubble:hover { border-color: #5f6368; }
    .tx-name {
        font-size: 0.72rem;
        font-weight: 500;
        color: #8ab4f8;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tx-bubble-user {
        background: #1a2535;
        border-color: #1a73e8;
    }
    .tx-name-user {
        color: #fbbc04;
    }

    /* ── Next step cards ── */
    .ns-card {
        background: #28282b;
        border: 1px solid #3c3c3f;
        border-left: 3px solid #1a73e8;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .ns-title {
        font-size: 0.84rem;
        font-weight: 500;
        color: #8ab4f8;
        margin-bottom: 4px;
    }
    .ns-body {
        font-size: 0.81rem;
        color: #9aa0a6;
        line-height: 1.5;
    }
    .ns-profile {
        font-size: 0.73rem;
        color: #5f6368;
        margin-top: 5px;
    }

    /* ── Section headers ── */
    .ga-section-title {
        font-size: 0.72rem;
        font-weight: 500;
        color: #9aa0a6;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 24px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #3c3c3f;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #28282b;
        border-radius: 6px;
        padding: 3px;
        gap: 2px;
        border: 1px solid #3c3c3f;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #9aa0a6 !important;
        border-radius: 4px;
        font-size: 0.84rem;
        font-weight: 500;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #35363a !important;
        color: #e8eaed !important;
    }

    /* ── Inputs ── */
    .stTextArea textarea,
    .stTextInput input {
        background: #28282b !important;
        border: 1px solid #3c3c3f !important;
        color: #e8eaed !important;
        border-radius: 6px !important;
        font-size: 0.87rem !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #1a73e8 !important;
        box-shadow: 0 0 0 2px rgba(26,115,232,0.2) !important;
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: #1a73e8 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 8px 22px !important;
        font-size: 0.87rem !important;
        letter-spacing: 0.2px !important;
        font-family: 'Roboto', sans-serif !important;
    }
    .stButton > button:hover {
        background: #1557b0 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #28282b !important;
        border: 1px solid #3c3c3f !important;
        border-radius: 6px !important;
        color: #bdc1c6 !important;
        font-size: 0.84rem !important;
    }

    /* ── Progress spinner ── */
    .stProgress > div > div {
        background-color: #1a73e8 !important;
    }

    /* ── Checkbox ── */
    .stCheckbox label span {
        font-size: 0.84rem !important;
    }

    /* ── Radio ── */
    .stRadio label span {
        font-size: 0.84rem !important;
    }

    /* ── Tooltip help icon ── */
    .ga-help {
        display: inline-block;
        width: 14px; height: 14px;
        background: #3c3c3f;
        color: #9aa0a6;
        border-radius: 50%;
        font-size: 0.65rem;
        text-align: center;
        line-height: 14px;
        cursor: default;
        margin-left: 4px;
        vertical-align: middle;
        font-weight: 700;
    }

    /* ── Phase 2 info box ── */
    .p2-info {
        background: #1a2535;
        border: 1px solid #1a73e8;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.82rem;
        color: #8ab4f8;
        margin-bottom: 20px;
        line-height: 1.5;
    }

    /* ── Export button row ── */
    .export-row {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    /* ── Divider ── */
    hr { border-color: #3c3c3f !important; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDeployButton"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }

    /* ── Sidebar expand button (fallback for auto-collapse on narrow screens) ── */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        position: fixed !important;
        top: 70px !important;
        left: 0 !important;
        z-index: 999999 !important;
        background: #1a73e8 !important;
        border: none !important;
        border-radius: 0 6px 6px 0 !important;
        padding: 10px 8px !important;
        color: #ffffff !important;
        cursor: pointer !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1c1c1e; }
    ::-webkit-scrollbar-thumb { background: #3c3c3f; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_session_state():
    defaults = {
        "api_key": "",
        "simulation_done": False,
        "transcript_lines": [],
        "insights": {},
        "auth": {},
        "focus_guide": "",
        "next_steps": [],
        "phase2_messages": [],
        "saved_panels": {},
        "custom_panel": None,
        "panel_mode": "library",
        "selected_personas": [],
        "pitch": "",
        "selected_priorities": [],
        "raw_transcript": "",
        "insights_text": "",
        "active_tab": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_personas():
    path = os.path.join(os.path.dirname(__file__), "personas.json")
    with open(path, "r") as f:
        return json.load(f)


def get_client():
    key = st.session_state.get("api_key", "").strip()
    if not key:
        return None
    return OpenAI(api_key=key)


# ─────────────────────────────────────────────
# LLM CALLS
# ─────────────────────────────────────────────
def generate_custom_panel(client, description):
    prompt = f"""You are a consumer research expert. Create exactly 4 diverse consumer personas for this target market: "{description}"

Return ONLY a JSON object with key "personas" containing an array of 4 objects, each with:
- name, age_group, location_type, income_bracket, core_values (array), communication_style, icon (emoji), background, rating_style (Very Tough/Tough/Balanced/Generous)

Make them diverse in age, income, background, and values."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9,
    )
    parsed = json.loads(resp.choices[0].message.content.strip())
    if isinstance(parsed, list):
        return parsed
    for v in parsed.values():
        if isinstance(v, list):
            return v
    return []


def generate_simulation(client, pitch, personas, priorities):
    priority_str = ", ".join(priorities) if priorities else "general consumer value"
    persona_block = "\n".join([
        f"- {p['icon']} {p['name']} ({p['age_group']}, {p['location_type']}, {p['income_bracket']}): "
        f"{p['communication_style']} Rating style: {p.get('rating_style','Balanced')}."
        for p in personas
    ])
    system = f"""Simulate a realistic, unscripted consumer focus group with {len(personas)} participants.

PARTICIPANTS:
{persona_block}

RULES:
1. Generate exactly 30-35 total exchanges. Each = one participant speaking.
2. NO moderator. Participants speak freely and react to each other.
3. MANDATORY: At least 2 participants openly disagree with another.
4. MANDATORY: At least 2 express genuine skepticism or concern.
5. MANDATORY: Each participant speaks at least 4 times.
6. Very Tough/Tough personas are harder to please. Generous personas are more open.
7. 2-4 sentences per response. No speeches.
8. Naturally explore: {priority_str}
9. Reflect each persona's background in what they focus on.
10. NO groupthink.

FORMAT (every line):
[NAME]: [message]

Start immediately. No intro text."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"PITCH:\n{pitch}\n\nBegin the discussion."}],
        temperature=0.85,
        max_tokens=3500,
    )
    return resp.choices[0].message.content.strip()


def generate_insights(client, pitch, transcript, personas, priorities):
    priority_str = ", ".join(priorities) if priorities else "overall consumer value"
    names = [p["name"] for p in personas]
    system = "You are a senior consumer insights analyst. Return structured data in the EXACT format. No commentary."
    user = f"""PITCH: {pitch}
TRANSCRIPT:
{transcript}
PRIORITY DIMENSIONS: {priority_str}
PERSONAS: {json.dumps([{"name": p["name"], "rating_style": p.get("rating_style","Balanced")} for p in personas])}

EXACT FORMAT:
ADOPTION_SCORE: [0-100]
SENTIMENT_BREAKDOWN: [Positive X% / Neutral X% / Negative X%]
TOP_PAIN_POINTS:
- [pain point 1]
- [pain point 2]
- [pain point 3]
TOP_STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]
KEY_OBJECTIONS:
- [objection 1]
- [objection 2]
PRIORITY_SCORES:
{chr(10).join([f"- {p}: [0-100]" for p in (priorities if priorities else ["Overall Value"])])}
PERSONA_HONESTY:
{chr(10).join([f"- {n}: [0-100]" for n in names])}
OVERALL_VERDICT: [1-2 sentence summary]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3, max_tokens=1200,
    )
    return resp.choices[0].message.content.strip()


def check_authenticity(client, pitch, transcript):
    system = "You are a focus group quality auditor. Return EXACT format only."
    user = f"""PITCH: {pitch}
TRANSCRIPT:
{transcript}

AUTHENTICITY_SCORE: [0-100]
GROUPTHINK_DETECTED: [Yes/No]
GROUPTHINK_NOTES: [brief or "None"]
OUTLIER_VOICES:
- [name or "None"]
CORPORATE_SYCOPHANCY_RISK: [Low/Medium/High]
FILTER_VERDICT: [1-2 sentences]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2, max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def generate_focus_guide(client, pitch, transcript, insights_text):
    system = "You are a qualitative research consultant. Write a practical human focus group guide."
    user = f"""PITCH: {pitch}
INSIGHTS: {insights_text}
TRANSCRIPT EXCERPT: {transcript[:2000]}

Write a Human Focus Group Guide with:
1. RESEARCH OBJECTIVES (3 points)
2. SCREENING CRITERIA (4-5 criteria)
3. WARM-UP QUESTIONS (2)
4. CORE DISCUSSION QUESTIONS (5-6 based on unresolved tensions)
5. PROBING FOLLOW-UPS (3)
6. CLOSING EXERCISE (1 activity)"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.5, max_tokens=1000,
    )
    return resp.choices[0].message.content.strip()


def generate_next_steps(client, pitch, insights_text, personas):
    system = "You are a consumer research strategist."
    user = f"""PITCH: {pitch}
FINDINGS: {insights_text}
CURRENT PANEL: {json.dumps([{"name": p["name"], "age_group": p["age_group"]} for p in personas])}

Recommend exactly 3 follow-up research populations:

PANEL_1_TITLE: [name]
PANEL_1_RATIONALE: [1-2 sentences]
PANEL_1_PROFILE: [age, location, income, trait]

PANEL_2_TITLE: [name]
PANEL_2_RATIONALE: [1-2 sentences]
PANEL_2_PROFILE: [age, location, income, trait]

PANEL_3_TITLE: [name]
PANEL_3_RATIONALE: [1-2 sentences]
PANEL_3_PROFILE: [age, location, income, trait]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.6, max_tokens=700,
    )
    return resp.choices[0].message.content.strip()


def generate_followup(client, pitch, original_transcript, personas, phase2_history, user_question):
    persona_block = "\n".join([f"- {p['icon']} {p['name']} ({p['age_group']}): {p['communication_style']}" for p in personas])
    history_block = "\n".join([
        f"{'Moderator' if m['role'] == 'user' else m.get('speaker','Panel')}: {m['content']}"
        for m in phase2_history[-10:]
    ])
    system = f"""You are simulating a follow-up Q&A with focus group participants.

ORIGINAL PITCH: {pitch}
PARTICIPANTS:
{persona_block}

RULES:
1. Select 2-3 most relevant participants to respond.
2. If question names a specific participant, ONLY that person responds.
3. 2-3 sentences each. Conversational.
4. Participants may reference what was said in the original session.
5. Maintain each persona's voice and values.

FORMAT:
[NAME]: [response]

Only participant responses. No narration."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"ORIGINAL TRANSCRIPT:\n{original_transcript}\n\nCONVERSATION SO FAR:\n{history_block}\n\nMODERATOR: {user_question}"},
        ],
        temperature=0.8, max_tokens=600,
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────
# PARSERS
# ─────────────────────────────────────────────
def parse_transcript(text, personas):
    lines = []
    persona_map = {p["name"].lower(): p for p in personas}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\[?([^\]:\n]+)\]?:\s*(.+)$", line)
        if m:
            speaker = m.group(1).strip()
            message = m.group(2).strip()
            persona = None
            for key, p in persona_map.items():
                if key in speaker.lower() or speaker.lower() in key:
                    persona = p
                    break
            lines.append({"speaker": speaker, "message": message, "persona": persona})
    return lines


def parse_insights(text):
    result = {}

    def extract(pattern, default="N/A"):
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    result["adoption_score"] = extract(r"ADOPTION_SCORE:\s*(\d+)")
    result["sentiment"] = extract(r"SENTIMENT_BREAKDOWN:\s*(.+?)(?:\n|$)")
    result["verdict"] = extract(r"OVERALL_VERDICT:\s*(.+?)(?:\n[A-Z_]+:|$)")

    for key, pattern in [
        ("pain_points", r"TOP_PAIN_POINTS:\s*((?:- .+\n?)+)"),
        ("strengths",   r"TOP_STRENGTHS:\s*((?:- .+\n?)+)"),
        ("objections",  r"KEY_OBJECTIONS:\s*((?:- .+\n?)+)"),
    ]:
        block = extract(pattern, "")
        result[key] = [l.lstrip("- ").strip() for l in block.strip().split("\n") if l.strip().startswith("-")]

    priority_block = extract(r"PRIORITY_SCORES:\s*((?:- .+\n?)+)", "")
    result["priority_scores"] = {}
    for line in priority_block.strip().split("\n"):
        mm = re.match(r"-\s*(.+?):\s*(\d+)", line)
        if mm:
            result["priority_scores"][mm.group(1).strip()] = int(mm.group(2))

    honesty_block = extract(r"PERSONA_HONESTY:\s*((?:- .+\n?)+)", "")
    result["honesty_scores"] = {}
    for line in honesty_block.strip().split("\n"):
        mm = re.match(r"-\s*(.+?):\s*(\d+)", line)
        if mm:
            result["honesty_scores"][mm.group(1).strip()] = int(mm.group(2))

    return result


def parse_authenticity(text):
    result = {}

    def extract(pattern, default="N/A"):
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    result["score"]            = extract(r"AUTHENTICITY_SCORE:\s*(\d+)")
    result["groupthink"]       = extract(r"GROUPTHINK_DETECTED:\s*(.+?)(?:\n|$)")
    result["groupthink_notes"] = extract(r"GROUPTHINK_NOTES:\s*(.+?)(?:\n|$)")
    result["sycophancy_risk"]  = extract(r"CORPORATE_SYCOPHANCY_RISK:\s*(.+?)(?:\n|$)")
    result["verdict"]          = extract(r"FILTER_VERDICT:\s*(.+?)(?:\n[A-Z_]+:|$)")

    outlier_block = extract(r"OUTLIER_VOICES:\s*((?:- .+\n?)+)", "")
    result["outliers"] = [l.lstrip("- ").strip() for l in outlier_block.strip().split("\n") if l.strip().startswith("-")]

    return result


def parse_next_steps(text):
    steps = []
    for i in range(1, 4):
        tm = re.search(rf"PANEL_{i}_TITLE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        rm = re.search(rf"PANEL_{i}_RATIONALE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        pm = re.search(rf"PANEL_{i}_PROFILE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if tm:
            steps.append({
                "title": tm.group(1).strip(),
                "rationale": rm.group(1).strip() if rm else "",
                "profile": pm.group(1).strip() if pm else "",
            })
    return steps


# ─────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────
def bar_html(value, color_class="ga-bar-fill"):
    pct = min(max(int(value), 0), 100)
    if color_class == "auto":
        if pct >= 60:
            color_class = "ga-bar-fill-green"
        elif pct >= 40:
            color_class = "ga-bar-fill"
        elif pct >= 25:
            color_class = "ga-bar-fill-warn"
        else:
            color_class = "ga-bar-fill-danger"
    return f'<div class="ga-bar-track"><div class="{color_class}" style="width:{pct}%"></div></div>'


def honesty_chip(score):
    if score >= 75:
        return f'<span class="honesty-chip hc-high">{score}</span>'
    elif score >= 50:
        return f'<span class="honesty-chip hc-mid">{score}</span>'
    else:
        return f'<span class="honesty-chip hc-low">{score}</span>'


def verdict_badge(adoption):
    try:
        a = int(adoption)
    except Exception:
        return '<span class="verdict-badge verdict-yellow">—</span>'
    if a >= 75:
        return f'<span class="verdict-badge verdict-green">🟢 Strong Buy Signal</span>'
    elif a >= 55:
        return f'<span class="verdict-badge verdict-yellow">🟡 Conditional Interest</span>'
    elif a >= 35:
        return f'<span class="verdict-badge verdict-orange">🟠 Skeptical — Needs Work</span>'
    else:
        return f'<span class="verdict-badge verdict-red">🔴 Significant Resistance</span>'


def scorecard_delta(value):
    try:
        v = int(value)
    except Exception:
        return ""
    if v >= 70:
        return f'<div class="ga-scorecard-delta delta-green">▲ Above threshold</div>'
    elif v >= 45:
        return f'<div class="ga-scorecard-delta delta-yellow">◆ Borderline</div>'
    else:
        return f'<div class="ga-scorecard-delta delta-red">▼ Below threshold</div>'


def build_export_txt(pitch, personas, priorities, transcript_lines, insights_text, auth, next_steps, phase2_messages):
    lines = [
        "=" * 60,
        "SIMGROUPAI — FULL SIMULATION REPORT",
        "=" * 60,
        f"\nPITCH:\n{pitch}",
        f"\nPANEL: {', '.join([p['name'] for p in personas])}",
        f"\nPRIORITIES: {', '.join(priorities) if priorities else 'None specified'}",
        "\n" + "=" * 60,
        "PHASE 1 — TRANSCRIPT",
        "=" * 60,
    ]
    for item in transcript_lines:
        lines.append(f"\n{item['speaker']}: {item['message']}")

    lines += [
        "\n\n" + "=" * 60,
        "PHASE 1 — INSIGHTS",
        "=" * 60,
        insights_text,
        "\n\n" + "=" * 60,
        "PHASE 1 — AUTHENTICITY FILTER",
        "=" * 60,
        f"Score: {auth.get('score')} | Groupthink: {auth.get('groupthink')} | Sycophancy Risk: {auth.get('sycophancy_risk')}",
        f"Verdict: {auth.get('verdict')}",
    ]

    if next_steps:
        lines += ["\n\n" + "=" * 60, "RECOMMENDED NEXT STEPS", "=" * 60]
        for i, s in enumerate(next_steps, 1):
            lines.append(f"\n{i}. {s['title']}\n   {s['rationale']}\n   Target: {s['profile']}")

    if phase2_messages:
        lines += ["\n\n" + "=" * 60, "PHASE 2 — FOLLOW-UP CONVERSATION", "=" * 60]
        for msg in phase2_messages:
            if msg["role"] == "user":
                lines.append(f"\nMODERATOR: {msg['content']}")
            else:
                for line in msg["content"].strip().split("\n"):
                    line = line.strip()
                    if line:
                        lines.append(f"\n{line}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(all_personas):
    with st.sidebar:
        st.markdown("### 🧠 SimGroupAI")
        st.markdown("---")

        st.markdown("**API Key**")
        key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-...",
            label_visibility="collapsed",
        )
        if key_input:
            st.session_state.api_key = key_input

        st.markdown("---")
        st.markdown("**Panel**")

        panel_mode = st.radio(
            "Panel type",
            ["Default Library", "Custom AI Panel"],
            index=0 if st.session_state.panel_mode == "library" else 1,
            label_visibility="collapsed",
        )
        st.session_state.panel_mode = "library" if panel_mode == "Default Library" else "custom"

        selected_personas = []

        if st.session_state.panel_mode == "library":
            for p in all_personas:
                if st.checkbox(f"{p['icon']} {p['name']} · {p['age_group']}", value=True, key=f"persona_{p['name']}"):
                    selected_personas.append(p)

            if len(selected_personas) >= 2:
                with st.expander("💾 Save this panel"):
                    pname = st.text_input("Name", placeholder="e.g. Skeptics", key="save_pname")
                    if st.button("Save") and pname:
                        st.session_state.saved_panels[pname] = list(selected_personas)
                        st.success(f"Saved: {pname}")

            if st.session_state.saved_panels:
                with st.expander("📂 Load saved panel"):
                    sname = st.selectbox("Panel", list(st.session_state.saved_panels.keys()))
                    if st.button("Load"):
                        st.session_state.custom_panel = st.session_state.saved_panels[sname]
                        st.session_state.panel_mode = "custom"
                        st.rerun()

        else:
            if st.session_state.custom_panel:
                for p in st.session_state.custom_panel:
                    st.markdown(f"{p['icon']} **{p['name']}** · {p['age_group']}")
                selected_personas = st.session_state.custom_panel
                if st.button("✕ Clear panel"):
                    st.session_state.custom_panel = None
                    st.session_state.panel_mode = "library"
                    st.rerun()
            else:
                audience_desc = st.text_area(
                    "Describe target audience",
                    placeholder="e.g. Health-conscious millennials in urban areas...",
                    height=90,
                    label_visibility="collapsed",
                    key="audience_desc",
                )
                if st.button("⚡ Generate Panel"):
                    client = get_client()
                    if not client:
                        st.error("Enter API key first.")
                    elif not audience_desc.strip():
                        st.warning("Describe your audience.")
                    else:
                        with st.spinner("Building panel..."):
                            try:
                                ps = generate_custom_panel(client, audience_desc)
                                st.session_state.custom_panel = ps
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**Priorities**")
        st.caption("What matters most for this product:")
        selected_priorities = [p for p in PRIORITIES if st.checkbox(p, value=False, key=f"prio_{p}")]
        custom_p = st.text_input("Custom priority", placeholder="e.g. Gamification", key="custom_prio")
        if custom_p.strip():
            selected_priorities.append(custom_p.strip())

        return selected_personas, selected_priorities


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    init_session_state()
    inject_css()

    # Top nav bar
    st.markdown("""
    <div class="ga-topbar">
        <div class="ga-logo">
            <span class="ga-logo-dot"></span>SimGroupAI
        </div>
        <div class="ga-property">Consumer Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    all_personas = load_personas()
    selected_personas, selected_priorities = render_sidebar(all_personas)

    # Pitch input
    pitch = st.text_area(
        "Product or Service Pitch",
        placeholder='Describe your product or service concisely. e.g. "WealthMind is a personal finance AI that builds custom savings plans — no spreadsheets required."',
        height=100,
    )

    col_btn, col_info = st.columns([1, 5])
    with col_btn:
        run_btn = st.button("▶  Run Simulation", use_container_width=True)
    with col_info:
        if selected_personas:
            st.caption(f"{len(selected_personas)} panelists · {len(selected_priorities)} priorities selected")
        else:
            st.caption("Select at least 2 personas in the sidebar.")

    # ── Run ──
    if run_btn:
        client = get_client()
        if not client:
            st.error("Enter your OpenAI API key in the sidebar.")
        elif not pitch.strip():
            st.warning("Enter a pitch first.")
        elif len(selected_personas) < 2:
            st.warning("Select at least 2 personas.")
        else:
            st.session_state.simulation_done = False
            st.session_state.phase2_messages = []
            st.session_state.active_tab = 0

            prog = st.progress(0, text="Initializing...")
            try:
                prog.progress(10, text="🗣  Generating transcript...")
                raw = generate_simulation(client, pitch, selected_personas, selected_priorities)
                st.session_state.transcript_lines = parse_transcript(raw, selected_personas)
                st.session_state.raw_transcript = raw

                prog.progress(35, text="📊  Extracting insights...")
                it = generate_insights(client, pitch, raw, selected_personas, selected_priorities)
                st.session_state.insights = parse_insights(it)
                st.session_state.insights_text = it

                prog.progress(60, text="🔍  Authenticity filter...")
                at = check_authenticity(client, pitch, raw)
                st.session_state.auth = parse_authenticity(at)

                prog.progress(75, text="🗺  Building focus guide...")
                st.session_state.focus_guide = generate_focus_guide(client, pitch, raw, it)

                prog.progress(88, text="🔭  Next-step recommendations...")
                nst = generate_next_steps(client, pitch, it, selected_personas)
                st.session_state.next_steps = parse_next_steps(nst)

                prog.progress(100, text="✅  Done.")
                st.session_state.simulation_done = True
                st.session_state.selected_personas = selected_personas
                st.session_state.pitch = pitch
                st.session_state.selected_priorities = selected_priorities

            except Exception as e:
                prog.empty()
                st.error(f"Error: {e}")

    # ── Results ──
    if st.session_state.simulation_done:
        insights   = st.session_state.insights
        auth       = st.session_state.auth
        personas   = st.session_state.selected_personas
        priorities = st.session_state.selected_priorities
        honesty    = insights.get("honesty_scores", {})

        # ── Scorecard row ──
        adoption   = insights.get("adoption_score", "—")
        auth_score = auth.get("score", "—")
        sentiment  = insights.get("sentiment", "—")

        st.markdown(f"""
        <div class="ga-scorecard-row">
            <div class="ga-scorecard">
                <div class="ga-scorecard-label">Adoption Score</div>
                <div class="ga-scorecard-value">{adoption}<span style="font-size:1rem;color:#5f6368">/100</span></div>
                {scorecard_delta(adoption)}
            </div>
            <div class="ga-scorecard">
                <div class="ga-scorecard-label">Authenticity Score</div>
                <div class="ga-scorecard-value">{auth_score}<span style="font-size:1rem;color:#5f6368">/100</span></div>
                {scorecard_delta(auth_score)}
            </div>
            <div class="ga-scorecard">
                <div class="ga-scorecard-label">Sentiment</div>
                <div style="font-size:0.88rem;color:#bdc1c6;margin-top:6px;line-height:1.4;">{sentiment}</div>
            </div>
            <div class="ga-scorecard" style="flex:2">
                <div class="ga-scorecard-label">Verdict</div>
                <div style="margin-top:6px;">{verdict_badge(adoption)}</div>
                <div style="font-size:0.78rem;color:#9aa0a6;margin-top:6px;line-height:1.4;">{insights.get("verdict","")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabs ──
        tab1, tab2 = st.tabs(["📊  Phase 1 — Results", "💬  Phase 2 — Follow-Up"])

        # ════════════════════════════════════
        # PHASE 1
        # ════════════════════════════════════
        with tab1:

            # Export row at top
            st.markdown('<div class="ga-section-title">Export</div>', unsafe_allow_html=True)
            exp_col1, exp_col2, _ = st.columns([1, 1, 4])
            with exp_col1:
                st.download_button(
                    "⬇  Full Report (.txt)",
                    data=build_export_txt(
                        st.session_state.pitch, personas, priorities,
                        st.session_state.transcript_lines, st.session_state.insights_text,
                        auth, st.session_state.next_steps, st.session_state.phase2_messages
                    ),
                    file_name="simgroup_report.txt",
                    mime="text/plain",
                    key="dl_full_top",
                )
            with exp_col2:
                st.download_button(
                    "⬇  Focus Guide (.txt)",
                    data=st.session_state.focus_guide,
                    file_name="simgroup_focus_guide.txt",
                    mime="text/plain",
                    key="dl_guide_top",
                )

            # ── Dashboard ──
            col_left, col_right = st.columns(2)

            with col_left:
                # Adoption & Authenticity bars
                st.markdown('<div class="ga-section-title">Scores</div>', unsafe_allow_html=True)
                for label, val, tip in [
                    ("Adoption Score", adoption, None),
                    ("Authenticity Score", auth_score, None),
                ]:
                    try:
                        v = int(val)
                    except Exception:
                        v = 0
                    st.markdown(f"""
                    <div class="ga-bar-row">
                        <div class="ga-bar-label-row"><span>{label}</span><span style="color:#8ab4f8;font-weight:500">{v}</span></div>
                        {bar_html(v, "auto")}
                    </div>
                    """, unsafe_allow_html=True)

                # Priority scores
                priority_scores = insights.get("priority_scores", {})
                if priority_scores:
                    st.markdown(
                        '<div class="ga-section-title">Priority Dimension Scores'
                        ' <span class="ga-help" title="How strongly the panel reacted to each priority you selected, scored 0–100. Higher = more discussed and validated.">?</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    for dim, score in priority_scores.items():
                        st.markdown(f"""
                        <div class="ga-bar-row">
                            <div class="ga-bar-label-row"><span>{dim}</span><span style="color:#8ab4f8;font-weight:500">{score}</span></div>
                            {bar_html(score, "auto")}
                        </div>
                        """, unsafe_allow_html=True)

                # Honesty scores directly below priority scores
                if honesty:
                    st.markdown('<div class="ga-section-title">Persona Honesty Scores</div>', unsafe_allow_html=True)
                    for name, score in honesty.items():
                        p_obj = next((p for p in personas if p["name"] == name), None)
                        icon = p_obj["icon"] if p_obj else "👤"
                        st.markdown(f"""
                        <div class="ga-bar-row">
                            <div class="ga-bar-label-row">
                                <span>{icon} {name}</span>
                                {honesty_chip(score)}
                            </div>
                            {bar_html(score, "auto")}
                        </div>
                        """, unsafe_allow_html=True)

            with col_right:
                st.markdown('<div class="ga-section-title">Key Findings</div>', unsafe_allow_html=True)

                pain_points = insights.get("pain_points", [])
                if pain_points:
                    st.markdown('<div style="font-size:0.72rem;font-weight:500;color:#9aa0a6;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:6px;">Pain Points</div>', unsafe_allow_html=True)
                    for pt in pain_points:
                        st.markdown(f'<div class="ga-finding-row"><div class="ga-finding-dot dot-red"></div><span>{pt}</span></div>', unsafe_allow_html=True)

                strengths = insights.get("strengths", [])
                if strengths:
                    st.markdown('<div style="font-size:0.72rem;font-weight:500;color:#9aa0a6;text-transform:uppercase;letter-spacing:0.7px;margin:14px 0 6px;">Strengths</div>', unsafe_allow_html=True)
                    for s in strengths:
                        st.markdown(f'<div class="ga-finding-row"><div class="ga-finding-dot dot-green"></div><span>{s}</span></div>', unsafe_allow_html=True)

                objections = insights.get("objections", [])
                if objections:
                    st.markdown('<div style="font-size:0.72rem;font-weight:500;color:#9aa0a6;text-transform:uppercase;letter-spacing:0.7px;margin:14px 0 6px;">Key Objections</div>', unsafe_allow_html=True)
                    for obj in objections:
                        st.markdown(f'<div class="ga-finding-row"><div class="ga-finding-dot dot-yellow"></div><span>{obj}</span></div>', unsafe_allow_html=True)

                # Authenticity notes
                gnotes = auth.get("groupthink_notes", "")
                if gnotes and gnotes.lower() not in ("none", "n/a", ""):
                    st.markdown(f"""
                    <div style="margin-top:16px;padding:10px 14px;background:#3a2810;border:1px solid #f57c00;border-radius:6px;font-size:0.8rem;color:#ffb74d;line-height:1.45;">
                    ⚠ <strong>Groupthink Note:</strong> {gnotes}
                    </div>
                    """, unsafe_allow_html=True)

            # ── Next Steps ── (above transcript)
            if st.session_state.next_steps:
                st.markdown('<div class="ga-section-title">Recommended Next Research Steps</div>', unsafe_allow_html=True)
                ns_cols = st.columns(len(st.session_state.next_steps))
                for i, (col, step) in enumerate(zip(ns_cols, st.session_state.next_steps)):
                    with col:
                        st.markdown(f"""
                        <div class="ns-card">
                            <div class="ns-title">→ {step["title"]}</div>
                            <div class="ns-body">{step["rationale"]}</div>
                            <div class="ns-profile">Target: {step["profile"]}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # ── Transcript ──
            st.markdown('<div class="ga-section-title">Focus Group Transcript</div>', unsafe_allow_html=True)
            for item in st.session_state.transcript_lines:
                speaker = item["speaker"]
                message = item["message"]
                persona = item.get("persona")
                icon = persona["icon"] if persona else "👤"
                hs = honesty.get(speaker, None)
                chip = honesty_chip(hs) if hs is not None else ""
                st.markdown(f"""
                <div class="tx-bubble">
                    <div class="tx-name">{icon} {speaker}{chip}</div>
                    {message}
                </div>
                """, unsafe_allow_html=True)

        # ════════════════════════════════════
        # PHASE 2
        # ════════════════════════════════════
        with tab2:

            # Export row at top of Phase 2
            st.markdown('<div class="ga-section-title">Export</div>', unsafe_allow_html=True)
            p2_exp_col, _ = st.columns([1, 5])
            with p2_exp_col:
                st.download_button(
                    "⬇  Full Report (.txt)",
                    data=build_export_txt(
                        st.session_state.pitch, personas, priorities,
                        st.session_state.transcript_lines, st.session_state.insights_text,
                        auth, st.session_state.next_steps, st.session_state.phase2_messages
                    ),
                    file_name="simgroup_report_with_followup.txt",
                    mime="text/plain",
                    key="dl_full_p2",
                )

            st.markdown("""
            <div class="p2-info">
                💬 <strong>Phase 2 — Follow-Up Q&A</strong><br>
                Ask follow-up questions directly to the panelists. Address the group or call out a specific participant by name.
            </div>
            """, unsafe_allow_html=True)

            # Conversation history
            for msg in st.session_state.phase2_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="tx-bubble tx-bubble-user">
                        <div class="tx-name tx-name-user">🎤 You (Moderator)</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    for line in msg["content"].strip().split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        mm = re.match(r"^\[?([^\]:\n]+)\]?:\s*(.+)$", line)
                        if mm:
                            speaker = mm.group(1).strip()
                            text    = mm.group(2).strip()
                            p_obj   = next((p for p in personas if p["name"].lower() in speaker.lower()), None)
                            icon    = p_obj["icon"] if p_obj else "👤"
                            hs      = honesty.get(speaker, None)
                            chip    = honesty_chip(hs) if hs is not None else ""
                            st.markdown(f"""
                            <div class="tx-bubble">
                                <div class="tx-name">{icon} {speaker}{chip}</div>
                                {text}
                            </div>
                            """, unsafe_allow_html=True)

            # Input — use regular button (not st.form) to avoid tab reset
            user_q = st.text_input(
                "Ask a follow-up",
                placeholder='e.g. "What would make you actually buy this?" or "Robert, what\'s your biggest concern?"',
                key="phase2_input",
                label_visibility="collapsed",
            )
            send_btn = st.button("Send →", key="phase2_send")

            if send_btn and user_q.strip():
                client = get_client()
                if not client:
                    st.error("API key required.")
                else:
                    st.session_state.phase2_messages.append({"role": "user", "content": user_q})
                    st.session_state.active_tab = 1
                    with st.spinner("Panelists responding..."):
                        try:
                            response = generate_followup(
                                client,
                                st.session_state.pitch,
                                st.session_state.raw_transcript,
                                personas,
                                st.session_state.phase2_messages,
                                user_q,
                            )
                            st.session_state.phase2_messages.append({
                                "role": "assistant",
                                "speaker": "panel",
                                "content": response,
                            })
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.rerun()

    else:
        # Empty state
        st.markdown("""
        <div style="text-align:center;padding:70px 20px;">
            <div style="font-size:2.5rem;margin-bottom:14px;">🧬</div>
            <div style="font-size:1rem;font-weight:500;color:#5f6368;margin-bottom:8px;">No simulation running</div>
            <div style="font-size:0.84rem;color:#3c3c3f;">Enter your pitch above and click <strong style="color:#8ab4f8">Run Simulation</strong></div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
