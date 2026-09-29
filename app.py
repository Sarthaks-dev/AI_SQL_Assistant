"""
app.py — AI SQL Query Generator & Database Assistant

A sleek, cohesive dark-theme developer-tool interface for querying MySQL databases
using AI-generated SQL with deterministic safety validation.
"""

import os
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from database import test_connection, execute_query, get_table_names, get_table_columns
from sql_generator import generate_sql
from sql_validator import validate_sql
from chart_generator import generate_chart
from sql_explainer import explain_sql

load_dotenv(override=True)

# ── Page Configuration ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Initialization ──────────────────────────────────
if "pending_query_input" not in st.session_state:
    st.session_state["pending_query_input"] = None

# ── Cohesive Dark Theme Custom CSS ─────────────────────────────────

st.markdown("""
<style>
    /* ── Color Palette Variables ──────────────────────────────────────
       Main Background:       #0F1117
       Sidebar Background:    #151922
       Card Background:       #1B1F2A
       Elevated Background:   #202532
       Borders:               #303746
       Primary Text:          #F5F7FA
       Secondary Text:        #AAB2C0
       Muted Text:            #7F8999
       Primary Accent:        #4F8CFF
       Primary Hover:         #3A78F2
       Success:               #35D07F
       Warning:               #F5B942
       Danger:                #FF5C67
    ──────────────────────────────────────────────────────────────── */

    /* Global Base Reset */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        background-color: #0F1117 !important;
        color: #F5F7FA !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1300px;
    }

    /* Typography & Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #F5F7FA !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em;
    }

    p, span, div {
        color: #F5F7FA;
    }

    /* Application Header */
    .app-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F5F7FA !important;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .badge-tag {
        font-size: 0.72rem;
        font-weight: 600;
        background: #202532;
        color: #4F8CFF;
        border: 1px solid #303746;
        border-radius: 4px;
        padding: 0.15rem 0.45rem;
        vertical-align: middle;
        margin-left: 0.5rem;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #AAB2C0 !important;
        margin-bottom: 1.5rem;
        line-height: 1.45;
    }

    /* Sidebar Container */
    [data-testid="stSidebar"] {
        background-color: #151922 !important;
        border-right: 1px solid #303746 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }

    /* Sidebar Section Titles */
    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #7F8999 !important;
        margin-top: 1.1rem;
        margin-bottom: 0.45rem;
    }

    /* Status Cards in Sidebar */
    .status-card {
        background: #1B1F2A;
        border: 1px solid #303746;
        border-radius: 8px;
        padding: 0.70rem 0.85rem;
        margin-bottom: 0.5rem;
        transition: all 0.18s ease;
    }
    .status-card:hover {
        transform: translateY(-1px);
        border-color: #4F8CFF;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .status-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.25rem;
    }
    .status-card-title {
        font-size: 0.84rem;
        font-weight: 600;
        color: #F5F7FA !important;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .status-badge {
        font-size: 0.70rem;
        font-weight: 600;
        padding: 0.12rem 0.50rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    .status-badge-ok {
        background: rgba(53, 208, 127, 0.15);
        color: #35D07F !important;
        border: 1px solid rgba(53, 208, 127, 0.4);
    }
    .status-badge-warn {
        background: rgba(245, 185, 66, 0.15);
        color: #F5B942 !important;
        border: 1px solid rgba(245, 185, 66, 0.4);
    }
    .status-badge-err {
        background: rgba(255, 92, 103, 0.15);
        color: #FF5C67 !important;
        border: 1px solid rgba(255, 92, 103, 0.4);
    }
    .status-meta {
        font-size: 0.75rem;
        color: #AAB2C0 !important;
        line-height: 1.3;
        margin-top: 0.2rem;
    }

    /* Database Schema Expanders */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: #1B1F2A !important;
        border: 1px solid #303746 !important;
        border-radius: 8px !important;
        margin-bottom: 0.35rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        color: #F5F7FA !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 0.65rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        color: #4F8CFF !important;
    }

    /* Column Row styling */
    .col-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.76rem;
        padding: 0.22rem 0.1rem;
        border-bottom: 1px solid #202532;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .col-name {
        color: #F5F7FA !important;
        font-weight: 500;
    }
    .col-type {
        color: #AAB2C0 !important;
        font-size: 0.70rem;
        background: #202532;
        padding: 0.05rem 0.35rem;
        border-radius: 4px;
        border: 1px solid #303746;
    }
    .key-badge-pri {
        background: rgba(79, 140, 255, 0.2);
        color: #4F8CFF !important;
        font-weight: 700;
        font-size: 0.65rem;
        padding: 0.05rem 0.25rem;
        border-radius: 3px;
        border: 1px solid rgba(79, 140, 255, 0.4);
        margin-right: 0.25rem;
    }
    .key-badge-mul {
        background: rgba(168, 85, 247, 0.2);
        color: #C084FC !important;
        font-weight: 700;
        font-size: 0.65rem;
        padding: 0.05rem 0.25rem;
        border-radius: 3px;
        border: 1px solid rgba(168, 85, 247, 0.4);
        margin-right: 0.25rem;
    }

    /* Sidebar Buttons (Example Questions) */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1B1F2A !important;
        color: #F5F7FA !important;
        border: 1px solid #303746 !important;
        border-radius: 6px !important;
        font-size: 0.81rem !important;
        font-weight: 500 !important;
        padding: 0.42rem 0.65rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.18s ease !important;
        margin-bottom: 0.25rem !important;
        line-height: 1.35 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #202532 !important;
        border-color: #4F8CFF !important;
        color: #4F8CFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0px) !important;
        background-color: #272E3E !important;
    }

    /* Safety Test Bench Buttons */
    .safety-zone .stButton > button {
        background-color: #1B1F2A !important;
        border: 1px solid rgba(245, 185, 66, 0.35) !important;
        border-left: 3px solid #F5B942 !important;
        color: #F5F7FA !important;
    }
    .safety-zone .stButton > button:hover {
        background-color: #202532 !important;
        border-color: #F5B942 !important;
        border-left: 3px solid #F5B942 !important;
        color: #F5B942 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(245, 185, 66, 0.18) !important;
    }

    /* Question Input Textbox */
    label[data-testid="stWidgetLabel"] p {
        color: #F5F7FA !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stTextInput"] input {
        background-color: #1B1F2A !important;
        color: #F5F7FA !important;
        border: 1px solid #303746 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 0.9rem !important;
        transition: all 0.18s ease !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #4F8CFF !important;
        box-shadow: 0 0 0 2px rgba(79, 140, 255, 0.25) !important;
        color: #FFFFFF !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #7F8999 !important;
    }

    /* Primary Generate Button */
    div.stButton > button[kind="primary"] {
        background: #4F8CFF !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.62rem 1.4rem !important;
        border-radius: 8px !important;
        border: 1px solid #4F8CFF !important;
        box-shadow: 0 2px 8px rgba(79, 140, 255, 0.3) !important;
        transition: all 0.18s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #3A78F2 !important;
        border-color: #3A78F2 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(79, 140, 255, 0.45) !important;
    }
    div.stButton > button[kind="primary"]:active {
        transform: translateY(0px) !important;
    }

    /* Secondary Reset Button */
    div.stButton > button[kind="secondary"] {
        background-color: #1B1F2A !important;
        color: #AAB2C0 !important;
        border: 1px solid #303746 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.62rem 1.0rem !important;
        transition: all 0.18s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #202532 !important;
        color: #F5F7FA !important;
        border-color: #7F8999 !important;
        transform: translateY(-1px) !important;
    }

    /* Code Blocks */
    [data-testid="stCodeBlock"] {
        background-color: #151922 !important;
        border: 1px solid #303746 !important;
        border-radius: 8px !important;
    }
    [data-testid="stCodeBlock"] pre {
        background-color: #151922 !important;
        color: #F5F7FA !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1B1F2A !important;
        border: 1px solid #303746 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #AAB2C0 !important;
        font-size: 0.82rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #F5F7FA !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* Semantic Alerts */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentSuccess"]) {
        background-color: rgba(53, 208, 127, 0.12) !important;
        border: 1px solid #35D07F !important;
        color: #F5F7FA !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentWarning"]) {
        background-color: rgba(245, 185, 66, 0.12) !important;
        border: 1px solid #F5B942 !important;
        color: #F5F7FA !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentError"]) {
        background-color: rgba(255, 92, 103, 0.12) !important;
        border: 1px solid #FF5C67 !important;
        color: #F5F7FA !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentInfo"]) {
        background-color: rgba(79, 140, 255, 0.12) !important;
        border: 1px solid #4F8CFF !important;
        color: #F5F7FA !important;
    }

    /* Caption styling */
    [data-testid="stCaptionContainer"] p {
        color: #AAB2C0 !important;
    }

    /* Divider */
    hr {
        border-color: #303746 !important;
        margin: 1.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Callback Handlers for Buttons ─────────────────────────────────

def set_query(q):
    """Callback when an example question is clicked: loads into input without executing."""
    st.session_state["pending_query_input"] = q
    st.session_state["user_question"] = q
    st.session_state["execute_trigger"] = False


def set_safety_query(q):
    """Callback when an adversarial test is clicked: loads into input and flags for validation."""
    st.session_state["pending_query_input"] = q
    st.session_state["user_question"] = q
    st.session_state["execute_trigger"] = True


def reset_state():
    """Restores clean pristine state without touching DB."""
    st.session_state["pending_query_input"] = ""
    st.session_state["user_question"] = ""
    for k in ["generated_sql", "validation", "query_result", "chart_result", "explanation", "execute_trigger"]:
        st.session_state.pop(k, None)


# ── Sidebar: Configuration, Status, Schema, & Suggestions ─────────

with st.sidebar:
    st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)

    # 1. Database Status Card
    db_ok, db_msg = test_connection()
    if db_ok:
        st.markdown("""
        <div class="status-card">
            <div class="status-card-header">
                <span class="status-card-title">🗄️ Database</span>
                <span class="status-badge status-badge-ok">● Connected</span>
            </div>
            <div class="status-meta">MySQL / MariaDB Server (ai_sales)</div>
        </div>
        """, unsafe_allow_html=True)
        use_demo_db = False
    else:
        st.markdown("""
        <div class="status-card">
            <div class="status-card-header">
                <span class="status-card-title">🗄️ Database</span>
                <span class="status-badge status-badge-warn">● Fallback Active</span>
            </div>
            <div class="status-meta">Local SQLite Mirror (ai_sales.db)</div>
        </div>
        """, unsafe_allow_html=True)
        use_demo_db = True

    # 2. Groq LLM Status Card (API Key completely hidden from UI)
    has_groq_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    if has_groq_key:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-card-header">
                <span class="status-card-title">🔐 Groq LLM</span>
                <span class="status-badge status-badge-ok">● API Configured</span>
            </div>
            <div class="status-meta">Securely loaded from .env ({groq_model})</div>
        </div>
        """, unsafe_allow_html=True)
        use_demo_ai = False
    else:
        st.markdown("""
        <div class="status-card">
            <div class="status-card-header">
                <span class="status-card-title">🔐 Groq LLM</span>
                <span class="status-badge status-badge-err">● Not Configured</span>
            </div>
            <div class="status-meta">Offline Demo Engine active for standard queries</div>
        </div>
        """, unsafe_allow_html=True)
        use_demo_ai = True

    # 3. Tables & Columns UI (Compact Schema Explorer)
    st.markdown('<div class="sidebar-section-title">Database Schema</div>', unsafe_allow_html=True)
    tables = get_table_names()
    if tables:
        for table in tables:
            cols = get_table_columns(table)
            with st.expander(f"🗃️ {table} ({len(cols)} cols)"):
                for col in cols:
                    field = col.get("Field", "")
                    ftype = col.get("Type", "")
                    key = col.get("Key", "")
                    key_tag = ""
                    if key == "PRI":
                        key_tag = '<span class="key-badge-pri">PK</span>'
                    elif key == "MUL":
                        key_tag = '<span class="key-badge-mul">FK</span>'
                    st.markdown(
                        f'<div class="col-row">'
                        f'<span>{key_tag}<span class="col-name">{field}</span></span>'
                        f'<span class="col-type">{ftype}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
    else:
        st.caption("No tables discovered. Check database connection.")

    # 4. Example Queries (Dark Suggestion Cards)
    st.markdown('<div class="sidebar-section-title">Example Queries</div>', unsafe_allow_html=True)
    example_questions = [
        "Show the top 5 customers by total purchase.",
        "What are the top 5 products by sales?",
        "Show total sales by city.",
        "Which product category generated the highest revenue?",
        "Show the total number of orders.",
        "Show monthly sales for 2023.",
        "List customers from Mumbai.",
        "Show products with price above 1000.",
        "Show average order amount.",
        "Show the customer with the highest total purchase.",
    ]
    for idx, eq in enumerate(example_questions):
        st.button(
            f"🔎 {eq}",
            key=f"ex_btn_{idx}",
            on_click=set_query,
            args=(eq,),
            use_container_width=True,
            help="Click to insert this query into the input box"
        )

    # 5. Safety Test Queries (Functional Warning Cards)
    st.markdown('<div class="sidebar-section-title">🛡️ Safety Test Bench</div>', unsafe_allow_html=True)
    safety_questions = [
        "Delete all customers.",
        "Drop the orders table.",
        "Update all product prices to 0.",
    ]
    st.markdown('<div class="safety-zone">', unsafe_allow_html=True)
    for idx, sq in enumerate(safety_questions):
        st.button(
            f"⚠️ {sq}",
            key=f"safe_btn_{idx}",
            on_click=set_safety_query,
            args=(sq,),
            use_container_width=True,
            help="Test SQL Safety Barrier: this destructive operation will be blocked"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. Clear / Reset Action
    st.markdown('<div class="sidebar-section-title">Session Control</div>', unsafe_allow_html=True)
    if st.button(
        "🔄 Clear / Reset Application",
        key="reset_btn",
        use_container_width=True,
        help="Clear current question, results, and reset interface"
    ):
        reset_state()
        st.rerun()


# ── Main Content Area ──────────────────────────────────────────────

st.markdown(
    '<div class="app-title">'
    '🔍 AI SQL Query Generator & Database Assistant'
    '<span class="badge-tag">v1.0.0</span>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="app-subtitle">'
    'Ask analytical questions in conversational English. '
    'The AI writes schema-grounded MySQL SQL, verifies safety barriers, '
    'executes against the database, and provides instant charts and explanations.'
    '</div>',
    unsafe_allow_html=True
)

# ── Query Input Box ────────────────────────────────────────────────

if st.session_state.get("pending_query_input") is not None:
    st.session_state["query_input"] = st.session_state["pending_query_input"]
    st.session_state["pending_query_input"] = None

user_question = st.text_input(
    "💬 Ask your question:",
    key="query_input",
    placeholder="e.g., Show the top 5 customers by total purchase",
    help="Type your question or choose an example from the sidebar."
)

col_run, col_clear = st.columns([4, 1])
with col_run:
    generate_btn = st.button("🚀 Generate SQL & Execute", type="primary", use_container_width=True)
with col_clear:
    if st.button("🔄 Reset", key="main_reset_btn", use_container_width=True):
        reset_state()
        st.rerun()

should_execute = generate_btn or st.session_state.get("execute_trigger", False)

# ── Processing Pipeline ────────────────────────────────────────────

if should_execute:
    # Reset trigger flag so subsequent non-action reruns don't loop
    st.session_state["execute_trigger"] = False
    active_question = user_question.strip() if user_question else st.session_state.get("user_question", "").strip()

    if not active_question:
        st.warning("⚠️ Please enter a question or select an example from the sidebar.")
    else:
        st.session_state["user_question"] = active_question

        # Step 1: Generate SQL via Groq
        with st.spinner("🤖 Generating SQL with Groq AI..."):
            gen_result = generate_sql(
                active_question,
                allow_demo_fallback=use_demo_ai
            )

        if not gen_result["success"]:
            # If the AI refused a destructive/modifying request, capture candidate SQL for validator demonstration
            from demo_mode import match_demo_query
            matched = match_demo_query(active_question)
            if matched and any(kw in matched["sql"].upper() for kw in ["DELETE", "DROP", "UPDATE", "INSERT"]):
                generated_sql = matched["sql"]
            else:
                st.error(f"❌ SQL Generation Failed: {gen_result['error']}")
                st.stop()
        else:
            generated_sql = gen_result["sql"]

        # Display Generated SQL Box
        st.subheader("📝 Generated SQL")
        st.code(generated_sql, language="sql")
        if gen_result.get("model"):
            st.caption(f"Engine: Groq | Model: `{gen_result['model']}`")

        # Step 2: Validate SQL Safety
        st.subheader("🛡️ SQL Safety Validation")
        validation = validate_sql(generated_sql)

        if validation["is_safe"]:
            st.success(f"✅ SAFE — {validation['reason']}")
        else:
            st.error(f"🛡️ BLOCKED — {validation['reason']}")
            st.warning(
                "Unsafe SQL detected. The query was blocked before reaching the database. "
                "Destructive operations (INSERT, UPDATE, DELETE, DROP, ALTER) are strictly prohibited."
            )
            st.stop()

        # Step 3: Execute SQL on MySQL
        st.subheader("📊 Query Results")
        with st.spinner("⏳ Executing query against database..."):
            exec_result = execute_query(validation["sanitized_sql"], allow_fallback=use_demo_db)

        if not exec_result["success"]:
            st.error(f"❌ Execution Error: {exec_result['error']}")
            st.info("💡 Check if the requested table or column exists in the database schema.")
            st.stop()

        df = exec_result["data"]

        # Results Metadata
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Rows Returned", exec_result["row_count"])
        with m_col2:
            st.metric("Execution Latency", f"{exec_result['execution_time']}s")
        with m_col3:
            st.metric("Database Engine", exec_result.get("engine", "MySQL"))

        # Table Display
        if df.empty:
            st.info("ℹ️ The query executed successfully but returned 0 rows.")
        else:
            st.dataframe(df, use_container_width=True)

        # Step 4: Automatic Visualization
        if not df.empty:
            st.subheader("📈 Automatic Visualization")
            chart_result = generate_chart(df)
            if chart_result["has_chart"]:
                import io
                img_buf = io.BytesIO()
                chart_result["figure"].savefig(
                    img_buf,
                    format="png",
                    bbox_inches="tight",
                    dpi=200,
                    facecolor="#1B1F2A",
                    edgecolor="#303746",
                )
                img_buf.seek(0)
                st.image(img_buf)
                st.caption(f"Chart: {chart_result['chart_type'].title()} — {chart_result['reason']}")
            else:
                st.info(f"ℹ️ {chart_result['reason']}")

        # Step 5: SQL Explanation
        st.subheader("💡 SQL Explanation")
        with st.spinner("📖 Generating explanation..."):
            explain_result = explain_sql(
                generated_sql,
                allow_demo_fallback=use_demo_ai
            )

        if explain_result["success"]:
            st.info(explain_result["explanation"])
        else:
            st.warning(f"Could not generate explanation: {explain_result['error']}")

# ── Footer ─────────────────────────────────────────────────────────

st.divider()
st.caption(
    "AI SQL Query Generator & Database Assistant | "
    "Academic Capstone Project | "
    "Python • Streamlit • Groq LLM (openai/gpt-oss-120b) • MySQL (ai_sales)"
)
