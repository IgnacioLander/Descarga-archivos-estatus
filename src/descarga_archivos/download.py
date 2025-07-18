#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

from descarga_archivos.scripts.manejo   import run as run_manejo
from descarga_archivos.scripts.pilares  import run as run_pilares
from descarga_archivos.scripts.control  import run as run_control

def main(task: str):
    # 1. Determine download directory
    download_dir = os.getenv("DOWNLOAD_DIR", f"./downloads/{task}")
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # 2. Launch browser with custom download path
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        context.set_default_downloads_path(download_dir)
        page = context.new_page()

        # 3. Dispatch to the correct script
        if task == "Manejo":
            run_manejo(page)
        elif task == "Pilares":
            run_pilares(page)
        elif task.lower() == "control":
            run_control(page)
        else:
            print(f"Unknown task: {task}")
            sys.exit(1)

        browser.close()
        print(f"✅ All downloads for '{task}' are in: {download_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download.py [Manejo|Pilares|control]")
        sys.exit(1)
    main(sys.argv[1])
