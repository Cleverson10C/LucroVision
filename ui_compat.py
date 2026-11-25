"""Widgets CustomTkinter com uma ponte pequena para as telas legadas do app."""

import tkinter as _tk
from tkinter import ttk
from typing import Any, Callable

import customtkinter as _ctk


_ctk.set_appearance_mode("light")
_ctk.set_default_color_theme("blue")


def _adaptar_opcoes(opcoes: dict[str, Any]) -> dict[str, Any]:
    opcoes = dict(opcoes)
    if "bg" in opcoes:
        opcoes["fg_color"] = opcoes.pop("bg")
    if "fg" in opcoes:
        opcoes["text_color"] = opcoes.pop("fg")
    # Opções exclusivas de widgets Tk clássicos, sem equivalente visual no CTk.
    for opcao in ("relief", "borderwidth", "cursor", "padx", "pady", "highlightthickness", "wraplength"):
        opcoes.pop(opcao, None)
    return opcoes


def _configurar_widget(
    widget: Any,
    configurar_base: Callable[..., Any],
    cnf: Any,
    opcoes: dict[str, Any],
) -> Any:
    if cnf is not None:
        if isinstance(cnf, dict):
            opcoes = {**cnf, **opcoes}
        else:
            return configurar_base(widget, cnf)
    return configurar_base(widget, **_adaptar_opcoes(opcoes))


class _Janela(_ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTk.configure, cnf, kwargs)

    config = configure


class _JanelaSecundaria(_ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkToplevel.configure, cnf, kwargs)

    config = configure


class _Frame(_ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkFrame.configure, cnf, kwargs)

    config = configure


class _Label(_ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkLabel.configure, cnf, kwargs)

    config = configure


class _Button(_ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkButton.configure, cnf, kwargs)

    config = configure


class _Entry(_ctk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkEntry.configure, cnf, kwargs)

    config = configure


class _RadioButton(_ctk.CTkRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkRadioButton.configure, cnf, kwargs)

    config = configure


class _OptionMenu(_ctk.CTkOptionMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **_adaptar_opcoes(kwargs))

    def configure(self, cnf: Any = None, **kwargs: Any) -> Any:
        return _configurar_widget(self, _ctk.CTkOptionMenu.configure, cnf, kwargs)

    config = configure


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

    def __getattr__(self, nome: str) -> Any:
        return getattr(_tk, nome)


tk = _TkNamespace()


def configurar_tabelas() -> None:
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
        rowheight=36,
        borderwidth=0,
        font=("Segoe UI", 12),
    )
    estilo.configure(
        "Treeview.Heading",
        background="#E8EEF7",
        foreground="#172B4D",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
    )
    estilo.map("Treeview", background=[("selected", "#C7DBF8")], foreground=[("selected", "#172B4D")])
