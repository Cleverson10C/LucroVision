"""
Módulo de Registro de Vendas
Permite registrar vendas de produtos e atualiza o estoque automaticamente
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from datetime import datetime

def tela_vendas():
    """Cria e exibe a tela de registro de vendas"""
    
    janela_vendas = tk.Toplevel()
    janela_vendas.title("Registrar Venda")
    janela_vendas.geometry("1200x780")
    janela_vendas.configure(bg="#f0f0f0")
    
    # Frame superior - Seleção de produto
    frame_superior = tk.LabelFrame(janela_vendas, text="Selecionar Produto", 
                                   font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
    frame_superior.pack(pady=10, padx=20, fill=tk.X)
    
    # Campo de busca
    tk.Label(frame_superior, text="Buscar produto:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
    campo_busca = tk.Entry(frame_superior, width=40, font=("Arial", 10))
    campo_busca.grid(row=0, column=1, padx=10, pady=5)

    # Campo de leitura de código de barras
    tk.Label(frame_superior, text="Código de barras:", bg="white", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5)
    campo_codigo_barras = tk.Entry(frame_superior, width=14, font=("Arial", 10))
    campo_codigo_barras.grid(row=0, column=3, padx=10, pady=5)
    
    # Lista de produtos disponíveis
    tk.Label(frame_superior, text="Produtos disponíveis:", bg="white", font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
    
    frame_lista = tk.Frame(frame_superior, bg="white")
    frame_lista.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
    
    scrollbar_produtos = tk.Scrollbar(frame_lista)
    scrollbar_produtos.pack(side=tk.RIGHT, fill=tk.Y)
    
    colunas_produtos = ("ID", "Nome", "Categoria", "Estoque", "Preço", "Código de barras")
    tabela_produtos = ttk.Treeview(frame_lista, columns=colunas_produtos, show="headings", 
                                   height=6, yscrollcommand=scrollbar_produtos.set)
    scrollbar_produtos.config(command=tabela_produtos.yview)
    
    tabela_produtos.heading("ID", text="ID")
    tabela_produtos.heading("Nome", text="Nome do Produto")
    tabela_produtos.heading("Categoria", text="Categoria")
    tabela_produtos.heading("Estoque", text="Estoque")
    tabela_produtos.heading("Preço", text="Preço Unit.")
    tabela_produtos.heading("Código de barras", text="Código de barras")
    
    tabela_produtos.column("ID", width=50, anchor=tk.CENTER, stretch=False)
    tabela_produtos.column("Nome", width=260, stretch=True)
    tabela_produtos.column("Categoria", width=140, stretch=False)
    tabela_produtos.column("Estoque", width=90, anchor=tk.CENTER, stretch=False)
    tabela_produtos.column("Preço", width=110, anchor=tk.CENTER, stretch=False)
    tabela_produtos.column("Código de barras", width=140, anchor=tk.CENTER, stretch=False)
    
    tabela_produtos.pack(fill=tk.BOTH, expand=True)
    
    # Frame de informações do produto selecionado
    frame_info = tk.LabelFrame(janela_vendas, text="Informações da Venda", 
                               font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
    frame_info.pack(pady=10, padx=20, fill=tk.X)

    # Variáveis para armazenar informações
    produto_selecionado = {"id": None, "nome": "", "preco": 0.0, "estoque": 0, "categoria": "", "codigo_barras": ""}
    itens_venda = []  # Lista de itens da venda

    tk.Label(frame_info, text="Produto:", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
    label_produto_selecionado = tk.Label(frame_info, text="Nenhum produto selecionado", bg="white", font=("Arial", 10))
    label_produto_selecionado.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

    tk.Label(frame_info, text="Preço unitário:", bg="white", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
    label_preco = tk.Label(frame_info, text="R$ 0,00", bg="white", font=("Arial", 10))
    label_preco.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

    tk.Label(frame_info, text="Estoque disponível:", bg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
    label_estoque = tk.Label(frame_info, text="0 unidades", bg="white", font=("Arial", 10))
    label_estoque.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

    # Campo de quantidade (padrão)
    tk.Label(frame_info, text="Quantidade:", bg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
    campo_quantidade = tk.Entry(frame_info, width=15, font=("Arial", 10))
    campo_quantidade.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
    campo_quantidade.insert(0, "1")
    # Campo especial para carnes e frios
    campo_kg = tk.Entry(frame_info, width=15, font=("Arial", 10))
    campo_kg.grid(row=3, column=2, sticky=tk.W, padx=10, pady=5)
    campo_kg.insert(0, "0,100")
    campo_kg.grid_remove()  # Esconde por padrão
    label_kg = tk.Label(frame_info, text="(Ex: 0,350 para 350g)", bg="white", font=("Arial", 8, "italic"))
    label_kg.grid(row=3, column=3, sticky=tk.W, padx=5)
    label_kg.grid_remove()
    # Botões de ajuste para kg
    def ajustar_kg(delta):
        try:
            valor = campo_kg.get().replace(",", ".")
            valor_float = float(valor)
            novo_valor = max(0.1, round(valor_float + delta, 3))
            campo_kg.delete(0, tk.END)
            campo_kg.insert(0, f"{novo_valor:.3f}".replace(".", ","))
            calcular_total()
        except:
            campo_kg.delete(0, tk.END)
            campo_kg.insert(0, "0,100")
            calcular_total()

    
    # Treeview para itens da venda com Scrollbar
    colunas_venda = ("Nome", "Preço Unitário", "Quantidade", "Subtotal", "Código de barras")
    scrollbar_venda = tk.Scrollbar(frame_info)
    scrollbar_venda.grid(row=5, column=6, sticky="ns", pady=(10, 0))
    tabela_venda = ttk.Treeview(frame_info, columns=colunas_venda, show="headings", height=5, yscrollcommand=scrollbar_venda.set)
    tabela_venda.grid(row=5, column=0, columnspan=6, sticky="ew", pady=(10, 0))
    scrollbar_venda.config(command=tabela_venda.yview)
    tabela_venda.heading("Nome", text="Produto")
    tabela_venda.heading("Preço Unitário", text="Preço Unitário")
    tabela_venda.heading("Quantidade", text="Quantidade")
    tabela_venda.heading("Subtotal", text="Subtotal")
    tabela_venda.heading("Código de barras", text="Código de barras")
    tabela_venda.column("Nome", width=220, anchor=tk.CENTER, stretch=True)
    tabela_venda.column("Preço Unitário", width=110, anchor=tk.CENTER, stretch=False)
    tabela_venda.column("Quantidade", width=90, anchor=tk.CENTER, stretch=False)
    tabela_venda.column("Subtotal", width=110, anchor=tk.CENTER, stretch=False)
    tabela_venda.column("Código de barras", width=140, anchor=tk.CENTER, stretch=False)

    # Função para adicionar item à venda
    def adicionar_item_venda():
        if not produto_selecionado["id"]:
            messagebox.showerror("Erro", "Selecione um produto para adicionar!")
            return
        try:
            if campo_kg.winfo_ismapped():
                quantidade = float(campo_kg.get().replace(",", "."))
            else:
                quantidade = int(campo_quantidade.get())
            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!")
                return
            subtotal = produto_selecionado["preco"] * quantidade
            # Adiciona na lista e na tabela
            item = {
                "id": produto_selecionado["id"],
                "nome": produto_selecionado["nome"],
                "preco": produto_selecionado["preco"],
                "quantidade": quantidade,
                "subtotal": subtotal,
                "codigo_barras": produto_selecionado["codigo_barras"],
            }
            itens_venda.append(item)
            tabela_venda.insert(
                "",
                tk.END,
                values=(
                    item["nome"],
                    f"R$ {item['preco']:.2f}",
                    item["quantidade"],
                    f"R$ {item['subtotal']:.2f}",
                    item["codigo_barras"],
                ),
            )
            atualizar_total_venda()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {e}")

    # Função para atualizar o total geral da venda
    def atualizar_total_venda():
        total = sum(item["subtotal"] for item in itens_venda)
        total_formatado = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        label_total.config(text=total_formatado)

    # Botão para adicionar item à venda
    botao_add_item = tk.Button(frame_info, text="Adicionar à Venda", command=adicionar_item_venda, bg="#2980b9", fg="white", font=("Arial", 10, "bold"))
    botao_add_item.grid(row=3, column=4, padx=10, pady=5)
    btn_menos = tk.Label(frame_info, text="-0,100kg", width=8)
    btn_mais = tk.Label(frame_info, text="+0,100kg", width=8)
    
    def carregar_produtos(texto_filtro=""):
        """Carrega os produtos disponíveis no estoque"""
        # Limpar itens anteriores da tabela
        for item_tabela in tabela_produtos.get_children():
            tabela_produtos.delete(item_tabela)
        
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()
        
        # Buscar com filtro ou todos os produtos
        if texto_filtro:
            cursor_banco.execute("""
                SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
                FROM produtos 
                WHERE quantidade > 0 AND nome LIKE ?
                ORDER BY nome ASC
            """, (f"%{texto_filtro}%",))
        else:
            cursor_banco.execute("""
                SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
                FROM produtos 
                WHERE quantidade > 0
                ORDER BY nome ASC
            """)
        
        lista_produtos_disponiveis = cursor_banco.fetchall()
        conexao_banco.close()
        
        # Preencher tabela com produtos
        for dados_produto in lista_produtos_disponiveis:
            id_produto, nome_produto, categoria_produto, quantidade_estoque, preco_unitario, codigo_barras = dados_produto
            preco_formatado = f"R$ {preco_unitario:.2f}"
            tabela_produtos.insert(
                "",
                tk.END,
                values=(
                    id_produto,
                    nome_produto,
                    categoria_produto,
                    quantidade_estoque,
                    preco_formatado,
                    codigo_barras,
                ),
            )
    
    def aplicar_produto_selecionado(id_produto, nome_produto, categoria_produto, quantidade_estoque, preco_unitario, codigo_barras):
        produto_selecionado["id"] = id_produto
        produto_selecionado["nome"] = nome_produto
        produto_selecionado["estoque"] = quantidade_estoque
        produto_selecionado["preco"] = float(preco_unitario)
        produto_selecionado["categoria"] = categoria_produto
        produto_selecionado["codigo_barras"] = codigo_barras

        # Atualizar labels com as informações
        label_produto_selecionado.config(text=produto_selecionado["nome"])
        label_preco.config(text=f"R$ {produto_selecionado['preco']:.2f}")
        categorias_kg = ["carnes", "frios", "padaria", "hortifruti"]
        if categoria_produto.lower() in categorias_kg:
            campo_quantidade.grid_remove()
            campo_kg.grid()
            label_kg.config(text="(Ex: 0,350 para 350g. Digite o peso em kg)")
            label_kg.grid()
            label_estoque.config(text=f"{produto_selecionado['estoque']} kg")
        else:
            campo_quantidade.grid()
            campo_kg.grid_remove()
            label_kg.grid_remove()
            label_estoque.config(text=f"{produto_selecionado['estoque']} unidades")
        calcular_total()

    def ao_selecionar_produto(evento):
        """Atualiza as informações quando um produto é selecionado"""
        item_selecionado = tabela_produtos.selection()
        if item_selecionado:
            dados_item = tabela_produtos.item(item_selecionado[0])
            valores_produto = dados_item['values']
            preco_texto = valores_produto[4].replace("R$ ", "").replace(",", ".")
            aplicar_produto_selecionado(
                valores_produto[0],
                valores_produto[1],
                valores_produto[2],
                valores_produto[3],
                preco_texto,
                valores_produto[5],
            )
    

    # ====== CRIAÇÃO DO LABEL TOTAL =====
    tk.Label(frame_info, text="Total da Compra:", bg="white", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky=tk.W, pady=10)
    label_total = tk.Label(frame_info, text="R$ 0,00", bg="white", font=("Arial", 14, "bold"), fg="#27ae60")
    label_total.grid(row=6, column=1, sticky=tk.W, padx=10, pady=10)

    def calcular_total():
        try:
            if campo_kg.winfo_ismapped():
                quantidade_digitada = float(campo_kg.get().replace(",", "."))
            else:
                quantidade_digitada = int(campo_quantidade.get())
            valor_total = produto_selecionado["preco"] * quantidade_digitada
            # Formatar para padrão brasileiro (R$ 1.234,56)
            total_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            # Mostra o total do item selecionado, não o total geral
        except:
            pass
    
    def buscar_produto(evento=None):
        """Busca produtos conforme o texto digitado"""
        texto_digitado = campo_busca.get()
        carregar_produtos(texto_digitado)

    def buscar_por_codigo(evento=None):
        codigo = campo_codigo_barras.get().strip()
        if not codigo:
            return
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()
        cursor_banco.execute("""
            SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
            FROM produtos 
            WHERE codigo_barras = ?
        """, (codigo,))
        resultado = cursor_banco.fetchone()
        conexao_banco.close()

        if not resultado:
            messagebox.showerror("Erro", "Código de barras não encontrado.")
            campo_codigo_barras.delete(0, tk.END)
            campo_codigo_barras.focus_set()
            return

        id_produto, nome_produto, categoria_produto, quantidade_estoque, preco_unitario, codigo_barras = resultado
        aplicar_produto_selecionado(
            id_produto,
            nome_produto,
            categoria_produto,
            quantidade_estoque,
            preco_unitario,
            codigo_barras,
        )

        categorias_kg = ["carnes", "frios", "padaria", "hortifruti"]
        if categoria_produto.lower() in categorias_kg:
            campo_kg.focus_set()
        else:
            campo_quantidade.delete(0, tk.END)
            campo_quantidade.insert(0, "1")
            adicionar_item_venda()

        campo_codigo_barras.delete(0, tk.END)
        campo_codigo_barras.focus_set()
    

    def registrar_venda():
        """Registra a venda no banco de dados e atualiza o estoque para todos os itens da venda"""
        if not itens_venda:
            messagebox.showerror("Erro", "Adicione pelo menos um item à venda!")
            return
        try:
            conexao_banco = conectar()
            cursor_banco = conexao_banco.cursor()
            data_venda_atual = datetime.now().strftime("%Y-%m-%d")
            total_geral = 0
            for item in itens_venda:
                # Validar estoque
                cursor_banco.execute("SELECT quantidade FROM produtos WHERE id = ?", (item["id"],))
                estoque_atual = cursor_banco.fetchone()
                if not estoque_atual or item["quantidade"] > estoque_atual[0]:
                    messagebox.showerror("Erro", f"Estoque insuficiente para o produto {item['nome']}! Disponível: {estoque_atual[0] if estoque_atual else 0}")
                    conexao_banco.close()
                    return
            # Confirmação
            total_geral = sum(i["subtotal"] for i in itens_venda)
            usuario_confirmou = messagebox.askyesno(
                "Confirmar Venda",
                f"Itens: {len(itens_venda)}\nTotal: R$ {total_geral:.2f}\n\nConfirmar venda?")
            if not usuario_confirmou:
                conexao_banco.close()
                return
            # Registrar cada item
            for item in itens_venda:
                cursor_banco.execute("""
                    INSERT INTO vendas (produto_id, quantidade, data_venda)
                    VALUES (?, ?, ?)
                """, (item["id"], item["quantidade"], data_venda_atual))
                cursor_banco.execute("""
                    UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
                """, (item["quantidade"], item["id"]))
            conexao_banco.commit()
            conexao_banco.close()
            messagebox.showinfo("Sucesso", f"Venda registrada com sucesso!\nTotal: R$ {total_geral:.2f}")
            # Limpar seleção e itens
            produto_selecionado["id"] = None
            produto_selecionado["nome"] = ""
            produto_selecionado["preco"] = 0.0
            produto_selecionado["estoque"] = 0
            produto_selecionado["codigo_barras"] = ""
            itens_venda.clear()
            for i in tabela_venda.get_children():
                tabela_venda.delete(i)
            atualizar_total_venda()
            label_produto_selecionado.config(text="Nenhum produto selecionado")
            label_preco.config(text="R$ 0,00")
            label_estoque.config(text="0 unidades")
            campo_quantidade.delete(0, tk.END)
            campo_quantidade.insert(0, "1")
            campo_kg.delete(0, tk.END)
            campo_kg.insert(0, "0,100")
            carregar_produtos()
        except Exception as erro_exception:
            messagebox.showerror("Erro", f"Erro ao registrar venda: {str(erro_exception)}")
    
    # Vincular eventos aos componentes
    tabela_produtos.bind('<<TreeviewSelect>>', ao_selecionar_produto)
    campo_busca.bind('<KeyRelease>', buscar_produto)
    campo_codigo_barras.bind('<Return>', buscar_por_codigo)
    campo_quantidade.bind('<KeyRelease>', lambda evento: calcular_total())
    campo_kg.bind('<KeyRelease>', lambda evento: calcular_total())

    # Botões
    frame_botoes = tk.Frame(janela_vendas, bg="#f0f0f0")
    frame_botoes.pack(pady=20, padx=20)

    botao_registrar = tk.Button(frame_botoes, text="💰 Registrar Venda", command=registrar_venda, 
                                bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                                padx=35, pady=10, cursor="hand2", relief=tk.RAISED, borderwidth=2)
    botao_registrar.pack(side=tk.LEFT, padx=10)

    botao_cancelar = tk.Button(frame_botoes, text="❌ Cancelar", command=janela_vendas.destroy, 
                               bg="#c0392b", fg="white", font=("Arial", 11, "bold"), 
                               padx=35, pady=10, cursor="hand2", relief=tk.RAISED, borderwidth=2)
    botao_cancelar.pack(side=tk.LEFT, padx=10)

    # Carregar produtos inicialmente
    carregar_produtos()
    campo_codigo_barras.focus_set()
