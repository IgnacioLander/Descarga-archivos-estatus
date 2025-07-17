import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run_manejo():
    email = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")

    print("🛠️ Iniciando proceso de login a academia.farmatodo.com...")

    if not email or not password:
        print("❌ ERROR: F_EMAIL o F_PASSWORD no están definidas como variables de entorno.")
        return

    with sync_playwright() as playwright:
        print("🚀 Lanzando navegador Chromium en modo headless...")
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("🌐 Navegando a https://academia.farmatodo.com ...")
            page.goto("https://academia.farmatodo.com", timeout=60000)

            print("⌛ Esperando campo de email...")
            page.wait_for_selector("input#topMenutxtEmail", timeout=15000)

            print("✍️ Ingresando email y contraseña...")
            page.fill("input#topMenutxtEmail", email)
            page.fill("input#topMenutxtContrasena", password)

            print("🖱️ Haciendo clic en 'Iniciar sesión'...")
            page.click("button:has-text('Iniciar sesión')")

            print("⏳ Esperando a que cargue el dashboard...")
            page.wait_for_timeout(5000)  # Ajusta según carga real

            print("✅ Login completado con éxito.")

        except PlaywrightTimeoutError as e:
            print(f"❌ Timeout esperando elementos: {e}")
            page.screenshot(path="error.png")
            with open("error.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        except Exception as e:
            print(f"❌ Error inesperado durante el login: {e}")
        finally:
            print("🧹 Cerrando navegador...")
            browser.close()

def main(curso):
    print(f"📚 Ejecutando login para el curso: {curso}")
    run_manejo()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ Uso: python -m descarga_archivos.download <NombreCurso>")
        sys.exit(1)

    main(sys.argv[1])
