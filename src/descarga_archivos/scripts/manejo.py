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

        print("🔍 Esperando campo de identidad...")
        page.wait_for_selector("input[name='Email / NUMERO IDENTIDAD']", timeout=60_000)

        print("✍️ Llenando formulario de login...")
        page.fill("input[name='Email / NUMERO IDENTIDAD']", F_EMAIL)
        page.fill("input[name='password']", F_PASSWORD)
        page.click("button:has-text('Iniciar sesión')")

        print("⏳ Esperando que cargue después del login...")
        page.wait_for_load_state("networkidle", timeout=30_000)

        # Validar si realmente entró al dashboard (ajusta este selector según lo que veas)
        if page.query_selector("text=Mi progreso") is None:
            raise Exception("⚠️ No se detectó el texto esperado luego del login. Puede haber fallado el acceso.")

        print("✅ Login exitoso. Continuando con el flujo...")

        # Aquí continúa tu lógica (navegar, descargar, etc.)

        context.close()
        browser.close()

    except PlaywrightTimeoutError as e:
        print("⏱️ Timeout esperando un selector. Capturando estado para depuración...")
        guardar_debug(page)
        raise e

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
        guardar_debug(page)
        raise e


def guardar_debug(page):
    os.makedirs("debug", exist_ok=True)
    try:
        print("🧾 Guardando página HTML...")
        with open("debug/error_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        print("📸 Capturando pantalla...")
        page.screenshot(path="debug/error_login.png")
    except Exception as e:
        print(f"⚠️ Error al guardar archivos de depuración: {e}")
