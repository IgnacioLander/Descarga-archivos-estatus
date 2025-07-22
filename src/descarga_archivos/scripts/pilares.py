#!/usr/bin/env python3
# src/descarga_archivos/scripts/pilares.py

import os
import time
import zipfile
import traceback
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PWTimeoutError
import pandas as pd

EMAIL    = os.getenv("F_EMAIL")
PASSWORD = os.getenv("F_PASSWORD")

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
    download_dir  = os.path.join(os.getcwd(), "downloads", "Pilares")
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    zip_file_path = os.path.join(download_dir, "Pilares.zip")

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page    = context.new_page()

    try:
        print("🌐 Navigating to login page")
        page.goto("https://academia.farmatodo.com/default")
        time.sleep(1)

        print("⌛ Filling login form")
        page.locator("input#centerPagetxtEmail").fill(EMAIL)
        page.locator("input#centerPagetxtPassword").fill(PASSWORD)
        page.get_by_role("link", name="Entrar").click()

        # 1) Handle the intermediate selectmode page if it appears
        if "selectmode" in page.url:
            print("⚙️ Detected selectmode page, choosing mode…")
            # adjust selector to match the button text on that page
            page.wait_for_selector("button:has-text('Profesor')", timeout=10_000)
            page.click("button:has-text('Profesor')")
            time.sleep(1)

        # 2) Wait for the dashboard nav to become visible
        print("⏳ Waiting for dashboard to load…")
        page.wait_for_selector("nav.main-header", state="visible", timeout=30_000)
        print("✅ Dashboard is visible")

        # 3) Navigate into the Pilares program
        print("🔎 Opening Pilares program…")
        page.locator("#manageIcon").click()
        page.locator(
            "#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch"
        ).click()
        time.sleep(3)

        print("🔍 Searching for 'pilares de la operación'")
        page.fill("input[placeholder='Escribe aquí para buscar...']", "pilares de la operación")
        page.get_by_role("link", name="Buscar").click()

        print("📂 Clicking the program link")
        page.get_by_role(
            "link",
            name="Programa Pilares de la Operación | Escuela de Excelencia"
        ).click()
        time.sleep(5)

        # 4) Build the report
        print("📑 Building report")
        page.locator("#courses").click()
        page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
        page.get_by_role("link", name="Nuevo reporte").click()
        page.locator("#popup-new-report-useractivity-report-icon").click()
        page.locator("span").filter(has_text="Último acceso").first.click()
        page.get_by_text("Sin filtros").click()
        page.get_by_text("seleccionados").click()

        # — Column selection —
        to_check = ["Identifier","Department","Country","EnrolledAs"]
        to_uncheck = [
            "Deleted","EnrollmentDate","FirstAccessDate","LastAccessDate",
            "GraduationDate","Satisfaction","Attendance","CourseAccessCount",
            "TimeOnCourse","CompletedContentCount"
        ]
        for col in to_check:
            page.locator(f"input[name='{col}']").check()
        for col in to_uncheck:
            page.locator(f"input[name='{col}']").uncheck()

        page.get_by_role("link", name="Aplicar").click()
        page.locator("a").filter(has_text="Exportar a excel").click()
        time.sleep(5)

        # 5) Dump before-download snapshot for debugging
        before_png  = Path(download_dir) / "before_download.png"
        before_html = Path(download_dir) / "before_download.html"
        print(f"📋 Saving snapshot: {before_png.name}, {before_html.name}")
        page.screenshot(path=str(before_png), full_page=True)
        with open(before_html, "w", encoding="utf-8") as f:
            f.write(page.content())

        # 6) Wait up to 2 minutes for the download event
        print("⬇️ Waiting for download (timeout 2min)…")
        try:
            with page.expect_download(timeout=120_000) as dl_info:
                page.get_by_text("Descargar Guardando Guardado").click()
            download = dl_info.value
            print("✅ Download started, saving file…")
            download.save_as(zip_file_path)
        except PWTimeoutError:
            print("❌ Download did not start within 2 minutes!")
            raise

        # 7) Unzip & read the Excel
        print("📂 Unzipping and reading the Excel file")
        df = descomprimir_y_leer_excel(zip_file_path, download_dir, "Pilares")
        print(df.head())

    except Exception:
        print("⚠️ Error during Pilares flow:")
        traceback.print_exc()

        # final debug artifacts
        err_png  = Path(download_dir) / "error.png"
        err_html = Path(download_dir) / "error.html"
        print(f"🧹 Saving final artifacts: {err_png.name}, {err_html.name}")
        page.screenshot(path=str(err_png), full_page=True)
        with open(err_html, "w", encoding="utf-8") as f:
            f.write(page.content())
        raise

    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)
