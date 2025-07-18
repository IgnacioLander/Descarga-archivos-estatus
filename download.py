#!/usr/bin/env python3
import sys

from descarga_archivos.scripts.manejo_selenium  import run_selenium as run_manejo
from descarga_archivos.scripts.pilares_selenium import run_selenium as run_pilares
from descarga_archivos.scripts.control_selenium import run_selenium as run_control

def main(task: str):
    """
    Dispatches to the appropriate Selenium-based script.
    """
    if task == "Manejo":
        run_manejo()
    elif task == "Pilares":
        run_pilares()
    elif task.lower() == "control":
        run_control()
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download.py [Manejo|Pilares|control]")
        sys.exit(1)
    main(sys.argv[1])
