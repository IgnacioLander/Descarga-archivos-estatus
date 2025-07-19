#!/usr/bin/env python3
# src/descarga_archivos/scripts/manejo_selenium.py

import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_selenium():
    """
    Logs into academia.farmatodo.com under the 'Manejo' context,
    clicks 'Descargar Informe' and lets Chrome drop the .xlsx into DOWNLOAD_DIR.
    """
    # 1) Read credentials and download directory from env
    email        = os.getenv("F_EMAIL")
    password     = os.getenv("F_PASSWORD")
    download_dir = os.getenv(
        "DOWNLOAD_DIR",
        str(Path.cwd() / "downloads" / "Manejo")
    )
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # 2) Launch headless Chrome with proper flags + download prefs
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1
    })

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_opts
    )
    wait = WebDriverWait(driver, 20)

    try:
        # 3) Navigate to the exact login page
        print("🌐 Navigating to login page…")
        driver.get("https://academia.farmatodo.com/default")
        time.sleep(1)  # allow any JS to finish

        # 4) Fill in Email by its real ID
        print("⌛ Waiting for email field…")
        email_el = wait.until(
            EC.element_to_be_clickable((By.ID, "centerPagetxtEmail"))
        )
        email_el.clear()
        email_el.send_keys(email)

        # 5) Fill in Password by its real ID
        print("⌛ Waiting for password field…")
        pwd_el = wait.until(
            EC.element_to_be_clickable((By.ID, "centerPagetxtPassword"))
        )
        pwd_el.clear()
        pwd_el.send_keys(password)

        # 6) Click "Entrar"
        print("🖱️ Clicking 'Entrar'…")
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Entrar"))).click()

        # 7) Wait for dashboard nav to prove login succeeded
        print("⏳ Waiting for dashboard…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        print("✅ Login successful")

        # 8) Trigger the Manejo report download
        print("📥 Triggering report download…")
        dl_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Descargar Informe']"))
        )
        dl_btn.click()

        print(f"✅ Download should appear in {download_dir}")

    except Exception as e:
        # On failure, dump screenshot + HTML for debugging
        png_path = Path(download_dir) / "login_error.png"
        html_path = Path(download_dir) / "login_error.html"
        try:
            driver.save_screenshot(str(png_path))
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Error during login/download: {e!r}")
            print(f"🧹 Debug artifacts saved at {png_path}, {html_path}")
        except Exception as dump_err:
            print(f"⚠️ Failed to write debug artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()


if __name__ == "__main__":
    run_selenium()
