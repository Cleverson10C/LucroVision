import relatorios_data


class DummyCursor:
    def __init__(self, fetchall_results):
        self.fetchall_results = fetchall_results
        self.execute_calls = 0

    def execute(self, _query):
        self.execute_calls += 1

    def fetchall(self):
        idx = self.execute_calls - 1
        return self.fetchall_results[idx]


class DummyConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


def test_obter_dados_relatorios_via_api(monkeypatch):
    monkeypatch.setattr(relatorios_data, "api_habilitada", lambda: True)
    monkeypatch.setattr(
        relatorios_data,
        "relatorios_dados",
        lambda: {
            "mensal_produtos": [{"mes": "2026-05", "nome": "Arroz", "lucro": 50.0}],
            "mensal_totais": [{"mes": "2026-05", "lucro": 50.0}],
            "anual_categorias": [{"ano": "2026", "categoria": "Mercearia", "lucro": 50.0}],
            "anual_totais": [{"ano": "2026", "lucro": 50.0}],
        },
    )

    dados = relatorios_data.obter_dados_relatorios()

    assert dados["mensais_produtos"] == [("2026-05", "Arroz", 50.0)]
    assert dados["mensais_totais"] == [("2026-05", 50.0)]
    assert dados["anuais_categorias"] == [("2026", "Mercearia", 50.0)]
    assert dados["anuais_totais"] == [("2026", 50.0)]


def test_obter_dados_relatorios_via_banco(monkeypatch):
    monkeypatch.setattr(relatorios_data, "api_habilitada", lambda: False)
    cursor = DummyCursor(
        [
            [("2026-05", "Feijao", 80.0)],
            [("2026-05", 80.0)],
            [("2026", "Mercearia", 80.0)],
            [("2026", 80.0)],
        ]
    )
    conexao = DummyConnection(cursor)
    monkeypatch.setattr(relatorios_data, "conectar", lambda: conexao)

    dados = relatorios_data.obter_dados_relatorios()

    assert cursor.execute_calls == 4
    assert conexao.closed is True
    assert dados["mensais_produtos"] == [("2026-05", "Feijao", 80.0)]
    assert dados["mensais_totais"] == [("2026-05", 80.0)]
    assert dados["anuais_categorias"] == [("2026", "Mercearia", 80.0)]
    assert dados["anuais_totais"] == [("2026", 80.0)]
