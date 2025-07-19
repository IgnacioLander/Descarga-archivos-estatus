#!/usr/bin/env python3
# src/descarga_archivos/scripts/pilares_playwright.py

import os
import time
import zipfile
import subprocess
from pathlib import Path
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright

EMAIL    = os.getenv("F_EMAIL")
PASSWORD = os.getenv("F_PASSWORD")
DRIVE_Uploader = "src/descarga_archivos/upload_to_drive.py"

def descomprimir_y_leer_excel(zip_file_path: str, download_path: str, nuevo_nombre: str):
    destino = Path(download_path) / "Escuela de Excelencia"
    destino.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, "r") as z:
        z.extractall(destino)
        archivos = z.namelist()

    xlsx = [f for f in archivos if f.endswith(".xlsx")]
    if not xlsx:
        return None

    origen = destino / xlsx[0]
    final  = destino / f"{nuevo_nombre}.xlsx"
    origen.rename(final)
    return pd.read_excel(final)

def run(playwright: Playwright) -> None:
    download_dir   = os.path.join(os.getcwd(), "downloads", "Pilares")
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    zip_file_path  = os.path.join(download_dir, "Pilares.zip")

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page    = context.new_page()

    # — LOGIN (using the real #centerPagetxtEmail / #centerPagetxtPassword) —
    page.goto("https://academia.farmatodo.com/default")
    page.locator("input#centerPagetxtEmail").fill(EMAIL)
    page.locator("input#centerPagetxtPassword").fill(PASSWORD)
    page.get_by_role("link", name="Entrar").click()

    # — NAVIGATE to “Pilares” program —
    page.locator("#manageIcon").click()
    page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
    time.sleep(3)
    page.get_by_placeholder("Escribe aquí para buscar...").fill("pilares de la operación")
    page.get_by_role("link", name="Buscar").click()
    page.get_by_role(
        "link",
        name="Programa Pilares de la Operación | Escuela de Excelencia"
    ).click()
    time.sleep(5)

    # — BUILD & EXPORT REPORT —
    page.locator("#courses").click()
    page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#popup-new-report-useractivity-report-icon").click()
    page.locator("span").filter(has_text="Último acceso").first.click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()

    # select columns…
    # (your existing selector logic here)

    page.get_by_role("link", name="Aplicar").click()
    page.locator("a").filter(has_text="Exportar a excel").click()
    time.sleep(5)  # let the server prep it

    # — WAIT UP TO 10 MIN FOR THE DOWNLOAD EVENT —
    with page.expect_download(timeout=600_000) as dl_info:
        page.get_by_text("Descargar Guardando Guardado").click()
    download = dl_info.value
    download.save_as(zip_file_path)

    # — UNZIP & READ —
    df = descomprimir_y_leer_excel(zip_file_path, download_dir, "Pilares")
    print(df)

    # — UPLOAD TO GOOGLE DRIVE —
    subprocess.run([
        "python", DRIVE_Uploader, zip_file_path
    ], check=True)

    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)
