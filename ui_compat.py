"""Widgets CustomTkinter com uma ponte pequena para as telas legadas do app."""

import tkinter as _tk
from tkinter import ttk

import customtkinter as _ctk


_ctk.set_appearance_mode("light")
_ctk.set_default_color_theme("blue")


def _adaptar_opcoes(opcoes):
    opcoes = dict(opcoes)
    if "bg" in opcoes:
        opcoes["fg_color"] = opcoes.pop("bg")
    if "fg" in opcoes:
        opcoes["text_color"] = opcoes.pop("fg")
    # Opções exclusivas de widgets Tk clássicos, sem equivalente visual no CTk.
    for opcao in ("relief", "borderwidth", "cursor", "padx", "pady", "highlightthickness", "wraplength"):
        opcoes.pop(opcao, None)
    return opcoes


class _ConfiguraCores:
    def configure(self, cnf=None, **kwargs):
        if cnf is not None:
            if isinstance(cnf, dict):
                kwargs = {**cnf, **kwargs}
            else:
                return super().configure(cnf)
        return super().configure(**_adaptar_opcoes(kwargs))

    config = configure


class _Janela(_ConfiguraCores, _ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _JanelaSecundaria(_ConfiguraCores, _ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _Frame(_ConfiguraCores, _ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _Label(_ConfiguraCores, _ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _Button(_ConfiguraCores, _ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _Entry(_ConfiguraCores, _ctk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _RadioButton(_ConfiguraCores, _ctk.CTkRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _OptionMenu(_ConfiguraCores, _ctk.CTkOptionMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))


class _TkNamespace:
    Tk = _Janela
    Toplevel = _JanelaSecundaria
    Frame = _Frame
    Label = _Label
    Button = _Button
    Entry = _Entry
    Radiobutton = _RadioButton
    OptionMenu = _OptionMenu

    # Widgets sem substituto direto continuam disponíveis para tabelas,
    # listas, barras de rolagem e compatibilidade com os fluxos existentes.
    LabelFrame = _tk.LabelFrame
    Scrollbar = _tk.Scrollbar
    Listbox = _tk.Listbox

    def __getattr__(self, nome):
        return getattr(_tk, nome)


tk = _TkNamespace()


def configurar_tabelas():
    """Aplica um tema claro coerente às tabelas ttk que permanecem no app."""
    estilo = ttk.Style()
    try:
        estilo.theme_use("clam")
    except _tk.TclError:
        pass
    estilo.configure(
        "Treeview",
        background="#FFFFFF",
        fieldbackground="#FFFFFF",
        foreground="#1F2937",
        rowheight=30,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    estilo.configure(
        "Treeview.Heading",
        background="#E8EEF7",
        foreground="#172B4D",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    estilo.map("Treeview", background=[("selected", "#C7DBF8")], foreground=[("selected", "#172B4D")])
