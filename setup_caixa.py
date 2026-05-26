import logging
import sys
from pathlib import Path
from cx_Freeze import Executable, setup

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

BASE_DIR = Path(__file__).resolve().parent
BAT_PATH = BASE_DIR / "iniciar_caixa.bat"

if not BAT_PATH.exists():
    BAT_PATH.write_text(
        "@echo off\n"
        "setlocal\n\n"
        "rem Ajuste para o IP/porta do computador servidor (API)\n"
        "set \"LUCROVISOR_API_URL=http://192.168.0.10:8000\"\n\n"
        "echo Iniciando LucroVision Caixa...\n"
        "echo API: %LUCROVISOR_API_URL%\n"
        "echo.\n\n"
        "set \"APP_DIR=%~dp0\"\n"
        "\"%APP_DIR%LucroVisionCaixa.exe\"\n\n"
        "endlocal\n",
        encoding="utf-8",
    )
    logger.info("Arquivo iniciar_caixa.bat criado automaticamente em %s", BAT_PATH)

build_exe_options = {
    "packages": ["tkinter", "sqlite3", "requests"],
    "include_files": ["Logo.png", "Logo.ico", "iniciar_caixa.bat"],
}

base = None
if sys.platform == "win32":
    base = "gui"

logger.info("Iniciando build do executavel do Caixa (base=%s)", base)

setup(
    name="LucroVisionCaixa",
    version="1.0",
    description="LucroVision - Caixa (somente vendas)",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "caixa_main.py",
            base=base,
            target_name="LucroVisionCaixa.exe",
            icon="Logo.ico",
        )
    ],
)
