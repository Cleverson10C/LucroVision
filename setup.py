import sys
import os
from cx_Freeze import setup, Executable

# Configuração das opções de build
build_exe_options = {
    "packages": ["tkinter", "sqlite3"],
    "include_files": ["comercio.db", "licenca.txt"],  # Adicione outros arquivos necessários
}

# Detecta base correta para ocultar console no Windows
base = None
if sys.platform == "win32":
    base = "gui"   # em versões novas do cx_Freeze

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