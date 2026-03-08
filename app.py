import streamlit as st
import json
import re
import os
from openai import OpenAI

# ─────────────────────────────────────────────
# CONFIG
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
# CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0a1628;
        color: #e8edf5;
    }

    section[data-testid="stSidebar"] {
        background: #0f1e35 !important;
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] * {
        color: #c8d6e8 !important;
    }

    .simgroup-header {
        background: linear-gradient(135deg, #0d2040 0%, #162038 100%);
        border-bottom: 2px solid #1e4d7b;
        padding: 20px 32px 16px;
        margin: -1rem -1rem 2rem -1rem;
    }
    .simgroup-logo {
        font-size: 1.7rem;
        font-weight: 700;
        color: #4ecdc4;
        letter-spacing: -0.5px;
    }
    .simgroup-tagline {
        font-size: 0.82rem;
        color: #7a9bbf;
        margin-top: 2px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .summary-bar {
        background: #0f1e35;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 32px;
        flex-wrap: wrap;
    }
    .summary-metric {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 90px;
    }
    .summary-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4ecdc4;
        line-height: 1.1;
    }
    .summary-metric-label {
        font-size: 0.7rem;
        color: #7a9bbf;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-top: 2px;
    }
    .summary-badge {
        background: #162038;
        border: 1px solid #4ecdc4;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.82rem;
        color: #4ecdc4;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .summary-divider {
        width: 1px;
        height: 40px;
        background: #1e3a5f;
    }

    .metric-card {
        background: #0f1e35;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 12px;
    }
    .metric-card-label {
        font-size: 0.72rem;
        color: #7a9bbf;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .metric-card-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4ecdc4;
        line-height: 1;
    }
    .metric-card-sub {
        font-size: 0.78rem;
        color: #5a7a9a;
        margin-top: 4px;
    }

    .progress-container {
        background: #162038;
        border-radius: 4px;
        height: 6px;
        margin-top: 8px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #4ecdc4, #45b7d1);
    }
    .progress-fill-warn {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #f7971e, #ffd200);
    }
    .progress-fill-danger {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #f44336, #e91e63);
    }

    .chat-bubble {
        padding: 12px 16px;
        border-radius: 10px;
        margin: 6px 0;
        font-size: 0.92rem;
        line-height: 1.55;
        border-left: 3px solid #4ecdc4;
        background: #0f1e35;
        color: #d0dff0;
    }
    .chat-bubble-user {
        border-left-color: #f7971e;
        background: #141e2e;
    }
    .chat-name {
        font-size: 0.75rem;
        font-weight: 600;
        color: #4ecdc4;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .chat-name-user {
        color: #f7971e;
    }

    .honesty-badge {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 600;
        margin-left: 8px;
    }
    .honesty-high { background: #1a3a2a; color: #4ecdc4; }
    .honesty-mid  { background: #2a2a1a; color: #f7c948; }
    .honesty-low  { background: #3a1a1a; color: #f77a48; }

    .tag {
        display: inline-block;
        background: #162038;
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 3px 10px;
        font-size: 0.75rem;
        color: #7a9bbf;
        margin: 2px;
    }

    .section-header {
        font-size: 0.72rem;
        font-weight: 600;
        color: #7a9bbf;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #1e3a5f;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4ecdc4, #45b7d1) !important;
        color: #0a1628 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px !important;
    }

    .stTextArea textarea, .stTextInput input {
        background: #0f1e35 !important;
        border: 1px solid #1e3a5f !important;
        color: #e8edf5 !important;
        border-radius: 8px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0f1e35;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #1e3a5f;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #7a9bbf !important;
        border-radius: 6px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #162038 !important;
        color: #4ecdc4 !important;
    }

    .streamlit-expanderHeader {
        background: #0f1e35 !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 8px !important;
        color: #c8d6e8 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    hr { border-color: #1e3a5f !important; }

    .next-step-card {
        background: #0f1e35;
        border: 1px solid #1e4d7b;
        border-left: 4px solid #4ecdc4;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .next-step-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #4ecdc4;
        margin-bottom: 4px;
    }
    .next-step-body {
        font-size: 0.82rem;
        color: #a0b8d0;
        line-height: 1.5;
    }
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
    prompt = f"""You are a consumer research expert. Create exactly 4 diverse consumer personas tailored to this target market:

"{description}"

Return ONLY valid JSON — a single JSON object with key "personas" containing an array of 4 objects. Each object must have:
- name (string)
- age_group (string, e.g. "Millennial (32)")
- location_type (string: Urban / Suburban / Rural)
- income_bracket (string, e.g. "Middle ($60k-$80k)")
- core_values (array of 3-4 strings)
- communication_style (string, 2-3 sentences)
- icon (single emoji)
- background (string, 1-2 sentence bio)
- rating_style (one of: "Very Tough", "Tough", "Balanced", "Generous")

Make them genuinely diverse in age, background, income, and values."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9,
    )
    raw = resp.choices[0].message.content.strip()
    parsed = json.loads(raw)
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

    system = f"""You are simulating a realistic, unscripted consumer focus group with {len(personas)} distinct participants.

PARTICIPANTS:
{persona_block}

SIMULATION RULES:
1. Generate exactly 30-35 total exchanges. Each exchange = one participant speaking.
2. NO moderator. Participants speak freely and react to each other naturally.
3. MANDATORY: At least 2 participants must openly disagree with another participant.
4. MANDATORY: At least 2 participants must express genuine skepticism or a concern.
5. MANDATORY: Each participant speaks at least 4 times.
6. "Very Tough" and "Tough" rating style personas are harder to please and more critical.
7. "Generous" rating style personas are more open and enthusiastic.
8. Keep each response 2-4 sentences. No speeches.
9. The group naturally explores: {priority_str}
10. Reflect each persona's background and values in what they focus on.
11. NO groupthink. The conversation should be contentious at times.

FORMAT — use exactly this for every line:
[NAME]: [message]

Start immediately with the first participant. No intro text."""

    user = f"PRODUCT/SERVICE PITCH:\n{pitch}\n\nBegin the focus group discussion now."

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.85,
        max_tokens=3500,
    )
    return resp.choices[0].message.content.strip()


def generate_insights(client, pitch, transcript, personas, priorities):
    priority_str = ", ".join(priorities) if priorities else "overall consumer value"
    persona_names = [p["name"] for p in personas]

    system = "You are a senior consumer insights analyst. Return structured data in the EXACT format specified. No extra commentary."

    user = f"""PITCH: {pitch}

TRANSCRIPT:
{transcript}

PRIORITY DIMENSIONS: {priority_str}

PERSONAS:
{json.dumps([{"name": p["name"], "rating_style": p.get("rating_style","Balanced")} for p in personas], indent=2)}

Return in this EXACT format:

ADOPTION_SCORE: [0-100 integer]
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
{chr(10).join([f"- {name}: [0-100 integer]" for name in persona_names])}
OVERALL_VERDICT: [1-2 sentence summary]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=1200,
    )
    return resp.choices[0].message.content.strip()


def check_authenticity(client, pitch, transcript):
    system = "You are a focus group quality auditor. Return data in the EXACT format specified."

    user = f"""PITCH: {pitch}

TRANSCRIPT:
{transcript}

AUTHENTICITY_SCORE: [0-100]
GROUPTHINK_DETECTED: [Yes/No]
GROUPTHINK_NOTES: [brief note or "None"]
OUTLIER_VOICES:
- [name or "None"]
CORPORATE_SYCOPHANCY_RISK: [Low/Medium/High]
FILTER_VERDICT: [1-2 sentences on transcript quality]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def generate_focus_guide(client, pitch, transcript, insights_text):
    system = "You are a qualitative research consultant. Write a practical focus group guide based on AI simulation findings."

    user = f"""PITCH: {pitch}

AI SIMULATION INSIGHTS:
{insights_text}

KEY THEMES FROM TRANSCRIPT:
{transcript[:2000]}

Write a Human Focus Group Guide with:
1. RESEARCH OBJECTIVES (3 bullet points)
2. SCREENING CRITERIA (4-5 criteria)
3. WARM-UP QUESTIONS (2 questions)
4. CORE DISCUSSION QUESTIONS (5-6 questions based on unresolved tensions)
5. PROBING FOLLOW-UPS (3 probes)
6. CLOSING EXERCISE (one activity)

Keep it concise and tied to simulation findings."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.5,
        max_tokens=1000,
    )
    return resp.choices[0].message.content.strip()


def generate_next_steps(client, pitch, insights_text, personas):
    system = "You are a consumer research strategist. Recommend follow-up research populations."

    user = f"""PITCH: {pitch}

FINDINGS:
{insights_text}

CURRENT PANEL:
{json.dumps([{"name": p["name"], "age_group": p["age_group"], "income_bracket": p["income_bracket"]} for p in personas], indent=2)}

Recommend exactly 3 follow-up research populations:

PANEL_1_TITLE: [short name]
PANEL_1_RATIONALE: [1-2 sentences]
PANEL_1_PROFILE: [age range, location, income, key trait]

PANEL_2_TITLE: [short name]
PANEL_2_RATIONALE: [1-2 sentences]
PANEL_2_PROFILE: [age range, location, income, key trait]

PANEL_3_TITLE: [short name]
PANEL_3_RATIONALE: [1-2 sentences]
PANEL_3_PROFILE: [age range, location, income, key trait]"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.6,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()


def generate_followup(client, pitch, original_transcript, personas, phase2_history, user_question):
    persona_block = "\n".join([
        f"- {p['icon']} {p['name']} ({p['age_group']}): {p['communication_style']}"
        for p in personas
    ])
    history_block = "\n".join([
        f"{'Moderator' if m['role'] == 'user' else m.get('speaker','Panel')}: {m['content']}"
        for m in phase2_history[-10:]
    ])

    system = f"""You are simulating a follow-up with focus group participants who completed a prior session.

ORIGINAL PITCH: {pitch}

PARTICIPANTS:
{persona_block}

RULES:
1. Select 2-3 most relevant participants to respond.
2. If question names a specific participant, ONLY that participant responds.
3. Each response is 2-3 sentences — conversational.
4. Participants REMEMBER the original discussion and may reference it.
5. Maintain each persona's voice, values, and rating style.
6. Participants may agree or disagree with each other.

FORMAT:
[NAME]: [response]

Only output participant responses. No narration."""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"ORIGINAL TRANSCRIPT:\n{original_transcript}\n\nPHASE 2 HISTORY:\n{history_block}\n\nMODERATOR: {user_question}"},
        ],
        temperature=0.8,
        max_tokens=600,
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

    pain_block = extract(r"TOP_PAIN_POINTS:\s*((?:- .+\n?)+)", "")
    result["pain_points"] = [l.lstrip("- ").strip() for l in pain_block.strip().split("\n") if l.strip().startswith("-")]

    strength_block = extract(r"TOP_STRENGTHS:\s*((?:- .+\n?)+)", "")
    result["strengths"] = [l.lstrip("- ").strip() for l in strength_block.strip().split("\n") if l.strip().startswith("-")]

    obj_block = extract(r"KEY_OBJECTIONS:\s*((?:- .+\n?)+)", "")
    result["objections"] = [l.lstrip("- ").strip() for l in obj_block.strip().split("\n") if l.strip().startswith("-")]

    priority_block = extract(r"PRIORITY_SCORES:\s*((?:- .+\n?)+)", "")
    priority_scores = {}
    for line in priority_block.strip().split("\n"):
        mm = re.match(r"-\s*(.+?):\s*(\d+)", line)
        if mm:
            priority_scores[mm.group(1).strip()] = int(mm.group(2))
    result["priority_scores"] = priority_scores

    honesty_block = extract(r"PERSONA_HONESTY:\s*((?:- .+\n?)+)", "")
    honesty_scores = {}
    for line in honesty_block.strip().split("\n"):
        mm = re.match(r"-\s*(.+?):\s*(\d+)", line)
        if mm:
            honesty_scores[mm.group(1).strip()] = int(mm.group(2))
    result["honesty_scores"] = honesty_scores

    return result


def parse_authenticity(text):
    result = {}

    def extract(pattern, default="N/A"):
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    result["score"] = extract(r"AUTHENTICITY_SCORE:\s*(\d+)")
    result["groupthink"] = extract(r"GROUPTHINK_DETECTED:\s*(.+?)(?:\n|$)")
    result["groupthink_notes"] = extract(r"GROUPTHINK_NOTES:\s*(.+?)(?:\n|$)")
    result["sycophancy_risk"] = extract(r"CORPORATE_SYCOPHANCY_RISK:\s*(.+?)(?:\n|$)")
    result["verdict"] = extract(r"FILTER_VERDICT:\s*(.+?)(?:\n[A-Z_]+:|$)")

    outlier_block = extract(r"OUTLIER_VOICES:\s*((?:- .+\n?)+)", "")
    result["outliers"] = [l.lstrip("- ").strip() for l in outlier_block.strip().split("\n") if l.strip().startswith("-")]

    return result


def parse_next_steps(text):
    steps = []
    for i in range(1, 4):
        title_m = re.search(rf"PANEL_{i}_TITLE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        rationale_m = re.search(rf"PANEL_{i}_RATIONALE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        profile_m = re.search(rf"PANEL_{i}_PROFILE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if title_m:
            steps.append({
                "title": title_m.group(1).strip(),
                "rationale": rationale_m.group(1).strip() if rationale_m else "",
                "profile": profile_m.group(1).strip() if profile_m else "",
            })
    return steps


# ─────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────
def progress_bar_html(value, warn_threshold=50, danger_threshold=30):
    pct = min(max(int(value), 0), 100)
    if pct <= danger_threshold:
        cls = "progress-fill-danger"
    elif pct <= warn_threshold:
        cls = "progress-fill-warn"
    else:
        cls = "progress-fill"
    return f'<div class="progress-container"><div class="{cls}" style="width:{pct}%"></div></div>'


def honesty_badge_html(score):
    if score >= 75:
        return f'<span class="honesty-badge honesty-high">Candor {score}</span>'
    elif score >= 50:
        return f'<span class="honesty-badge honesty-mid">Candor {score}</span>'
    else:
        return f'<span class="honesty-badge honesty-low">Candor {score}</span>'


def render_summary_bar(insights, auth):
    adoption = insights.get("adoption_score", "—")
    auth_score = auth.get("score", "—")
    verdict = insights.get("verdict", "")

    try:
        a = int(adoption)
        if a >= 75:
            badge = "🟢 Strong Buy Signal"
        elif a >= 55:
            badge = "🟡 Conditional Interest"
        elif a >= 35:
            badge = "🟠 Skeptical — Needs Work"
        else:
            badge = "🔴 Significant Resistance"
    except Exception:
        badge = "—"

    st.markdown(f"""
    <div class="summary-bar">
        <div class="summary-metric">
            <div class="summary-metric-value">{adoption}</div>
            <div class="summary-metric-label">Adoption Score</div>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-metric">
            <div class="summary-metric-value">{auth_score}</div>
            <div class="summary-metric-label">Authenticity</div>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-badge">{badge}</div>
        <div class="summary-divider"></div>
        <div style="flex:1; font-size:0.82rem; color:#7a9bbf; line-height:1.4;">{verdict}</div>
    </div>
    """, unsafe_allow_html=True)


def render_transcript(transcript_lines, honesty_scores=None):
    st.markdown('<div class="section-header">Focus Group Transcript</div>', unsafe_allow_html=True)
    if honesty_scores is None:
        honesty_scores = {}
    for item in transcript_lines:
        speaker = item["speaker"]
        message = item["message"]
        persona = item.get("persona")
        icon = persona["icon"] if persona else "👤"
        hs = honesty_scores.get(speaker, None)
        badge_html = honesty_badge_html(hs) if hs is not None else ""
        st.markdown(f"""
        <div class="chat-bubble">
            <div class="chat-name">{icon} {speaker}{badge_html}</div>
            {message}
        </div>
        """, unsafe_allow_html=True)


def render_dashboard(insights, auth, selected_personas):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Sentiment & Adoption</div>', unsafe_allow_html=True)
        adoption = insights.get("adoption_score", 0)
        try:
            adoption_int = int(adoption)
        except Exception:
            adoption_int = 0

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-label">Adoption Score</div>
            <div class="metric-card-value">{adoption_int}<span style="font-size:1rem;color:#7a9bbf">/100</span></div>
            {progress_bar_html(adoption_int)}
            <div class="metric-card-sub">{insights.get("sentiment","")}</div>
        </div>
        """, unsafe_allow_html=True)

        auth_score = auth.get("score", 0)
        try:
            auth_int = int(auth_score)
        except Exception:
            auth_int = 0

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-label">Authenticity Score</div>
            <div class="metric-card-value">{auth_int}<span style="font-size:1rem;color:#7a9bbf">/100</span></div>
            {progress_bar_html(auth_int)}
            <div class="metric-card-sub">Groupthink: {auth.get("groupthink","N/A")} · Sycophancy Risk: {auth.get("sycophancy_risk","N/A")}</div>
        </div>
        """, unsafe_allow_html=True)

        priority_scores = insights.get("priority_scores", {})
        if priority_scores:
            st.markdown('<div class="section-header">Priority Dimension Scores</div>', unsafe_allow_html=True)
            for dim, score in priority_scores.items():
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#a0b8d0;margin-bottom:3px;">
                        <span>{dim}</span><span style="color:#4ecdc4;font-weight:600">{score}</span>
                    </div>
                    {progress_bar_html(score)}
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Key Findings</div>', unsafe_allow_html=True)

        pain_points = insights.get("pain_points", [])
        if pain_points:
            st.markdown('<div style="font-size:0.75rem;color:#f77a48;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">⚠ Pain Points</div>', unsafe_allow_html=True)
            for pt in pain_points:
                st.markdown(f'<div class="tag">• {pt}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        strengths = insights.get("strengths", [])
        if strengths:
            st.markdown('<div style="font-size:0.75rem;color:#4ecdc4;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">✓ Strengths</div>', unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f'<div class="tag">• {s}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        objections = insights.get("objections", [])
        if objections:
            st.markdown('<div style="font-size:0.75rem;color:#f7c948;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">✗ Key Objections</div>', unsafe_allow_html=True)
            for obj in objections:
                st.markdown(f'<div class="tag">• {obj}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        honesty_scores = insights.get("honesty_scores", {})
        if honesty_scores:
            st.markdown('<div class="section-header">Persona Honesty Scores</div>', unsafe_allow_html=True)
            for name, score in honesty_scores.items():
                p_obj = next((p for p in selected_personas if p["name"] == name), None)
                icon = p_obj["icon"] if p_obj else "👤"
                st.markdown(f"""
                <div style="display:flex;align-items:center;margin-bottom:8px;gap:10px;">
                    <span style="font-size:1.1rem">{icon}</span>
                    <div style="flex:1">
                        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#a0b8d0;margin-bottom:2px;">
                            <span>{name}</span>{honesty_badge_html(score)}
                        </div>
                        {progress_bar_html(score)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if auth.get("groupthink_notes") and auth["groupthink_notes"].lower() not in ("none", "n/a"):
            st.markdown(f"""
            <div style="margin-top:16px;padding:12px;background:#1a1a0a;border:1px solid #3a3a1a;border-radius:8px;font-size:0.8rem;color:#d0c060;">
            ⚠ <strong>Groupthink Note:</strong> {auth["groupthink_notes"]}
            </div>
            """, unsafe_allow_html=True)


def render_next_steps(next_steps):
    st.markdown('<div class="section-header">Recommended Next Research Steps</div>', unsafe_allow_html=True)
    for step in next_steps:
        st.markdown(f"""
        <div class="next-step-card">
            <div class="next-step-title">→ {step["title"]}</div>
            <div class="next-step-body">{step["rationale"]}</div>
            <div style="margin-top:6px;font-size:0.75rem;color:#5a7a9a;"><em>Target: {step["profile"]}</em></div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(all_personas):
    with st.sidebar:
        st.markdown("### 🧠 SimGroupAI")
        st.markdown("---")

        st.markdown("**API Configuration**")
        key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="sk-...",
        )
        if key_input:
            st.session_state.api_key = key_input

        st.markdown("---")

        st.markdown("**Panel Selection**")
        panel_mode = st.radio(
            "Panel type",
            ["Default Library", "Custom AI Panel"],
            index=0 if st.session_state.panel_mode == "library" else 1,
            label_visibility="collapsed",
        )
        st.session_state.panel_mode = "library" if panel_mode == "Default Library" else "custom"

        selected_personas = []

        if st.session_state.panel_mode == "library":
            st.markdown("**Select Personas (2–6)**")
            for p in all_personas:
                checked = st.checkbox(
                    f"{p['icon']} {p['name']} — {p['age_group']}",
                    value=True,
                    key=f"persona_{p['name']}",
                )
                if checked:
                    selected_personas.append(p)

            if len(selected_personas) >= 2:
                with st.expander("💾 Save This Panel"):
                    panel_name = st.text_input("Panel name", placeholder="e.g. Skeptics Group", key="save_panel_name")
                    if st.button("Save Panel") and panel_name:
                        st.session_state.saved_panels[panel_name] = [p for p in selected_personas]
                        st.success(f"Saved: {panel_name}")

            if st.session_state.saved_panels:
                with st.expander("📂 Load Saved Panel"):
                    saved_name = st.selectbox("Select saved panel", list(st.session_state.saved_panels.keys()))
                    if st.button("Load Panel"):
                        st.session_state.custom_panel = st.session_state.saved_panels[saved_name]
                        st.session_state.panel_mode = "custom"
                        st.rerun()

        else:
            if st.session_state.custom_panel:
                st.markdown("**Custom Panel Loaded:**")
                for p in st.session_state.custom_panel:
                    st.markdown(f"{p['icon']} **{p['name']}** — {p['age_group']}")
                selected_personas = st.session_state.custom_panel
                if st.button("Clear Custom Panel"):
                    st.session_state.custom_panel = None
                    st.session_state.panel_mode = "library"
                    st.rerun()
            else:
                st.markdown("**Describe your target audience:**")
                audience_desc = st.text_area(
                    "Target audience",
                    placeholder="e.g. Tech-savvy parents in their 30s-40s, suburban, mid-to-high income, interested in smart home products",
                    height=100,
                    label_visibility="collapsed",
                    key="audience_desc",
                )
                if st.button("⚡ Generate Panel with AI"):
                    client = get_client()
                    if not client:
                        st.error("Please enter your API key first.")
                    elif not audience_desc.strip():
                        st.warning("Describe your target audience first.")
                    else:
                        with st.spinner("Generating custom panel..."):
                            try:
                                personas = generate_custom_panel(client, audience_desc)
                                st.session_state.custom_panel = personas
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        st.markdown("---")

        st.markdown("**Evaluation Priorities**")
        st.caption("Select what matters most for this product:")
        selected_priorities = []
        for p in PRIORITIES:
            if st.checkbox(p, value=False, key=f"prio_{p}"):
                selected_priorities.append(p)

        custom_priority = st.text_input(
            "Add custom priority",
            placeholder="e.g. Gamification",
            key="custom_priority_input",
        )
        if custom_priority.strip():
            selected_priorities.append(custom_priority.strip())

        return selected_personas, selected_priorities


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    init_session_state()
    inject_css()

    st.markdown("""
    <div class="simgroup-header">
        <div class="simgroup-logo">🧠 SimGroupAI</div>
        <div class="simgroup-tagline">Autonomous Consumer Intelligence · Silicon Population Research</div>
    </div>
    """, unsafe_allow_html=True)

    all_personas = load_personas()
    selected_personas, selected_priorities = render_sidebar(all_personas)

    st.markdown('<div class="section-header">Product or Service Pitch</div>', unsafe_allow_html=True)
    pitch = st.text_area(
        "Pitch",
        placeholder='Describe your product or service. e.g. "WealthMind is a personal finance AI that analyzes spending and builds a custom savings plan — no spreadsheets required."',
        height=120,
        label_visibility="collapsed",
    )

    run_col, info_col = st.columns([1, 4])
    with run_col:
        run_btn = st.button("▶ Run Simulation", use_container_width=True)
    with info_col:
        if selected_personas:
            st.caption(f"Panel: {len(selected_personas)} participants · Priorities: {len(selected_priorities)} selected")
        else:
            st.caption("Select at least 2 personas in the sidebar to run a simulation.")

    # ── Run Simulation ──
    if run_btn:
        client = get_client()
        if not client:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not pitch.strip():
            st.warning("Please enter a product pitch before running.")
        elif len(selected_personas) < 2:
            st.warning("Please select at least 2 personas from the sidebar.")
        else:
            st.session_state.simulation_done = False
            st.session_state.phase2_messages = []

            progress = st.progress(0, text="Starting simulation...")

            try:
                progress.progress(10, text="🗣 Generating focus group transcript...")
                raw_transcript = generate_simulation(client, pitch, selected_personas, selected_priorities)
                transcript_lines = parse_transcript(raw_transcript, selected_personas)
                st.session_state.transcript_lines = transcript_lines
                st.session_state.raw_transcript = raw_transcript

                progress.progress(35, text="📊 Extracting insights...")
                insights_text = generate_insights(client, pitch, raw_transcript, selected_personas, selected_priorities)
                insights = parse_insights(insights_text)
                st.session_state.insights = insights
                st.session_state.insights_text = insights_text

                progress.progress(60, text="🔍 Running authenticity filter...")
                auth_text = check_authenticity(client, pitch, raw_transcript)
                auth = parse_authenticity(auth_text)
                st.session_state.auth = auth

                progress.progress(75, text="🗺 Generating focus group guide...")
                focus_guide = generate_focus_guide(client, pitch, raw_transcript, insights_text)
                st.session_state.focus_guide = focus_guide

                progress.progress(88, text="🔭 Generating next-step recommendations...")
                next_steps_text = generate_next_steps(client, pitch, insights_text, selected_personas)
                next_steps = parse_next_steps(next_steps_text)
                st.session_state.next_steps = next_steps

                progress.progress(100, text="✅ Simulation complete.")

                st.session_state.simulation_done = True
                st.session_state.selected_personas = selected_personas
                st.session_state.pitch = pitch
                st.session_state.selected_priorities = selected_priorities

            except Exception as e:
                progress.empty()
                st.error(f"Simulation error: {e}")

    # ── Results ──
    if st.session_state.simulation_done:
        insights = st.session_state.insights
        auth = st.session_state.auth
        personas = st.session_state.selected_personas
        honesty_scores = insights.get("honesty_scores", {})

        render_summary_bar(insights, auth)

        tab1, tab2 = st.tabs(["📊 Phase 1 — Simulation Results", "💬 Phase 2 — Follow-Up Conversation"])

        with tab1:
            render_dashboard(insights, auth, personas)
            st.markdown("<br>", unsafe_allow_html=True)
            render_transcript(st.session_state.transcript_lines, honesty_scores)
            st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state.next_steps:
                render_next_steps(st.session_state.next_steps)
                st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state.focus_guide:
                with st.expander("📋 Human Focus Group Guide (Export Ready)"):
                    st.markdown(st.session_state.focus_guide)
                    st.download_button(
                        label="⬇ Download Guide (.txt)",
                        data=st.session_state.focus_guide,
                        file_name="simgroup_focus_guide.txt",
                        mime="text/plain",
                        key="dl_guide",
                    )

            with st.expander("⬇ Export Full Simulation Results"):
                export_lines = [
                    "=" * 60,
                    "SIMGROUPAI — SIMULATION RESULTS",
                    "=" * 60,
                    f"\nPITCH:\n{st.session_state.pitch}",
                    f"\nPANEL: {', '.join([p['name'] for p in personas])}",
                    f"\nPRIORITIES: {', '.join(st.session_state.selected_priorities) if st.session_state.selected_priorities else 'None specified'}",
                    "\n" + "=" * 60,
                    "TRANSCRIPT",
                    "=" * 60,
                ]
                for item in st.session_state.transcript_lines:
                    export_lines.append(f"\n{item['speaker']}: {item['message']}")
                export_lines += [
                    "\n\n" + "=" * 60,
                    "INSIGHTS",
                    "=" * 60,
                    st.session_state.insights_text,
                    "\n\n" + "=" * 60,
                    "AUTHENTICITY FILTER",
                    "=" * 60,
                    f"Score: {auth.get('score')}\nGroupthink: {auth.get('groupthink')}\nSycophancy Risk: {auth.get('sycophancy_risk')}\nVerdict: {auth.get('verdict')}",
                    "\n\n" + "=" * 60,
                    "NEXT STEPS",
                    "=" * 60,
                ]
                for i, step in enumerate(st.session_state.next_steps, 1):
                    export_lines.append(f"\n{i}. {step['title']}\n   {step['rationale']}\n   Target: {step['profile']}")
                export_txt = "\n".join(export_lines)
                st.download_button(
                    label="⬇ Download Full Results (.txt)",
                    data=export_txt,
                    file_name="simgroup_results.txt",
                    mime="text/plain",
                    key="dl_full",
                )

        with tab2:
            st.markdown("""
            <div style="padding:14px;background:#0f1e35;border:1px solid #1e3a5f;border-radius:8px;margin-bottom:20px;font-size:0.85rem;color:#7a9bbf;line-height:1.5;">
            💬 <strong style="color:#4ecdc4;">Phase 2: Follow-Up Conversation</strong><br>
            Ask follow-up questions directly to the panelists. They remember the full discussion.
            Address the group or call out a specific participant by name.
            </div>
            """, unsafe_allow_html=True)

            for msg in st.session_state.phase2_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble chat-bubble-user">
                        <div class="chat-name chat-name-user">🎤 You (Moderator)</div>
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
                            text = mm.group(2).strip()
                            p_obj = next((p for p in personas if p["name"].lower() in speaker.lower()), None)
                            icon = p_obj["icon"] if p_obj else "👤"
                            hs = honesty_scores.get(speaker, None)
                            badge_html = honesty_badge_html(hs) if hs is not None else ""
                            st.markdown(f"""
                            <div class="chat-bubble">
                                <div class="chat-name">{icon} {speaker}{badge_html}</div>
                                {text}
                            </div>
                            """, unsafe_allow_html=True)

            with st.form(key="phase2_form", clear_on_submit=True):
                user_q = st.text_input(
                    "Ask a follow-up",
                    placeholder='e.g. "What would it take for you to actually buy this?" or "Robert, what\'s your biggest concern?"',
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Send →")

            if submitted and user_q.strip():
                client = get_client()
                if not client:
                    st.error("API key required.")
                else:
                    st.session_state.phase2_messages.append({"role": "user", "content": user_q})
                    with st.spinner("Panelists are responding..."):
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
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3a5a7a;">
            <div style="font-size:3rem;margin-bottom:12px;">🧬</div>
            <div style="font-size:1.1rem;font-weight:500;color:#4a7a9a;margin-bottom:8px;">No simulation running yet</div>
            <div style="font-size:0.85rem;color:#2a4a6a;">Enter your pitch above, select personas in the sidebar, and click <strong>Run Simulation</strong></div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
