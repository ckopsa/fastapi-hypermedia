from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_extra_http_headers({"Accept": "text/html"})

    # 1. Start on the index page
    page.goto("http://127.0.0.1:8000/")
    page.wait_for_selector("#idle-state")

    # 2. Open the HUD
    page.keyboard.press("Space")
    page.wait_for_selector("#hud-filter-input")

    # Check input has aria-label
    aria_label = page.locator("#hud-filter-input").get_attribute("aria-label")
    print(f"HUD Filter Input aria-label: {aria_label}")

    # 3. Open a record
    # Arrow down past Search Protocols to first Write Operations or Data Record
    # Instead, we can just type 'workflow' and hit enter
    page.keyboard.type("workflow")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    # Check if a new page loaded or a record opened
    page.wait_for_timeout(2000)

    page.screenshot(path="verification.png")
    browser.close()