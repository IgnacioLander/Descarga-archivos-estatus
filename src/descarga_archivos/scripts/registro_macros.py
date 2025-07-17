import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://drive.google.com/drive/folders/0AAjNTltlHaksUk9PVA")
    page.locator("div").filter(has_text=re.compile(r"^NUEVOS INGRESOS$")).first.dblclick()
    with page.expect_popup() as page1_info:
        page.get_by_label("Copia2 de NUEVOS INGRESOS-").dblclick()
    page1 = page1_info.value
    page1.goto("https://docs.google.com/spreadsheets/d/14yl7fxIm6ly_lOG8N4SNhOWCDp6mDL03IgJcyrrsJS4/edit?gid=1585319799#gid=1585319799")
    page.goto("https://drive.google.com/drive/folders/0AAjNTltlHaksUk9PVA")
    page.locator("div").filter(has_text=re.compile(r"^ESTATUS ESCUELA COMERCIAL$")).first.dblclick()
    page.get_by_label("No hay archivos en esta").click(button="right")
    page.get_by_label("Subir archivo", exact=True).click()
    page.locator("c-wiz").filter(has_text=re.compile(r"^Suelta los archivos aquío usa el botón \"Nuevo\"\.$")).set_input_files("Nómina Empleados Octubre 2024 SS (2).xlsx")
    with page.expect_popup() as page2_info:
        page.locator("div").filter(has_text=re.compile(r"^Nómina Empleados Octubre 2024 SS \(2\)\.xlsx$")).first.click()
    page2 = page2_info.value
    page2.goto("https://docs.google.com/spreadsheets/d/1D7IhCq_y2C_DUjPUzxIvx6muCmpEJehc/edit?gid=1685832894#gid=1685832894")
    page2.locator("#waffle-rich-text-editor").click()
    with page2.expect_popup() as page3_info:
        page2.get_by_label("Guardar como Hojas de cálculo").click()
    page3 = page3_info.value
    page3.goto("https://docs.google.com/spreadsheets/d/1skMdQMAO0A82MuOVve-lAyUdT1j9bg33le_yGl5j-WA/edit?gid=1685832894#gid=1685832894")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)