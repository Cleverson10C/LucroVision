import tkinter as tk
from tkinter import ttk
import cadastro_produto
import estoque
import relatorios
import vendas
from database import conectar
from datetime import datetime, timedelta

def abrir_dashboard():
    janela = tk.Tk()
    janela.title("Dashboard - Sistema de Gerenciamento de Produtos")
    janela.geometry("900x700")
    # janela.resizable(True, True)
    janela.configure(bg="#f0f0f0")

    # Função para atualizar dados
    def atualizar_dashboard():
        conn = conectar()
        cursor = conn.cursor()
        
        # Total de produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        label_total_produtos.config(text=str(total_produtos))
        
        # Produtos com estoque baixo
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo")
        estoque_baixo = cursor.fetchone()[0]
        label_estoque_baixo.config(text=str(estoque_baixo))
        
        # Total de itens em estoque
        cursor.execute("SELECT SUM(quantidade) FROM produtos")
        total_itens = cursor.fetchone()[0] or 0
        label_total_itens.config(text=str(total_itens))
        
        # Vendas do mês
        primeiro_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM vendas WHERE data_venda >= ?", (primeiro_dia_mes,))
        vendas_mes = cursor.fetchone()[0]
        label_vendas_mes.config(text=str(vendas_mes))
        
        # Valor total em estoque
        cursor.execute("SELECT SUM(quantidade * preco_venda) FROM produtos")
        valor_estoque = cursor.fetchone()[0] or 0
        label_valor_estoque.config(text=f"R$ {valor_estoque:,.2f}")
        
        # Produtos mais vendidos (últimos 30 dias)
        data_30_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT p.nome, SUM(v.quantidade) as total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            WHERE v.data_venda >= ?
            GROUP BY p.nome
            ORDER BY total DESC
            LIMIT 5
        """, (data_30_dias,))
        mais_vendidos = cursor.fetchall()
        
        # Limpar lista de mais vendidos
        for item in tree_vendidos.get_children():
            tree_vendidos.delete(item)
        
        for produto, quantidade in mais_vendidos:
            tree_vendidos.insert("", tk.END, values=(produto, quantidade))
        
        # Produtos próximos ao vencimento (próximos 60 dias)
        data_60_dias = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT nome, validade, quantidade
            FROM produtos
            WHERE validade <= ?
            ORDER BY validade ASC
            LIMIT 5
        """, (data_60_dias,))
        proximos_vencimento = cursor.fetchall()
        
        # Limpar lista de vencimentos
        for item in tree_vencimento.get_children():
            tree_vencimento.delete(item)
        
        for produto, validade, qtd in proximos_vencimento:
            tree_vencimento.insert("", tk.END, values=(produto, validade, qtd))
        
        conn.close()

    # ===== CABEÇALHO =====
    frame_header = tk.Frame(janela, bg="#2c3e50", height=80)
    frame_header.pack(fill=tk.X)
    
    tk.Label(frame_header, text="🏥 Dashboard - Sistema de Gerenciamento de Produtos", 
             font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

    # ===== FRAME PRINCIPAL =====
    frame_main = tk.Frame(janela, bg="#f0f0f0")
    frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # ===== CARDS DE ESTATÍSTICAS =====
    frame_cards = tk.Frame(frame_main, bg="#f0f0f0")
    frame_cards.pack(fill=tk.X, pady=(0, 20))

    def criar_card(parent, titulo, valor_var, cor):
        card = tk.Frame(parent, bg=cor, relief=tk.RAISED, borderwidth=2)
        card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text=titulo, font=("Arial", 10), bg=cor, fg="white").pack(pady=(15, 5))
        label_valor = tk.Label(card, text="0", font=("Arial", 24, "bold"), bg=cor, fg="white")
        label_valor.pack(pady=(0, 15))
        
        return label_valor

    label_total_produtos = criar_card(frame_cards, "📦 Total de Produtos", "0", "#3498db")
    label_estoque_baixo = criar_card(frame_cards, "⚠️ Estoque Baixo", "0", "#e74c3c")
    label_total_itens = criar_card(frame_cards, "📊 Total de Itens", "0", "#2ecc71")
    label_vendas_mes = criar_card(frame_cards, "💰 Vendas do Mês", "0", "#f39c12")

    # Card de valor total
    card_valor = tk.Frame(frame_cards, bg="#9b59b6", relief=tk.RAISED, borderwidth=2)
    card_valor.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    tk.Label(card_valor, text="💵 Valor em Estoque", font=("Arial", 10), bg="#9b59b6", fg="white").pack(pady=(15, 5))
    label_valor_estoque = tk.Label(card_valor, text="R$ 0,00", font=("Arial", 18, "bold"), bg="#9b59b6", fg="white")
    label_valor_estoque.pack(pady=(0, 15))

    # ===== FRAME PARA TABELAS =====
    frame_tabelas = tk.Frame(frame_main, bg="#f0f0f0")
    frame_tabelas.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Coluna esquerda - Mais vendidos
    frame_vendidos = tk.LabelFrame(frame_tabelas, text="🔥 Produtos Mais Vendidos (Últimos 30 dias)", 
                                   font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
    frame_vendidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    tree_vendidos = ttk.Treeview(frame_vendidos, columns=("Produto", "Quantidade"), show="headings", height=6)
    tree_vendidos.heading("Produto", text="Produto")
    tree_vendidos.heading("Quantidade", text="Qtd Vendida")
    tree_vendidos.column("Produto", width=200)
    tree_vendidos.column("Quantidade", width=100, anchor=tk.CENTER)
    tree_vendidos.pack(fill=tk.BOTH, expand=True)

    # Coluna direita - Próximos ao vencimento
    frame_vencimento = tk.LabelFrame(frame_tabelas, text="⏰ Produtos Próximos ao Vencimento", 
                                     font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
    frame_vencimento.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree_vencimento = ttk.Treeview(frame_vencimento, columns=("Produto", "Validade", "Estoque"), show="headings", height=6)
    tree_vencimento.heading("Produto", text="Produto")
    tree_vencimento.heading("Validade", text="Validade")
    tree_vencimento.heading("Estoque", text="Estoque")
    tree_vencimento.column("Produto", width=180)
    tree_vencimento.column("Validade", width=100, anchor=tk.CENTER)
    tree_vencimento.column("Estoque", width=80, anchor=tk.CENTER)
    tree_vencimento.pack(fill=tk.BOTH, expand=True)

    # ===== BOTÕES DE AÇÃO =====
    frame_botoes = tk.Frame(frame_main, bg="#f0f0f0")
    frame_botoes.pack(fill=tk.X)

    def criar_botao(parent, texto, comando, cor):
        btn = tk.Button(parent, text=texto, command=comando, bg=cor, fg="white", 
                       font=("Arial", 9, "bold"), relief=tk.RAISED, borderwidth=2,
                       cursor="hand2", padx=10, pady=8, wraplength=100)
        btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
        return btn

    criar_botao(frame_botoes, "💰 Registrar Venda", vendas.tela_vendas, "#e67e22")
    criar_botao(frame_botoes, "➕ Cadastrar Produto", cadastro_produto.tela_cadastro, "#27ae60")
    criar_botao(frame_botoes, "📦 Ver Estoque", estoque.tela_estoque, "#2980b9")
    criar_botao(frame_botoes, "📊 Relatórios", relatorios.tela_relatorios, "#8e44ad")
    criar_botao(frame_botoes, "🔄 Atualizar Dados", atualizar_dashboard, "#f39c12")
    criar_botao(frame_botoes, "🚪 Sair do Sistema", janela.destroy, "#c0392b")

    # Atualizar dashboard ao abrir
    atualizar_dashboard()

    janela.mainloop()