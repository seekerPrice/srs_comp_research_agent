import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import sqlite3
import uuid

# Ensure we can import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph import create_graph

class TestAgentIntegration(unittest.TestCase):
    
    def setUp(self):
        # Use an in-memory database for testing to avoid creating files
        self.mock_db_patcher = patch('sqlite3.connect', side_effect=lambda x, **kwargs: sqlite3.connect(":memory:", **kwargs))
        self.mock_db = self.mock_db_patcher.start()

    def tearDown(self):
        self.mock_db_patcher.stop()

    def test_agent_citation_flow(self):
        """
        Tests the full agent flow:
        1. Planner creates a plan.
        2. Researcher executes the plan (hopefully selecting Citation Formatter).
        3. Responder synthesizes the result.
        """
        print("\n\nRunning End-to-End Agent Citation Test...")
        
        # Initialize the graph
        app = create_graph()
        
        # unique thread per test
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        topic = "Get the APA citation for the paper 'Attention Is All You Need' by Vaswani"
        print(f"Topic: {topic}")
        
        # Run the agent
        # We need to collect the final output. The graph returns the final state.
        final_state = app.invoke({"topic": topic}, config=config)
        
        # Check findings (Researcher output)
        findings = final_state.get('findings', [])
        print(f"Findings: {findings}")
        
        # Check final response (Responder output)
        messages = final_state.get('messages', [])
        final_answer = messages[-1] if messages else ""
        print(f"Final Agent Answer: {final_answer}")
        
        # Assertions
        # 1. Verify that we have findings
        self.assertTrue(len(findings) > 0, "Agent should have produced findings")
        
        # 2. Verify that the Citation Formatter was likely used (by checking the source in findings)
        # Note: The researcher node formats finding as "Source: {source}..."
        citation_tool_used = any("Source: Citation Formatter" in f for f in findings)
        self.assertTrue(citation_tool_used, "Agent should have selected the Citation Formatter tool")
        
        # 3. Verify the final answer contains the citation details
        self.assertIn("Vaswani", final_answer)
        self.assertIn("2017", final_answer)

if __name__ == '__main__':
    unittest.main()
