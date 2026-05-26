"""
Entrypoint do Caixa (somente tela de vendas).
Uso:
1) Defina LUCROVISOR_API_URL no ambiente.
2) Execute este arquivo (ou o EXE gerado dele).
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from vendas import tela_vendas

logger = logging.getLogger(__name__)


def _configurar_logging():
    if logging.getLogger().handlers:
        return

    if getattr(sys, "frozen", False):
        base_log = Path(sys.executable).resolve().parent
    else:
        base_log = Path(__file__).resolve().parent

    arquivo_log = base_log / "lucrovision_caixa.log"
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)

    handler_arquivo = RotatingFileHandler(
        arquivo_log,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler_arquivo.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[handler_console, handler_arquivo])
    logger.info("Logging do caixa configurado em %s", arquivo_log)


if __name__ == "__main__":
    _configurar_logging()
    api_url = os.environ.get("LUCROVISOR_API_URL", "").strip()
    logger.info("Inicializando Caixa. API URL configurada: %s", bool(api_url))

    if not api_url:
        messagebox.showerror(
            "Configuração ausente",
            "Defina LUCROVISOR_API_URL antes de abrir o Caixa.\n"
            "Exemplo: http://192.168.0.10:8000",
        )
        raise SystemExit(1)

    root = tk.Tk()
    root.withdraw()
    tela_vendas()
    root.mainloop()
