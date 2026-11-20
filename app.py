import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from search import get_tavily_api_key
from llm import (
    get_nebius_api_key,
    fetch_available_nebius_models,
    DEFAULT_NEBIUS_BASE_URL,
    FALLBACK_NEBIUS_BASE_URL
)
from agent import run_verity_agent

# Configure Streamlit page
st.set_page_config(
    page_title="Verity AI • Sourced, Verifiable Knowledge",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Navy / Charcoal Theme + Gradients + Sleek Cards)
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #172554 0%, #0b0f19 55%, #050811 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Hero Branding */
    .brand-hero {
        padding: 1.5rem 0 1rem 0;
        text-align: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2rem;
    }
    .brand-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
    }
    .brand-tagline {
        font-size: 1.25rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 0.5rem;
    }
    .brand-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.25rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Card Containers */
    .verity-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    /* Answer Box */
    .answer-card {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        line-height: 1.7;
        font-size: 1.05rem;
    }

    /* Finding Bullet with Citations */
    .finding-item {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        line-height: 1.5;
    }
    .finding-bullet {
        color: #38bdf8;
        font-weight: bold;
        font-size: 1.1rem;
        line-height: 1.3;
    }
    .finding-content {
        flex: 1;
        color: #e2e8f0;
    }
    .cite-pill {
        display: inline-block;
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(14, 165, 233, 0.4);
        padding: 0.1rem 0.45rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-left: 0.4rem;
        vertical-align: baseline;
    }

    /* Source Cards */
    .source-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .source-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .source-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }
    .source-badge {
        background: #0284c7;
        color: white;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
    }
    .source-domain {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .source-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .source-title a {
        color: #60a5fa !important;
        text-decoration: none;
    }
    .source-title a:hover {
        text-decoration: underline;
    }
    .source-snippet {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    /* Transparency Panel */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 0.5rem;
    }
    .metric-box {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
        word-break: break-all;
    }

    /* Footer */
    .verity-footer {
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to check secrets
def resolve_secret(key_name: str) -> str:
    """Check st.secrets first, then environment variable."""
    try:
        if key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return os.environ.get(key_name, "").strip()

# Initialize Session State
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "research_results" not in st.session_state:
    st.session_state.research_results = None
if "selected_example" not in st.session_state:
    st.session_state.selected_example = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    st.markdown("Verity AI orchestrates **Nebius Token Factory** open models with **Tavily** real-time grounding.")
    
    # API Keys Resolution
    env_tavily = resolve_secret("TAVILY_API_KEY")
    env_nebius = resolve_secret("NEBIUS_API_KEY")
    
    tavily_key_input = st.text_input(
        "Tavily API Key",
        value=env_tavily,
        type="password",
        help="Get your key at https://tavily.com"
    )
    
    nebius_key_input = st.text_input(
        "Nebius Token Factory API Key",
        value=env_nebius,
        type="password",
        help="Get your key at https://tokenfactory.nebius.com"
    )

    base_url_choice = st.selectbox(
        "Nebius Base URL",
        options=[DEFAULT_NEBIUS_BASE_URL, FALLBACK_NEBIUS_BASE_URL],
        index=0,
        help="Official OpenAI-compatible endpoint for Nebius Token Factory"
    )

    # Dynamic Model Discovery via official Nebius /models endpoint
    st.markdown("---")
    st.markdown("#### 🧠 Model Selection")
    
    model_options = ["Auto-select best open model"]
    if nebius_key_input:
        try:
            with st.spinner("Querying Nebius /models catalog..."):
                discovered_models = fetch_available_nebius_models(
                    api_key=nebius_key_input,
                    base_url=base_url_choice
                )
                if discovered_models:
                    model_options = ["Auto-select best open model"] + discovered_models
        except Exception as e:
            st.caption(f"⚠️ Notice: Could not list models ({str(e)[:60]}...). Will auto-resolve during run.")
    
    chosen_model = st.selectbox(
        "Nebius Open Model",
        options=model_options,
        index=0,
        help="Open models hosted on Nebius Token Factory"
    )
    
    max_sources_slider = st.slider(
        "Max Search Sources",
        min_value=3,
        max_value=8,
        value=5,
        step=1,
        help="Number of real-time web sources to retrieve via Tavily"
    )

    st.markdown("---")
    st.markdown("#### 🛡️ Verification Rules")
    st.caption("• **100% Sourced:** Claims without citations are rejected.")
    st.caption("• **Zero Hallucination:** No phantom quotes or URLs.")
    st.caption("• **Conflict Detection:** Identifies contradictory evidence.")
    st.caption("• **Gaps Transparency:** Highlights unverified areas.")

    st.markdown("---")
    st.caption("🏆 **ODSC × Nebius AI Hackathon 2026**")

# Landing Section
st.markdown("""
<div class="brand-hero">
    <div class="brand-badge">ODSC × Nebius Hackathon 2026</div>
    <div class="brand-title">🛡️ Verity AI</div>
    <div class="brand-tagline">From Question to Verified Knowledge</div>
    <p style="color: #64748b; font-size: 0.95rem; max-width: 650px; margin: 0.5rem auto 0 auto;">
        An autonomous research agent turning complex inquiries into verifiable, citation-backed answers using 
        real-time web search and verified open-weights models.
    </p>
</div>
""", unsafe_allow_html=True)

# Example Questions Section
st.markdown("##### 💡 Try an Example Research Query:")
example_queries = [
    "What is the scheduled launch window and crew for NASA's Artemis II mission?",
    "What are the recent milestone breakthroughs in magnetic confinement fusion?",
    "How does DeepSeek-V3 Multi-Head Latent Attention (MLA) reduce memory bandwidth?",
    "What are the commercialization timelines for solid-state battery vehicles?"
]

col_ex1, col_ex2 = st.columns(2)
for i, ex in enumerate(example_queries):
    target_col = col_ex1 if i % 2 == 0 else col_ex2
    with target_col:
        if st.button(f"🔍 {ex}", key=f"ex_btn_{i}", use_container_width=True):
            st.session_state.query_input = ex

# Input Section
query_text = st.text_input(
    "Enter your research question:",
    value=st.session_state.query_input,
    placeholder="e.g., What are the confirmed specifications and payload capacity of Starship Flight 6?",
    help="Be specific to get high-quality verifiable findings."
)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    research_pressed = st.button("🚀 Verify & Research", type="primary", use_container_width=True)
with col_btn2:
    if st.session_state.research_results is not None:
        if st.button("🧹 Clear Results", use_container_width=False):
            st.session_state.research_results = None
            st.session_state.query_input = ""
            st.rerun()

# Execution Logic
if research_pressed:
    # 1. Empty input validation
    if not query_text or not query_text.strip():
        st.warning("⚠️ Please enter a research question before clicking Research.")
    # 2. API Key validation
    elif not tavily_key_input:
        st.error("🔑 **Tavily API Key is missing!**")
        st.info("""
        **Quick 1-Minute Steps to get Tavily API Key:**
        1. Visit [tavily.com](https://tavily.com) and create a free account.
        2. Copy your API Key from the dashboard.
        3. Paste it in the sidebar on the left, or set `TAVILY_API_KEY` in your `.env` file.
        """)
    elif not nebius_key_input:
        st.error("🔑 **Nebius Token Factory API Key is missing!**")
        st.info("""
        **Quick 1-Minute Steps to get Nebius API Key:**
        1. Log in to [tokenfactory.nebius.com](https://tokenfactory.nebius.com).
        2. Navigate to API Keys and generate a new key.
        3. Paste it in the sidebar on the left, or set `NEBIUS_API_KEY` in your `.env` file.
        """)
    else:
        # Step-by-step progress tracking
        progress_placeholder = st.empty()
        
        def handle_progress(step_id: str, message: str):
            icons = {
                "searching": "🌐",
                "model_resolving": "⚙️",
                "synthesizing": "🧠",
                "verifying": "🔍"
            }
            progress_placeholder.info(f"{icons.get(step_id, '⏳')} **Step: {message}**")

        try:
            target_model = None if chosen_model == "Auto-select best open model" else chosen_model
            
            with st.spinner("Verity AI is conducting verified research..."):
                result = run_verity_agent(
                    question=query_text.strip(),
                    tavily_api_key=tavily_key_input,
                    nebius_api_key=nebius_key_input,
                    selected_model=target_model,
                    max_sources=max_sources_slider,
                    base_url=base_url_choice,
                    progress_callback=handle_progress
                )
                st.session_state.research_results = result
                progress_placeholder.empty()
                st.success("✅ Research and citation verification complete!")
        except Exception as e:
            progress_placeholder.empty()
            st.error(f"❌ Research Failed: {str(e)}")

# Display Results Section
res = st.session_state.research_results
if res:
    st.markdown("---")
    
    # Confidence Banner
    conf = res.get("confidence", "Medium")
    conf_reason = res.get("confidence_reason", "")
    
    if conf == "High":
        conf_color = "#10b981"
        conf_bg = "rgba(16, 185, 129, 0.15)"
        conf_icon = "🟢"
    elif conf == "Medium":
        conf_color = "#f59e0b"
        conf_bg = "rgba(245, 158, 11, 0.15)"
        conf_icon = "🟡"
    else:
        conf_color = "#ef4444"
        conf_bg = "rgba(239, 68, 68, 0.15)"
        conf_icon = "🔴"

    st.markdown(f"""
    <div style="background: {conf_bg}; border: 1px solid {conf_color}; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.8rem;">
        <div>
            <span style="font-weight: 800; color: {conf_color}; font-size: 1.05rem;">{conf_icon} Source Confidence: {conf}</span>
            <div style="color: #cbd5e1; font-size: 0.9rem; margin-top: 0.2rem;">{conf_reason}</div>
        </div>
        <div style="background: rgba(0,0,0,0.3); padding: 0.35rem 0.8rem; border-radius: 6px; font-size: 0.8rem; color: #94a3b8;">
            Audit: <strong>100% Grounded Citations</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Verified Answer Card
    st.markdown("### 📝 Verified Synthesis")
    st.markdown(f"""
    <div class="answer-card">
        {res['answer']}
    </div>
    """, unsafe_allow_html=True)

    # Key Findings with Interactive Citations
    st.markdown("### 🔑 Key Grounded Findings")
    findings = res.get("key_findings", [])
    if findings:
        for finding in findings:
            claim_text = finding.get("claim", "")
            source_ids = finding.get("source_ids", [])
            
            pills = "".join([f'<span class="cite-pill">Source [{sid}]</span>' for sid in source_ids])
            st.markdown(f"""
            <div class="finding-item">
                <span class="finding-bullet">•</span>
                <div class="finding-content">
                    {claim_text} {pills}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No discrete key findings could be isolated from the sources.")

    # Source Cards
    sources = res.get("sources", [])
    st.markdown(f"### 🌐 Verified Web Sources ({len(sources)})")
    
    if sources:
        col_s1, col_s2 = st.columns(2)
        for idx, src in enumerate(sources):
            target_col = col_s1 if idx % 2 == 0 else col_s2
            with target_col:
                st.markdown(f"""
                <div class="source-card">
                    <div class="source-header">
                        <span class="source-badge">[{src['id']}]</span>
                        <span class="source-domain">{src['domain']}</span>
                    </div>
                    <div class="source-title">
                        <a href="{src['url']}" target="_blank" rel="noopener noreferrer">
                            {src['title']} ↗
                        </a>
                    </div>
                    <div class="source-snippet">
                        {src['content'][:230]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No external web sources available.")

    # Deep-Dive Evidence & Transparency Expanders
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("⚖️ Contradictions & Conflicting Evidence", expanded=False):
            conflicts = res.get("conflicts", "None identified across retrieved sources.")
            st.markdown(f"**Identified Conflicts:**\n\n{conflicts}")
            
    with col_exp2:
        with st.expander("❓ Information Gaps & Unverified Nuances", expanded=False):
            gaps = res.get("gaps", "None identified.")
            st.markdown(f"**Identified Gaps:**\n\n{gaps}")

    with st.expander("🔍 Complete Source Text & Excerpts", expanded=False):
        for src in sources:
            st.markdown(f"#### [{src['id']}] {src['title']}")
            st.caption(f"Source URL: {src['url']}")
            st.markdown(f"> {src['content']}")
            st.markdown("---")

    # Research Transparency Panel
    st.markdown("### 🔬 Research Transparency Audit")
    st.markdown(f"""
    <div class="verity-card">
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-label">Research Query</div>
                <div class="metric-value">{res['question']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Nebius Inference Model</div>
                <div class="metric-value">{res['model_used']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Sources Retrieved</div>
                <div class="metric-value">{len(sources)} Verified Pages</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Total Execution Time</div>
                <div class="metric-value">{res['execution_time_sec']}s</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="verity-footer">
    <strong>Verity AI</strong> • From Question to Verified Knowledge<br>
    Built for the <strong>ODSC × Nebius AI Hackathon 2026</strong> • Powered by <strong>Nebius Token Factory</strong> and <strong>Tavily Search</strong>
</div>
""", unsafe_allow_html=True)
