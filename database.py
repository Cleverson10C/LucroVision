import sqlite3

def conectar():
    """Conecta ao banco de dados SQLite da comercio"""
    return sqlite3.connect("comercio.db")

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

    conexao_banco.commit()
    conexao_banco.close()