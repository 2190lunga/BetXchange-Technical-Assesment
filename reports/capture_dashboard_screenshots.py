"""Capture full-page screenshots of each dashboard page at a controlled desktop
viewport, for use in the PowerPoint deck. Run standalone (not via the VS Code
integrated browser) so the viewport is fully controllable.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "dashboard_screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("index.html", "01_executive_overview.png"),
    ("customers.html", "02_customer_behaviour.png"),
    ("products.html", "03_financial_product_mix.png"),
    ("risk.html", "04_risk_concentration.png"),
    ("growth.html", "05_growth_opportunities.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 1100})
    for file_name, out_name in PAGES:
        url = (DASHBOARD_DIR / file_name).resolve().as_uri()
        page.goto(url)
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUTPUT_DIR / out_name), full_page=True)
        print(f"Captured {out_name}")
    browser.close()

print("All screenshots captured successfully.")
