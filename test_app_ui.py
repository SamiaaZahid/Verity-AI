import os
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class TestStreamlitAppUI(unittest.TestCase):
    def test_missing_keys_setup_message_on_load(self):
        """Verify that when API keys are missing, the UI shows a clear setup message and no fake output."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "", "NEBIUS_API_KEY": ""}):
            at = AppTest.from_file("app.py", default_timeout=15).run()
            
            # Ensure app did not crash
            self.assertFalse(at.exception)
            
            # Check markdown elements for setup required message
            all_markdown_text = " ".join([m.value for m in at.markdown])
            self.assertIn("API Configuration Required", all_markdown_text)
            self.assertIn("TAVILY_API_KEY", all_markdown_text)
            self.assertIn("NEBIUS_API_KEY", all_markdown_text)
            self.assertIn("No fake or ungrounded responses are ever produced", all_markdown_text)

            # Check that no research synthesis card or fake sources exist
            self.assertNotIn("Verified Synthesis", all_markdown_text)
            self.assertNotIn("Primary Web Evidence", all_markdown_text)

    def test_missing_keys_blocks_execution_on_button_click(self):
        """Verify that clicking research with missing keys blocks execution and shows error setup instructions."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "", "NEBIUS_API_KEY": ""}):
            at = AppTest.from_file("app.py", default_timeout=15).run()
            
            # Fill in a question
            at.text_input[0].input("What is the launch date of Artemis II?").run()
            
            # Find and click the 'Run Verified Research' button
            research_btn = None
            for btn in at.button:
                if "Run Verified Research" in btn.label:
                    research_btn = btn
                    break
            
            self.assertIsNotNone(research_btn, "Research button not found")
            research_btn.click().run()
            
            # Check error message displayed
            self.assertTrue(len(at.error) > 0)
            error_text = " ".join([e.value for e in at.error])
            self.assertIn("Execution Blocked", error_text)
            self.assertIn("is missing from environment / secrets", error_text)

            # Ensure no fake synthesis or fake results are produced
            all_markdown = " ".join([m.value for m in at.markdown])
            self.assertNotIn("Verified Synthesis", all_markdown)
            self.assertNotIn("100% Grounded Citations", all_markdown)

if __name__ == "__main__":
    unittest.main()
