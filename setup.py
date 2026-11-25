import sys
import os
import logging
from pathlib import Path
import customtkinter
from cx_Freeze import setup, Executable

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

# Configuração das opções de build
customtkinter_assets = Path(customtkinter.__file__).resolve().parent / "assets"
customtkinter_license = Path(__file__).resolve().parent / "licenses" / "customtkinter-MIT.txt"
build_exe_options = {
    "packages": ["tkinter", "sqlite3", "customtkinter"],
    "include_files": ["Logo.png", "Logo.ico", (str(customtkinter_assets), "lib/customtkinter/assets"),
                      (str(customtkinter_license), "licenses/customtkinter-MIT.txt")],
}

# Detecta base correta para ocultar console no Windows
base = None
if sys.platform == "win32":
    base = "gui"   # em versões novas do cx_Freeze
logger.info("Iniciando build do executavel LucroVisor (base=%s)", base)

# Configuração do executável
setup(
    name="LucroVisor",
    version="1.0",
    description="Sistema de Gerenciamento de Estoque Inteligente",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="LucroVisor.exe",
            icon="Logo.ico"
        )
    ]
)
