# src/descarga_archivos/scripts/manejo.py

import os
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

def run(page: Page) -> None:
    """
    Logs into academia.farmatodo.com under the 'Manejo' course context,
    triggers the report download, and reports the saved path.
    """

    # Environment inputs
    email = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv("DOWNLOAD_DIR", "./downloads/Manejo")

    # Sanity checks
    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set in env variables")
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    try:
        print("🚀 Navigating to login page…")
        page.goto("https://academia.farmatodo.com", timeout=60000)

        print("⌛ Waiting for login fields…")
        page.wait_for_selector("input#topMenutxtEmail", timeout=15000)
        page.wait_for_selector("input#topMenutxtContrasena", timeout=15000)

        print("✍️ Filling in credentials…")
        page.fill("input#topMenutxtEmail", email)
        page.fill("input#topMenutxtContrasena", password)

        print("🖱️ Submitting login form…")
        page.click("button:has-text('Iniciar sesión')")

        print("⏳ Waiting for dashboard to stabilize…")
        page.wait_for_load_state("networkidle", timeout=30000)
        print("✅ Login successful")

        # Navigate to the Manejo report section if needed
        # e.g., page.click("a#menu-manejo")

        print("📥 Triggering report download…")
        with page.expect_download() as download_info:
            # Adjust selector to your “Download” button
            page.click("button:has-text('Descargar Informe')")
        download = download_info.value

        # Wait for file to be written, then log its path
        file_path = download.path()
        print(f"✅ File downloaded to: {file_path}")

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        _save_error_state(page, download_dir)
        raise

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        _save_error_state(page, download_dir)
        raise

def _save_error_state(page: Page, download_dir: str) -> None:
    """
    On failure, dump a screenshot and page HTML for diagnostics.
    """
    err_png = Path(download_dir) / "error.png"
    err_html = Path(download_dir) / "error.html"
    try:
        page.screenshot(path=str(err_png), full_page=True)
        with open(err_html, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"🧹 Saved error state to {err_png} and {err_html}")
    except Exception as dump_err:
        print(f"⚠️ Failed to save error artifacts: {dump_err}")
