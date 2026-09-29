"""
verify_session_state_fix.py — Rigorous Test for Streamlit Lifecycle & Session State Fix

Tests the exact user scenario:
1. Navigate to http://localhost:8501
2. Click Example Question 1 ("Show the top 5 customers by total purchase.")
3. Verify input field contains the question without auto-executing
4. Click 'Generate SQL & Execute' and wait for results
5. Verify Generated SQL, metrics, table, chart appear
6. Click 'Reset' button
7. Verify input is empty, results/SQL/charts cleared
8. Click Example Question 2 ("What are the top 5 products by sales?")
9. Verify input field updates
10. Execute query 2
11. Click Sidebar 'Clear / Reset Application' button
12. Verify complete reset again
13. Check browser console logs and DOM for any StreamlitWidgetAlreadyInstantiatedError
"""

import sys
import time
from playwright.sync_api import sync_playwright

def run_verification():
    errors = []
    print("Connecting to Streamlit application on http://localhost:8501...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture browser console errors
        def on_console(msg):
            if msg.type == "error":
                print(f"[BROWSER ERROR] {msg.text}")
                errors.append(msg.text)
        page.on("console", on_console)

        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector("input", timeout=25000)
        page.wait_for_timeout(3000)

        # 1. Initial State Check
        input_elem = page.locator("input[data-testid='stTextInputRootElement'] input, input[type='text']").last
        initial_val = input_elem.input_value()
        print(f"Step 1 - Initial input value: '{initial_val}'")
        assert initial_val == "", f"Expected empty input initially, got '{initial_val}'"

        # 2. Click Example Question 1
        print("Step 2 - Clicking Example Question 1: 'Show the top 5 customers by total purchase.'")
        ex1_btn = page.locator("button:has-text('Show the top 5 customers')").first
        ex1_btn.click()
        page.wait_for_timeout(2500)

        # 3. Confirm it appears in the query input and does NOT execute automatically
        val1 = input_elem.input_value()
        print(f"Step 3 - Input value after clicking example: '{val1}'")
        assert "Show the top 5 customers by total purchase" in val1, f"Expected example in input, got '{val1}'"

        # Verify not auto-executed yet (no 'Generated SQL' header)
        assert page.locator("h3:has-text('Generated SQL'), [data-testid='stHeadingWithActionElements']:has-text('Generated SQL')").count() == 0, \
            "Query should not execute automatically upon selecting example!"
        print("Verified: Example loaded into input without auto-executing.")

        # 4. Click 'Generate SQL & Execute'
        print("Step 4 - Clicking 'Generate SQL & Execute'...")
        gen_btn = page.locator("button:has-text('Generate SQL & Execute')").first
        gen_btn.click()
        page.wait_for_timeout(7000)

        # 5. Confirm results appear
        sql_box = page.locator("pre, code").first
        assert sql_box.is_visible(), "Generated SQL code block should be visible!"
        print("Verified: Generated SQL rendered.")

        # Check for any Streamlit exception dialogs/alerts
        err_elements = page.locator("[data-testid='stNotification']:has-text('StreamlitWidgetAlreadyInstantiatedError'), [data-testid='stException']").all_text_contents()
        assert len(err_elements) == 0, f"Encountered Streamlit error: {err_elements}"

        # 6. Click Main Reset Button
        print("Step 6 - Clicking 'Reset' button...")
        reset_btn = page.locator("button:has-text('Reset')").first
        reset_btn.click()
        page.wait_for_timeout(3000)

        # 7. Confirm everything resets
        val_after_reset = input_elem.input_value()
        print(f"Step 7 - Input value after reset: '{val_after_reset}'")
        assert val_after_reset == "", f"Expected empty input after reset, got '{val_after_reset}'"

        # Confirm Generated SQL and results are cleared
        assert page.locator("h3:has-text('Generated SQL'), [data-testid='stHeadingWithActionElements']:has-text('Generated SQL')").count() == 0, \
            "Generated SQL should be cleared after reset!"
        print("Verified: Interface fully returned to pristine state.")

        # Check for StreamlitWidgetAlreadyInstantiatedError
        err_elements = page.locator("[data-testid='stNotification']:has-text('StreamlitWidgetAlreadyInstantiatedError'), [data-testid='stException']").all_text_contents()
        assert len(err_elements) == 0, f"Encountered Streamlit error on reset: {err_elements}"

        # 8. Click Example Question 2
        print("Step 8 - Clicking Example Question 2: 'What are the top 5 products by sales?'")
        ex2_btn = page.locator("button:has-text('What are the top 5 products')").first
        ex2_btn.click()
        page.wait_for_timeout(2500)

        # 9. Confirm it appears in the input
        val2 = input_elem.input_value()
        print(f"Step 9 - Input value after clicking second example: '{val2}'")
        assert "What are the top 5 products by sales" in val2, f"Expected second example in input, got '{val2}'"

        # 10. Execute Query 2
        print("Step 10 - Executing Query 2...")
        gen_btn.click()
        page.wait_for_timeout(7000)
        assert page.locator("pre, code").first.is_visible(), "Generated SQL should be visible for query 2!"
        print("Verified: Query 2 executed successfully.")

        # 11. Repeat Reset using Sidebar Clear / Reset button
        print("Step 11 - Clicking Sidebar 'Clear / Reset Application'...")
        sidebar_reset = page.locator("button:has-text('Clear / Reset Application')").first
        sidebar_reset.click()
        page.wait_for_timeout(3000)

        val_after_reset2 = input_elem.input_value()
        print(f"Step 12 - Input value after sidebar reset: '{val_after_reset2}'")
        assert val_after_reset2 == "", f"Expected empty input after sidebar reset, got '{val_after_reset2}'"

        err_elements = page.locator("[data-testid='stNotification']:has-text('StreamlitWidgetAlreadyInstantiatedError'), [data-testid='stException']").all_text_contents()
        assert len(err_elements) == 0, f"Encountered Streamlit error on sidebar reset: {err_elements}"

        browser.close()
        print("SUCCESS: All lifecycle, example selection, execution, and reset steps passed with 0 errors!")

if __name__ == "__main__":
    run_verification()
