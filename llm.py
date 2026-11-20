import json
import os
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI

DEFAULT_NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
FALLBACK_NEBIUS_BASE_URL = "https://api.studio.nebius.ai/v1/"

# Prioritized list of verified open reasoning and instruction models on Nebius
PREFERRED_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1",
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "mistralai/Mistral-Small-24B-Instruct-2501",
    "Qwen/Qwen2.5-32B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
]

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve secret from Streamlit secrets first, then environment variables."""
    try:
        import streamlit as st
        if key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        pass
    
    val = os.environ.get(key, "").strip()
    if val:
        return val
        
    return default

def get_nebius_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Nebius API key from argument, st.secrets, or environment variables."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    return get_secret("NEBIUS_API_KEY")

def get_nebius_base_url(provided_url: Optional[str] = None) -> str:
    """Retrieve Nebius base URL from argument, st.secrets, or environment variables."""
    if provided_url and provided_url.strip():
        return provided_url.strip()
    return get_secret("NEBIUS_BASE_URL", DEFAULT_NEBIUS_BASE_URL)

def get_configured_nebius_model_name() -> Optional[str]:
    """Retrieve statically configured NEBIUS_MODEL from st.secrets or environment variables."""
    return get_secret("NEBIUS_MODEL")

def get_nebius_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> OpenAI:
    """Create an OpenAI-compatible client configured for Nebius Token Factory."""
    resolved_key = get_nebius_api_key(api_key)
    if not resolved_key:
        raise ValueError(
            "NEBIUS_API_KEY is missing. Please configure it in your environment variables (.env) "
            "or Streamlit secrets (st.secrets)."
        )
    resolved_url = get_nebius_base_url(base_url)
    return OpenAI(
        base_url=resolved_url,
        api_key=resolved_key,
        timeout=60.0
    )

def fetch_available_nebius_models(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[str]:
    """
    Query the official Nebius /models endpoint to get live open models.
    Never guesses model IDs.
    """
    resolved_url = get_nebius_base_url(base_url)
    client = get_nebius_client(api_key=api_key, base_url=resolved_url)
    try:
        model_list = client.models.list()
        ids = [m.id for m in model_list.data if m.id]
        return sorted(ids)
    except Exception as e:
        # Fallback to secondary endpoint if default failed
        if resolved_url != FALLBACK_NEBIUS_BASE_URL:
            try:
                fallback_client = get_nebius_client(api_key=api_key, base_url=FALLBACK_NEBIUS_BASE_URL)
                model_list = fallback_client.models.list()
                ids = [m.id for m in model_list.data if m.id]
                return sorted(ids)
            except Exception:
                pass
        raise RuntimeError(f"Failed to query Nebius models list from {resolved_url}: {str(e)}") from e

def select_best_model(available_models: List[str]) -> str:
    """
    Select the highest quality open model from the real models returned by Nebius.
    Never invents or guesses a non-existent model ID.
    """
    if not available_models:
        raise ValueError("No open models returned by Nebius Token Factory endpoint.")
    
    # Check preferred models in priority order
    for preferred in PREFERRED_MODELS:
        if preferred in available_models:
            return preferred
            
    # Fuzzy match for preferred family
    for preferred in PREFERRED_MODELS:
        target_name = preferred.lower().split("/")[-1]
        for candidate in available_models:
            if target_name in candidate.lower():
                return candidate

    # Fallback to the first available model from the verified list
    return available_models[0]

def get_nebius_model(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    provided_model: Optional[str] = None
) -> str:
    """
    Determine the model to use:
    1. If provided_model is specified, use it.
    2. If NEBIUS_MODEL is set in env or st.secrets, use it.
    3. If NEBIUS_MODEL is empty or unset, query Nebius /models and pick an available open model.
    Never guesses model IDs.
    """
    if provided_model and provided_model.strip():
        return provided_model.strip()
    
    configured = get_configured_nebius_model_name()
    if configured:
        return configured

    # NEBIUS_MODEL is empty: fetch real models list and select an available open model
    available = fetch_available_nebius_models(api_key=api_key, base_url=base_url)
    return select_best_model(available)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Safely extract and parse JSON from model response text,
    handling markdown code blocks if present.
    """
    clean_text = text.strip()
    
    # Strip markdown code blocks if present
    markdown_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
    if markdown_match:
        clean_text = markdown_match.group(1).strip()
        
    # Find outer curly braces if extra text surrounds JSON
    brace_match = re.search(r"(\{[\s\S]*\})", clean_text)
    if brace_match:
        clean_text = brace_match.group(1).strip()

    return json.loads(clean_text)

def generate_grounded_answer(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 1
) -> Dict[str, Any]:
    """
    Generate grounded response from Nebius Token Factory.
    Enforces JSON schema and performs one retry on JSON parse failure.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    last_error: Optional[Exception] = None
    raw_response_text = ""

    for attempt in range(max_retries + 1):
        try:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048,
                    response_format={"type": "json_object"}
                )
            except Exception:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048
                )

            raw_response_text = completion.choices[0].message.content or ""
            parsed_json = extract_json_from_text(raw_response_text)
            return parsed_json

        except (json.JSONDecodeError, ValueError) as json_err:
            last_error = json_err
            if attempt < max_retries:
                messages.append({"role": "assistant", "content": raw_response_text})
                messages.append({
                    "role": "user",
                    "content": (
                        "CRITICAL ERROR: Your previous response was not valid JSON. "
                        "Return ONLY a strictly valid JSON object without markdown, prose, or extra text."
                    )
                })
                continue
            raise RuntimeError(
                f"Nebius model ({model}) returned non-JSON response after retry. Output was: {raw_response_text[:200]}"
            ) from json_err

        except Exception as api_err:
            error_str = str(api_err).lower()
            if "unauthorized" in error_str or "invalid api key" in error_str:
                raise RuntimeError("Invalid Nebius API key. Please verify your credentials at tokenfactory.nebius.com.") from api_err
            if "timeout" in error_str:
                raise RuntimeError("Nebius API request timed out. Please try again.") from api_err
            raise RuntimeError(f"Nebius inference failed: {str(api_err)}") from api_err

    raise RuntimeError(f"Failed to generate structured answer: {str(last_error)}")
