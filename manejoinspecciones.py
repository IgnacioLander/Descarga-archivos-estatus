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
    # Nombre de la nueva carpeta
    carpeta_destino = "Formaciones Asincronas"
    
    # Crear la nueva carpeta si no existe
    nueva_carpeta = os.path.join(download_path, carpeta_destino)
    os.makedirs(nueva_carpeta, exist_ok=True)

    # Descomprimir el archivo ZIP en la nueva carpeta
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(nueva_carpeta)  # Extraer en la nueva carpeta

    # Obtener el nombre del archivo extraído
    archivos_extraidos = zip_ref.namelist()  # Lista de archivos dentro del ZIP
    archivo_excel = [f for f in archivos_extraidos if f.endswith('.xlsx')]

    if archivo_excel:
        # Asumimos que solo hay un archivo .xlsx
        archivo_excel_path = os.path.join(nueva_carpeta, archivo_excel[0])
        nuevo_excel_file_path = os.path.join(nueva_carpeta, nuevo_nombre + '.xlsx')

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
    page.get_by_placeholder("Escribe aquí para buscar...").fill("manejo de inspecciones")
    page.get_by_role("link", name="Buscar").click()
    page.get_by_role("checkbox").nth(1).check()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#popup-new-report-useractivity-report-icon").click()
    page.locator("span").filter(has_text="Último acceso").first.click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()
    page.locator("input[name=\"Identifier\"]").check()
    page.locator("input[name=\"Department\"]").check()
    page.locator("input[name=\"Country\"]").check()
    page.locator("input[name=\"UserStatus\"]").check()
    page.locator("input[name=\"EnrolledAs\"]").check()
    page.locator("input[name=\"Deleted\"]").uncheck()
    page.locator("input[name=\"EnrollmentDate\"]").uncheck()
    page.locator("input[name=\"FirstAccessDate\"]").uncheck()
    page.locator("input[name=\"LastAccessDate\"]").uncheck()
    page.locator("input[name=\"GraduationDate\"]").uncheck()
    page.locator("input[name=\"Satisfaction\"]").uncheck()
    page.locator("input[name=\"Attendance\"]").uncheck()
    page.locator("input[name=\"CourseAccessCount\"]").uncheck()
    page.locator("input[name=\"TimeOnCourse\"]").uncheck()
    page.locator("input[name=\"CompletedContentCount\"]").uncheck()
    page.get_by_role("link", name="Aplicar").click()
    page.locator("a").filter(has_text="Exportar a excel").click()
    
    
    # Esperar a que el botón de descarga esté visible y hacer clic
    with page.expect_download() as download_info:
        # Wait for the element to be visible and interactable
        time.sleep(90)  # Esperar a que la página se actualice
        page.wait_for_selector("text=Descargar Guardando Guardado", timeout=10000)
        page.get_by_text("Descargar Guardando Guardado").click()
    download = download_info.value
    
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    zip_file_path = os.path.join(download_path, f"test.zip")
    download.save_as(zip_file_path)  # Confirmación de descarga
    df = descomprimir_y_leer_excel(zip_file_path, download_path, "manejo de inspecciones")
    print(df)  # Mostrar el DataFrame
    
    # Cerrar el navegador y el contexto
    context.storage_state(path="auth.json")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
    