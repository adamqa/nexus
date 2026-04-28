import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import run_classification_logic, run_anomaly_logic
import io
import streamlit.components.v1 as components
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NEXUS · AI Inventory Risk Cockpit",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⬡"
)

# ============================================================
#   NEXUS ULTRA-PREMIUM CSS — Palantir + Tesla + McKinsey AI
# ============================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&family=Exo+2:wght@300;400;500;600;700;800&display=swap');

/* ================================================================
   ROOT DESIGN TOKENS — Cyberpunk Command Center
================================================================ */
:root {
    --bg-void:     #020509;
    --bg-base:     #050B14;
    --bg-panel:    #080F1A;
    --bg-card:     #0B1220;
    --bg-card2:    #0D1628;
    --bg-elevated: #101830;
    --border:      rgba(0,217,255,0.06);
    --border-md:   rgba(0,217,255,0.12);
    --border-act:  rgba(0,217,255,0.28);

    --txt:         #B8D4F0;
    --txt-bright:  #E8F3FF;
    --txt-muted:   #5A7A9A;
    --txt-dim:     #2A4060;

    --cyan:        #00D9FF;
    --cyan-dim:    rgba(0,217,255,0.7);
    --cyan-glow:   rgba(0,217,255,0.15);
    --cyan-pulse:  rgba(0,217,255,0.08);
    --blue:        #008CFF;
    --blue-glow:   rgba(0,140,255,0.12);
    --green:       #00D26A;
    --green-glow:  rgba(0,210,106,0.12);
    --orange:      #FF9D2E;
    --orange-glow: rgba(255,157,46,0.12);
    --red:         #FF3B3B;
    --red-glow:    rgba(255,59,59,0.15);
    --purple:      #9B5CF6;

    --r-xl:  18px;
    --r-lg:  12px;
    --r-md:  8px;
    --r-sm:  5px;

    --t-fast: all 0.15s cubic-bezier(0.4,0,0.2,1);
    --t:      all 0.24s cubic-bezier(0.4,0,0.2,1);
    --t-slow: all 0.4s cubic-bezier(0.4,0,0.2,1);

    --shadow-sm: 0 2px 12px rgba(0,0,0,0.5);
    --shadow:    0 4px 24px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.025) inset;
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.7), 0 1px 0 rgba(255,255,255,0.03) inset;
    --glow-cyan: 0 0 20px rgba(0,217,255,0.12), 0 0 1px rgba(0,217,255,0.5);
    --glow-red:  0 0 20px rgba(255,59,59,0.18), 0 0 1px rgba(255,59,59,0.6);
}

/* ================================================================
   GLOBAL RESET
================================================================ */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif !important;
    color: var(--txt);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body { background: var(--bg-void); }

/* Animated grid background */
.stApp {
    background:
        radial-gradient(ellipse 120% 60% at -10% -5%, rgba(0,100,200,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 80% 50% at 110% 5%, rgba(0,217,255,0.05) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 50% 100%, rgba(0,80,180,0.04) 0%, transparent 60%),
        linear-gradient(rgba(0,217,255,0.012) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,217,255,0.012) 1px, transparent 1px),
        #050B14;
    background-size: auto, auto, auto, 32px 32px, 32px 32px, 100%;
    min-height: 100vh;
}

#MainMenu, footer { visibility: hidden; }

header[data-testid="stHeader"] {
    visibility: visible !important;
    background: rgba(5,11,20,0.97) !important;
    backdrop-filter: blur(20px) saturate(180%);
    border-bottom: 1px solid var(--border) !important;
    height: 48px !important;
    z-index: 999;
}

.block-container {
    padding: 1.4rem 2rem 3rem !important;
    max-width: 1800px !important;
}

/* ================================================================
   TYPOGRAPHY
================================================================ */
h1, h2, h3, h4 {
    font-family: 'Orbitron', sans-serif !important;
    color: var(--txt-bright) !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

h1 { font-size: 1.7rem !important; font-weight: 800 !important; letter-spacing: 0.1em; }
h2 { font-size: 1.2rem !important; font-weight: 700 !important; }
h3 { font-size: 0.95rem !important; font-weight: 600 !important; }

p, label, span { color: var(--txt); line-height: 1.6; }

[data-testid="stMetricValue"], code, kbd {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ================================================================
   SIDEBAR — NEXUS COMMAND PANEL
================================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #040810 0%, #060C18 100%) !important;
    border-right: 1px solid rgba(0,217,255,0.08) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.8), 1px 0 0 rgba(0,217,255,0.04) !important;
    width: 235px !important;
    overflow: hidden;
}

/* Top accent line */
section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 5%, var(--cyan) 30%, var(--blue) 70%, transparent 95%);
    opacity: 0.9;
    z-index: 10;
}

/* Vertical glow on left edge */
section[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 1px;
    background: linear-gradient(180deg, var(--cyan), var(--blue), transparent);
    opacity: 0.15;
}

section[data-testid="stSidebar"] * { color: var(--txt) !important; }

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: var(--cyan) !important;
    -webkit-text-fill-color: var(--cyan) !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.14em;
    text-shadow: 0 0 24px rgba(0,217,255,0.5), 0 0 48px rgba(0,217,255,0.2);
}

section[data-testid="stSidebar"] hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-act), transparent);
    margin: 0.6rem 0;
    opacity: 0.6;
}

/* Sidebar radio label */
section[data-testid="stSidebar"] .stRadio > label {
    font-size: 0.6rem !important;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--txt-dim) !important;
    font-weight: 700 !important;
    font-family: 'Orbitron', sans-serif !important;
}

section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--txt-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.025em;
    font-family: 'Exo 2', sans-serif !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--r-md);
    padding: 10px 12px !important;
    margin-bottom: 2px !important;
    transition: var(--t);
    position: relative;
    overflow: hidden;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label::before {
    content: '';
    position: absolute;
    top: 0; bottom: 0; left: 0;
    width: 0;
    background: linear-gradient(90deg, rgba(0,217,255,0.08), transparent);
    transition: width 0.3s ease;
    border-radius: var(--r-md);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover::before { width: 100%; }

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    border-color: rgba(0,217,255,0.12);
    background: rgba(0,217,255,0.03);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(0,217,255,0.07);
    border-color: rgba(0,217,255,0.2);
    border-left: 2px solid var(--cyan);
    box-shadow: inset 3px 0 0 rgba(0,217,255,0.25), 0 0 12px rgba(0,217,255,0.04);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)
    [data-testid="stMarkdownContainer"] p {
    color: var(--cyan) !important;
    font-weight: 600 !important;
    text-shadow: 0 0 8px rgba(0,217,255,0.3);
}

/* ================================================================
   KPI / METRIC CARDS
================================================================ */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid rgba(0,217,255,0.18) !important;
    border-radius: var(--r-xl) !important;
    padding: 20px 22px !important;
    box-shadow: var(--shadow);
    transition: var(--t);
    position: relative;
    overflow: hidden;
    animation: slideUp 0.4s cubic-bezier(0.4,0,0.2,1) both;
}

[data-testid="metric-container"]::before {
    content: "";
    position: absolute;
    top: -1px; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    opacity: 0.6;
}

[data-testid="metric-container"]::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 40px;
    background: linear-gradient(180deg, transparent, rgba(0,217,255,0.02));
    pointer-events: none;
}

[data-testid="metric-container"]:hover {
    border-top-color: var(--cyan) !important;
    border-color: rgba(0,217,255,0.2) !important;
    transform: translateY(-4px) scale(1.005);
    box-shadow: var(--shadow-lg), var(--glow-cyan);
}

[data-testid="stMetricLabel"] > div {
    color: var(--txt-muted) !important;
    font-size: 0.62rem !important;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 700 !important;
    font-family: 'Orbitron', sans-serif !important;
}

[data-testid="stMetricValue"] > div {
    color: var(--txt-bright) !important;
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.03em;
    line-height: 1;
    text-shadow: 0 0 20px rgba(0,217,255,0.15);
}

[data-testid="stMetricDelta"] { font-size: 0.72rem !important; }

/* ================================================================
   GLASS PANEL WRAPPERS
================================================================ */
div[data-testid="stVerticalBlock"] > div:has(.stPlotlyChart),
div[data-testid="stVerticalBlock"] > div:has(.stDataFrame) {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    padding: 20px;
    box-shadow: var(--shadow);
    transition: var(--t);
    animation: slideUp 0.45s cubic-bezier(0.4,0,0.2,1) both;
}

div[data-testid="stVerticalBlock"] > div:has(.stPlotlyChart):hover,
div[data-testid="stVerticalBlock"] > div:has(.stDataFrame):hover {
    border-color: var(--border-md);
    box-shadow: var(--shadow-lg), 0 0 30px rgba(0,217,255,0.04);
}

/* ================================================================
   TABS — Command Interface Style
================================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px;
    background: rgba(5,11,20,0.9);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 5px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
}

.stTabs [data-baseweb="tab"] {
    height: 36px;
    padding: 0 20px;
    border-radius: var(--r-md);
    color: var(--txt-muted) !important;
    font-weight: 600;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'Orbitron', sans-serif !important;
    transition: var(--t);
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--txt-bright) !important;
    background: rgba(0,217,255,0.04);
}

.stTabs [aria-selected="true"] {
    background: rgba(0,217,255,0.1) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(0,217,255,0.22) !important;
    box-shadow: 0 0 16px rgba(0,217,255,0.1), inset 0 1px 0 rgba(0,217,255,0.15) !important;
    text-shadow: 0 0 8px rgba(0,217,255,0.4);
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ================================================================
   BUTTONS — Premium Command Style
================================================================ */
.stButton > button,
.stDownloadButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border: 1px solid rgba(0,217,255,0.3) !important;
    border-radius: var(--r-md) !important;
    padding: 0.7rem 1.8rem !important;
    color: var(--cyan) !important;
    background: rgba(0,217,255,0.06) !important;
    transition: var(--t) !important;
    box-shadow: 0 0 0 transparent !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before,
.stDownloadButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.08), transparent);
    transition: left 0.4s ease;
}

.stButton > button:hover::before,
.stDownloadButton > button:hover::before { left: 100%; }

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: rgba(0,217,255,0.14) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 24px rgba(0,217,255,0.2), 0 4px 16px rgba(0,0,0,0.4) !important;
    transform: translateY(-2px) !important;
    color: #fff !important;
    text-shadow: 0 0 8px rgba(0,217,255,0.6);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #9B0000 0%, #FF1A1A 50%, #FF3B3B 100%) !important;
    border-color: rgba(255,59,59,0.5) !important;
    color: #fff !important;
    box-shadow: 0 0 24px rgba(255,59,59,0.3) !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #CC0000 0%, #FF2222 50%, #FF5555 100%) !important;
    box-shadow: 0 0 36px rgba(255,59,59,0.45), 0 4px 16px rgba(0,0,0,0.5) !important;
}

.stButton > button:active { transform: translateY(0) scale(0.98) !important; }

/* ================================================================
   SLIDERS — Precision Controls
================================================================ */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, var(--cyan), var(--blue)) !important;
    box-shadow: 0 0 8px rgba(0,217,255,0.4);
}

[data-testid="stSlider"] .stSlider > div { accent-color: var(--cyan); }

/* ================================================================
   INPUTS — Neon Style
================================================================ */
.stTextInput label, .stSelectbox label,
.stMultiSelect label, .stNumberInput label,
.stFileUploader label {
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    color: var(--txt-muted) !important;
    font-family: 'Orbitron', sans-serif !important;
}

.stTextInput input, .stNumberInput input, textarea {
    background: rgba(4,8,16,0.95) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-md) !important;
    color: var(--txt-bright) !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    transition: var(--t);
    font-family: 'JetBrains Mono', monospace !important;
    box-shadow: inset 0 1px 0 rgba(0,0,0,0.4);
}

.stTextInput input:focus, .stNumberInput input:focus, textarea:focus {
    border-color: rgba(0,217,255,0.45) !important;
    box-shadow: 0 0 0 3px rgba(0,217,255,0.07), inset 0 1px 0 rgba(0,0,0,0.4) !important;
    outline: none;
}

div[data-baseweb="select"] > div {
    background: rgba(4,8,16,0.95) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-md) !important;
    color: var(--txt-bright) !important;
    transition: var(--t);
}

div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(0,217,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,217,255,0.07) !important;
}

/* ================================================================
   FILE UPLOADER — Premium Drop Zone
================================================================ */
[data-testid="stFileUploader"] {
    background: rgba(4,8,16,0.8);
    border: 2px dashed rgba(0,217,255,0.15) !important;
    border-radius: var(--r-lg);
    padding: 24px;
    transition: var(--t);
    position: relative;
}

[data-testid="stFileUploader"]::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: var(--r-lg);
    background: linear-gradient(135deg, rgba(0,217,255,0.03), transparent, rgba(0,140,255,0.03));
    pointer-events: none;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,217,255,0.35) !important;
    background: rgba(0,217,255,0.015);
    box-shadow: 0 0 24px rgba(0,217,255,0.06);
}

[data-testid="stFileUploader"] * { color: var(--txt) !important; }

/* ================================================================
   DATAFRAME / TABLE — Command Table
================================================================ */
.stDataFrame {
    border: 1px solid var(--border-md) !important;
    border-radius: var(--r-lg) !important;
    overflow: hidden;
    box-shadow: var(--shadow);
}

thead tr th {
    background: rgba(4,8,16,0.98) !important;
    color: var(--cyan) !important;
    font-weight: 700 !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    border-bottom: 1px solid rgba(0,217,255,0.15) !important;
    padding: 12px 14px !important;
    font-family: 'Orbitron', sans-serif !important;
}

tbody tr { transition: background 0.12s ease; }
tbody tr:nth-child(even) { background: rgba(255,255,255,0.008) !important; }
tbody tr:hover { background: rgba(0,217,255,0.03) !important; }

tbody tr td {
    padding: 9px 14px !important;
    border-bottom: 1px solid rgba(255,255,255,0.025) !important;
    color: var(--txt) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ================================================================
   ALERTS — Status Panels
================================================================ */
.stAlert {
    border-radius: var(--r-lg) !important;
    border-left-width: 3px !important;
    backdrop-filter: blur(10px);
}

.stSuccess {
    background: rgba(0,210,106,0.05) !important;
    border: 1px solid rgba(0,210,106,0.15) !important;
    border-left: 3px solid var(--green) !important;
    box-shadow: 0 0 16px rgba(0,210,106,0.06) !important;
}

.stWarning {
    background: rgba(255,157,46,0.05) !important;
    border: 1px solid rgba(255,157,46,0.15) !important;
    border-left: 3px solid var(--orange) !important;
}

.stError {
    background: rgba(255,59,59,0.06) !important;
    border: 1px solid rgba(255,59,59,0.15) !important;
    border-left: 3px solid var(--red) !important;
    box-shadow: 0 0 16px rgba(255,59,59,0.06) !important;
}

.stInfo {
    background: rgba(0,217,255,0.04) !important;
    border: 1px solid rgba(0,217,255,0.12) !important;
    border-left: 3px solid var(--cyan) !important;
}

/* ================================================================
   CHARTS
================================================================ */
.js-plotly-plot { border-radius: var(--r-lg); overflow: hidden; }
.stPlotlyChart  { border-radius: var(--r-lg); }

/* ================================================================
   SCROLLBAR — Neon Track
================================================================ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(4,8,16,0.95); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(0,217,255,0.5), rgba(0,140,255,0.3));
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, var(--cyan), var(--blue)); }

/* ================================================================
   DIVIDERS
================================================================ */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.18), transparent);
    margin: 1.4rem 0;
}

/* ================================================================
   SUBHEADER accent
================================================================ */
.stApp h3[data-testid="stHeading"],
.stApp [data-testid="stMarkdownContainer"] h3 {
    border-left: 2px solid var(--cyan);
    padding-left: 14px;
    margin: 1.6rem 0 0.9rem;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-shadow: 0 0 16px rgba(0,217,255,0.2);
}

/* ================================================================
   SPINNER
================================================================ */
.stSpinner > div { border-top-color: var(--cyan) !important; }

/* ================================================================
   KEYFRAME ANIMATIONS
================================================================ */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes scanRight {
    0%   { left: -100%; }
    100% { left: 200%; }
}

@keyframes pulseGlow {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px currentColor; }
    50%       { opacity: 0.5; box-shadow: 0 0 2px currentColor; }
}

@keyframes blinkDot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.75); }
}

@keyframes glitchShift {
    0%, 100% { transform: skewX(0deg); }
    33%       { transform: skewX(0.4deg); }
    66%       { transform: skewX(-0.4deg); }
}

@keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}

@keyframes borderPulse {
    0%, 100% { border-color: rgba(0,217,255,0.14); }
    50%       { border-color: rgba(0,217,255,0.28); }
}

/* Apply entrance animations */
.stTabs, .element-container, .stPlotlyChart,
.stDataFrame, [data-testid="metric-container"] {
    animation: slideUp 0.4s cubic-bezier(0.4,0,0.2,1) both;
}

/* ================================================================
   LOGIN SCREEN — Industrial Glassmorphism
================================================================ */
.login-overlay {
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 20%, rgba(0,60,160,0.15) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,200,255,0.08) 0%, transparent 50%),
        linear-gradient(rgba(0,217,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,217,255,0.015) 1px, transparent 1px),
        #030710;
    background-size: auto, auto, 32px 32px, 32px 32px, 100%;
    z-index: -1;
    animation: fadeIn 0.8s ease;
}

/* Scanline animation */
.login-overlay::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.3), transparent);
    animation: scanline 6s linear infinite;
    opacity: 0.6;
}

.login-wrapper {
    min-height: 90vh;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.6s cubic-bezier(0.4,0,0.2,1) both;
}

.login-container {
    width: 100%;
    max-width: 440px;
    margin: 0 auto;
    padding: 50px 44px 54px;
    background: linear-gradient(160deg,
        rgba(8,15,30,0.98) 0%,
        rgba(5,11,22,0.99) 50%,
        rgba(8,12,24,0.98) 100%
    );
    border: 1px solid rgba(0,217,255,0.12);
    border-top: 1px solid rgba(0,217,255,0.4);
    border-radius: 22px;
    box-shadow:
        0 40px 100px rgba(0,0,0,0.8),
        0 0 80px rgba(0,217,255,0.06),
        0 0 1px rgba(0,217,255,0.3),
        inset 0 1px 0 rgba(0,217,255,0.15),
        inset 0 -1px 0 rgba(0,0,0,0.5);
    backdrop-filter: blur(32px) saturate(200%);
    position: relative;
    overflow: hidden;
    animation: glitchShift 8s ease-in-out infinite;
}

/* Top cyan glow beam */
.login-container::before {
    content: "";
    position: absolute;
    top: -1px; left: 5%; right: 5%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--blue), var(--cyan), transparent);
    box-shadow: 0 0 20px rgba(0,217,255,0.6), 0 0 40px rgba(0,217,255,0.3);
}

/* Scanning light sweep */
.login-container::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    width: 60px;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.04), transparent);
    animation: scanRight 3s ease-in-out infinite;
    pointer-events: none;
}

.login-hex-icon {
    text-align: center;
    margin-bottom: 22px;
    font-size: 2.8rem;
    filter: drop-shadow(0 0 16px rgba(0,217,255,0.6)) drop-shadow(0 0 32px rgba(0,217,255,0.3));
    animation: pulseGlow 3s ease-in-out infinite;
    color: var(--cyan);
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.1em;
}

.login-eyebrow {
    text-align: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--txt-dim);
    margin-bottom: 8px;
}

.login-title {
    text-align: center;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: linear-gradient(135deg, #FFFFFF 0%, #00D9FF 40%, #008CFF 70%, #00D9FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
    text-shadow: none;
    filter: drop-shadow(0 0 12px rgba(0,217,255,0.3));
}

.login-subtitle {
    text-align: center;
    color: var(--txt-dim);
    font-size: 0.68rem;
    margin-bottom: 32px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: 'Exo 2', sans-serif;
}

.login-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.2), transparent);
    margin: 26px 0;
    position: relative;
}

.login-divider::after {
    content: '⬡';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(5,11,22,0.99);
    padding: 0 8px;
    color: var(--txt-dim);
    font-size: 0.7rem;
}

.login-footer {
    text-align: center;
    font-size: 0.62rem;
    color: var(--txt-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.04);
}

/* ================================================================
   HERO HEADER — Page Banner
================================================================ */
.nexus-hero {
    position: relative;
    padding: 24px 32px;
    margin-bottom: 1.8rem;
    margin-top: 1.8rem;
    border-radius: var(--r-xl);
    background: linear-gradient(135deg,
        rgba(11,18,32,0.98) 0%,
        rgba(8,15,26,0.96) 60%,
        rgba(11,16,28,0.98) 100%
    );
    border: 1px solid rgba(0,217,255,0.1);
    border-top: 1px solid rgba(0,217,255,0.25);
    backdrop-filter: blur(20px);
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    animation: slideUp 0.35s cubic-bezier(0.4,0,0.2,1) both;
}

.nexus-hero::before {
    content: "";
    position: absolute;
    top: 0; left: 5%; right: 5%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--blue), var(--cyan), transparent);
    opacity: 0.8;
}

/* Decorative geometric corner */
.nexus-hero::after {
    content: "";
    position: absolute;
    right: 28px; top: 28px;
    width: 60px; height: 60px;
    border-top: 1px solid rgba(0,217,255,0.15);
    border-right: 1px solid rgba(0,217,255,0.15);
    border-radius: 0 var(--r-sm) 0 0;
}

.nexus-hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: linear-gradient(135deg, #E8F3FF 0%, #A8D8FF 50%, #60C0FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 5px;
    filter: drop-shadow(0 0 8px rgba(0,217,255,0.2));
}

.nexus-hero-sub {
    font-size: 0.78rem;
    color: var(--txt-muted);
    letter-spacing: 0.06em;
    font-family: 'Exo 2', sans-serif;
}

.nexus-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 4px 12px;
    border-radius: var(--r-sm);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cyan);
    background: rgba(0,217,255,0.07);
    border: 1px solid rgba(0,217,255,0.2);
    margin-bottom: 11px;
    font-family: 'Orbitron', sans-serif;
    box-shadow: 0 0 12px rgba(0,217,255,0.06);
}

.dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: blinkDot 2s ease-in-out infinite;
    display: inline-block;
}

/* ================================================================
   INLINE HTML COMPONENT LIBRARY
================================================================ */

/* HERO variant (inline) */
.hero {
    padding: 22px 28px;
    border-radius: var(--r-xl);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 2px solid rgba(0,217,255,0.18);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px;
    background: rgba(0,217,255,0.07); border: 1px solid rgba(0,217,255,0.18);
    border-radius: var(--r-sm); font-size: 9px; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--cyan);
    margin-bottom: 8px; font-family: 'Orbitron', sans-serif;
}
.hero-badge-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); display: inline-block; }
.hero-title {
    font-family: 'Orbitron', sans-serif; font-size: 22px; font-weight: 800;
    background: linear-gradient(135deg, #E8F3FF, #80C8FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;
}
.hero-sub { font-size: 12px; color: #5a7a9a; letter-spacing: 0.04em; }

/* KPI GRID */
.kpi-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 22px; }
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 2px solid rgba(0,217,255,0.15);
    border-radius: var(--r-xl);
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: var(--t);
    animation: borderPulse 4s ease-in-out infinite;
}
.kpi-card:hover {
    border-top-color: var(--cyan);
    transform: translateY(-3px);
    box-shadow: 0 0 20px rgba(0,217,255,0.1), var(--shadow);
}
.kpi-card.accent { border-color: rgba(0,217,255,0.18); }
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 5%; right: 5%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,217,255,0.3), transparent);
    opacity: 0.5;
}
.kpi-label {
    font-size: 9px; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--txt-dim); margin-bottom: 9px;
    font-family: 'Orbitron', sans-serif; display: flex; align-items: center; justify-content: space-between;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 700;
    color: #E8F3FF; letter-spacing: -0.02em; line-height: 1; margin-bottom: 6px;
    text-shadow: 0 0 16px rgba(0,217,255,0.12);
}
.kpi-delta { display: inline-flex; align-items: center; gap: 3px; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; }
.kpi-delta.up   { color: #00D26A; background: rgba(0,210,106,0.1); }
.kpi-delta.down { color: #FF3B3B; background: rgba(255,59,59,0.1); }
.kpi-delta.warn { color: #FF9D2E; background: rgba(255,157,46,0.1); }
.kpi-sub { font-size: 10px; color: var(--txt-dim); margin-top: 4px; }
.kpi-icon { width: 28px; height: 28px; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kpi-icon.cyan   { background: rgba(0,217,255,0.1);   color: var(--cyan); }
.kpi-icon.green  { background: rgba(0,210,106,0.1);   color: var(--green); }
.kpi-icon.amber  { background: rgba(255,157,46,0.1);  color: var(--orange); }
.kpi-icon.red    { background: rgba(255,59,59,0.1);   color: var(--red); }
.kpi-icon.blue   { background: rgba(0,140,255,0.1);   color: var(--blue); }

/* SECTION HEADER */
.section-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.section-title {
    font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700;
    color: #E8F3FF; display: flex; align-items: center; gap: 8px;
    text-transform: uppercase; letter-spacing: 0.12em;
}
.section-title::before {
    content: ''; display: block; width: 2px; height: 13px;
    background: linear-gradient(180deg, var(--cyan), var(--blue));
    border-radius: 2px;
    box-shadow: 0 0 8px rgba(0,217,255,0.6);
}

/* CARD */
.card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-xl); padding: 18px; position: relative; overflow: hidden;
}
.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
}

/* RISK TABLE */
.risk-table { width: 100%; border-collapse: collapse; }
.risk-table th {
    font-size: 8.5px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--txt-dim); padding: 0 10px 9px; text-align: left;
    border-bottom: 1px solid var(--border-md); font-family: 'Orbitron', sans-serif;
}
.risk-table th:last-child { text-align: right; }
.risk-table td {
    padding: 9px 10px; border-bottom: 1px solid rgba(255,255,255,0.025);
    font-size: 11.5px; color: var(--txt); font-family: 'JetBrains Mono', monospace;
}
.risk-table tr:last-child td { border-bottom: none; }
.risk-table td:last-child { text-align: right; }
.risk-table tr:hover td { background: rgba(0,217,255,0.025); }
.risk-chip {
    display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 9px;
    font-weight: 700; font-family: 'Orbitron', sans-serif; letter-spacing: 0.06em;
}
.r1 { color: #FF6060; background: rgba(255,59,59,0.1);   border: 1px solid rgba(255,59,59,0.22); }
.r2 { color: #FF9D2E; background: rgba(255,157,46,0.1);  border: 1px solid rgba(255,157,46,0.22); }
.r3 { color: #00D26A; background: rgba(0,210,106,0.1);   border: 1px solid rgba(0,210,106,0.22); }
.r4 { color: #40C4FF; background: rgba(0,140,255,0.1);   border: 1px solid rgba(0,140,255,0.22); }
.status-ok     { color: #00D26A; }
.status-warn   { color: #FF9D2E; }
.status-danger { color: #FF3B3B; }

/* INSIGHTS */
.insight-item { display: flex; gap: 10px; padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.insight-item:last-child { border-bottom: none; padding-bottom: 0; }
.insight-icon { width: 28px; height: 28px; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }
.insight-icon.ok     { background: rgba(0,210,106,0.1);  color: var(--green); }
.insight-icon.warn   { background: rgba(255,157,46,0.1); color: var(--orange); }
.insight-icon.danger { background: rgba(255,59,59,0.1);  color: var(--red); }
.insight-icon.info   { background: rgba(0,217,255,0.08); color: var(--cyan); }
.insight-text { font-size: 11.5px; color: var(--txt); line-height: 1.5; }
.insight-text strong { color: #E8F3FF; font-weight: 600; }
.insight-time { font-size: 9.5px; color: var(--txt-dim); margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

/* FEED */
.feed-item { display: flex; gap: 9px; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
.feed-item:last-child { border-bottom: none; }
.feed-time { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: var(--txt-dim); white-space: nowrap; padding-top: 2px; min-width: 44px; }
.feed-dot-col { display: flex; flex-direction: column; align-items: center; padding-top: 4px; }
.feed-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.feed-dot.ok     { background: var(--green); box-shadow: 0 0 6px var(--green); }
.feed-dot.warn   { background: var(--orange); box-shadow: 0 0 6px var(--orange); }
.feed-dot.danger { background: var(--red); box-shadow: 0 0 6px var(--red); }
.feed-dot.info   { background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
.feed-line { flex: 1; width: 1px; background: rgba(255,255,255,0.05); margin-top: 4px; }
.feed-body { flex: 1; }
.feed-title { font-size: 11.5px; font-weight: 600; color: var(--txt); margin-bottom: 1px; }
.feed-desc  { font-size: 10.5px; color: var(--txt-dim); }
.tag-pass  { color: #00D26A; background: rgba(0,210,106,0.1);  padding: 1px 5px; border-radius: 3px; font-size: 9px; font-weight: 700; }
.tag-fail  { color: #FF6060; background: rgba(255,59,59,0.1);  padding: 1px 5px; border-radius: 3px; font-size: 9px; font-weight: 700; }
.tag-alert { color: #FF9D2E; background: rgba(255,157,46,0.1); padding: 1px 5px; border-radius: 3px; font-size: 9px; font-weight: 700; }

/* DONUT */
.donut-wrap { display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 12px; }
.donut-pos  { position: relative; width: 140px; height: 140px; }
.donut-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); text-align: center; }
.donut-val { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 700; color: #E8F3FF; }
.donut-lbl { font-size: 9px; color: var(--txt-dim); text-transform: uppercase; letter-spacing: 0.12em; font-family: 'Orbitron', sans-serif; }
.donut-legend { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; margin-top: 4px; }
.dl-item { display: flex; align-items: center; gap: 5px; font-size: 10.5px; color: var(--txt); }
.dl-dot  { width: 7px; height: 7px; border-radius: 2px; flex-shrink: 0; }

/* CRISIS HERO */
.crisis-hero {
    padding: 20px 26px;
    background: linear-gradient(135deg, rgba(255,59,59,0.08), rgba(255,157,46,0.04));
    border: 1px solid rgba(255,59,59,0.22);
    border-top: 2px solid rgba(255,59,59,0.4);
    border-radius: var(--r-xl);
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 18px;
    box-shadow: 0 0 32px rgba(255,59,59,0.07);
    position: relative; overflow: hidden;
}
.crisis-hero::before {
    content: ''; position: absolute; top: 0; left: 5%; right: 5%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,59,59,0.5), transparent);
}
.crisis-title { font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 800; color: #FF6060; letter-spacing: 0.08em; text-transform: uppercase; text-shadow: 0 0 12px rgba(255,59,59,0.4); }
.crisis-sub   { font-size: 11px; color: var(--txt-muted); margin-top: 2px; }
.crisis-badge { font-size: 8.5px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; background: rgba(255,59,59,0.12); color: var(--red); border: 1px solid rgba(255,59,59,0.25); display: inline-block; margin-bottom: 4px; font-family: 'Orbitron', sans-serif; }
.crisis-live  { display: flex; align-items: center; gap: 5px; font-size: 9.5px; font-weight: 700; color: var(--red); margin-left: auto; font-family: 'Orbitron', sans-serif; letter-spacing: 0.12em; text-transform: uppercase; }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--red); box-shadow: 0 0 8px var(--red); animation: blinkDot 1.2s ease-in-out infinite; }

/* GAUGE */
.gauge-card {
    background: rgba(255,255,255,0.018); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: 16px; text-align: center;
    transition: var(--t);
}
.gauge-card:hover { border-color: var(--border-md); }
.gauge-label { font-size: 8.5px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: var(--txt-dim); margin-bottom: 8px; font-family: 'Orbitron', sans-serif; }
.gauge-val { font-family: 'JetBrains Mono', monospace; font-size: 17px; font-weight: 700; margin-bottom: 3px; }
.gauge-status { font-size: 8.5px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; font-family: 'Orbitron', sans-serif; }
.gc-red   { color: var(--red); text-shadow: 0 0 8px rgba(255,59,59,0.4); }
.gc-amber { color: var(--orange); }
.gc-green { color: var(--green); text-shadow: 0 0 8px rgba(0,210,106,0.4); }
.crisis-gauge-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }

/* METRICS LIST */
.metric-list .metric-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.metric-row:last-child { border-bottom: none; }
.metric-name  { font-size: 11.5px; color: var(--txt-muted); flex: 1; }
.metric-val   { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500; color: #E8F3FF; min-width: 46px; text-align: right; }
.metric-unit  { font-size: 9.5px; color: var(--txt-dim); min-width: 32px; }
.metric-spark { width: 56px; height: 18px; flex-shrink: 0; }
.metric-delta { font-size: 10px; font-weight: 700; min-width: 34px; text-align: right; font-family: 'JetBrains Mono', monospace; }
.delta-pos { color: var(--green); }
.delta-neg { color: var(--red); }

/* SIM FIELDS */
.sim-field { margin-bottom: 12px; }
.sim-field label { display: block; font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--txt-dim); margin-bottom: 6px; font-family: 'Orbitron', sans-serif; }
.sim-select { width: 100%; background: rgba(4,8,16,0.95); border: 1px solid var(--border-md); border-radius: var(--r-md); padding: 9px 12px; color: var(--txt); font-size: 12px; outline: none; cursor: pointer; transition: var(--t); font-family: 'JetBrains Mono', monospace; }
.sim-select:focus { border-color: rgba(0,217,255,0.35); }
.run-btn { width: 100%; padding: 13px; background: linear-gradient(135deg, #8B0000, #CC1100, #FF2200); border: 1px solid rgba(255,59,59,0.4); border-radius: var(--r-md); color: white; font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; cursor: pointer; transition: var(--t); margin-top: 6px; box-shadow: 0 0 20px rgba(255,59,59,0.2); }
.run-btn:hover { background: linear-gradient(135deg, #AA0000, #DD1100, #FF3300); box-shadow: 0 0 30px rgba(255,59,59,0.35); }

/* ALERTS */
.alert-item { display: flex; gap: 10px; align-items: flex-start; padding: 10px 12px; border-radius: var(--r-md); margin-bottom: 7px; border: 1px solid transparent; transition: var(--t); }
.alert-item:hover { background: rgba(255,255,255,0.012); }
.alert-item.high   { background: rgba(255,59,59,0.04);   border-color: rgba(255,59,59,0.14); }
.alert-item.medium { background: rgba(255,157,46,0.03);  border-color: rgba(255,157,46,0.12); }
.alert-icon { width: 26px; height: 26px; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-red   { background: rgba(255,59,59,0.14); }
.ai-amber { background: rgba(255,157,46,0.12); }
.alert-title { font-size: 11.5px; font-weight: 600; color: #E8F3FF; }
.alert-sub   { font-size: 10.5px; color: var(--txt-muted); margin-top: 1px; }
.alert-time  { font-size: 9px; color: var(--txt-dim); margin-left: auto; white-space: nowrap; font-family: 'JetBrains Mono', monospace; padding-top: 1px; }

/* RECOMMENDATIONS */
.recom-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: var(--r-md); border: 1px solid var(--border); margin-bottom: 7px; background: rgba(255,255,255,0.012); transition: var(--t); }
.recom-item:hover { background: rgba(0,217,255,0.025); border-color: rgba(0,217,255,0.12); }
.recom-label { flex: 1; font-size: 11.5px; color: var(--txt); }
.priority-chip { padding: 2px 8px; border-radius: 4px; font-size: 8.5px; font-weight: 700; flex-shrink: 0; font-family: 'Orbitron', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; }
.p-high { color: #FF6060; background: rgba(255,59,59,0.1);  border: 1px solid rgba(255,59,59,0.22); }
.p-med  { color: #FF9D2E; background: rgba(255,157,46,0.1); border: 1px solid rgba(255,157,46,0.2); }
.p-low  { color: #8AA8CC; background: rgba(138,168,204,0.07); border: 1px solid rgba(138,168,204,0.14); }

/* SYSSTAT */
.sysstat-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.sysstat-row:last-child { border-bottom: none; }
.ss-label { font-size: 11px; color: var(--txt-muted); }
.ss-val   { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; font-weight: 500; color: #E8F3FF; }
.ss-val.critical { color: var(--red); font-weight: 700; text-shadow: 0 0 6px rgba(255,59,59,0.4); }
.ss-val.ok       { color: var(--green); text-shadow: 0 0 6px rgba(0,210,106,0.4); }

/* TAB PILLS */
.tab-pill { padding: 4px 12px; border-radius: 4px; border: 1px solid transparent; font-size: 9.5px; font-weight: 700; cursor: pointer; transition: var(--t); color: var(--txt-muted); font-family: 'Orbitron', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; }
.tab-pill.active { background: rgba(0,217,255,0.08); border-color: rgba(0,217,255,0.22); color: var(--cyan); }
.tab-pill:hover:not(.active) { background: rgba(255,255,255,0.03); }
.section-controls { display: flex; gap: 5px; align-items: center; }

/* SECTION LABEL */
.section-label {
    font-family: 'Orbitron', sans-serif; font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.2em; color: var(--txt-muted);
    margin-bottom: 0.5rem;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
#   SESSION STATE INITIALIZATION
# ============================================================
if 'df_p'           not in st.session_state: st.session_state.df_p           = None
if 'df_c'           not in st.session_state: st.session_state.df_c           = None
if 'results_p'      not in st.session_state: st.session_state.results_p      = None
if 'results_a'      not in st.session_state: st.session_state.results_a      = None
if 'authenticated'  not in st.session_state: st.session_state.authenticated  = False
if 'stage'          not in st.session_state: st.session_state.stage          = 'login'
if 'sim_res_p'      not in st.session_state: st.session_state.sim_res_p      = None

# ============================================================
#   BOOT SCREEN HTML  (components.html — true iframe, no sanitisation)
# ============================================================
_BOOT_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400&display=swap');
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html,body{width:100%;height:100%;background:#020509;overflow:hidden;font-family:'Orbitron',sans-serif}
  body::before{content:'';position:fixed;inset:0;
    background:linear-gradient(rgba(0,217,255,.04) 1px,transparent 1px),
               linear-gradient(90deg,rgba(0,217,255,.04) 1px,transparent 1px);
    background-size:48px 48px;pointer-events:none}
  @keyframes scan   {from{top:-4px}to{top:100%}}
  @keyframes spin   {from{transform:rotate(0deg) scale(1)}50%{transform:rotate(180deg) scale(1.12)}to{transform:rotate(360deg) scale(1)}}
  @keyframes fill   {0%{width:0%}20%{width:14%}45%{width:50%}70%{width:75%}90%{width:94%}100%{width:100%}}
  @keyframes textIn {from{opacity:0;letter-spacing:.5em;filter:blur(6px)}to{opacity:1;letter-spacing:.12em;filter:blur(0)}}
  @keyframes pulse  {0%,100%{opacity:.65}50%{opacity:1}}
  @keyframes fadeOut{from{opacity:1}to{opacity:0}}
  .scanline{position:fixed;left:0;right:0;height:3px;
    background:linear-gradient(90deg,transparent 10%,#00D9FF 50%,transparent 90%);
    animation:scan 1.6s linear infinite;z-index:10}
  .c{position:fixed;width:52px;height:52px;border:2px solid rgba(0,217,255,.4)}
  .tl{top:24px;left:24px;border-right:none;border-bottom:none}
  .tr{top:24px;right:24px;border-left:none;border-bottom:none}
  .bl{bottom:24px;left:24px;border-right:none;border-top:none}
  .br{bottom:24px;right:24px;border-left:none;border-top:none}
  .stage{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:18px;text-align:center;animation:pulse 3s ease-in-out 2.5s infinite}
  .eyebrow{font-size:.55rem;font-weight:700;letter-spacing:.4em;text-transform:uppercase;
    color:rgba(0,217,255,.5);animation:textIn .9s ease .1s both}
  .hex{font-size:4.8rem;color:#00D9FF;line-height:1;
    text-shadow:0 0 28px rgba(0,217,255,.9),0 0 60px rgba(0,217,255,.4);
    animation:spin 2.8s cubic-bezier(.4,0,.2,1) forwards}
  .title{font-size:3rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase;
    background:linear-gradient(135deg,#fff 0%,#00D9FF 45%,#008CFF 85%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    filter:drop-shadow(0 0 16px rgba(0,217,255,.5));animation:textIn 1.1s ease .35s both}
  .sub{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:rgba(0,217,255,.4);
    letter-spacing:.08em;animation:textIn 1.1s ease .55s both}
  .bar-wrap{width:340px;height:3px;background:rgba(0,217,255,.08);
    border:1px solid rgba(0,217,255,.1);border-radius:999px;overflow:hidden;
    animation:textIn .4s ease .75s both}
  .bar-fill{height:100%;background:linear-gradient(90deg,#008CFF,#00D9FF,#fff);
    border-radius:999px;width:0%;animation:fill 2.5s cubic-bezier(.4,0,.6,1) .6s forwards}
  .status{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.14em;
    text-transform:uppercase;color:rgba(0,217,255,.35);animation:textIn .4s ease .9s both}
  .fading{animation:fadeOut .6s ease forwards!important;pointer-events:none}
</style>
</head>
<body>
  <div class="scanline"></div>
  <div class="c tl"></div><div class="c tr"></div>
  <div class="c bl"></div><div class="c br"></div>
  <div class="stage" id="stage">
    <div class="eyebrow">&#x2B21; &nbsp; INITIALIZING STOCK INTELLIGENCE PLATFORM &nbsp; &#x2B21;</div>
    <div class="hex">&#x2B21;</div>
    <div class="title">STOCK AI PRO</div>
    <div class="sub">SMART INVENTORY COMMAND CENTER &nbsp;&middot;&nbsp; v4.0 &nbsp;&middot;&nbsp; AUTHORIZED ACCESS ONLY</div>
    <div class="bar-wrap"><div class="bar-fill"></div></div>
    <div class="status" id="st">LOADING CORE MODULES...</div>
  </div>
<script>
// status cycle
var msgs=["LOADING CORE MODULES...","CALIBRATING RISK ENGINE...","CONNECTING AI INFERENCE LAYER...","INITIALIZING ANOMALY DETECTION...","MOUNTING SUPPLY CHAIN GRAPH...","NEXUS SYSTEMS ONLINE \u2713"];
var i=0,el=document.getElementById('st');
var iv=setInterval(function(){i++;if(i>=msgs.length){clearInterval(iv);return;}if(el)el.textContent=msgs[i];},430);

// startup sound
(function(){
  try{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    var t=ctx.currentTime;
    function tone(f,s,d,tp,v,fi,fo){
      var o=ctx.createOscillator(),g=ctx.createGain();
      o.type=tp;o.frequency.setValueAtTime(f,t+s);
      g.gain.setValueAtTime(0,t+s);
      g.gain.linearRampToValueAtTime(v,t+s+fi);
      g.gain.setValueAtTime(v,t+s+d-fo);
      g.gain.linearRampToValueAtTime(0,t+s+d);
      o.connect(g);g.connect(ctx.destination);
      o.start(t+s);o.stop(t+s+d);
    }
    tone(52,0,.4,'sine',.24,.01,.3);
    tone(104,0,.35,'triangle',.11,.01,.25);
    var sw=ctx.createOscillator(),sg=ctx.createGain();
    sw.type='sawtooth';
    sw.frequency.setValueAtTime(90,t+.3);
    sw.frequency.exponentialRampToValueAtTime(1400,t+1.1);
    sg.gain.setValueAtTime(0,t+.3);sg.gain.linearRampToValueAtTime(.055,t+.35);sg.gain.linearRampToValueAtTime(0,t+1.2);
    sw.connect(sg);sg.connect(ctx.destination);sw.start(t+.3);sw.stop(t+1.25);
    tone(220,.6,.7,'sine',.10,.12,.30);tone(440,.7,.5,'sine',.06,.10,.25);
    tone(523.25,1.1,.6,'sine',.13,.04,.35);tone(659.25,1.18,.5,'sine',.09,.04,.30);tone(783.99,1.26,.45,'sine',.06,.04,.28);
    tone(1046.5,1.55,.6,'sine',.09,.02,.45);tone(1318.5,1.62,.5,'sine',.05,.02,.40);
    tone(110,1.75,1.1,'sine',.045,.1,.8);
  }catch(e){console.warn('audio',e);}
})();

// after 3.2s: fade then notify parent via postMessage
setTimeout(function(){
  document.getElementById('stage').classList.add('fading');
  setTimeout(function(){
    window.parent.postMessage({type:'NEXUS_BOOT_DONE'},'*');
  },650);
},3200);
</script>
</body>
</html>"""


# ============================================================
#   LOGIN SCREEN
# ============================================================
def login_screen():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 20% 20%, rgba(0,60,160,0.18) 0%, transparent 55%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,200,255,0.09) 0%, transparent 50%),
            radial-gradient(ellipse 50% 30% at 50% 50%, rgba(0,30,80,0.12) 0%, transparent 60%),
            linear-gradient(rgba(0,217,255,0.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,217,255,0.018) 1px, transparent 1px),
            #030710 !important;
        background-size: auto, auto, auto, 32px 32px, 32px 32px, 100% !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"]   { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown("""
        <div class="login-container">
            <div class="login-hex-icon">⬡</div>
            <div class="login-eyebrow">⬡ STOCK INTELLIGENCE PLATFORM</div>
            <div class="login-title">STOCK AI PRO</div>
            <div class="login-subtitle">Smart Inventory Command Center · Authorized Personnel Only</div>
            <div class="login-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        user     = st.text_input("Identifiant", placeholder="USERNAME", label_visibility="visible")
        password = st.text_input("Clé d'accès", type="password", placeholder="••••••••••••", label_visibility="visible")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if st.button("⬡  UNLOCK COCKPIT", use_container_width=True):
            if user == "admin" and password == "123":
                st.session_state.authenticated = True
                st.session_state.stage         = 'video'
                st.rerun()
            else:
                st.error("⛔  ACCESS DENIED — Invalid credentials")

        st.markdown("""
        <div class="login-footer">
            NEXUS v4.0 &nbsp;·&nbsp; CONFIDENTIAL &nbsp;·&nbsp; AI SUPPLY CHAIN INTELLIGENCE
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#   BOOT SCREEN  (stage = 'video')
#   Strategy: render iframe + a hidden st.button
#   JS sends postMessage → parent page JS clicks the hidden button
#   → Streamlit reruns with stage='app'   (no URL redirect needed)
# ============================================================
def boot_screen():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display:none !important; }
    header[data-testid="stHeader"]   { display:none !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    /* visually hide the advance button but keep it in DOM */
    [data-testid="stButton"]:last-of-type button {
        position:fixed !important; opacity:0 !important;
        pointer-events:none !important; width:0px !important; height:0px !important;
    }
                
    </style>
    """, unsafe_allow_html=True)

    # This hidden button is clicked by JS to trigger st.rerun()
    advance = st.button("▶", key="nx_boot_advance")
    if advance:
        st.session_state.stage = 'app'
        st.rerun()

    


    components.html(_BOOT_HTML, height=1000, scrolling=False)

    # Listen for postMessage from iframe, then click the hidden button
    # ⬇️ délai simulé (durée de ta vidéo boot)
    time.sleep(6)  # adapte à la durée réelle

    st.session_state.stage = 'app'
    st.rerun()

# ============================================================
#   EXECUTION GATE
# ============================================================
if not st.session_state.authenticated:
    st.session_state.stage = 'login'
    login_screen()
    st.stop()

if st.session_state.stage == 'video':
    boot_screen()
    st.stop()

# ── stage == 'app' ── dashboard with entrance animation
st.markdown("""
<style>
@keyframes nx-slideUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
.block-container { animation: nx-slideUp .65s cubic-bezier(.4,0,.2,1) both; }
</style>
""", unsafe_allow_html=True)

# ============================================================
#   SIDEBAR — NEXUS COMMAND PANEL
# ============================================================

# ============================================================
#   NEXUS EXECUTIVE AI REPORT — PDF GENERATOR
#   Inséré automatiquement — ne pas modifier le code existant
# ============================================================
def _generate_nexus_pdf(results_p=None, results_a=None, df_p=None):
    """
    Génère un rapport PDF exécutif premium depuis les données session NEXUS.
    Retourne les bytes du PDF ou None si aucune donnée disponible.
    """
    import io
    from datetime import datetime
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether,
    )
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    # ── Résoudre la source de données ────────────────────────────────────────
    df = None
    if results_p is not None and not results_p.empty:
        df = results_p.copy()
    elif results_a is not None and not results_a.empty:
        df = results_a.copy()
    elif df_p is not None and not df_p.empty:
        df = df_p.copy()
    if df is None:
        return None

    W, H = A4

    # ── Palette ───────────────────────────────────────────────────────────────
    DARK_BG  = colors.HexColor('#0B1220')
    DARKEST  = colors.HexColor('#060C18')
    CYAN     = colors.HexColor('#00D9FF')
    CYAN_DIM = colors.HexColor('#006080')
    BLUE     = colors.HexColor('#008CFF')
    RED      = colors.HexColor('#DC2626')
    ORANGE   = colors.HexColor('#F59E0B')
    GREEN    = colors.HexColor('#10B981')
    WHITE    = colors.HexColor('#FFFFFF')
    GREY_LT  = colors.HexColor('#94A3B8')
    GREY_MED = colors.HexColor('#475569')
    GREY_DRK = colors.HexColor('#1E2D3D')
    SLATE    = colors.HexColor('#0F1E2E')

    # ── Styles ────────────────────────────────────────────────────────────────
    def _ps(name, **kw): return ParagraphStyle(name, **kw)
    S = {
        'cover_brand': _ps('cb', fontName='Helvetica-Bold', fontSize=42,
                           textColor=WHITE, leading=46, alignment=TA_CENTER),
        'cover_sub':   _ps('cs', fontName='Helvetica', fontSize=10,
                           textColor=CYAN, leading=14, alignment=TA_CENTER, letterSpacing=4),
        'cover_date':  _ps('cd', fontName='Helvetica', fontSize=8,
                           textColor=GREY_LT, leading=12, alignment=TA_CENTER, letterSpacing=2),
        'section':     _ps('sec', fontName='Helvetica-Bold', fontSize=9,
                           textColor=CYAN, leading=13, spaceAfter=8, spaceBefore=18, letterSpacing=2),
        'h2':          _ps('h2', fontName='Helvetica-Bold', fontSize=13,
                           textColor=WHITE, leading=17, spaceAfter=6),
        'body':        _ps('bd', fontName='Helvetica', fontSize=8.5,
                           textColor=GREY_LT, leading=13, spaceAfter=3),
        'body_sm':     _ps('bsm', fontName='Helvetica', fontSize=7.5,
                           textColor=GREY_MED, leading=11, spaceAfter=2),
        'rec_title':   _ps('rt', fontName='Helvetica-Bold', fontSize=8.5,
                           textColor=WHITE, leading=12, spaceAfter=1),
        'rec_body':    _ps('rb', fontName='Helvetica', fontSize=7.5,
                           textColor=GREY_LT, leading=11, spaceAfter=4, leftIndent=10),
        'footer':      _ps('ft', fontName='Helvetica', fontSize=6.5,
                           textColor=GREY_MED, leading=9, alignment=TA_CENTER),
        'table_hd':    _ps('thd', fontName='Helvetica-Bold', fontSize=7.5,
                           textColor=CYAN, leading=10, alignment=TA_CENTER, letterSpacing=1),
        'table_cel':   _ps('tcl', fontName='Helvetica', fontSize=7.5,
                           textColor=WHITE, leading=10, alignment=TA_CENTER),
        'table_cel_l': _ps('tcll', fontName='Helvetica', fontSize=7.5,
                           textColor=WHITE, leading=10),
    }

    def hr(color=CYAN_DIM, w=1):
        return HRFlowable(width='100%', thickness=w, color=color, spaceAfter=6)

    def sec(text):
        return [
            Paragraph(f'◈  {text.upper()}', S['section']),
            HRFlowable(width='100%', thickness=0.5, color=CYAN_DIM, spaceAfter=10),
        ]

    def cover_drawing():
        d = Drawing(W - 40*mm, 180)
        d.add(Rect(0, 0, W-40*mm, 180, fillColor=DARKEST,
                   strokeColor=CYAN_DIM, strokeWidth=0.5))
        d.add(Rect(0, 176, W-40*mm, 4,  fillColor=CYAN,  strokeColor=None))
        d.add(Rect(0, 0,   W-40*mm, 3,  fillColor=BLUE,  strokeColor=None))
        for i in range(0, int(W-40*mm), 24):
            d.add(Line(i, 0, i, 180,
                       strokeColor=colors.HexColor('#0A1828'), strokeWidth=0.4))
        for j in range(0, 180, 24):
            d.add(Line(0, j, W-40*mm, j,
                       strokeColor=colors.HexColor('#0A1828'), strokeWidth=0.4))
        d.add(Rect((W-40*mm)/2-50, 35, 100, 100,
                   fillColor=colors.HexColor('#00D9FF'),
                   strokeColor=None, fillOpacity=0.04))
        d.add(Rect((W-40*mm)/2-32, 53, 64, 64,
                   fillColor=colors.HexColor('#00D9FF'),
                   strokeColor=None, fillOpacity=0.06))
        return d

    def kpi_row(items):
        """items = [(value, label, hex_color), ...]"""
        cells = [
            [Paragraph(str(v), _ps(f'kv{i}', fontName='Helvetica-Bold', fontSize=18,
              textColor=colors.HexColor(c), leading=22, alignment=TA_CENTER))
             for i, (v, l, c) in enumerate(items)],
            [Paragraph(l, _ps(f'kl{i}', fontName='Helvetica', fontSize=6.5,
              textColor=GREY_MED, leading=9, alignment=TA_CENTER, letterSpacing=1))
             for i, (v, l, c) in enumerate(items)],
        ]
        cw = [(W - 40*mm) / len(items)] * len(items)
        t  = Table(cells, colWidths=cw, rowHeights=[26, 14])
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,-1), SLATE),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [SLATE, GREY_DRK]),
            ('BOX',            (0,0), (-1,-1), 0.5, GREY_DRK),
            ('LINEABOVE',      (0,0), (-1, 0), 1.5, CYAN_DIM),
            ('INNERGRID',      (0,0), (-1,-1), 0.3, GREY_DRK),
            ('TOPPADDING',     (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 5),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    def risk_tbl(data):
        RCOL = {'R1': RED, 'R2': ORANGE, 'R3': CYAN, 'R4': GREY_LT}
        top  = data.sort_values('RRS', ascending=False).head(15)                if 'RRS' in data.columns else data.head(15)
        hdrs = ['PRODUCT ID', 'RISK', 'ABC', 'RRS', 'CRITICALITY', 'LEAD TIME']
        rows = [[Paragraph(h, S['table_hd']) for h in hdrs]]
        for _, r in top.iterrows():
            rc  = str(r.get('risk_class', ''))
            col = RCOL.get(rc, WHITE)
            rrs = float(r.get('RRS', 0))
            rows.append([
                Paragraph(str(r.get('product_id', '')), S['table_cel_l']),
                Paragraph(rc, _ps('rc2', fontName='Helvetica-Bold', fontSize=7.5,
                          textColor=col, leading=10, alignment=TA_CENTER)),
                Paragraph(str(r.get('abc_class', '')), S['table_cel']),
                Paragraph(f'{rrs:.2f}', _ps('rrs2', fontName='Helvetica-Bold', fontSize=7.5,
                          textColor=col if rrs > 7 else WHITE,
                          leading=10, alignment=TA_CENTER)),
                Paragraph(str(r.get('criticality', '')), S['table_cel']),
                Paragraph(str(r.get('avg_lead_time', '')), S['table_cel']),
            ])
        cw = [40*mm, 22*mm, 18*mm, 22*mm, 38*mm, 26*mm]
        t  = Table(rows, colWidths=cw, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1, 0), GREY_DRK),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [SLATE, colors.HexColor('#0D1A2A')]),
            ('BOX',            (0,0), (-1,-1), 0.5, GREY_DRK),
            ('INNERGRID',      (0,0), (-1,-1), 0.3, GREY_DRK),
            ('LINEBELOW',      (0,0), (-1, 0), 1.0, CYAN_DIM),
            ('TOPPADDING',     (0,0), (-1,-1), 5),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 5),
            ('LEFTPADDING',    (0,0), (-1,-1), 6),
            ('RIGHTPADDING',   (0,0), (-1,-1), 6),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    def pie_chart(counts):
        labs = [k for k, v in counts.items() if v > 0]
        vals = [v for v in counts.values() if v > 0]
        if not vals: return Spacer(1, 10)
        d = Drawing(170, 150)
        d.add(Rect(0, 0, 170, 150, fillColor=SLATE,
                   strokeColor=GREY_DRK, strokeWidth=0.5))
        pie = Pie()
        pie.x, pie.y          = 25, 15
        pie.width = pie.height = 110
        pie.data, pie.labels   = vals, [f'{k} ({v})' for k, v in zip(labs, vals)]
        pie.sideLabels         = True
        SCOLS = [RED, ORANGE, CYAN, GREY_LT]
        for i, c in enumerate(SCOLS[:len(labs)]):
            pie.slices[i].fillColor   = c
            pie.slices[i].strokeColor = SLATE
            pie.slices[i].strokeWidth = 1
            pie.slices[i].labelRadius = 1.25
        pie.slices.fontName  = 'Helvetica'
        pie.slices.fontSize  = 6
        pie.slices.fontColor = WHITE
        d.add(pie)
        return d

    def bar_chart(counts):
        labs = list(counts.keys())
        vals = [counts[k] for k in labs]
        if not any(vals): return Spacer(1, 10)
        d = Drawing(260, 150)
        d.add(Rect(0, 0, 260, 150, fillColor=SLATE,
                   strokeColor=GREY_DRK, strokeWidth=0.5))
        bc = VerticalBarChart()
        bc.x, bc.y           = 28, 18
        bc.width, bc.height  = 220, 110
        bc.data              = [vals]
        bc.categoryAxis.categoryNames       = labs
        bc.categoryAxis.labels.fontName     = 'Helvetica'
        bc.categoryAxis.labels.fontSize     = 7
        bc.categoryAxis.labels.fillColor    = GREY_LT
        bc.categoryAxis.strokeColor         = GREY_DRK
        bc.valueAxis.labels.fontName        = 'Helvetica'
        bc.valueAxis.labels.fontSize        = 7
        bc.valueAxis.labels.fillColor       = GREY_LT
        bc.valueAxis.strokeColor            = GREY_DRK
        bc.bars[0].fillColor = CYAN
        bc.bars.strokeWidth  = 0
        d.add(bc)
        return d

    # ── Page template (dark background + header/footer on every page) ─────────
    def _on_page(cv, doc):
        cv.saveState()
        cv.setFillColor(DARK_BG)
        cv.rect(0, 0, W, H, fill=1, stroke=0)
        cv.setFillColor(GREY_DRK); cv.rect(0, H-22, W, 22, fill=1, stroke=0)
        cv.setFillColor(CYAN);     cv.rect(0, H-2,  W,  2, fill=1, stroke=0)
        cv.setFillColor(GREY_MED); cv.setFont('Helvetica', 6.5)
        cv.drawString(20, H-15, 'NEXUS  ·  EXECUTIVE AI REPORT  ·  CONFIDENTIAL')
        cv.drawRightString(W-20, H-15,
            datetime.now().strftime('%d %b %Y') + f'  |  PAGE {doc.page}')
        cv.setFillColor(GREY_DRK); cv.rect(0, 0, W, 18, fill=1, stroke=0)
        cv.setFillColor(BLUE);     cv.rect(0, 0, W,  2, fill=1, stroke=0)
        cv.setFillColor(GREY_MED); cv.setFont('Helvetica', 6)
        cv.drawCentredString(W/2, 6,
            'Generated by NEXUS AI Platform  ·  Confidential & Proprietary')
        cv.restoreState()

    # ── Compute stats ─────────────────────────────────────────────────────────
    now        = datetime.now()
    total      = len(df)
    rc_counts  = df['risk_class'].value_counts().to_dict()                  if 'risk_class' in df.columns else {}
    n_r1 = rc_counts.get('R1', 0); n_r2 = rc_counts.get('R2', 0)
    n_r3 = rc_counts.get('R3', 0); n_r4 = rc_counts.get('R4', 0)
    gs   = round(df['RRS'].mean(), 2) if 'RRS' in df.columns else 0.0
    r1p  = round(100*n_r1/total, 1) if total else 0
    r2p  = round(100*n_r2/total, 1) if total else 0
    risk_level = ('CRITICAL' if r1p > 25 else
                  'ELEVATED' if r1p > 10 else 'MODERATE')

    # ── Build story ───────────────────────────────────────────────────────────
    buf   = io.BytesIO()
    doc   = SimpleDocTemplate(buf, pagesize=A4,
                topMargin=32, bottomMargin=28,
                leftMargin=20*mm, rightMargin=20*mm,
                title='NEXUS Executive AI Report',
                author='NEXUS AI Platform')
    story = []

    # Page 1 — Cover ──────────────────────────────────────────────────────────
    story.append(cover_drawing())
    story.append(Spacer(1, 20))
    story.append(Paragraph('NEXUS', S['cover_brand']))
    story.append(Spacer(1, 4))
    story.append(Paragraph('EXECUTIVE AI INVENTORY RISK REPORT', S['cover_sub']))
    story.append(Spacer(1, 10))
    story.append(hr(CYAN, 1))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        now.strftime('Generated on %d %B %Y  ·  %H:%M').upper(), S['cover_date']))
    story.append(Paragraph(
        f'{total} PRODUCTS ANALYZED  ·  CLASSIFICATION ENGINE  ·  CONFIDENTIAL',
        S['cover_date']))
    story.append(PageBreak())

    # Page 2 — Executive Summary ──────────────────────────────────────────────
    story += sec('Executive Summary')
    story.append(Paragraph('Portfolio Risk Assessment', S['h2']))
    story.append(Paragraph(
        f'NEXUS AI has completed a multi-factor risk classification of <b>{total}</b> inventory '
        f'products. The Risk Ranking Score (RRS) integrates lead time variability, ABC criticality, '
        f'consumption volatility and supplier reliability signals. '
        f'The global portfolio risk score is <b>{gs:.2f} / 10</b>.',
        S['body']))
    story.append(Spacer(1, 10))
    story.append(kpi_row([
        (total,         'TOTAL PRODUCTS',  '#00D9FF'),
        (n_r1,          'R1  CRITICAL',    '#DC2626'),
        (n_r2,          'R2  HIGH RISK',   '#F59E0B'),
        (n_r3,          'R3  MEDIUM RISK', '#00D9FF'),
        (n_r4,          'R4  LOW RISK',    '#94A3B8'),
        (f'{gs:.1f}',   'GLOBAL RRS',      '#10B981'),
    ]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f'Risk Level : <b>{risk_level}</b>', S['h2']))
    story.append(Paragraph(
        f'<b>{r1p}%</b> of the portfolio is Critical (R1) — immediate procurement action required. '
        f'<b>{r2p}%</b> is High-Risk (R2) — proactive monitoring is strongly advised. '
        f'These two tiers represent the primary focus area for supply chain intervention.',
        S['body']))
    story.append(PageBreak())

    # Page 3 — Risk Items Table ───────────────────────────────────────────────
    story += sec('Top Risk Items — Priority Procurement List')
    story.append(Paragraph(
        'Ranked by RRS Score (descending)  ·  Top 15 items displayed', S['body_sm']))
    story.append(Spacer(1, 6))
    story.append(risk_tbl(df))
    story.append(PageBreak())

    # Page 4 — AI Recommendations ─────────────────────────────────────────────
    story += sec('AI-Generated Recommendations')
    recs = []
    if n_r1:
        recs.append(('IMMEDIATE ACTION  —  Critical Items (R1)',
            f'{n_r1} products require emergency reorder. Activate backup suppliers immediately '
            f'and increase safety stock buffer by 30-50%. Escalate to procurement director '
            f'within 24 hours.'))
    if n_r2:
        recs.append(('PROACTIVE MONITORING  —  High Risk Items (R2)',
            f'{n_r2} items show elevated risk profiles. Review supplier contracts and negotiate '
            f'shorter lead times. Consider dual-sourcing strategy for the top-5 ranked products.'))
    if n_r3:
        recs.append(('OPTIMIZATION  —  Medium Risk Items (R3)',
            f'{n_r3} products are stable but require periodic recalibration of safety stock '
            f'formulas. Apply EOQ optimization to reduce holding costs while maintaining '
            f'target service levels.'))
    recs.append(('PORTFOLIO HEALTH  —  Global Score Management',
        f'Current global RRS is {gs:.2f}/10. Target threshold: below 4.0. Deploy weekly '
        f'automated monitoring via NEXUS to track score evolution and trigger proactive '
        f'supply chain alerts.'))
    recs.append(('DATA QUALITY  —  Continuous Improvement',
        'Ensure consumption history covers a minimum of 12 rolling months for all products. '
        'Incomplete history inflates RRS estimates. Enrich supplier data fields to improve '
        'model precision and reduce false-positive alerts.'))
    for i, (title, body) in enumerate(recs, 1):
        story.append(KeepTogether([
            Paragraph(f'{i:02d}.  {title}', S['rec_title']),
            Paragraph(body, S['rec_body']),
            Spacer(1, 4),
        ]))
    story.append(PageBreak())

    # Page 5 — Charts ─────────────────────────────────────────────────────────
    story += sec('Risk Distribution Analytics')
    story.append(Spacer(1, 8))
    charts = Table(
        [[pie_chart({'R1': n_r1, 'R2': n_r2, 'R3': n_r3, 'R4': n_r4}),
          bar_chart({'R1': n_r1, 'R2': n_r2, 'R3': n_r3, 'R4': n_r4})]],
        colWidths=[88*mm, 100*mm]
    )
    charts.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), SLATE),
        ('BOX',           (0,0), (-1,-1), 0.5, GREY_DRK),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(charts)
    story.append(Spacer(1, 14))
    if 'abc_class' in df.columns:
        story.append(Paragraph('ABC Classification Distribution', S['h2']))
        story.append(Spacer(1, 6))
        story.append(bar_chart(df['abc_class'].value_counts().to_dict()))
    story.append(PageBreak())

    # Page 6 — Conclusion ─────────────────────────────────────────────────────
    story += sec('Conclusion & Next Steps')
    story.append(Paragraph('Strategic Outlook', S['h2']))
    story.append(Paragraph(
        f'The NEXUS AI engine has completed its multi-factor inventory risk assessment across '
        f'the full portfolio of <b>{total}</b> products. The analysis reveals a portfolio risk '
        f'profile that is <b>{risk_level.lower()}</b>, with particular concentration in the '
        f'R1 and R2 tiers that warrant immediate management attention.',
        S['body']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '<b>Recommended next steps:</b> (1) Execute emergency procurement for all R1-classified '
        'items within 72 hours. (2) Schedule weekly NEXUS Stress Test simulations to validate '
        'resilience against supply disruption scenarios. (3) Initiate supplier negotiations for '
        'lead time reduction on the top-10 risk-ranked products. '
        '(4) Review and update safety stock parameters on a quarterly basis.',
        S['body']))
    story.append(Spacer(1, 14))
    story.append(hr(CYAN_DIM))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f'NEXUS AI Platform  ·  Report generated {now.strftime("%d %B %Y at %H:%M")}  '
        f'·  Confidential & Proprietary  ·  Do not distribute',
        S['footer']))

    # ── Render ────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    buf.seek(0)
    return buf.getvalue()

with st.sidebar:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Logo + Brand
    col_logo, col_title = st.columns([1, 2.5])
    with col_logo:
        st.markdown("""
        <div style="
            width:48px; height:48px;
            background: linear-gradient(135deg, rgba(0,217,255,0.15), rgba(0,140,255,0.08));
            border: 1px solid rgba(0,217,255,0.3);
            border-radius: 12px;
            display:flex; align-items:center; justify-content:center;
            font-size:1.4rem; color:#00D9FF;
            box-shadow: 0 0 16px rgba(0,217,255,0.2), inset 0 1px 0 rgba(0,217,255,0.2);
        ">⬡</div>
        """, unsafe_allow_html=True)

    with col_title:
        st.markdown("""
        <div style='padding-top:4px'>
            <div style='
                font-family: Orbitron, sans-serif;
                font-size: 1rem; font-weight: 900;
                background: linear-gradient(135deg, #FFFFFF, #00D9FF, #008CFF);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                letter-spacing: 0.06em; line-height: 1.1;
            '>STOCK AI</div>
            <div style='
                font-size: 0.56rem; color: #3A6080;
                letter-spacing: 0.2em; text-transform: uppercase;
                font-weight: 700; font-family: Orbitron, sans-serif;
                margin-top: 2px;
            '>SMART INVENTORY</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Navigation label
    st.markdown("""
    <div style='
        font-size:0.55rem; font-weight:700; letter-spacing:0.24em;
        text-transform:uppercase; color:#2A4060;
        font-family:Orbitron,sans-serif; padding:2px 2px 8px;
    '>Navigation Modules</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "⊕  Executive Dashboard",
            "⚠  Risk Classification",
            "⊞  Inventory Policy",
            "◈  Anomaly Detection",
            "⚡  Stress Test Simulator",
            "⊟  Data Management",
            "🔊  Nexus Voice AI",
            "📄  Executive Report",
        ],
        label_visibility="collapsed"
    )

    # Clean page name for logic
    page = page.split("  ", 1)[1] if "  " in page else page

    st.markdown("<hr>", unsafe_allow_html=True)

    # System online badge
    st.markdown("""
    <div style='
        display:flex; align-items:center; gap:9px; padding:12px 14px;
        background:rgba(0,210,106,0.05); border:1px solid rgba(0,210,106,0.14);
        border-radius:12px; margin-bottom:10px;
    '>
        <div style='
            width:7px; height:7px; border-radius:50%;
            background:#00D26A; box-shadow:0 0 10px #00D26A;
            flex-shrink:0; animation:blinkDot 2s infinite;
        '></div>
        <div style='line-height:1.4'>
            <div style='font-size:0.7rem; font-weight:700; color:#6EE7B7;
                        font-family:Orbitron,sans-serif; letter-spacing:0.08em;'>
                SYSTEM <span style='color:#A7F3D0'>ONLINE</span>
            </div>
            <div style='font-size:0.6rem; color:#2A5040; font-family:JetBrains Mono,monospace; margin-top:1px;'>
                Supply Chain AI Active
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button("⬡  DISCONNECT", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()



# ============================================================
#   DATA MANAGEMENT PAGE
# ============================================================
if page == "Data Management":
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>Data Ingestion Center · Secure Pipeline</div>"
        "<div class='nexus-hero-title'>Industrial Data Management</div>"
        "<div class='nexus-hero-sub'>Upload and process your supply chain datasets · Products Master & Consumption History</div>"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='
            font-size:0.62rem; font-weight:700; letter-spacing:0.18em;
            text-transform:uppercase; color:#5A7A9A;
            font-family:Orbitron,sans-serif; margin-bottom:6px;
        '>⊞ Products Master File</div>
        """, unsafe_allow_html=True)
        u_p = st.file_uploader("Products Master", type=['xlsx', 'csv'], label_visibility="collapsed")

    with col2:
        st.markdown("""
        <div style='
            font-size:0.62rem; font-weight:700; letter-spacing:0.18em;
            text-transform:uppercase; color:#5A7A9A;
            font-family:Orbitron,sans-serif; margin-bottom:6px;
        '>◈ Consumption History File</div>
        """, unsafe_allow_html=True)
        u_c = st.file_uploader("Consumption Data", type=['xlsx', 'csv'], label_visibility="collapsed")

    if u_p and u_c:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("⚡  PROCESS INDUSTRIAL DATA", use_container_width=False):
            df_p = pd.read_excel(u_p) if u_p.name.endswith('xlsx') else pd.read_csv(u_p)
            df_c = pd.read_excel(u_c) if u_c.name.endswith('xlsx') else pd.read_csv(u_c)
            with st.spinner("⚙  Analyzing Supply Chain Intelligence..."):
                res_p = run_classification_logic(df_p, df_c)
                res_a = run_anomaly_logic(res_p, df_c)
                st.session_state.df_p      = df_p
                st.session_state.df_c      = df_c
                st.session_state.results_p = res_p
                st.session_state.results_a = res_a
                st.success("✅  Analysis Complete — All NEXUS modules initialized.")

# ============================================================
#   DATA GATE
# ============================================================
if st.session_state.results_p is None:
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='
        padding:28px 32px;
        background:rgba(255,157,46,0.04);
        border:1px solid rgba(255,157,46,0.18);
        border-left:3px solid #FF9D2E;
        border-radius:16px;
        display:flex; gap:16px; align-items:center;
    '>
        <div style='font-size:1.5rem;'>⚠</div>
        <div>
            <div style='font-family:Orbitron,sans-serif; font-size:0.8rem; font-weight:700; color:#FF9D2E; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:4px;'>
                DATA REQUIRED
            </div>
            <div style='font-size:0.82rem; color:#8AA8CC;'>
                Upload your supply chain datasets in the <strong style='color:#E8F3FF'>Data Management</strong> module to initialize the cockpit.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================================
#   PLOTLY DARK THEME
# ============================================================
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono, monospace', color='#7A9AB8', size=11),
    title_font=dict(family='Orbitron, sans-serif', color='#C8E0FF', size=13),
    legend=dict(
        bgcolor='rgba(5,11,20,0.8)',
        bordercolor='rgba(0,217,255,0.08)',
        borderwidth=1,
        font=dict(color='#7A9AB8', size=10)
    ),
    xaxis=dict(
        gridcolor='rgba(255,255,255,0.03)',
        linecolor='rgba(0,217,255,0.06)',
        tickcolor='rgba(0,217,255,0.04)',
        tickfont=dict(color='#5A7A9A', size=10)
    ),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.03)',
        linecolor='rgba(0,217,255,0.06)',
        tickcolor='rgba(0,217,255,0.04)',
        tickfont=dict(color='#5A7A9A', size=10)
    ),
    margin=dict(l=20, r=20, t=50, b=20),
)

# ============================================================
#   EXECUTIVE DASHBOARD
# ============================================================
if page == "Executive Dashboard":
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>Live · Executive Intelligence View</div>"
        "<div class='nexus-hero-title'>Supply Chain Executive Overview</div>"
        "<div class='nexus-hero-sub'>Real-time risk intelligence · AI-powered supply chain analytics · Enterprise Standards</div>"
        "</div>",
        unsafe_allow_html=True
    )

    res_p = st.session_state.results_p
    res_a = st.session_state.results_a
    last_week = res_a[res_a['week'] == res_a['week'].max()]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total SKU", f"{len(res_p):,}")
    m2.metric("Critical (R1)", len(res_p[res_p['risk_class'] == 'R1']), delta_color="inverse")
    m3.metric("Current Red Alerts", len(last_week[last_week['alert_level'] == 'RED']))
    m4.metric("Avg RRS Score", f"{res_p['RRS'].mean():.2f}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_risk = px.pie(
            res_p, names='risk_class',
            title="Risk Distribution (R1–R4)",
            color_discrete_sequence=['#CC0000', '#CC6600', '#CC9900', '#006600'],
            hole=0.48
        )
        fig_risk.update_layout(**PLOTLY_LAYOUT)
        fig_risk.update_traces(
            textfont_color='white',
            marker=dict(line=dict(color='rgba(0,0,0,0.4)', width=2))
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with c2:
        df_alert = res_a['alert_level'].value_counts().reset_index()
        df_alert.columns = ['alert_level', 'count']
        fig_alert = px.bar(
            df_alert, x='alert_level', y='count',
            title="Global Alert Distribution",
            color='alert_level', text='count',
            color_discrete_map={
                'RED':    '#ef4444',
                'ORANGE': '#f97316',
                'YELLOW': '#eab308',
                'GREEN':  '#10b981'
            }
        )
        fig_alert.update_traces(textposition='outside', textfont_color='white', marker_line_width=0)
        fig_alert.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig_alert, use_container_width=True)

# ============================================================
#   RISK CLASSIFICATION
# ============================================================
elif page == "Risk Classification":
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>AI Engine · Classification Module · Active</div>"
        "<div class='nexus-hero-title'>AI Risk Classification</div>"
        "<div class='nexus-hero-sub'>Multi-factor risk scoring · ABC analysis integration · RRS ranking system</div>"
        "</div>",
        unsafe_allow_html=True
    )

    res_p = st.session_state.results_p
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_risk = st.multiselect(
            "Filter Risk Class",
            ['R1', 'R2', 'R3', 'R4'],
            default=['R1', 'R2']
        )
    with col_f2:
        search_id = st.text_input("Search Product ID", placeholder="Enter product ID...")

    filtered_df = res_p[res_p['risk_class'].isin(selected_risk)]
    if search_id:
        filtered_df = filtered_df[filtered_df['product_id'].astype(str).str.contains(search_id)]

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.dataframe(
        filtered_df[['product_id', 'risk_class', 'abc_class', 'RRS', 'criticality', 'avg_lead_time']]
            .sort_values('RRS', ascending=False),
        use_container_width=True
    )

    st.subheader("ABC vs AI Risk Heatmap")
    cross_tab = pd.crosstab(res_p['abc_class'], res_p['risk_class'])
    fig_heat = px.imshow(
        cross_tab,
        text_auto=True,
        color_continuous_scale=[[0, '#020810'], [0.3, '#0E2040'], [0.6, '#B45309'], [1.0, '#DC2626']],
        labels=dict(x="AI Risk Class", y="ABC Class")
    )
    fig_heat.update_layout(**PLOTLY_LAYOUT)
    fig_heat.update_traces(textfont=dict(color='white', size=13))
    st.plotly_chart(fig_heat, use_container_width=True)

# ============================================================
#   INVENTORY POLICY
# ============================================================
elif page == "Inventory Policy":

    # =========================================================
    #  PREMIUM CSS — scoped to Inventory Policy only
    # =========================================================
    st.markdown("""
    <style>
    /* ── KPI glassmorphism cards ── */
    .ip-kpi {
        background: linear-gradient(135deg,rgba(11,18,32,0.96),rgba(8,15,26,0.92));
        border: 1px solid rgba(0,217,255,0.14);
        border-top: 2px solid rgba(0,217,255,0.55);
        border-radius: 16px;
        padding: 20px 22px 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.45),
                    inset 0 1px 0 rgba(0,217,255,0.06);
        transition: transform .22s ease, box-shadow .22s ease;
        text-align: center;
    }
    .ip-kpi:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 16px 44px rgba(0,0,0,0.55),
                    0 0 24px rgba(0,217,255,0.12);
    }
    .ip-kpi-val {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.85rem; font-weight: 800;
        background: linear-gradient(135deg,#fff 0%,#00D9FF 60%,#008CFF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 10px rgba(0,217,255,0.4));
        line-height: 1.1; margin-bottom: 6px;
    }
    .ip-kpi-lbl {
        font-size: .58rem; font-weight: 700;
        letter-spacing: .22em; text-transform: uppercase;
        color: rgba(90,122,154,0.9);
    }
    /* ── Section separator ── */
    .ip-sep {
        height: 1px;
        background: linear-gradient(90deg,transparent,rgba(0,217,255,0.18),transparent);
        margin: 28px 0;
    }
    /* ── Section label ── */
    .ip-sec {
        font-family: 'Orbitron', sans-serif;
        font-size: .6rem; font-weight: 800;
        letter-spacing: .24em; text-transform: uppercase;
        color: #00D9FF; text-shadow: 0 0 12px rgba(0,217,255,0.5);
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 16px;
    }
    .ip-sec::after {
        content: ''; flex: 1; height: 1px;
        background: linear-gradient(90deg,rgba(0,217,255,0.3),transparent);
    }
    /* ── SKU KPI mini cards ── */
    .ip-sku-card {
        background: rgba(8,15,26,0.92);
        border: 1px solid rgba(0,217,255,0.1);
        border-radius: 12px; padding: 16px 14px 12px;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35);
        transition: transform .18s ease;
    }
    .ip-sku-card:hover { transform: translateY(-3px); }
    /* ── Recommendation box ── */
    .ip-rec {
        background: linear-gradient(135deg,rgba(11,18,32,0.97),rgba(6,12,24,0.95));
        border: 1px solid rgba(0,217,255,0.1);
        border-left: 3px solid #00D9FF;
        border-radius: 14px; padding: 22px 26px;
        box-shadow: 0 6px 28px rgba(0,0,0,0.4),
                    inset 0 1px 0 rgba(0,217,255,0.04);
    }
    .ip-rec-title {
        font-family: 'Orbitron', sans-serif;
        font-size: .6rem; font-weight: 800;
        letter-spacing: .2em; text-transform: uppercase;
        color: #00D9FF; margin-bottom: 14px;
    }
    .ip-rec-item {
        display: flex; gap: 10px; align-items: flex-start;
        margin-bottom: 9px;
    }
    .ip-rec-dot {
        width: 6px; height: 6px; border-radius: 50%;
        flex-shrink: 0; margin-top: 5px;
    }
    .ip-rec-text {
        font-size: .8rem; color: #94A3B8; line-height: 1.55;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>"
        "Policy Engine · Optimization Active</div>"
        "<div class='nexus-hero-title'>Differentiated Inventory Policy</div>"
        "<div class='nexus-hero-sub'>Safety stock optimization · "
        "Reorder point strategy · Service level targets</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # ── Data ──────────────────────────────────────────────────
    res_p = st.session_state.results_p
    policy_summary = res_p.groupby('risk_class').agg({
        'safety_stock':  'mean',
        'reorder_point': 'mean',
        'Z':             'first'
    }).round(2)

    # =========================================================
    #  PREMIUM KPI CARDS
    # =========================================================
    st.markdown('<div class="ip-sec">&#x2295; Portfolio at a Glance</div>',
                unsafe_allow_html=True)

    _ip_total  = len(res_p)
    _ip_avg_ss = int(round(res_p['safety_stock'].mean()))   if 'safety_stock'  in res_p.columns else "N/A"
    _ip_avg_rp = int(round(res_p['reorder_point'].mean()))  if 'reorder_point' in res_p.columns else "N/A"
    _ip_r1_pct = (
        f"{round(100*len(res_p[res_p['risk_class']=='R1'])/_ip_total,1)}%"
        if 'risk_class' in res_p.columns and _ip_total else "N/A"
    )

    _ipk1, _ipk2, _ipk3, _ipk4 = st.columns(4)
    for _col, _val, _lbl in [
        (_ipk1, f"{_ip_total:,}",   "Total SKU"),
        (_ipk2, f"{_ip_avg_ss:,}",  "Avg Safety Stock"),
        (_ipk3, f"{_ip_avg_rp:,}",  "Avg Reorder Point"),
        (_ipk4, _ip_r1_pct,         "High Risk SKU %"),
    ]:
        _col.markdown(
            f"<div class='ip-kpi'>"
            f"<div class='ip-kpi-val'>{_val}</div>"
            f"<div class='ip-kpi-lbl'>{_lbl}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown('<div class="ip-sep"></div>', unsafe_allow_html=True)

    # =========================================================
    #  EXISTING CHARTS (unchanged)
    # =========================================================
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Safety Stock Strategy")
        fig_ss = px.bar(
            policy_summary.reset_index(),
            x='risk_class', y='safety_stock',
            color='risk_class',
            color_discrete_sequence=['#ef4444', '#f97316', '#eab308', '#10b981'],
            title="Average Safety Stock by Risk Class"
        )
        fig_ss.update_layout(**PLOTLY_LAYOUT)
        fig_ss.update_traces(marker_line_width=0)
        st.plotly_chart(fig_ss, use_container_width=True)

    with col_p2:
        st.subheader("Recommended Service Levels")
        sl_data = {
            "Class":         ["R1 (Critical)", "R2 (High)", "R3 (Moderate)", "R4 (Low)"],
            "Service Level": ["99.9%",         "98.0%",     "95.0%",          "90.0%"],
            "Z-Factor":      [3.09,             2.05,        1.65,             1.28],
            "Review":        ["Continuous",     "Weekly",    "Bi-weekly",      "Monthly"]
        }
        st.table(pd.DataFrame(sl_data))

    st.markdown('<div class="ip-sep"></div>', unsafe_allow_html=True)

    # =========================================================
    #  DONUT CHART — Policy Distribution
    # =========================================================
    st.markdown('<div class="ip-sec">&#x25C8; Policy Distribution</div>',
                unsafe_allow_html=True)

    if 'risk_class' in res_p.columns:
        _ip_rc   = res_p['risk_class'].value_counts().reset_index()
        _ip_rc.columns = ['Risk Class', 'Count']
        _ip_fig_donut = px.pie(
            _ip_rc, names='Risk Class', values='Count',
            hole=0.58,
            color='Risk Class',
            color_discrete_map={
                'R1': '#DC2626', 'R2': '#F59E0B',
                'R3': '#00D9FF', 'R4': '#94A3B8'
            },
            title='SKU Distribution by Risk Policy'
        )
        _ip_fig_donut.update_traces(
            textinfo='percent+label',
            textfont=dict(size=11, color='white'),
            marker=dict(line=dict(color='#050B14', width=2)),
            pull=[0.04, 0.02, 0, 0],
            hovertemplate='<b>%{label}</b><br>%{value} SKUs (%{percent})<extra></extra>'
        )
        _ip_fig_donut.update_layout(
            **PLOTLY_LAYOUT,
            
            annotations=[dict(
                text=f'<b>{_ip_total}</b><br><span style="font-size:11px">SKUs</span>',
                x=0.5, y=0.5, font=dict(size=15, color='#E8F3FF'),
                showarrow=False
            )]
        )
        _dc1, _dc2, _dc3 = st.columns([0.5, 2, 0.5])
        with _dc2:
            st.plotly_chart(_ip_fig_donut, use_container_width=True)

    st.markdown('<div class="ip-sep"></div>', unsafe_allow_html=True)

    # =========================================================
    #  SKU INVENTORY POLICY EXPLORER
    # =========================================================
    st.markdown('<div class="ip-sec">&#x2B61; SKU Inventory Policy Explorer</div>',
                unsafe_allow_html=True)

    _ex_all = sorted(res_p['product_id'].dropna().astype(str).unique().tolist())

    _ex_search = st.text_input(
        "Search SKU",
        placeholder="Type SKU name or ID...",
        key="sku_ex_search",
    )
    _ex_filtered = (
        [s for s in _ex_all if _ex_search.strip().lower() in s.lower()]
        if _ex_search.strip() else _ex_all
    )

    if not _ex_filtered:
        st.warning("No SKU found matching your search.")
        _ex_choice = ""
    else:
        _ex_choice = st.selectbox(
            "Select SKU",
            options=[""] + _ex_filtered,
            format_func=lambda x: "Choose a SKU..." if x == "" else x,
            key="sku_ex_select",
        )

    # ── Mini KPI dashboard ────────────────────────────────────
    if _ex_choice:
        _ex_row = res_p[res_p['product_id'].astype(str) == _ex_choice]

        if _ex_row.empty:
            st.info("No data found for this SKU.")
        else:
            _ex_r = _ex_row.iloc[0]

            def _exv(col, fmt=None):
                if col not in _ex_r.index or _ex_r[col] is None:
                    return "N/A"
                v = _ex_r[col]
                try:
                    if fmt == "int":   return int(round(float(v)))
                    if fmt == "float": return round(float(v), 2)
                except Exception:
                    return "N/A"
                return v

            _SL_MAP  = {"R1":"99.9%","R2":"98.0%","R3":"95.0%","R4":"90.0%"}
            _RC_COL  = {"R1":"#DC2626","R2":"#F59E0B","R3":"#00D9FF","R4":"#94A3B8"}
            _rc_val  = str(_exv("risk_class"))
            _rc_col  = _RC_COL.get(_rc_val, "#00D9FF")
            _rrs_val = _exv("RRS", "float")

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            # Row 1 — 4 cards
            _m1, _m2, _m3, _m4 = st.columns(4)
            for _col, _v, _l, _c in [
                (_m1, _rc_val,                    "Risk Policy",    _rc_col),
                (_m2, _exv("safety_stock", "int"), "Safety Stock",  "#00D9FF"),
                (_m3, _exv("reorder_point","int"), "Reorder Point", "#00D9FF"),
                (_m4, _exv("avg_lead_time","int"), "Lead Time (d)", "#00D9FF"),
            ]:
                _col.markdown(
                    f"<div class='ip-sku-card'>"
                    f"<div style='font-family:Orbitron,sans-serif;font-size:1.4rem;"
                    f"font-weight:800;color:{_c};margin-bottom:5px;"
                    f"text-shadow:0 0 12px {_c}66;'>{_v}</div>"
                    f"<div style='font-size:.56rem;font-weight:700;letter-spacing:.18em;"
                    f"text-transform:uppercase;color:rgba(90,122,154,0.9);'>{_l}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # Row 2 — 2 cards
            _m5, _m6, _mpad = st.columns([1, 1, 2])
            _rrs_delta = (
                "Critical" if _rrs_val != "N/A" and float(_rrs_val) > 7 else
                "High"     if _rrs_val != "N/A" and float(_rrs_val) > 5 else
                "Medium"   if _rrs_val != "N/A" and float(_rrs_val) > 3 else
                "Low"      if _rrs_val != "N/A" else None
            )
            _m5.metric("RRS Score",    _rrs_val,
                       delta=_rrs_delta, delta_color="off")
            _m6.metric("Service Level", _SL_MAP.get(_rc_val, "N/A"))

            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

            # =========================================================
            #  SMART RECOMMENDATION BOX
            # =========================================================
            _rrs_f    = float(_rrs_val) if _rrs_val != "N/A" else 0
            _ss_f     = float(_exv("safety_stock",  "float"))                         if _exv("safety_stock","float") != "N/A" else 0
            _lt_f     = float(_exv("avg_lead_time", "float"))                         if _exv("avg_lead_time","float") != "N/A" else 0

            _recs = []

            if _rc_val == "R1":
                _recs.append(("#DC2626",
                    f"<b style='color:#E8F3FF;'>Emergency protocol active.</b> "
                    f"This SKU is Critical (R1). Maintain continuous review "
                    f"and a 99.9% service level target at all times."))
            elif _rc_val == "R2":
                _recs.append(("#F59E0B",
                    f"<b style='color:#E8F3FF;'>Weekly review recommended.</b> "
                    f"High-risk profile requires proactive reorder triggers "
                    f"and dual-supplier validation."))
            elif _rc_val in ("R3","R4"):
                _recs.append(("#10B981",
                    f"<b style='color:#E8F3FF;'>Stable profile.</b> "
                    f"Bi-weekly to monthly review cadence is sufficient. "
                    f"Consider EOQ optimization to reduce holding cost."))

            if _rrs_f > 7:
                _recs.append(("#DC2626",
                    f"<b style='color:#E8F3FF;'>RRS Score {_rrs_val} — Critical threshold.</b> "
                    f"Escalate to procurement director and activate "
                    f"emergency safety stock buffer (+30-50%)."))
            elif _rrs_f > 5:
                _recs.append(("#F59E0B",
                    f"<b style='color:#E8F3FF;'>RRS Score {_rrs_val} — Elevated risk.</b> "
                    f"Review supplier lead time agreements and consider "
                    f"increasing safety stock by 15-25%."))

            if _lt_f > 30:
                _recs.append(("#9B5CF6",
                    f"<b style='color:#E8F3FF;'>Lead time is {int(_lt_f)} days.</b> "
                    f"Long replenishment cycle detected. "
                    f"Consider pre-positioning stock closer to demand points."))

            if _ss_f == 0:
                _recs.append(("#F59E0B",
                    "<b style='color:#E8F3FF;'>Zero safety stock detected.</b> "
                    "This SKU has no buffer against demand variability. "
                    "Immediate recalibration of safety stock formula is advised."))

            if not _recs:
                _recs.append(("#10B981",
                    "<b style='color:#E8F3FF;'>No critical signals detected.</b> "
                    "This SKU is within normal operating parameters. "
                    "Continue standard monitoring cadence."))

            _items_html = "".join([
                f"<div class='ip-rec-item'>"
                f"<div class='ip-rec-dot' style='background:{c};box-shadow:0 0 6px {c}88;'></div>"
                f"<div class='ip-rec-text'>{t}</div>"
                f"</div>"
                for c, t in _recs
            ])
            st.markdown(
                f"<div class='ip-rec'>"
                f"<div class='ip-rec-title'>&#x2B21; AI Smart Recommendation</div>"
                f"{_items_html}"
                f"</div>",
                unsafe_allow_html=True
            )

# ============================================================
#   ANOMALY DETECTION
# ============================================================
elif page == "Anomaly Detection":
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>Anomaly Engine · Real-time Monitoring</div>"
        "<div class='nexus-hero-title'>AI Anomaly Monitoring</div>"
        "<div class='nexus-hero-sub'>Real-time spike detection · 4-week rolling baseline · RED/ORANGE/GREEN alert system</div>"
        "</div>",
        unsafe_allow_html=True
    )

    res_a = st.session_state.results_a
    red_alerts = res_a[(res_a['week'] == res_a['week'].max()) & (res_a['alert_level'] == 'RED')]

    st.subheader(f"Current Critical RED Alerts — Week {res_a['week'].max()}")
    if not red_alerts.empty:
        st.warning(f"⚠️  **{len(red_alerts)} SKU(s)** require immediate intervention.")
        st.table(red_alerts[['product_id', 'risk_class', 'consumption', 'rolling_mean_4w', 'stock_level']])
    else:
        st.success("✅  No critical spikes detected in current week.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Time Series Analysis")
    p_to_view = st.selectbox("Select Product to Monitor", res_a['product_id'].unique())
    p_data    = res_a[res_a['product_id'] == p_to_view]

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=p_data['week'], y=p_data['consumption'],
        name='Consumption',
        line=dict(color='#00D9FF', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(0,217,255,0.05)'
    ))
    fig_ts.add_trace(go.Scatter(
        x=p_data['week'], y=p_data['rolling_mean_4w'],
        name='4W Rolling Mean',
        line=dict(dash='dot', color='#6A8AAA', width=1.8)
    ))
    anomalies = p_data[p_data['is_anomaly'] == 1]
    fig_ts.add_trace(go.Scatter(
        x=anomalies['week'], y=anomalies['consumption'],
        mode='markers',
        name='Anomaly',
        marker=dict(
            color='#FF3B3B',
            size=12,
            symbol='circle',
            line=dict(color='#FF6B6B', width=2)
        )
    ))
    fig_ts.update_layout(
        **PLOTLY_LAYOUT,
        title=f"Consumption Signal — Product {p_to_view}",
        hovermode='x unified'
    )
    st.plotly_chart(fig_ts, use_container_width=True)

# ============================================================
#   STRESS TEST SIMULATOR
# ============================================================
elif page == "Stress Test Simulator":
    from nexus_3d_warehouse import build_warehouse_html as _build_wh

    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>Digital Twin · Crisis Command Engine</div>"
        "<div class='nexus-hero-title'>Stress Test Simulator</div>"
        "<div class='nexus-hero-sub'>Simulate supplier delays, demand surges and stock shocks before they happen</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Crisis header banner
    st.markdown("""
    <div class="crisis-hero">
        <div>
            <div class="crisis-badge">⚡ CRISIS SIMULATION MODE</div>
            <div class="crisis-title">Command Center · Digital Twin</div>
            <div class="crisis-sub">Adjust scenario parameters and launch simulation to assess supply chain resilience</div>
        </div>
        <div class="crisis-live">
            <div class="live-dot"></div> SYSTEM READY
        </div>
    </div>
    """, unsafe_allow_html=True)

    res_p = st.session_state.results_p.copy()

    c1, c2, c3 = st.columns(3)
    with c1:
        lead_time_spike = st.slider("Supplier Delay %",  min_value=0, max_value=200, value=0, step=5)
    with c2:
        demand_surge    = st.slider("Demand Surge %",    min_value=0, max_value=150, value=0, step=5)
    with c3:
        stock_reduction = st.slider("Stock Loss %",      min_value=0, max_value=60,  value=0, step=5)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    run_simulation = st.button("⚡  LAUNCH CRISIS SIMULATION", use_container_width=True)

    if run_simulation:
        # Fallback columns
        if 'avg_consumption' not in res_p.columns: res_p['avg_consumption'] = 10
        if 'stock_level'     not in res_p.columns: res_p['stock_level']     = res_p['safety_stock'] * 100
        if 'unit_cost'       not in res_p.columns: res_p['unit_cost']       = 100

        # ── Calcul simulation ─────────────────────────────────────────────────
        res_p['sim_lead_time'] = res_p['avg_lead_time'] * (1 + lead_time_spike / 100)
        res_p['sim_demand']    = res_p['avg_consumption'] * (1 + demand_surge / 100)
        res_p['sim_stock']     = res_p['stock_level'] * (1 - stock_reduction / 100)
        res_p['sim_need']      = res_p['sim_lead_time'] * res_p['sim_demand']
        res_p['is_rupture']    = res_p['sim_stock'] < res_p['sim_need']

        # ── Persister les résultats de simulation en session ─────────────────
        st.session_state.sim_res_p = res_p.copy()

        rupture_count    = int(res_p['is_rupture'].sum())
        critical_rupture = len(res_p[(res_p['is_rupture']) & (res_p['risk_class'] == 'R1')])
        value_risk       = int(
            (res_p[res_p['is_rupture']]['unit_cost'] * res_p[res_p['is_rupture']]['sim_demand']).sum()
        )

        severity = lead_time_spike * 0.4 + demand_surge * 0.4 + stock_reduction * 0.2
        if   severity < 25: level = "LOW"
        elif severity < 50: level = "MEDIUM"
        elif severity < 80: level = "HIGH"
        else:               level = "CRITICAL"

        # KPI
        st.subheader("Crisis Impact Overview")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Products in Rupture",     rupture_count)
        k2.metric("Critical R1 Impact",      critical_rupture)
        k3.metric("Stock Value at Risk (€)", f"{value_risk:,}")
        k4.metric("Scenario Severity",       level)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Chart
        fig = px.bar(
            pd.DataFrame({"Metric": ["Supplier Delay","Demand Surge","Stock Loss"],
                          "Value":  [lead_time_spike, demand_surge, stock_reduction]}),
            x="Metric", y="Value", color="Metric", title="Scenario Parameters (%)"
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

        # Recommendations
        st.subheader("🧠  AI Recommendations")
        if rupture_count == 0:
            st.success("✅  Current inventory is resilient for this scenario.")
        else:
            st.warning("⚠️  Immediate action recommended:")
            st.markdown("""
            - Urgent reorder of critical items  
            - Activate backup supplier  
            - Increase safety stock temporarily  
            - Daily monitoring until crisis ends  
            """)

        # ── Digital Twin dynamique ─────────────────────────────────────────────
        # Les racks dont is_rupture==True clignotent en rouge dans Three.js
        # via CRITICAL_RACK_SET et CRITICAL_RACK_META injectés par f-string Python.
        _rupture_df    = res_p[res_p['is_rupture'] == True]
        _n_rupt        = int(res_p['is_rupture'].sum())
        _dt_color      = '#FF3B3B' if _n_rupt > 0 else '#00D26A'
        _dt_label      = f"⚠ {_n_rupt} RUPTURE{'S' if _n_rupt != 1 else ''} DÉTECTÉE{'S' if _n_rupt != 1 else ''}" if _n_rupt else "✓ AUCUNE RUPTURE"
        st.markdown(
            f"<div style='font-size:.62rem;font-weight:700;letter-spacing:.18em;"
            f"text-transform:uppercase;color:{_dt_color};font-family:Orbitron,sans-serif;"
            f"margin:22px 0 8px;display:flex;align-items:center;gap:8px;'>"
            f"<div style='width:2px;height:13px;background:linear-gradient(180deg,{_dt_color},#FF9D2E);"
            f"border-radius:2px;box-shadow:0 0 8px rgba(255,59,59,.6);'></div>"
            f"&#11041; DIGITAL TWIN &middot; {_dt_label} &middot; DONNÉES SIMULATION INJECTÉES"
            f"</div>",
            unsafe_allow_html=True
        )
        with st.container():
            components.html(
                _build_wh(
                    df_rupture = _rupture_df,
                    df_all     = res_p,
                    title      = f"NEXUS · Digital Twin · {_n_rupt} Rupture{'s' if _n_rupt != 1 else ''} · {level}",
                ),
                height=640, scrolling=False
            )
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        # Priority table
        urgent = res_p[res_p['is_rupture']].copy()
        if not urgent.empty:
            st.subheader("🚨  Emergency Procurement Priority")
            export_df = urgent[
                ['product_id', 'risk_class', 'sim_stock', 'sim_need']
            ].sort_values(by=['risk_class', 'sim_need'], ascending=[True, False])

            st.dataframe(export_df, use_container_width=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.subheader("📥  Export Crisis Report")

            col_exp1, col_exp2 = st.columns(2)

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name="Stress_Test", index=False)

            with col_exp1:
                st.download_button(
                    label="⬡  Export Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name="stress_test_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            csv_data = export_df.to_csv(index=False).encode('utf-8')
            with col_exp2:
                st.download_button(
                    label="⬡  Export CSV Report",
                    data=csv_data,
                    file_name="stress_test_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.success("✅  No emergency procurement required.")

    # ── Digital Twin statique (affiché si simulation pas encore lancée) ───────
    if st.session_state.sim_res_p is None:
        st.markdown(
            "<div style='font-size:.62rem;font-weight:700;letter-spacing:.18em;"
            "text-transform:uppercase;color:#00D9FF;font-family:Orbitron,sans-serif;"
            "margin:22px 0 8px;display:flex;align-items:center;gap:8px;'>"
            "<div style='width:2px;height:13px;background:linear-gradient(180deg,#00D9FF,#008CFF);"
            "border-radius:2px;box-shadow:0 0 8px rgba(0,217,255,.6);'></div>"
            "&#11041; DIGITAL TWIN &middot; EN ATTENTE &middot; LANCE UNE SIMULATION POUR ACTIVER LES ALERTES"
            "</div>",
            unsafe_allow_html=True
        )
        with st.container():
            components.html(
                _build_wh(
                    df_rupture = pd.DataFrame(),
                    df_all     = st.session_state.results_p,
                    title      = "NEXUS · Digital Twin · Entrepôt A-7 · En attente",
                ),
                height=640, scrolling=False
            )
# ============================================================
#   NEXUS VOICE AI — Ultra Premium JARVIS Interface
# ============================================================
elif page == "Nexus Voice AI":
    import base64, tempfile, os, re, requests as _requests

    # ── Ollama configuration ─────────────────────────────────
    _OLLAMA_URL   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    _OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    # ── Session state ────────────────────────────────────────
    if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
    if "voice_enabled"  not in st.session_state: st.session_state.voice_enabled  = True
    if "tts_audio_b64"  not in st.session_state: st.session_state.tts_audio_b64  = None

    # ── TTS helper ───────────────────────────────────────────
    def generate_voice_response(text: str):
        clean = re.sub(r"[*_`#>\[\]()!]", "", text)
        clean = re.sub(r"\n+", " ", clean).strip()[:800]
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                gTTS(text=clean, lang="en", slow=False).save(tmp.name)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.unlink(tmp_path)
            return b64
        except Exception:
            return None

    def autoplay_audio(b64_mp3: str):
        st.components.v1.html(
            f'<audio autoplay style="display:none"><source src="data:audio/mpeg;base64,{b64_mp3}" type="audio/mpeg"></audio>',
            height=0,
        )

    def build_system_context() -> str:
        lines = [
            "You are NEXUS, an advanced AI supply chain intelligence assistant with a concise, "
            "authoritative style (think JARVIS). You analyse inventory risk data and give actionable insights. "
            "Keep responses under 120 words unless the user asks for detail. "
            "Never use markdown headers — use clean sentences and short bullet lines if needed."
        ]
        if st.session_state.results_p is not None:
            rp = st.session_state.results_p
            lines.append(
                f"Loaded dataset: {len(rp)} SKUs. "
                f"Risk distribution — R1:{(rp['risk_class']=='R1').sum()} "
                f"R2:{(rp['risk_class']=='R2').sum()} "
                f"R3:{(rp['risk_class']=='R3').sum()} "
                f"R4:{(rp['risk_class']=='R4').sum()}. "
                f"Average RRS score: {rp['RRS'].mean():.2f}."
            )
        if st.session_state.results_a is not None:
            ra = st.session_state.results_a
            wk = ra["week"].max()
            red = len(ra[(ra["week"] == wk) & (ra["alert_level"] == "RED")])
            lines.append(f"Latest anomaly week {wk}: {red} RED alerts active.")
        return " ".join(lines)

    # ── Ultra-premium CSS ────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;500;600&display=swap');

    /* ── ORB ANIMATION ── */
    @keyframes orbPulse {
        0%,100% { transform: scale(1);    opacity: 0.85; box-shadow: 0 0 60px 20px rgba(0,217,255,0.25), 0 0 120px 50px rgba(0,100,255,0.12), inset 0 0 40px rgba(0,217,255,0.1); }
        50%      { transform: scale(1.06); opacity: 1;    box-shadow: 0 0 90px 35px rgba(0,217,255,0.4),  0 0 180px 80px rgba(0,100,255,0.18), inset 0 0 60px rgba(0,217,255,0.2); }
    }
    @keyframes orbRing1 {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }
    @keyframes orbRing2 {
        from { transform: rotate(0deg) rotateX(60deg); }
        to   { transform: rotate(-360deg) rotateX(60deg); }
    }
    @keyframes waveBar {
        0%,100% { height: 4px;  opacity: 0.3; }
        50%      { height: 28px; opacity: 1; }
    }
    @keyframes scanLine {
        0%   { top: 0%;   opacity: 0; }
        10%  { opacity: 0.6; }
        90%  { opacity: 0.6; }
        100% { top: 100%; opacity: 0; }
    }
    @keyframes msgSlideIn {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes statusBlink {
        0%,100% { opacity: 1; }
        50%      { opacity: 0.3; }
    }
    @keyframes holoBorder {
        0%,100% { border-color: rgba(0,217,255,0.3); box-shadow: 0 0 20px rgba(0,217,255,0.1); }
        50%      { border-color: rgba(0,217,255,0.7); box-shadow: 0 0 40px rgba(0,217,255,0.25); }
    }
    @keyframes cornerPulse {
        0%,100% { opacity: 0.4; }
        50%      { opacity: 1; }
    }
    @keyframes dataStream {
        from { background-position: 0 0; }
        to   { background-position: 0 100px; }
    }

    /* ── LAYOUT WRAPPERS ── */
    .voice-page-shell {
        display: flex;
        flex-direction: column;
        gap: 0;
        min-height: calc(100vh - 120px);
        position: relative;
    }

    /* ── HERO PANEL ── */
    .voice-hero {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 32px 40px 28px;
        background:
            linear-gradient(135deg, rgba(0,217,255,0.04) 0%, transparent 50%),
            linear-gradient(180deg, rgba(0,20,40,0.95) 0%, rgba(5,11,20,0.98) 100%);
        border: 1px solid rgba(0,217,255,0.1);
        border-radius: 20px;
        margin-bottom: 20px;
        overflow: hidden;
    }
    .voice-hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background:
            repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(0,217,255,0.018) 32px),
            repeating-linear-gradient(90deg, transparent, transparent 31px, rgba(0,217,255,0.018) 32px);
        pointer-events: none;
        animation: dataStream 8s linear infinite;
    }
    .voice-hero::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00D9FF 30%, #008CFF 70%, transparent 100%);
    }
    /* Corner brackets */
    .voice-hero-corner {
        position: absolute;
        width: 20px; height: 20px;
        animation: cornerPulse 3s ease-in-out infinite;
    }
    .voice-hero-corner.tl { top: 12px; left: 12px; border-top: 2px solid #00D9FF; border-left: 2px solid #00D9FF; }
    .voice-hero-corner.tr { top: 12px; right: 12px; border-top: 2px solid #00D9FF; border-right: 2px solid #00D9FF; animation-delay: 0.5s; }
    .voice-hero-corner.bl { bottom: 12px; left: 12px; border-bottom: 2px solid #00D9FF; border-left: 2px solid #00D9FF; animation-delay: 1s; }
    .voice-hero-corner.br { bottom: 12px; right: 12px; border-bottom: 2px solid #00D9FF; border-right: 2px solid #00D9FF; animation-delay: 1.5s; }

    .voice-hero-left { flex: 1; z-index: 1; }
    .voice-hero-eyebrow {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.62rem;
        color: #00D9FF;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .voice-hero-eyebrow::before {
        content: '';
        display: inline-block;
        width: 24px; height: 1px;
        background: #00D9FF;
        opacity: 0.7;
    }
    .voice-hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #E8F3FF;
        text-shadow: 0 0 40px rgba(0,217,255,0.4), 0 0 80px rgba(0,217,255,0.15);
        line-height: 1;
        margin-bottom: 10px;
    }
    .voice-hero-title span { color: #00D9FF; }
    .voice-hero-sub {
        font-family: 'Exo 2', sans-serif;
        font-size: 0.8rem;
        color: #4A6A8A;
        letter-spacing: 0.06em;
    }
    .voice-hero-stats {
        display: flex;
        gap: 28px;
        margin-top: 18px;
    }
    .voice-stat {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .voice-stat-val {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.1rem;
        color: #00D9FF;
        text-shadow: 0 0 12px rgba(0,217,255,0.5);
    }
    .voice-stat-lbl {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.5rem;
        color: #2A4060;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    /* ── ORB CONTAINER ── */
    .voice-orb-shell {
        position: relative;
        width: 140px;
        height: 140px;
        flex-shrink: 0;
        z-index: 1;
        margin-left: 40px;
    }
    .voice-orb {
        position: absolute;
        inset: 20px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%,
            rgba(0,217,255,0.5) 0%,
            rgba(0,100,200,0.3) 40%,
            rgba(0,30,80,0.8) 70%,
            rgba(0,10,30,0.95) 100%
        );
        animation: orbPulse 3s ease-in-out infinite;
        box-shadow: 0 0 60px 20px rgba(0,217,255,0.25), 0 0 120px 50px rgba(0,100,255,0.12);
    }
    .voice-orb-ring {
        position: absolute;
        border-radius: 50%;
        border: 1px solid rgba(0,217,255,0.35);
    }
    .voice-orb-ring-1 {
        inset: 10px;
        border-style: dashed;
        animation: orbRing1 8s linear infinite;
    }
    .voice-orb-ring-2 {
        inset: 2px;
        border-color: rgba(0,140,255,0.2);
        animation: orbRing1 12s linear infinite reverse;
    }
    .voice-orb-label {
        position: absolute;
        bottom: 0; left: 50%;
        transform: translateX(-50%);
        font-family: 'Orbitron', sans-serif;
        font-size: 0.48rem;
        color: #00D9FF;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        white-space: nowrap;
        opacity: 0.7;
    }

    /* ── WAVEFORM ── */
    .voice-wave {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 32px;
    }
    .voice-wave-bar {
        width: 3px;
        border-radius: 2px;
        background: linear-gradient(180deg, #00D9FF, #0066CC);
        animation: waveBar 1.2s ease-in-out infinite;
    }
    .voice-wave-bar:nth-child(1)  { animation-delay: 0.0s; }
    .voice-wave-bar:nth-child(2)  { animation-delay: 0.1s; }
    .voice-wave-bar:nth-child(3)  { animation-delay: 0.2s; }
    .voice-wave-bar:nth-child(4)  { animation-delay: 0.3s; }
    .voice-wave-bar:nth-child(5)  { animation-delay: 0.4s; }
    .voice-wave-bar:nth-child(6)  { animation-delay: 0.3s; }
    .voice-wave-bar:nth-child(7)  { animation-delay: 0.2s; }
    .voice-wave-bar:nth-child(8)  { animation-delay: 0.1s; }
    .voice-wave-bar:nth-child(9)  { animation-delay: 0.0s; }
    .voice-wave-bar:nth-child(10) { animation-delay: 0.15s; }
    .voice-wave-bar:nth-child(11) { animation-delay: 0.25s; }
    .voice-wave-bar:nth-child(12) { animation-delay: 0.35s; }

    /* ── CONTROL BAR ── */
    .voice-control-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 20px;
        background: rgba(4,8,16,0.9);
        border: 1px solid rgba(0,217,255,0.08);
        border-radius: 14px;
        margin-bottom: 16px;
        backdrop-filter: blur(12px);
    }
    .vc-btn {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 18px;
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid;
        white-space: nowrap;
    }
    .vc-btn-voice-on {
        background: rgba(0,210,106,0.08);
        border-color: rgba(0,210,106,0.3);
        color: #00D26A;
    }
    .vc-btn-voice-off {
        background: rgba(255,59,59,0.08);
        border-color: rgba(255,59,59,0.3);
        color: #FF3B3B;
    }
    .vc-status-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
        animation: statusBlink 2s ease-in-out infinite;
    }
    .vc-model-badge {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(0,217,255,0.04);
        border: 1px solid rgba(0,217,255,0.1);
        border-radius: 6px;
    }
    .vc-model-name {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.7rem;
        color: #00D9FF;
        opacity: 0.8;
    }
    .vc-msg-count {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.65rem;
        color: #3A6080;
    }

    /* ── CHAT PANEL ── */
    .voice-chat-panel {
        position: relative;
        background:
            linear-gradient(180deg, rgba(4,8,16,0.97) 0%, rgba(5,11,20,0.99) 100%);
        border: 1px solid rgba(0,217,255,0.1);
        border-radius: 18px;
        overflow: hidden;
        box-shadow:
            0 8px 40px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(0,217,255,0.05),
            inset 0 -1px 0 rgba(0,0,0,0.3);
    }
    .voice-chat-panel::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0,217,255,0.6), rgba(0,140,255,0.4), transparent);
        z-index: 2;
    }

    /* Scan line effect */
    .voice-chat-panel::after {
        content: '';
        position: absolute;
        left: 0; right: 0;
        height: 80px;
        background: linear-gradient(180deg, transparent, rgba(0,217,255,0.015), transparent);
        pointer-events: none;
        z-index: 1;
        animation: scanLine 6s linear infinite;
    }

    .chat-panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 22px;
        border-bottom: 1px solid rgba(0,217,255,0.06);
        background: rgba(0,217,255,0.02);
    }
    .chat-panel-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.58rem;
        font-weight: 700;
        color: #00D9FF;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }
    .chat-panel-indicators {
        display: flex;
        gap: 6px;
    }
    .chat-dot { width: 8px; height: 8px; border-radius: 50%; }
    .chat-dot-r { background: #FF3B3B; opacity: 0.7; }
    .chat-dot-y { background: #FFB800; opacity: 0.7; }
    .chat-dot-g { background: #00D26A; opacity: 0.7; animation: statusBlink 2s ease-in-out infinite; }

    .voice-chat-messages {
        max-height: 440px;
        overflow-y: auto;
        padding: 24px 20px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        scrollbar-width: thin;
        scrollbar-color: rgba(0,217,255,0.2) transparent;
    }
    .voice-chat-messages::-webkit-scrollbar { width: 4px; }
    .voice-chat-messages::-webkit-scrollbar-track { background: transparent; }
    .voice-chat-messages::-webkit-scrollbar-thumb {
        background: rgba(0,217,255,0.2);
        border-radius: 4px;
    }

    /* Empty state */
    .chat-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        gap: 16px;
    }
    .chat-empty-orb {
        width: 64px; height: 64px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, rgba(0,217,255,0.3), rgba(0,50,120,0.5), rgba(0,10,30,0.9));
        box-shadow: 0 0 30px rgba(0,217,255,0.15);
        animation: orbPulse 3s ease-in-out infinite;
    }
    .chat-empty-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        color: #1E3A5A;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }
    .chat-empty-sub {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.68rem;
        color: #0E2030;
        letter-spacing: 0.08em;
    }
    .chat-empty-hints {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 8px;
        width: 100%;
        max-width: 420px;
    }
    .chat-hint {
        padding: 10px 16px;
        background: rgba(0,217,255,0.025);
        border: 1px solid rgba(0,217,255,0.07);
        border-radius: 10px;
        font-family: 'Exo 2', sans-serif;
        font-size: 0.75rem;
        color: #2A4A6A;
        cursor: default;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .chat-hint::before {
        content: '›';
        color: rgba(0,217,255,0.3);
        font-size: 1rem;
        flex-shrink: 0;
    }

    /* Message rows */
    .msg-row-user {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        animation: msgSlideIn 0.3s ease both;
    }
    .msg-row-ai {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        animation: msgSlideIn 0.3s ease both;
    }
    .msg-meta-user {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.55rem;
        color: #2A5080;
        letter-spacing: 0.14em;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .msg-meta-ai {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.55rem;
        color: #00D9FF;
        letter-spacing: 0.14em;
        margin-bottom: 5px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
        opacity: 0.8;
    }
    .msg-bubble-user {
        max-width: 72%;
        padding: 12px 18px;
        background: linear-gradient(135deg, rgba(0,140,255,0.12), rgba(0,80,180,0.08));
        border: 1px solid rgba(0,140,255,0.25);
        border-radius: 18px 18px 4px 18px;
        font-family: 'Exo 2', sans-serif;
        font-size: 0.875rem;
        color: #C8E0FF;
        line-height: 1.6;
        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
    }
    .msg-bubble-ai {
        max-width: 80%;
        padding: 14px 20px;
        background: linear-gradient(135deg, rgba(0,30,60,0.9), rgba(0,20,45,0.95));
        border: 1px solid rgba(0,217,255,0.14);
        border-left: 3px solid #00D9FF;
        border-radius: 4px 18px 18px 18px;
        font-family: 'Exo 2', sans-serif;
        font-size: 0.875rem;
        color: #A8CCF0;
        line-height: 1.7;
        box-shadow:
            0 2px 20px rgba(0,0,0,0.4),
            0 0 0 0.5px rgba(0,217,255,0.08) inset;
        position: relative;
    }
    .msg-bubble-ai::before {
        content: '⬡';
        position: absolute;
        top: -10px;
        left: 14px;
        font-size: 0.9rem;
        color: #00D9FF;
        text-shadow: 0 0 12px rgba(0,217,255,0.8);
        background: #050B14;
        padding: 0 4px;
    }
    .msg-audio-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        background: rgba(0,210,106,0.1);
        border: 1px solid rgba(0,210,106,0.2);
        border-radius: 20px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.5rem;
        color: #00D26A;
        letter-spacing: 0.1em;
    }

    /* ── INPUT ZONE ── */
    .voice-input-zone {
        padding: 16px 20px 20px;
        border-top: 1px solid rgba(0,217,255,0.06);
        background: rgba(0,217,255,0.015);
        display: flex;
        gap: 0;
        align-items: center;
        position: relative;
    }
    .voice-input-zone::before {
        content: 'INPUT CHANNEL OPEN';
        position: absolute;
        top: -9px; left: 22px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.48rem;
        color: rgba(0,217,255,0.4);
        letter-spacing: 0.2em;
        background: #050B14;
        padding: 0 8px;
    }

    /* Override Streamlit input inside voice zone */
    .voice-input-inner .stTextInput input {
        background: rgba(0,8,20,0.97) !important;
        border: 1px solid rgba(0,217,255,0.18) !important;
        border-right: none !important;
        border-radius: 10px 0 0 10px !important;
        color: #C8E0FF !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.88rem !important;
        padding: 12px 18px !important;
        letter-spacing: 0.03em;
        animation: holoBorder 4s ease-in-out infinite;
    }
    .voice-input-inner .stTextInput input:focus {
        border-color: rgba(0,217,255,0.5) !important;
        box-shadow: 0 0 0 2px rgba(0,217,255,0.06), 0 0 20px rgba(0,217,255,0.05) !important;
        animation: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Compute live stats ───────────────────────────────────
    n_msgs = len(st.session_state.chat_history)
    voice_state_label = "ACTIVE" if st.session_state.voice_enabled else "MUTED"
    model_display = _OLLAMA_MODEL.upper()

    # ── Hero panel (CSS + HTML in one block to ensure styles apply) ──
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;500;600&display=swap');
    @keyframes orbPulse {{
        0%,100% {{ transform: scale(1);    opacity: 0.85; box-shadow: 0 0 60px 20px rgba(0,217,255,0.25), 0 0 120px 50px rgba(0,100,255,0.12), inset 0 0 40px rgba(0,217,255,0.1); }}
        50%      {{ transform: scale(1.06); opacity: 1;    box-shadow: 0 0 90px 35px rgba(0,217,255,0.4),  0 0 180px 80px rgba(0,100,255,0.18), inset 0 0 60px rgba(0,217,255,0.2); }}
    }}
    @keyframes orbRing1 {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    @keyframes orbRing2 {{ from {{ transform: rotate(0deg) rotateX(60deg); }} to {{ transform: rotate(-360deg) rotateX(60deg); }} }}
    @keyframes cornerPulse {{ 0%,100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}
    @keyframes dataStream {{ from {{ background-position: 0 0; }} to {{ background-position: 0 100px; }} }}
    .nxhero {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 32px 40px 28px;
        background: linear-gradient(135deg, rgba(0,217,255,0.04) 0%, transparent 50%),
                    linear-gradient(180deg, rgba(0,20,40,0.95) 0%, rgba(5,11,20,0.98) 100%);
        border: 1px solid rgba(0,217,255,0.1);
        border-top: 2px solid #00D9FF;
        border-radius: 20px;
        margin-bottom: 20px;
        overflow: hidden;
    }}
    .nxhero-grid {{
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(0,217,255,0.018) 32px),
                    repeating-linear-gradient(90deg, transparent, transparent 31px, rgba(0,217,255,0.018) 32px);
        pointer-events: none;
        animation: dataStream 8s linear infinite;
    }}
    .nxhero-corner {{
        position: absolute;
        width: 20px; height: 20px;
        animation: cornerPulse 3s ease-in-out infinite;
    }}
    .nxhero-corner.tl {{ top: 12px; left: 12px; border-top: 2px solid #00D9FF; border-left: 2px solid #00D9FF; }}
    .nxhero-corner.tr {{ top: 12px; right: 12px; border-top: 2px solid #00D9FF; border-right: 2px solid #00D9FF; animation-delay: 0.5s; }}
    .nxhero-corner.bl {{ bottom: 12px; left: 12px; border-bottom: 2px solid #00D9FF; border-left: 2px solid #00D9FF; animation-delay: 1s; }}
    .nxhero-corner.br {{ bottom: 12px; right: 12px; border-bottom: 2px solid #00D9FF; border-right: 2px solid #00D9FF; animation-delay: 1.5s; }}
    .nxhero-left {{ flex: 1; z-index: 1; }}
    .nxhero-eyebrow {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.62rem; color: #00D9FF;
        letter-spacing: 0.3em; text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .nxhero-title {{
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4rem; font-weight: 900;
        letter-spacing: 0.08em; text-transform: uppercase;
        color: #E8F3FF;
        text-shadow: 0 0 40px rgba(0,217,255,0.4), 0 0 80px rgba(0,217,255,0.15);
        line-height: 1; margin-bottom: 10px;
    }}
    .nxhero-title span {{ color: #00D9FF; }}
    .nxhero-sub {{
        font-family: 'Exo 2', sans-serif;
        font-size: 0.8rem; color: #4A6A8A; letter-spacing: 0.06em;
    }}
    .nxhero-stats {{ display: flex; gap: 28px; margin-top: 18px; }}
    .nxstat {{ display: flex; flex-direction: column; gap: 2px; }}
    .nxstat-val {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.1rem; color: #00D9FF;
        text-shadow: 0 0 12px rgba(0,217,255,0.5);
    }}
    .nxstat-lbl {{
        font-family: 'Orbitron', sans-serif;
        font-size: 0.5rem; color: #2A4060;
        letter-spacing: 0.18em; text-transform: uppercase;
    }}
    .nxorb-shell {{
        position: relative; width: 140px; height: 140px;
        flex-shrink: 0; z-index: 1; margin-left: 40px;
    }}
    .nxorb {{
        position: absolute; inset: 20px; border-radius: 50%;
        background: radial-gradient(circle at 35% 35%,
            rgba(0,217,255,0.5) 0%, rgba(0,100,200,0.3) 40%,
            rgba(0,30,80,0.8) 70%, rgba(0,10,30,0.95) 100%);
        animation: orbPulse 3s ease-in-out infinite;
        box-shadow: 0 0 60px 20px rgba(0,217,255,0.25), 0 0 120px 50px rgba(0,100,255,0.12);
    }}
    .nxorb-ring {{
        position: absolute; border-radius: 50%;
        border: 1px solid rgba(0,217,255,0.35);
    }}
    .nxorb-ring-1 {{ inset: 10px; border-style: dashed; animation: orbRing1 8s linear infinite; }}
    .nxorb-ring-2 {{ inset: 2px; border-color: rgba(0,140,255,0.2); animation: orbRing1 12s linear infinite reverse; }}
    .nxorb-label {{
        position: absolute; bottom: 0; left: 50%;
        transform: translateX(-50%);
        font-family: 'Orbitron', sans-serif;
        font-size: 0.48rem; color: #00D9FF;
        letter-spacing: 0.25em; text-transform: uppercase;
        white-space: nowrap; opacity: 0.7;
    }}
    </style>
    <div class="nxhero">
        <div class="nxhero-grid"></div>
        <div class="nxhero-corner tl"></div>
        <div class="nxhero-corner tr"></div>
        <div class="nxhero-corner bl"></div>
        <div class="nxhero-corner br"></div>
        <div class="nxhero-left">
            <div class="nxhero-eyebrow">JARVIS PROTOCOL · VOICE INTELLIGENCE</div>
            <div class="nxhero-title">NEXUS <span>VOICE</span> AI</div>
            <div class="nxhero-sub">Real-time TTS · Local LLM · Supply Chain Intelligence · Autonomous Analysis</div>
            <div class="nxhero-stats">
                <div class="nxstat"><div class="nxstat-val">{n_msgs}</div><div class="nxstat-lbl">Messages</div></div>
                <div class="nxstat"><div class="nxstat-val">{model_display}</div><div class="nxstat-lbl">Model</div></div>
                <div class="nxstat"><div class="nxstat-val">{voice_state_label}</div><div class="nxstat-lbl">Voice</div></div>
            </div>
        </div>
        <div class="nxorb-shell">
            <div class="nxorb-ring nxorb-ring-2"></div>
            <div class="nxorb-ring nxorb-ring-1"></div>
            <div class="nxorb"></div>
            <div class="nxorb-label">NEXUS · ONLINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Control buttons (Streamlit native for interactivity) ─
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.2, 1, 1, 3])
    with ctrl1:
        v_label = "🔊  VOICE ON" if st.session_state.voice_enabled else "🔇  MUTED"
        if st.button(v_label, use_container_width=True, key="btn_voice_toggle"):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            st.rerun()
    with ctrl2:
        if st.button("🗑  CLEAR", use_container_width=True, key="btn_clear_chat"):
            st.session_state.chat_history  = []
            st.session_state.tts_audio_b64 = None
            st.rerun()
    with ctrl3:
        if st.button("⬡  STATUS", use_container_width=True, key="btn_status"):
            pass
    with ctrl4:
        dot_color = "#00D26A" if st.session_state.voice_enabled else "#FF3B3B"
        dot_label = "VOICE SYNTHESIS ACTIVE" if st.session_state.voice_enabled else "VOICE SYNTHESIS MUTED"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;padding:10px 18px;"
            f"background:rgba(4,8,16,0.9);border:1px solid rgba(0,217,255,0.07);"
            f"border-radius:8px;height:42px;'>"
            f"<div style='width:7px;height:7px;border-radius:50%;background:{dot_color};"
            f"box-shadow:0 0 8px {dot_color};flex-shrink:0;'></div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;"
            f"color:#3A6080;letter-spacing:0.12em;'>{dot_label}</div>"
            f"<div style='margin-left:auto;display:flex;align-items:center;gap:3px;'>"
            + "".join(['<div class="voice-wave-bar" style="width:3px;border-radius:2px;background:linear-gradient(180deg,#00D9FF,#0066CC);"></div>']*12 if st.session_state.voice_enabled else [])
            + "</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Chat panel ───────────────────────────────────────────
    chat_body = ""
    if not st.session_state.chat_history:
        chat_body = """
        <div class="chat-empty">
            <div class="chat-empty-orb"></div>
            <div class="chat-empty-title">NEXUS — STANDING BY</div>
            <div class="chat-empty-sub">_  awaiting operator input  _</div>
            <div class="chat-empty-hints">
                <div class="chat-hint">What are my top R1 critical SKUs right now?</div>
                <div class="chat-hint">Summarize current RED alerts and their impact</div>
                <div class="chat-hint">Recommend reorder strategy for high-risk items</div>
                <div class="chat-hint">Analyze my inventory resilience score</div>
            </div>
        </div>"""
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_body += f"""
                <div class="msg-row-user">
                    <div class="msg-meta-user">▸ operator input</div>
                    <div class="msg-bubble-user">{msg['content']}</div>
                </div>"""
            else:
                audio_badge = ""
                if msg.get("audio") and st.session_state.voice_enabled:
                    audio_badge = '<span class="msg-audio-badge">▶ VOICE</span>'
                chat_body += f"""
                <div class="msg-row-ai">
                    <div class="msg-meta-ai">⬡ NEXUS · AI RESPONSE {audio_badge}</div>
                    <div class="msg-bubble-ai">{msg['content']}</div>
                </div>"""

    st.markdown(f"""
    <div class="voice-chat-panel">
        <div class="chat-panel-header">
            <div class="chat-panel-title">◈ NEXUS INTELLIGENCE FEED · SECURE CHANNEL</div>
            <div class="chat-panel-indicators">
                <div class="chat-dot chat-dot-r"></div>
                <div class="chat-dot chat-dot-y"></div>
                <div class="chat-dot chat-dot-g"></div>
            </div>
        </div>
        <div class="voice-chat-messages">{chat_body}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-play TTS ─────────────────────────────────────────
    if st.session_state.voice_enabled and st.session_state.tts_audio_b64:
        autoplay_audio(st.session_state.tts_audio_b64)
        st.session_state.tts_audio_b64 = None

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Input form ────────────────────────────────────────────
    with st.form("nexus_voice_form", clear_on_submit=True):
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input(
                "nexus_input",
                placeholder="⬡  Transmit to NEXUS — ask about risks, anomalies, strategy…",
                label_visibility="collapsed",
            )
        with btn_col:
            submitted = st.form_submit_button("⬡  SEND", use_container_width=True)

    # ── Process submission ────────────────────────────────────
    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

        try:
            system_ctx   = build_system_context()
            history_text = "\n".join(
                f"{'User' if m['role'] == 'user' else 'NEXUS'}: {m['content']}"
                for m in st.session_state.chat_history
            )
            full_prompt = f"{system_ctx}\n\nConversation so far:\n{history_text}"
            resp = _requests.post(
                f"{_OLLAMA_URL}/api/generate",
                json={"model": _OLLAMA_MODEL, "prompt": full_prompt, "stream": False},
                timeout=60,
            )
            resp.raise_for_status()
            ai_text = resp.json().get("response", "").strip()
            if not ai_text:
                ai_text = "[NEXUS OFFLINE] Ollama returned an empty response."
        except _requests.exceptions.ConnectionError:
            ai_text = f"[NEXUS OFFLINE] Cannot reach Ollama at {_OLLAMA_URL} — is it running?"
        except Exception as e:
            ai_text = f"[NEXUS OFFLINE] Ollama error: {e}"

        audio_b64 = None
        if st.session_state.voice_enabled:
            audio_b64 = generate_voice_response(ai_text)

        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": ai_text,
            "audio":   audio_b64 is not None
        })

        if audio_b64:
            st.session_state.tts_audio_b64 = audio_b64

        st.rerun()
# ============================================================
#   EXECUTIVE REPORT PAGE
#   Ajouté proprement — zéro modification du code existant
# ============================================================
elif page == "Executive Report":

    # ── Résoudre la source de données ────────────────────────────────────────
    _rp = st.session_state.get('results_p', None)
    _ra = st.session_state.get('results_a', None)
    _dp = st.session_state.get('df_p', None)

    def _get_df():
        if _rp is not None and hasattr(_rp, 'empty') and not _rp.empty:
            return _rp
        if _ra is not None and hasattr(_ra, 'empty') and not _ra.empty:
            return _ra
        if _dp is not None and hasattr(_dp, 'empty') and not _dp.empty:
            return _dp
        return None

    _df = _get_df()

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='nexus-hero'>"
        "<div class='nexus-badge'><span class='dot'></span>"
        "Board-Level Intelligence · AI Report Engine · Active</div>"
        "<div class='nexus-hero-title'>📄 Executive AI Report Center</div>"
        "<div class='nexus-hero-sub'>"
        "Generate board-level strategic inventory intelligence reports instantly — "
        "McKinsey-grade clarity · Palantir-grade depth · NEXUS precision"
        "</div></div>",
        unsafe_allow_html=True
    )

    # ── NO DATA STATE ─────────────────────────────────────────────────────────
    if _df is None:
        st.markdown("""
        <div style='
            margin: 2rem auto; max-width: 600px;
            background: linear-gradient(135deg, rgba(11,18,32,0.98), rgba(8,15,26,0.96));
            border: 1px solid rgba(255,157,46,0.2);
            border-top: 2px solid #FF9D2E;
            border-radius: 18px; padding: 40px 36px;
            text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        '>
            <div style='font-size:2.8rem; margin-bottom:16px;'>⬡</div>
            <div style='
                font-family: Orbitron, sans-serif; font-size: 0.9rem;
                font-weight: 800; letter-spacing: 0.15em;
                color: #FF9D2E; margin-bottom: 10px; text-transform: uppercase;
            '>No Data Available</div>
            <div style='
                color: #5A7A9A; font-size: 0.82rem; line-height: 1.7;
                font-family: "Exo 2", sans-serif;
            '>
                Upload your product and consumption files in<br>
                <b style="color:#00D9FF;">⊟ Data Management</b> and run the AI classification engine<br>
                before generating an Executive Report.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── COMPUTE KPIs ──────────────────────────────────────────────────────────
    _total   = len(_df)
    _rc      = _df['risk_class'].value_counts().to_dict() if 'risk_class' in _df.columns else {}
    _n_r1    = _rc.get('R1', 0)
    _n_r2    = _rc.get('R2', 0)
    _n_r3    = _rc.get('R3', 0)
    _n_r4    = _rc.get('R4', 0)
    _rrs_avg = round(_df['RRS'].mean(), 2) if 'RRS' in _df.columns else 0.0
    _r1_pct  = round(100 * _n_r1 / _total, 1) if _total else 0
    _health  = ('🔴 CRITICAL' if _r1_pct > 25 else
                '🟠 ELEVATED' if _r1_pct > 10 else
                '🟡 MODERATE' if _r1_pct > 4  else '🟢 HEALTHY')

    # ── SECTION LABEL helper ──────────────────────────────────────────────────
    def _sec(label, color='#00D9FF', icon='◈'):
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;"
            f"margin:2rem 0 0.8rem;'>"
            f"<div style='width:3px;height:20px;"
            f"background:linear-gradient(180deg,{color},transparent);"
            f"border-radius:2px;box-shadow:0 0 8px {color}44;'></div>"
            f"<span style='font-family:Orbitron,sans-serif;font-size:0.62rem;"
            f"font-weight:800;letter-spacing:0.22em;text-transform:uppercase;"
            f"color:{color};text-shadow:0 0 12px {color}66;'>"
            f"{icon} &nbsp;{label}</span>"
            f"<div style='flex:1;height:1px;"
            f"background:linear-gradient(90deg,{color}33,transparent);'></div>"
            f"</div>",
            unsafe_allow_html=True
        )

    # ════════════════════════════════════════════════════════════════════════
    # KPI CARDS
    # ════════════════════════════════════════════════════════════════════════
    _sec('Portfolio Intelligence Metrics', '#00D9FF', '⊕')
    _k1, _k2, _k3, _k4, _k5 = st.columns(5)
    _k1.metric("Total Records",    _total,
               delta="Full Portfolio", delta_color="off")
    _k2.metric("🔴 Critical R1",   _n_r1,
               delta=f"{_r1_pct}% of portfolio",
               delta_color="inverse" if _n_r1 > 0 else "off")
    _k3.metric("🟠 High Risk R2",  _n_r2,
               delta=f"{round(100*_n_r2/_total,1) if _total else 0}%",
               delta_color="off")
    _k4.metric("🟡 Medium R3",     _n_r3,
               delta=f"{round(100*_n_r3/_total,1) if _total else 0}%",
               delta_color="off")
    _k5.metric("Global RRS Score", f"{_rrs_avg}/10",
               delta="Portfolio Risk Index",
               delta_color="inverse" if _rrs_avg > 5 else "off")

    # ════════════════════════════════════════════════════════════════════════
    # REPORT PREVIEW PANEL
    # ════════════════════════════════════════════════════════════════════════
    _sec('Report Preview — Inventory Intelligence Summary', '#00D9FF', '◈')

    _left_col, _right_col = st.columns([1.1, 0.9], gap="large")

    with _left_col:
        # Inventory health card
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(11,18,32,0.98), rgba(8,15,26,0.96));
            border: 1px solid rgba(0,217,255,0.12);
            border-top: 2px solid #00D9FF;
            border-radius: 18px; padding: 24px 28px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); margin-bottom: 16px;
            animation: slideUp 0.4s both;
        '>
            <div style='
                font-family: Orbitron, sans-serif; font-size: 0.55rem;
                font-weight: 800; letter-spacing: 0.24em;
                color: #5A7A9A; text-transform: uppercase; margin-bottom: 14px;
            '>Inventory Health Status</div>
            <div style='font-size: 1.3rem; font-weight: 800; margin-bottom: 8px;
                        font-family: Orbitron, sans-serif;'>{_health}</div>
            <div style='
                display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px;
            '>
                {''.join([
                    f"<div style='background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.25);"
                    f"border-radius:6px;padding:5px 12px;font-size:0.7rem;color:#DC2626;"
                    f"font-family:Orbitron,sans-serif;font-weight:700;letter-spacing:0.08em;'>"
                    f"R1 · {_n_r1} items</div>"
                    if _n_r1 > 0 else "",
                    f"<div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);"
                    f"border-radius:6px;padding:5px 12px;font-size:0.7rem;color:#F59E0B;"
                    f"font-family:Orbitron,sans-serif;font-weight:700;letter-spacing:0.08em;'>"
                    f"R2 · {_n_r2} items</div>"
                    if _n_r2 > 0 else "",
                    f"<div style='background:rgba(0,217,255,0.07);border:1px solid rgba(0,217,255,0.2);"
                    f"border-radius:6px;padding:5px 12px;font-size:0.7rem;color:#00D9FF;"
                    f"font-family:Orbitron,sans-serif;font-weight:700;letter-spacing:0.08em;'>"
                    f"R3 · {_n_r3} items</div>"
                    if _n_r3 > 0 else "",
                    f"<div style='background:rgba(148,163,184,0.07);border:1px solid rgba(148,163,184,0.15);"
                    f"border-radius:6px;padding:5px 12px;font-size:0.7rem;color:#94A3B8;"
                    f"font-family:Orbitron,sans-serif;font-weight:700;letter-spacing:0.08em;'>"
                    f"R4 · {_n_r4} items</div>"
                    if _n_r4 > 0 else "",
                ])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Main detected risks
        st.markdown(f"""
        <div style='
            background: rgba(8,15,26,0.9);
            border: 1px solid rgba(255,59,59,0.12);
            border-top: 2px solid rgba(255,59,59,0.4);
            border-radius: 18px; padding: 22px 28px;
            box-shadow: 0 4px 20px rgba(255,59,59,0.05);
        '>
            <div style='
                font-family: Orbitron, sans-serif; font-size: 0.55rem;
                font-weight: 800; letter-spacing: 0.24em;
                color: #FF3B3B; text-transform: uppercase; margin-bottom: 14px;
            '>Main Detected Risks</div>
            {''.join([
                f"<div style='display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;'>"
                f"<div style='width:6px;height:6px;border-radius:50%;background:#FF3B3B;"
                f"box-shadow:0 0 8px #FF3B3B;flex-shrink:0;margin-top:5px;'></div>"
                f"<span style='font-size:0.8rem;color:#B8D4F0;line-height:1.5;'>{risk}</span></div>"
                for risk in [
                    f"<b style='color:#FF3B3B;'>{_n_r1} Critical items (R1)</b> require immediate procurement action"
                    if _n_r1 > 0 else None,
                    f"<b style='color:#F59E0B;'>{_n_r2} High-risk items (R2)</b> need proactive monitoring"
                    if _n_r2 > 0 else None,
                    f"Global Risk Score of <b style='color:#00D9FF;'>{_rrs_avg}/10</b> — "
                    f"{'above' if _rrs_avg > 5 else 'below'} critical threshold",
                    "Lead time variability detected across supplier network"
                    if 'avg_lead_time' in _df.columns else None,
                ]
                if risk is not None
            ])}
        </div>
        """, unsafe_allow_html=True)

    with _right_col:
        # Urgent actions card
        _urgent_items = _df[_df['risk_class'].isin(['R1','R2'])].nlargest(
            6, 'RRS') if 'RRS' in _df.columns and 'risk_class' in _df.columns             else _df.head(6)

        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(11,18,32,0.98), rgba(8,15,26,0.96));
            border: 1px solid rgba(0,217,255,0.1);
            border-top: 2px solid rgba(255,157,46,0.5);
            border-radius: 18px; padding: 22px 28px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); height: 100%;
        '>
            <div style='
                font-family: Orbitron, sans-serif; font-size: 0.55rem;
                font-weight: 800; letter-spacing: 0.24em;
                color: #FF9D2E; text-transform: uppercase; margin-bottom: 16px;
            '>⚡ Urgent Actions Required</div>
            {''.join([
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:9px 0;border-bottom:1px solid rgba(0,217,255,0.06);'>"
                f"<div>"
                f"<span style='font-family:JetBrains Mono,monospace;font-size:0.78rem;"
                f"color:#E8F3FF;font-weight:600;'>{str(row.get('product_id','—'))}</span>"
                f"<br><span style='font-size:0.65rem;color:#5A7A9A;letter-spacing:0.06em;'>"
                f"Lead time: {str(row.get('avg_lead_time','—'))}d</span>"
                f"</div>"
                f"<div style='text-align:right;'>"
                f"<span style='font-family:Orbitron,sans-serif;font-size:0.62rem;font-weight:800;"
                f"color:{'#DC2626' if str(row.get('risk_class',''))=='R1' else '#F59E0B'};"
                f"background:{'rgba(220,38,38,0.1)' if str(row.get('risk_class',''))=='R1' else 'rgba(245,158,11,0.1)'};"
                f"border:1px solid {'rgba(220,38,38,0.3)' if str(row.get('risk_class',''))=='R1' else 'rgba(245,158,11,0.3)'};"
                f"border-radius:5px;padding:3px 8px;'>{str(row.get('risk_class',''))}</span>"
                f"</div>"
                f"</div>"
                for _, row in _urgent_items.iterrows()
            ])}
            {'<div style="color:#00D26A;font-size:0.75rem;text-align:center;margin-top:14px;padding-top:10px;border-top:1px solid rgba(0,217,255,0.06);">✓ No urgent R1/R2 items detected</div>' if _urgent_items.empty else ''}
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # CHARTS
    # ════════════════════════════════════════════════════════════════════════
    _sec('Risk Analytics — Distribution & Exposure', '#00D9FF', '◈')
    _ch1, _ch2 = st.columns(2, gap="large")

    with _ch1:
        if 'risk_class' in _df.columns:
            _risk_counts = _df['risk_class'].value_counts().reset_index()
            _risk_counts.columns = ['Risk Class', 'Count']
            _RISK_COLORS = {'R1': '#DC2626', 'R2': '#F59E0B', 'R3': '#00D9FF', 'R4': '#94A3B8'}
            _fig_pie = px.pie(
                _risk_counts, names='Risk Class', values='Count',
                title='Risk Class Distribution',
                color='Risk Class', color_discrete_map=_RISK_COLORS,
                hole=0.55,
            )
            _fig_pie.update_traces(
                textinfo='percent+label',
                textfont=dict(size=11, color='white'),
                marker=dict(line=dict(color='#050B14', width=2))
            )
            _fig_pie.update_layout(
                **PLOTLY_LAYOUT,
                showlegend=True,
                
                annotations=[dict(
                    text=f'<b>{_total}</b><br><span style="font-size:10px">items</span>',
                    x=0.5, y=0.5, font=dict(size=14, color='#E8F3FF'),
                    showarrow=False
                )]
            )
            st.plotly_chart(_fig_pie, use_container_width=True)

    with _ch2:
        if 'RRS' in _df.columns and 'risk_class' in _df.columns:
            _top15 = _df.nlargest(12, 'RRS')[
                ['product_id', 'RRS', 'risk_class']
            ].copy()
            _top15['color'] = _top15['risk_class'].map(
                {'R1': '#DC2626', 'R2': '#F59E0B', 'R3': '#00D9FF', 'R4': '#94A3B8'}
            ).fillna('#94A3B8')
            _fig_bar = px.bar(
                _top15, x='product_id', y='RRS',
                title='Top 12 Risk-Ranked Products',
                color='risk_class',
                color_discrete_map={'R1':'#DC2626','R2':'#F59E0B','R3':'#00D9FF','R4':'#94A3B8'},
                text='RRS',
            )
            _fig_bar.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside',
                textfont=dict(size=9, color='white'),
                marker_line_width=0,
            )
            _fig_bar.update_layout(
                **PLOTLY_LAYOUT,
                showlegend=True,
                
                bargap=0.25,
            )
            st.plotly_chart(_fig_bar, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # GENERATE PDF BUTTON
    # ════════════════════════════════════════════════════════════════════════
    _sec('Report Generation Engine', '#9B5CF6', '⬡')

    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(155,92,246,0.06), rgba(8,15,26,0.96));
        border: 1px solid rgba(155,92,246,0.2);
        border-top: 2px solid rgba(155,92,246,0.5);
        border-radius: 18px; padding: 28px 32px;
        text-align: center; margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(155,92,246,0.08);
    '>
        <div style='
            font-family: Orbitron, sans-serif; font-size: 0.62rem;
            font-weight: 800; letter-spacing: 0.22em;
            color: rgba(155,92,246,0.8); text-transform: uppercase;
            margin-bottom: 8px;
        '>Board-Ready Intelligence Package</div>
        <div style='
            font-size: 0.85rem; color: #5A7A9A;
            font-family: "Exo 2", sans-serif; line-height: 1.6;
        '>
            6-page executive PDF · Risk tables · AI recommendations ·
            Distribution charts · Management conclusion
        </div>
    </div>
    """, unsafe_allow_html=True)

    _btn_col1, _btn_col2, _btn_col3 = st.columns([1, 2, 1])
    with _btn_col2:
        _gen_pdf = st.button(
            "📄  GENERATE PDF REPORT",
            use_container_width=True,
            type="primary",
        )

    if _gen_pdf:
        with st.spinner("⬡  Compiling Executive Intelligence Report..."):
            _pdf_out = _generate_nexus_pdf(
                results_p = _rp,
                results_a = _ra,
                df_p      = _dp,
            )
        if _pdf_out:
            st.success("✅  Report ready — click below to download")
            _dl1, _dl2, _dl3 = st.columns([1, 2, 1])
            with _dl2:
                st.download_button(
                    label     = "⬇  DOWNLOAD  NEXUS_Executive_Report.pdf",
                    data      = _pdf_out,
                    file_name = "NEXUS_Executive_Report.pdf",
                    mime      = "application/pdf",
                    use_container_width=True,
                )
        else:
            st.error("❌  Report generation failed. Verify data integrity.")