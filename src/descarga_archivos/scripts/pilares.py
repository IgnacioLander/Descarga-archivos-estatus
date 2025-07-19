#!/usr/bin/env python3
# src/descarga_archivos/scripts/pilares_playwright.py

import os
import time
import zipfile
import pandas as pd
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

EMAIL = os.getenv("F_EMAIL")
PASSWORD = os.getenv("F_PASSWORD")

def descomprimir_y_leer_excel(zip_file_path: str, download_path: str, nuevo_nombre: str):
    carpeta_destino = "Escuela de Excelencia"
    destino = Path(download_path) / carpeta_destino
    destino.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(destino)
        extraidos = zip_ref.namelist()

    xlsx = [f for f in extraidos if f.endswith(".xlsx")]
    if not xlsx:
        return None

    original = destino / xlsx[0]
    renombrado = destino / f"{nuevo_nombre}.xlsx"
    original.rename(renombrado)
    return pd.read_excel(renombrado)

def run(playwright: Playwright) -> None:
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    zip_file_path = os.path.join(download_path, "Pilares.zip")

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # — LOGIN (fixed selectors matching the real IDs on /default) —
    page.goto("https://academia.farmatodo.com/default")
    page.locator("input#centerPagetxtEmail").click()
    page.locator("input#centerPagetxtEmail").fill(EMAIL)
    page.locator("input#centerPagetxtPassword").click()
    page.locator("input#centerPagetxtPassword").fill(PASSWORD)
    page.get_by_role("link", name="Entrar").click()

    # — NAVIGATE to “Pilares de la Operación” —
    page.locator("#manageIcon").click()
    page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
    time.sleep(3)
    page.get_by_placeholder("Escribe aquí para buscar...").fill("pilares de la operación")
    page.get_by_role("link", name="Buscar").click()
    page.get_by_role("link", name="Programa Pilares de la Operación | Escuela de Excelencia").click()
    time.sleep(5)

    # — BUILD REPORT —
    page.locator("#courses").click()
    page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#popup-new-report-useractivity-report-icon").click()
    page.locator("span").filter(has_text="Último acceso").first.click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()

    # — COLUMNS SELECTION —
    for col in ["Identifier","Department","EnrolledAs","Country","UserStatus","Progress"]:
        page.locator(f"input[name='{col}']").check()
    for col in [
        "Deleted","EnrollmentDate","FirstAccessDate","LastAccessDate",
        "GraduationDate","Satisfaction","Attendance","CourseAccessCount",
        "TimeOnCourse","CompletedContentCount"
    ]:
        page.locator(f"input[name='{col}']").uncheck()

    page.get_by_role("link", name="Aplicar").click()

    # — EXPORT & DOWNLOAD —
    page.locator("a").filter(has_text="Exportar a excel").click()
    # give the server time to prepare the file
    time.sleep(5)

    with page.expect_download() as download_info:
        page.get_by_text("Descargar Guardando Guardado").click()
    download = download_info.value
    download.save_as(zip_file_path)

    # — UNZIP & READ —
    df = descomprimir_y_leer_excel(zip_file_path, download_path, "Pilares")
    print(df)

    context.storage_state(path="auth.json")
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)
