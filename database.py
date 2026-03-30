import sqlite3
import os
import sys

NOME_APP = "LucroVisor"
NOME_BANCO = "comercio.db"


def _normalizar_categoria(categoria):
    if categoria is None:
        return ""
    categoria_limpa = " ".join(categoria.strip().split())
    return categoria_limpa.title()


def _obter_diretorio_dados():
    """
    Retorna um diretório persistente para armazenar dados do aplicativo.
    - Executável: usa %LOCALAPPDATA%\\LucroVisor
    - Script Python: usa o diretório do arquivo .py
    """
    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            diretorio = os.path.join(local_app_data, NOME_APP)
        else:
            diretorio = os.path.dirname(sys.executable)
    else:
        diretorio = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(diretorio, exist_ok=True)
    return diretorio


def _caminho_banco():
    caminho_personalizado = os.environ.get("LUCROVISOR_DB_PATH", "").strip()
    if caminho_personalizado:
        caminho_absoluto = os.path.abspath(caminho_personalizado)
        pasta_banco = os.path.dirname(caminho_absoluto)
        if pasta_banco:
            os.makedirs(pasta_banco, exist_ok=True)
        return caminho_absoluto
    return os.path.join(_obter_diretorio_dados(), NOME_BANCO)

def conectar():
    """Conecta ao banco de dados SQLite da comercio"""
    return sqlite3.connect(_caminho_banco())

def criar_tabelas():
    """Cria todas as tabelas necessárias no banco de dados"""
    conexao_banco = conectar()
    cursor_banco = conexao_banco.cursor()

    # Tabela de controle de acesso do sistema
    cursor_banco.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )""")

    # Tabela de produtos em estoque
    cursor_banco.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        codigo_barras TEXT UNIQUE,
        categoria TEXT,
        preco_custo REAL,
        preco_venda REAL,
        quantidade INTEGER,
        estoque_minimo INTEGER,
        validade TEXT
    )""")

    # Tabela de vendas realizadas
    cursor_banco.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        data_venda TEXT,
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )""")

    # Migração de dados legados:
    # registros antigos podem ter codigo_barras vazio ("").
    # Com UNIQUE, isso causa conflito em novos cadastros sem código.
    cursor_banco.execute("""
    UPDATE produtos
    SET codigo_barras = NULL
    WHERE TRIM(COALESCE(codigo_barras, '')) = ''
    """)

    # Migração de categorias:
    # padroniza capitalização e remove espaços extras para evitar duplicidade visual.
    cursor_banco.execute("SELECT id, categoria FROM produtos")
    for produto_id, categoria in cursor_banco.fetchall():
        categoria_padronizada = _normalizar_categoria(categoria)
        if (categoria or "") != categoria_padronizada:
            cursor_banco.execute(
                "UPDATE produtos SET categoria = ? WHERE id = ?",
                (categoria_padronizada, produto_id),
            )

    conexao_banco.commit()
    conexao_banco.close()
