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
    email    = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv("DOWNLOAD_DIR", str(Path.cwd() / "downloads" / "Manejo"))
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # Chrome headless + auto-download config
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
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
        # 1) Go direct to the login endpoint
        print("🌐 Navigating to https://academia.farmatodo.com/default …")
        driver.get("https://academia.farmatodo.com/default")

        # 2) Wait for the email textbox by placeholder
        print("⌛ Waiting for the email field…")
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "input[placeholder='Email / NUMERO IDENTIDAD']"
        )))

        # 3) Fill credentials via placeholder selectors
        print("✍️ Filling credentials…")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Email / NUMERO IDENTIDAD']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Contraseña']").send_keys(password)

        # 4) Submit
        print("🖱️ Clicking 'Entrar'…")
        driver.find_element(By.LINK_TEXT, "Entrar").click()

        # 5) Wait for dashboard nav (adjust selector as needed)
        print("⏳ Waiting for dashboard to load…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))

        # 6) Trigger the Manejo report download
        print("📥 Triggering report download…")
        # adjust this if your actual button text/selector differs
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Descargar Informe']")))
        btn.click()

        print(f"✅ Download should land in: {download_dir}")

    except Exception as e:
        # On any failure, dump a screenshot & HTML for postmortem
        dump_png = Path(download_dir) / "login_error.png"
        dump_html = Path(download_dir) / "login_error.html"
        try:
            driver.save_screenshot(str(dump_png))
            with open(dump_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Encountered error: {e!r}")
            print(f"🧹 Saved debug artifacts: {dump_png} + {dump_html}")
        except Exception as dump_err:
            print(f"⚠️ Failed writing debug artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
