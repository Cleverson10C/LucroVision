"""
Sistema de Gerenciamento de Estoque Inteligente - LucroVision
Arquivo principal - Inicializa o banco de dados e abre a tela de login
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from api_client import api_habilitada
from database import criar_tabelas

logger = logging.getLogger(__name__)


def _configurar_logging():
    """Configura logging da aplicação para console e arquivo."""
    if logging.getLogger().handlers:
        return

    if getattr(sys, "frozen", False):
        base_log = Path(sys.executable).resolve().parent
    else:
        base_log = Path(__file__).resolve().parent

    arquivo_log = base_log / "lucrovision.log"
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
    logger.info("Logging configurado em %s", arquivo_log)


def _configurar_tk():
    """Define caminhos do Tcl/Tk antes de carregar telas Tkinter."""
    logger.info("Iniciando configuracao de caminhos Tcl/Tk")
    candidatos = []

    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
        candidatos.extend(
            [
                (base / "share" / "tcl8.6", base / "share" / "tk8.6"),
                (base / "tcl" / "tcl8.6", base / "tcl" / "tk8.6"),
            ]
        )
    else:
        base = Path(sys.base_prefix)
        candidatos.extend(
            [
                (base / "tcl" / "tcl8.6", base / "tcl" / "tk8.6"),
                (base / "Library" / "lib" / "tcl8.6", base / "Library" / "lib" / "tk8.6"),
            ]
        )

    for tcl_dir, tk_dir in candidatos:
        if tcl_dir.is_dir() and tk_dir.is_dir():
            os.environ.setdefault("TCL_LIBRARY", str(tcl_dir))
            os.environ.setdefault("TK_LIBRARY", str(tk_dir))
            logger.info("Tcl/Tk configurado com TCL_LIBRARY=%s e TK_LIBRARY=%s", tcl_dir, tk_dir)
            return

    logger.warning("Nenhum caminho valido de Tcl/Tk foi encontrado")


def _validar_tk():
    logger.info("Validando ambiente Tkinter/Tcl")
    try:
        import tkinter as tk

        interp = tk.Tcl()
        interp.eval("info patchlevel")
        logger.info("Ambiente Tkinter/Tcl validado com sucesso")
    except Exception as exc:
        logger.exception("Falha ao validar Tkinter/Tcl")
        mensagem = (
            "Falha ao inicializar a interface gráfica (Tkinter/Tcl).\n\n"
            "Recomendação:\n"
            "1) Reinstale o Python com o componente Tcl/Tk.\n"
            "2) Preferencialmente use Python 3.12 para este projeto.\n"
            "3) Se estiver usando executável, gere novamente com 'python setup.py build'.\n\n"
            f"Detalhe técnico: {exc}"
        )

        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, mensagem, "LucroVision - Erro de ambiente", 0x10)
        except Exception:
            pass

        raise RuntimeError(mensagem) from exc

if __name__ == "__main__":
    _configurar_logging()
    logger.info("Iniciando aplicacao LucroVision")
    _configurar_tk()
    _validar_tk()

    from login import tela_login

    # Inicializar estrutura do banco de dados local somente em modo sem API
    if api_habilitada():
        logger.info("Modo API habilitado. Banco local nao sera inicializado neste cliente.")
    else:
        logger.info("Inicializando estrutura do banco de dados")
        criar_tabelas()
    
    # Abrir tela de login do sistema (com validação de licença incluída)
    logger.info("Abrindo tela de login")
    tela_login()
    
