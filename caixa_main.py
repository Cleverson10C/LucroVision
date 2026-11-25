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
from ui_compat import tk
from tkinter import messagebox

from vendas import tela_vendas
from api_client import login as api_login, encerrar_sessao as api_logout

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
    root.title("Login do Caixa - LucroVision")
    root.geometry("360x250")
    root.configure(bg="#f0f0f0")
    tk.Label(root, text="Acesso ao Caixa", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=16)
    tk.Label(root, text="Usuário", bg="#f0f0f0").pack()
    campo_usuario = tk.Entry(root, width=30)
    campo_usuario.pack(pady=4)
    tk.Label(root, text="Senha", bg="#f0f0f0").pack()
    campo_senha = tk.Entry(root, width=30, show="*")
    campo_senha.pack(pady=4)

    def entrar(event=None):
        try:
            if not api_login(campo_usuario.get().strip(), campo_senha.get()):
                messagebox.showerror("Acesso negado", "Usuário ou senha inválidos.", parent=root)
                return
            root.withdraw()
            janela_venda = tela_vendas()

            def sair_do_caixa(event=None):
                if event is not None and event.widget is not janela_venda:
                    return
                api_logout()
                root.deiconify()
                campo_senha.delete(0, tk.END)

            janela_venda.bind("<Destroy>", sair_do_caixa, add="+")
            janela_venda.protocol("WM_DELETE_WINDOW", janela_venda.destroy)
        except Exception as erro:
            messagebox.showerror("Falha de conexão", f"Não foi possível acessar a API: {erro}", parent=root)

    campo_senha.bind("<Return>", entrar)
    tk.Button(root, text="Entrar", command=entrar, bg="#27ae60", fg="white", padx=25, pady=6).pack(pady=14)
    root.mainloop()
