#!/usr/bin/env python3
# src/descarga_archivos/scripts/manejo_selenium.py

import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

def switch_to_login_frame(driver, wait):
    """
    Loops through all iframes and switches into the first one
    where the email field is present and clickable.
    Returns True if switched, False otherwise.
    """
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"🔍 Found {len(frames)} iframes on page")
    for idx, frame in enumerate(frames):
        try:
            driver.switch_to.frame(frame)
            # test for presence
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input#topMenutxtEmail")
            ))
            print(f"➡️ Switched into iframe #{idx}")
            return True
        except TimeoutException:
            driver.switch_to.default_content()
    print("➡️ No iframe contained the login field; using main document")
    return False

def dismiss_cookie_banner(driver):
    """
    If a cookie banner or modal pops up, try to close it.
    Adjust the selector to match your site’s button.
    """
    try:
        btn = driver.find_element(By.XPATH, "//button[text()='Aceptar']")
        btn.click()
        print("🍪 Closed cookie banner")
        time.sleep(1)
    except NoSuchElementException:
        pass

def run_selenium():
    # 1) Env + download path
    email    = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv(
        "DOWNLOAD_DIR",
        str(Path.cwd() / "downloads" / "Manejo")
    )
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # 2) Headless Chrome + prefs
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
        # 3) Navigate to the login page
        print("🌐 Navigating to https://academia.farmatodo.com/default …")
        driver.get("https://academia.farmatodo.com/default")

        # 4) Dismiss cookie banner if any
        dismiss_cookie_banner(driver)

        # 5) Try iframes for the login form
        switched = switch_to_login_frame(driver, wait)

        # 6) Wait for & fill email
        print("⌛ Waiting for Email field…")
        email_el = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "input#topMenutxtEmail"
        )))
        print("✍️ Filling Email…")
        email_el.clear()
        email_el.click()
        email_el.send_keys(email)

        # 7) Wait for & fill password
        print("⌛ Waiting for Password field…")
        pwd_el = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "input#topMenutxtContrasena"
        )))
        print("✍️ Filling Password…")
        pwd_el.clear()
        pwd_el.click()
        pwd_el.send_keys(password)

        # 8) Submit
        print("🖱️ Clicking 'Iniciar sesión'…")
        login_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[text()='Iniciar sesión']"
        )))
        login_btn.click()

        # 9) Wait for dashboard nav
        print("⏳ Waiting for dashboard to load…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        print("✅ Logged in successfully")

        # 10) Trigger your Manejo report download
        print("📥 Triggering report download…")
        dl_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[text()='Descargar Informe']"
        )))
        dl_btn.click()
        print(f"✅ Download should appear in: {download_dir}")

    except Exception as e:
        # Dump screenshot and HTML for debugging
        png = Path(download_dir) / "login_error.png"
        html = Path(download_dir) / "login_error.html"
        try:
            driver.save_screenshot(str(png))
            with open(html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Error: {e!r}")
            print(f"🧹 Saved artifacts: {png}, {html}")
        except Exception as dump_err:
            print(f"⚠️ Failed saving artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
