#!/usr/bin/env python3
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
    # 1) Env vars & download dir
    email    = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")
    download_dir = os.getenv(
        "DOWNLOAD_DIR",
        str(Path.cwd() / "downloads" / "Manejo")
    )
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # 2) Chrome headless + runner flags + download prefs
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1
    })

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=opts
    )
    wait = WebDriverWait(driver, 20)

    try:
        # 3) Go to the EXACT login page
        print("🌐 Navigating to login…")
        driver.get("https://academia.farmatodo.com/default")
        time.sleep(1)

        # 4) Fill email by real ID
        print("⌛ Waiting for email field…")
        email_el = wait.until(
            EC.element_to_be_clickable((By.ID, "centerPagetxtEmail"))
        )
        email_el.clear()
        email_el.send_keys(email)

        # 5) Fill password by real ID
        print("⌛ Waiting for password field…")
        pwd_el = wait.until(
            EC.element_to_be_clickable((By.ID, "centerPagetxtPassword"))
        )
        pwd_el.clear()
        pwd_el.send_keys(password)

        # 6) Click “Entrar”
        print("🖱️ Clicking 'Entrar'…")
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Entrar"))).click()

        # 7) Wait for dashboard to confirm login
        print("⏳ Waiting for dashboard…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
        print("✅ Login successful")

        # 8) Navigate into “Manejo” program
        print("🔎 Opening Manejo program…")
        driver.find_element(By.CSS_SELECTOR, "#manageIcon").click()
        driver.find_element(
            By.CSS_SELECTOR,
            "#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch"
        ).click()

        time.sleep(2)  # let the search box appear
        search = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Escribe aquí para buscar...']"))
        )
        search.clear()
        search.send_keys("Manejo de estatus")       # CHANGE this to your exact program name
        driver.find_element(By.LINK_TEXT, "Buscar").click()

        # 9) Click the exact link for your Manejo course
        link = wait.until(EC.element_to_be_clickable((
            By.LINK_TEXT,
            "Programa Manejo de estatus | Escuela de Excelencia"  # adjust this if needed
        )))
        link.click()
        time.sleep(5)  # let the course page fully load

        # 10) Trigger the download
        print("📥 Triggering report download…")
        dl_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[text()='Descargar Informe']"
        )))
        dl_btn.click()
        print(f"✅ Download dropped into {download_dir}")

    except Exception as e:
        # Save screenshot + HTML for postmortem
        png = Path(download_dir) / "error.png"
        html = Path(download_dir) / "error.html"
        try:
            driver.save_screenshot(str(png))
            with open(html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ Error: {e!r}")
            print(f"🧹 Debug artifacts at {png} + {html}")
        except Exception as dump_err:
            print(f"⚠️ Failed to write artifacts: {dump_err!r}")
        raise

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
