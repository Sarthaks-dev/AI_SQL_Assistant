"""
init_demo_db.py — Local SQLite Database Initializer

Creates a local SQLite mirror of the `ai_sales` MySQL database with the exact
same schema and sample data from `database.sql`. This enables immediate offline
demonstration, automated UI testing, and presentation captures even when a live
MySQL daemon is not currently active on the host machine.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ai_sales.db")


def init_sqlite_db():
    """Create and populate the local SQLite ai_sales database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")

    # Create tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        city TEXT,
        registration_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT,
        price REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        order_date TEXT,
        amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # Read and execute insert statements from database.sql
    sql_file = os.path.join(os.path.dirname(__file__), "database.sql")
    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove SQL line comments
    clean_lines = []
    for line in content.splitlines():
        line_stripped = line.strip()
        if not line_stripped.startswith("--"):
            clean_lines.append(line)
    clean_sql = "\n".join(clean_lines)

    # Extract and execute statements
    statements = clean_sql.split(";")
    for stmt in statements:
        stmt_clean = stmt.strip()
        if stmt_clean.upper().startswith("INSERT INTO"):
            cursor.execute(stmt_clean)

    conn.commit()

    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    conn.close()
    return cust_count, prod_count, order_count


if __name__ == "__main__":
    c, p, o = init_sqlite_db()
    print(f"Initialized local SQLite ai_sales.db successfully:")
    print(f"  - Customers: {c} rows")
    print(f"  - Products:  {p} rows")
    print(f"  - Orders:    {o} rows")
