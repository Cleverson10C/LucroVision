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
    janela_vendas.geometry("700x650")
    janela_vendas.configure(bg="#f0f0f0")
    
    # Frame superior - Seleção de produto
    frame_superior = tk.LabelFrame(janela_vendas, text="Selecionar Produto", 
                                   font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
    frame_superior.pack(pady=10, padx=20, fill=tk.X)
    
    # Campo de busca
    tk.Label(frame_superior, text="Buscar produto:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
    campo_busca = tk.Entry(frame_superior, width=40, font=("Arial", 10))
    campo_busca.grid(row=0, column=1, padx=10, pady=5)
    
    # Lista de produtos disponíveis
    tk.Label(frame_superior, text="Produtos disponíveis:", bg="white", font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
    
    frame_lista = tk.Frame(frame_superior, bg="white")
    frame_lista.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
    
    scrollbar_produtos = tk.Scrollbar(frame_lista)
    scrollbar_produtos.pack(side=tk.RIGHT, fill=tk.Y)
    
    colunas_produtos = ("ID", "Nome", "Categoria", "Estoque", "Preço")
    tabela_produtos = ttk.Treeview(frame_lista, columns=colunas_produtos, show="headings", 
                                   height=6, yscrollcommand=scrollbar_produtos.set)
    scrollbar_produtos.config(command=tabela_produtos.yview)
    
    tabela_produtos.heading("ID", text="ID")
    tabela_produtos.heading("Nome", text="Nome do Produto")
    tabela_produtos.heading("Categoria", text="Categoria")
    tabela_produtos.heading("Estoque", text="Estoque")
    tabela_produtos.heading("Preço", text="Preço Unit.")
    
    tabela_produtos.column("ID", width=40, anchor=tk.CENTER)
    tabela_produtos.column("Nome", width=250)
    tabela_produtos.column("Categoria", width=120)
    tabela_produtos.column("Estoque", width=80, anchor=tk.CENTER)
    tabela_produtos.column("Preço", width=100, anchor=tk.CENTER)
    
    tabela_produtos.pack(fill=tk.BOTH, expand=True)
    
    # Frame de informações do produto selecionado
    frame_info = tk.LabelFrame(janela_vendas, text="Informações da Venda", 
                               font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
    frame_info.pack(pady=10, padx=20, fill=tk.X)
    
    # Variáveis para armazenar informações
    produto_selecionado = {"id": None, "nome": "", "preco": 0.0, "estoque": 0}
    
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
    btn_menos = tk.Button(frame_info, text="-0,100kg", command=lambda: ajustar_kg(-0.1), width=8)
    btn_mais = tk.Button(frame_info, text="+0,100kg", command=lambda: ajustar_kg(0.1), width=8)
    btn_menos.grid(row=3, column=4, padx=2)
    btn_mais.grid(row=3, column=5, padx=2)
    btn_menos.grid_remove()
    btn_mais.grid_remove()
    
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
                SELECT id, nome, categoria, quantidade, preco_venda 
                FROM produtos 
                WHERE quantidade > 0 AND nome LIKE ?
                ORDER BY nome ASC
            """, (f"%{texto_filtro}%",))
        else:
            cursor_banco.execute("""
                SELECT id, nome, categoria, quantidade, preco_venda 
                FROM produtos 
                WHERE quantidade > 0
                ORDER BY nome ASC
            """)
        
        lista_produtos_disponiveis = cursor_banco.fetchall()
        conexao_banco.close()
        
        # Preencher tabela com produtos
        for dados_produto in lista_produtos_disponiveis:
            id_produto, nome_produto, categoria_produto, quantidade_estoque, preco_unitario = dados_produto
            preco_formatado = f"R$ {preco_unitario:.2f}"
            tabela_produtos.insert("", tk.END, values=(id_produto, nome_produto, categoria_produto, quantidade_estoque, preco_formatado))
    
    def ao_selecionar_produto(evento):
        """Atualiza as informações quando um produto é selecionado"""
        item_selecionado = tabela_produtos.selection()
        if item_selecionado:
            dados_item = tabela_produtos.item(item_selecionado[0])
            valores_produto = dados_item['values']
            
            # Armazenar informações do produto selecionado
            produto_selecionado["id"] = valores_produto[0]
            produto_selecionado["nome"] = valores_produto[1]
            produto_selecionado["estoque"] = valores_produto[3]
            preco_texto = valores_produto[4].replace("R$ ", "").replace(",", ".")
            produto_selecionado["preco"] = float(preco_texto)
            
            # Atualizar labels com as informações
            label_produto_selecionado.config(text=produto_selecionado["nome"])
            label_preco.config(text=valores_produto[4])
            # Verifica se é categoria que usa kg
            categorias_kg = ["carnes", "frios", "padaria", "hortifruti"]
            if valores_produto[2].lower() in categorias_kg:
                campo_quantidade.grid_remove()
                campo_kg.grid()
                label_kg.config(text="(Ex: 0,350 para 350g. Digite o peso em kg)")
                label_kg.grid()
                btn_menos.grid()
                btn_mais.grid()
                label_estoque.config(text=f"{produto_selecionado['estoque']} kg")
            else:
                campo_quantidade.grid()
                campo_kg.grid_remove()
                label_kg.grid_remove()
                btn_menos.grid_remove()
                btn_mais.grid_remove()
                label_estoque.config(text=f"{produto_selecionado['estoque']} unidades")
            calcular_total()
    
    # ====== CRIAÇÃO DO LABEL TOTAL =====
    tk.Label(frame_info, text="Total:", bg="white", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky=tk.W, pady=10)
    label_total = tk.Label(frame_info, text="R$ 0,00", bg="white", font=("Arial", 14, "bold"), fg="#27ae60")
    label_total.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
    
    def calcular_total():
        nonlocal label_total
        try:
            if campo_kg.winfo_ismapped():
                quantidade_digitada = float(campo_kg.get().replace(",", "."))
            else:
                quantidade_digitada = int(campo_quantidade.get())
            valor_total = produto_selecionado["preco"] * quantidade_digitada
            # Formatar para padrão brasileiro (R$ 1.234,56)
            total_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            label_total.config(text=total_formatado)
        except:
            label_total.config(text="R$ 0,00")
    
    def buscar_produto(evento=None):
        """Busca produtos conforme o texto digitado"""
        texto_digitado = campo_busca.get()
        carregar_produtos(texto_digitado)
    
    def registrar_venda():
        """Registra a venda no banco de dados e atualiza o estoque"""
        # Validar se há produto selecionado
        if not produto_selecionado["id"]:
            messagebox.showerror("Erro", "Selecione um produto para vender!")
            return
        
        try:
            if campo_kg.winfo_ismapped():
                quantidade_para_vender = float(campo_kg.get().replace(",", "."))
            else:
                quantidade_para_vender = int(campo_quantidade.get())
            
            # Validar quantidade
            if quantidade_para_vender <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!")
                return
            
            # Validar estoque disponível
            estoque_disponivel = produto_selecionado["estoque"]
            if quantidade_para_vender > estoque_disponivel:
                if campo_kg.winfo_ismapped():
                    messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {estoque_disponivel} kg")
                else:
                    messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {estoque_disponivel} unidades")
                return
            
            # Calcular total e confirmar venda
            preco_unitario = produto_selecionado["preco"]
            valor_total_venda = preco_unitario * quantidade_para_vender
            
            usuario_confirmou = messagebox.askyesno(
                "Confirmar Venda",
                f"Produto: {produto_selecionado['nome']}\n"
                f"Quantidade: {quantidade_para_vender}\n"
                f"Total: R$ {valor_total_venda:.2f}\n\n"
                f"Confirmar venda?"
            )
            
            if not usuario_confirmou:
                return
            

            # Conectar ao banco e registrar venda
            conexao_banco = conectar()
            cursor_banco = conexao_banco.cursor()

            # Inserir registro de venda
            data_venda_atual = datetime.now().strftime("%Y-%m-%d")
            cursor_banco.execute("""
                INSERT INTO vendas (produto_id, quantidade, data_venda)
                VALUES (?, ?, ?)
            """, (produto_selecionado["id"], quantidade_para_vender, data_venda_atual))

            # Atualizar quantidade em estoque
            cursor_banco.execute("""
                UPDATE produtos 
                SET quantidade = quantidade - ?
                WHERE id = ?
            """, (quantidade_para_vender, produto_selecionado["id"]))

            conexao_banco.commit()
            conexao_banco.close()
            
            # Exibir mensagem de sucesso
            messagebox.showinfo("Sucesso", f"Venda registrada com sucesso!\nTotal: R$ {valor_total_venda:.2f}")
            
            # Limpar seleção atual
            produto_selecionado["id"] = None
            produto_selecionado["nome"] = ""
            produto_selecionado["preco"] = 0.0
            produto_selecionado["estoque"] = 0
            
            # Resetar interface
            label_produto_selecionado.config(text="Nenhum produto selecionado")
            label_preco.config(text="R$ 0,00")
            label_estoque.config(text="0 unidades")
            label_total.config(text="R$ 0,00")
            campo_quantidade.delete(0, tk.END)
            campo_quantidade.insert(0, "1")
            campo_kg.delete(0, tk.END)
            campo_kg.insert(0, "0,100")
            
            # Recarregar lista de produtos
            carregar_produtos()
            
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida!")
        except Exception as erro_exception:
            messagebox.showerror("Erro", f"Erro ao registrar venda: {str(erro_exception)}")
    
    # Vincular eventos aos componentes
    tabela_produtos.bind('<<TreeviewSelect>>', ao_selecionar_produto)
    campo_busca.bind('<KeyRelease>', buscar_produto)
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
