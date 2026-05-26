from estoque import montar_filtros_estoque_sql


def test_filtro_todos_sem_categoria_nao_aplica_where():
    where_sql, parametros = montar_filtros_estoque_sql("todos", "Todas")
    assert where_sql == ""
    assert parametros == []


def test_filtro_todos_com_categoria_aplica_apenas_categoria():
    where_sql, parametros = montar_filtros_estoque_sql("todos", "Bebidas")
    assert where_sql == "WHERE categoria = ?"
    assert parametros == ["Bebidas"]


def test_filtro_baixo_sem_categoria_aplica_estoque_baixo():
    where_sql, parametros = montar_filtros_estoque_sql("baixo", "Todas")
    assert where_sql == "WHERE quantidade <= estoque_minimo"
    assert parametros == []
