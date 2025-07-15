import os
import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
import os
import time
import zipfile
from playwright.sync_api import sync_playwright
import pandas as pd



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
    page.get_by_placeholder("Escribe aquí para buscar...").fill("tendencias")
    page.get_by_placeholder("Escribe aquí para buscar...").press("Enter")
    page.get_by_role("link", name="Programa Tendencias de Cosmé").click()
    page.locator("#courses").click()
    page.locator("#pagerDropdown_grid-container_CareerCourses span").click()
    page.get_by_text("25").click()
    page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
    page.locator("div").filter(has_text=re.compile(r"^Curso 2Obligatorio$")).locator("div").first.click()
    page.locator("div").filter(has_text=re.compile(r"^Curso 3Obligatorio$")).locator("div").first.click()
    page.get_by_role("link", name="Nuevo reporte").click()
    page.locator("#ic_user_activity_report").click()
    page.locator("span").filter(has_text="Último acceso").first.click()
    page.get_by_text("Sin filtros").click()
    page.get_by_text("seleccionados").click()
    page.locator("input[name=\"Identifier\"]").check()
    page.locator("#report-column-dropdown-container div").filter(has_text="VICEPRESIDENCIA").nth(1).click()
    page.locator("input[name=\"Country\"]").check()
    page.locator("input[name=\"UserStatus\"]").check()
    page.locator("input[name=\"Deleted\"]").uncheck()
    page.locator("input[name=\"EnrollmentDate\"]").uncheck()
    page.locator("input[name=\"FirstAccessDate\"]").uncheck()
    page.locator("input[name=\"LastAccessDate\"]").uncheck()
    page.locator("input[name=\"GraduationDate\"]").uncheck()
    page.locator("input[name=\"Satisfaction\"]").uncheck()
    page.locator("input[name=\"Attendance\"]").uncheck()
    page.locator("#report-column-dropdown-container div").filter(has_text="Visitas al curso").nth(1).click()
    page.locator("input[name=\"TimeOnCourse\"]").uncheck()
    page.locator("input[name=\"CompletedContentCount\"]").uncheck()
    page.get_by_role("link", name="Aplicar").click()
    page.locator("a").filter(has_text="Exportar a excel").click()
    with page.expect_download() as download_info:
        page.get_by_text("Descargar Guardando Guardado").click()
    download = download_info.value

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)


