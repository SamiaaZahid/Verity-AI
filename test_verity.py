import sys
import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile

# Import modules to test
from search import search_tavily, extract_domain, get_tavily_api_key
from llm import (
    get_nebius_api_key,
    get_nebius_base_url,
    get_nebius_model,
    get_configured_nebius_model_name,
    get_nebius_client,
    extract_json_from_text,
    select_best_model,
    DEFAULT_NEBIUS_BASE_URL,
    PREFERRED_MODELS
)
from agent import (
    format_sources_for_llm,
    validate_and_sanitize_result,
    run_verity_agent
)

def helper_ensure_env_file(directory: str):
    env_path = os.path.join(directory, ".env")
    env_example_path = os.path.join(directory, ".env.example")
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        with open(env_example_path, "r", encoding="utf-8") as f_ex:
            content = f_ex.read()
        with open(env_path, "w", encoding="utf-8") as f_env:
            f_env.write(content)

class TestVerityEnvAndKeys(unittest.TestCase):
    def test_ensure_env_file_creates_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            example_file = os.path.join(tmpdir, ".env.example")
            with open(example_file, "w", encoding="utf-8") as f:
                f.write("NEBIUS_API_KEY=\nTAVILY_API_KEY=\n")
            
            env_file = os.path.join(tmpdir, ".env")
            self.assertFalse(os.path.exists(env_file))
            
            helper_ensure_env_file(tmpdir)
            self.assertTrue(os.path.exists(env_file))
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("NEBIUS_API_KEY=", content)
            self.assertIn("TAVILY_API_KEY=", content)

    def test_gitignore_excludes_env(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        gitignore_path = os.path.join(root_dir, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path))
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        self.assertIn(".env", lines)

class TestVeritySearch(unittest.TestCase):
    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://www.nasa.gov/mission/artemis/"), "nasa.gov")
        self.assertEqual(extract_domain("https://sub.domain.co.uk/test?q=1"), "sub.domain.co.uk")
        self.assertEqual(extract_domain("invalid-url"), "web")

    def test_missing_tavily_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                search_tavily("test query", api_key=None)
            self.assertIn("TAVILY_API_KEY is missing", str(ctx.exception))

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
    def test_missing_nebius_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                get_nebius_client(api_key=None)
            self.assertIn("NEBIUS_API_KEY is missing", str(ctx.exception))

    def test_nebius_base_url_default_and_env(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_nebius_base_url(), DEFAULT_NEBIUS_BASE_URL)
        
        custom_url = "https://custom.nebius.endpoint/v1/"
        with patch.dict(os.environ, {"NEBIUS_BASE_URL": custom_url}, clear=True):
            self.assertEqual(get_nebius_base_url(), custom_url)

    def test_nebius_model_from_env(self):
        pinned_model = "meta-llama/Llama-3.3-70B-Instruct"
        with patch.dict(os.environ, {"NEBIUS_MODEL": pinned_model}, clear=True):
            self.assertEqual(get_configured_nebius_model_name(), pinned_model)
            model_to_use = get_nebius_model(api_key="mock-key")
            self.assertEqual(model_to_use, pinned_model)

    @patch("llm.fetch_available_nebius_models")
    def test_nebius_model_empty_queries_models_endpoint(self, mock_fetch):
        mock_fetch.return_value = [
            "meta-llama/Llama-3.3-70B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct"
        ]
        with patch.dict(os.environ, {"NEBIUS_MODEL": ""}, clear=True):
            self.assertIsNone(get_configured_nebius_model_name())
            model_to_use = get_nebius_model(api_key="mock-key")
            self.assertEqual(model_to_use, "meta-llama/Llama-3.3-70B-Instruct")
            mock_fetch.assert_called_once()

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
        
        self.assertEqual(findings[0]["source_ids"], [1])
        self.assertEqual(findings[1]["source_ids"], [1, 2])
        self.assertEqual(findings[2]["source_ids"], [1])
        self.assertEqual(findings[3]["source_ids"], [])

    def test_agent_missing_tavily_key_raises_error_no_fake_output(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                run_verity_agent("Valid question", tavily_api_key=None, nebius_api_key="mock-key")
            self.assertIn("TAVILY_API_KEY is missing", str(ctx.exception))

    @patch("agent.search_tavily")
    def test_agent_missing_nebius_key_returns_sources_with_notice(self, mock_search):
        mock_search.return_value = self.sample_sources
        res = run_verity_agent("Valid question", tavily_api_key="mock-key", nebius_api_key=None)
        self.assertTrue(res["ai_unavailable"])
        self.assertEqual(res["answer"], "AI answer unavailable until NEBIUS_API_KEY is added.")
        self.assertEqual(res["model_used"], "None (NEBIUS_API_KEY missing)")
        self.assertEqual(len(res["sources"]), 2)

    def test_agent_empty_query_validation(self):
        with self.assertRaises(ValueError) as ctx:
            run_verity_agent("   ", tavily_api_key="mock", nebius_api_key="mock")
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
