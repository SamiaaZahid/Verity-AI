# 🛡️ Verity AI
### *From Question to Verified Knowledge*

[![Hackathon](https://img.shields.io/badge/ODSC%20%C3%97%20Nebius-Hackathon%202026-6366f1?style=for-the-badge)](https://odsc.com)
[![Engine](https://img.shields.io/badge/Nebius-Token%20Factory-0284c7?style=for-the-badge)](https://tokenfactory.nebius.com)
[![Search](https://img.shields.io/badge/Search-Tavily%20API-10b981?style=for-the-badge)](https://tavily.com)
[![Framework](https://img.shields.io/badge/Built%20With-Streamlit-ff4b4b?style=for-the-badge)](https://streamlit.io)

---

## 📖 Overview

**Verity AI** is an autonomous scientific and analytical research agent designed to combat the epidemic of LLM hallucinations. Rather than generating answers from static model weights, Verity AI retrieves real-time, authoritative ground truth via **Tavily Search**, submits the evidence to high-performance open-weight models hosted on **Nebius Token Factory**, and subjects the output to a strict citation and cross-verification pipeline.

Every claim is attributed to specific, real-world source IDs (`[1]`, `[2]`), contradictions across sources are flagged explicitly, and missing details are highlighted as knowledge gaps.

---

## 🎯 The Problem

Large Language Models (LLMs) suffer from critical vulnerabilities when used for analytical or scientific research:
1. **Hallucination & Fabrication:** Models confidently generate convincing citations, fake URLs, and non-existent data points.
2. **Knowledge Cutoffs:** Offline models cannot answer questions about ongoing developments, recent breakthroughs, or fluid events.
3. **Black-Box Reasoning:** Traditional AI answers do not provide traceable provenance, making verification laborious and error-prone.
4. **False Consensus:** Models frequently gloss over conflicting reports, presenting ambiguous data as settled facts.

---

## 💡 The Solution

Verity AI solves this with a **zero-hallucination, verification-first architecture**:
* **Live Retrieval:** Queries Tavily for primary web sources with deep snippet extraction.
* **Open-Model Inference via Nebius:** Dynamically connects to **Nebius Token Factory** to run leading open-weight LLMs (such as Llama 3.3 70B, DeepSeek-V3, Qwen 2.5 72B).
* **Deterministic Citation Auditing:** Validates that every citation in the answer strictly matches an existing retrieved source. Any ungrounded claim is purged or flagged.
* **Conflict & Gap Transparency:** Highlights contradictory claims and openly declares unanswerable sub-questions.

---

## 🏗️ System Architecture

```
[ User Inquiry ]
       │
       ▼
[ Query Validation ]
       │
       ▼
[ Tavily Real-Time Search API ] ──► (Fetches top verified web sources & snippets)
       │
       ▼
[ Evidence Numbering & Grounding Prompt ] ──► ([1], [2], [3] source indexing)
       │
       ▼
[ Nebius Token Factory ] ──► (Inference with open models: Llama 3.3, Qwen 2.5, DeepSeek)
       │
       ▼
[ Structured JSON Output ]
  ├── Verified Answer with inline citations
  ├── Key Findings mapped to source_ids
  ├── Confidence Score & Rationale
  ├── Detected Contradictions
  └── Information Gaps
       │
       ▼
[ Verification & Citation Audit ] ──► (Verifies all cited IDs exist; strips phantoms)
       │
       ▼
[ Premium Streamlit UI ] ──► (Interactive citation pills, source cards, transparency panel)
```

---

## ✨ Key Features

- **🛡️ Strict Grounding Guarantee:** The agent is constitutionally instructed to answer strictly based on provided source snippets.
- **🔗 Verified Citation Badges:** Every key finding is tagged with verified badge pills (e.g. `Source [1]`, `Source [2]`) linking directly to primary web sources.
- **⚡ Dynamic Nebius Model Discovery:** Queries the official Nebius `/models` endpoint dynamically to list and select real open models without hardcoded guesses.
- **⚖️ Contradiction & Gap Detection:** Identifies discrepancies across sources and discloses unanswered angles.
- **🔬 Full Research Transparency Panel:** Exposes the exact query, inference model, source count, latency, and citation validity.
- **🎨 Premium Dark Theme:** Custom-styled dark navy/charcoal UI with gradient accents, responsive cards, and step-by-step progress tracking.

---

## 🛠️ Tech Stack

- **Inference Provider:** [Nebius Token Factory](https://tokenfactory.nebius.com) (OpenAI-compatible open-weights API)
- **Web Grounding:** [Tavily Search API](https://tavily.com)
- **Frontend / Application Framework:** [Streamlit](https://streamlit.io)
- **Language / Runtime:** Python 3.10+
- **Version Control & CI/CD:** GitHub & Streamlit Community Cloud

---

## 📁 Repository Structure

```
verity-ai/
├── app.py              # Main Streamlit web application & UI components
├── agent.py            # Research orchestration & citation audit logic
├── search.py           # Tavily search wrapper & source extraction
├── llm.py              # Nebius Token Factory client & dynamic model discovery
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules
├── SUBMISSION.md       # ODSC × Nebius Hackathon pitch & demo script
└── README.md           # Comprehensive project documentation
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/verity-ai.git
cd verity-ai
```

### 3. Create a Virtual Environment
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and insert your API credentials:
```env
NEBIUS_API_KEY=your_actual_nebius_api_key
TAVILY_API_KEY=tvly-your_actual_tavily_api_key
```

> **Where to get keys:**
> - **Nebius Token Factory Key:** Sign up at [tokenfactory.nebius.com](https://tokenfactory.nebius.com) and generate a key in the dashboard.
> - **Tavily Key:** Sign up for a free plan at [tavily.com](https://tavily.com).

*Note: You can also enter API keys directly into the Streamlit sidebar at runtime.*

### 6. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Verity AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/verity-ai.git
   git push -u origin main
   ```
2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
   - Click **"New app"**.
   - Select your repository (`verity-ai`), branch (`main`), and main file path (`app.py`).
   - Click **"Advanced settings"** and add your secrets:
     ```toml
     NEBIUS_API_KEY = "your_nebius_key"
     TAVILY_API_KEY = "tvly-your_tavily_key"
     ```
   - Click **"Deploy!"**.

---

## 🧪 Testing Checklist

- [x] **Empty Input Validation:** Displays a warning if research query is submitted empty.
- [x] **Missing Keys Guard:** Informs user with clear steps if API keys are absent; prevents unauthenticated crashes.
- [x] **Zero Hallucination Audit:** Strips or flags any citation ID not present in retrieved sources.
- [x] **Model Discovery:** Dynamically loads open models directly from Nebius `/models` endpoint.
- [x] **One-Click Examples:** Clicking pre-built queries populates the input instantly.
- [x] **Responsive Layout:** Source cards and metrics render cleanly across desktop and mobile screens.

---

## 🔮 Limitations & Future Work

- **Multi-Hop Search:** Expand single-turn search into iterative multi-hop reasoning (e.g. generating sub-queries for complex multi-part questions).
- **PDF & Academic Paper Grounding:** Integrate arXiv and PubMed API extractors alongside Tavily web search.
- **Export Reports:** Add one-click export to PDF and Markdown research briefs.

---

## 📜 License & Acknowledgments

Built with pride for the **ODSC × Nebius AI Hackathon 2026**.
Powered by open models on **Nebius Token Factory** and search intelligence from **Tavily**.
