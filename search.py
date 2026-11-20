import os
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from tavily import TavilyClient

def get_tavily_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Tavily API key from argument, environment, or Streamlit secrets."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    return os.environ.get("TAVILY_API_KEY", "").strip() or None

def extract_domain(url: str) -> str:
    """Extract clean domain name from URL."""
    try:
        netloc = urlparse(url).netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "web"
    except Exception:
        return "web"

def search_tavily(
    query: str,
    api_key: Optional[str] = None,
    max_results: int = 5,
    search_depth: str = "basic"
) -> List[Dict[str, Any]]:
    """
    Execute real-time Tavily search.
    
    Args:
        query: The search query string.
        api_key: Tavily API key (optional if set in env).
        max_results: Maximum number of sources (default: 5).
        search_depth: "basic" or "advanced" (default: "basic").
        
    Returns:
        List of dicts: [
            {
                "id": 1,
                "title": str,
                "url": str,
                "content": str,
                "domain": str,
                "score": float
            },
            ...
        ]
        
    Raises:
        ValueError: If API key is missing or query is empty.
        RuntimeError: If Tavily API call fails.
    """
    resolved_key = get_tavily_api_key(api_key)
    if not resolved_key:
        raise ValueError(
            "Tavily API Key is missing. Please provide a key in the sidebar, "
            ".env file, or set the TAVILY_API_KEY environment variable."
        )

    clean_query = query.strip()
    if not clean_query:
        raise ValueError("Search query cannot be empty.")

    try:
        client = TavilyClient(api_key=resolved_key)
        response = client.search(
            query=clean_query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=False,
            include_raw_content=False
        )
    except Exception as e:
        error_msg = str(e)
        if "unauthorized" in error_msg.lower() or "invalid api key" in error_msg.lower():
            raise RuntimeError("Invalid Tavily API Key. Please verify your credentials.") from e
        raise RuntimeError(f"Tavily search request failed: {error_msg}") from e

    raw_results = response.get("results", [])
    if not raw_results:
        return []

    structured_sources: List[Dict[str, Any]] = []
    for idx, item in enumerate(raw_results, start=1):
        raw_content = item.get("content") or item.get("snippet") or ""
        # Clean content string
        content = " ".join(raw_content.split())
        
        structured_sources.append({
            "id": idx,
            "title": item.get("title", "Untitled Source").strip(),
            "url": item.get("url", "").strip(),
            "content": content,
            "domain": extract_domain(item.get("url", "")),
            "score": item.get("score", 0.0)
        })

    return structured_sources
