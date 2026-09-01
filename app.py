"""
Harbor — AI Student Check-in & Support System
Frontend / UI / UX Layer
Built with Streamlit + Custom CSS

Author: Hansika (Frontend & UX Lead)
Hackathon: SIC Hack 2026

Architecture:
    - Single file: app.py
    - All UI rendered via Streamlit with injected CSS
    - Mock data used throughout — backend team replaces via integration points
    - Backend modules: database.py, scoring.py, analytics.py, planner.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

TASKS = [
    {"name": "DBMS Assignment", "days_until_due": 1, "estimated_hours": 2},
    {"name": "Python Project", "days_until_due": 2, "estimated_hours": 4},
    {"name": "Math Revision", "days_until_due": 4, "estimated_hours": 3}
]
AVAILABLE_HOURS = 4
import sqlite3
import pandas as pd
from integration import run_pipeline, _ensure_db_ready
from chatbot import StudentSupportChatbot
from action_router import detect_action
from resource_router import route_resource


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Harbor · Student Pulse",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DESIGN SYSTEM — CSS
# ============================================================

def inject_global_css():
    """Inject the complete design system CSS."""
    st.markdown("""
    <style>
    /* ========================================
       IMPORTS — Fonts
    ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ========================================
       CSS VARIABLES — Design Tokens
    ======================================== */
    :root {
        --bg-primary: #EEF2F7;
        --bg-secondary: #F6F8FB;
        --bg-card: #FFFFFF;
        --bg-blue-card: #3B6B9A;
        --bg-blue-light: #D6E4F0;
        --bg-blue-subtle: #E8EFF6;
        --text-primary: #1A2332;
        --text-secondary: #5A6B7F;
        --text-tertiary: #8899AA;
        --text-inverse: #FFFFFF;
        --accent-blue: #4A7FB5;
        --accent-blue-hover: #3A6A9A;
        --accent-blue-light: #6B9FD4;
        --border-light: #DDE5EE;
        --border-subtle: #E8EFF6;
        --shadow-sm: 0 1px 3px rgba(26,35,50,0.04);
        --shadow-md: 0 4px 16px rgba(26,35,50,0.06);
        --shadow-lg: 0 8px 32px rgba(26,35,50,0.08);
        --shadow-hover: 0 8px 28px rgba(26,35,50,0.10);
        --radius-sm: 8px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --radius-xl: 24px;
        --font-serif: 'Playfair Display', Georgia, 'Times New Roman', serif;
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        --transition: all 0.2s ease;
    }

    /* ========================================
       GLOBAL RESET
    ======================================== */
    .stApp {
        background-color: var(--bg-primary) !important;
        font-family: var(--font-sans) !important;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}

    /* Hide sidebar */
    [data-testid="stSidebar"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    button[kind="headerNoPadding"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}

    /* ========================================
       CONTENT CONTAINER
    ======================================== */
    .block-container {
        max-width: 1200px !important;
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* ========================================
       NAVIGATION BAR
    ======================================== */
    .harbor-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        margin-bottom: 8px;
        border-bottom: 1px solid var(--border-subtle);
        position: sticky;
        top: 0;
        z-index: 999;
        background: var(--bg-primary);
    }
    .harbor-nav-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .harbor-logo {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: var(--bg-blue-card);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: var(--font-serif);
        font-size: 18px;
        font-weight: 600;
        flex-shrink: 0;
    }
    .harbor-brand h1 {
        font-family: var(--font-sans);
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }
    .harbor-brand span {
        font-family: var(--font-sans);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        color: var(--accent-blue);
        text-transform: uppercase;
    }
    .harbor-nav-center {
        display: flex;
        align-items: center;
        gap: 32px;
    }
    .harbor-nav-center a {
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        text-decoration: none;
        transition: var(--transition);
        padding: 6px 2px;
        border-bottom: 2px solid transparent;
        cursor: pointer;
    }
    .harbor-nav-center a:hover,
    .harbor-nav-center a.active {
        color: var(--text-primary);
        border-bottom-color: var(--accent-blue);
    }
    .harbor-nav-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .harbor-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--accent-blue);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: var(--font-sans);
        font-size: 13px;
        font-weight: 600;
    }
    .harbor-username {
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
    }

    /* ========================================
       TYPOGRAPHY
    ======================================== */
    .eyebrow {
        font-family: var(--font-sans);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--accent-blue);
        margin-bottom: 12px;
    }
    .hero-heading {
        font-family: var(--font-serif);
        font-size: 42px;
        font-weight: 400;
        color: var(--text-primary);
        line-height: 1.2;
        margin-bottom: 36px;
    }
    .hero-heading .accent {
        color: var(--accent-blue);
        font-style: italic;
    }
    .section-title {
        font-family: var(--font-serif);
        font-size: 22px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 20px;
    }
    .card-label {
        font-family: var(--font-sans);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-tertiary);
        margin-bottom: 6px;
    }
    .card-label-blue {
        font-family: var(--font-sans);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent-blue-light);
        margin-bottom: 6px;
    }

    /* ========================================
       CARDS
    ======================================== */
    .harbor-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 28px;
        border: 1px solid var(--border-subtle);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        margin-bottom: 16px;
    }
    .harbor-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }
    .harbor-card-blue {
        background: var(--bg-blue-card);
        border-radius: var(--radius-lg);
        padding: 24px;
        color: var(--text-inverse);
        box-shadow: var(--shadow-md);
        transition: var(--transition);
        margin-bottom: 16px;
    }
    .harbor-card-blue:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }
    .harbor-card-subtle {
        background: var(--bg-blue-subtle);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        border: none;
        margin-bottom: 10px;
    }

    /* ========================================
       BUTTONS
    ======================================== */
    .harbor-btn-primary {
        display: inline-block;
        background: var(--bg-blue-card);
        color: white !important;
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 600;
        padding: 14px 32px;
        border-radius: var(--radius-md);
        border: none;
        cursor: pointer;
        transition: var(--transition);
        text-align: center;
        text-decoration: none;
        width: 100%;
        letter-spacing: 0.3px;
    }
    .harbor-btn-primary:hover {
        background: #2C5680;
        box-shadow: var(--shadow-md);
    }
    .harbor-btn-outline {
        display: inline-block;
        background: transparent;
        color: var(--accent-blue) !important;
        font-family: var(--font-sans);
        font-size: 13px;
        font-weight: 500;
        padding: 8px 18px;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-light);
        cursor: pointer;
        transition: var(--transition);
        text-decoration: none;
    }
    .harbor-btn-outline:hover {
        background: var(--bg-blue-subtle);
        border-color: var(--accent-blue);
    }

    /* ========================================
       STATUS / BADGES
    ======================================== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: var(--font-sans);
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
    }
    .status-attention {
        background: #FFF3E8;
        color: #C4700A;
    }
    .status-good {
        background: #E8F5E9;
        color: #2E7D32;
    }
    .status-moderate {
        background: #E3F0FC;
        color: var(--accent-blue);
    }
    .capacity-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--bg-blue-subtle);
        color: var(--accent-blue);
        font-family: var(--font-sans);
        font-size: 13px;
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 20px;
    }
    .capacity-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #E8963A;
    }

    /* ========================================
       CHAT BUBBLES
    ======================================== */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px 0;
    }
    .chat-bubble-ai {
        background: var(--bg-blue-subtle);
        border-radius: 4px 18px 18px 18px;
        padding: 16px 20px;
        margin-bottom: 12px;
        max-width: 85%;
        font-family: var(--font-sans);
        font-size: 14px;
        line-height: 1.65;
        color: var(--text-primary);
    }
    .chat-bubble-user {
        background: var(--accent-blue);
        color: white;
        border-radius: 18px 4px 18px 18px;
        padding: 16px 20px;
        margin-bottom: 12px;
        max-width: 85%;
        margin-left: auto;
        font-family: var(--font-sans);
        font-size: 14px;
        line-height: 1.65;
    }
    .chat-active-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4AA564;
        margin-right: 8px;
    }

    /* ========================================
       TIMELINE
    ======================================== */
    .timeline-item {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 14px 0;
        border-bottom: 1px solid var(--border-subtle);
    }
    .timeline-item:last-child {
        border-bottom: none;
    }
    .timeline-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-top: 5px;
        flex-shrink: 0;
    }
    .timeline-dot-orange { background: #E8963A; }
    .timeline-dot-blue { background: var(--accent-blue); }
    .timeline-dot-green { background: #4AA564; }
    .timeline-content h4 {
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 3px 0;
    }
    .timeline-content p {
        font-family: var(--font-sans);
        font-size: 12px;
        color: var(--text-tertiary);
        margin: 0;
    }
    .timeline-time {
        font-family: var(--font-sans);
        font-size: 12px;
        color: var(--text-tertiary);
        margin-left: auto;
        white-space: nowrap;
    }

    /* ========================================
       RESOURCE CARDS
    ======================================== */
    .resource-card {
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: 22px;
        border: 1px solid var(--border-subtle);
        transition: var(--transition);
        margin-bottom: 12px;
    }
    .resource-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--accent-blue);
    }
    .resource-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: var(--bg-blue-card);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 600;
        flex-shrink: 0;
    }

    /* ========================================
       SLEEP BARS
    ======================================== */
    .sleep-bars {
        display: flex;
        align-items: flex-end;
        gap: 8px;
        height: 60px;
        margin: 16px 0;
    }
    .sleep-bar {
        width: 28px;
        border-radius: 6px;
        background: rgba(255,255,255,0.3);
        transition: var(--transition);
    }
    .sleep-bar:hover {
        background: rgba(255,255,255,0.5);
    }

    /* ========================================
       CHECK-IN FORM OVERRIDES
    ======================================== */
    .stRadio > div {
        flex-direction: row !important;
        gap: 12px !important;
        flex-wrap: wrap;
    }
    .stRadio > div > label {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 10px 20px !important;
        font-family: var(--font-sans) !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: var(--transition) !important;
    }
    .stRadio > div > label:hover {
        border-color: var(--accent-blue) !important;
        background: var(--bg-blue-subtle) !important;
    }
    .stRadio > div > label[data-checked="true"],
    .stRadio > div [data-checked="true"] {
        border-color: var(--accent-blue) !important;
        background: var(--bg-blue-subtle) !important;
    }

    /* Slider overrides */
    .stSlider > div > div > div {
        background-color: var(--bg-blue-light) !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: var(--accent-blue) !important;
        border-color: var(--accent-blue) !important;
    }

    /* Text area overrides */
    .stTextArea textarea {
        border-radius: var(--radius-md) !important;
        border-color: var(--border-light) !important;
        font-family: var(--font-sans) !important;
        padding: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 1px var(--accent-blue) !important;
    }

    /* Number input overrides */
    .stNumberInput input {
        border-radius: var(--radius-sm) !important;
        border-color: var(--border-light) !important;
        font-family: var(--font-sans) !important;
    }

    /* Streamlit button overrides */
    .stButton > button {
        background: var(--bg-blue-card) !important;
        color: white !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        padding: 12px 28px !important;
        font-size: 14px !important;
        transition: var(--transition) !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        background: #2C5680 !important;
        box-shadow: var(--shadow-md) !important;
        border: none !important;
    }
    .stButton > button:focus {
        box-shadow: none !important;
        border: none !important;
    }
    .stButton > button:active {
        background: #1F4060 !important;
    }

    /* Reset button variant */
    .reset-btn .stButton > button {
        background: var(--bg-blue-subtle) !important;
        color: var(--accent-blue) !important;
        font-size: 13px !important;
        padding: 10px 18px !important;
    }
    .reset-btn .stButton > button:hover {
        background: var(--bg-blue-light) !important;
    }

    /* ========================================
       ACTION PLAN CARDS
    ======================================== */
    .action-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: var(--transition);
        cursor: pointer;
        margin-bottom: 8px;
    }
    .action-card:hover {
        border-color: var(--accent-blue);
        box-shadow: var(--shadow-sm);
        transform: translateY(-1px);
    }
    .action-icon {
        font-size: 20px;
        flex-shrink: 0;
    }
    .action-text {
        font-family: var(--font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
    }
    .action-meta {
        font-family: var(--font-sans);
        font-size: 12px;
        color: var(--text-tertiary);
        margin-left: auto;
    }

    /* ========================================
       LOGBOOK ENTRY
    ======================================== */
    .log-entry {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 24px 28px;
        border: 1px solid var(--border-subtle);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        margin-bottom: 14px;
        cursor: pointer;
    }
    .log-entry:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--accent-blue);
    }
    .log-date {
        font-family: var(--font-sans);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent-blue);
        margin-bottom: 10px;
    }
    .log-metrics {
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
    }
    .log-metric-item {
        text-align: center;
    }
    .log-metric-value {
        font-family: var(--font-sans);
        font-size: 22px;
        font-weight: 600;
        color: var(--text-primary);
    }
    .log-metric-label {
        font-family: var(--font-sans);
        font-size: 11px;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ========================================
       DE-ESCALATION
    ======================================== */
    .reset-card {
        background: linear-gradient(135deg, #F0F5FB 0%, #E6EDF5 100%);
        border-radius: var(--radius-lg);
        padding: 28px;
        border: 1px solid var(--border-subtle);
        text-align: center;
    }
    .reset-option {
        display: inline-block;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: 10px 18px;
        margin: 4px;
        font-family: var(--font-sans);
        font-size: 13px;
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition);
    }
    .reset-option:hover {
        border-color: var(--accent-blue);
        color: var(--accent-blue);
    }

    /* ========================================
       CHART OVERRIDES
    ======================================== */
    [data-testid="stPlotlyChart"] {
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    /* ========================================
       CHAT INPUT OVERRIDES
    ======================================== */
    [data-testid="stChatInput"] {
        border-radius: var(--radius-md) !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: var(--font-sans) !important;
    }

    /* ========================================
       DIVIDER
    ======================================== */
    .harbor-divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 16px 0;
    }

    /* ========================================
       RESPONSIVE
    ======================================== */
    @media (max-width: 768px) {
        .hero-heading {
            font-size: 30px;
        }
        .harbor-nav-center {
            gap: 16px;
        }
        .harbor-nav-center a {
            font-size: 13px;
        }
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* ========================================
       STREAMLIT ELEMENT SPACING
    ======================================== */
    .element-container {
        margin-bottom: 0 !important;
    }
    .stMarkdown {
        margin-bottom: 0 !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-secondary) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        background: var(--bg-blue-subtle) !important;
    }

    /* Metric override */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: 16px;
        border: 1px solid var(--border-subtle);
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "current_page": "home",
        "checkin_submitted": False,
        "checkin_data": {},
        "chat_messages": [
            {
                "role": "ai",
                "content": "I've looked at your workload for today. Let's focus on one 25-minute block instead of trying to finish everything at once. How does that feel?"
            }
        ],
        "selected_reset": None,
        "selected_action": None,
        "logbook_detail": None,
        "show_triage": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# MOCK DATA
# ============================================================
# These will be replaced by backend team via integration points

def get_mock_student():
    """Return mock student profile."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: database.get_student(student_id)
    # ============================
    return {
        "name": "Hansika",
        "initials": "HS",
        "student_id": "student_001",
    }

def get_mock_triage():
    system_data = st.session_state.get('system_data')
    if system_data and system_data.get('ui_data'):
        ui = system_data['ui_data']
        score = ui['score']
        plan = ui['plan']
        return {
            "status": "High Academic Pressure" if score['support_level'] == "High" else "Moderate Pressure",
            "capacity": 42,
            "priority": "NEEDS ATTENTION" if score['support_level'] == "High" else "STABLE",
            "support_level": score['support_level'],
            "ai_analysis": st.session_state.get('system_data', {}).get('ai_prompt_context', "").split("Instructions for AI")[0][-150:] + "...",
            "recommended_action": plan['strategy_recommended'],
            "best_focus_window": "10:30 AM - 12:15 PM",
            "study_strategy": plan['strategy_recommended'],
        }
    return {
        "status": "Needs Attention", "capacity": 42, "priority": "NEEDS ATTENTION",
        "support_level": "High", "ai_analysis": "Please check in first.",
        "recommended_action": "Check-in to see recommendations.",
        "best_focus_window": "-", "study_strategy": "-",
    }

def get_mock_sleep_data():
    """Return mock sleep history."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: analytics.get_student_trends(student_id)
    # ============================
    return {
        "current": 5.2,
        "history": [4.8, 6.1, 5.0, 6.5, 7.2, 5.2],
        "days": ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon"],
        "deficit": -1.8,
        "insight": "Your sleep has been below your usual level this week.",
    }

def get_mock_deadlines():
    """Return mock upcoming deadlines."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: planner.generate_study_plan(tasks, ...)
    # and database queries for upcoming tasks
    # ============================
    return [
        {
            "title": "Data Structures Midterm",
            "time": "09:00 AM",
            "when": "Tomorrow",
            "note": "Needs active retrieval practice",
            "color": "orange",
        },
        {
            "title": "Python Project Submission",
            "time": "05:00 PM",
            "when": "Friday",
            "note": "Final polishing phase",
            "color": "blue",
        },
        {
            "title": "Technical Writing Essay",
            "time": "11:59 PM",
            "when": "Next Monday",
            "note": "Draft review complete",
            "color": "green",
        },
    ]

def get_mock_resources():
    system_data = st.session_state.get('system_data')
    if system_data and 'resources' in system_data:
        mapped = []
        for r in system_data['resources']:
            mapped.append({
                "category": "SUPPORT",
                "name": r['name'],
                "initials": r['name'][0:2].upper(),
                "availability": "Available",
                "description": r['description']
            })
        return mapped
    return []

def get_mock_logbook():
    """Return mock check-in history."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: database queries for check_ins table
    # ============================
    today = datetime.now()
    return [
        {
            "date": "TODAY",
            "full_date": today.strftime("%B %d, %Y"),
            "pressure": 8, "energy": 4, "sleep": 5.2,
            "mood": "Okay", "workload": "High", "deadlines": 3,
            "message": "Feeling overwhelmed with midterms approaching.",
            "status": "Needs Attention",
        },
        {
            "date": "YESTERDAY",
            "full_date": (today - timedelta(days=1)).strftime("%B %d, %Y"),
            "pressure": 7, "energy": 5, "sleep": 6.1,
            "mood": "Okay", "workload": "High", "deadlines": 3,
            "message": "",
            "status": "Moderate",
        },
        {
            "date": "MONDAY",
            "full_date": (today - timedelta(days=2)).strftime("%B %d, %Y"),
            "pressure": 5, "energy": 7, "sleep": 7.0,
            "mood": "Good", "workload": "Moderate", "deadlines": 2,
            "message": "Had a productive study session today.",
            "status": "Stable",
        },
        {
            "date": "SUNDAY",
            "full_date": (today - timedelta(days=3)).strftime("%B %d, %Y"),
            "pressure": 4, "energy": 8, "sleep": 7.5,
            "mood": "Great", "workload": "Low", "deadlines": 1,
            "message": "",
            "status": "Good",
        },
        {
            "date": "SATURDAY",
            "full_date": (today - timedelta(days=4)).strftime("%B %d, %Y"),
            "pressure": 3, "energy": 8, "sleep": 8.0,
            "mood": "Great", "workload": "Low", "deadlines": 1,
            "message": "Relaxed weekend. Caught up on sleep.",
            "status": "Good",
        },
    ]

def get_mock_trends():
    """Return mock trend data for charts."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: analytics.get_student_trends(student_id, days=7)
    # ============================
    days = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
    return {
        "days": days,
        "pressure": [3, 4, 5, 6, 7, 7, 8],
        "sleep": [8.0, 7.5, 7.0, 6.1, 5.0, 6.5, 5.2],
        "energy": [8, 8, 7, 5, 4, 5, 4],
        "mood_scores": [4, 4, 3, 3, 2, 3, 2],
    }


# ============================================================
# MOCK CHATBOT LOGIC
# ============================================================

def get_mock_chat_response(user_message):
    try:
        context = st.session_state.get('system_data', {}).get('ai_prompt_context', "Be supportive.")
        chatbot = StudentSupportChatbot(context)
        resp = chatbot.get_response(user_message)
        
        if isinstance(resp, dict):
            if "error" in resp:
                return f"?? Error: {resp['error']}"
                
            msg = resp.get('message', '')
            formatted = f"<p style='margin-bottom: 0;'>{msg}</p>"
            
            actions = resp.get('priority_actions')
            if actions and isinstance(actions, list) and len(actions) > 0 and str(actions[0]).lower() != 'none':
                formatted += "<div style='margin-top:14px; font-weight:600; font-size: 13px; color:var(--accent-blue); letter-spacing: 0.5px;'>SUGGESTED ACTIONS</div>"
                formatted += "<ul style='margin-top:6px; padding-left: 20px; margin-bottom: 0;'>"
                for action in actions:
                    formatted += f"<li style='margin-bottom: 4px;'>{action}</li>"
                formatted += "</ul>"
                
            de_esc = resp.get('de_escalation')
            if de_esc and str(de_esc).lower() != 'none':
                formatted += f"<div style='margin-top:14px; padding: 10px 14px; background: rgba(255,255,255,0.6); border-left: 3px solid #E8963A; border-radius: 4px; font-size: 13.5px;'><i>{de_esc}</i></div>"
                
            follow = resp.get('follow_up')
            if follow and str(follow).lower() != 'none':
                formatted += f"<p style='margin-top:14px; margin-bottom: 0;'>{follow}</p>"
                
            return formatted
            
        return str(resp)
    except Exception as e:
        return f"I'm here to help you navigate your day. (Groq API fallback: {e})"


# ============================================================
# NAVIGATION
# ============================================================

def render_navigation():
    """Render the top navigation bar."""
    student = get_mock_student()
    current = st.session_state.current_page

    # Build active class markers
    def active(page):
        return "active" if current == page or (current == "home" and page == "insights_nav") else ""

    st.markdown(f"""
    <div class="harbor-nav">
        <div class="harbor-nav-left">
            <div class="harbor-logo">H</div>
            <div class="harbor-brand">
                <h1>Harbor</h1>
                <span>Student Pulse</span>
            </div>
        </div>
        <div class="harbor-nav-center">
            <a class="{'active' if current in ['home'] else ''}"
               onclick="window.location.href='?page=home'"
               style="cursor:pointer;">Home</a>
            <a class="{'active' if current == 'insights' else ''}"
               onclick="window.location.href='?page=insights'"
               style="cursor:pointer;">Insights</a>
            <a class="{'active' if current == 'logbook' else ''}"
               onclick="window.location.href='?page=logbook'"
               style="cursor:pointer;">Logbook</a>
            <a class="{'active' if current == 'resources' else ''}"
               onclick="window.location.href='?page=resources'"
               style="cursor:pointer;">Resources</a>
        </div>
        <div class="harbor-nav-right">
            <div class="harbor-avatar">{student['initials']}</div>
            <span class="harbor-username">{student['name']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit-based navigation using columns for reliable page switching
    nav_cols = st.columns([1, 1, 1, 1, 1, 4])
    with nav_cols[0]:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with nav_cols[1]:
        if st.button("📊 Insights", key="nav_insights", use_container_width=True):
            st.session_state.current_page = "insights"
            st.rerun()
    with nav_cols[2]:
        if st.button("📖 Logbook", key="nav_logbook", use_container_width=True):
            st.session_state.current_page = "logbook"
            st.rerun()
    with nav_cols[3]:
        if st.button("🧭 Resources", key="nav_resources", use_container_width=True):
            st.session_state.current_page = "resources"
            st.rerun()
    with nav_cols[4]:
        if st.button("💬 Chat", key="nav_chat", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()

    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)


# ============================================================
# PAGE: HOME / DASHBOARD
# ============================================================

def render_home():
    """Render the main home/dashboard page."""
    student = get_mock_student()
    triage = get_mock_triage()
    sleep_data = get_mock_sleep_data()
    deadlines = get_mock_deadlines()

    # Day of week
    day_name = datetime.now().strftime("%A").upper()

    # --- Hero Section ---
    st.markdown(f"""
    <div class="eyebrow">MORNING CHECK-IN · {day_name}</div>
    <div class="hero-heading">
        Let's find your<br>
        <span class="accent">rhythm</span> today, {student['name']}.
    </div>
    """, unsafe_allow_html=True)

    # --- Main Status + Recovery Cards ---
    col_main, col_side = st.columns([2.2, 1])

    with col_main:
        render_status_card(triage)

    with col_side:
        render_recovery_card(sleep_data)
        render_intention_card()

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # --- Upcoming Pressure + Support Network ---
    col_pressure, col_support = st.columns([1.2, 1])

    with col_pressure:
        render_upcoming_pressure(deadlines)

    with col_support:
        render_support_network()

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # --- AI Chat + Action Plan ---
    col_chat, col_actions = st.columns([1.5, 1])

    with col_chat:
        render_chat_section()

    with col_actions:
        render_action_plan()
        render_reset_card()


def render_status_card(triage):
    """Render the main AI triage status card."""
    capacity_color = "#E8963A" if triage["capacity"] < 50 else "#4AA564"

    st.markdown(f"""
    <div class="harbor-card" style="padding: 32px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
            <div>
                <div class="card-label">CURRENT STATUS</div>
                <div style="font-family: var(--font-serif); font-size: 26px; font-weight: 500; color: var(--text-primary); margin-bottom: 8px;">
                    {triage['status']}
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                <div class="capacity-badge">
                    <span class="capacity-dot" style="background: {capacity_color};"></span>
                    Capacity: {triage['capacity']}%
                </div>
                <div style="font-family: var(--font-sans); font-size: 10px; font-weight: 600; letter-spacing: 1.5px; color: var(--text-tertiary);">
                    PRIORITY: {triage['priority']}
                </div>
            </div>
        </div>
        <div class="harbor-divider"></div>
        <div style="display: flex; gap: 24px; margin-top: 20px;">
            <div style="flex: 1.2;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: var(--accent-blue);"></div>
                    <span class="card-label" style="margin-bottom: 0;">AI TRIAGE ANALYSIS</span>
                </div>
                <p style="font-family: var(--font-sans); font-size: 14px; line-height: 1.75; color: var(--text-secondary); margin: 0;">
                    {triage['ai_analysis']}
                </p>
            </div>
            <div style="flex: 0.8; display: flex; flex-direction: column; gap: 10px;">
                <div class="harbor-card-subtle">
                    <div class="card-label" style="color: var(--accent-blue); margin-bottom: 4px;">RECOMMENDED ACTION</div>
                    <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                        {triage['recommended_action']}
                    </div>
                </div>
                <div class="harbor-card-subtle">
                    <div class="card-label" style="color: var(--accent-blue); margin-bottom: 4px;">BEST FOCUS WINDOW</div>
                    <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                        {triage['best_focus_window']}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_recovery_card(sleep_data):
    """Render the blue recovery/sleep status card."""
    # Build sleep bars
    max_sleep = max(sleep_data["history"])
    bars_html = ""
    for val in sleep_data["history"]:
        height = max(8, int((val / max_sleep) * 55))
        bars_html += f'<div class="sleep-bar" style="height: {height}px;"></div>'

    deficit_display = f"{sleep_data['deficit']}h"

    st.markdown(f"""
    <div class="harbor-card-blue">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="card-label-blue">RECOVERY STATUS</div>
            <div style="font-family: var(--font-sans); font-size: 28px; font-weight: 700; color: #FF9F6B;">
                {deficit_display}
            </div>
        </div>
        <div style="margin-top: 2px; margin-bottom: 2px;">
            <span style="font-family: var(--font-sans); font-size: 13px; color: rgba(255,255,255,0.7);">Sleep</span>
            <span style="font-family: var(--font-sans); font-size: 18px; font-weight: 600; color: white; margin-left: 8px;">
                {sleep_data['current']} hrs
            </span>
        </div>
        <div class="sleep-bars">{bars_html}</div>
        <p style="font-family: var(--font-sans); font-size: 12px; color: rgba(255,255,255,0.65); margin: 0; line-height: 1.5;">
            {sleep_data['insight']}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_intention_card():
    """Render the intention card with Begin Check-in button."""
    st.markdown("""
    <div class="harbor-card" style="text-align: center; padding: 28px;">
        <div class="card-label">INTENTION</div>
        <div style="font-family: var(--font-serif); font-size: 24px; font-weight: 500; color: var(--text-primary); margin-bottom: 6px;">
            Steady Progress
        </div>
        <p style="font-family: var(--font-sans); font-size: 13px; color: var(--text-tertiary); margin-bottom: 20px;">
            Small steps count today.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Begin Check-in", key="begin_checkin", use_container_width=True):
        st.session_state.current_page = "checkin"
        st.rerun()


def render_upcoming_pressure(deadlines):
    """Render the upcoming pressure timeline card."""
    timeline_html = ""
    for d in deadlines:
        dot_class = f"timeline-dot-{d['color']}"
        timeline_html += f"""
        <div class="timeline-item">
            <div class="timeline-dot {dot_class}"></div>
            <div class="timeline-content">
                <h4>{d['title']}</h4>
                <p>{d['note']} · {d['when']}</p>
            </div>
            <span class="timeline-time">{d['time']}</span>
        </div>
        """

    st.markdown(f"""
    <div class="harbor-card">
        <div class="section-title">Upcoming Pressure</div>
        {timeline_html}
    </div>
    """, unsafe_allow_html=True)


def render_support_network():
    """Render the support network card."""
    resources = get_mock_resources()[:2]  # Show first 2 on home

    cards_html = ""
    for r in resources:
        cards_html += f"""
        <div style="display: flex; align-items: center; gap: 14px; padding: 14px 0; border-bottom: 1px solid var(--border-subtle);">
            <div class="resource-avatar">{r['initials']}</div>
            <div style="flex: 1;">
                <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">{r['name']}</div>
                <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary);">{r['category']} · {r['availability']}</div>
            </div>
            <div class="harbor-btn-outline" style="font-size: 12px; padding: 6px 14px;">Request</div>
        </div>
        """

    st.markdown(f"""
    <div class="harbor-card">
        <div class="section-title">Support Network</div>
        {cards_html}
    </div>
    """, unsafe_allow_html=True)


def render_chat_section():
    """Render the embedded AI chat section on home."""
    st.markdown("""
    <div class="harbor-card" style="padding: 28px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div style="font-family: var(--font-serif); font-size: 20px; font-weight: 500; color: var(--text-primary);">
                AI Support
            </div>
            <div style="font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary);">
                <span class="chat-active-dot"></span>Harmony is active
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Display chat messages
    chat_html = '<div class="chat-container">'
    for msg in st.session_state.chat_messages:
        if msg["role"] == "ai":
            chat_html += f'<div class="chat-bubble-ai">{msg["content"]}</div>'
        else:
            chat_html += f'<div class="chat-bubble-user">{msg["content"]}</div>'
    chat_html += '</div>'

    st.markdown(chat_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Type your thoughts...", key="home_chat_input")
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        response = get_mock_chat_response(user_input)
        st.session_state.chat_messages.append({"role": "ai", "content": response})
        st.rerun()


def render_action_plan():
    """Render the contextual action plan panel."""
    actions = [
        {"icon": "🍅", "text": "Focus Block", "meta": "25 minutes", "key": "focus"},
        {"icon": "🧘", "text": "15-Minute Reset", "meta": "Breathing + stretch", "key": "reset"},
        {"icon": "📚", "text": "Peer Tutoring", "meta": "Available today", "key": "tutor"},
        {"icon": "✉️", "text": "Draft Extension", "meta": "Email template", "key": "extension"},
    ]

    st.markdown("""
    <div class="harbor-card">
        <div class="card-label">YOUR ACTION PLAN</div>
        <div style="height: 8px;"></div>
    """, unsafe_allow_html=True)

    for a in actions:
        selected = st.session_state.selected_action == a["key"]
        border_color = "var(--accent-blue)" if selected else "var(--border-subtle)"
        bg = "var(--bg-blue-subtle)" if selected else "var(--bg-card)"

        st.markdown(f"""
        <div class="action-card" style="border-color: {border_color}; background: {bg};">
            <span class="action-icon">{a['icon']}</span>
            <span class="action-text">{a['text']}</span>
            <span class="action-meta">{a['meta']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Functional action buttons
    action_cols = st.columns(4)
    action_keys = ["focus", "reset", "tutor", "extension"]
    action_labels = ["🍅", "🧘", "📚", "✉️"]
    for i, col in enumerate(action_cols):
        with col:
            if st.button(action_labels[i], key=f"action_{action_keys[i]}", use_container_width=True):
                st.session_state.selected_action = action_keys[i]
                st.rerun()

    if st.session_state.selected_action:
        st.markdown(f"""
        <div style="background: var(--bg-blue-subtle); border-radius: var(--radius-md); padding: 14px 18px; margin-top: 8px;">
            <div style="font-family: var(--font-sans); font-size: 13px; color: var(--accent-blue); font-weight: 500;">
                ✓ Action selected. Your next step is ready when you are.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_reset_card():
    """Render the de-escalation reset card."""
    st.markdown("""
    <div class="reset-card">
        <div style="font-family: var(--font-serif); font-size: 18px; color: var(--text-primary); margin-bottom: 6px;">
            Take a moment.
        </div>
        <p style="font-family: var(--font-sans); font-size: 13px; color: var(--text-tertiary); margin-bottom: 14px;">
            A short reset can help you come back stronger.
        </p>
    </div>
    """, unsafe_allow_html=True)

    reset_cols = st.columns(2)
    resets = [
        ("🚶 15-min Walk", "walk"),
        ("🫁 2-min Breathing", "breathe"),
        ("📵 10-min Screen Break", "screen"),
        ("😴 Strategic Nap", "nap"),
    ]
    for i, (label, key) in enumerate(resets):
        with reset_cols[i % 2]:
            if st.button(label, key=f"reset_{key}", use_container_width=True):
                st.session_state.selected_reset = key
                st.rerun()

    if st.session_state.selected_reset:
        st.markdown("""
        <div style="background: var(--bg-blue-subtle); border-radius: var(--radius-md); padding: 14px 18px; margin-top: 8px; text-align: center;">
            <div style="font-family: var(--font-sans); font-size: 13px; color: var(--accent-blue); font-weight: 500;">
                ✓ Reset selected. Your next step is ready when you are.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE: CHECK-IN
# ============================================================

def render_checkin():
    """Render the check-in form page."""
    student = get_mock_student()

    if st.session_state.checkin_submitted and st.session_state.show_triage:
        render_triage_result()
        return

    # Header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 36px; margin-top: 20px;">
        <div class="hero-heading" style="font-size: 36px; margin-bottom: 8px;">
            How are you arriving today?
        </div>
        <p style="font-family: var(--font-sans); font-size: 16px; color: var(--text-tertiary);">
            This takes less than a minute.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Form container
    with st.container():
        # Mood
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">MOOD</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 12px; font-weight: 500;">
                How are you feeling right now?
            </div>
        </div>
        """, unsafe_allow_html=True)
        mood = st.radio(
            "Select your mood",
            ["Low", "Okay", "Good", "Great"],
            index=1,
            key="mood_input",
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Energy
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">ENERGY LEVEL</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 4px; font-weight: 500;">
                How's your energy today?
            </div>
        </div>
        """, unsafe_allow_html=True)
        energy = st.radio(
    "Energy",
    options=list(range(0, 11)),   # numbers 0–10
    index=4,                      # default selection
    key="energy_input",
    label_visibility="collapsed"  # hide duplicate label
)
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Sleep
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">SLEEP</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 4px; font-weight: 500;">
                Hours of sleep last night
            </div>
        </div>
        """, unsafe_allow_html=True)
        sleep_hours = st.selectbox(
    "Sleep hours",
    options=[x * 0.5 for x in range(0, 25)],  # 0.0 to 12.0 in steps of 0.5
    index=10,                                 # default = 5.0 hours
    key="sleep_input",
    label_visibility="collapsed"
)

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Academic Pressure
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">ACADEMIC PRESSURE</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 4px; font-weight: 500;">
                How much academic pressure do you feel?
            </div>
        </div>
        """, unsafe_allow_html=True)
        pressure =st.radio(
    "Pressure",
    options=list(range(0, 11)),
    index=8,
    key="pressure_input",
    label_visibility="collapsed"
)

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Workload
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">WORKLOAD</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 12px; font-weight: 500;">
                How would you describe your current workload?
            </div>
        </div>
        """, unsafe_allow_html=True)
        workload = st.radio(
            "Select workload level",
            ["Low", "Moderate", "High", "Very High"],
            index=2,
            key="workload_input",
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Upcoming deadlines
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">UPCOMING DEADLINES</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 4px; font-weight: 500;">
                Number of deadlines this week
            </div>
        </div>
        """, unsafe_allow_html=True)
        deadlines = st.number_input("Deadlines", min_value=0, max_value=20, value=3, key="deadlines_input", label_visibility="collapsed")

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        # Optional message
        st.markdown("""
        <div class="harbor-card" style="padding: 24px 28px;">
            <div class="card-label">ANYTHING ELSE?</div>
            <div style="font-family: var(--font-sans); font-size: 15px; color: var(--text-primary); margin-bottom: 4px; font-weight: 500;">
                Anything you'd like the AI to know?
            </div>
        </div>
        """, unsafe_allow_html=True)
        message = st.text_area(
            "Optional message",
            placeholder="Share what's on your mind... (optional)",
            key="message_input",
            label_visibility="collapsed",
            height=100,
        )

        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

        # Submit
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Complete Check-in", key="submit_checkin", use_container_width=True):
                mood_map = {"Low": 2, "Okay": 4, "Good": 7, "Great": 9}
                workload_map = {"Low": 2, "Moderate": 5, "High": 8, "Very High": 10}

                checkin_data = {
                    "mood": mood,
                    "mood_score": mood_map.get(mood, 5),
                    "energy_level": energy,
                    "sleep_hours": sleep_hours,
                    "academic_pressure": pressure,
                    "workload": workload,
                    "workload_level": workload_map.get(workload, 5),
                    "deadlines_count": deadlines,
                    "optional_message": message,
                    "timestamp": datetime.now().isoformat(),
                }
                st.session_state.checkin_data = checkin_data
                
                # INTEGRATION POINT
                _ensure_db_ready()
                result = run_pipeline("student_001", checkin_data, TASKS, AVAILABLE_HOURS, persist=True)
                st.session_state.system_data = result
                st.session_state.checkin_submitted = True
                st.session_state.show_triage = True
                st.rerun()


def render_triage_result():
    """Render the post check-in triage result."""
    student = get_mock_student()
    triage = get_mock_triage()
    data = st.session_state.checkin_data

    # ============================
    # BACKEND INTEGRATION POINT
    # Replace triage mock with actual result from:
    # scoring.calculate_support_score(checkin_data)
    # planner.build_ai_context_payload(student_id, checkin_data, tasks, hours)
    # ============================

    # Confirmation header
    st.markdown(f"""
    <div style="text-align: center; margin-top: 24px; margin-bottom: 32px;">
        <div style="font-size: 36px; margin-bottom: 12px;">✓</div>
        <div class="hero-heading" style="font-size: 32px; margin-bottom: 8px;">
            Thanks, {student['name']}.
        </div>
        <p style="font-family: var(--font-sans); font-size: 16px; color: var(--text-tertiary);">
            Let's see what would help today.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mood", data.get("mood", "Okay"))
    with col2:
        st.metric("Energy", f"{data.get('energy_level', 4)}/10")
    with col3:
        st.metric("Sleep", f"{data.get('sleep_hours', 5.0)}h")
    with col4:
        st.metric("Pressure", f"{data.get('academic_pressure', 8)}/10")

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # Triage result card
    render_status_card(triage)

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🏠 Go to Dashboard", key="triage_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with col_b:
        if st.button("💬 Talk to Harmony", key="triage_chat", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()
    with col_c:
        if st.button("📊 View Insights", key="triage_insights", use_container_width=True):
            st.session_state.current_page = "insights"
            st.rerun()


# ============================================================
# PAGE: CHATBOT (Full Page)
# ============================================================

def render_chatbot():
    """Render the full-page AI chatbot."""
    student = get_mock_student()

    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; margin-top: 12px;">
        <div>
            <div class="section-title" style="margin-bottom: 4px;">AI Support</div>
            <div style="font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary);">
                <span class="chat-active-dot"></span>Harmony is active
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_deck = st.columns([1.6, 1])

    with col_chat:
        # Chat messages
        chat_html = '<div class="harbor-card" style="padding: 24px; min-height: 400px;"><div class="chat-container">'
        for msg in st.session_state.chat_messages:
            if msg["role"] == "ai":
                chat_html += f"""
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--bg-blue-subtle); display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 4px;">
                        <span style="font-size: 14px;">🔵</span>
                    </div>
                    <div class="chat-bubble-ai" style="margin-bottom: 0;">{msg["content"]}</div>
                </div>
                """
            else:
                chat_html += f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">
                    <div class="chat-bubble-user">{msg["content"]}</div>
                </div>
                """
        chat_html += '</div></div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # Chat input
        user_input = st.chat_input("Type your thoughts...", key="full_chat_input")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            # ============================
            # BACKEND INTEGRATION POINT
            # Replace with: chatbot.get_response(user_input, ai_context)
            # ai_context from: planner.build_ai_context_payload()
            # ============================
            response = get_mock_chat_response(user_input)
            st.session_state.chat_messages.append({"role": "ai", "content": response})
            st.rerun()

    with col_deck:
        # Contextual Deck
        st.markdown("""
        <div class="harbor-card">
            <div class="card-label">CONTEXTUAL DECK</div>
            <div style="height: 12px;"></div>
        """, unsafe_allow_html=True)

        actions = [
            {"icon": "🍅", "text": "Focus Block", "meta": "25:00", "key": "deck_focus"},
            {"icon": "🧘", "text": "Guided Reset", "meta": "15:00", "key": "deck_reset"},
            {"icon": "📚", "text": "Peer Tutoring", "meta": "ACTIVE", "key": "deck_tutor"},
            {"icon": "✉️", "text": "Extension Draft", "meta": "Ready", "key": "deck_ext"},
        ]

        for a in actions:
            st.markdown(f"""
            <div class="action-card">
                <span class="action-icon">{a['icon']}</span>
                <span class="action-text">{a['text']}</span>
                <span class="action-meta">{a['meta']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick suggestion buttons
        st.markdown("""
        <div class="harbor-card" style="padding: 20px;">
            <div class="card-label">QUICK PROMPTS</div>
            <div style="height: 8px;"></div>
        </div>
        """, unsafe_allow_html=True)

        prompt_cols = st.columns(2)
        prompts = [
            ("I'm stressed", "prompt_stress"),
            ("Help me study", "prompt_study"),
            ("Find a tutor", "prompt_tutor"),
            ("Plan my day", "prompt_plan"),
        ]
        for i, (label, key) in enumerate(prompts):
            with prompt_cols[i % 2]:
                if st.button(label, key=key, use_container_width=True):
                    st.session_state.chat_messages.append({"role": "user", "content": label})
                    response = get_mock_chat_response(label)
                    st.session_state.chat_messages.append({"role": "ai", "content": response})
                    st.rerun()


# ============================================================
# PAGE: INSIGHTS
# ============================================================

def render_insights():
    """Render the insights/analytics page."""
    trends = get_mock_trends()

    st.markdown("""
    <div style="margin-top: 16px; margin-bottom: 32px;">
        <div class="hero-heading" style="font-size: 34px; margin-bottom: 8px;">
            Your Patterns
        </div>
        <p style="font-family: var(--font-sans); font-size: 15px; color: var(--text-tertiary);">
            Small signals become useful patterns over time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Chart styling
    chart_layout = dict(
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=40),
        height=260,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, color="#8899AA"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E8EFF6",
            tickfont=dict(size=12, color="#8899AA"),
        ),
    )

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="harbor-card" style="padding: 24px;">
            <div class="card-label">ACADEMIC PRESSURE</div>
        </div>
        """, unsafe_allow_html=True)

        fig_pressure = go.Figure()
        fig_pressure.add_trace(go.Scatter(
            x=trends["days"], y=trends["pressure"],
            mode="lines+markers",
            line=dict(color="#4A7FB5", width=2.5, shape="spline"),
            marker=dict(size=7, color="#4A7FB5"),
            fill="tozeroy",
            fillcolor="rgba(74, 127, 181, 0.08)",
        ))
        fig_pressure.update_layout(**chart_layout, yaxis_range=[0, 10])
        st.plotly_chart(fig_pressure, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("""
        <div class="harbor-card" style="padding: 24px;">
            <div class="card-label">SLEEP HOURS</div>
        </div>
        """, unsafe_allow_html=True)

        fig_sleep = go.Figure()
        fig_sleep.add_trace(go.Bar(
            x=trends["days"], y=trends["sleep"],
            marker_color=["#D6E4F0" if v >= 7 else "#4A7FB5" if v >= 5 else "#E8963A" for v in trends["sleep"]],
            marker=dict(cornerradius=6),
        ))
        fig_sleep.update_layout(**chart_layout, yaxis_range=[0, 10])
        st.plotly_chart(fig_sleep, use_container_width=True, config={"displayModeBar": False})

    # Second row
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class="harbor-card" style="padding: 24px;">
            <div class="card-label">ENERGY LEVEL</div>
        </div>
        """, unsafe_allow_html=True)

        fig_energy = go.Figure()
        fig_energy.add_trace(go.Scatter(
            x=trends["days"], y=trends["energy"],
            mode="lines+markers",
            line=dict(color="#4AA564", width=2.5, shape="spline"),
            marker=dict(size=7, color="#4AA564"),
            fill="tozeroy",
            fillcolor="rgba(74, 165, 100, 0.08)",
        ))
        fig_energy.update_layout(**chart_layout, yaxis_range=[0, 10])
        st.plotly_chart(fig_energy, use_container_width=True, config={"displayModeBar": False})

    with col4:
        st.markdown("""
        <div class="harbor-card" style="padding: 24px;">
            <div class="card-label">MOOD TREND</div>
        </div>
        """, unsafe_allow_html=True)

        mood_labels = {1: "Low", 2: "Okay", 3: "Good", 4: "Great"}
        fig_mood = go.Figure()
        fig_mood.add_trace(go.Scatter(
            x=trends["days"], y=trends["mood_scores"],
            mode="lines+markers",
            line=dict(color="#8B6DB0", width=2.5, shape="spline"),
            marker=dict(size=7, color="#8B6DB0"),
        ))
        fig_mood.update_layout(
            **chart_layout,
            yaxis=dict(
                showgrid=True,
                gridcolor="#E8EFF6",
                tickvals=[1, 2, 3, 4],
                ticktext=["Low", "Okay", "Good", "Great"],
                tickfont=dict(size=11, color="#8899AA"),
                range=[0.5, 4.5],
            ),
        )
        st.plotly_chart(fig_mood, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # AI Insight Card
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with AI-generated insight from:
    # analytics.get_student_trends(student_id, days=7)
    # + AI engine interpretation
    # ============================
    st.markdown("""
    <div class="harbor-card" style="padding: 28px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: var(--accent-blue);"></div>
            <span class="card-label" style="margin-bottom: 0;">AI PATTERN INSIGHT</span>
        </div>
        <p style="font-family: var(--font-sans); font-size: 15px; line-height: 1.75; color: var(--text-secondary); margin-bottom: 16px;">
            Your academic pressure has increased over the last three check-ins while your sleep
            has decreased. These two patterns often reinforce each other — higher pressure can make
            it harder to wind down, and less sleep can make pressure feel more intense.
        </p>
        <div class="harbor-card-subtle" style="margin-bottom: 0;">
            <div class="card-label" style="color: var(--accent-blue); margin-bottom: 4px;">SUGGESTED FOCUS</div>
            <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                Protect your evening recovery time. Consider a screen-free wind-down starting at 10 PM.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE: LOGBOOK
# ============================================================

def render_logbook():
    """Render the historical check-in logbook."""
    entries = get_mock_logbook()

    st.markdown("""
    <div style="margin-top: 16px; margin-bottom: 32px;">
        <div class="hero-heading" style="font-size: 34px; margin-bottom: 8px;">
            Your Logbook
        </div>
        <p style="font-family: var(--font-sans); font-size: 15px; color: var(--text-tertiary);">
            A record of how you've been showing up. No judgments, just data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for entry in entries:
        # Status badge
        status_class = "status-attention"
        if entry["status"] in ["Good", "Stable"]:
            status_class = "status-good"
        elif entry["status"] == "Moderate":
            status_class = "status-moderate"

        st.markdown(f"""
        <div class="log-entry">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <div class="log-date">{entry['date']}</div>
                    <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary);">
                        {entry['full_date']}
                    </div>
                </div>
                <div class="status-badge {status_class}">{entry['status']}</div>
            </div>
            <div class="log-metrics">
                <div class="log-metric-item">
                    <div class="log-metric-value">{entry['pressure']}/10</div>
                    <div class="log-metric-label">Pressure</div>
                </div>
                <div class="log-metric-item">
                    <div class="log-metric-value">{entry['energy']}/10</div>
                    <div class="log-metric-label">Energy</div>
                </div>
                <div class="log-metric-item">
                    <div class="log-metric-value">{entry['sleep']}h</div>
                    <div class="log-metric-label">Sleep</div>
                </div>
                <div class="log-metric-item">
                    <div class="log-metric-value">{entry['mood']}</div>
                    <div class="log-metric-label">Mood</div>
                </div>
                <div class="log-metric-item">
                    <div class="log-metric-value">{entry['workload']}</div>
                    <div class="log-metric-label">Workload</div>
                </div>
            </div>
            {"<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-subtle);'><p style=\"font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary); font-style: italic; margin: 0;\">\"" + entry['message'] + "\"</p></div>" if entry.get('message') else ""}
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE: RESOURCES
# ============================================================

def render_resources():
    """Render the resource discovery page."""
    all_resources = get_mock_resources()

    st.markdown("""
    <div style="margin-top: 16px; margin-bottom: 32px;">
        <div class="hero-heading" style="font-size: 34px; margin-bottom: 8px;">
            Support, when you need it.
        </div>
        <p style="font-family: var(--font-sans); font-size: 15px; color: var(--text-tertiary);">
            Campus resources available to help you succeed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Category filters
    categories = ["All", "Academic", "Well-being", "Financial", "Social"]
    cat_cols = st.columns(len(categories))

    if "resource_filter" not in st.session_state:
        st.session_state.resource_filter = "All"

    for i, cat in enumerate(categories):
        with cat_cols[i]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state.resource_filter = cat
                st.rerun()

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # Resource cards
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: resources.get_resources_by_category(filter)
    # Dynamic filtering and availability from backend
    # ============================

    # Map resources to categories for filtering
    resource_categories = {
        "PEER TUTORING": "Academic",
        "WRITING CENTER": "Academic",
        "ACADEMIC ADVISING": "Academic",
        "STUDENT SUPPORT": "Well-being",
        "FINANCIAL AID": "Financial",
        "STUDENT LIFE": "Social",
    }

    filtered = all_resources
    if st.session_state.resource_filter != "All":
        filtered = [r for r in all_resources if resource_categories.get(r["category"]) == st.session_state.resource_filter]

    # Display in grid
    cols = st.columns(2)
    for i, resource in enumerate(filtered):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="resource-card">
                <div style="display: flex; align-items: flex-start; gap: 16px;">
                    <div class="resource-avatar">{resource['initials']}</div>
                    <div style="flex: 1;">
                        <div class="card-label" style="margin-bottom: 4px;">{resource['category']}</div>
                        <div style="font-family: var(--font-sans); font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">
                            {resource['name']}
                        </div>
                        <p style="font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 10px;">
                            {resource['description']}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary);">
                                {resource['availability']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Functional buttons per resource
            btn_cols = st.columns(2)
            with btn_cols[0]:
                st.button("View Resource", key=f"view_{resource['initials']}_{i}", use_container_width=True)
            with btn_cols[1]:
                st.button("Request Help", key=f"req_{resource['initials']}_{i}", use_container_width=True)


# ============================================================
# ROUTER
# ============================================================

def route_page():
    """Route to the correct page based on session state."""
    page = st.session_state.current_page

    if page == "home":
        render_home()
    elif page == "checkin":
        render_checkin()
    elif page == "chatbot":
        render_chatbot()
    elif page == "insights":
        render_insights()
    elif page == "logbook":
        render_logbook()
    elif page == "resources":
        render_resources()
    else:
        render_home()


# ============================================================
# MAIN
# ============================================================

def main():
    """Main application entry point."""
    init_session_state()
    inject_global_css()
    render_navigation()
    route_page()


if __name__ == "__main__":
    main()

