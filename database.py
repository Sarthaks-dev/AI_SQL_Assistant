"""
database.py — MySQL Database Connection and Query Execution Module

Handles all database interactions including connection management,
query execution, and schema retrieval for the AI SQL Assistant.
"""

import os
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    """Retrieve database configuration from environment variables."""
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "ai_sales"),
    }


_last_error = None


def get_connection():
    """
    Create and return a MySQL database connection.
    
    Returns:
        mysql.connector.connection.MySQLConnection or None
    """
    global _last_error
    try:
        config = get_db_config()
        connection = mysql.connector.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            connection_timeout=10,
        )
        _last_error = None
        return connection
    except Error as e:
        _last_error = str(e)
        return None


def test_connection():
    """
    Test whether the database connection is successful.
    
    Returns:
        tuple: (bool success, str message)
    """
    global _last_error
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            server_info = conn.get_server_info()
            conn.close()
            return True, f"Connected to MySQL Server {server_info}"
        err_detail = f": {_last_error}" if _last_error else ""
        return False, f"Connection failed{err_detail} — check your .env configuration and MySQL service."
    except Error as e:
        return False, f"Connection failed: {e}"


LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "ai_sales.db")


def is_local_db_available():
    """Check if the local SQLite mirror database exists."""
    return os.path.exists(LOCAL_DB_PATH)


def execute_query(sql, allow_fallback=False):
    """
    Execute a read-only SQL query and return results as a DataFrame.
    
    Args:
        sql (str): The SQL query to execute.
        allow_fallback (bool): If True and MySQL is unreachable, query the local demo DB.
    
    Returns:
        dict: {
            "success": bool,
            "data": pd.DataFrame or None,
            "row_count": int,
            "execution_time": float (seconds),
            "error": str or None,
            "engine": str
        }
    """
    result = {
        "success": False,
        "data": None,
        "row_count": 0,
        "execution_time": 0.0,
        "error": None,
        "engine": "MySQL",
    }

    conn = None
    try:
        conn = get_connection()
        if conn is None:
            if allow_fallback and is_local_db_available():
                return _execute_sqlite_fallback(sql)
            result["error"] = (
                "Could not connect to the database. "
                "Please check your MySQL configuration in .env."
            )
            return result

        start_time = time.time()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        end_time = time.time()

        df = pd.DataFrame(rows) if rows else pd.DataFrame()

        result["success"] = True
        result["data"] = df
        result["row_count"] = len(df)
        result["execution_time"] = round(end_time - start_time, 4)
        result["engine"] = "MySQL"

        cursor.close()
    except Error as e:
        result["error"] = f"SQL Execution Error: {e}"
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()

    return result


def _execute_sqlite_fallback(sql):
    """Execute SQL against the local SQLite mirror database."""
    import sqlite3
    result = {
        "success": False,
        "data": None,
        "row_count": 0,
        "execution_time": 0.0,
        "error": None,
        "engine": "SQLite (Demo Mirror)",
    }
    try:
        start_time = time.time()
        conn = sqlite3.connect(LOCAL_DB_PATH)
        df = pd.read_sql_query(sql, conn)
        end_time = time.time()
        conn.close()

        result["success"] = True
        result["data"] = df
        result["row_count"] = len(df)
        result["execution_time"] = round(end_time - start_time, 4)
    except Exception as e:
        result["error"] = f"Demo Query Execution Error: {e}"
    return result


def get_table_names():
    """
    Retrieve all table names from the database.
    
    Returns:
        list: Table names, or empty list on failure.
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            if is_local_db_available():
                import sqlite3
                s_conn = sqlite3.connect(LOCAL_DB_PATH)
                s_cursor = s_conn.cursor()
                s_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [r[0] for r in s_cursor.fetchall()]
                s_conn.close()
                return tables
            return []
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    except Error:
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_table_columns(table_name):
    """
    Retrieve column details for a specific table.
    
    Args:
        table_name (str): Name of the table.
    
    Returns:
        list[dict]: Column info with name, type, key, nullable.
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            if is_local_db_available():
                import sqlite3
                s_conn = sqlite3.connect(LOCAL_DB_PATH)
                s_cursor = s_conn.cursor()
                s_cursor.execute(f"PRAGMA table_info({table_name})")
                cols = []
                for row in s_cursor.fetchall():
                    cols.append({
                        "Field": row[1],
                        "Type": row[2],
                        "Key": "PRI" if row[5] else "",
                    })
                s_conn.close()
                return cols
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        cursor.close()
        return columns
    except Error:
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_schema_string():
    """
    Build a human-readable schema string for the LLM prompt.
    
    Returns:
        str: Formatted schema description.
    """
    tables = get_table_names()
    if not tables:
        # Fallback: return the known static schema
        return _get_static_schema()

    schema_parts = []
    for table in tables:
        columns = get_table_columns(table)
        col_lines = []
        for col in columns:
            col_name = col.get("Field", "")
            col_type = col.get("Type", "")
            col_key = col.get("Key", "")
            extra = ""
            if col_key == "PRI":
                extra = " (PRIMARY KEY)"
            elif col_key == "MUL":
                extra = " (FOREIGN KEY)"
            col_lines.append(f"  - {col_name} ({col_type}){extra}")
        schema_parts.append(f"{table}:\n" + "\n".join(col_lines))

    return "\n\n".join(schema_parts)


def _get_static_schema():
    """Return the known static schema when DB is unavailable."""
    return """customers:
  - customer_id (INT) (PRIMARY KEY)
  - name (VARCHAR(100))
  - email (VARCHAR(150))
  - city (VARCHAR(100))
  - registration_date (DATE)

products:
  - product_id (INT) (PRIMARY KEY)
  - product_name (VARCHAR(150))
  - category (VARCHAR(100))
  - price (DECIMAL(10,2))

orders:
  - order_id (INT) (PRIMARY KEY)
  - customer_id (INT) (FOREIGN KEY)
  - product_id (INT) (FOREIGN KEY)
  - quantity (INT)
  - order_date (DATE)
  - amount (DECIMAL(10,2))"""
