import tkinter as tk
from database import conectar

def tela_relatorios():
    """Cria e exibe a tela de relatórios de lucratividade"""
    janela_relatorios = tk.Toplevel()
    janela_relatorios.title("Relatórios de Lucratividade")
    janela_relatorios.geometry("700x600")

    # Seção de Lucro Mensal
    tk.Label(janela_relatorios, text="Lucro Mensal", font=("Arial", 12, "bold")).pack(pady=5)
    
    # Frame com scrollbar para a lista mensal
    frame_mensal = tk.Frame(janela_relatorios)
    frame_mensal.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
    
    scrollbar_mensal = tk.Scrollbar(frame_mensal)
    scrollbar_mensal.pack(side=tk.RIGHT, fill=tk.Y)
    
    lista_lucros_mensais = tk.Listbox(frame_mensal, width=80, height=12, yscrollcommand=scrollbar_mensal.set)
    lista_lucros_mensais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_mensal.config(command=lista_lucros_mensais.yview)

    conexao_banco = conectar()
    cursor_banco = conexao_banco.cursor()
    
    # Buscar lucros mensais por produto
    cursor_banco.execute("""
        SELECT strftime('%Y-%m', data_venda) as mes,
               p.nome,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_produto
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY mes, p.nome
        ORDER BY mes DESC, lucro_produto DESC
    """)
    
    resultados_mensais_produtos = cursor_banco.fetchall()
    
    # Buscar total mensal
    cursor_banco.execute("""
        SELECT strftime('%Y-%m', data_venda) as mes,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY mes
        ORDER BY mes DESC
    """)
    
    resultados_totais_mensais = cursor_banco.fetchall()
    
    # Criar dicionário com totais por mês
    totais_por_mes = {mes: lucro for mes, lucro in resultados_totais_mensais}
    
    # Exibir produtos agrupados por mês
    mes_anterior = None
    for mes_ano, nome_produto, lucro_produto in resultados_mensais_produtos:
        # Converter formato de data (2025-11 para 11/2025)
        ano, mes = mes_ano.split('-')
        mes_formatado = f"{mes}/{ano}"
        
        if mes_ano != mes_anterior:
            if mes_anterior is not None:
                # Mostrar total do mês anterior
                total_formatado = f"{totais_por_mes[mes_anterior]:,.2f}"
                lista_lucros_mensais.insert(tk.END, f"  {'─' * 60}")
                lista_lucros_mensais.insert(tk.END, f"  TOTAL {mes_anterior_formatado}: R$ {total_formatado}")
                lista_lucros_mensais.insert(tk.END, "")
            
            lista_lucros_mensais.insert(tk.END, f"▼ {mes_formatado}")
            mes_anterior = mes_ano
            mes_anterior_formatado = mes_formatado
        
        lucro_formatado = f"{lucro_produto:,.2f}"
        lista_lucros_mensais.insert(tk.END, f"  • {nome_produto}: R$ {lucro_formatado}")
    
    # Mostrar total do último mês
    if mes_anterior is not None:
        total_formatado = f"{totais_por_mes[mes_anterior]:,.2f}"
        lista_lucros_mensais.insert(tk.END, f"  {'─' * 120}")
        lista_lucros_mensais.insert(tk.END, f"  TOTAL {mes_anterior_formatado}: R$ {total_formatado}")

    # Seção de Lucro Anual
    tk.Label(janela_relatorios, text="Lucro Anual", font=("Arial", 12, "bold")).pack(pady=10)
    
    # Frame com scrollbar para a lista anual
    frame_anual = tk.Frame(janela_relatorios)
    frame_anual.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
    
    scrollbar_anual = tk.Scrollbar(frame_anual)
    scrollbar_anual.pack(side=tk.RIGHT, fill=tk.Y)
    
    lista_lucros_anuais = tk.Listbox(frame_anual, width=80, height=8, yscrollcommand=scrollbar_anual.set)
    lista_lucros_anuais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_anual.config(command=lista_lucros_anuais.yview)

    # Buscar lucros anuais por categoria
    cursor_banco.execute("""
        SELECT strftime('%Y', data_venda) as ano,
               p.categoria,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_categoria
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY ano, p.categoria
        ORDER BY ano DESC, lucro_categoria DESC
    """)
    
    resultados_anuais_categorias = cursor_banco.fetchall()
    
    # Buscar total anual
    cursor_banco.execute("""
        SELECT strftime('%Y', data_venda) as ano,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY ano
        ORDER BY ano DESC
    """)
    
    resultados_totais_anuais = cursor_banco.fetchall()
    
    # Criar dicionário com totais por ano
    totais_por_ano = {ano: lucro for ano, lucro in resultados_totais_anuais}
    
    # Exibir categorias agrupadas por ano
    ano_anterior = None
    for ano, categoria, lucro_categoria in resultados_anuais_categorias:
        if ano != ano_anterior:
            if ano_anterior is not None:
                # Mostrar total do ano anterior
                total_formatado = f"{totais_por_ano[ano_anterior]:,.2f}"
                lista_lucros_anuais.insert(tk.END, f"  {'─' * 120}")
                lista_lucros_anuais.insert(tk.END, f"  TOTAL {ano_anterior}: R$ {total_formatado}")
                lista_lucros_anuais.insert(tk.END, "")
            
            lista_lucros_anuais.insert(tk.END, f"▼ {ano}")
            ano_anterior = ano
        
        lucro_formatado = f"{lucro_categoria:,.2f}"
        lista_lucros_anuais.insert(tk.END, f"  • {categoria}: R$ {lucro_formatado}")
    
    # Mostrar total do último ano
    if ano_anterior is not None:
        total_formatado = f"{totais_por_ano[ano_anterior]:,.2f}"
        lista_lucros_anuais.insert(tk.END, f"  {'─' * 120}")
        lista_lucros_anuais.insert(tk.END, f"  TOTAL {ano_anterior}: R$ {total_formatado}")

    conexao_banco.close()