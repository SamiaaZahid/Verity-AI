# 🏆 ODSC × Nebius AI Hackathon 2026: Submission Kit

## Project Information
- **Project Name:** Verity AI
- **Tagline:** *From Question to Verified Knowledge*
- **Track:** Open Model Inference & Real-time Agents
- **Core Technologies:** Nebius Token Factory, Tavily Search API, Streamlit, Python

---

## 📌 Short Submission Description (For Devpost / Form)

> **Verity AI** is an autonomous research verification agent that solves the critical problem of AI hallucination by turning any complex inquiry into a verified, citation-backed knowledge synthesis. Powered by **Nebius Token Factory's** open-weight model infrastructure and **Tavily's** real-time search engine, Verity AI retrieves live ground-truth web sources, numbers and extracts primary evidence, and guides the LLM under strict grounding constraints. Every finding is audited against retrieved sources, ensuring 100% citation integrity with zero phantom quotes or invented URLs. With built-in contradiction detection, knowledge gap reporting, and a full research transparency audit, Verity AI delivers verifiable knowledge researchers and decision-makers can trust.

---

## ⏱️ 2-to-3 Minute Video Demo Script

### **[0:00 - 0:30] Hook & Problem Statement**
*(Screen: Title slide or Verity AI landing page with dark theme)*
> "Hello everyone! When people turn to AI for research, they face a dangerous problem: hallucinations, fabricated citations, outdated knowledge, and phantom URLs. If you can't verify an answer, you can't trust it.
> 
> My name is [Your Name], competing solo in the ODSC × Nebius AI Hackathon, and today I'm proud to present **Verity AI: From Question to Verified Knowledge**."

---

### **[0:30 - 1:00] Architecture & How It Works**
*(Screen: Zooming in on the UI, showing the Nebius model selector and Tavily search settings)*
> "Verity AI pairs the speed and intelligence of open-weight models on **Nebius Token Factory** with real-time web grounding from **Tavily Search**.
> 
> Here in the sidebar, Verity AI connects to the official Nebius models endpoint, discovering real active open models like Llama 3.3 70B, Qwen 2.5 72B, and DeepSeek.
> 
> When a user enters a question, Verity AI executes a 4-step pipeline:
> 1. It retrieves fresh, primary sources via Tavily.
> 2. It indexes and excerpts each source as evidence `[1]`, `[2]`, `[3]`.
> 3. It runs grounded inference with Nebius Token Factory under zero-hallucination rules.
> 4. And critically, our verification engine audits every citation to ensure no hallucinated sources ever reach the user."

---

### **[1:00 - 2:00] Live Demonstration**
*(Screen: Clicking an example query or typing: 'What is the scheduled launch window and crew for NASA's Artemis II mission?' and hitting 'Verify & Research')*
> "Let's test it with a fast-moving, real-world query: *'What is the scheduled launch window and crew for NASA's Artemis II mission?'*
> 
> Notice the progress tracker updating in real-time: querying Tavily, connecting to Nebius Token Factory, synthesizing evidence, and auditing citations.
> 
> And here are the results:
> - **Source Confidence:** We receive an instant confidence indicator — High — with an explanation based on source agreement.
> - **Verified Synthesis:** A comprehensive summary with inline citations.
> - **Key Grounded Findings:** Each bulleted claim is linked with an interactive source badge like `Source [1]`.
> - **Verified Web Sources:** Below, every single source card displays the publisher domain, page title, excerpt, and a direct clickable link to inspect the original webpage.
> - **Contradictions & Gaps:** Click here to see whether sources disagree, and what details remain unverified.
> - **Research Transparency Panel:** Full visibility into the inference model used, source count, and execution latency."

---

### **[2:00 - 2:30] Edge Case Handling & Robustness**
*(Screen: Demonstrating empty input validation or missing key guidance)*
> "We also engineered Verity AI for real-world resilience:
> - Submitting an empty question warns the user immediately.
> - If an API key is missing, friendly step-by-step setup guides appear instead of broken crashes or fake outputs.
> - And our post-inference validator prevents phantom citations by verifying every source ID against real retrieval results."

---

### **[2:30 - 3:00] Conclusion & Impact**
*(Screen: Return to Verity AI hero section)*
> "By combining **Nebius Token Factory's** open model compute with **Tavily's** real-time retrieval and our strict citation verification engine, Verity AI turns the web from a sea of noise into verifiable knowledge.
> 
> Thank you to the ODSC and Nebius teams for hosting this incredible hackathon. Verity AI is open-source and ready to deploy today!"

---

## 📝 Key Hackathon Submission Fields

| Field | Content |
|---|---|
| **Project Title** | Verity AI |
| **Tagline** | From Question to Verified Knowledge |
| **GitHub Repository** | `https://github.com/[YOUR_USERNAME]/verity-ai` |
| **Live App URL** | `https://[YOUR_APP_SUBDOMAIN].streamlit.app` |
| **Track** | Nebius Token Factory & Real-Time Open Agents |
| **Open Model Used** | `meta-llama/Llama-3.3-70B-Instruct` / `Qwen/Qwen2.5-72B-Instruct` |
| **Search Engine** | Tavily Search API |
