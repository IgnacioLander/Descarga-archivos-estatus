# src/descarga_archivos/scripts/manejo.py

from playwright.sync_api import Playwright
import os

def run(playwright: Playwright):
    import time

    print("🚀 Iniciando navegador...")
    browser = playwright.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    context = browser.new_context()
    page = context.new_page()

    try:
        print("🌐 Accediendo a https://academia.farmatodo.com ...")
        page.goto("https://academia.farmatodo.com", timeout=60000)

        print("⏳ Esperando carga inicial...")
        page.wait_for_timeout(5000)

        print("🛠️ Verificando si hay que abrir el formulario...")
        try:
            page.click("text=Iniciar sesión", timeout=3000)
            print("🖱️ Se hizo clic en 'Iniciar sesión'")
        except:
            print("ℹ️ No se encontró botón 'Iniciar sesión', probablemente ya está visible.")

        print("🔍 Buscando campo de identidad...")
        login_input = page.locator(
            "//input[contains(@id,'txtEmail') or contains(@placeholder,'identidad') or @name='Email / NUMERO IDENTIDAD']"
        ).first
        login_input.wait_for(state="visible", timeout=15000)

        print("✅ Campo visible. Ingresando credenciales...")
        login_input.fill(os.environ["F_EMAIL"])
        page.fill("input[type='password']", os.environ["F_PASSWORD"])

        print("🔐 Haciendo submit...")
        page.click("button:has-text('Iniciar sesión')")

        print("⏳ Esperando navegación post-login...")
        page.wait_for_load_state("networkidle", timeout=15000)
        print("🎉 Login completado correctamente.")

        # Aquí continúa el resto del flujo, si lo necesitas.

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

        debug_dir = "/debug"
        os.makedirs(debug_dir, exist_ok=True)

        screenshot_path = f"{debug_dir}/screenshot.png"
        html_path = f"{debug_dir}/page.html"

        print(f"📸 Capturando pantalla en {screenshot_path}")
        page.screenshot(path=screenshot_path, full_page=True)

        print(f"🧾 Guardando HTML en {html_path}")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())

        raise e

    finally:
        print("🧹 Cerrando navegador.")
        context.close()
        browser.close()

