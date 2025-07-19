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

    original = destino / xlsx[0]
    final    = destino / f"{nuevo_nombre}.xlsx"
    original.rename(final)
    return pd.read_excel(final)

def run(playwright: Playwright) -> None:
    # Prepare download folder
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

        print("⏳ Waiting for dashboard…")
        page.wait_for_selector("nav", timeout=30_000)

        print("🔎 Navigating to Pilares program")
        page.locator("#manageIcon").click()
        page.locator("#ctl00_TopMenuControl_TopMenuDesktopControl1_adminOrTeacherSearch").click()
        time.sleep(2)
        page.get_by_placeholder("Escribe aquí para buscar...").fill("pilares de la operación")
        page.get_by_role("link", name="Buscar").click()
        page.get_by_role(
            "link",
            name="Programa Pilares de la Operación | Escuela de Excelencia"
        ).click()
        time.sleep(5)

        print("📑 Building report…")
        page.locator("#courses").click()
        page.get_by_title("Select/Deselect All").get_by_role("checkbox").check()
        page.get_by_role("link", name="Nuevo reporte").click()
        page.locator("#popup-new-report-useractivity-report-icon").click()
        page.locator("span").filter(has_text="Último acceso").first.click()
        page.get_by_text("Sin filtros").click()
        page.get_by_text("seleccionados").click()

        # select/unselect columns as before…
        # for brevity, assume your column logic remains here

        page.get_by_role("link", name="Aplicar").click()
        page.locator("a").filter(has_text="Exportar a excel").click()
        time.sleep(5)

        # Dump page state for debugging BEFORE download
        before_png = Path(download_dir) / "before_download.png"
        before_html= Path(download_dir) / "before_download.html"
        print(f"📋 Saving debug snapshot before download: {before_png.name}, {before_html.name}")
        page.screenshot(path=str(before_png), full_page=True)
        with open(before_html, "w", encoding="utf-8") as f:
            f.write(page.content())

        print("⬇️ Waiting for download to start (up to 2 minutes)…")
        try:
            with page.expect_download(timeout=120_000) as dl_info:
                # ensure we click the exact link that triggers the download
                page.get_by_text("Descargar Guardando Guardado").click()
            download = dl_info.value
            print("✅ Download event fired, saving file…")
            download.save_as(zip_file_path)
        except PWTimeoutError:
            print("❌ Download did not start within 2 minutes!")
            raise

        print("📂 Unzipping & reading Excel")
        df = descomprimir_y_leer_excel(zip_file_path, download_dir, "Pilares")
        print(df.head())

    except Exception as e:
        print("⚠️ Error during Pilares flow:")
        traceback.print_exc()

        # Dump final page state on failure
        err_png  = Path(download_dir) / "error.png"
        err_html = Path(download_dir) / "error.html"
        print(f"🧹 Saving final debug artifacts: {err_png.name}, {err_html.name}")
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
