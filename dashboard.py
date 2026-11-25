from ui_compat import tk, ttk, configurar_tabelas
import cadastro_produto
import estoque
import relatorios
import vendas
from database import conectar
from datetime import datetime, timedelta
from PIL import Image
from customtkinter import CTkImage
from api_client import api_habilitada, dashboard_dados, cadastrar_usuario as api_cadastrar_usuario
import os
import sys
import logging

logger = logging.getLogger(__name__)

def obter_caminho_recurso(arquivo):
    """Obtém o caminho correto do arquivo se está rodando como exe ou script"""
    caminhos_base = []

    if getattr(sys, "frozen", False):
        # PyInstaller
        diretorio_meipass = getattr(sys, "_MEIPASS", None)
        if diretorio_meipass:
            caminhos_base.append(diretorio_meipass)
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

def gerenciar_usuarios():
    """Cadastro administrativo de usuários. A API repete a checagem de permissão."""
    from tkinter import messagebox
    from security import gerar_hash_senha

    janela_usuario = tk.Toplevel()
    janela_usuario.title("Cadastrar usuário")
    janela_usuario.geometry("360x300")
    tk.Label(janela_usuario, text="Novo usuário", font=("Segoe UI", 20, "bold")).pack(pady=12)
    tk.Label(janela_usuario, text="Usuário", font=("Segoe UI", 14)).pack()
    campo_usuario = tk.Entry(janela_usuario, width=300, height=36)
    campo_usuario.pack(pady=4)
    tk.Label(janela_usuario, text="Senha", font=("Segoe UI", 14)).pack()
    campo_senha = tk.Entry(janela_usuario, width=300, height=36, show="*")
    campo_senha.pack(pady=4)
    tk.Label(janela_usuario, text="Perfil", font=("Segoe UI", 14)).pack()
    perfil = tk.StringVar(value="caixa")
    tk.OptionMenu(janela_usuario, variable=perfil, values=("caixa", "admin"), width=220).pack(pady=4)

    def salvar():
        usuario, senha = campo_usuario.get().strip(), campo_senha.get().strip()
        if len(usuario) < 4 or len(senha) < 4:
            messagebox.showerror("Dados inválidos", "Usuário e senha devem ter pelo menos 4 caracteres.", parent=janela_usuario)
            return
        try:
            if api_habilitada():
                api_cadastrar_usuario(usuario, senha, perfil.get())
            else:
                conexao = conectar()
                try:
                    conexao.execute("INSERT INTO funcionarios (usuario, senha, perfil) VALUES (?, ?, ?)",
                                    (usuario, gerar_hash_senha(senha), perfil.get()))
                    conexao.commit()
                finally:
                    conexao.close()
            messagebox.showinfo("Sucesso", "Usuário cadastrado.", parent=janela_usuario)
            janela_usuario.destroy()
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível cadastrar o usuário: {erro}", parent=janela_usuario)

    tk.Button(janela_usuario, text="Cadastrar", command=salvar, bg="#15803d", fg="white",
              font=("Segoe UI", 16, "bold"), height=42, corner_radius=12).pack(pady=14)
    return janela_usuario


def abrir_dashboard():
    logger.info("Abrindo dashboard")
    janela = tk.Tk()
    configurar_tabelas()
    janela.title("Painel de Gestão de Produtos — LucroVision")
    janela.geometry("1100x700")
    try:
        janela.state("zoomed")
    except tk.TclError:
        janela.after(100, lambda: janela.attributes("-zoomed", True))
    janela.configure(bg="#f0f0f0")

    estilo_tabelas = ttk.Style()
    estilo_tabelas.configure("Treeview", rowheight=38, font=("Segoe UI", 12))
    estilo_tabelas.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"))

    # Carregar e redimensionar o logo (com fallback para evitar tela em branco no EXE)
    logo_tk = None
    try:
        caminho_logo = obter_caminho_recurso("Logo.png")
        if os.path.exists(caminho_logo):
            logo_img = Image.open(caminho_logo)
            logo_img = logo_img.resize((108, 108), Image.Resampling.LANCZOS)
            logo_tk = CTkImage(light_image=logo_img, dark_image=logo_img, size=(108, 108))
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
    frame_header = tk.Frame(janela, bg="#FFFFFF", height=120)
    frame_header.pack_propagate(False)
    frame_header.pack(fill=tk.X)
    # A arte já contém o nome LucroVision; mantemos só a imagem no cabeçalho.
    frame_logo = tk.Frame(frame_header, bg="#FFFFFF")
    frame_logo.pack(expand=True)
    if logo_tk is not None:
        label_logo = tk.Label(frame_logo, image=logo_tk, bg="#FFFFFF")
        label_logo.image = logo_tk  # Mantém referência
        label_logo.pack(padx=4, pady=4)
    else:
        tk.Label(frame_logo, text="LV", font=("Segoe UI", 28, "bold"), bg="#FFFFFF", fg="#2c3e50").pack(padx=4, pady=4)

    # ===== FRAME PRINCIPAL =====
    frame_main = tk.Frame(janela, bg="#f0f0f0")
    frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # ===== CARDS DE ESTATÍSTICAS =====
    frame_cards = tk.Frame(frame_main, bg="#f0f0f0")
    frame_cards.pack(fill=tk.X, pady=(0, 20))

    def criar_card(parent, titulo, cor):
        card = tk.Frame(parent, bg=cor, corner_radius=16)
        card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text=titulo, font=("Segoe UI", 16, "bold"), bg=cor, fg="white").pack(pady=(16, 8))
        label_valor = tk.Label(card, text="0", font=("Segoe UI", 27, "bold"), bg=cor, fg="white")
        label_valor.pack(pady=(0, 18))
        
        return label_valor

    label_total_produtos = criar_card(frame_cards, "📦 Total de Produtos", "#2563eb")
    label_estoque_baixo = criar_card(frame_cards, "⚠️ Estoque Baixo", "#dc2626")
    label_total_itens = criar_card(frame_cards, "📊 Total de Itens", "#16a34a")
    label_vendas_mes = criar_card(frame_cards, "💰 Vendas do Mês", "#d97706")

    # Card de valor total
    card_valor = tk.Frame(frame_cards, bg="#7c3aed", corner_radius=16)
    card_valor.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    tk.Label(card_valor, text="Valor em Estoque", font=("Segoe UI", 16, "bold"), bg="#7c3aed", fg="white").pack(pady=(16, 8))
    label_valor_estoque = tk.Label(card_valor, text="R$ 0,00", font=("Segoe UI", 27, "bold"), bg="#7c3aed", fg="white")
    label_valor_estoque.pack(pady=(0, 18))

    # ===== FRAME PARA TABELAS =====
    frame_tabelas = tk.Frame(frame_main, bg="#f0f0f0")
    frame_tabelas.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Coluna esquerda - Mais vendidos
    frame_vendidos = tk.LabelFrame(frame_tabelas, text="🔥 Produtos Mais Vendidos (Últimos 30 dias)", 
                                   font=("Segoe UI", 15, "bold"), bg="white", padx=10, pady=10)
    frame_vendidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    tree_vendidos = ttk.Treeview(frame_vendidos, columns=("Produto", "Quantidade"), show="headings", height=6)
    tree_vendidos.heading("Produto", text="Produto")
    tree_vendidos.heading("Quantidade", text="Qtd Vendida")
    tree_vendidos.column("Produto", width=240, stretch=True)
    tree_vendidos.column("Quantidade", width=110, anchor=tk.CENTER, stretch=False)
    tree_vendidos.pack(fill=tk.BOTH, expand=True)

    # Coluna direita - Próximos ao vencimento
    frame_vencimento = tk.LabelFrame(frame_tabelas, text="⏰ Produtos Próximos ao Vencimento", 
                                     font=("Segoe UI", 15, "bold"), bg="white", padx=10, pady=10)
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
    frame_botoes.pack(fill=tk.X, pady=(8, 0))

    def criar_botao(parent, texto, comando, cor, hover, coluna, linha, reabilitar_ao_fechar=False):
        def _comando_wrapper():
            if reabilitar_ao_fechar:
                btn.config(state=tk.DISABLED)
            try:
                janela_alvo = comando()
            except Exception:
                btn.configure(state=tk.NORMAL)
                raise
            if reabilitar_ao_fechar and isinstance(janela_alvo, tk.Toplevel):
                def _on_destroy(event):
                    if event.widget is janela_alvo:
                        btn.configure(state=tk.NORMAL)
                janela_alvo.bind("<Destroy>", _on_destroy, add="+")
            elif reabilitar_ao_fechar:
                btn.configure(state=tk.NORMAL)

        btn = tk.Button(parent, text=texto, command=_comando_wrapper, bg=cor, fg="white",
                       font=("Segoe UI", 18, "bold"), width=250, height=58,
                       corner_radius=16, hover_color=hover)
        btn.grid(row=linha, column=coluna, padx=8, pady=8, sticky="ew")
        return btn

    for coluna in range(4):
        frame_botoes.grid_columnconfigure(coluna, weight=1, uniform="acoes")
    criar_botao(frame_botoes, "Registrar vendas", vendas.tela_vendas, "#d97706", "#b45309", 0, 0, True)
    criar_botao(frame_botoes, "Cadastrar produtos", cadastro_produto.tela_cadastro, "#15803d", "#166534", 1, 0, True)
    criar_botao(frame_botoes, "Ver estoque", estoque.tela_estoque, "#2563eb", "#1d4ed8", 2, 0, True)
    criar_botao(frame_botoes, "Relatórios", relatorios.tela_relatorios, "#7c3aed", "#6d28d9", 3, 0, True)
    criar_botao(frame_botoes, "Usuários", gerenciar_usuarios, "#475569", "#334155", 0, 1, True)
    criar_botao(frame_botoes, "Atualizar dados", atualizar_dashboard, "#b45309", "#92400e", 1, 1)
    criar_botao(frame_botoes, "Sair do sistema", janela.destroy, "#b91c1c", "#991b1b", 2, 1)

    # Atualizar dashboard ao abrir
    atualizar_dashboard()

    janela.mainloop()
