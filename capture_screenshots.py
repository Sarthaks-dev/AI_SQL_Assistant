"""
capture_screenshots.py — Real UI Screenshot Capture Script

Navigates to the running Streamlit web application on http://localhost:8501
using headless Chromium via Playwright, executes real user queries and adversarial tests,
and saves high-resolution cropped screenshots directly to docs/screenshots/.
"""

import time
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_ui():
    print("Launching Chromium to capture live Streamlit screenshots...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1350})
        page = context.new_page()

        # 1. Home / Application Screen
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector("input", timeout=25000)
        page.wait_for_timeout(4000)  # Wait for sidebar & widgets to stabilize

        path_home = os.path.join(OUTPUT_DIR, "01_home_screen.png")
        page.screenshot(path=path_home, full_page=False)
        print(f"Captured: {path_home}")

        # 2. Schema Browser (Expand customers table to show columns)
        print("Expanding schema table...")
        try:
            page.locator("summary:has-text('customers')").click()
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Expander click note: {e}")

        path_schema = os.path.join(OUTPUT_DIR, "02_database_schema_sidebar.png")
        page.screenshot(path=path_schema, full_page=False)
        print(f"Captured: {path_schema}")

        # 3. Enter Query: "Show the top 5 customers by total purchase."
        print("Submitting query: Show the top 5 customers by total purchase...")
        inputs = page.locator("input[type='text']")
        # Main query input is the last text input or has placeholder containing 'Ask'
        query_input = page.locator("input[placeholder*='Show the top 5']").first
        if not query_input.is_visible():
            query_input = inputs.last

        query_input.fill("Show the top 5 customers by total purchase.")
        page.wait_for_timeout(1000)

        # Click Generate button
        gen_btn = page.locator("button:has-text('Generate SQL & Execute')").first
        gen_btn.click()

        # Wait for SQL and Results
        page.wait_for_timeout(7000)  # Wait for pipeline to finish

        path_query_results = os.path.join(OUTPUT_DIR, "03_query_results_and_chart.png")
        page.screenshot(path=path_query_results, full_page=True)
        print(f"Captured: {path_query_results}")

        # 4. Capture Unsafe Query Rejection
        print("Testing adversarial query: Delete all customers...")
        query_input.fill("Delete all customers.")
        page.wait_for_timeout(1000)
        gen_btn.click()
        page.wait_for_timeout(5000)

        path_unsafe = os.path.join(OUTPUT_DIR, "04_unsafe_sql_rejection.png")
        page.screenshot(path=path_unsafe, full_page=False)
        print(f"Captured: {path_unsafe}")

        # 5. Capture another analytical query: Show total sales by city.
        print("Testing second analytical query: Show total sales by city...")
        query_input.fill("Show total sales by city.")
        page.wait_for_timeout(1000)
        gen_btn.click()
        page.wait_for_timeout(7000)
        # Scroll down so bar chart and explanation are in view
        page.evaluate("() => { const el = document.querySelector('section.main') || document.querySelector('[data-testid=\"stAppViewContainer\"]'); if(el) el.scrollTop = 600; }")
        page.wait_for_timeout(1500)

        path_city_sales = os.path.join(OUTPUT_DIR, "05_city_sales_barchart.png")
        page.screenshot(path=path_city_sales, full_page=False)
        print(f"Captured: {path_city_sales}")

        browser.close()
        print("All screenshots successfully captured from live application!")

if __name__ == "__main__":
    capture_ui()
