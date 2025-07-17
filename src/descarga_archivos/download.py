#!/usr/bin/env python3
import sys
from playwright.sync_api import sync_playwright
from descarga_archivos.scripts.manejo   import run as run_manejo
from descarga_archivos.scripts.pilares  import run as run_pilares
from descarga_archivos.scripts.control  import run as run_control

def main(task: str):
    with sync_playwright() as playwright:
        if task == "Manejo":
            run_manejo(playwright)
        elif task == "Pilares":
            run_pilares(playwright)
        elif task == "control":
            run_control(playwright)
        else:
            print(f"Unknown task: {task}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download.py [Manejo|Pilares|control]")
        sys.exit(1)
    main(sys.argv[1])
