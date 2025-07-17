import os
import time
import zipfile
import pandas as pd
from playwright.sync_api import Playwright

# Credentials from environment
EMAIL = os.getenv("F_EMAIL")
PASSWORD = os.getenv("F_PASSWORD")

def descomprimir_y_leer_excel(zip_file_path, download_path, nuevo_nombre):
    carpeta_destino = "Escuela de Excelencia"
    nueva_carpeta = os.path.join(download_path, carpeta_destino)
    os.makedirs(nueva_carpeta, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(nueva_carpeta)
        archivos_extraidos = zip_ref.namelist()

    archivo_excel = [f for f in archivos_extraidos if f.endswith('.xlsx')]
    if not archivo_excel:
        return None

    archivo_excel_path = os.path.join(nueva_carpeta, archivo_excel[0])
    nuevo_excel_file_path = os.path.join(nueva_carpeta, f"{nuevo_nombre}.xlsx")
    os.rename(archivo_excel_path, nuevo_excel_file_path)
    return pd.read_excel(nuevo_excel_file_path)

def run(playwright: Playwright) -> None:
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    zip_file_path = os.path.join(download_path, "Manejo.zip")

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("https://academia.farmatodo.com/default")
    page.get_by_role("textbox", name="Email / NUMERO IDENTIDAD").fill(EMAIL)
    page.get_by_role("textbox", name="Contraseña").fill(PASSWORD)
    page.get_by_role("link", name="Entrar").click()

    # Navigate to “Manejo de planogramas”
    page.locator("#manageIcon").click()
    time.sleep(5)
    page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
    page.get_by_placeholder("Escribe aquí para buscar...").fill("manejo de planogramas")
    page.get_by_role("link", name="Buscar").click()
    page.get_by_role("link", name="Programa Manejo de").click()

    # Build report
    page.locator("#courses").click()
    page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
    page.get_by_role("link", name="Ordenar").click()
    page.get_by_role("button").click()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#popup-new-report-useractivity-report-icon").click()
    page.locator("#column-date-filter_selectedArea").get_by_text("Último acceso").click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()

    # Columns selection
    for col in ["Identifier","Department","Country","UserStatus","EnrolledAs"]:
        page.locator(f"input[name=\"{col}\"]").check()
    for col in ["Deleted","EnrollmentDate","FirstAccessDate","LastAccessDate",
                "GraduationDate","Satisfaction","Attendance",
                "CourseAccessCount","TimeOnCourse","CompletedContentCount"]:
        page.locator(f"input[name=\"{col}\"]").uncheck()
    page.locator("input[name=\"Progress\"]").check()

    page.get_by_role("link", name="Aplicar").click()
    page.locator("a").filter(has_text="Exportar a excel").click()

    # Download
    with page.expect_download() as download_info:
        time.sleep(90)
        page.get_by_text("Descargar Guardando Guardado").click()
    download = download_info.value
    download.save_as(zip_file_path)

    # Extract & rename
    df = descomprimir_y_leer_excel(zip_file_path, download_path, "Manejo")
    print(df)

    context.storage_state(path="auth.json")
    context.close()
    browser.close()
