# src/descarga_archivos/scripts/manejo.py

import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run(playwright):
    F_EMAIL = os.getenv("F_EMAIL", "")
    F_PASSWORD = os.getenv("F_PASSWORD", "")

    if not F_EMAIL or not F_PASSWORD:
        raise ValueError("❌ Las variables de entorno F_EMAIL o F_PASSWORD no están definidas.")

    try:
        print("🚀 Iniciando navegador...")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("🌐 Accediendo a https://academia.farmatodo.com ...")
        page.goto("https://academia.farmatodo.com", timeout=60_000)

        print("⏳ Esperando que cargue el HTML...")
        page.wait_for_load_state("networkidle", timeout=60_000)

        print("🔍 Buscando input de identidad (modo garantizado)...")
        selector_xpath = "//input[contains(@placeholder, 'identidad') or contains(@aria-label, 'identidad') or contains(@name, 'identidad') or contains(@name, 'Email')]"

        try:
            input_locator = page.locator(selector_xpath).first
            input_locator.wait_for(state="visible", timeout=60_000)
            print("✅ Input localizado correctamente.")
        except:
            print("❌ No se encontró el input esperado.")
            guardar_debug(page)
            print("📝 HTML capturado:")
            print(page.content())  # Esto imprime el HTML cargado
            raise Exception("No se encontró el input de login.")

        print("✍️ Llenando formulario de login...")
        input_locator.fill(F_EMAIL)
        page.fill("input[type='password']", F_PASSWORD)
        page.click("button:has-text('Iniciar sesión')")

        print("⏳ Esperando página de inicio...")
        page.wait_for_load_state("networkidle", timeout=30_000)

        if page.query_selector("text=Mi progreso") is None:
            raise Exception("⚠️ Login no exitoso: 'Mi progreso' no detectado.")

        print("✅ Login exitoso. Continuando con el flujo...")

        # Aquí iría tu lógica después del login
        context.close()
        browser.close()

    except PlaywrightTimeoutError as e:
        print("⏱️ Timeout. Guardando estado...")
        guardar_debug(page)
        raise e

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        guardar_debug(page)
        raise e

def guardar_debug(page):
    os.makedirs("debug", exist_ok=True)
    try:
        with open("debug/error_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        page.screenshot(path="debug/error_login.png")
        print("📁 Archivos guardados en /debug")
    except Exception as e:
        print(f"⚠️ Error al guardar archivos de depuración: {e}")

