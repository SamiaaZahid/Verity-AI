import os
import sys
import httpx
from unittest.mock import patch
from dotenv import load_dotenv

# Load local environment
load_dotenv()

from agent import run_verity_agent
from search import get_tavily_api_key

def test_live_search_without_nebius():
    tavily_key = get_tavily_api_key()
    assert tavily_key, "TAVILY_API_KEY must be present in .env for this live test."

    print("Executing live Tavily search query with missing NEBIUS_API_KEY...")
    query = "What is the scheduled launch window and crew for NASA's Artemis II mission?"
    
    result = run_verity_agent(
        question=query,
        tavily_api_key=tavily_key,
        nebius_api_key=None, # Explicitly missing
        max_sources=4
    )

    # 1. Assertions on AI unavailable notice
    assert result["ai_unavailable"] is True, "Expected ai_unavailable to be True"
    assert result["answer"] == "AI answer unavailable until NEBIUS_API_KEY is added.", f"Unexpected answer: {result['answer']}"
    assert result["model_used"] == "None (NEBIUS_API_KEY missing)"
    assert result["execution_time_sec"] > 0, "Execution time should be recorded"

    # 2. Assertions on real retrieved web sources
    sources = result["sources"]
    assert len(sources) > 0, "Expected at least 1 real web source from Tavily"
    print(f"Retrieved {len(sources)} real web sources:")

    for idx, src in enumerate(sources, start=1):
        print(f"\n--- Source [{src['id']}] ---")
        print(f"Title:  {src['title']}")
        print(f"Domain: {src['domain']}")
        print(f"URL:    {src['url']}")
        print(f"Snippet length: {len(src['content'])} characters")

        assert src["title"], "Source title cannot be empty"
        assert src["url"].startswith("http"), f"Invalid URL format: {src['url']}"
        assert src["domain"], "Source domain cannot be empty"
        assert len(src["content"]) > 20, "Source snippet too short"

    # 3. HTTP URL Reachability Check on real sources using httpx
    print("\nVerifying that retrieved URLs point to real live pages...")
    verified_urls = 0
    client = httpx.Client(
        headers={"User-Agent": "VerityAI/1.0 (Hackathon Verification Engine)"},
        timeout=10.0,
        follow_redirects=True
    )
    
    with client:
        for src in sources:
            try:
                resp = client.get(src["url"])
                print(f"Verified live URL: {src['url']} (HTTP {resp.status_code})")
                if resp.status_code < 400:
                    verified_urls += 1
            except Exception as e:
                print(f"URL {src['url']} note: {e}")

    assert verified_urls > 0, "At least one URL must be confirmed live and reachable"
    print(f"\nSUCCESS: Live search and URL reachability confirmed! ({verified_urls} verified)")

def test_empty_input_validation():
    print("\nTesting empty input validation...")
    try:
        run_verity_agent("   ", tavily_api_key="mock", nebius_api_key=None)
        assert False, "Expected ValueError for empty input"
    except ValueError as e:
        assert "Please provide a question" in str(e)
        print("Empty input correctly rejected with ValueError:", e)

def test_missing_tavily_key_validation():
    print("\nTesting missing Tavily key validation...")
    with patch.dict(os.environ, {"TAVILY_API_KEY": ""}):
        try:
            run_verity_agent("Valid question", tavily_api_key=None, nebius_api_key=None)
            assert False, "Expected ValueError for missing Tavily key"
        except ValueError as e:
            assert "TAVILY_API_KEY is missing" in str(e)
            print("Missing Tavily key correctly blocked with ValueError:", e)

if __name__ == "__main__":
    test_empty_input_validation()
    test_missing_tavily_key_validation()
    test_live_search_without_nebius()
