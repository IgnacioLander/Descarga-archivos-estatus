# download.py
import sys
from playwright.sync_api import sync_playwright
from Manejo import run as run_manejo
from Pilares import run as run_pilares
from control import run as run_control

def main(task):
    with sync_playwright() as p:
        if task == "Manejo":
            run_manejo(p)
        elif task == "Pilares":
            run_pilares(p)
        elif task == "control":
            run_control(p)
        else:
            raise ValueError(f"Unknown task: {task}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download.py [Manejo|Pilares|control]")
        sys.exit(1)
    main(sys.argv[1])
