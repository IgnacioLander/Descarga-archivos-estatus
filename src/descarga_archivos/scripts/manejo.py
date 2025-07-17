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

        print("⏳ Esperando carga inicial (JavaScript dinámico)...")
        page.wait_for_timeout(5000)

        print("🛠️ Intentando forzar visibilidad del formulario de login...")

        # Intenta hacer clic en algo que muestre el formulario (si aplica)
        try:
            page.click("text=Iniciar sesión", timeout=3000)
            print("🖱️ Se hizo clic en 'Iniciar sesión'")
        except:
            print("ℹ️ No se encontró botón 'Iniciar sesión', posiblemente no es necesario.")

        # Buscar input de login robustamente
        login_input = page.locator("//input[contains(@id,'txtEmail') or contains(@placeholder,'identidad') or @name='Email / NUMERO IDENTIDAD']").first
        print("🔍 Buscando campo de identidad...")
        login_input.wait_for(state="visible", timeout=15000)

        print("✅ Campo visible. Ingresando credenciales...")
        login_input.fill(os.environ["USER_EMAIL"])
        page.fill("input[type='password']", os.environ["USER_PASS"])

        print("🔐 Haciendo submit...")
        page.click("button:has-text('Iniciar sesión')")

        print("⏳ Esperando navegación post-login...")
        page.wait_for_load_state("networkidle", timeout=15000)
        print("🎉 Login completado.")

        # Aquí puedes seguir con el flujo de descarga de archivos, etc.

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

        # Ruta para depuración
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
