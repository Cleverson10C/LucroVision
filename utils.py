# utils.py
from tkinter import messagebox

def validar_campos(campos):
    """
    Verifica se todos os campos obrigatórios foram preenchidos.
    campos: dicionário {nome_do_campo: valor}
    """
    for nome, valor in campos.items():
        if not valor.strip():
            messagebox.showwarning("Campo obrigatório", f"Preencha o campo: {nome}")
            return False
    return True

def formatar_moeda(valor):
    """
    Formata um número float como moeda brasileira.
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def confirmar_acao(mensagem="Tem certeza que deseja continuar?"):
    """
    Exibe uma caixa de confirmação.
    """
    return messagebox.askyesno("Confirmação", mensagem)