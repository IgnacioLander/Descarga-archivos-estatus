#!/usr/bin/env python3
import sys
from pathlib import Path

def main(task: str):
    task = task.lower()
    if task == "manejo":
        # your existing Selenium script
        from descarga_archivos.scripts.manejo_selenium import run_selenium
        run_selenium()

    elif task == "pilares":
        # call your Playwright script
        from descarga_archivos.scripts.pilares import run as run_pilares
        from playwright.sync_api import sync_playwright

        # ensure downloads go into the right folder
        Path("downloads/Pilares").mkdir(parents=True, exist_ok=True)
        with sync_playwright() as pw:
            run_pilares(pw)

    elif task == "control":
        # you can choose Selenium or Playwright here
        from descarga_archivos.scripts.control_selenium import run_selenium
        run_selenium()

    else:
        raise ValueError(f"Unknown task: {task}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download.py [Manejo|Pilares|control]")
        sys.exit(1)
    main(sys.argv[1])
