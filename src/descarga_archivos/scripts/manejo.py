import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run():
    email = os.getenv("F_EMAIL")
    password = os.getenv("F_PASSWORD")

    if not email or not password:
        print("❌ Variables F_EMAIL o F_PASSWORD no están definidas.")
        return

    with sync_playwright() as p:
        print("🚀 Iniciando navegador Chromium en modo headless seguro...")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
                "--single-process",
                "--disable-accelerated-2d-canvas"
            ]
        )

        page = browser.new_page(viewport={"width": 1280, "height": 800})

        try:
            print("🌐 Accediendo a https://academia.farmatodo.com ...")
            page.goto("https://academia.farmatodo.com", timeout=60000)

            print("🔍 Esperando campo de Email...")
            page.wait_for_selector("input#topMenutxtEmail", timeout=15000)

            print("✍️ Ingresando usuario y contraseña...")
            page.fill("input#topMenutxtEmail", email)
            page.fill("input#topMenutxtContrasena", password)

            print("🖱️ Clic en 'Iniciar sesión'...")
            page.click("button:has-text('Iniciar sesión')")

            print("⏳ Esperando redirección o carga posterior al login...")
            page.wait_for_timeout(5000)

            # Validación simple de login
            if "login" in page.url.lower():
                raise Exception("Parece que el login falló. Verifica credenciales o cambios en el sitio.")

            print("✅ Login exitoso.")

            # Aquí puedes continuar con descarga si hace falta

        except PlaywrightTimeoutError as e:
            print(f"❌ Timeout esperando selector: {e}")
            page.screenshot(path="error.png")
            with open("error.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            page.screenshot(path="error.png")
            with open("error.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        finally:
            browser.close()

if __name__ == "__main__":
    run()
