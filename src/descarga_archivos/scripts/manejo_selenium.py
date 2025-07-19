#!/usr/bin/env python3
# src/descarga_archivos/scripts/manejo_selenium.py

import os
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_selenium():
    #–– 1) Env vars & paths
    email    = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv("DOWNLOAD_DIR",
                              str(Path.cwd() / "downloads" / "Manejo"))
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    #–– 2) Chrome headless + window size + download prefs
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
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
        #–– 3) Navigate
        print("🌐 Navigating to login…")
        driver.get("https://academia.farmatodo.com/default")

        #–– 4) Wait for & fill email
        print("⌛ Waiting for Email field…")
        email_el = wait.until(EC.element_to_be_clickable((
            By.NAME, "Email / NUMERO IDENTIDAD"
        )))
        print("✍️ Filling Email…")
        email_el.clear()
        email_el.click()
        email_el.send_keys(email)

        #–– 5) Wait for & fill password
        print("⌛ Waiting for Password field…")
        pwd_el = wait.until(EC.element_to_be_clickable((
            By.NAME, "Contraseña"
        )))
        print("✍️ Filling Password…")
        pwd_el.clear()
        pwd_el.click()
        pwd_el.send_keys(password)

        #–– 6) Submit form
        print("🖱️ Clicking 'Entrar'…")
        login_btn = wait.until(EC.element_to_be_clickable((
            By.LINK_TEXT, "Entrar"
        )))
        login_btn.click()

        #–– 7) Wait for dashboard
        print("⏳ Waiting for dashboard…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        print("✅ Logged in successfully")

        #–– 8) Trigger download
        print("📥 Triggering report download…")
        dl_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[text()='Descargar Informe']"
        )))
        dl_btn.click()
        print(f"✅ Download should appear in {download_dir}")

    except Exception as e:
        # Dump a screenshot + HTML for debugging
        dump_png  = Path(download_dir) / "login_error.png"
        dump_html = Path(download_dir) / "login_error.html"
        try:
            driver.save_screenshot(str(dump_png))
            with open(dump_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Error: {e!r}")
            print(f"🧹 Saved artifacts at {dump_png} + {dump_html}")
        except Exception as dump_err:
            print(f"⚠️ Could not save artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
