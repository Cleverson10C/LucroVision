import logging
from datetime import datetime, timedelta
import secrets
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from database import conectar, criar_tabelas, iniciar_backups_automaticos
from security import gerar_hash_senha, verificar_hash_senha

logger = logging.getLogger("lucrovision.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="LucroVision API", version="1.0.0")
_sessoes = {}
_bearer = HTTPBearer(auto_error=False)


def _usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(_bearer)):
    usuario = _sessoes.get(credenciais.credentials) if credenciais else None
    if not usuario:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    return usuario


def _exigir_admin(usuario=Depends(_usuario_atual)):
    if usuario["perfil"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador.")
    return usuario


class LoginIn(BaseModel):
    usuario: str
    senha: str


class RegisterIn(BaseModel):
    usuario: str
    senha: str
    perfil: str = "caixa"


class VendaItemIn(BaseModel):
    id: int
    quantidade: float
    subtotal: float


class VendaIn(BaseModel):
    itens: List[VendaItemIn]
    data_venda: str


class ProdutoIn(BaseModel):
    nome: str
    categoria: str
    codigo_barras: Optional[str] = None
    preco_custo: float
    preco_venda: float
    quantidade: float
    estoque_minimo: float
    validade: str


def _normalizar_categoria(categoria_texto: str) -> str:
    categoria_limpa = " ".join(categoria_texto.strip().split())
    return categoria_limpa.title()


@app.on_event("startup")
def startup_event():
    criar_tabelas()
    iniciar_backups_automaticos()
    logger.info("API inicializada")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def auth_login(payload: LoginIn):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute("SELECT id, senha, perfil FROM funcionarios WHERE usuario=?", (payload.usuario,))
    row = cursor.fetchone()
    if not row:
        conexao_banco.close()
        return {"autenticado": False}

    funcionario_id, senha_armazenada, perfil = row
    senha_armazenada = senha_armazenada or ""

    if "$" in senha_armazenada and verificar_hash_senha(payload.senha, senha_armazenada):
        conexao_banco.close()
        token = secrets.token_urlsafe(32)
        _sessoes[token] = {"id": funcionario_id, "usuario": payload.usuario, "perfil": perfil or "caixa"}
        return {"autenticado": True, "access_token": token, "perfil": perfil or "caixa"}

    if senha_armazenada == payload.senha:
        cursor.execute("UPDATE funcionarios SET senha=? WHERE id=?", (gerar_hash_senha(payload.senha), funcionario_id))
        conexao_banco.commit()
        conexao_banco.close()
        token = secrets.token_urlsafe(32)
        _sessoes[token] = {"id": funcionario_id, "usuario": payload.usuario, "perfil": perfil or "caixa"}
        return {"autenticado": True, "access_token": token, "perfil": perfil or "caixa"}

    conexao_banco.close()
    return {"autenticado": False}


@app.post("/auth/logout")
def auth_logout(credenciais: HTTPAuthorizationCredentials = Depends(_bearer)):
    if credenciais:
        _sessoes.pop(credenciais.credentials, None)
    return {"ok": True}


@app.get("/auth/bootstrap-status")
def auth_bootstrap_status():
    conexao_banco = conectar()
    try:
        total = conexao_banco.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0]
        return {"necessario": total == 0}
    finally:
        conexao_banco.close()


@app.post("/auth/register")
def auth_register(payload: RegisterIn, credenciais: HTTPAuthorizationCredentials = Depends(_bearer)):
    usuario = payload.usuario.strip()
    senha = payload.senha.strip()

    if len(usuario) < 4 or len(senha) < 4:
        raise HTTPException(status_code=400, detail="Usuário e senha devem ter pelo menos 4 caracteres.")

    if payload.perfil not in ("admin", "caixa"):
        raise HTTPException(status_code=400, detail="Perfil deve ser admin ou caixa.")

    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute("BEGIN IMMEDIATE")
    total_usuarios = cursor.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0]
    if total_usuarios == 0 and credenciais is None:
        perfil_novo = "admin"
    else:
        usuario_atual = _sessoes.get(credenciais.credentials) if credenciais else None
        if not usuario_atual or usuario_atual["perfil"] != "admin":
            conexao_banco.close()
            raise HTTPException(status_code=403, detail="Somente administrador pode cadastrar usuários.")
        perfil_novo = payload.perfil
    cursor.execute("SELECT 1 FROM funcionarios WHERE usuario=?", (usuario,))
    if cursor.fetchone():
        conexao_banco.close()
        raise HTTPException(status_code=409, detail="Usuário já cadastrado.")

    cursor.execute("INSERT INTO funcionarios (usuario, senha, perfil) VALUES (?, ?, ?)", (usuario, gerar_hash_senha(senha), perfil_novo))
    conexao_banco.commit()
    conexao_banco.close()
    return {"ok": True}


@app.get("/dashboard")
def dashboard(_usuario=Depends(_exigir_admin)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo")
    estoque_baixo = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantidade) FROM produtos")
    total_itens = cursor.fetchone()[0] or 0

    primeiro_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM vendas WHERE data_venda >= ?", (primeiro_dia_mes,))
    vendas_mes = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantidade * preco_venda) FROM produtos")
    valor_estoque = cursor.fetchone()[0] or 0

    data_30_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT p.nome, SUM(v.quantidade) as total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE v.data_venda >= ?
        GROUP BY p.nome
        ORDER BY total DESC
        """,
        (data_30_dias,),
    )
    mais_vendidos = [{"produto": nome, "quantidade": quantidade} for nome, quantidade in cursor.fetchall()]

    hoje = datetime.now()
    proximo_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)
    ano_mes_limite = proximo_mes.strftime("%Y-%m")
    cursor.execute(
        """
        SELECT nome, validade, quantidade
        FROM produtos
        WHERE validade <= ?
        ORDER BY validade ASC
        LIMIT 30
        """,
        (ano_mes_limite,),
    )
    vencimento = [{"produto": n, "validade": v, "quantidade": q} for n, v, q in cursor.fetchall()]
    conexao_banco.close()

    return {
        "total_produtos": total_produtos,
        "estoque_baixo": estoque_baixo,
        "total_itens": total_itens,
        "vendas_mes": vendas_mes,
        "valor_estoque": valor_estoque,
        "mais_vendidos": mais_vendidos,
        "proximos_vencimento": vencimento,
    }


@app.get("/produtos/disponiveis")
def produtos_disponiveis(filtro: str = "", _usuario=Depends(_usuario_atual)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    if filtro:
        cursor.execute(
            """
            SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
            FROM produtos
            WHERE quantidade > 0 AND nome LIKE ?
            ORDER BY nome ASC
            """,
            (f"%{filtro}%",),
        )
    else:
        cursor.execute(
            """
            SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
            FROM produtos
            WHERE quantidade > 0
            ORDER BY nome ASC
            """
        )
    rows = cursor.fetchall()
    conexao_banco.close()
    itens = [
        {
            "id": row[0],
            "nome": row[1],
            "categoria": row[2],
            "quantidade": row[3],
            "preco_venda": row[4],
            "codigo_barras": row[5],
        }
        for row in rows
    ]
    return {"itens": itens}


@app.get("/produtos/codigo/{codigo}")
def produto_por_codigo(codigo: str, _usuario=Depends(_usuario_atual)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute(
        """
        SELECT id, nome, categoria, quantidade, preco_venda, codigo_barras
        FROM produtos
        WHERE codigo_barras = ?
        """,
        (codigo,),
    )
    row = cursor.fetchone()
    conexao_banco.close()
    if not row:
        return {"item": None}
    return {
        "item": {
            "id": row[0],
            "nome": row[1],
            "categoria": row[2],
            "quantidade": row[3],
            "preco_venda": row[4],
            "codigo_barras": row[5],
        }
    }


@app.post("/produtos/salvar")
def produto_salvar(payload: ProdutoIn, _usuario=Depends(_exigir_admin)):
    nome_produto = payload.nome.strip()
    categoria = _normalizar_categoria(payload.categoria)
    codigo_barras = payload.codigo_barras.strip() if payload.codigo_barras else None
    if not codigo_barras:
        codigo_barras = None

    if not nome_produto:
        raise HTTPException(status_code=400, detail="Nome do produto obrigatório.")
    if payload.preco_custo <= 0 or payload.preco_venda <= 0:
        raise HTTPException(status_code=400, detail="Preços devem ser maiores que zero.")
    if payload.quantidade < 0 or payload.estoque_minimo < 0:
        raise HTTPException(status_code=400, detail="Quantidade inválida.")

    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO produtos (nome, codigo_barras, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome_produto,
                codigo_barras,
                categoria,
                payload.preco_custo,
                payload.preco_venda,
                payload.quantidade,
                payload.estoque_minimo,
                payload.validade,
            ),
        )
        conexao_banco.commit()
        return {"resultado": "criado"}
    except Exception as exc:
        msg = str(exc)
        if "UNIQUE constraint failed: produtos.codigo_barras" in msg:
            raise HTTPException(status_code=409, detail="Código de barras já cadastrado.")
        if "UNIQUE constraint failed" not in msg:
            raise HTTPException(status_code=500, detail=f"Erro ao cadastrar produto: {msg}")

        cursor.execute("SELECT quantidade, preco_venda, preco_custo FROM produtos WHERE nome=?", (nome_produto,))
        atual = cursor.fetchone()
        qtd_atual = atual[0] if atual else 0
        preco_venda_atual = atual[1] if atual else 0.0
        preco_custo_atual = atual[2] if atual else 0.0
        novo_preco_venda = ((qtd_atual * preco_venda_atual) + (payload.quantidade * payload.preco_venda)) / (qtd_atual + payload.quantidade)
        novo_preco_custo = ((qtd_atual * preco_custo_atual) + (payload.quantidade * payload.preco_custo)) / (qtd_atual + payload.quantidade)
        cursor.execute(
            """
            UPDATE produtos
            SET categoria=?,
                codigo_barras=COALESCE(?, codigo_barras),
                preco_custo=?,
                preco_venda=?,
                quantidade=quantidade+?,
                estoque_minimo=?,
                validade=?
            WHERE nome=?
            """,
            (
                categoria,
                codigo_barras,
                novo_preco_custo,
                novo_preco_venda,
                payload.quantidade,
                payload.estoque_minimo,
                payload.validade,
                nome_produto,
            ),
        )
        conexao_banco.commit()
        return {"resultado": "atualizado"}
    finally:
        conexao_banco.close()


@app.get("/estoque/categorias")
def estoque_categorias(_usuario=Depends(_exigir_admin)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria != ''")
    categorias = sorted([row[0] for row in cursor.fetchall()])
    conexao_banco.close()
    return {"categorias": categorias}


@app.get("/estoque")
def estoque_lista(tipo: str = "todos", categoria: str = "Todas", _usuario=Depends(_exigir_admin)):
    parametros = []
    filtros_sql = []
    if tipo == "baixo":
        filtros_sql.append("quantidade <= estoque_minimo")
    else:
        filtros_sql.append("quantidade > estoque_minimo")
    if categoria != "Todas":
        filtros_sql.append("categoria = ?")
        parametros.append(categoria)

    consulta = f"""
        SELECT nome, categoria, quantidade, estoque_minimo, preco_venda, validade
        FROM produtos
        WHERE {' AND '.join(filtros_sql)}
        ORDER BY nome ASC
    """
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute(consulta, parametros)
    rows = cursor.fetchall()
    conexao_banco.close()
    itens = [
        {
            "nome": r[0],
            "categoria": r[1],
            "quantidade": r[2],
            "estoque_minimo": r[3],
            "preco_venda": r[4],
            "validade": r[5],
        }
        for r in rows
    ]
    return {"itens": itens}


@app.get("/estoque/estatisticas")
def estoque_stats(_usuario=Depends(_exigir_admin)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo")
    estoque_baixo = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(quantidade) FROM produtos")
    total_itens = cursor.fetchone()[0] or 0
    conexao_banco.close()
    return {
        "total_produtos": total_produtos,
        "estoque_baixo": estoque_baixo,
        "total_itens": total_itens,
    }


@app.post("/vendas")
def vendas_registrar(payload: VendaIn, _usuario=Depends(_usuario_atual)):
    if not payload.itens:
        raise HTTPException(status_code=400, detail="Nenhum item informado.")

    conexao_banco = conectar()
    cursor = conexao_banco.cursor()
    try:
        for item in payload.itens:
            cursor.execute("SELECT nome, quantidade FROM produtos WHERE id = ?", (item.id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Produto {item.id} não encontrado.")
            nome, estoque_atual = row
            if item.quantidade > estoque_atual:
                raise HTTPException(
                    status_code=409,
                    detail=f"Estoque insuficiente para {nome}. Disponível: {estoque_atual}",
                )

        for item in payload.itens:
            cursor.execute(
                """
                INSERT INTO vendas (produto_id, quantidade, data_venda)
                VALUES (?, ?, ?)
                """,
                (item.id, item.quantidade, payload.data_venda),
            )
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (item.quantidade, item.id))

        conexao_banco.commit()
        total = sum(item.subtotal for item in payload.itens)
        return {"ok": True, "total": total}
    finally:
        conexao_banco.close()


@app.get("/relatorios")
def relatorios(_usuario=Depends(_exigir_admin)):
    conexao_banco = conectar()
    cursor = conexao_banco.cursor()

    cursor.execute(
        """
        SELECT strftime('%Y-%m', data_venda) as mes,
               p.nome,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_produto
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY mes, p.nome
        ORDER BY mes DESC, lucro_produto DESC
        """
    )
    mensal_produtos = cursor.fetchall()

    cursor.execute(
        """
        SELECT strftime('%Y-%m', data_venda) as mes,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY mes
        ORDER BY mes DESC
        """
    )
    mensal_totais = cursor.fetchall()

    cursor.execute(
        """
        SELECT strftime('%Y', data_venda) as ano,
               p.categoria,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_categoria
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY ano, p.categoria
        ORDER BY ano DESC, lucro_categoria DESC
        """
    )
    anual_categorias = cursor.fetchall()

    cursor.execute(
        """
        SELECT strftime('%Y', data_venda) as ano,
               SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY ano
        ORDER BY ano DESC
        """
    )
    anual_totais = cursor.fetchall()
    conexao_banco.close()

    return {
        "mensal_produtos": [{"mes": m, "nome": n, "lucro": l} for m, n, l in mensal_produtos],
        "mensal_totais": [{"mes": m, "lucro": l} for m, l in mensal_totais],
        "anual_categorias": [{"ano": a, "categoria": c, "lucro": l} for a, c, l in anual_categorias],
        "anual_totais": [{"ano": a, "lucro": l} for a, l in anual_totais],
    }
