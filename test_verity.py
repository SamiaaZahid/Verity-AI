import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Import modules to test
from search import search_tavily, extract_domain, get_tavily_api_key
from llm import (
    extract_json_from_text,
    select_best_model,
    PREFERRED_MODELS
)
from agent import (
    format_sources_for_llm,
    validate_and_sanitize_result,
    run_verity_agent
)

class TestVeritySearch(unittest.TestCase):
    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://www.nasa.gov/mission/artemis/"), "nasa.gov")
        self.assertEqual(extract_domain("https://sub.domain.co.uk/test?q=1"), "sub.domain.co.uk")
        self.assertEqual(extract_domain("invalid-url"), "web")

    def test_missing_tavily_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                search_tavily("test query", api_key=None)
            self.assertIn("Tavily API Key is missing", str(ctx.exception))

    def test_empty_query(self):
        with self.assertRaises(ValueError) as ctx:
            search_tavily("   ", api_key="test-key")
        self.assertIn("query cannot be empty", str(ctx.exception))

    @patch("search.TavilyClient")
    def test_search_results_formatting(self, mock_tavily_class):
        mock_client = MagicMock()
        mock_tavily_class.return_value = mock_client
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Artemis II Launch Update",
                    "url": "https://www.nasa.gov/artemis-2",
                    "content": "NASA has targeted the launch for September 2025.",
                    "score": 0.98
                },
                {
                    "title": "Spaceflight Now Artemis News",
                    "url": "https://spaceflightnow.com/artemis",
                    "content": "The four astronauts continue training.",
                    "score": 0.89
                }
            ]
        }

        results = search_tavily("Artemis II status", api_key="dummy-key", max_results=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["domain"], "nasa.gov")
        self.assertEqual(results[1]["id"], 2)
        self.assertEqual(results[1]["domain"], "spaceflightnow.com")
        self.assertIn("September 2025", results[0]["content"])

class TestVerityLLM(unittest.TestCase):
    def test_extract_json_plain(self):
        raw = '{"answer": "Clean summary", "confidence": "High"}'
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["answer"], "Clean summary")
        self.assertEqual(parsed["confidence"], "High")

    def test_extract_json_with_markdown_fences(self):
        raw = '''```json
        {
            "answer": "Markdown wrapped summary",
            "confidence": "Medium"
        }
        ```'''
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["answer"], "Markdown wrapped summary")
        self.assertEqual(parsed["confidence"], "Medium")

    def test_extract_json_with_surrounding_text(self):
        raw = 'Here is the JSON report:\n{"answer": "Surrounded JSON"}\nHope this helps!'
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["answer"], "Surrounded JSON")

    def test_select_best_model_preferred(self):
        available = [
            "some-random-model",
            "meta-llama/Llama-3.3-70B-Instruct",
            "other-model"
        ]
        chosen = select_best_model(available)
        self.assertEqual(chosen, "meta-llama/Llama-3.3-70B-Instruct")

    def test_select_best_model_fallback(self):
        available = ["custom/open-model-v1", "custom/open-model-v2"]
        chosen = select_best_model(available)
        self.assertEqual(chosen, "custom/open-model-v1")

class TestVerityAgentGrounding(unittest.TestCase):
    def setUp(self):
        self.sample_sources = [
            {
                "id": 1,
                "title": "Source 1",
                "domain": "site1.com",
                "url": "https://site1.com/a",
                "content": "Fact A is verified."
            },
            {
                "id": 2,
                "title": "Source 2",
                "domain": "site2.com",
                "url": "https://site2.com/b",
                "content": "Fact B is verified."
            }
        ]

    def test_format_sources(self):
        formatted = format_sources_for_llm(self.sample_sources)
        self.assertIn("--- SOURCE [1] ---", formatted)
        self.assertIn("--- SOURCE [2] ---", formatted)
        self.assertIn("Fact A is verified.", formatted)

    def test_citation_validator_purges_phantom_ids(self):
        """CRITICAL: Test that citations with IDs not present in retrieved sources are purged."""
        raw_llm_output = {
            "answer": "Synthesized text",
            "confidence": "High",
            "confidence_reason": "Clear corroboration",
            "conflicts": "None identified across retrieved sources.",
            "gaps": "None identified.",
            "key_findings": [
                {
                    "claim": "Claim with valid source 1",
                    "source_ids": [1]
                },
                {
                    "claim": "Claim with valid sources 1 and 2",
                    "source_ids": [1, 2]
                },
                {
                    "claim": "Claim with hallucinated phantom source ID 99",
                    "source_ids": [1, 99, 42]
                },
                {
                    "claim": "Claim with completely fake source ID 88",
                    "source_ids": [88]
                }
            ]
        }

        sanitized = validate_and_sanitize_result(raw_llm_output, self.sample_sources)
        findings = sanitized["key_findings"]
        
        # Finding 0: [1]
        self.assertEqual(findings[0]["source_ids"], [1])
        # Finding 1: [1, 2]
        self.assertEqual(findings[1]["source_ids"], [1, 2])
        # Finding 2: 99 and 42 stripped, only [1] preserved
        self.assertEqual(findings[2]["source_ids"], [1])
        # Finding 3: 88 stripped, empty list []
        self.assertEqual(findings[3]["source_ids"], [])

    def test_agent_empty_query_validation(self):
        with self.assertRaises(ValueError) as ctx:
            run_verity_agent("   ")
        self.assertIn("Please provide a question", str(ctx.exception))

    @patch("agent.search_tavily")
    def test_agent_no_results_graceful_handling(self, mock_search):
        mock_search.return_value = []
        result = run_verity_agent(
            question="Nonexistent topic xyz12345",
            tavily_api_key="dummy",
            nebius_api_key="dummy"
        )
        self.assertEqual(result["confidence"], "Low")
        self.assertEqual(result["sources"], [])
        self.assertIn("No relevant real-time web sources", result["answer"])

if __name__ == "__main__":
    unittest.main()
