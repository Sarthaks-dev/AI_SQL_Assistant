"""
sql_validator.py — SQL Safety Validation Module

Validates generated SQL queries to ensure they are read-only and safe
to execute. This is the critical safety barrier before query execution.
"""

import re


# SQL keywords/statements that are NOT allowed (destructive or modifying)
FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "CALL",
    "LOAD DATA",
    "LOAD",
    "SET",
    "RENAME",
    "LOCK",
    "UNLOCK",
    "FLUSH",
    "PURGE",
    "RESET",
    "KILL",
    "EXECUTE",
    "PREPARE",
    "DEALLOCATE",
    "HANDLER",
    "DO",
    "IMPORT",
    "INSTALL",
    "UNINSTALL",
]


def validate_sql(sql):
    """
    Validate a SQL query for safety before execution.

    Ensures the query is read-only (SELECT / WITH … SELECT) and does
    not contain destructive or modifying statements.

    Args:
        sql (str): The SQL query string to validate.

    Returns:
        dict: {
            "is_safe": bool,
            "reason": str,
            "sanitized_sql": str or None
        }
    """
    result = {
        "is_safe": False,
        "reason": "",
        "sanitized_sql": None,
    }

    if not sql or not sql.strip():
        result["reason"] = "Empty SQL query."
        return result

    # --- Step 1: Normalize the SQL -----------------------------------------
    sanitized = _normalize_sql(sql)

    # --- Step 2: Reject multiple statements --------------------------------
    if _has_multiple_statements(sanitized):
        result["reason"] = (
            "Multiple SQL statements detected. "
            "Only single analytical queries are allowed."
        )
        return result

    # --- Step 3: Check for forbidden keywords ------------------------------
    forbidden_found = _detect_forbidden_keywords(sanitized)
    if forbidden_found:
        result["reason"] = (
            f"Unsafe SQL operation detected: {', '.join(forbidden_found)}. "
            "Only read-only SELECT queries are allowed."
        )
        return result

    # --- Step 4: Ensure it starts with SELECT or WITH ----------------------
    if not _is_read_only_query(sanitized):
        result["reason"] = (
            "Query does not begin with SELECT or WITH. "
            "Only read-only analytical queries are permitted."
        )
        return result

    # --- Step 5: Check for USE statement -----------------------------------
    if _contains_use_statement(sanitized):
        result["reason"] = (
            "USE statement detected. "
            "Database switching is not allowed."
        )
        return result

    # All checks passed
    result["is_safe"] = True
    result["reason"] = "Query is safe (read-only SELECT)."
    result["sanitized_sql"] = sanitized
    return result


def _normalize_sql(sql):
    """
    Normalize SQL: strip whitespace, remove markdown fences, trailing
    semicolons, and collapse internal whitespace.
    """
    s = sql.strip()

    # Remove markdown code fences (```sql ... ``` or ``` ... ```)
    s = re.sub(r"^```(?:sql)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s, flags=re.IGNORECASE)
    s = s.strip()

    # Remove trailing semicolons
    s = s.rstrip(";").strip()

    # Collapse multiple spaces/newlines into single spaces
    # (preserve readability but simplify pattern matching)
    normalized = re.sub(r"\s+", " ", s)

    return normalized


def _has_multiple_statements(sql):
    """
    Detect whether the SQL contains multiple statements separated by
    semicolons. Ignores semicolons inside string literals.
    """
    # Simple heuristic: look for ';' that is NOT inside quotes
    in_single = False
    in_double = False
    for i, char in enumerate(sql):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == ";" and not in_single and not in_double:
            # There is a semicolon outside quotes — remaining text after it?
            remaining = sql[i + 1 :].strip()
            if remaining:
                return True
    return False


def _detect_forbidden_keywords(sql):
    """
    Detect forbidden SQL keywords in the query.
    Uses word-boundary matching to avoid false positives
    (e.g., 'UPDATED_AT' should not match 'UPDATE').

    Returns:
        list: Forbidden keywords found, or empty list.
    """
    upper_sql = sql.upper()
    found = []
    for kw in FORBIDDEN_KEYWORDS:
        # Match whole word only
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, upper_sql):
            found.append(kw)
    return found


def _is_read_only_query(sql):
    """
    Check that the query starts with SELECT or WITH (for CTEs).
    """
    upper = sql.strip().upper()
    return upper.startswith("SELECT") or upper.startswith("WITH")


def _contains_use_statement(sql):
    """
    Check for 'USE <database>' statements.
    """
    return bool(re.match(r"^\s*USE\s+", sql, re.IGNORECASE))
