# src/descarga_archivos/scripts/manejo.py

import os
import time
import zipfile
import pandas as pd
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

# Credentials from environment
EMAIL = os.getenv("F_EMAIL")
PASSWORD = os.getenv("F_PASSWORD")

def descomprimir_y_leer_excel(zip_file_path: Path, download_path: Path, nuevo_nombre: str):
    carpeta_destino = "Escuela de Excelencia"
    nueva_carpeta = download_path / carpeta_destino
    nueva_carpeta.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(nueva_carpeta)
        archivos_extraidos = zip_ref.namelist()

    archivo_excel = [f for f in archivos_extraidos if f.endswith('.xlsx')]
    if not archivo_excel:
        return None

    origen = nueva_carpeta / archivo_excel[0]
    destino = nueva_carpeta / f"{nuevo_nombre}.xlsx"
    origen.replace(destino)  # rename
    return pd.read_excel(destino)

def run(playwright: Playwright) -> None:
    # Prepare directories
    cwd = Path.cwd()
    download_path = cwd / "downloads"
    debug_path = cwd / "debug"
    download_path.mkdir(exist_ok=True)
    debug_path.mkdir(exist_ok=True)
    zip_file = download_path / "Manejo.zip"

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 1. Login and navigate to the “Manejo de planogramas” page
    try:
        page.goto("https://academia.farmatodo.com/default")
        page.fill("textbox[name='Email / NUMERO IDENTIDAD']", EMAIL)
        page.fill("textbox[name='Contraseña']", PASSWORD)
        page.click("text=Entrar")
        page.wait_for_load_state("networkidle", timeout=60_000)

        page.wait_for_selector("#manageIcon", timeout=60_000)
        page.click("#manageIcon")
    except Exception:
        # Dump HTML & screenshot for debugging
        (debug_path / "manejo_login.png").write_bytes(page.screenshot(full_page=True))
        html_debug = debug_path / "manejo_login.html"
        html_debug.write_text(page.content(), encoding="utf-8")
        print(f"Login/navigation failed. See {debug_path} for artifacts.")
        raise

    # 2. Search for “manejo de planogramas”
    page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
    page.fill("input[placeholder='Escribe aquí para buscar...']", "manejo de planogramas")
    page.click("text=Buscar")
    page.click("text=Programa Manejo de")

    # 3. Build the report
    page.click("#courses")
    page.locator("title=Select/Deselect All").get_by_role("checkbox").check()
    page.click("text=Ordenar")
    page.click("button")  # confirm any popup
    page.click("text=Nuevo reporte")
    page.click("#popup-new-report-useractivity-report-icon")

    page.click("#column-date-filter_selectedArea >> text=Último acceso")
    page.click("text=Sin filtros")
    page.click("text=seleccionados")

    # Select & unselect columns
    for col in ["Identifier", "Department", "Country", "UserStatus", "EnrolledAs"]:
        page.locator(f"input[name=\"{col}\"]").check()
    for col in [
        "Deleted", "EnrollmentDate", "FirstAccessDate", "LastAccessDate",
        "GraduationDate", "Satisfaction", "Attendance",
        "CourseAccessCount", "TimeOnCourse", "CompletedContentCount"
    ]:
        page.locator(f"input[name=\"{col}\"]").uncheck()
    page.locator("input[name=\"Progress\"]").check()

    page.click("text=Aplicar")
    page.locator("a:has-text('Exportar a excel')").click()

    # 4. Download the ZIP
    with page.expect_download() as download_info:
        time.sleep(10)  # give the page a moment to prepare the link
        page.click("text=Descargar Guardando Guardado")
    download = download_info.value
    download.save_as(str(zip_file))

    # 5. Extract & rename the Excel inside the zip
    df = descomprimir_y_leer_excel(zip_file, download_path, "Manejo")
    if df is not None:
        print(df.head())
    else:
        print("No Excel file found in the downloaded ZIP.")

    # 6. Persist auth state and clean up
    context.storage_state(path="auth.json")
    context.close()
    browser.close()

# Allow standalone execution for local testing
if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)
