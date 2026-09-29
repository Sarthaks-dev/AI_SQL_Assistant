"""
tests/test_database.py — Tests for Database Module

Tests database connection utilities and query execution.
Unit tests use mocking to avoid requiring a live MySQL server.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    get_db_config,
    test_connection,
    execute_query,
    get_schema_string,
    _get_static_schema,
)


class TestDBConfig(unittest.TestCase):
    """Tests for database configuration loading."""

    def test_config_returns_dict(self):
        config = get_db_config()
        self.assertIsInstance(config, dict)
        self.assertIn("host", config)
        self.assertIn("port", config)
        self.assertIn("user", config)
        self.assertIn("password", config)
        self.assertIn("database", config)

    def test_config_port_is_int(self):
        config = get_db_config()
        self.assertIsInstance(config["port"], int)

    def test_default_values(self):
        with patch.dict(os.environ, {}, clear=True):
            config = get_db_config()
            self.assertEqual(config["host"], "localhost")
            self.assertEqual(config["port"], 3306)
            self.assertEqual(config["database"], "ai_sales")


class TestConnectionFailure(unittest.TestCase):
    """Test behavior when MySQL is unavailable."""

    @patch("database.mysql.connector.connect")
    def test_connection_failure(self, mock_connect):
        """Simulate MySQL connection failure."""
        from mysql.connector import Error
        mock_connect.side_effect = Error("Connection refused")

        success, msg = test_connection()
        self.assertFalse(success)
        self.assertIn("failed", msg.lower())

    @patch("database.get_connection")
    def test_execute_query_no_connection(self, mock_conn):
        """execute_query should return error when connection is None."""
        mock_conn.return_value = None

        result = execute_query("SELECT 1")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("connect", result["error"].lower())


class TestExecuteQueryFormat(unittest.TestCase):
    """Test the return format of execute_query."""

    @patch("database.get_connection")
    def test_return_keys(self, mock_conn):
        mock_conn.return_value = None
        result = execute_query("SELECT 1")
        self.assertIn("success", result)
        self.assertIn("data", result)
        self.assertIn("row_count", result)
        self.assertIn("execution_time", result)
        self.assertIn("error", result)

    @patch("database.get_connection")
    def test_successful_query_mock(self, mock_get_conn):
        """Mock a successful query execution."""
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"customer_id": 1, "name": "Aarav Sharma"},
            {"customer_id": 2, "name": "Priya Patel"},
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = execute_query("SELECT customer_id, name FROM customers LIMIT 2")
        self.assertTrue(result["success"])
        self.assertIsInstance(result["data"], pd.DataFrame)
        self.assertEqual(result["row_count"], 2)

    @patch("database.get_connection")
    def test_empty_result_mock(self, mock_get_conn):
        """Mock a query that returns no rows."""
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = execute_query("SELECT * FROM customers WHERE city = 'Nonexistent'")
        self.assertTrue(result["success"])
        self.assertEqual(result["row_count"], 0)


class TestStaticSchema(unittest.TestCase):
    """Test the fallback static schema."""

    def test_static_schema_contains_tables(self):
        schema = _get_static_schema()
        self.assertIn("customers", schema)
        self.assertIn("products", schema)
        self.assertIn("orders", schema)

    def test_static_schema_contains_columns(self):
        schema = _get_static_schema()
        self.assertIn("customer_id", schema)
        self.assertIn("product_name", schema)
        self.assertIn("order_date", schema)
        self.assertIn("amount", schema)


class TestGetSchemaString(unittest.TestCase):
    """Test get_schema_string falls back gracefully."""

    @patch("database.get_table_names")
    def test_fallback_when_no_tables(self, mock_tables):
        """When DB is unavailable, should return static schema."""
        mock_tables.return_value = []
        schema = get_schema_string()
        self.assertIn("customers", schema)
        self.assertIn("products", schema)
        self.assertIn("orders", schema)


if __name__ == "__main__":
    unittest.main(verbosity=2)
