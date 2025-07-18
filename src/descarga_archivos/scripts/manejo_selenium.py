# src/descarga_archivos/scripts/manejo_selenium.py

import os
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
    download_dir = os.getenv("DOWNLOAD_DIR", "./downloads/Manejo")
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if not email or not password:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # Headless Chrome + auto-download config
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

    try:
        wait = WebDriverWait(driver, 20)

        print("🌐 Navigating to login page…")
        driver.get("https://academia.farmatodo.com")

        print("⌛ Waiting for login fields…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#topMenutxtEmail")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#topMenutxtContrasena")))

        print("✍️ Filling in credentials…")
        driver.find_element(By.CSS_SELECTOR, "#topMenutxtEmail").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "#topMenutxtContrasena").send_keys(password)

        print("🖱️ Clicking 'Iniciar sesión'…")
        driver.find_element(By.XPATH, "//button[text()='Iniciar sesión']").click()

        print("⏳ Waiting for dashboard…")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))

        print("📥 Triggering report download…")
        download_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[text()='Descargar Informe']")))
        download_btn.click()

        print(f"✅ Download triggered into {download_dir}")

    finally:
        driver.quit()
