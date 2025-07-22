#!/usr/bin/env python3
import os
import time
import zipfile
import pandas as pd
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def descomprimir_y_leer_excel(zip_file_path: str, download_dir: str, nuevo_nombre: str):
    destino = Path(download_dir) / "Escuela de Excelencia"
    destino.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destino)
        extraidos = zip_ref.namelist()

    xlsx = [f for f in extraidos if f.endswith('.xlsx')]
    if not xlsx:
        return None

    src = destino / xlsx[0]
    dst = destino / f"{nuevo_nombre}.xlsx"
    src.rename(dst)
    return pd.read_excel(dst)

def run_selenium():
    # 1. Env & paths
    EMAIL        = os.getenv("F_EMAIL")
    PASSWORD     = os.getenv("F_PASSWORD")
    download_dir = os.getenv("DOWNLOAD_DIR", str(Path.cwd() / "downloads" / "Pilares"))
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    zip_path = str(Path(download_dir) / "Pilares.zip")

    if not EMAIL or not PASSWORD:
        raise RuntimeError("F_EMAIL and F_PASSWORD must be set")

    # 2. Chrome headless + download prefs
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

        # Login
        driver.get("https://academia.farmatodo.com/default")
        wait.until(EC.presence_of_element_located((By.NAME, "Email / NUMERO IDENTIDAD")))
        driver.find_element(By.NAME, "Email / NUMERO IDENTIDAD").send_keys(EMAIL)
        driver.find_element(By.NAME, "Contraseña").send_keys(PASSWORD)
        driver.find_element(By.LINK_TEXT, "Entrar").click()

        # Navigate to “Pilares de la Operación”
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#manageIcon"))).click()
        driver.find_element(By.CSS_SELECTOR,
            "#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch"
        ).click()

        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR,
            "input[placeholder='Escribe aquí para buscar...']"
        ).send_keys("pilares de la operación")
        driver.find_element(By.LINK_TEXT, "Buscar").click()
        driver.find_element(
            By.LINK_TEXT,
            "Programa Pilares de la Operación | Escuela de Excelencia"
        ).click()

        time.sleep(5)
        driver.find_element(By.CSS_SELECTOR, "#courses").click()

        # Select all, create new report, sort by Último acceso
        driver.find_element(By.CSS_SELECTOR, "[title='Select/Deselect All']").click()
        driver.find_element(By.LINK_TEXT, "Nuevo reporte").click()
        driver.find_element(By.CSS_SELECTOR, "#popup-new-report-useractivity-report-icon").click()
        driver.find_element(By.XPATH, "(//span[contains(text(),'Último acceso')])[1]").click()
        driver.find_element(By.XPATH, "//*[text()='Sin filtros']").click()
        driver.find_element(By.XPATH, "//*[text()='seleccionados']").click()

        # Columns selection
        check_cols = ["Identifier","Department","EnrolledAs","Country","UserStatus","Progress"]
        uncheck_cols = [
            "Deleted","EnrollmentDate","FirstAccessDate","LastAccessDate",
            "GraduationDate","Satisfaction","Attendance","CourseAccessCount",
            "TimeOnCourse","CompletedContentCount"
        ]

        for col in check_cols:
            cb = driver.find_element(By.CSS_SELECTOR, f"input[name='{col}']")
            if not cb.is_selected():
                cb.click()
        for col in uncheck_cols:
            cb = driver.find_element(By.CSS_SELECTOR, f"input[name='{col}']")
            if cb.is_selected():
                cb.click()

        driver.find_element(By.LINK_TEXT, "Aplicar").click()
        driver.find_element(By.XPATH, "//a[contains(text(),'Exportar a excel')]").click()

        # Trigger and wait for download
        driver.find_element(By.XPATH, "//*[contains(text(),'Descargar Guardando Guardado')]").click()
        time.sleep(90)

        # Move the .zip to our named path
        zips = list(Path(download_dir).glob("*.zip"))
        if not zips:
            raise FileNotFoundError("No .zip found in download directory")
        latest = max(zips, key=lambda p: p.stat().st_mtime)
        latest.rename(zip_path)

        # Extract & print
        df = descomprimir_y_leer_excel(zip_path, download_dir, "Pilares")
        print(df)

    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium()
