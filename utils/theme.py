"""
ACE-Omega Theme v3 — Industrial Minimal
Noto Sans SC + Inter font stack (fixes Chinese rendering).
Extreme minimal padding. Clear hierarchy.
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400&display=swap');
:root {
    --bg-0: #0a0a0f; --bg-1: #12121a; --bg-2: #1a1a24; --bg-3: #262630;
    --text-0: #f0f0f2; --text-1: #d4d4d8; --text-2: #8b8b94; --text-3: #55555e;
    --blue: #6ea8fe; --green: #75d9a0; --red: #f28b82; --yellow: #fdd663;
    --purple: #b39ddb; --cyan: #67e8f9; --orange: #f9a856;
    --border: rgba(255,255,255,0.06); --radius: 6px;
    --font: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono: 'JetBrains Mono', 'Noto Sans SC', monospace;
}
*, *::before, *::after { font-family: var(--font) !important; }
code, pre, .stCode, [data-testid="stCode"] { font-family: var(--mono) !important; }

.stApp, [data-testid="stAppViewContainer"], .main {
    background: var(--bg-0) !important; color: var(--text-1) !important;
}
section[data-testid="stSidebar"] > div {
    background: var(--bg-1) !important; border-right: 1px solid var(--border) !important;
    padding-top: 0.5rem !important;
}
[data-testid="stSidebar"] * { color: var(--text-1) !important; }
h1,h2,h3,h4,h5 {
    font-family: var(--font) !important; color: var(--text-0) !important;
    font-weight: 600 !important; letter-spacing: -0.02em !important;
}
h1 { font-size: 24px !important; margin-bottom: 4px !important; }
h2 { font-size: 19px !important; } h3 { font-size: 16px !important; }
p,span,label,div,li { color: var(--text-1) !important; font-size: 14px !important; }

/* Metrics — compact */
[data-testid="stMetric"] {
    background: var(--bg-2) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 10px 14px !important;
}
[data-testid="stMetricValue"] {
    color: var(--blue) !important; font-weight: 700 !important;
    font-size: 22px !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-2) !important; font-size: 11px !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
}

/* Buttons — pill, no decorations */
.stButton>button {
    background: var(--bg-3) !important; color: var(--text-1) !important;
    border: 1px solid var(--border) !important; border-radius: 4px !important;
    padding: 6px 16px !important; font-weight: 500 !important;
    font-size: 13px !important; transition: all .15s !important;
}
.stButton>button:hover {
    background: rgba(110,168,254,0.1) !important;
    border-color: var(--blue) !important; color: var(--blue) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { color: var(--text-2) !important; font-weight: 500 !important; background: transparent !important; padding: 8px 16px !important; font-size: 13px !important; }
.stTabs [aria-selected="true"] { color: var(--blue) !important; border-bottom: 2px solid var(--blue) !important; }

/* Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input,
[data-baseweb="select"]>div, .stSelectbox>div>div {
    background: var(--bg-2) !important; color: var(--text-1) !important;
    border: 1px solid var(--border) !important; border-radius: 4px !important;
    font-size: 13px !important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {
    border-color: var(--blue) !important; box-shadow: 0 0 0 1px rgba(110,168,254,0.2) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-2) !important; border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: var(--radius) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-2) !important; border: 1px solid var(--border) !important;
    border-radius: 4px !important; font-size: 13px !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 1400px !important; }

/* Sidebar nav */
div[data-testid="stSidebarNav"] li div a { color: var(--text-1) !important; font-size: 13px !important; }
div[data-testid="stSidebarNav"] li div a span { font-size: 13px !important; }

/* Slider compact */
[data-testid="stSlider"] label { font-size: 12px !important; }

/* Custom classes */
.ace-card {
    background: var(--bg-2); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 12px 16px; margin-bottom: 8px;
}
.ace-badge {
    display: inline-block; padding: 2px 8px; border-radius: 3px;
    font-size: 10px; font-weight: 600; margin-right: 4px;
}
.b-blue { background: rgba(110,168,254,0.12); color: #6ea8fe; }
.b-green { background: rgba(117,217,160,0.12); color: #75d9a0; }
.b-red { background: rgba(242,139,130,0.12); color: #f28b82; }
.b-yellow { background: rgba(253,214,99,0.12); color: #fdd663; }
.b-purple { background: rgba(179,157,219,0.12); color: #b39ddb; }
.error-bar { background: rgba(242,139,130,0.08); border: 1px solid rgba(242,139,130,0.2); border-radius: 4px; padding: 8px 14px; color: #f28b82; margin-bottom: 8px; }
.warn-bar { background: rgba(253,214,99,0.06); border: 1px solid rgba(253,214,99,0.15); border-radius: 4px; padding: 8px 14px; color: #fdd663; margin-bottom: 8px; }
.info-bar { background: rgba(110,168,254,0.06); border: 1px solid rgba(110,168,254,0.15); border-radius: 4px; padding: 8px 14px; color: #6ea8fe; margin-bottom: 8px; }
.status-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 6px; }
.status-ok { background: #75d9a0; } .status-err { background: #f28b82; } .status-warn { background: #fdd663; }

/* Dataframe compact */
[data-testid="stDataFrame"] { border-radius: 4px !important; font-size: 12px !important; }

/* Progress bar styling */
.stProgress > div > div { background: var(--blue) !important; }

/* Divider */
hr { border-color: var(--border) !important; margin: 8px 0 !important; }
</style>
"""

def inject_theme():
    """Call at top of every page."""
    import streamlit as st
    st.markdown(THEME_CSS, unsafe_allow_html=True)
