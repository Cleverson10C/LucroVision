import tkinter as tk
from tkinter import ttk
import cadastro_produto
import estoque
import relatorios
import vendas
from database import conectar
from datetime import datetime, timedelta
from tkinter import PhotoImage
from PIL import Image, ImageTk
from api_client import api_habilitada, dashboard_dados
import os
import sys
import logging

logger = logging.getLogger(__name__)

def obter_caminho_recurso(arquivo):
    """Obtém o caminho correto do arquivo se está rodando como exe ou script"""
    caminhos_base = []

    if getattr(sys, "frozen", False):
        # PyInstaller
        if hasattr(sys, "_MEIPASS"):
            caminhos_base.append(sys._MEIPASS)
        # cx_Freeze (ou fallback em executável)
        caminhos_base.append(os.path.dirname(sys.executable))

    # Execução normal em script
    caminhos_base.append(os.path.dirname(os.path.abspath(__file__)))
    caminhos_base.append(os.getcwd())

    for base in caminhos_base:
        caminho = os.path.join(base, arquivo)
        if os.path.exists(caminho):
            logger.debug("Recurso '%s' encontrado em %s", arquivo, caminho)
            return caminho

    # Fallback: mantém comportamento previsível se não encontrar o arquivo
    fallback = os.path.join(caminhos_base[0], arquivo)
    logger.warning("Recurso '%s' nao encontrado. Usando fallback %s", arquivo, fallback)
    return fallback

def abrir_dashboard():
    logger.info("Abrindo dashboard")
    janela = tk.Tk()
    janela.title("Painel de Gestão de Produtos — LucroVision")
    janela.geometry("1100x700")
    # janela.resizable(True, True)
    janela.configure(bg="#f0f0f0")

    # Carregar e redimensionar o logo (com fallback para evitar tela em branco no EXE)
    logo_tk = None
    try:
        caminho_logo = obter_caminho_recurso("Logo.png")
        if os.path.exists(caminho_logo):
            logo_img = Image.open(caminho_logo)
            logo_img = logo_img.resize((80, 80), Image.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_img)
            logger.info("Logo carregada com sucesso de %s", caminho_logo)
    except Exception:
        logger.exception("Falha ao carregar logo")
        logo_tk = None

    # Função para atualizar dados
    def atualizar_dashboard():
        from tkinter import messagebox
        conn = None
        try:
            logger.info("Atualizando indicadores do dashboard")
            if api_habilitada():
                dados = dashboard_dados()
                total_produtos = dados["total_produtos"]
                estoque_baixo = dados["estoque_baixo"]
                total_itens = dados["total_itens"]
                vendas_mes = dados["vendas_mes"]
                valor_estoque = dados["valor_estoque"]
                mais_vendidos = [(item["produto"], item["quantidade"]) for item in dados["mais_vendidos"]]
                proximos_vencimento = [
                    (item["produto"], item["validade"], item["quantidade"])
                    for item in dados["proximos_vencimento"]
                ]
            else:
                conn = conectar()
                cursor = conn.cursor()

                # Total de produtos
                cursor.execute("SELECT COUNT(*) FROM produtos")
                total_produtos = cursor.fetchone()[0]

                # Produtos com estoque baixo
                cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo")
                estoque_baixo = cursor.fetchone()[0]

                # Total de itens em estoque
                cursor.execute("SELECT SUM(quantidade) FROM produtos")
                total_itens = cursor.fetchone()[0] or 0

                # Vendas do mês
                primeiro_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
                cursor.execute("SELECT COUNT(*) FROM vendas WHERE data_venda >= ?", (primeiro_dia_mes,))
                vendas_mes = cursor.fetchone()[0]

                # Valor total em estoque
                cursor.execute("SELECT SUM(quantidade * preco_venda) FROM produtos")
                valor_estoque = cursor.fetchone()[0] or 0

                # Produtos mais vendidos (últimos 30 dias)
                data_30_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                cursor.execute("""
                    SELECT p.nome, SUM(v.quantidade) as total
                    FROM vendas v
                    JOIN produtos p ON v.produto_id = p.id
                    WHERE v.data_venda >= ?
                    GROUP BY p.nome
                    ORDER BY total DESC
                """, (data_30_dias,))
                mais_vendidos = cursor.fetchall()

                # Produtos próximos ao vencimento (mês atual + 1 mês)
                hoje = datetime.now()
                proximo_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)
                ano_mes_limite = proximo_mes.strftime("%Y-%m")
                cursor.execute("""
                    SELECT nome, validade, quantidade
                    FROM produtos
                    WHERE validade <= ?
                    ORDER BY validade ASC
                    LIMIT 30
                """, (ano_mes_limite,))
                proximos_vencimento = cursor.fetchall()

            label_total_produtos.config(text=str(total_produtos))
            label_estoque_baixo.config(text=str(estoque_baixo))
            label_total_itens.config(text=str(total_itens))
            label_vendas_mes.config(text=str(vendas_mes))
            label_valor_estoque.config(text=f"R$ {valor_estoque:,.2f}")

            # Limpar lista de mais vendidos
            for item in tree_vendidos.get_children():
                tree_vendidos.delete(item)

            for produto, quantidade in mais_vendidos:
                tree_vendidos.insert("", tk.END, values=(produto, quantidade))

            # Limpar lista de vencimentos
            for item in tree_vencimento.get_children():
                tree_vencimento.delete(item)

            for produto, validade, qtd in proximos_vencimento:
                # Formatar validade para MM/YYYY
                validade_formatada = ""
                if validade:
                    try:
                        partes = validade.split("-")
                        validade_formatada = f"{partes[1]}/{partes[0]}"
                    except Exception:
                        validade_formatada = validade
                tree_vencimento.insert("", tk.END, values=(produto, validade_formatada, qtd))
            logger.info(
                "Dashboard atualizado: total_produtos=%s, estoque_baixo=%s, total_itens=%s, vendas_mes=%s",
                total_produtos,
                estoque_baixo,
                total_itens,
                vendas_mes,
            )
        except Exception as erro:
            logger.exception("Falha ao atualizar dashboard: %s", erro)
            messagebox.showerror("Erro", f"Falha ao atualizar dashboard: {erro}")
        finally:
            if conn is not None:
                conn.close()

    # ===== CABEÇALHO =====
    frame_header = tk.Frame(janela, bg="#FFFFFF", height=80)
    frame_header.pack(fill=tk.X)
    # Frame para destacar a logo (sem borda)
    frame_logo = tk.Frame(frame_header, bg="#FFFFFF")
    frame_logo.pack(side=tk.LEFT, padx=8, pady=2)
    if logo_tk is not None:
        label_logo = tk.Label(frame_logo, image=logo_tk, bg="#FFFFFF")
        label_logo.image = logo_tk  # Mantém referência
        label_logo.pack(padx=2, pady=2)
    else:
        tk.Label(frame_logo, text="LV", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#2c3e50").pack(padx=2, pady=2)
    # Frame para centralizar texto
    frame_texto = tk.Frame(frame_header, bg="#FFFFFF")
    frame_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    tk.Label(frame_texto, text="Painel de Gestão de Produtos", 
             font=("Arial", 18,"bold"), bg="#FFFFFF", fg="#000000").pack(expand=True, pady=2)

    # ===== FRAME PRINCIPAL =====
    frame_main = tk.Frame(janela, bg="#f0f0f0")
    frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # ===== CARDS DE ESTATÍSTICAS =====
    frame_cards = tk.Frame(frame_main, bg="#f0f0f0")
    frame_cards.pack(fill=tk.X, pady=(0, 20))

    def criar_card(parent, titulo, valor_var, cor):
        card = tk.Frame(parent, bg=cor, relief=tk.RAISED, borderwidth=2)
        card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text=titulo, font=("Arial", 10), bg=cor, fg="white").pack(pady=(10, 5))
        label_valor = tk.Label(card, text="0", font=("Arial", 18, "bold"), bg=cor, fg="white")
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
    tree_vendidos.column("Produto", width=240, stretch=True)
    tree_vendidos.column("Quantidade", width=110, anchor=tk.CENTER, stretch=False)
    tree_vendidos.pack(fill=tk.BOTH, expand=True)

    # Coluna direita - Próximos ao vencimento
    frame_vencimento = tk.LabelFrame(frame_tabelas, text="⏰ Produtos Próximos ao Vencimento", 
                                     font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
    frame_vencimento.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree_vencimento = ttk.Treeview(frame_vencimento, columns=("Produto", "Validade", "Estoque"), show="headings", height=6)
    tree_vencimento.heading("Produto", text="Produto")
    tree_vencimento.heading("Validade", text="Validade")
    tree_vencimento.heading("Estoque", text="Estoque")
    tree_vencimento.column("Produto", width=220, stretch=True)
    tree_vencimento.column("Validade", width=110, anchor=tk.CENTER, stretch=False)
    tree_vencimento.column("Estoque", width=90, anchor=tk.CENTER, stretch=False)
    tree_vencimento.pack(fill=tk.BOTH, expand=True)

    # ===== BOTÕES DE AÇÃO =====
    frame_botoes = tk.Frame(frame_main, bg="#f0f0f0")
    frame_botoes.pack(fill=tk.X)

    def criar_botao(parent, texto, comando, cor, desabilitar_apos_clique=False, reabilitar_ao_fechar=False):
        def _comando_wrapper():
            if desabilitar_apos_clique:
                btn.config(state=tk.DISABLED)
            filhos_antes = set(janela.winfo_children())
            root_antes = getattr(tk, "_default_root", None)
            resultado = comando()
            if reabilitar_ao_fechar:
                janela_alvo = None
                if isinstance(resultado, (tk.Toplevel, tk.Tk)):
                    janela_alvo = resultado
                else:
                    filhos_depois = set(janela.winfo_children())
                    novas_janelas = [
                        w for w in filhos_depois
                        if w not in filhos_antes and isinstance(w, tk.Toplevel)
                    ]
                    if novas_janelas:
                        janela_alvo = novas_janelas[-1]
                    else:
                        root_depois = getattr(tk, "_default_root", None)
                        if root_depois is not root_antes and isinstance(root_depois, tk.Tk):
                            janela_alvo = root_depois

                if janela_alvo is not None:
                    def _on_destroy(event):
                        if event.widget is janela_alvo:
                            btn.config(state=tk.NORMAL)

                    janela_alvo.bind("<Destroy>", _on_destroy)
                elif desabilitar_apos_clique:
                    btn.config(state=tk.NORMAL)

        btn = tk.Button(parent, text=texto, command=_comando_wrapper, bg=cor, fg="white", 
                       font=("Arial", 9, "bold"), relief=tk.RAISED, borderwidth=2,
                       cursor="hand2", padx=10, pady=8, wraplength=100)
        btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
        return btn

    criar_botao(frame_botoes, "💰 Registrar Venda", vendas.tela_vendas, "#e67e22", desabilitar_apos_clique=True, reabilitar_ao_fechar=True)
    criar_botao(frame_botoes, "➕ Cadastrar Produto", cadastro_produto.tela_cadastro, "#27ae60", desabilitar_apos_clique=True, reabilitar_ao_fechar=True)
    criar_botao(frame_botoes, "📦 Ver Estoque", estoque.tela_estoque, "#2980b9", desabilitar_apos_clique=True, reabilitar_ao_fechar=True)
    criar_botao(frame_botoes, "📊 Relatórios", relatorios.tela_relatorios, "#8e44ad", desabilitar_apos_clique=True, reabilitar_ao_fechar=True)
    criar_botao(frame_botoes, "🔄 Atualizar Dados", atualizar_dashboard, "#f39c12")
    criar_botao(frame_botoes, "🚪 Sair do Sistema", janela.destroy, "#c0392b")

    # Atualizar dashboard ao abrir
    atualizar_dashboard()

    janela.mainloop()
