import os
import streamlit as st
from dotenv import load_dotenv

# Ensure .env exists with empty values if missing
def ensure_env_file():
    """Ensure .env exists by copying .env.example with empty values if absent."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    env_example_path = os.path.join(base_dir, ".env.example")
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        try:
            with open(env_example_path, "r", encoding="utf-8") as f_ex:
                content = f_ex.read()
            with open(env_path, "w", encoding="utf-8") as f_env:
                f_env.write(content)
        except Exception:
            pass

ensure_env_file()

# Load environment variables from .env
load_dotenv()

from search import get_tavily_api_key
from llm import (
    get_nebius_api_key,
    get_nebius_base_url,
    get_configured_nebius_model_name,
    fetch_available_nebius_models,
    DEFAULT_NEBIUS_BASE_URL
)
from agent import run_verity_agent

# Configure Streamlit page
st.set_page_config(
    page_title="Verity AI | Sourced, Verifiable Knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inline SVG Icons for clean, emoji-free modern UI
ICON_SHIELD = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>"""
ICON_SEARCH = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""
ICON_CHECK = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>"""
ICON_EXTERNAL = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>"""
ICON_CPU = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>"""
ICON_DATABASE = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>"""
ICON_CLOCK = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>"""
ICON_ALERT = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>"""
ICON_SETTINGS = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>"""

# High-Performance Futuristic Dark Theme CSS
st.markdown("""
<style>
    :root {
        --bg-main: #0B1020;
        --surface-card: #121A30;
        --surface-card-hover: #17223D;
        --color-cyan: #22D3EE;
        --color-blue: #4F8CFF;
        --color-violet: #7C5CFF;
        --color-teal: #2DD4BF;
        --color-warning: #F59E0B;
        --color-error: #EF4444;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --border-subtle: rgba(79, 140, 255, 0.16);
        --border-highlight: rgba(34, 211, 238, 0.4);
    }

    .stApp {
        background-color: var(--bg-main) !important;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(79, 140, 255, 0.12) 0%, transparent 60%),
            radial-gradient(circle at 10% 20%, rgba(124, 92, 255, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 90% 80%, rgba(34, 211, 238, 0.06) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0D1426 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }

    h1, h2, h3, h4, h5 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0%, 100% { opacity: 0.8; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.05); }
    }

    .brand-hero {
        padding: 2rem 1rem 1.5rem 1rem;
        text-align: center;
        animation: fadeInSlide 0.6s ease-out;
        position: relative;
    }
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(124, 92, 255, 0.12);
        color: #A5B4FC;
        border: 1px solid rgba(124, 92, 255, 0.35);
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 20px rgba(124, 92, 255, 0.15);
    }
    .brand-title {
        font-size: 3.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.4rem;
        line-height: 1.1;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
    }
    .brand-title-verity {
        color: #F8FAFC;
        text-shadow: 0 0 30px rgba(248, 250, 252, 0.2);
    }
    .brand-title-ai {
        background: linear-gradient(135deg, var(--color-cyan) 0%, var(--color-blue) 50%, var(--color-violet) 100%);
        background-size: 200% 200%;
        animation: gradientFlow 5s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    .brand-tagline {
        font-size: 1.25rem;
        color: #CBD5E1;
        font-weight: 400;
        margin-bottom: 0.6rem;
    }
    .brand-description {
        color: var(--text-muted);
        font-size: 0.95rem;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .verity-card {
        background: var(--surface-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        animation: fadeInSlide 0.5s ease-out;
    }
    .verity-card:hover {
        border-color: var(--border-highlight);
        box-shadow: 0 14px 40px -10px rgba(79, 140, 255, 0.22);
        transform: translateY(-2px);
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--color-cyan);
        margin-bottom: 0.9rem;
    }

    /* Key Status Row */
    .key-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.55rem 0.8rem;
        background: rgba(18, 26, 48, 0.6);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        margin-bottom: 0.6rem;
    }
    .status-badge-ok {
        background: rgba(45, 212, 191, 0.15);
        color: var(--color-teal);
        border: 1px solid rgba(45, 212, 191, 0.4);
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .status-badge-missing {
        background: rgba(245, 158, 11, 0.15);
        color: var(--color-warning);
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    /* Missing Key Setup Alert Card */
    .setup-required-card {
        background: linear-gradient(180deg, rgba(24, 20, 36, 0.95) 0%, rgba(18, 26, 48, 0.95) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 4px solid var(--color-warning);
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.8rem;
        animation: fadeInSlide 0.5s ease-out;
    }

    div[data-testid="stButton"] button {
        background-color: var(--surface-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: var(--surface-card-hover) !important;
        border-color: var(--color-cyan) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px -4px rgba(34, 211, 238, 0.3) !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, var(--color-cyan) 0%, var(--color-blue) 50%, var(--color-violet) 100%) !important;
        background-size: 200% 200% !important;
        animation: gradientFlow 5s ease infinite !important;
        color: #0B1020 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        padding: 0.75rem 1.6rem !important;
        box-shadow: 0 4px 25px rgba(79, 140, 255, 0.45) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 35px rgba(34, 211, 238, 0.55) !important;
        color: #050811 !important;
    }

    div[data-testid="stTextInput"] input {
        background-color: #0F162B !important;
        color: #F8FAFC !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.2rem !important;
        font-size: 1.05rem !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--color-cyan) !important;
        box-shadow: 0 0 20px rgba(34, 211, 238, 0.25) !important;
    }

    .synthesis-card {
        background: linear-gradient(180deg, rgba(18, 26, 48, 0.9) 0%, rgba(13, 20, 38, 0.95) 100%);
        border: 1px solid rgba(79, 140, 255, 0.35);
        border-left: 4px solid var(--color-cyan);
        border-radius: 14px;
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        line-height: 1.75;
        font-size: 1.05rem;
        color: #E2E8F0;
        box-shadow: 0 12px 35px -5px rgba(0, 0, 0, 0.55);
        animation: fadeInSlide 0.5s ease-out;
    }

    .finding-card {
        background: rgba(18, 26, 48, 0.65);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        line-height: 1.6;
        transition: all 0.2s ease;
    }
    .finding-card:hover {
        background: rgba(23, 34, 61, 0.8);
        border-color: rgba(79, 140, 255, 0.4);
        transform: translateX(3px);
    }
    .finding-indicator {
        color: var(--color-cyan);
        display: inline-flex;
        margin-top: 0.2rem;
    }
    .finding-body {
        flex: 1;
        color: #E2E8F0;
        font-size: 0.98rem;
    }
    .citation-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(45, 212, 191, 0.12);
        color: var(--color-teal);
        border: 1px solid rgba(45, 212, 191, 0.35);
        padding: 0.12rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-left: 0.45rem;
    }

    .source-panel {
        background: #0E1529;
        border: 1px solid rgba(45, 212, 191, 0.22);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .source-panel:hover {
        border-color: var(--color-teal);
        background: #121C35;
        box-shadow: 0 10px 30px -5px rgba(45, 212, 191, 0.22);
        transform: translateY(-3px);
    }
    .source-top-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .source-badge-teal {
        background: rgba(45, 212, 191, 0.15);
        color: var(--color-teal);
        border: 1px solid rgba(45, 212, 191, 0.45);
        font-weight: 800;
        font-size: 0.75rem;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
    }
    .source-domain-tag {
        color: var(--text-muted);
        font-size: 0.8rem;
        font-weight: 600;
    }
    .source-link-title {
        font-size: 0.98rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    .source-link-title a {
        color: #93C5FD !important;
        text-decoration: none !important;
    }
    .source-link-title a:hover {
        color: var(--color-cyan) !important;
    }
    .source-snippet-text {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .confidence-banner {
        border-radius: 12px;
        padding: 1.1rem 1.5rem;
        margin-bottom: 1.6rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        animation: fadeInSlide 0.5s ease-out;
    }
    .confidence-banner.high {
        background: rgba(45, 212, 191, 0.1);
        border: 1px solid rgba(45, 212, 191, 0.4);
    }
    .confidence-banner.medium {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .confidence-banner.low {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .confidence-indicator-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
        animation: pulseGlow 2s infinite ease-in-out;
    }
    .dot-high { background-color: var(--color-teal); box-shadow: 0 0 12px var(--color-teal); }
    .dot-medium { background-color: var(--color-warning); box-shadow: 0 0 12px var(--color-warning); }
    .dot-low { background-color: var(--color-error); box-shadow: 0 0 12px var(--color-error); }

    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 1rem;
        margin-top: 0.5rem;
    }
    .telemetry-cell {
        background: rgba(18, 26, 48, 0.8);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }
    .telemetry-cell:hover {
        border-color: rgba(79, 140, 255, 0.4);
        background: rgba(23, 34, 61, 0.9);
    }
    .telemetry-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .telemetry-data {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        word-break: break-all;
    }

    .progress-bar-container {
        width: 100%;
        height: 6px;
        background: rgba(18, 26, 48, 0.8);
        border-radius: 9999px;
        overflow: hidden;
        margin: 1rem 0;
        border: 1px solid var(--border-subtle);
    }
    .progress-bar-fill {
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, var(--color-cyan), var(--color-blue), var(--color-violet), var(--color-teal));
        background-size: 200% 100%;
        animation: gradientFlow 2.5s linear infinite;
    }

    .verity-footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-subtle);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Cursor Glow
st.html("""
<script>
(function() {
    try {
        const pDoc = window.parent.document;
        if (!pDoc.getElementById('verity-cursor-glow')) {
            const glow = pDoc.createElement('div');
            glow.id = 'verity-cursor-glow';
            glow.style.position = 'fixed';
            glow.style.top = '0';
            glow.style.left = '0';
            glow.style.width = '600px';
            glow.style.height = '600px';
            glow.style.borderRadius = '50%';
            glow.style.pointerEvents = 'none';
            glow.style.transform = 'translate(-50%, -50%)';
            glow.style.background = 'radial-gradient(circle, rgba(79, 140, 255, 0.08) 0%, rgba(124, 92, 255, 0.04) 35%, rgba(34, 211, 238, 0.02) 65%, transparent 80%)';
            glow.style.zIndex = '0';
            glow.style.transition = 'opacity 0.4s ease, transform 0.08s ease-out';
            glow.style.opacity = '0';
            pDoc.body.appendChild(glow);

            pDoc.addEventListener('mousemove', function(e) {
                glow.style.opacity = '1';
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            });

            pDoc.addEventListener('mouseleave', function() {
                glow.style.opacity = '0';
            });
        }
    } catch (err) {}
})();
</script>
""")

# Resolve keys exclusively from environment variables or st.secrets
active_tavily_key = get_tavily_api_key()
active_nebius_key = get_nebius_api_key()
active_base_url = get_nebius_base_url()
configured_model_name = get_configured_nebius_model_name()

# Initialize Session State
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "research_results" not in st.session_state:
    st.session_state.research_results = None

# Sidebar: Engine Configuration
with st.sidebar:
    st.markdown(f"""
    <div class="section-header">
        {ICON_SETTINGS} Engine Configuration
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Verity AI reads credentials strictly from environment variables (.env) or Streamlit secrets.")
    
    # Credential Status Displays
    tavily_status_html = f'<span class="status-badge-ok">{ICON_CHECK} CONFIGURED</span>' if active_tavily_key else f'<span class="status-badge-missing">{ICON_ALERT} MISSING</span>'
    nebius_status_html = f'<span class="status-badge-ok">{ICON_CHECK} CONFIGURED</span>' if active_nebius_key else f'<span class="status-badge-missing">{ICON_ALERT} MISSING</span>'

    st.markdown(f"""
    <div class="key-status-row">
        <span style="font-size: 0.82rem; font-weight: 600; color: #CBD5E1;">TAVILY_API_KEY</span>
        {tavily_status_html}
    </div>
    <div class="key-status-row">
        <span style="font-size: 0.82rem; font-weight: 600; color: #CBD5E1;">NEBIUS_API_KEY</span>
        {nebius_status_html}
    </div>
    """, unsafe_allow_html=True)

    # Active Base URL
    st.markdown(f"""
    <div style="background: rgba(18, 26, 48, 0.4); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 0.6rem 0.8rem; margin: 0.6rem 0 1rem 0;">
        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Active Endpoint (NEBIUS_BASE_URL)</div>
        <div style="font-size: 0.82rem; color: #93C5FD; word-break: break-all; margin-top: 0.2rem;">{active_base_url}</div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic Model Discovery / Configuration
    st.markdown("---")
    st.markdown(f"""
    <div class="section-header">
        {ICON_CPU} Model Configuration
    </div>
    """, unsafe_allow_html=True)

    if configured_model_name:
        st.markdown(f"""
        <div style="background: rgba(18, 26, 48, 0.6); border: 1px solid rgba(79, 140, 255, 0.25); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.8rem;">
            <div style="font-size: 0.7rem; color: var(--color-cyan); text-transform: uppercase; font-weight: 700;">Pinned Model (from NEBIUS_MODEL)</div>
            <div style="font-size: 0.88rem; font-weight: 600; color: #F8FAFC; margin-top: 0.2rem;">{configured_model_name}</div>
        </div>
        """, unsafe_allow_html=True)
        chosen_model = configured_model_name
    else:
        # If NEBIUS_MODEL is empty, query live /models from Nebius when key is available
        model_options = ["Auto-select best open model"]
        if active_nebius_key:
            try:
                with st.spinner("Connecting to Nebius /models catalog..."):
                    discovered_models = fetch_available_nebius_models(
                        api_key=active_nebius_key,
                        base_url=active_base_url
                    )
                    if discovered_models:
                        model_options = ["Auto-select best open model"] + discovered_models
            except Exception as e:
                st.caption(f"Catalog notice: {str(e)[:55]}... Model will auto-resolve on execute.")
        else:
            st.caption("NEBIUS_MODEL is empty. Model list will load once NEBIUS_API_KEY is configured.")

        chosen_model = st.selectbox(
            "Inference Model",
            options=model_options,
            index=0,
            help="Models queried dynamically from official Nebius /models catalog"
        )

    max_sources_slider = st.slider(
        "Max Grounding Sources",
        min_value=3,
        max_value=8,
        value=5,
        step=1,
        help="Number of real-time web sources to retrieve via Tavily"
    )

    st.markdown("---")
    st.markdown(f"""
    <div class="section-header">
        {ICON_CHECK} Verification Protocols
    </div>
    """, unsafe_allow_html=True)
    st.caption("• 100% Sourced: Claims without citations are rejected.")
    st.caption("• Zero Hallucination: No phantom quotes or URLs.")
    st.caption("• Conflict Detection: Contradictory evidence flagged.")
    st.caption("• Knowledge Gaps: Unverified dimensions declared.")

    st.markdown("---")
    st.caption("ODSC x Nebius AI Hackathon 2026")

# Landing / Header Section
st.markdown(f"""
<div class="brand-hero">
    <div class="brand-pill">
        {ICON_SHIELD} ODSC x Nebius Hackathon 2026 • Verified Intelligence
    </div>
    <div class="brand-title">
        <span class="brand-title-verity">Verity</span>
        <span class="brand-title-ai">AI</span>
    </div>
    <div class="brand-tagline">From Question to Verified Knowledge</div>
    <p class="brand-description">
        Autonomous research agent synthesizing verifiable, citation-audited knowledge briefs
        using real-time web grounding and Nebius Token Factory open-weights models.
    </p>
</div>
""", unsafe_allow_html=True)

# Missing Key Alert Card (Shown prominent on main dashboard if any required key is missing)
keys_missing = []
if not active_tavily_key:
    keys_missing.append("TAVILY_API_KEY")
if not active_nebius_key:
    keys_missing.append("NEBIUS_API_KEY")

if keys_missing:
    missing_items_html = " ".join([f"<strong style='color: var(--color-warning);'>{k}</strong>" for k in keys_missing])
    st.markdown(f"""
    <div class="setup-required-card">
        <div style="display: flex; align-items: center; gap: 0.6rem; color: var(--color-warning); font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;">
            {ICON_ALERT} API Configuration Required: {missing_items_html}
        </div>
        <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.8rem;">
            Verity AI strictly requires genuine API credentials to execute real-time web grounding and open-model inference. 
            <strong>No fake or ungrounded responses are ever produced.</strong>
        </div>
        <div style="background: rgba(11, 16, 32, 0.7); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 0.8rem 1rem; font-size: 0.85rem; color: #E2E8F0; line-height: 1.6;">
            <strong>How to configure locally:</strong><br>
            1. Open the <code>.env</code> file in your project directory (created automatically from <code>.env.example</code>).<br>
            2. Add your keys: <code>TAVILY_API_KEY=tvly-...</code> and <code>NEBIUS_API_KEY=...</code><br>
            3. Restart Streamlit or refresh this page.<br><br>
            <strong>How to configure on Streamlit Community Cloud:</strong><br>
            Add <code>TAVILY_API_KEY</code> and <code>NEBIUS_API_KEY</code> in <em>App Settings &gt; Secrets</em>.<br><br>
            <strong>Obtain credentials:</strong><br>
            • Tavily Search: <a href="https://tavily.com" target="_blank" style="color: var(--color-cyan); text-decoration: none;">tavily.com</a><br>
            • Nebius Token Factory: <a href="https://tokenfactory.nebius.com" target="_blank" style="color: var(--color-cyan); text-decoration: none;">tokenfactory.nebius.com</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Example Inquiries Section
st.markdown(f"""
<div class="section-header">
    {ICON_SEARCH} Explore Verified Inquiries
</div>
""", unsafe_allow_html=True)

example_queries = [
    {"tag": "Aerospace", "text": "What is the scheduled launch window and crew for NASA's Artemis II mission?"},
    {"tag": "Fusion Physics", "text": "What are the recent milestone breakthroughs in magnetic confinement fusion?"},
    {"tag": "LLM Architecture", "text": "How does DeepSeek-V3 Multi-Head Latent Attention (MLA) reduce memory bandwidth?"},
    {"tag": "Energy Storage", "text": "What are the commercialization timelines for solid-state battery vehicles?"}
]

col_ex1, col_ex2 = st.columns(2)
for i, item in enumerate(example_queries):
    target_col = col_ex1 if i % 2 == 0 else col_ex2
    with target_col:
        button_label = f"[{item['tag'].upper()}]  {item['text']}"
        if st.button(button_label, key=f"ex_btn_{i}", use_container_width=True):
            st.session_state.query_input = item["text"]

st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

# Main Research Input Area
query_text = st.text_input(
    "Research Inquiry:",
    value=st.session_state.query_input,
    placeholder="Enter an inquiry, e.g., Confirmed technical specifications and payload capacity of Starship Flight 6",
    help="Be specific to generate rigorous, cited findings."
)

col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    research_pressed = st.button("Run Verified Research", type="primary", use_container_width=True)
with col_act2:
    if st.session_state.research_results is not None:
        if st.button("Clear Results", use_container_width=False):
            st.session_state.research_results = None
            st.session_state.query_input = ""
            st.rerun()

# Execution Logic
if research_pressed:
    # 1. Empty input validation
    if not query_text or not query_text.strip():
        st.warning("Please enter a research inquiry before running verification.")
    # 2. Strict Key Validation (Clear setup message, NEVER fake output)
    elif not active_tavily_key:
        st.error("Execution Blocked: TAVILY_API_KEY is missing from environment / secrets.")
        st.info("""
        Setup Instructions for Tavily:
        1. Obtain a free API key at https://tavily.com.
        2. Set TAVILY_API_KEY in your local .env file or Streamlit Cloud Secrets.
        3. Refresh the page to execute verified research.
        """)
    elif not active_nebius_key:
        st.error("Execution Blocked: NEBIUS_API_KEY is missing from environment / secrets.")
        st.info("""
        Setup Instructions for Nebius Token Factory:
        1. Obtain an API key from https://tokenfactory.nebius.com under API Keys.
        2. Set NEBIUS_API_KEY in your local .env file or Streamlit Cloud Secrets.
        3. Refresh the page to execute verified research.
        """)
    else:
        # Step-by-step progress tracking with animated bar
        progress_placeholder = st.empty()
        
        def handle_progress(step_id: str, message: str):
            progress_placeholder.markdown(f"""
            <div class="verity-card" style="margin-top: 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: var(--color-cyan); text-transform: uppercase; letter-spacing: 0.06em;">
                        Active Phase: {step_id.replace('_', ' ').upper()}
                    </span>
                    <span style="font-size: 0.85rem; color: #94A3B8;">{message}</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        try:
            target_model = None if chosen_model == "Auto-select best open model" else chosen_model
            
            with st.spinner("Synthesizing verified research..."):
                result = run_verity_agent(
                    question=query_text.strip(),
                    tavily_api_key=active_tavily_key,
                    nebius_api_key=active_nebius_key,
                    selected_model=target_model,
                    max_sources=max_sources_slider,
                    base_url=active_base_url,
                    progress_callback=handle_progress
                )
                st.session_state.research_results = result
                progress_placeholder.empty()
                st.success("Research synthesis verified against primary web sources.")
        except Exception as e:
            progress_placeholder.empty()
            st.error(f"Verification Pipeline Error: {str(e)}")

# Display Results Section
res = st.session_state.research_results
if res:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Confidence Level & Audit Banner
    conf = res.get("confidence", "Medium")
    conf_reason = res.get("confidence_reason", "")
    
    if conf == "High":
        conf_class = "high"
        dot_class = "dot-high"
        conf_text_color = "var(--color-teal)"
    elif conf == "Medium":
        conf_class = "medium"
        dot_class = "dot-medium"
        conf_text_color = "var(--color-warning)"
    else:
        conf_class = "low"
        dot_class = "dot-low"
        conf_text_color = "var(--color-error)"

    st.markdown(f"""
    <div class="confidence-banner {conf_class}">
        <div>
            <div style="display: flex; align-items: center; font-weight: 800; font-size: 1.05rem; color: {conf_text_color}; letter-spacing: 0.02em;">
                <span class="confidence-indicator-dot {dot_class}"></span>
                {conf.upper()} SOURCE CONFIDENCE
            </div>
            <div style="color: #CBD5E1; font-size: 0.9rem; margin-top: 0.35rem;">
                {conf_reason}
            </div>
        </div>
        <div style="background: rgba(11, 16, 32, 0.7); border: 1px solid rgba(79, 140, 255, 0.2); padding: 0.4rem 0.9rem; border-radius: 8px; font-size: 0.8rem; color: #94A3B8;">
            Audit Status: <strong style="color: var(--color-teal);">100% Grounded Citations</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Verified Synthesis Card
    st.markdown(f"""
    <div class="section-header">
        {ICON_SHIELD} Verified Synthesis
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="synthesis-card">
        {res['answer']}
    </div>
    """, unsafe_allow_html=True)

    # Key Grounded Findings with Verified Citations
    st.markdown(f"""
    <div class="section-header">
        {ICON_CHECK} Grounded Key Findings
    </div>
    """, unsafe_allow_html=True)
    
    findings = res.get("key_findings", [])
    if findings:
        for finding in findings:
            claim_text = finding.get("claim", "")
            source_ids = finding.get("source_ids", [])
            
            pills = "".join([f'<span class="citation-badge">Source [{sid}]</span>' for sid in source_ids])
            st.markdown(f"""
            <div class="finding-card">
                <span class="finding-indicator">{ICON_CHECK}</span>
                <div class="finding-body">
                    {claim_text} {pills}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No discrete key findings could be isolated from retrieved sources.")

    # Primary Web Evidence (Verified Sources - Accented with Teal #2DD4BF)
    sources = res.get("sources", [])
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-header" style="color: var(--color-teal);">
        {ICON_DATABASE} Primary Web Evidence ({len(sources)} Verified Sources)
    </div>
    """, unsafe_allow_html=True)
    
    if sources:
        col_s1, col_s2 = st.columns(2)
        for idx, src in enumerate(sources):
            target_col = col_s1 if idx % 2 == 0 else col_s2
            with target_col:
                st.markdown(f"""
                <div class="source-panel">
                    <div>
                        <div class="source-top-meta">
                            <span class="source-badge-teal">SOURCE [{src['id']}]</span>
                            <span class="source-domain-tag">{src['domain']}</span>
                        </div>
                        <div class="source-link-title">
                            <a href="{src['url']}" target="_blank" rel="noopener noreferrer">
                                {src['title']}
                            </a>
                        </div>
                        <div class="source-snippet-text">
                            {src['content'][:240]}...
                        </div>
                    </div>
                    <div style="margin-top: 0.8rem; text-align: right;">
                        <a href="{src['url']}" target="_blank" rel="noopener noreferrer" style="color: var(--color-cyan); font-size: 0.78rem; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 0.3rem;">
                            View Source Document {ICON_EXTERNAL}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No external web sources were retrieved.")

    # Evidence Deep-Dive Expanders
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("Discrepancies & Conflicting Evidence", expanded=False):
            conflicts = res.get("conflicts", "None identified across retrieved sources.")
            st.markdown(f"**Cross-Source Conflict Analysis:**\n\n{conflicts}")
            
    with col_exp2:
        with st.expander("Knowledge Gaps & Unverified Nuances", expanded=False):
            gaps = res.get("gaps", "None identified.")
            st.markdown(f"**Identified Information Gaps:**\n\n{gaps}")

    with st.expander("Primary Source Transcripts & Excerpts", expanded=False):
        for src in sources:
            st.markdown(f"**[Source {src['id']}] {src['title']}**")
            st.caption(f"Domain: {src['domain']} • URL: {src['url']}")
            st.markdown(f"> {src['content']}")
            st.markdown("<hr style='border: 0; border-top: 1px solid rgba(79, 140, 255, 0.15); margin: 0.8rem 0;'>", unsafe_allow_html=True)

    # Telemetry Transparency Audit Panel
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-header">
        {ICON_CPU} Research Transparency Audit
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="verity-card">
        <div class="telemetry-grid">
            <div class="telemetry-cell">
                <div class="telemetry-label">{ICON_SEARCH} Executed Query</div>
                <div class="telemetry-data">{res['question']}</div>
            </div>
            <div class="telemetry-cell">
                <div class="telemetry-label">{ICON_CPU} Nebius Inference Engine</div>
                <div class="telemetry-data">{res['model_used']}</div>
            </div>
            <div class="telemetry-cell">
                <div class="telemetry-label">{ICON_DATABASE} Grounding Documents</div>
                <div class="telemetry-data">{len(sources)} Verified Pages</div>
            </div>
            <div class="telemetry-cell">
                <div class="telemetry-label">{ICON_CLOCK} Execution Latency</div>
                <div class="telemetry-data">{res['execution_time_sec']}s</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Polished Minimal Footer
st.markdown("""
<div class="verity-footer">
    <strong>Verity AI</strong> • From Question to Verified Knowledge<br>
    Built for the <strong>ODSC x Nebius AI Hackathon 2026</strong> • Powered by <strong>Nebius Token Factory</strong> and <strong>Tavily Search</strong>
</div>
""", unsafe_allow_html=True)
