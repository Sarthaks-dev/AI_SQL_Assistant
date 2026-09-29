"""
tests/test_sql_validator.py — Automated Tests for SQL Validation

Tests the sql_validator module to ensure it correctly identifies
safe (read-only) and unsafe (destructive/modifying) SQL queries.
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_validator import validate_sql


class TestSQLValidatorSafe(unittest.TestCase):
    """Tests for queries that SHOULD be marked as SAFE."""

    def test_simple_select(self):
        sql = "SELECT * FROM customers"
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_where(self):
        sql = "SELECT name, email FROM customers WHERE city = 'Mumbai'"
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_join(self):
        sql = """
        SELECT c.name, o.amount
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_group_by(self):
        sql = """
        SELECT c.city, SUM(o.amount) AS total_sales
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.city
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_order_by(self):
        sql = """
        SELECT product_name, price
        FROM products
        ORDER BY price DESC
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_limit(self):
        sql = """
        SELECT c.name, SUM(o.amount) AS total
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total DESC
        LIMIT 5
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_aggregation(self):
        sql = "SELECT COUNT(*) AS total_orders FROM orders"
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_subquery(self):
        sql = """
        SELECT name FROM customers
        WHERE customer_id IN (
            SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 3
        )
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_cte(self):
        sql = """
        WITH top_customers AS (
            SELECT customer_id, SUM(amount) AS total
            FROM orders
            GROUP BY customer_id
            ORDER BY total DESC
            LIMIT 5
        )
        SELECT c.name, tc.total
        FROM top_customers tc
        JOIN customers c ON tc.customer_id = c.customer_id
        """
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_markdown_fences(self):
        sql = "```sql\nSELECT * FROM products\n```"
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_with_trailing_semicolon(self):
        sql = "SELECT * FROM customers;"
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")

    def test_select_column_named_updated_at(self):
        """Column names containing forbidden keywords should not trigger false positives."""
        sql = "SELECT customer_id, name FROM customers"
        # This is safe — 'customer_id' does not contain a forbidden keyword
        result = validate_sql(sql)
        self.assertTrue(result["is_safe"], f"Expected safe: {result['reason']}")


class TestSQLValidatorUnsafe(unittest.TestCase):
    """Tests for queries that SHOULD be marked as UNSAFE."""

    def test_insert(self):
        sql = "INSERT INTO customers (name, email) VALUES ('Test', 'test@test.com')"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "INSERT should be unsafe")

    def test_update(self):
        sql = "UPDATE customers SET name = 'Hacked' WHERE customer_id = 1"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "UPDATE should be unsafe")

    def test_delete(self):
        sql = "DELETE FROM customers WHERE customer_id = 1"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "DELETE should be unsafe")

    def test_drop_table(self):
        sql = "DROP TABLE customers"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "DROP should be unsafe")

    def test_alter_table(self):
        sql = "ALTER TABLE customers ADD COLUMN phone VARCHAR(20)"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "ALTER should be unsafe")

    def test_truncate(self):
        sql = "TRUNCATE TABLE orders"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "TRUNCATE should be unsafe")

    def test_create_table(self):
        sql = "CREATE TABLE hacked (id INT)"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "CREATE should be unsafe")

    def test_grant(self):
        sql = "GRANT ALL PRIVILEGES ON ai_sales.* TO 'hacker'@'%'"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "GRANT should be unsafe")

    def test_multiple_statements(self):
        sql = "SELECT * FROM customers; DROP TABLE customers"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "Multiple statements should be unsafe")

    def test_multiple_statements_select_only(self):
        sql = "SELECT 1; SELECT 2"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "Multiple SELECT statements should be unsafe")

    def test_empty_query(self):
        sql = ""
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "Empty query should be unsafe")

    def test_none_query(self):
        result = validate_sql(None)
        self.assertFalse(result["is_safe"], "None query should be unsafe")

    def test_use_statement(self):
        sql = "USE mysql"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "USE statement should be unsafe")

    def test_load_data(self):
        sql = "LOAD DATA INFILE '/tmp/data.csv' INTO TABLE customers"
        result = validate_sql(sql)
        self.assertFalse(result["is_safe"], "LOAD DATA should be unsafe")


class TestSQLValidatorReturnFormat(unittest.TestCase):
    """Tests for the return structure of validate_sql."""

    def test_return_keys(self):
        result = validate_sql("SELECT 1")
        self.assertIn("is_safe", result)
        self.assertIn("reason", result)
        self.assertIn("sanitized_sql", result)

    def test_safe_returns_sanitized_sql(self):
        result = validate_sql("SELECT * FROM products")
        self.assertTrue(result["is_safe"])
        self.assertIsNotNone(result["sanitized_sql"])
        self.assertIn("SELECT", result["sanitized_sql"].upper())

    def test_unsafe_returns_no_sanitized_sql(self):
        result = validate_sql("DROP TABLE customers")
        self.assertFalse(result["is_safe"])
        self.assertIsNone(result["sanitized_sql"])

    def test_reason_is_string(self):
        result = validate_sql("SELECT 1")
        self.assertIsInstance(result["reason"], str)
        self.assertTrue(len(result["reason"]) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
