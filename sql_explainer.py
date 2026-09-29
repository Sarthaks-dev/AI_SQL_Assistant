"""
sql_explainer.py — SQL Explanation Module

Uses the Groq LLM to generate a plain-English explanation of
a given SQL query, helping non-technical users understand what
the query does.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-120b"


def _get_client(api_key=None):
    """Create and return a Groq client."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(api_key=key)


def _get_model():
    """Return the configured Groq model name."""
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL)


def explain_sql(sql, api_key=None, allow_demo_fallback=False):
    """
    Generate a plain-English explanation of the given SQL query.

    Args:
        sql (str): The SQL query to explain.
        api_key (str, optional): Groq API key override.
        allow_demo_fallback (bool): If True and no API key is set, use demo explainer.

    Returns:
        dict: {
            "success": bool,
            "explanation": str or None,
            "error": str or None
        }
    """
    result = {
        "success": False,
        "explanation": None,
        "error": None,
    }

    if not sql or not sql.strip():
        result["error"] = "No SQL query provided for explanation."
        return result

    active_key = api_key or os.getenv("GROQ_API_KEY")
    if not active_key:
        if allow_demo_fallback:
            from demo_mode import DEMO_QUERIES
            # Check if this SQL matches any demo queries
            clean_sql_norm = " ".join(sql.strip().split()).upper()
            for dq in DEMO_QUERIES.values():
                ref_sql_norm = " ".join(dq["sql"].strip().split()).upper()
                if clean_sql_norm == ref_sql_norm:
                    result["success"] = True
                    result["explanation"] = dq["explanation"]
                    return result
            # General fallback explanation
            result["success"] = True
            result["explanation"] = (
                "This query retrieves data from the database using SQL SELECT, "
                "applying required joins, filters, aggregations, and ordering to provide analytical insights."
            )
            return result
        result["error"] = "GROQ_API_KEY is not set."
        return result

    try:
        client = _get_client(api_key=active_key)
        model = _get_model()

        system_prompt = """You are a helpful SQL teacher. 
Your job is to explain SQL queries in simple, plain English that a non-technical person can understand.

RULES:
1. Explain what the query does step by step.
2. Mention which tables are used and how they are connected.
3. Explain any filters, grouping, sorting, or limits.
4. Keep the explanation concise — 2 to 4 sentences.
5. Do NOT include any SQL code in your explanation.
6. Use everyday language, not technical jargon."""

        user_prompt = f"Please explain this SQL query in simple language:\n\n{sql}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=512,
            top_p=1,
        )

        explanation = response.choices[0].message.content.strip()

        if explanation:
            result["success"] = True
            result["explanation"] = explanation
        else:
            result["error"] = "The AI returned an empty explanation."

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Explanation generation error: {e}"

    return result
