import os
import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
import os
import time
import zipfile
from playwright.sync_api import sync_playwright
import pandas as pd

def descomprimir_y_leer_excel(zip_file_path, download_path, nuevo_nombre):
    # Descomprimir el archivo ZIP
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(download_path)  # Extraer en la misma carpeta de descargas

    # Obtener el nombre del archivo extraído
    archivos_extraidos = zip_ref.namelist()  # Lista de archivos dentro del ZIP
    archivo_excel = [f for f in archivos_extraidos if f.endswith('.xlsx')]

    if archivo_excel:
        # Asumimos que solo hay un archivo .xlsx
        archivo_excel_path = os.path.join(download_path, archivo_excel[0])
        nuevo_excel_file_path = os.path.join(download_path, nuevo_nombre + '.xlsx')

        # Renombrar el archivo extraído
        os.rename(archivo_excel_path, nuevo_excel_file_path)

        # Leer el archivo Excel renombrado
        df = pd.read_excel(nuevo_excel_file_path)  
        
        return df
    else:
        return None

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://academia.farmatodo.com/default")
    page.get_by_role("textbox", name="Email / NUMERO IDENTIDAD").click()
    page.get_by_role("textbox", name="Email / NUMERO IDENTIDAD").fill("27670903")
    page.get_by_role("textbox", name="Contraseña").click()
    page.get_by_role("textbox", name="Contraseña").fill("27670903")
    page.get_by_role("link", name="Entrar").click()
    page.locator("#manageIcon").click()
    page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
    time.sleep(3)
    page.get_by_placeholder("Escribe aquí para buscar...").fill("servicios")
    page.get_by_role("link", name="Buscar").click()
    page.get_by_role("link", name="Programa Servicios Farmacéuticos | Venezuela - Escuela Comercial").click()
    page.locator("#courses").click()
    page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#ic_user_activity_report").click()
    page.locator("#column-date-filter_selectedArea").get_by_text("Último acceso").click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()
    page.locator("input[name=\"Identifier\"]").check()
    page.locator("input[name=\"EnrolledAs\"]").check()
    page.locator("input[name=\"Department\"]").check()
    page.locator("input[name=\"Country\"]").check()
    page.locator("input[name=\"UserStatus\"]").check()
    page.locator("input[name=\"Deleted\"]").uncheck()
    page.locator("input[name=\"EnrollmentDate\"]").uncheck()
    page.locator("input[name=\"FirstAccessDate\"]").uncheck()
    page.locator("input[name=\"LastAccessDate\"]").uncheck()
    page.locator("input[name=\"GraduationDate\"]").uncheck()
    page.locator("input[name=\"Satisfaction\"]").uncheck()
    page.locator("input[name=\"Progress\"]").uncheck()
    page.locator("input[name=\"Progress\"]").check()
    page.locator("input[name=\"Attendance\"]").uncheck()
    page.locator("input[name=\"CourseAccessCount\"]").uncheck()
    page.locator("input[name=\"TimeOnCourse\"]").uncheck()
    page.locator("input[name=\"CompletedContentCount\"]").uncheck()
    page.get_by_role("link", name="Aplicar").click()
    page.locator("a").filter(has_text="Exportar a excel").click()
    # Wait for the element to be visible and interactable
    time.sleep(120)
    with page.expect_download() as download_info:
        page.get_by_text("Descargar Guardando Guardado").click()
    download = download_info.value
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    zip_file_path = os.path.join(download_path, f"test.zip")
    download.save_as(zip_file_path)  # Confirmación de descarga
    df = descomprimir_y_leer_excel(zip_file_path, download_path, "SF VE")

    # ---------------------
    


with sync_playwright() as playwright:
    run(playwright)
