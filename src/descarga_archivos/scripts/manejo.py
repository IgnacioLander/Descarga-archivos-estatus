# src/descarga_archivos/scripts/manejo.py

# src/descarga_archivos/scripts/manejo.py
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run():
    email = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")

    if not email or not password:
        raise Exception("❌ Las credenciales F_EMAIL y F_PASSWORD no están definidas.")

    print("🚀 Iniciando navegador...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 Accediendo a https://academia.farmatodo.com ...")
        page.goto("https://academia.farmatodo.com", timeout=60000)

        try:
            print("🔍 Esperando campo de identidad...")
            page.wait_for_selector("input#topMenutxtEmail", timeout=15000)

            print("⌨️ Ingresando credenciales...")
            page.fill("input#topMenutxtEmail", email)
            page.fill("input#topMenutxtPassword", password)
            page.click("input#btnIngresar")

            print("✅ Login enviado. Esperando redirección...")
            page.wait_for_load_state("networkidle", timeout=20000)

            # Aquí deberías poner la lógica para descargar el archivo
            print("📥 (Ejemplo) Lógica de descarga aquí...")

        except PlaywrightTimeoutError as e:
            print("❌ Timeout esperando un elemento. HTML capturado.")
            with open("page_error.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            raise e
        finally:
            print("🧹 Cerrando navegador.")
            browser.close()
