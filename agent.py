import time
from typing import Dict, Any, List, Optional
from search import search_tavily
from llm import (
    get_nebius_client,
    fetch_available_nebius_models,
    select_best_model,
    generate_grounded_answer,
    DEFAULT_NEBIUS_BASE_URL
)

SYSTEM_PROMPT = """You are Verity AI, an objective, rigorous scientific research verification agent.
Your mission is to turn user questions into sourced, verifiable knowledge.

You will be given:
1. The user's question.
2. A numbered list of retrieved web sources ([1], [2], [3], etc.) containing real excerpts.

STRICT OPERATIONAL RULES:
1. ABSOLUTE GROUNDING: Make claims ONLY if they are explicitly corroborated by the provided numbered sources.
2. ZERO HALLUCINATION: Never invent facts, dates, sources, URLs, quotes, or statistics.
3. PRECISE CITATIONS: For each claim in "key_findings", provide the exact integer source IDs in "source_ids" that support that claim (e.g., [1], [1, 2]). Only reference source IDs that actually exist in the provided source list!
4. SOURCE CONFIDENCE:
   - "High": Multiple authoritative sources directly agree and confirm the primary points.
   - "Medium": Sources provide partial answers or limited corroboration.
   - "Low": Sources are scarce, indirect, or present substantial conflicting information.
5. CONFLICTS: Detail any discrepancies, conflicting data, or competing timelines between sources in "conflicts". If none, write "None identified across retrieved sources."
6. GAPS: Explicitly identify what aspects of the user's question remain unanswered or unverified by the sources in "gaps".

You MUST reply with ONLY a single valid JSON object matching this exact schema:
{
  "answer": "A coherent, comprehensive synthesized overview directly answering the question, with inline bracket citations like [1] or [1][2].",
  "key_findings": [
    {
      "claim": "Specific verified factual statement.",
      "source_ids": [1]
    }
  ],
  "confidence": "High" | "Medium" | "Low",
  "confidence_reason": "Detailed justification for the assigned confidence score based on source authority and agreement.",
  "conflicts": "Summary of any conflicting assertions among sources, or 'None identified across retrieved sources.'",
  "gaps": "Important nuances or sub-questions left unaddressed by the sources, or 'None identified.'"
}
"""

def format_sources_for_llm(sources: List[Dict[str, Any]]) -> str:
    """Format structured sources into numbered evidence blocks for the LLM."""
    if not sources:
        return "No web sources were retrieved."
    
    formatted_blocks = []
    for s in sources:
        sid = s["id"]
        title = s.get("title", "Untitled")
        domain = s.get("domain", "")
        url = s.get("url", "")
        content = s.get("content", "").strip()
        formatted_blocks.append(
            f"--- SOURCE [{sid}] ---\n"
            f"Title: {title}\n"
            f"Domain: {domain}\n"
            f"URL: {url}\n"
            f"Excerpt: {content}\n"
        )
    return "\n".join(formatted_blocks)

def validate_and_sanitize_result(
    result: Dict[str, Any],
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate JSON structure and verify that all cited source_ids exist in retrieved sources.
    Prevents phantom or hallucinated citations.
    """
    valid_ids = {s["id"] for s in sources}
    
    # Validate top-level keys with safe fallbacks
    answer = str(result.get("answer", "")).strip()
    if not answer:
        answer = "No comprehensive synthesis could be formed from the retrieved sources."

    confidence = str(result.get("confidence", "Medium")).strip().capitalize()
    if confidence not in ["High", "Medium", "Low"]:
        confidence = "Medium"

    confidence_reason = str(result.get("confidence_reason", "Assessed based on retrieved source coverage.")).strip()
    conflicts = str(result.get("conflicts", "None identified across retrieved sources.")).strip()
    gaps = str(result.get("gaps", "None identified.")).strip()

    raw_findings = result.get("key_findings", [])
    sanitized_findings = []

    if isinstance(raw_findings, list):
        for item in raw_findings:
            if not isinstance(item, dict):
                continue
            claim = str(item.get("claim", "")).strip()
            if not claim:
                continue
            
            raw_ids = item.get("source_ids", [])
            cleaned_ids = []
            if isinstance(raw_ids, list):
                for sid in raw_ids:
                    try:
                        int_id = int(sid)
                        # CRITICAL: Verify source ID actually exists
                        if int_id in valid_ids and int_id not in cleaned_ids:
                            cleaned_ids.append(int_id)
                    except (ValueError, TypeError):
                        continue
            
            cleaned_ids.sort()
            sanitized_findings.append({
                "claim": claim,
                "source_ids": cleaned_ids
            })

    return {
        "answer": answer,
        "key_findings": sanitized_findings,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "conflicts": conflicts,
        "gaps": gaps
    }

def run_verity_agent(
    question: str,
    tavily_api_key: Optional[str] = None,
    nebius_api_key: Optional[str] = None,
    selected_model: Optional[str] = None,
    max_sources: int = 5,
    base_url: str = DEFAULT_NEBIUS_BASE_URL,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Execute end-to-end Verity AI research pipeline:
    1. Validation of inputs
    2. Tavily real-time search
    3. Source numbering & structuring
    4. Nebius live model resolution
    5. Grounded synthesis via Nebius Token Factory
    6. Citation verification & JSON sanitization
    
    Returns complete report dictionary.
    """
    start_time = time.time()
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("Please provide a question to research.")

    # Step 1: Web Retrieval
    if progress_callback:
        progress_callback("searching", "Searching live web via Tavily...")
    
    sources = search_tavily(
        query=clean_question,
        api_key=tavily_api_key,
        max_results=max_sources,
        search_depth="basic"
    )

    if not sources:
        return {
            "question": clean_question,
            "answer": "No relevant real-time web sources were found for this query. Please refine the query.",
            "key_findings": [],
            "confidence": "Low",
            "confidence_reason": "No verifiable web sources were returned by Tavily search.",
            "conflicts": "None (No data)",
            "gaps": "Entire query could not be verified due to lack of search results.",
            "sources": [],
            "model_used": "N/A",
            "execution_time_sec": round(time.time() - start_time, 2),
            "citations_verified": True
        }

    # Step 2: Nebius Model Setup
    if progress_callback:
        progress_callback("model_resolving", "Connecting to Nebius Token Factory...")
    
    client = get_nebius_client(api_key=nebius_api_key, base_url=base_url)
    
    # Resolve model dynamically if not specified
    model_to_use = selected_model
    if not model_to_use:
        available_models = fetch_available_nebius_models(api_key=nebius_api_key, base_url=base_url)
        model_to_use = select_best_model(available_models)

    # Step 3: LLM Inference
    if progress_callback:
        progress_callback("synthesizing", f"Synthesizing verified knowledge with {model_to_use}...")

    formatted_evidence = format_sources_for_llm(sources)
    user_prompt = (
        f"USER QUESTION: {clean_question}\n\n"
        f"RETRIEVED WEB SOURCES:\n"
        f"{formatted_evidence}\n\n"
        f"Carefully evaluate the evidence and provide the JSON report adhering strictly to all grounding and citation rules."
    )

    raw_json_result = generate_grounded_answer(
        client=client,
        model=model_to_use,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_retries=1
    )

    # Step 4: Verification & Citation Audit
    if progress_callback:
        progress_callback("verifying", "Auditing citations and validating source claims...")

    sanitized = validate_and_sanitize_result(raw_json_result, sources)
    elapsed_time = round(time.time() - start_time, 2)

    return {
        "question": clean_question,
        "answer": sanitized["answer"],
        "key_findings": sanitized["key_findings"],
        "confidence": sanitized["confidence"],
        "confidence_reason": sanitized["confidence_reason"],
        "conflicts": sanitized["conflicts"],
        "gaps": sanitized["gaps"],
        "sources": sources,
        "model_used": model_to_use,
        "execution_time_sec": elapsed_time,
        "citations_verified": True
    }
