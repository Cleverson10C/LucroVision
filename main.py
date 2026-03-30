"""
Sistema de Gerenciamento de Estoque Inteligente - LucroVision
Arquivo principal - Inicializa o banco de dados e abre a tela de login
"""

import os
import sys
from pathlib import Path

from database import criar_tabelas


def _configurar_tk():
    """Define caminhos do Tcl/Tk antes de carregar telas Tkinter."""
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
            return


def _validar_tk():
    try:
        import tkinter as tk

        interp = tk.Tcl()
        interp.eval("info patchlevel")
    except Exception as exc:
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
    _configurar_tk()
    _validar_tk()

    from login import tela_login

    # Inicializar estrutura do banco de dados
    criar_tabelas()
    
    # Abrir tela de login do sistema (com validação de licença incluída)
    tela_login()
    
