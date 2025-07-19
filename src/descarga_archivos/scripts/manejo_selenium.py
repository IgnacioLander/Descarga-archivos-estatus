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
    Logs into academia.farmatodo.com, triggers the 'Manejo' report download,
    and saves the file into DOWNLOAD_DIR.
    """
    # 1) Read env vars
    email    = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv(
        "DOWNLOAD_DIR",
        str(Path.cwd() / "downloads" / "Manejo")
    )
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # 2) Configure headless Chrome with download prefs
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
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
        # 3) Navigate to the login page
        print("🌐 Navigating to https://academia.farmatodo.com/default …")
        driver.get("https://academia.farmatodo.com/default")

        # 4) Dismiss cookie banner if present
        try:
            btn = driver.find_element(By.XPATH, "//button[text()='Aceptar']")
            btn.click()
            print("🍪 Closed cookie banner")
            time.sleep(1)
        except Exception:
            pass

        # 5) Wait for & fill the email field
        print("⌛ Waiting for email field…")
        email_el = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "input[placeholder='Email / NUMERO IDENTIDAD']"
        )))
        email_el.clear()
        email_el.click()
        email_el.send_keys(email)

        # 6) Wait for & fill the password field
        print("⌛ Waiting for password field…")
        pwd_el = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "input[placeholder='Contraseña']"
        )))
        pwd_el.clear()
        pwd_el.click()
        pwd_el.send_keys(password)

        # 7) Submit the form
        print("🖱️ Clicking 'Entrar'…")
        login_btn = wait.until(EC.element_to_be_clickable((
            By.LINK_TEXT, "Entrar"
        )))
        login_btn.click()

        # 8) Wait for the dashboard to appear
        print("⏳ Waiting for dashboard…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        print("✅ Logged in successfully")

        # 9) Trigger the Manejo report download
        print("📥 Triggering report download…")
        dl_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[text()='Descargar Informe']"
        )))
        dl_btn.click()
        print(f"✅ Download should appear in: {download_dir}")

    except Exception as e:
        # 10) On error, save a screenshot and HTML for debugging
        dump_png  = Path(download_dir) / "login_error.png"
        dump_html = Path(download_dir) / "login_error.html"
        try:
            driver.save_screenshot(str(dump_png))
            with open(dump_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Error: {e!r}")
            print(f"🧹 Saved artifacts: {dump_png}, {dump_html}")
        except Exception as dump_err:
            print(f"⚠️ Failed to save debug artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
