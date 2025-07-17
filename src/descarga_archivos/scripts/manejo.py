# src/descarga_archivos/scripts/manejo.py

import os
import time
import zipfile
import pandas as pd
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

# Credenciales desde variables de entorno
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
    origen.replace(destino)  # renombrar
    return pd.read_excel(destino)

def run(playwright: Playwright) -> None:
    # Preparar directorios
    cwd = Path.cwd()
    download_path = cwd / "downloads"
    debug_path = cwd / "debug"
    download_path.mkdir(exist_ok=True)
    debug_path.mkdir(exist_ok=True)
    zip_file = download_path / "Manejo.zip"

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # 1. Login y navegación
    try:
        page.goto("https://academia.farmatodo.com/default", timeout=60_000)
        page.wait_for_selector("input[name='Email / NUMERO IDENTIDAD']", timeout=60_000)
        page.fill("input[name='Email / NUMERO IDENTIDAD']", EMAIL)
        page.fill("input[name='Contraseña']", PASSWORD)
        page.click("text=Entrar")
        page.wait_for_load_state("networkidle", timeout=60_000)

        page.wait_for_selector("#manageIcon", timeout=60_000)
        page.click("#manageIcon")
    except Exception:
        # Dump para debug
        (debug_path / "manejo_login.png").write_bytes(page.screenshot(full_page=True))
        html_debug = debug_path / "manejo_login.html"
        html_debug.write_text(page.content(), encoding="utf-8")
        print(f"Error en login o navegación. Verifica los archivos en {debug_path}.")
        raise

    # 2. Buscar programa
    page.click("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch")
    page.fill("input[placeholder='Escribe aquí para buscar...']", "manejo de planogramas")
    page.click("text=Buscar")
    page.click("text=Programa Manejo de")

    # 3. Generar reporte
    page.click("#courses")
    page.locator("title=Select/Deselect All").get_by_role("checkbox").check()
    page.click("text=Ordenar")
    page.click("button")  # confirmar popup
    page.click("text=Nuevo reporte")
    page.click("#popup-new-report-useractivity-report-icon")

    page.click("#column-date-filter_selectedArea >> text=Último acceso")
    page.click("text=Sin filtros")
    page.click("text=seleccionados")

    # Seleccionar y quitar columnas
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

    # 4. Descargar ZIP
    with page.expect_download() as download_info:
        time.sleep(5)
        page.click("text=Descargar Guardando Guardado")

    download = download_info.value
    download.save_as(str(zip_file))

    # 5. Extraer y renombrar Excel
    df = descomprimir_y_leer_excel(zip_file, download_path, "Manejo")
    if df is not None:
        print(df.head())
    else:
        print("No se encontró archivo Excel en el ZIP.")

    # 6. Guardar sesión y cerrar
    context.storage_state(path="auth.json")
    context.close()
    browser.close()

# Ejecutar como módulo principal
if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)


