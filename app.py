"""
SynthoPanel — Autonomous Consumer Simulation Platform
BUSN 32210 Final Project

Stack: Python · Streamlit · OpenAI API (GPT-4o)
Run:   streamlit run app.py
"""

import streamlit as st
import json
import os
import re
from openai import OpenAI

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SynthoPanel | Silicon Population Research",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# CSS INJECTION — Clinical / Laboratory theme
# Deep Navy (#0a1628) · Slate Gray (#6b8aad) · Mint Green (#4ecdc4)
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Global ── */
        .stApp { background-color: #0a1628; font-family: 'Inter', sans-serif; }
        .block-container { padding-top: 1.5rem !important; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #0d1e38 !important;
            border-right: 1px solid #1e3054;
        }
        [data-testid="stSidebar"] * { color: #e8edf5 !important; }

        /* ── Typography helpers ── */
        .main-title   { font-size: 2rem; font-weight: 700; color: #e8edf5; letter-spacing: -0.5px; }
        .mint         { color: #4ecdc4; }
        .subtitle     { font-size: 0.78rem; font-weight: 400; color: #6b8aad; letter-spacing: 2.5px; text-transform: uppercase; margin-top: 4px; }
        .section-label{ font-size: 0.68rem; font-weight: 700; color: #4ecdc4; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
        .muted        { color: #6b8aad; font-size: 0.85rem; }

        /* ── Cards ── */
        .panel-card {
            background: #1a2744; border: 1px solid #1e3054; border-radius: 8px;
            padding: 1.25rem; margin-bottom: 1rem;
        }
        .metric-card {
            background: #162038; border: 1px solid #2d4470; border-radius: 8px;
            padding: 1.25rem; text-align: center;
        }
        .metric-value { font-size: 2.5rem; font-weight: 700; color: #4ecdc4; font-family: 'JetBrains Mono', monospace; }
        .metric-sub   { font-size: 0.6rem; color: #6b8aad; }
        .metric-label { font-size: 0.72rem; color: #6b8aad; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; }

        /* ── Status bar ── */
        .status-bar {
            background: #162038; border: 1px solid #1e3054; border-radius: 6px;
            padding: 0.65rem 1rem; display: flex; align-items: center; gap: 8px;
            font-size: 0.82rem; color: #6b8aad; margin-bottom: 1.25rem;
        }

        /* ── Insight bullets ── */
        .insight-bullet {
            display: flex; align-items: flex-start; gap: 8px; padding: 8px 0;
            border-bottom: 1px solid #1e3054; font-size: 0.875rem; color: #c8d8e8;
        }
        .insight-bullet:last-child { border-bottom: none; }

        /* ── Badges ── */
        .badge-pass    { background:#1a3d2e; color:#4ecdc4; border:1px solid #4ecdc4; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }
        .badge-warning { background:#3d2e1a; color:#f5a623; border:1px solid #f5a623; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }
        .badge-flag    { background:#3d1a1a; color:#e74c3c; border:1px solid #e74c3c; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; }

        /* ── Inputs ── */
        .stTextArea textarea, .stTextInput input {
            background-color: #162038 !important; color: #e8edf5 !important;
            border: 1px solid #2d4470 !important; border-radius: 6px !important;
        }
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #4ecdc4 !important;
            box-shadow: 0 0 0 2px rgba(78,205,196,0.15) !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #4ecdc4, #2eb8af) !important;
            color: #0a1628 !important; font-weight: 700 !important;
            border: none !important; border-radius: 6px !important;
            padding: 0.55rem 1.5rem !important; font-size: 0.88rem !important;
            letter-spacing: 0.4px !important; transition: all 0.2s !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 15px rgba(78,205,196,0.3) !important;
        }
        .stButton > button:disabled {
            background: #1e3054 !important; color: #4a6080 !important;
            transform: none !important; box-shadow: none !important;
        }

        /* ── Download button ── */
        .stDownloadButton > button {
            background: #162038 !important; color: #4ecdc4 !important;
            border: 1px solid #4ecdc4 !important; border-radius: 6px !important;
            font-weight: 600 !important; font-size: 0.85rem !important;
        }

        /* ── Multiselect ── */
        .stMultiSelect [data-baseweb="select"] { background-color: #162038 !important; }
        .stMultiSelect [data-baseweb="tag"]    { background-color: #1a3d2e !important; }

        /* ── Chat messages ── */
        [data-testid="stChatMessage"] {
            background: #162038 !important; border: 1px solid #1e3054 !important;
            border-radius: 8px !important; margin-bottom: 6px !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: #162038 !important; border: 1px solid #1e3054 !important;
            border-radius: 6px !important; color: #e8edf5 !important;
        }

        /* ── Spinner text ── */
        .stSpinner p { color: #4ecdc4 !important; }

        /* ── Divider ── */
        hr { border-color: #1e3054 !important; margin: 1rem 0 !important; }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_personas():
    """Load the Silicon Population library from personas.json."""
    path = os.path.join(os.path.dirname(__file__), "personas.json")
    with open(path, "r") as f:
        return json.load(f)


def get_client():
    """Return an OpenAI client using the key stored in session state."""
    key = st.session_state.get("api_key", "").strip()
    if not key:
        return None
    return OpenAI(api_key=key)


# ─────────────────────────────────────────────────────────────────────────────
# LLM LAYER  —  4 independent, focused calls
# ─────────────────────────────────────────────────────────────────────────────

def generate_simulation(client, pitch: str, personas: list) -> str:
    """
    CALL 1 — Single LLM generates the full focus group transcript.
    A strict system prompt prevents groupthink and infinite loops.
    """
    roster = "\n".join(
        f"  • {p['name']} ({p['age_group']}, {p['location_type']}, {p['income_bracket']})\n"
        f"    Values: {', '.join(p['core_values'])}\n"
        f"    Voice: {p['communication_style']}"
        for p in personas
    )

    system = f"""You are Dr. Reyes, a veteran consumer research moderator for SynthoPanel.

Your job: Generate a realistic, unscripted focus group transcript where {len(personas)} distinct consumer personas
debate a product pitch. Each persona has a fixed identity — they do NOT change their position just to be polite.

PANEL ROSTER:
{roster}

TRANSCRIPT RULES (non-negotiable):
1. Format every line as:  [SPEAKER NAME]: dialogue
2. Dr. Reyes speaks ONLY to: (a) introduce the pitch, (b) redirect once if needed, (c) close the session.
3. Every persona speaks between 2 and 4 times. No one dominates; no one is silent.
4. Personas MUST disagree with each other based on their core values — no groupthink.
5. Include at least ONE direct, named confrontation (e.g., one persona calls out another by name).
6. Each persona's vocabulary, concerns, and references must match their background — no generic corporate-speak.
7. Produce 16–22 exchanges total. Then stop. Do NOT loop or repeat.
8. End with Dr. Reyes closing the session in one sentence."""

    user = f"""PITCH SUBMITTED FOR PANEL EVALUATION:

---
{pitch}
---

Generate the focus group transcript now. Start with Dr. Reyes introducing the pitch."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.85,
        max_tokens=2200,
    )
    return response.choices[0].message.content


def generate_insights(client, pitch: str, transcript: str, personas: list) -> str:
    """
    CALL 2 — Structured extraction of quantitative + qualitative signals.
    Returns a strictly formatted string for deterministic parsing.
    """
    system = """You are an AI research analyst for SynthoPanel.
Analyze the focus group transcript and extract structured consumer insights.
Return ONLY the following format — no extra text, no markdown, no deviations:

ADOPTION_SCORE: [integer 1-10]
ADOPTION_RATIONALE: [one sentence]
PAIN_POINTS:
• [pain point 1]
• [pain point 2]
• [pain point 3]
TRUST_TRIGGERS:
• [trust trigger 1]
• [trust trigger 2]
• [trust trigger 3]
PERSONA_SCORES:
[NAME]: [score]/10
[NAME]: [score]/10
KEY_TENSION: [the single most important unresolved conflict in one sentence]"""

    user = f"""PITCH: {pitch}

TRANSCRIPT:
{transcript}

Provide your structured analysis now. Use the exact format specified."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=700,
    )
    return response.choices[0].message.content


def check_authenticity(client, pitch: str, transcript: str) -> str:
    """
    CALL 3 — AI Authenticity Filter: flags disingenuous or out-of-touch messaging.
    Returns strictly formatted string.
    """
    system = """You are SynthoPanel's AI Authenticity Filter.
Assess whether this product pitch feels authentic and in-touch with real consumers,
or whether it feels AI-generated, corporate, or disingenuous based on panel reaction.

Return ONLY this format — no extra text:

AUTHENTICITY_STATUS: [PASS or WARNING or FLAG]
AUTHENTICITY_SCORE: [integer 1-10, where 10 = fully authentic]
AUTHENTICITY_VERDICT: [one sentence verdict]
RISK_SIGNALS:
• [specific signal, or "None identified"]
RECOMMENDATION: [one actionable sentence]"""

    user = f"""PITCH: {pitch}

PANEL REACTION EXCERPT:
{transcript[:1500]}

Provide your authenticity assessment now."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=450,
    )
    return response.choices[0].message.content


def generate_focus_guide(client, pitch: str, transcript: str, insights: str) -> str:
    """
    CALL 4 — The Bridge: generates a strategic Human Focus Group Guide
    for real-world follow-up based on simulation friction points.
    """
    system = """You are a senior qualitative research strategist at a top consumer insights firm.
Based on a synthetic focus group simulation, write a professional Human Focus Group Guide
for real-world follow-up validation. Be specific and actionable — this should be ready to hand to a moderator.

Use this structure exactly:

═══════════════════════════════════════════════
HUMAN FOCUS GROUP GUIDE
Generated by SynthoPanel Insight Engine
═══════════════════════════════════════════════

RESEARCH OBJECTIVE
[1-2 sentences defining the goal of the human session]

RECOMMENDED PARTICIPANT PROFILE
[Describe ideal recruits — demographics, psychographics — based on simulation tensions]

WARM-UP QUESTIONS (5 min)
1. [Question]
2. [Question]

CORE EXPLORATION (20 min)
1. [Question targeting the primary pain point]
2. [Question probing the trust gap]
3. [Question surfacing the key demographic tension]
4. [Question on pricing/value perception]
5. [Open-ended question]

STIMULUS RESPONSE (10 min)
[Present the pitch, then ask:]
A. [Immediate reaction probe]
B. [Credibility probe]
C. [Barrier probe]

CLOSING (5 min)
1. [Final ranking or rating exercise]
2. [One-word association exercise]

HYPOTHESES TO TEST
• H1: [Specific, testable hypothesis from simulation]
• H2: [Specific, testable hypothesis from simulation]
• H3: [Specific, testable hypothesis from simulation]

ANALYST NOTES
[2-3 sentences on what the moderator should watch for, based on the synthetic session]"""

    user = f"""ORIGINAL PITCH:
{pitch}

KEY INSIGHTS FROM SYNTHETIC SIMULATION:
{insights}

Generate the Human Focus Group Guide now."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=1400,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# PARSING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_insights(text: str) -> dict:
    """Parse the structured insights string into a Python dict."""
    result = {
        "adoption_score": None,
        "adoption_rationale": "",
        "pain_points": [],
        "trust_triggers": [],
        "persona_scores": {},
        "key_tension": "",
    }
    section = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("ADOPTION_SCORE:"):
            m = re.search(r"(\d+(?:\.\d+)?)", line)
            if m:
                result["adoption_score"] = float(m.group(1))
        elif line.startswith("ADOPTION_RATIONALE:"):
            result["adoption_rationale"] = line.split(":", 1)[1].strip()
        elif line.startswith("PAIN_POINTS:"):
            section = "pain"
        elif line.startswith("TRUST_TRIGGERS:"):
            section = "trust"
        elif line.startswith("PERSONA_SCORES:"):
            section = "persona"
        elif line.startswith("KEY_TENSION:"):
            result["key_tension"] = line.split(":", 1)[1].strip()
            section = None
        elif line.startswith(("•", "-", "*")):
            content = line.lstrip("•-* ").strip()
            if section == "pain" and content:
                result["pain_points"].append(content)
            elif section == "trust" and content:
                result["trust_triggers"].append(content)
        elif section == "persona" and ":" in line:
            # e.g. "Maya Chen: 7/10"
            parts = line.split(":")
            name = parts[0].strip()
            m = re.search(r"(\d+(?:\.\d+)?)", parts[1])
            if m and name:
                result["persona_scores"][name] = float(m.group(1))

    return result


def parse_authenticity(text: str) -> dict:
    """Parse the authenticity check string into a Python dict."""
    result = {
        "status": "PASS",
        "score": None,
        "verdict": "",
        "risk_signals": [],
        "recommendation": "",
    }
    section = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("AUTHENTICITY_STATUS:"):
            result["status"] = line.split(":", 1)[1].strip()
        elif line.startswith("AUTHENTICITY_SCORE:"):
            m = re.search(r"(\d+(?:\.\d+)?)", line)
            if m:
                result["score"] = float(m.group(1))
        elif line.startswith("AUTHENTICITY_VERDICT:"):
            result["verdict"] = line.split(":", 1)[1].strip()
            section = None
        elif line.startswith("RISK_SIGNALS:"):
            section = "risk"
        elif line.startswith("RECOMMENDATION:"):
            result["recommendation"] = line.split(":", 1)[1].strip()
            section = None
        elif line.startswith(("•", "-", "*")) and section == "risk":
            content = line.lstrip("•-* ").strip()
            if content and content.lower() != "none identified":
                result["risk_signals"].append(content)

    return result


def parse_transcript(text: str, personas: list) -> list:
    """
    Convert a raw transcript string into a list of {speaker, message, persona} dicts.
    Handles formats like [Dr. Reyes]: ... and [Maya Chen]: ...
    """
    persona_map = {p["name"].lower(): p for p in personas}
    lines = []

    for raw in text.split("\n"):
        raw = raw.strip()
        if ":" not in raw:
            continue
        # Match [NAME]: message  or  NAME: message
        m = re.match(r"^\[?([^\]:]+)\]?:\s*(.+)$", raw)
        if not m:
            continue
        speaker = m.group(1).strip()
        message = m.group(2).strip()
        if not message:
            continue

        # Find the matching persona (fuzzy match on first name or full name)
        matched = None
        speaker_lower = speaker.lower()
        for key, p in persona_map.items():
            first_name = key.split()[0]
            if speaker_lower == key or first_name in speaker_lower or speaker_lower in key:
                matched = p
                break

        lines.append({"speaker": speaker, "message": message, "persona": matched})

    return lines


# ─────────────────────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(personas: list) -> tuple[list, bool]:
    """
    Renders the Recruitment Center sidebar.
    Returns (selected_personas, api_key_present).
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem;">
                <div style="font-size:0.62rem; color:#4ecdc4; text-transform:uppercase; letter-spacing:2px; font-weight:700;">SynthoPanel v1.0</div>
                <div style="font-size:1.25rem; font-weight:700; color:#e8edf5; margin-top:4px;">Recruitment Center</div>
                <div style="font-size:0.78rem; color:#6b8aad; margin-top:2px;">Configure your Silicon Population</div>
            </div>
            <hr>
            """,
            unsafe_allow_html=True,
        )

        # API key
        st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            value=st.session_state.get("api_key", os.getenv("OPENAI_API_KEY", "")),
            help="Enter your OpenAI API key. It is never stored beyond this session.",
            label_visibility="collapsed",
        )
        if api_key:
            st.session_state.api_key = api_key

        st.markdown("<br>", unsafe_allow_html=True)

        # Persona selection
        st.markdown('<div class="section-label">👥 Panel Roster</div>', unsafe_allow_html=True)
        all_names = [p["name"] for p in personas]
        selected_names = st.multiselect(
            "Recruit personas",
            options=all_names,
            default=all_names[:4],
            help="Select 2–8 personas. Diverse panels yield richer simulations.",
            label_visibility="collapsed",
        )
        selected_personas = [p for p in personas if p["name"] in selected_names]

        # Active panel display
        if selected_personas:
            st.markdown(
                f"""
                <div style="background:#0d1e38; border:1px solid #1e3054; border-radius:6px; padding:0.75rem; margin-top:8px;">
                    <div style="font-size:0.65rem; color:#6b8aad; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                        Active Panel — {len(selected_personas)} persona{"s" if len(selected_personas)!=1 else ""}
                    </div>
                """,
                unsafe_allow_html=True,
            )
            for p in selected_personas:
                st.markdown(
                    f"""
                    <div style="padding:5px 0; border-bottom:1px solid #1e3054;">
                        <span style="margin-right:6px;">{p["icon"]}</span>
                        <span style="color:#e8edf5; font-weight:600; font-size:0.82rem;">{p["name"]}</span>
                        <div style="color:#6b8aad; font-size:0.72rem; margin-left:22px;">{p["age_group"]} · {p["location_type"]} · {p["income_bracket"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Select at least 2 personas to run a simulation.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Full profile browser
        with st.expander("📋 Browse All Profiles"):
            for p in personas:
                active = p["name"] in selected_names
                border = "#4ecdc4" if active else "#1e3054"
                st.markdown(
                    f"""
                    <div style="padding:10px; background:#0d1e38; border:1px solid {border}; border-radius:6px; margin-bottom:6px;">
                        <div style="font-weight:700; font-size:0.82rem;">{p["icon"]} {p["name"]} {"✓" if active else ""}</div>
                        <div style="color:#6b8aad; font-size:0.72rem; margin:3px 0;">{p["age_group"]} · {p["location_type"]} · {p["income_bracket"]}</div>
                        <div style="color:#8899aa; font-size:0.72rem;">Values: {", ".join(p["core_values"][:3])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    return selected_personas, bool(api_key)


def render_transcript(transcript_lines: list):
    """Renders the parsed transcript using st.chat_message."""
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem;">
            <div class="section-label" style="margin:0;">🧬 Virtual Observation Room — Live Transcript</div>
            <div style="height:1px; flex:1; background:#1e3054;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for entry in transcript_lines:
        persona = entry.get("persona")
        icon = persona["icon"] if persona else "🎙️"
        speaker = entry["speaker"]
        message = entry["message"]
        with st.chat_message(name=speaker, avatar=icon):
            if persona is None:
                # Moderator gets italics
                st.markdown(f"*{message}*")
            else:
                st.markdown(message)


def render_dashboard(insights: dict, auth: dict, selected_personas: list):
    """Renders the Insight Engine metrics dashboard."""
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem;">
            <div class="section-label" style="margin:0;">📊 Insight Engine Dashboard</div>
            <div style="height:1px; flex:1; background:#1e3054;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Top metric cards ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        score = insights.get("adoption_score")
        disp = f"{score:.1f}" if score is not None else "—"
        color = "#4ecdc4" if score and score >= 6 else "#f5a623" if score and score >= 4 else "#e74c3c"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{disp}</div>
                <div class="metric-sub">out of 10</div>
                <div class="metric-label">Likelihood of Adoption</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        a_score = auth.get("score")
        a_disp = f"{a_score:.1f}" if a_score is not None else "—"
        a_color = "#4ecdc4" if a_score and a_score >= 7 else "#f5a623" if a_score and a_score >= 5 else "#e74c3c"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{a_color};">{a_disp}</div>
                <div class="metric-sub">out of 10</div>
                <div class="metric-label">Authenticity Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        status = auth.get("status", "PASS")
        badge_cls = "badge-pass" if status == "PASS" else "badge-warning" if status == "WARNING" else "badge-flag"
        emoji = "✅" if status == "PASS" else "⚠️" if status == "WARNING" else "🚨"
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:2rem; margin-bottom:4px;">{emoji}</div>
                <div><span class="{badge_cls}">{status}</span></div>
                <div class="metric-label" style="margin-top:10px;">Authenticity Filter</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Rationale ────────────────────────────────────────────────────────────
    rationale = insights.get("adoption_rationale", "")
    if rationale:
        st.markdown(
            f"""
            <div style="background:#162038; border:1px solid #2d4470; border-radius:6px; padding:0.75rem 1rem; margin-bottom:1rem; font-size:0.875rem; color:#c8d8e8; font-style:italic;">
                "{rationale}"
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Pain Points & Trust Triggers ─────────────────────────────────────────
    col_pain, col_trust = st.columns(2)

    with col_pain:
        pain_points = insights.get("pain_points", [])
        st.markdown(
            '<div class="panel-card"><div class="section-label">⚡ Pain Points</div>',
            unsafe_allow_html=True,
        )
        if pain_points:
            for pp in pain_points:
                st.markdown(
                    f'<div class="insight-bullet"><span style="color:#e74c3c;">▸</span><span>{pp}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="muted">No specific pain points extracted.</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_trust:
        trust_triggers = insights.get("trust_triggers", [])
        st.markdown(
            '<div class="panel-card"><div class="section-label">🔒 Trust Triggers</div>',
            unsafe_allow_html=True,
        )
        if trust_triggers:
            for tt in trust_triggers:
                st.markdown(
                    f'<div class="insight-bullet"><span style="color:#4ecdc4;">▸</span><span>{tt}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="muted">No trust triggers extracted.</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Key Tension ──────────────────────────────────────────────────────────
    key_tension = insights.get("key_tension", "")
    if key_tension:
        st.markdown(
            f"""
            <div class="panel-card" style="border-left:3px solid #f5a623; border-color:#f5a623;">
                <div class="section-label" style="color:#f5a623;">⚡ Key Tension Identified</div>
                <div style="color:#e8edf5; font-size:0.9rem;">{key_tension}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Authenticity Report ──────────────────────────────────────────────────
    verdict = auth.get("verdict", "")
    recommendation = auth.get("recommendation", "")
    risk_signals = auth.get("risk_signals", [])
    a_border = "#4ecdc4" if status == "PASS" else "#f5a623" if status == "WARNING" else "#e74c3c"

    if verdict or recommendation:
        risk_html = "".join(
            f'<div style="color:#f5a623; font-size:0.82rem; margin:3px 0;">⚠ {s}</div>'
            for s in risk_signals
        )
        st.markdown(
            f"""
            <div class="panel-card" style="border-left:3px solid {a_border}; border-color:{a_border};">
                <div class="section-label">🛡️ AI Authenticity Filter Report</div>
                <div style="color:#e8edf5; font-size:0.9rem; margin-bottom:6px;">{verdict}</div>
                {risk_html}
                <div style="color:#6b8aad; font-size:0.85rem; margin-top:8px; padding-top:8px; border-top:1px solid #1e3054;">
                    💡 {recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Per-Persona Scores ───────────────────────────────────────────────────
    persona_scores = insights.get("persona_scores", {})
    if persona_scores:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">👥 Per-Persona Adoption Likelihood</div>', unsafe_allow_html=True)
        items = list(persona_scores.items())
        cols = st.columns(min(len(items), 4))
        for idx, (name, score) in enumerate(items):
            # Match to persona for icon
            matched = next(
                (p for p in selected_personas if p["name"].lower() in name.lower() or name.lower() in p["name"].lower()),
                None,
            )
            icon = matched["icon"] if matched else "👤"
            s_color = "#4ecdc4" if score >= 7 else "#f5a623" if score >= 5 else "#e74c3c"
            short_name = name.split()[0]
            with cols[idx % len(cols)]:
                st.markdown(
                    f"""
                    <div class="metric-card" style="padding:0.75rem;">
                        <div style="font-size:1.5rem;">{icon}</div>
                        <div style="font-weight:600; font-size:0.72rem; color:#e8edf5; margin:4px 0;">{short_name}</div>
                        <div style="font-size:1.4rem; font-weight:700; color:{s_color}; font-family:'JetBrains Mono',monospace;">{score:.0f}/10</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "simulation_done": False,
        "transcript": "",
        "insights_raw": "",
        "authenticity_raw": "",
        "focus_guide": "",
        "last_pitch": "",
        "last_personas": [],
        "api_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main():
    inject_css()
    init_session_state()

    personas = load_personas()
    selected_personas, has_key = render_sidebar(personas)
    panel_count = len(selected_personas)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="border-bottom:1px solid #1e3054; padding-bottom:1rem; margin-bottom:1.5rem;">
            <div class="main-title">Syntho<span class="mint">Panel</span></div>
            <div class="subtitle">Autonomous Consumer Simulation · Silicon Population Research Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Status bar ────────────────────────────────────────────────────────────
    ready = panel_count >= 2 and has_key
    status_color = "#4ecdc4" if ready else "#e74c3c"
    status_dot = "●" if ready else "○"
    panel_msg = f"READY — {panel_count} personas recruited" if ready else f"STANDBY — {panel_count}/2 personas minimum"
    api_msg = "CONNECTED" if has_key else "NO KEY"

    st.markdown(
        f"""
        <div class="status-bar">
            <span style="color:{status_color};">{status_dot}</span>
            <span>Panel Status: <strong style="color:{status_color};">{panel_msg}</strong></span>
            <span style="margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:{'#4ecdc4' if has_key else '#e74c3c'};">API: {api_msg}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Pitch Input ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">📡 Product Pitch Terminal</div>', unsafe_allow_html=True)
    pitch = st.text_area(
        "Pitch",
        placeholder=(
            "Describe your product, pricing model, or marketing copy. The more specific, the richer the simulation.\n\n"
            "Example: 'We're launching BrewBot — a $299 countertop smart coffee appliance. "
            "It learns your taste profile over 7 days and auto-orders beans via a $45/month subscription.'"
        ),
        height=150,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Launch button ─────────────────────────────────────────────────────────
    btn_col, info_col = st.columns([2, 4])
    with btn_col:
        can_run = panel_count >= 2 and bool(pitch.strip()) and has_key
        start = st.button("⚡  Start Simulation", disabled=not can_run, use_container_width=True)
    with info_col:
        if not has_key:
            st.markdown('<span style="color:#e74c3c; font-size:0.84rem;">← Add your OpenAI API key in the sidebar</span>', unsafe_allow_html=True)
        elif panel_count < 2:
            st.markdown('<span class="muted">← Recruit at least 2 personas to begin</span>', unsafe_allow_html=True)
        elif not pitch.strip():
            st.markdown('<span class="muted">← Enter your pitch above</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color:#4ecdc4; font-size:0.84rem;">✓ Ready — {panel_count} personas, {len(pitch)} chars</span>', unsafe_allow_html=True)

    # ── Run simulation ────────────────────────────────────────────────────────
    if start and can_run:
        client = get_client()

        with st.spinner("⚡ Instantiating Silicon Population..."):
            transcript = generate_simulation(client, pitch, selected_personas)

        with st.spinner("🔬 Running Insight Engine analysis..."):
            insights_raw = generate_insights(client, pitch, transcript, selected_personas)

        with st.spinner("🛡️ Running AI Authenticity Filter..."):
            authenticity_raw = check_authenticity(client, pitch, transcript)

        # Persist to session state
        st.session_state.transcript = transcript
        st.session_state.insights_raw = insights_raw
        st.session_state.authenticity_raw = authenticity_raw
        st.session_state.last_pitch = pitch
        st.session_state.last_personas = selected_personas
        st.session_state.simulation_done = True
        st.session_state.focus_guide = ""  # reset guide on new run
        st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.simulation_done and st.session_state.transcript:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Transcript
        transcript_lines = parse_transcript(
            st.session_state.transcript, st.session_state.last_personas
        )
        render_transcript(transcript_lines)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Dashboard
        insights = parse_insights(st.session_state.insights_raw)
        auth = parse_authenticity(st.session_state.authenticity_raw)
        render_dashboard(insights, auth, st.session_state.last_personas)

        # ── The Bridge ────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:6px;">
                <div class="section-label" style="margin:0;">🌉 The Bridge — Human Follow-Up Intelligence</div>
                <div style="height:1px; flex:1; background:#1e3054;"></div>
            </div>
            <div class="muted" style="margin-bottom:1rem;">
                Convert simulation friction points into a strategic real-world focus group guide.
            </div>
            """,
            unsafe_allow_html=True,
        )

        guide_btn = st.button("📋  Export Human Focus Group Guide")

        if guide_btn:
            client = get_client()
            if client:
                with st.spinner("🌉 Generating Human Focus Group Guide..."):
                    guide = generate_focus_guide(
                        client,
                        st.session_state.last_pitch,
                        st.session_state.transcript,
                        st.session_state.insights_raw,
                    )
                    st.session_state.focus_guide = guide

        if st.session_state.focus_guide:
            st.markdown(
                f"""
                <div class="panel-card" style="border-left:3px solid #4ecdc4; border-color:#4ecdc4;">
                    <div class="section-label">📋 Human Focus Group Guide</div>
                    <pre style="white-space:pre-wrap; font-family:'Inter',sans-serif; font-size:0.85rem; color:#c8d8e8; margin-top:8px; line-height:1.65;">{st.session_state.focus_guide}</pre>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                label="⬇  Download Guide (.txt)",
                data=st.session_state.focus_guide,
                file_name="synthopanel_focus_group_guide.txt",
                mime="text/plain",
            )

        st.markdown("<br><br>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
