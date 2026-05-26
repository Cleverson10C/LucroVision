import tkinter as tk
import logging
from relatorios_data import obter_dados_relatorios

logger = logging.getLogger(__name__)


def tela_relatorios():
    """Cria e exibe a tela de relatórios de lucratividade"""
    logger.info("Tela de relatorios aberta")
    janela_relatorios = tk.Toplevel()
    janela_relatorios.title("Relatórios de Lucratividade")
    janela_relatorios.geometry("800x700")

    # Secao de Lucro Mensal
    tk.Label(janela_relatorios, text="Lucro Mensal", font=("Arial", 12, "bold")).pack(pady=5)
    frame_mensal = tk.Frame(janela_relatorios)
    frame_mensal.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    scrollbar_mensal = tk.Scrollbar(frame_mensal)
    scrollbar_mensal.pack(side=tk.RIGHT, fill=tk.Y)

    lista_lucros_mensais = tk.Listbox(frame_mensal, width=80, height=12, yscrollcommand=scrollbar_mensal.set)
    lista_lucros_mensais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_mensal.config(command=lista_lucros_mensais.yview)

    # Secao de Lucro Anual
    tk.Label(janela_relatorios, text="Lucro Anual", font=("Arial", 12, "bold")).pack(pady=10)
    frame_anual = tk.Frame(janela_relatorios)
    frame_anual.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    scrollbar_anual = tk.Scrollbar(frame_anual)
    scrollbar_anual.pack(side=tk.RIGHT, fill=tk.Y)

    lista_lucros_anuais = tk.Listbox(frame_anual, width=80, height=12, yscrollcommand=scrollbar_anual.set)
    lista_lucros_anuais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_anual.config(command=lista_lucros_anuais.yview)

    try:
        dados_relatorio = obter_dados_relatorios()
        resultados_mensais_produtos = dados_relatorio["mensais_produtos"]
        resultados_totais_mensais = dados_relatorio["mensais_totais"]
        resultados_anuais_categorias = dados_relatorio["anuais_categorias"]
        resultados_totais_anuais = dados_relatorio["anuais_totais"]
        logger.info(
            "Relatorio mensal carregado: produtos_mes=%s, totais_mes=%s",
            len(resultados_mensais_produtos),
            len(resultados_totais_mensais),
        )

        totais_por_mes = {mes: lucro for mes, lucro in resultados_totais_mensais}
        mes_anterior = None
        mes_anterior_formatado = ""
        for mes_ano, nome_produto, lucro_produto in resultados_mensais_produtos:
            ano, mes = mes_ano.split("-")
            mes_formatado = f"{mes}/{ano}"

            if mes_ano != mes_anterior:
                if mes_anterior is not None:
                    total_formatado = f"{totais_por_mes[mes_anterior]:,.2f}"
                    lista_lucros_mensais.insert(tk.END, f"  {'─' * 120}")
                    lista_lucros_mensais.insert(tk.END, f"  TOTAL {mes_anterior_formatado}: R$ {total_formatado}")
                    lista_lucros_mensais.insert(tk.END, "")

                lista_lucros_mensais.insert(tk.END, f"▼ {mes_formatado}")
                mes_anterior = mes_ano
                mes_anterior_formatado = mes_formatado

            lucro_formatado = f"{lucro_produto:,.2f}"
            lista_lucros_mensais.insert(tk.END, f"  • {nome_produto}: R$ {lucro_formatado}")

        if mes_anterior is not None:
            total_formatado = f"{totais_por_mes[mes_anterior]:,.2f}"
            lista_lucros_mensais.insert(tk.END, f"  {'─' * 120}")
            lista_lucros_mensais.insert(tk.END, f"  TOTAL {mes_anterior_formatado}: R$ {total_formatado}")

        logger.info(
            "Relatorio anual carregado: categorias_ano=%s, totais_ano=%s",
            len(resultados_anuais_categorias),
            len(resultados_totais_anuais),
        )

        totais_por_ano = {ano: lucro for ano, lucro in resultados_totais_anuais}
        ano_anterior = None
        for ano, categoria, lucro_categoria in resultados_anuais_categorias:
            if ano != ano_anterior:
                if ano_anterior is not None:
                    total_formatado = f"{totais_por_ano[ano_anterior]:,.2f}"
                    lista_lucros_anuais.insert(tk.END, f"  {'─' * 120}")
                    lista_lucros_anuais.insert(tk.END, f"  TOTAL {ano_anterior}: R$ {total_formatado}")
                    lista_lucros_anuais.insert(tk.END, "")

                lista_lucros_anuais.insert(tk.END, f"▼ {ano}")
                ano_anterior = ano

            lucro_formatado = f"{lucro_categoria:,.2f}"
            lista_lucros_anuais.insert(tk.END, f"  • {categoria}: R$ {lucro_formatado}")

        if ano_anterior is not None:
            total_formatado = f"{totais_por_ano[ano_anterior]:,.2f}"
            lista_lucros_anuais.insert(tk.END, f"  {'─' * 120}")
            lista_lucros_anuais.insert(tk.END, f"  TOTAL {ano_anterior}: R$ {total_formatado}")

        logger.info("Montagem dos relatorios concluida")
    except Exception:
        logger.exception("Falha ao montar relatorios")
