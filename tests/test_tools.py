import unittest
import sys
import os
from dotenv import load_dotenv

# Ensure we can import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables for real API calls
load_dotenv()

from tools import format_citation

class TestToolsIntegration(unittest.TestCase):
    """
    Integration tests that make REAL calls to the LLM to verify performance/output quality.
    WARNING: These tests consume API credits.
    """

    def test_format_citation_apa_real(self):
        print("\n\nRunning real LLM citation test...")
        query = "Attention Is All You Need paper (Ashish Vaswani et al, 2017) in APA"
        result = format_citation(query)
        print(f"LLM Output for APA: {result}")

        # Basic validation of the output structure
        self.assertIn("Vaswani", result, "Citation should mention the author 'Vaswani'")
        self.assertIn("2017", result, "Citation should mention the year '2017'")
        self.assertIn("Attention is all you need", result, "Citation should contain the title (case insensitive check usually preferred, but strict here)")

    def test_format_citation_bibtex_real(self):
        print("\n\nRunning real LLM BibTeX test...")
        query = "Deep Learning by Ian Goodfellow in BibTeX"
        result = format_citation(query)
        print(f"LLM Output for BibTeX: {result}")

        # Basic validation for BibTeX format
        self.assertIn("@book", result.lower(), "BibTeX should probably be a @book or @misc entry")
        self.assertIn("Goodfellow", result, "Citation should mention 'Goodfellow'")
        self.assertIn("author", result.lower(), "BeibTeX should have an author field")

    def test_tool_selection_performance(self):
        # We can also test the prompt logic if we want, but sticking to citation tool as requested
        pass

if __name__ == '__main__':
    unittest.main()
