"""
chart_generator.py — Automatic Chart Generation Module

Analyzes query result DataFrames and generates appropriate
matplotlib charts based on the data structure.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure matplotlib saves figures with dark background
plt.rcParams["figure.facecolor"] = "#1B1F2A"
plt.rcParams["axes.facecolor"] = "#1B1F2A"
plt.rcParams["savefig.facecolor"] = "#1B1F2A"
plt.rcParams["text.color"] = "#F5F7FA"
plt.rcParams["axes.labelcolor"] = "#F5F7FA"
plt.rcParams["xtick.color"] = "#AAB2C0"
plt.rcParams["ytick.color"] = "#AAB2C0"



def generate_chart(df):
    """
    Analyze a DataFrame and generate an appropriate chart.

    Heuristics:
      - 1 categorical + 1 numeric column  → bar chart
      - 1 date/temporal + 1 numeric       → line chart
      - 1 categorical + percentages / small set → pie chart
      - 2 numeric columns                 → scatter chart
      - Otherwise                          → no chart

    Args:
        df (pd.DataFrame): The query result DataFrame.

    Returns:
        dict: {
            "has_chart": bool,
            "figure": matplotlib.figure.Figure or None,
            "chart_type": str or None,
            "reason": str
        }
    """
    result = {
        "has_chart": False,
        "figure": None,
        "chart_type": None,
        "reason": "",
    }

    if df is None or df.empty:
        result["reason"] = "No data available for charting."
        return result

    if len(df) < 1:
        result["reason"] = "Not enough data for a chart."
        return result

    if len(df) > 50:
        # Too many rows for a meaningful chart in this prototype
        result["reason"] = "Too many rows for a clear chart (>50). Showing table only."
        return result

    # Classify columns
    cat_cols = []
    num_cols = []
    date_cols = []

    for col in df.columns:
        if _is_date_column(df[col]):
            date_cols.append(col)
        elif _is_numeric_column(df[col]):
            num_cols.append(col)
        else:
            cat_cols.append(col)

    # --- Decision tree for chart type ---

    # Case 1: date + numeric → line chart
    if len(date_cols) >= 1 and len(num_cols) >= 1:
        fig = _create_line_chart(df, date_cols[0], num_cols[0])
        result["has_chart"] = True
        result["figure"] = fig
        result["chart_type"] = "line"
        result["reason"] = f"Line chart: {date_cols[0]} vs {num_cols[0]}"
        return result

    # Case 2: categorical + numeric → bar or pie
    if len(cat_cols) >= 1 and len(num_cols) >= 1:
        # Small set (≤6 categories) and single numeric → pie chart
        unique_count = df[cat_cols[0]].nunique()
        if unique_count <= 6 and len(df) <= 6:
            fig = _create_pie_chart(df, cat_cols[0], num_cols[0])
            result["has_chart"] = True
            result["figure"] = fig
            result["chart_type"] = "pie"
            result["reason"] = f"Pie chart: {cat_cols[0]} distribution by {num_cols[0]}"
        else:
            fig = _create_bar_chart(df, cat_cols[0], num_cols[0])
            result["has_chart"] = True
            result["figure"] = fig
            result["chart_type"] = "bar"
            result["reason"] = f"Bar chart: {cat_cols[0]} vs {num_cols[0]}"
        return result

    # Case 3: two numeric columns → scatter
    if len(num_cols) >= 2 and len(cat_cols) == 0:
        fig = _create_scatter_chart(df, num_cols[0], num_cols[1])
        result["has_chart"] = True
        result["figure"] = fig
        result["chart_type"] = "scatter"
        result["reason"] = f"Scatter chart: {num_cols[0]} vs {num_cols[1]}"
        return result

    # Case 4: single numeric column with row index
    if len(num_cols) == 1 and len(cat_cols) == 0 and len(date_cols) == 0:
        if len(df) == 1:
            result["reason"] = "Single value result — no chart needed."
        else:
            result["reason"] = "Cannot determine meaningful chart axes."
        return result

    result["reason"] = "Data structure not suitable for automatic charting."
    return result


# ── Helper: column type detection ──────────────────────────────────

def _is_numeric_column(series):
    """Check if a pandas Series is numeric."""
    if pd.api.types.is_numeric_dtype(series):
        return True
    # Try to convert
    try:
        pd.to_numeric(series, errors="raise")
        return True
    except (ValueError, TypeError):
        return False


def _is_date_column(series):
    """Check if a pandas Series looks like dates."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    # Check column name heuristic
    name_lower = str(series.name).lower()
    if any(kw in name_lower for kw in ["date", "month", "year", "day", "time"]):
        try:
            pd.to_datetime(series, errors="raise")
            return True
        except (ValueError, TypeError):
            pass
    return False


# ── Chart creation functions ──────────────────────────────────────

def _apply_dark_theme(fig, ax):
    """Style chart for dark theme integration."""
    fig.patch.set_facecolor("#1B1F2A")
    ax.set_facecolor("#1B1F2A")
    ax.tick_params(colors="#AAB2C0", labelsize=9)
    ax.xaxis.label.set_color("#F5F7FA")
    ax.yaxis.label.set_color("#F5F7FA")
    ax.title.set_color("#F5F7FA")
    for spine in ax.spines.values():
        spine.set_color("#303746")


def _create_bar_chart(df, x_col, y_col):
    """Create a horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.5)))
    _apply_dark_theme(fig, ax)

    # Ensure numeric
    y_data = pd.to_numeric(df[y_col], errors="coerce")

    colors = plt.cm.viridis(
        [i / max(len(df) - 1, 1) for i in range(len(df))]
    )

    bars = ax.barh(df[x_col].astype(str), y_data, color=colors)
    ax.set_xlabel(y_col.replace("_", " ").title())
    ax.set_ylabel(x_col.replace("_", " ").title())
    ax.set_title(f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}")
    ax.invert_yaxis()

    # Add value labels
    for bar, val in zip(bars, y_data):
        if pd.notna(val):
            ax.text(
                bar.get_width() + max(y_data) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.2f}" if isinstance(val, float) else str(val),
                va="center",
                fontsize=9,
                color="#F5F7FA",
            )

    plt.tight_layout()
    return fig


def _create_line_chart(df, x_col, y_col):
    """Create a line chart for time-series data."""
    fig, ax = plt.subplots(figsize=(10, 5))
    _apply_dark_theme(fig, ax)
    ax.grid(True, linestyle="--", alpha=0.25, color="#7F8999")

    x_data = pd.to_datetime(df[x_col], errors="coerce")
    y_data = pd.to_numeric(df[y_col], errors="coerce")

    # Sort by date
    sorted_idx = x_data.argsort()
    x_sorted = x_data.iloc[sorted_idx]
    y_sorted = y_data.iloc[sorted_idx]

    ax.plot(x_sorted, y_sorted, marker="o", linewidth=2.5, color="#4F8CFF")
    ax.fill_between(x_sorted, y_sorted, alpha=0.2, color="#4F8CFF")
    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    ax.set_title(f"{y_col.replace('_', ' ').title()} over {x_col.replace('_', ' ').title()}")

    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def _create_pie_chart(df, label_col, value_col):
    """Create a pie chart for categorical distributions."""
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1B1F2A")
    ax.set_facecolor("#1B1F2A")

    labels = df[label_col].astype(str)
    values = pd.to_numeric(df[value_col], errors="coerce")

    colors = plt.cm.Set3([i / max(len(df) - 1, 1) for i in range(len(df))])

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
    )
    for t in texts:
        t.set_color("#F5F7FA")
        t.set_fontsize(9)
    for at in autotexts:
        at.set_color("#151922")
        at.set_fontweight("bold")
        at.set_fontsize(8.5)

    ax.set_title(f"{value_col.replace('_', ' ').title()} by {label_col.replace('_', ' ').title()}", color="#F5F7FA")

    plt.tight_layout()
    return fig


def _create_scatter_chart(df, x_col, y_col):
    """Create a scatter plot for two numeric columns."""
    fig, ax = plt.subplots(figsize=(8, 6))
    _apply_dark_theme(fig, ax)
    ax.grid(True, linestyle="--", alpha=0.25, color="#7F8999")

    x_data = pd.to_numeric(df[x_col], errors="coerce")
    y_data = pd.to_numeric(df[y_col], errors="coerce")

    ax.scatter(x_data, y_data, alpha=0.85, color="#FF5C67", edgecolors="#F5F7FA", s=50)
    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    ax.set_title(f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}")

    plt.tight_layout()
    return fig
