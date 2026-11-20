import os
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
from streamlit.testing.v1 import AppTest

load_dotenv()

class TestStreamlitAppUI(unittest.TestCase):
    def test_empty_input_shows_warning(self):
        """Verify submitting an empty inquiry displays a warning and does not trigger search."""
        at = AppTest.from_file("app.py", default_timeout=15).run()
        self.assertFalse(at.exception)
        
        # Click research with empty input
        research_btn = None
        for btn in at.button:
            if "Run Verified Research" in btn.label:
                research_btn = btn
                break
        
        self.assertIsNotNone(research_btn)
        research_btn.click().run()
        
        # Verify warning is shown
        self.assertTrue(len(at.warning) > 0)
        self.assertIn("Please enter a research inquiry", at.warning[0].value)

    def test_missing_tavily_key_blocks_execution(self):
        """Verify that when TAVILY_API_KEY is missing, execution is blocked with clear setup error."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": ""}):
            at = AppTest.from_file("app.py", default_timeout=15).run()
            at.text_input[0].input("What is Artemis II?").run()
            
            research_btn = None
            for btn in at.button:
                if "Run Verified Research" in btn.label:
                    research_btn = btn
                    break
            
            research_btn.click().run()
            
            self.assertTrue(len(at.error) > 0)
            self.assertIn("TAVILY_API_KEY is missing", at.error[0].value)

    def test_missing_nebius_key_allows_search_and_shows_notice(self):
        """Verify that when NEBIUS_API_KEY is missing, search runs, sources appear, and clear notice replaces AI answer."""
        tavily_key = os.environ.get("TAVILY_API_KEY", "")
        if not tavily_key:
            self.skipTest("TAVILY_API_KEY not present in environment")

        with patch.dict(os.environ, {"NEBIUS_API_KEY": ""}):
            at = AppTest.from_file("app.py", default_timeout=20).run()
            at.text_input[0].input("NASA Artemis II launch date").run()
            
            research_btn = None
            for btn in at.button:
                if "Run Verified Research" in btn.label:
                    research_btn = btn
                    break
            
            research_btn.click().run()
            
            all_markdown = " ".join([m.value for m in at.markdown])
            
            # Check for AI unavailable notice
            self.assertIn("AI answer unavailable until NEBIUS_API_KEY is added", all_markdown)
            
            # Check that real sources are rendered
            self.assertIn("Primary Web Evidence", all_markdown)
            self.assertIn("SOURCE [1]", all_markdown)
            
            # Check that Research Transparency panel is rendered
            self.assertIn("Research Transparency Audit", all_markdown)
            self.assertIn("None (NEBIUS_API_KEY missing)", all_markdown)

            # Ensure no fake synthesis or fake citations
            self.assertNotIn("100% Grounded Citations", all_markdown)

if __name__ == "__main__":
    unittest.main()
