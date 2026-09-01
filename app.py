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

import os
import base64
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time

@st.cache_data
def get_logo_b64():
    """Load and encode logo.png into base64 data URI for top nav logo display."""
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return None

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
import streamlit.components.v1 as components

def render_html(html_str):
    """Safely render HTML in Streamlit without triggering Markdown code block formatting."""
    cleaned = "\n".join(line.lstrip() for line in html_str.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_mouse_bubble():
    """Injects a subtle light blue mouse tracking glow effect positioned behind widgets."""
    components.html(
        """
        <script>
        const parentDoc = window.parent.document;
        let bubble = parentDoc.getElementById('mouse-bubble');
        
        if (!bubble) {
            bubble = parentDoc.createElement('div');
            bubble.id = 'mouse-bubble';
            bubble.style.position = 'fixed';
            bubble.style.pointerEvents = 'none';
            bubble.style.zIndex = '0';
            bubble.style.top = '0';
            bubble.style.left = '0';
            bubble.style.transform = 'translate3d(-2000px, -2000px, 0)';
            parentDoc.body.appendChild(bubble);

            let mouseX = -2000;
            let mouseY = -2000;
            let currentX = -2000;
            let currentY = -2000;

            parentDoc.addEventListener('mousemove', function(e) {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });

            function animate() {
                if (bubble.style.display !== 'none') {
                    // Smooth lerp movement (0.14 factor)
                    currentX += (mouseX - currentX) * 0.14;
                    currentY += (mouseY - currentY) * 0.14;
                    const halfSize = (parseFloat(bubble.style.width) || 300) / 2;
                    bubble.style.transform = `translate3d(${currentX - halfSize}px, ${currentY - halfSize}px, 0)`;
                }
                requestAnimationFrame(animate);
            }
            animate();
        }

        // Apply compact size, background z-index, and subtle glow opacity
        bubble.style.width = '300px';
        bubble.style.height = '300px';
        bubble.style.borderRadius = '50%';
        bubble.style.background = 'radial-gradient(circle, rgba(74, 127, 181, 0.18) 0%, rgba(74, 127, 181, 0.06) 40%, transparent 70%)';
        bubble.style.zIndex = '0';
        bubble.style.pointerEvents = 'none';
        bubble.style.display = 'block';
        </script>
        """,
        height=0,
        width=0,
    )

def hide_mouse_bubble():
    """Hides the mouse tracking bubble effect."""
    components.html(
        """
        <script>
        const parentDoc = window.parent.document;
        let bubble = parentDoc.getElementById('mouse-bubble');
        if (bubble) {
            bubble.style.display = 'none';
        }
        </script>
        """,
        height=0,
        width=0,
    )

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
       CONTENT CONTAINER & STACKING CONTEXT
    ======================================== */
    .block-container {
        max-width: 1200px !important;
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 2rem !important;
        position: relative;
        z-index: 2;
    }

    /* Keep cards and interactive widgets stacked above background glow */
    .harbor-card,
    .harbor-card-blue,
    .harbor-nav,
    div[data-testid="stVerticalBlockBorderWrapper"],
    .stButton,
    [data-testid="stChatInput"] {
        position: relative;
        z-index: 2;
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

    /* Clean Header Navigation Buttons */
    div[data-testid="stColumn"] button[key^="nav_btn_"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-family: var(--font-sans) !important;
        font-size: 15px !important;
        color: #5A6B7F !important;
        font-weight: 500 !important;
        border-radius: 0 !important;
        border-bottom: 2.5px solid transparent !important;
        padding: 6px 0 !important;
    }
    div[data-testid="stColumn"] button[key^="nav_btn_"]:hover {
        color: #1A2332 !important;
        background: transparent !important;
    }
    div[data-testid="stColumn"] button[key^="nav_btn_"][data-testid="stBaseButton-primary"],
    div[data-testid="stColumn"] button[key^="nav_btn_"][kind="primary"] {
        color: #1A2332 !important;
        font-weight: 700 !important;
        border-bottom: 2.5px solid #4A7FB5 !important;
        background: transparent !important;
    }

    /* Solid White Card Box for st.container(border=True) */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border-radius: 20px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #DDE5EE !important;
        box-shadow: 0 2px 12px rgba(26, 35, 50, 0.05) !important;
        padding: 24px 28px !important;
        margin-top: 12px !important;
        margin-bottom: 16px !important;
    }

    /* Contextual Deck Action Pill Buttons */
    div[data-testid="stColumn"] button[key^="deck_timer_"],
    button[key^="deck_timer_"] {
        background: #E8EFF6 !important;
        color: #2B5B84 !important;
        border: 1px solid #D6E4F0 !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 12px 18px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"] button[key^="deck_timer_"]:hover,
    button[key^="deck_timer_"]:hover {
        background: #2B5B84 !important;
        color: #FFFFFF !important;
        border-color: #2B5B84 !important;
        transform: translateY(-1px) !important;
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
    .stRadio > div > label,
    .stRadio label,
    .stRadio label p,
    .stRadio label span,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #1A2332 !important;
        font-weight: 600 !important;
    }
    .stRadio > div > label {
        background: #FFFFFF !important;
        border: 1px solid #DDE5EE !important;
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
        color: #1A2332 !important;
    }
    .stRadio > div > label[data-checked="true"],
    .stRadio > div [data-checked="true"],
    div[data-testid="stRadio"] label[aria-checked="true"] {
        border-color: var(--accent-blue) !important;
        background: var(--bg-blue-subtle) !important;
        color: #1A2332 !important;
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
# TIMER CONTRACT HELPERS & DISPATCH
# ============================================================

def format_timer_display(seconds: int) -> str:
    """Formats seconds into MM:SS (or HH:MM:SS if >= 3600s). Clamps negative to 00:00."""
    sec = max(0, int(seconds))
    hrs = sec // 3600
    mins = (sec % 3600) // 60
    secs = sec % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def compute_timer_progress(total: int, remaining: int) -> float:
    """Computes completion progress fraction between 0.0 and 1.0."""
    if total <= 0:
        return 1.0
    rem = max(0, min(total, remaining))
    return float(total - rem) / float(total)


def start_timer_session(preset_key: str, title: str, duration_seconds: int, auto_start: bool = True):
    """Safely transitions state and redirects to the Timer page."""
    st.session_state.timer_preset = preset_key
    st.session_state.timer_title = title
    st.session_state.timer_total = duration_seconds
    st.session_state.timer_remaining = duration_seconds
    st.session_state.timer_completed = False
    st.session_state.timer_running = auto_start
    if auto_start:
        st.session_state.timer_end_time = time.time() + duration_seconds
    else:
        st.session_state.timer_end_time = None

    st.session_state.current_page = "timer"
    st.session_state.selected_reset = preset_key
    try:
        st.rerun()
    except Exception:
        pass


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def init_session_state():
    """Initialize all session state variables and sync page query params."""
    if "current_page" not in st.session_state:
        page = "home"
        try:
            page_param = st.query_params.get("page")
            if page_param:
                p = page_param[0] if isinstance(page_param, list) else page_param
                if p in ["home", "insights", "logbook", "resources", "chatbot", "checkin", "timer"]:
                    page = p
        except Exception:
            pass
        st.session_state.current_page = page
    else:
        try:
            st.query_params["page"] = st.session_state.current_page
        except Exception:
            pass

    defaults = {
        "current_page": "home",
        "checkin_submitted": False,
        "checkin_data": {},
        "chat_messages": [
            {
                "role": "ai",
                "content": "I've analyzed your schedule. Today, let's focus on two 45-minute deep work blocks instead of a long grind. How does that feel?"
            }
        ],
        "selected_reset": None,
        "selected_action": None,
        "logbook_detail": None,
        "show_triage": False,
        # Timer Core State
        "timer_total": 900,
        "timer_remaining": 900,
        "timer_end_time": None,
        "timer_running": False,
        "timer_title": "15-min Walk",
        "timer_preset": "walk",
        "timer_completed": False,
        "timer_auto_started": False,
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
        "name": "Maya O.",
        "initials": "MO",
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
            "capacity": 15 if score['support_level'] == "High" else 42,
            "priority": "CRITICAL" if score['support_level'] == "High" else "STABLE",
            "support_level": score['support_level'],
            "ai_analysis": st.session_state.get('system_data', {}).get('ai_prompt_context', "").split("Instructions for AI")[0][-150:] + "...",
            "recommended_action": plan['strategy_recommended'],
            "best_focus_window": "10:30 AM – 12:15 PM",
            "study_strategy": plan['strategy_recommended'],
        }
    return {
        "status": "High-Stakes Week",
        "capacity": 15,
        "priority": "CRITICAL",
        "support_level": "High",
        "ai_analysis": "Your sleep track shows a 3-day deficit. Combined with the upcoming Econ midterm, your baseline stress is elevated. We should prioritize restoration over rigid schedules.",
        "recommended_action": "Postpone 2pm Group Sync",
        "best_focus_window": "10:30 AM – 12:15 PM",
        "study_strategy": "Restoration First",
    }

def get_mock_sleep_data():
    """Return mock sleep history."""
    # ============================
    # BACKEND INTEGRATION POINT
    # Replace with: analytics.get_student_trends(student_id)
    # ============================
    return {
        "current": 5.2,
        "history": [4.8, 5.0, 4.2, 6.8, 7.2, 5.2],
        "days": ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon"],
        "deficit": -2.4,
        "insight": "Deep sleep was interrupted. Expect a significant mid-afternoon energy dip.",
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
            "title": "Microeconomics Midterm",
            "time": "09:00 AM",
            "when": "Tomorrow",
            "note": "Needs active retrieval practice",
            "color": "red",
            "course": "ECON 201",
        },
        {
            "title": "Sustainability Lab Report",
            "time": "05:00 PM",
            "when": "Friday",
            "note": "Polishing phase",
            "color": "blue",
            "course": "ENVS 110",
        },
    ]

def get_mock_resources():
    system_data = st.session_state.get('system_data')
    if system_data and 'resources' in system_data:
        mapped = []
        for r in system_data['resources']:
            words = r.get('name', 'Peer Tutor').split()
            initials = "".join([w[0].upper() for w in words[:2]]) if words else "PT"
            mapped.append({
                "category": "Academic Support",
                "name": r.get('name', 'Peer Tutor'),
                "initials": initials,
                "availability": "Available Today",
                "description": r.get('description', 'Student support resource')
            })
        if mapped:
            return mapped

    return [
        {
            "name": "Alex Hudson",
            "initials": "AH",
            "category": "Economics Peer Tutor",
            "availability": "Today",
            "description": "Drop-in peer tutoring for ECON 201 and statistical methods.",
        },
        {
            "name": "Counseling Center",
            "initials": "CC",
            "category": "Mental Health Support",
            "availability": "Same-day intake",
            "description": "Confidential individual counseling and de-escalation sessions.",
        },
    ]


def get_mock_logbook():
    """Return check-in history queried dynamically from SQLite database (check_ins table)."""
    try:
        conn = sqlite3.connect("student_support.db")
        df = pd.read_sql_query('''
            SELECT timestamp, sleep_hours, academic_pressure, energy_level, mood_score, workload_level, deadlines_count, optional_message 
            FROM check_ins 
            ORDER BY timestamp DESC
            LIMIT 10
        ''', conn)
        conn.close()

        if not df.empty:
            mood_map = {1: "Low", 2: "Okay", 3: "Good", 4: "Great", 5: "Okay", 6: "Okay", 7: "Good", 8: "Good", 9: "Great"}
            logbook_entries = []
            for _, row in df.iterrows():
                try:
                    dt = datetime.strptime(str(row['timestamp'])[:10], "%Y-%m-%d")
                    day_label = dt.strftime("%A").upper()
                    full_date = dt.strftime("%B %d, %Y")
                except Exception:
                    day_label = "CHECK-IN"
                    full_date = str(row['timestamp'])

                m_val = row['mood_score']
                m_str = mood_map.get(m_val, "Okay") if isinstance(m_val, int) else str(m_val)
                p_val = row['academic_pressure']
                status = "Needs Attention" if p_val >= 8 else ("Moderate" if p_val >= 5 else "Good")

                logbook_entries.append({
                    "date": day_label,
                    "full_date": full_date,
                    "pressure": int(row['academic_pressure']),
                    "energy": int(row['energy_level']),
                    "sleep": float(row['sleep_hours']),
                    "mood": m_str,
                    "workload": "High" if row['workload_level'] >= 7 else "Moderate",
                    "deadlines": int(row['deadlines_count']),
                    "message": str(row['optional_message']) if pd.notna(row['optional_message']) and str(row['optional_message']) != 'nan' else "",
                    "status": status,
                })
            return logbook_entries
    except Exception:
        pass

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
    ]


def get_mock_trends():
    """Return trend data dynamically calculated from SQLite dataset (check_ins table)."""
    try:
        conn = sqlite3.connect("student_support.db")
        df = pd.read_sql_query('''
            SELECT timestamp, sleep_hours, academic_pressure, energy_level, mood_score 
            FROM check_ins 
            ORDER BY id ASC
            LIMIT 7
        ''', conn)
        conn.close()

        if not df.empty and len(df) >= 2:
            days = []
            for ts in df['timestamp']:
                try:
                    dt = datetime.strptime(str(ts)[:10], "%Y-%m-%d")
                    days.append(dt.strftime("%a"))
                except Exception:
                    days.append("Day")

            return {
                "days": days,
                "pressure": [int(x) for x in df['academic_pressure']],
                "sleep": [float(x) for x in df['sleep_hours']],
                "energy": [int(x) for x in df['energy_level']],
                "mood_scores": [int(x) for x in df['mood_score']],
            }
    except Exception:
        pass

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
    """Render the top navigation bar with the custom logo."""
    student = get_mock_student()
    current = st.session_state.current_page
    logo_src = get_logo_b64()

    logo_html = f'<img src="{logo_src}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover;" alt="Harbor Logo">' if logo_src else '<div class="harbor-logo">H</div>'

    def active_cls(page_key):
        return "active" if (current == page_key or (current not in ["insights", "logbook", "resources"] and page_key == "home")) else ""

    render_html(f"""
    <div class="harbor-nav">
        <div class="harbor-nav-left" style="display: flex; align-items: center; gap: 14px;">
            {logo_html}
            <h1 style="font-family: var(--font-sans); font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0; line-height: 1; letter-spacing: 1.5px; text-transform: uppercase;">
                Harbor
            </h1>
        </div>
        <div class="harbor-nav-center">
            <a href="?page=home" target="_self" class="{active_cls('home')}">Home</a>
            <a href="?page=insights" target="_self" class="{active_cls('insights')}">Insights</a>
            <a href="?page=logbook" target="_self" class="{active_cls('logbook')}">Logbook</a>
            <a href="?page=resources" target="_self" class="{active_cls('resources')}">Resources</a>
        </div>
        <div class="harbor-nav-right">
            <div class="harbor-avatar">{student['initials']}</div>
            <span class="harbor-username">{student['name']}</span>
        </div>
    </div>
    """)



# ============================================================
# PAGE: HOME / DASHBOARD
# ============================================================

# ============================================================
# PAGE: HOME / DASHBOARD (Mockups 1, 2, 3 Redesign)
# ============================================================

def render_home():
    """Render the main home/dashboard page in a clean, minimal style matching Mockups 1, 2, 3."""
    inject_mouse_bubble()

    student = get_mock_student()
    triage = get_mock_triage()
    sleep_data = get_mock_sleep_data()
    deadlines = get_mock_deadlines()
    first_name = student['name'].split()[0]

    # --- Hero Section (Mockups 1 & 2) ---
    hero_col1, hero_col2 = st.columns([3.2, 1])
    with hero_col1:
        render_html(f"""
        <div style="margin-top: 24px; margin-bottom: 24px;">
            <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: var(--accent-blue); margin-bottom: 12px;">
                — MORNING ALIGNMENT &middot; TUESDAY
            </div>
            <h1 style="font-family: var(--font-serif); font-size: 48px; font-weight: 400; color: var(--text-primary); line-height: 1.15; margin: 0 0 12px 0;">
                Let's find your <span style="font-style: italic; color: #4A7FB5;">rhythm</span> today, {first_name}.
            </h1>
        </div>
        """)
    with hero_col2:
        render_html('<div style="height: 42px;"></div>')
        if st.button("Begin Check-in", key="home_begin_checkin", use_container_width=True):
            st.session_state.checkin_submitted = False
            st.session_state.show_triage = False
            st.session_state.current_page = "checkin"
            st.query_params["page"] = "checkin"
            st.rerun()

    # --- Tier 1 Grid: Status & Recovery (Mockup 1) ---
    t1_col1, t1_col2 = st.columns([1.5, 1], gap="medium")
    with t1_col1:
        render_status_card(triage)
    with t1_col2:
        render_recovery_card(sleep_data)
        render_intention_card()

    render_html('<div style="height: 12px;"></div>')

    # --- Tier 2 Grid: Pressure & Support (Mockup 2) ---
    t2_col1, t2_col2 = st.columns([1, 1], gap="medium")
    with t2_col1:
        render_upcoming_pressure(deadlines)
    with t2_col2:
        render_support_network()

    render_html('<div style="height: 12px;"></div>')

    # --- Tier 3 Grid: Unified Harmony AI Support & Contextual Deck (Mockup 3) ---
    render_unified_harmony_card()


def render_status_card(triage):
    """Render the main AI triage status card matching Mockup 1."""
    capacity = triage.get("capacity", 15)
    is_critical = capacity < 30 or triage.get("priority") in ["CRITICAL", "NEEDS ATTENTION"]
    badge_bg = "#FDF1F0" if is_critical else "#EBF6F0"
    badge_color = "#D9534F" if is_critical else "#388E3C"
    dot_color = "#D9534F" if is_critical else "#4AA564"

    render_html(f"""
    <div class="harbor-card" style="padding: 28px 32px; min-height: 290px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
            <div>
                <div class="card-label">CURRENT STATUS</div>
                <div style="font-family: var(--font-serif); font-size: 28px; font-weight: 500; color: var(--text-primary); margin-bottom: 12px;">
                    {triage['status']}
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                <div style="display: inline-flex; align-items: center; gap: 6px; background: {badge_bg}; color: {badge_color}; font-family: var(--font-sans); font-size: 13px; font-weight: 600; padding: 6px 16px; border-radius: 20px;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: {dot_color};"></span>
                    Capacity: {capacity}%
                </div>
                <div style="font-family: var(--font-sans); font-size: 9px; font-weight: 700; letter-spacing: 1.5px; color: var(--text-tertiary); text-transform: uppercase; margin-top: 2px;">
                    PRIORITY: {triage.get('priority', 'CRITICAL')}
                </div>
            </div>
        </div>
        
        <div style="display: flex; align-items: flex-start; gap: 10px; margin-top: 8px; margin-bottom: 20px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent-blue); margin-top: 5px; flex-shrink: 0;"></span>
            <div>
                <div style="font-family: var(--font-sans); font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                    AI Triage Analysis
                </div>
                <div style="font-family: var(--font-sans); font-size: 13.5px; color: var(--text-secondary); line-height: 1.6;">
                    {triage['ai_analysis']}
                </div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 12px; margin-top: auto;">
            <div style="background: var(--bg-blue-subtle); border-radius: var(--radius-md); padding: 12px 16px;">
                <div style="font-family: var(--font-sans); font-size: 9px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 4px;">
                    RECOMMENDED ACTION
                </div>
                <div style="font-family: var(--font-sans); font-size: 13px; font-weight: 600; color: var(--text-primary);">
                    {triage.get('recommended_action', 'Postpone 2pm Group Sync')}
                </div>
            </div>
            <div style="background: var(--bg-blue-subtle); border-radius: var(--radius-md); padding: 12px 16px;">
                <div style="font-family: var(--font-sans); font-size: 9px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 4px;">
                    COGNITIVE PEAK
                </div>
                <div style="font-family: var(--font-sans); font-size: 13px; font-weight: 600; color: var(--text-primary);">
                    {triage.get('best_focus_window', '10:30 AM – 12:15 PM')}
                </div>
            </div>
        </div>
    </div>
    """)


def render_recovery_card(sleep_data):
    """Render the recovery status card in deep blue matching Mockup 1."""
    deficit_val = sleep_data.get('deficit', -2.4)
    deficit_str = f"{deficit_val:+.1f}h" if isinstance(deficit_val, (int, float)) else str(deficit_val)
    
    bars_html = ""
    history = sleep_data.get('history', [4.8, 5.0, 4.2, 6.8, 7.2, 5.2])
    for i, val in enumerate(history):
        h = max(20, min(100, int((val / 8.0) * 100)))
        is_highlight = (i >= len(history) - 2)
        bg = "rgba(255,255,255,0.95)" if is_highlight else "rgba(255,255,255,0.35)"
        glow = "box-shadow: 0 0 10px rgba(255,255,255,0.4);" if is_highlight else ""
        bars_html += f'<div style="flex: 1; height: {h}%; background: {bg}; border-radius: 8px; {glow}"></div>'

    render_html(f"""
    <div class="harbor-card-blue" style="padding: 22px 26px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-family: var(--font-sans); font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.7);">
                REST DEFICIT
            </div>
            <div style="font-family: var(--font-sans); font-size: 24px; font-weight: 700; color: #FFFFFF;">
                {deficit_str}
            </div>
        </div>
        
        <div style="display: flex; align-items: flex-end; gap: 8px; height: 52px; margin: 14px 0 12px 0;">
            {bars_html}
        </div>

        <div style="font-family: var(--font-sans); font-size: 12px; line-height: 1.5; color: rgba(255,255,255,0.9);">
            {sleep_data['insight']}
        </div>
    </div>
    """)


def render_intention_card():
    """Render the daily intention card matching Mockup 1."""
    render_html("""
    <div class="harbor-card" style="padding: 18px 24px; margin-bottom: 0;">
        <div class="card-label" style="margin-bottom: 4px;">INTENTION</div>
        <div style="font-family: var(--font-serif); font-size: 20px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px;">
            Steady Progress
        </div>
        <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary);">
            Small steps count today.
        </div>
    </div>
    """)


def render_upcoming_pressure(deadlines):
    """Render upcoming pressure card matching Mockup 2."""
    timeline_html = ""
    for i, d in enumerate(deadlines):
        dot_color = "#E05656" if d.get('color') == "red" else "#4A7FB5"
        is_last = (i == len(deadlines) - 1)
        line_html = "" if is_last else f'<div style="position: absolute; left: 5px; top: 18px; width: 2px; height: calc(100% - 10px); background: #DDE5EE;"></div>'

        timeline_html += f"""
        <div style="position: relative; display: flex; align-items: flex-start; gap: 16px; padding: 10px 0;">
            <div style="position: relative; flex-shrink: 0; width: 12px; height: 12px; margin-top: 4px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid {dot_color}; background: #FFFFFF;"></div>
                {line_html}
            </div>
            <div style="flex: 1;">
                <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                    {d['title']}
                </div>
                <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary); margin-top: 2px;">
                    {d.get('note', '')} &middot; {d.get('when', '')}
                </div>
            </div>
            <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-tertiary); font-weight: 500;">
                {d.get('time', '')}
            </div>
        </div>
        """

    render_html(f"""
    <div class="harbor-card" style="padding: 26px 30px; min-height: 200px;">
        <div style="font-family: var(--font-serif); font-size: 22px; font-weight: 500; color: var(--text-primary); margin-bottom: 16px;">
            Upcoming Pressure
        </div>
        {timeline_html}
    </div>
    """)


def render_support_network():
    """Render the support network card matching Mockup 2 with 24/7 helpline resources."""
    resources = get_mock_resources()[:1]
    r = resources[0] if resources else {
        "name": "Alex Hudson",
        "initials": "AH",
        "category": "Economics Peer Tutor",
        "availability": "Today",
    }

    render_html(f"""
    <div class="harbor-card" style="padding: 24px 28px; min-height: 200px;">
        <div style="font-family: var(--font-serif); font-size: 22px; font-weight: 500; color: var(--text-primary); margin-bottom: 14px;">
            Support Network
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-blue-subtle); border-radius: var(--radius-lg); padding: 14px 18px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: #2B5B84; display: flex; align-items: center; justify-content: center; color: white; font-family: var(--font-sans); font-size: 15px; font-weight: 600;">
                    {r['initials']}
                </div>
                <div>
                    <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                        {r['name']}
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                        {r['category']} &middot; {r.get('availability', 'Today')}
                    </div>
                </div>
            </div>
    """)

    if st.button("Request", key="req_support_network_primary", use_container_width=True):
        st.session_state.selected_action = "request_tutor"
        st.session_state.current_page = "resources"
        st.rerun()

    render_html("""
        </div>

        <!-- 24/7 Helplines & Emergency Support -->
        <div style="border-top: 1px solid var(--border-subtle); padding-top: 12px; margin-top: 10px;">
            <div style="font-family: var(--font-sans); font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 10px;">
                24/7 HELPLINES & CRISIS SUPPORT
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div>
                        <div style="font-family: var(--font-sans); font-size: 12.5px; font-weight: 600; color: var(--text-primary);">
                            💬 Crisis Text Line
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 11px; color: var(--text-tertiary);">
                            Text HOME to 741741
                        </div>
                    </div>
                    <span style="font-family: var(--font-sans); font-size: 11.5px; font-weight: 700; color: #3B6B9A; background: #E8EFF6; padding: 4px 10px; border-radius: 6px;">
                        📲 741741
                    </span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div>
                        <div style="font-family: var(--font-sans); font-size: 12.5px; font-weight: 600; color: var(--text-primary);">
                            🏫 Campus Wellness
                        </div>
                        <div style="font-family: var(--font-sans); font-size: 11px; color: var(--text-tertiary);">
                            Support Center
                        </div>
                    </div>
                    <a href="tel:18002738255" style="font-family: var(--font-sans); font-size: 12px; font-weight: 700; color: #3B6B9A; text-decoration: none; background: #E8EFF6; padding: 4px 10px; border-radius: 6px;">
                        📞 (800) 273-8255
                    </a>
                </div>
            </div>
        </div>
    </div>
    """)


def render_unified_harmony_card():
    """Render Tier 3 Unified Harmony AI Support & Contextual Deck Card matching Mockup 3."""
    with st.container(border=True):
        render_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border-subtle); margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px; font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #4A7FB5; box-shadow: 0 0 8px rgba(74, 127, 181, 0.6);"></span>
                Harmony is active
            </div>
            <div style="font-family: var(--font-sans); font-size: 10px; font-weight: 600; letter-spacing: 2px; color: var(--text-tertiary); text-transform: uppercase;">
                ENCRYPTED CHANNEL
            </div>
        </div>
        """)

        c_chat, c_deck = st.columns([1.3, 1], gap="large")

        with c_chat:
            # Chat Messages
            chat_html = '<div style="max-height: 280px; overflow-y: auto; padding: 4px 0 12px 0;">'
            for msg in st.session_state.chat_messages:
                if msg["role"] == "ai":
                    chat_html += f"""
                    <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 14px;">
                        <div style="width: 32px; height: 32px; border-radius: 50%; background: #D6E4F0; flex-shrink: 0; margin-top: 2px;"></div>
                        <div style="background: #EEF2F7; border-radius: 4px 18px 18px 18px; padding: 14px 18px; font-family: var(--font-sans); font-size: 13.5px; line-height: 1.6; color: var(--text-primary); max-width: 85%;">
                            {msg["content"]}
                        </div>
                    </div>
                    """
                else:
                    chat_html += f"""
                    <div style="display: flex; align-items: flex-start; justify-content: flex-end; gap: 10px; margin-bottom: 14px;">
                        <div style="background: #2B5B84; color: #FFFFFF; border-radius: 18px 4px 18px 18px; padding: 14px 18px; font-family: var(--font-sans); font-size: 13.5px; line-height: 1.6; max-width: 85%;">
                            {msg["content"]}
                        </div>
                        <div style="width: 32px; height: 32px; border-radius: 50%; background: #CBD5E1; flex-shrink: 0; margin-top: 2px;"></div>
                    </div>
                    """
            chat_html += '</div>'
            render_html(chat_html)

            # Chat Input
            user_input = st.chat_input("Type your thoughts...", key="home_chat_input")
            if user_input:
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                response = get_mock_chat_response(user_input)
                st.session_state.chat_messages.append({"role": "ai", "content": response})
                st.rerun()

        with c_deck:
            render_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-family: var(--font-sans); font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--text-tertiary);">
                    CONTEXTUAL DECK
                </div>
                <div style="font-family: var(--font-sans); font-size: 12px; font-weight: 600; color: var(--accent-blue); cursor: pointer;">
                    Edit
                </div>
            </div>
            """)

            # Interactive Deck Action Pills (Mockup 3)
            if st.button("● Deep Work Timer  ·  45:00", key="deck_timer_45", use_container_width=True):
                start_timer_session("deep_45", "45m Deep Work", 2700, auto_start=True)

            if st.button("● 15-min Walk  ·  15:00", key="deck_timer_15", use_container_width=True):
                start_timer_session("walk", "15-min Walk", 900, auto_start=True)

            if st.button("● 2-min Breathing  ·  02:00", key="deck_timer_2", use_container_width=True):
                start_timer_session("breathe", "2-min Breathing", 120, auto_start=True)


def render_chat_section(minimal=False):
    """Legacy helper for embedded chat."""
    render_unified_harmony_card()


def render_action_plan():
    """Render the contextual action plan panel with timer dispatches."""
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
                if action_keys[i] == "focus":
                    start_timer_session("focus_25", "25m Focus Block", 1500)
                elif action_keys[i] == "reset":
                    start_timer_session("walk", "15-min Walk", 900)
                else:
                    st.rerun()


def render_reset_card():
    """Render the de-escalation reset card with direct timer routing."""
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
        ("🚶 15-min Walk", "walk", "15-min Walk", 900),
        ("🫁 2-min Breathing", "breathe", "2-min Breathing", 120),
        ("📵 10-min Screen Break", "screen", "10-min Screen Break", 600),
        ("😴 Strategic Nap", "nap", "Strategic Nap", 1200),
    ]
    for i, (label, key, title, duration) in enumerate(resets):
        with reset_cols[i % 2]:
            if st.button(label, key=f"reset_{key}", use_container_width=True):
                start_timer_session(key, title, duration, auto_start=True)


# ============================================================
# PAGE: DEDICATED TIMER & COUNTDOWN ENGINE
# ============================================================

@st.fragment(run_every=1 if st.session_state.get("timer_running", False) else None)
def render_timer_engine():
    """Scoped auto-refreshing timer countdown engine."""
    now = time.time()

    # Wall-clock delta calculation
    if st.session_state.get("timer_running", False):
        end_time = st.session_state.get("timer_end_time", now)
        remaining = max(0, int(round(end_time - now)))
        st.session_state.timer_remaining = remaining
        if remaining == 0:
            st.session_state.timer_running = False
            st.session_state.timer_completed = True
            st.rerun()
    else:
        remaining = st.session_state.get("timer_remaining", 900)

    total = max(1, st.session_state.get("timer_total", 900))
    time_str = format_timer_display(remaining)
    progress_frac = compute_timer_progress(total, remaining)

    # SVG Circular Progress Ring
    radius = 110
    circumference = 2 * 3.14159265 * radius
    dashoffset = circumference * (1.0 - progress_frac)
    is_completed = st.session_state.get("timer_completed", False)
    is_running = st.session_state.get("timer_running", False)
    stroke_color = "#4AA564" if is_completed else "#4A7FB5"
    status_text = "Completed" if is_completed else ("Running" if is_running else "Paused")

    render_html(f"""
    <div class="harbor-card" style="text-align: center; padding: 36px 24px; max-width: 600px; margin: 0 auto;">
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="position: relative; width: 260px; height: 260px; display: flex; align-items: center; justify-content: center;">
                <svg width="260" height="260" viewBox="0 0 260 260" style="transform: rotate(-90deg);">
                    <circle cx="130" cy="130" r="{radius}" fill="none" stroke="var(--bg-blue-subtle)" stroke-width="12" />
                    <circle cx="130" cy="130" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="12"
                            stroke-dasharray="{circumference}" stroke-dashoffset="{dashoffset}"
                            stroke-linecap="round" style="transition: stroke-dashoffset 0.6s ease;" />
                </svg>
                <div style="position: absolute; text-align: center;">
                    <div style="font-family: var(--font-sans); font-size: 48px; font-weight: 700; color: var(--text-primary); letter-spacing: -1px;">
                        {time_str}
                    </div>
                    <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: {'#4AA564' if is_completed else 'var(--text-tertiary)'}; margin-top: 4px;">
                        {status_text}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)

    if is_completed:
        render_html("""
        <div style="background: #EBF6F0; border: 1px solid #C3E6CB; border-radius: var(--radius-md); padding: 16px 20px; text-align: center; max-width: 600px; margin: 12px auto;">
            <div style="font-family: var(--font-sans); font-size: 14px; font-weight: 600; color: #2E7D32;">
                🎉 Session Completed! Great job taking care of your rhythm today.
            </div>
        </div>
        """)

    # Control Action Buttons
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])

    with ctrl_col1:
        if is_running:
            if st.button("⏸ Pause", key="timer_pause", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_end_time = None
                st.rerun()
        else:
            btn_label = "▶ Start" if remaining == total else "▶ Resume"
            if st.button(btn_label, key="timer_start", use_container_width=True):
                st.session_state.timer_running = True
                st.session_state.timer_completed = False
                st.session_state.timer_end_time = time.time() + st.session_state.timer_remaining
                st.rerun()

    with ctrl_col2:
        if st.button("⏹ Stop", key="timer_stop", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_end_time = None
            st.session_state.timer_remaining = st.session_state.timer_total
            st.session_state.timer_completed = False
            st.rerun()

    with ctrl_col3:
        if st.button("🔄 Reset", key="timer_reset", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_end_time = None
            st.session_state.timer_remaining = st.session_state.timer_total
            st.session_state.timer_completed = False
            st.rerun()

    # Time Adjustment Buttons
    adj_col1, adj_col2, adj_col3 = st.columns(3)
    with adj_col1:
        if st.button("+1 Min", key="timer_plus_1m", use_container_width=True):
            st.session_state.timer_total += 60
            st.session_state.timer_remaining += 60
            if st.session_state.timer_running:
                st.session_state.timer_end_time = time.time() + st.session_state.timer_remaining
            st.rerun()
    with adj_col2:
        if st.button("+5 Min", key="timer_plus_5m", use_container_width=True):
            st.session_state.timer_total += 300
            st.session_state.timer_remaining += 300
            if st.session_state.timer_running:
                st.session_state.timer_end_time = time.time() + st.session_state.timer_remaining
            st.rerun()
    with adj_col3:
        if st.button("-1 Min", key="timer_minus_1m", use_container_width=True):
            new_rem = max(0, st.session_state.timer_remaining - 60)
            st.session_state.timer_remaining = new_rem
            if st.session_state.timer_running:
                st.session_state.timer_end_time = time.time() + new_rem
            st.rerun()


def render_timer():
    """Render the dedicated timer page."""
    inject_mouse_bubble()

    col_back, col_badge = st.columns([2, 1])
    with col_back:
        if st.button("← Return to Pulse (Home)", key="timer_return_home"):
            st.session_state.current_page = "home"
            st.rerun()

    with col_badge:
        title = st.session_state.get("timer_title", "Reset Session")
        st.markdown(f"""
        <div style="text-align: right; padding-top: 6px;">
            <span style="display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-sans); font-size: 13px; font-weight: 600; color: var(--accent-blue); background: var(--bg-blue-subtle); padding: 4px 12px; border-radius: 16px;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background: var(--accent-blue);"></span>
                {title}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    # Scoped timer engine
    render_timer_engine()

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # Preset switcher bar
    st.markdown("""
    <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 12px; text-align: center;">
        QUICK PRESETS
    </div>
    """, unsafe_allow_html=True)

    preset_cols = st.columns(6)
    presets = [
        ("🚶 15m Walk", "walk", "15-min Walk", 900),
        ("🫁 2m Breathe", "breathe", "2-min Breathing", 120),
        ("📵 10m Screen", "screen", "10-min Screen Break", 600),
        ("😴 20m Nap", "nap", "Strategic Nap", 1200),
        ("🍅 25m Focus", "focus_25", "25m Focus Block", 1500),
        ("🎯 45m Deep", "deep_45", "45m Deep Work", 2700),
    ]
    for i, (label, key, p_title, duration) in enumerate(presets):
        with preset_cols[i]:
            if st.button(label, key=f"quick_preset_{key}", use_container_width=True):
                start_timer_session(key, p_title, duration, auto_start=True)



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

    # Summary metrics with white text on dark blue card background
    render_html(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <div style="background: #2B5B84; border-radius: 16px; padding: 16px 20px; text-align: center; color: #FFFFFF; box-shadow: 0 2px 8px rgba(43,91,132,0.15);">
            <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: rgba(255,255,255,0.8); margin-bottom: 6px;">MOOD</div>
            <div style="font-family: var(--font-sans); font-size: 22px; font-weight: 700; color: #FFFFFF;">{data.get('mood', 'Okay')}</div>
        </div>
        <div style="background: #2B5B84; border-radius: 16px; padding: 16px 20px; text-align: center; color: #FFFFFF; box-shadow: 0 2px 8px rgba(43,91,132,0.15);">
            <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: rgba(255,255,255,0.8); margin-bottom: 6px;">ENERGY</div>
            <div style="font-family: var(--font-sans); font-size: 22px; font-weight: 700; color: #FFFFFF;">{data.get('energy_level', 4)}/10</div>
        </div>
        <div style="background: #2B5B84; border-radius: 16px; padding: 16px 20px; text-align: center; color: #FFFFFF; box-shadow: 0 2px 8px rgba(43,91,132,0.15);">
            <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: rgba(255,255,255,0.8); margin-bottom: 6px;">SLEEP</div>
            <div style="font-family: var(--font-sans); font-size: 22px; font-weight: 700; color: #FFFFFF;">{data.get('sleep_hours', 5.0)}h</div>
        </div>
        <div style="background: #2B5B84; border-radius: 16px; padding: 16px 20px; text-align: center; color: #FFFFFF; box-shadow: 0 2px 8px rgba(43,91,132,0.15);">
            <div style="font-family: var(--font-sans); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: rgba(255,255,255,0.8); margin-bottom: 6px;">PRESSURE</div>
            <div style="font-family: var(--font-sans); font-size: 22px; font-weight: 700; color: #FFFFFF;">{data.get('academic_pressure', 8)}/10</div>
        </div>
    </div>
    """)

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

    render_html("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; margin-top: 12px;">
        <div>
            <div class="section-title" style="margin-bottom: 4px;">AI Support</div>
            <div style="font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary);">
                <span class="chat-active-dot"></span>Harmony is active
            </div>
        </div>
    </div>
    """)

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
        render_html(chat_html)

        # Chat input
        user_input = st.chat_input("Type your thoughts...", key="full_chat_input")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            response = get_mock_chat_response(user_input)
            st.session_state.chat_messages.append({"role": "ai", "content": response})
            st.rerun()

    with col_deck:
        # Contextual Deck
        render_html("""
        <div class="harbor-card">
            <div class="card-label">CONTEXTUAL DECK</div>
            <div style="height: 12px;"></div>
        """)

        actions = [
            {"icon": "🍅", "text": "Focus Block", "meta": "25:00", "key": "deck_focus"},
            {"icon": "🧘", "text": "Guided Reset", "meta": "15:00", "key": "deck_reset"},
            {"icon": "📚", "text": "Peer Tutoring", "meta": "ACTIVE", "key": "deck_tutor"},
            {"icon": "✉️", "text": "Extension Draft", "meta": "Ready", "key": "deck_ext"},
        ]

        for a in actions:
            render_html(f"""
            <div class="action-card">
                <span class="action-icon">{a['icon']}</span>
                <span class="action-text">{a['text']}</span>
                <span class="action-meta">{a['meta']}</span>
            </div>
            """)

        render_html('</div>')

        # Quick suggestion buttons
        render_html("""
        <div class="harbor-card" style="padding: 20px;">
            <div class="card-label">QUICK PROMPTS</div>
            <div style="height: 8px;"></div>
        </div>
        """)

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
        chart_layout_mood = {k: v for k, v in chart_layout.items() if k != "yaxis"}
        fig_mood.update_layout(
            **chart_layout_mood,
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
    else:
        hide_mouse_bubble()
        if page == "checkin":
            render_checkin()
        elif page == "chatbot":
            render_chatbot()
        elif page == "insights":
            render_insights()
        elif page == "logbook":
            render_logbook()
        elif page == "resources":
            render_resources()
        elif page == "timer":
            render_timer()
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

