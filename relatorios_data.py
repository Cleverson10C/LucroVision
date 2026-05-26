import logging

from api_client import api_habilitada, relatorios_dados
from database import conectar

logger = logging.getLogger(__name__)


def obter_dados_relatorios():
    """Retorna datasets de relatorio desacoplados da camada de UI."""
    if api_habilitada():
        dados = relatorios_dados()
        return {
            "mensais_produtos": [(item["mes"], item["nome"], item["lucro"]) for item in dados["mensal_produtos"]],
            "mensais_totais": [(item["mes"], item["lucro"]) for item in dados["mensal_totais"]],
            "anuais_categorias": [(item["ano"], item["categoria"], item["lucro"]) for item in dados["anual_categorias"]],
            "anuais_totais": [(item["ano"], item["lucro"]) for item in dados["anual_totais"]],
        }

    conexao_banco = conectar()
    try:
        cursor_banco = conexao_banco.cursor()
        cursor_banco.execute(
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
        resultados_mensais_produtos = cursor_banco.fetchall()

        cursor_banco.execute(
            """
            SELECT strftime('%Y-%m', data_venda) as mes,
                   SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            GROUP BY mes
            ORDER BY mes DESC
            """
        )
        resultados_totais_mensais = cursor_banco.fetchall()

        cursor_banco.execute(
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
        resultados_anuais_categorias = cursor_banco.fetchall()

        cursor_banco.execute(
            """
            SELECT strftime('%Y', data_venda) as ano,
                   SUM((p.preco_venda - p.preco_custo) * v.quantidade) as lucro_total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            GROUP BY ano
            ORDER BY ano DESC
            """
        )
        resultados_totais_anuais = cursor_banco.fetchall()
    finally:
        conexao_banco.close()

    logger.info(
        "Dados de relatorios carregados: produtos_mes=%s, totais_mes=%s, categorias_ano=%s, totais_ano=%s",
        len(resultados_mensais_produtos),
        len(resultados_totais_mensais),
        len(resultados_anuais_categorias),
        len(resultados_totais_anuais),
    )
    return {
        "mensais_produtos": resultados_mensais_produtos,
        "mensais_totais": resultados_totais_mensais,
        "anuais_categorias": resultados_anuais_categorias,
        "anuais_totais": resultados_totais_anuais,
    }
