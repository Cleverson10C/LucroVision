"""
Módulo de Controle de Estoque
Gerencia a visualização e filtragem dos produtos em estoque
"""

import tkinter as tk
from tkinter import ttk
from database import conectar
import datetime

def tela_estoque():
    """Cria e exibe a tela de controle de estoque com filtros e estatísticas"""
    
    # Criar janela principal do estoque
    janela_estoque = tk.Toplevel()
    janela_estoque.title("Controle de Estoque")
    janela_estoque.geometry("800x500")

    # Frame superior com título e filtros
    frame_superior = tk.Frame(janela_estoque)
    frame_superior.pack(pady=10, padx=10, fill=tk.X)

    tk.Label(frame_superior, text="Controle de Estoque", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)

    # Variáveis para filtros
    tipo_filtro = tk.StringVar(value="todos")
    categoria_filtro = tk.StringVar(value="Todas")

    # Combobox de categoria dinâmico
    def atualizar_categorias():
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()
        cursor_banco.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria != ''")
        cats = sorted([row[0] for row in cursor_banco.fetchall()])
        conexao_banco.close()
        lista_categorias = ["Todas"] + cats
        combo_categoria['values'] = lista_categorias
        if categoria_filtro.get() not in lista_categorias:
            categoria_filtro.set("Todas")

    tk.Label(frame_superior, text="Categoria:").pack(side=tk.LEFT, padx=5)
    combo_categoria = ttk.Combobox(frame_superior, state="readonly", textvariable=categoria_filtro, width=12)
    combo_categoria.pack(side=tk.LEFT, padx=5)
    atualizar_categorias()

    def carregar_lista_produtos():
        atualizar_categorias()
        """Carrega os produtos do banco de dados conforme o filtro selecionado"""
        # Limpar itens anteriores da tabela
        for item_tabela in tabela_produtos.get_children():
            tabela_produtos.delete(item_tabela)
        
        # Conectar ao banco de dados
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()

        # Buscar produtos conforme filtro de categoria e tipo
        categoria = categoria_filtro.get()
        tipo_visualizacao = tipo_filtro.get()
        parametros = []
        filtros_sql = []

        if tipo_visualizacao == "baixo":
            filtros_sql.append("quantidade <= estoque_minimo")
        else:
            filtros_sql.append("quantidade > estoque_minimo")

        if categoria != "Todas":
            filtros_sql.append("categoria = ?")
            parametros.append(categoria)

        filtros_combinados = " AND ".join(filtros_sql)
        consulta = f"""
            SELECT nome, categoria, quantidade, estoque_minimo, preco_venda, validade
            FROM produtos
            WHERE {filtros_combinados}
            ORDER BY nome ASC
        """
        cursor_banco.execute(consulta, parametros)
        lista_produtos = cursor_banco.fetchall()
        conexao_banco.close()

        # Preencher tabela com os produtos
        if lista_produtos:
            for produto_info in lista_produtos:
                nome_produto, categoria_produto, quantidade_atual, quantidade_minima, preco_produto, data_validade = produto_info

                # Definir cor de destaque para estoque baixo
                cor_destaque = "estoque_baixo" if quantidade_atual <= quantidade_minima else "estoque_normal"

                # Formatar quantidade com unidade para carnes, frios, padaria e hortifruti
                if categoria_produto and categoria_produto.lower() in ["carnes", "frios", "padaria","hortifruti"]:
                    quantidade_exibicao = f"{quantidade_atual:.3f} kg"
                    quantidade_minima_exibicao = f"{quantidade_minima:.3f} kg"
                else:
                    quantidade_exibicao = str(quantidade_atual)
                    quantidade_minima_exibicao = str(quantidade_minima)

                # Formatar data para formato brasileiro (MM/YYYY)
                if data_validade:
                    try:
                        partes_data = data_validade.split('-')
                        data_formatada = f"{partes_data[1]}/{partes_data[0]}"
                    except:
                        data_formatada = data_validade
                else:
                    data_formatada = ""

                # Inserir produto na tabela
                tabela_produtos.insert("", tk.END,
                    values=(nome_produto, categoria_produto, quantidade_exibicao, quantidade_minima_exibicao,
                            f"R$ {preco_produto:.2f}", data_formatada),
                    tags=(cor_destaque,))
        else:
            tabela_produtos.insert("", tk.END, values=("Nenhum produto encontrado", "", "", "", "", ""))

    # Botões de filtro (radio buttons)
    tk.Radiobutton(frame_superior, text="Todos os Produtos", variable=tipo_filtro, value="todos", 
                   command=carregar_lista_produtos).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(frame_superior, text="Apenas Estoque Baixo", variable=tipo_filtro, value="baixo", 
                   command=carregar_lista_produtos).pack(side=tk.LEFT, padx=5)
    combo_categoria.bind("<<ComboboxSelected>>", lambda e: carregar_lista_produtos())

    # Frame para conter a tabela de produtos
    frame_tabela = tk.Frame(janela_estoque)
    frame_tabela.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Barra de rolagem vertical
    barra_rolagem = tk.Scrollbar(frame_tabela)
    barra_rolagem.pack(side=tk.RIGHT, fill=tk.Y)

    # Definir colunas da tabela
    colunas_tabela = ("Nome", "Categoria", "Quantidade", "Estoque Mín.", "Preço", "Validade")
    tabela_produtos = ttk.Treeview(frame_tabela, columns=colunas_tabela, show="headings", 
                                   yscrollcommand=barra_rolagem.set)
    barra_rolagem.config(command=tabela_produtos.yview)

    # Configurar cabeçalhos das colunas
    tabela_produtos.heading("Nome", text="Nome do Produto")
    tabela_produtos.heading("Categoria", text="Categoria")
    tabela_produtos.heading("Quantidade", text="Qtd.")
    tabela_produtos.heading("Estoque Mín.", text="Mín.")
    tabela_produtos.heading("Preço", text="Preço")
    tabela_produtos.heading("Validade", text="Validade")

    # Configurar largura das colunas
    tabela_produtos.column("Nome", width=200)
    tabela_produtos.column("Categoria", width=120)
    tabela_produtos.column("Quantidade", width=80, anchor=tk.CENTER)
    tabela_produtos.column("Estoque Mín.", width=80, anchor=tk.CENTER)
    tabela_produtos.column("Preço", width=100, anchor=tk.CENTER)
    tabela_produtos.column("Validade", width=100, anchor=tk.CENTER)

    # Configurar cores para destacar produtos
    tabela_produtos.tag_configure("estoque_baixo", background="#ffcccc")  # Vermelho claro para estoque baixo
    tabela_produtos.tag_configure("estoque_normal", background="#ffffff")  # Branco para estoque normal

    tabela_produtos.pack(fill=tk.BOTH, expand=True)

    # Frame inferior para estatísticas
    frame_informacoes = tk.Frame(janela_estoque)
    frame_informacoes.pack(pady=10, padx=10, fill=tk.X)

    rotulo_estatisticas = tk.Label(frame_informacoes, text="", font=("Arial", 9))
    rotulo_estatisticas.pack()

    def atualizar_estatisticas():
        """Atualiza as estatísticas exibidas na parte inferior da tela"""
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()
        
        # Total de produtos cadastrados
        cursor_banco.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor_banco.fetchone()[0]
        
        # Produtos com estoque baixo
        cursor_banco.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo")
        produtos_estoque_baixo = cursor_banco.fetchone()[0]
        
        # Total de itens em estoque (soma de todas as quantidades)
        cursor_banco.execute("SELECT SUM(quantidade) FROM produtos")
        total_itens_estoque = cursor_banco.fetchone()[0] or 0
        
        conexao_banco.close()
        
        # Atualizar texto do rótulo
        rotulo_estatisticas.config(
            text=f"Total de produtos: {total_produtos} | "
                 f"Produtos com estoque baixo: {produtos_estoque_baixo} | "
                 f"Total de itens em estoque: {total_itens_estoque}"
        )

    # Carregar dados iniciais
    carregar_lista_produtos()
    atualizar_estatisticas()