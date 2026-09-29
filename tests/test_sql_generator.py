"""
tests/test_sql_generator.py — Tests for SQL Generator Module

Contains unit tests that can run WITHOUT external services (Groq API),
plus integration test stubs that require a live Groq API key.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_generator import generate_sql, _clean_sql_output


class TestCleanSQLOutput(unittest.TestCase):
    """Tests for the _clean_sql_output helper function."""

    def test_plain_sql(self):
        raw = "SELECT * FROM customers"
        self.assertEqual(_clean_sql_output(raw), "SELECT * FROM customers")

    def test_sql_with_markdown_fences(self):
        raw = "```sql\nSELECT * FROM customers\n```"
        result = _clean_sql_output(raw)
        self.assertNotIn("```", result)
        self.assertIn("SELECT", result)

    def test_sql_with_backtick_fences_no_lang(self):
        raw = "```\nSELECT * FROM customers\n```"
        result = _clean_sql_output(raw)
        self.assertNotIn("```", result)

    def test_trailing_semicolon_removed(self):
        raw = "SELECT * FROM customers;"
        result = _clean_sql_output(raw)
        self.assertFalse(result.endswith(";"))

    def test_whitespace_trimmed(self):
        raw = "   SELECT * FROM customers   "
        result = _clean_sql_output(raw)
        self.assertEqual(result, "SELECT * FROM customers")

    def test_empty_string(self):
        self.assertEqual(_clean_sql_output(""), "")

    def test_multiline_sql(self):
        raw = """SELECT c.name, SUM(o.amount)
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.name;"""
        result = _clean_sql_output(raw)
        self.assertIn("SELECT", result)
        self.assertIn("GROUP BY", result)
        self.assertFalse(result.endswith(";"))


class TestGenerateSQLInputValidation(unittest.TestCase):
    """Tests for input validation in generate_sql (no API calls)."""

    def test_empty_question(self):
        result = generate_sql("")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_whitespace_only_question(self):
        result = generate_sql("   ")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_none_question(self):
        result = generate_sql(None)
        self.assertFalse(result["success"])

    def test_missing_api_key(self):
        """Without GROQ_API_KEY set, should return an error."""
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
            result = generate_sql("Show all customers")
            self.assertFalse(result["success"])
            self.assertIn("GROQ_API_KEY", result["error"])


class TestGenerateSQLWithMock(unittest.TestCase):
    """Tests using a mocked Groq client (no real API calls)."""

    @patch("sql_generator._get_client")
    def test_successful_generation(self, mock_get_client):
        """Mock a successful LLM response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="SELECT * FROM customers"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            result = generate_sql("Show all customers")
            self.assertTrue(result["success"])
            self.assertIn("SELECT", result["sql"].upper())

    @patch("sql_generator._get_client")
    def test_cannot_generate_response(self, mock_get_client):
        """Mock an LLM response that says CANNOT_GENERATE."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="CANNOT_GENERATE"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            result = generate_sql("Delete everything in the database")
            self.assertFalse(result["success"])
            self.assertIn("could not generate", result["error"].lower())

    @patch("sql_generator._get_client")
    def test_api_error_handling(self, mock_get_client):
        """Mock an API exception."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API timeout")
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            result = generate_sql("Show all customers")
            self.assertFalse(result["success"])
            self.assertIn("error", result["error"].lower())

    @patch("sql_generator._get_client")
    def test_empty_llm_response(self, mock_get_client):
        """Mock an empty LLM response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=""))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            result = generate_sql("Show something")
            self.assertFalse(result["success"])

    def test_return_format(self):
        """Verify the return dictionary has expected keys."""
        result = generate_sql("")
        self.assertIn("success", result)
        self.assertIn("sql", result)
        self.assertIn("error", result)
        self.assertIn("model", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
