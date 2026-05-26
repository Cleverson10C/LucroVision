import login
from security import gerar_hash_senha


class DummyCursor:
    def __init__(self, fetchone_result):
        self.fetchone_result = fetchone_result
        self.executed = []

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return self.fetchone_result


class DummyConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False
        self.committed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


def test_verificar_login_api_sucesso(monkeypatch):
    monkeypatch.setattr(login, "api_habilitada", lambda: True)
    monkeypatch.setattr(login, "api_login", lambda usuario, senha: True)
    assert login.verificar_login("admin", "1234") is True


def test_verificar_login_api_erro_retorna_false(monkeypatch):
    monkeypatch.setattr(login, "api_habilitada", lambda: True)

    def _falhar(*_args, **_kwargs):
        raise RuntimeError("falha de rede")

    monkeypatch.setattr(login, "api_login", _falhar)
    assert login.verificar_login("admin", "1234") is False


def test_verificar_login_usuario_inexistente(monkeypatch):
    monkeypatch.setattr(login, "api_habilitada", lambda: False)
    cursor = DummyCursor(None)
    conexao = DummyConnection(cursor)
    monkeypatch.setattr(login, "conectar", lambda: conexao)

    assert login.verificar_login("inexistente", "1234") is False
    assert conexao.closed is True


def test_verificar_login_hash_valido(monkeypatch):
    monkeypatch.setattr(login, "api_habilitada", lambda: False)
    senha_hash = gerar_hash_senha("1234")
    cursor = DummyCursor((10, senha_hash))
    conexao = DummyConnection(cursor)
    monkeypatch.setattr(login, "conectar", lambda: conexao)

    assert login.verificar_login("admin", "1234") is True
    assert conexao.committed is False


def test_verificar_login_migra_senha_legado(monkeypatch):
    monkeypatch.setattr(login, "api_habilitada", lambda: False)
    cursor = DummyCursor((7, "abc123"))
    conexao = DummyConnection(cursor)
    monkeypatch.setattr(login, "conectar", lambda: conexao)

    assert login.verificar_login("admin", "abc123") is True
    assert conexao.committed is True
    assert any("UPDATE funcionarios SET senha=?" in query for query, _ in cursor.executed)
