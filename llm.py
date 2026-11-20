import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI

DEFAULT_NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
FALLBACK_NEBIUS_BASE_URL = "https://api.studio.nebius.ai/v1/"

# Prioritized list of strong open reasoning and instruction models on Nebius
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

def get_nebius_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Nebius API key from argument or environment."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    return os.environ.get("NEBIUS_API_KEY", "").strip() or None

def get_nebius_client(
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_NEBIUS_BASE_URL
) -> OpenAI:
    """Create an OpenAI client configured for Nebius Token Factory."""
    resolved_key = get_nebius_api_key(api_key)
    if not resolved_key:
        raise ValueError(
            "Nebius API Key is missing. Please provide a key in the sidebar, "
            ".env file, or set the NEBIUS_API_KEY environment variable."
        )
    return OpenAI(
        base_url=base_url,
        api_key=resolved_key,
        timeout=60.0
    )

def fetch_available_nebius_models(
    api_key: Optional[str] = None,
    base_url: str = DEFAULT_NEBIUS_BASE_URL
) -> List[str]:
    """
    Query the official Nebius /models endpoint to get live open models.
    Never guesses model IDs.
    """
    client = get_nebius_client(api_key=api_key, base_url=base_url)
    try:
        model_list = client.models.list()
        ids = [m.id for m in model_list.data if m.id]
        return sorted(ids)
    except Exception as e:
        # If the default base URL had an issue, attempt fallback
        if base_url != FALLBACK_NEBIUS_BASE_URL:
            try:
                fallback_client = get_nebius_client(api_key=api_key, base_url=FALLBACK_NEBIUS_BASE_URL)
                model_list = fallback_client.models.list()
                ids = [m.id for m in model_list.data if m.id]
                return sorted(ids)
            except Exception:
                pass
        raise RuntimeError(f"Failed to query Nebius models list: {str(e)}") from e

def select_best_model(available_models: List[str]) -> str:
    """
    Select the highest quality open model from the real models returned by Nebius.
    """
    if not available_models:
        raise ValueError("No models available from Nebius Token Factory endpoint.")
    
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

    # Fallback to the first available model
    return available_models[0]

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
            # First attempt uses standard low-temp sampling
            # Request json_object format if supported
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048,
                    response_format={"type": "json_object"}
                )
            except Exception:
                # If response_format={"type": "json_object"} is unsupported by specific model
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
                # One retry with explicit error feedback
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
                raise RuntimeError("Invalid Nebius API key. Please check your token in the dashboard.") from api_err
            if "timeout" in error_str:
                raise RuntimeError("Nebius API request timed out. Please try again.") from api_err
            raise RuntimeError(f"Nebius inference failed: {str(api_err)}") from api_err

    raise RuntimeError(f"Failed to generate structured answer: {str(last_error)}")
